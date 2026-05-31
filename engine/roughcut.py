"""
Autonomous Rough Cut Engine v4
Waveform-first architecture with OpenAI Whisper API per-chunk transcription.
Removes retakes, false starts, side conversations. Keeps last take.
"""

import numpy as np
import wave
import json
import os
import subprocess
import sys
import time
from openai import OpenAI
from rapidfuzz import fuzz


# ============================================================
# CONFIGURATION
# ============================================================
SILENCE_MERGE_THRESHOLD = 0.30   # seconds -- tuned sweet spot for conversational speech
MIN_CHUNK_DURATION = 1.0         # skip fragments under this
RETAKE_TEXT_THRESHOLD = 60       # rapidfuzz token_sort_ratio
RETAKE_NOUN_OVERLAP = 0.60      # overlap coefficient
FRAGMENT_MAX_DURATION = 3.0      # only flag as fragment if under this
BREATH_GAP_MAX = 1.5             # gaps under this = natural breath
ROOM_TONE_VOLUME = 0.12         # subtle bed
AUDIO_FADE_MS = 30               # fade in/out at cuts
CRF_QUALITY = 16                 # near-lossless
AUDIO_BITRATE = "256k"


def load_api_key():
    # Prefer the OPENAI_API_KEY environment variable. Fall back to a local
    # .env.local in the current working directory if present.
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key.strip()
    env_path = os.path.join(os.getcwd(), ".env.local")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.strip().split("=", 1)[1]
    raise RuntimeError(
        "OPENAI_API_KEY not set. Export it as an environment variable "
        "(export OPENAI_API_KEY=sk-...) or add it to a .env.local file."
    )


def extract_audio(video_path, output_path):
    """Extract 16kHz mono WAV for analysis."""
    subprocess.run([
        "/usr/local/bin/ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", output_path
    ], capture_output=True)


def analyze_waveform(audio_path):
    """Find speech chunks using RMS energy analysis."""
    wav = wave.open(audio_path, "r")
    sample_rate = wav.getframerate()
    audio_bytes = wav.readframes(wav.getnframes())
    wav.close()

    audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
    audio_data /= np.max(np.abs(audio_data))

    window_ms = 10
    window_size = int(window_ms / 1000 * sample_rate)
    n_windows = len(audio_data) // window_size
    rms = np.array([
        np.sqrt(np.mean(audio_data[i*window_size:(i+1)*window_size]**2))
        for i in range(n_windows)
    ])

    silence_threshold = max(np.percentile(rms, 10) * 3, 0.008)

    # Smooth
    smoothed = rms > silence_threshold
    kernel = 3
    for i in range(kernel, len(smoothed) - kernel):
        w = smoothed[max(0, i-kernel):i+kernel+1]
        smoothed[i] = np.sum(w) > kernel

    # Find chunks
    chunks_raw = []
    in_s = False
    cs = 0
    for i in range(len(smoothed)):
        t = i * window_ms / 1000
        if smoothed[i] and not in_s:
            cs = t
            in_s = True
        elif not smoothed[i] and in_s:
            if t - cs >= 0.10:
                chunks_raw.append({
                    'start': round(cs, 3),
                    'end': round(t, 3),
                    'duration': round(t - cs, 3)
                })
            in_s = False

    # Merge close chunks
    merged = []
    for c in chunks_raw:
        if merged and (c['start'] - merged[-1]['end']) < SILENCE_MERGE_THRESHOLD:
            merged[-1]['end'] = c['end']
            merged[-1]['duration'] = round(merged[-1]['end'] - merged[-1]['start'], 3)
        else:
            merged.append(dict(c))

    return merged, sample_rate, audio_bytes


def transcribe_chunks(chunks, sample_rate, audio_bytes, chunk_dir, client):
    """Transcribe each chunk individually via OpenAI Whisper API."""
    os.makedirs(chunk_dir, exist_ok=True)
    all_chunks = []

    for i, chunk in enumerate(chunks):
        sb = int(chunk['start'] * sample_rate) * 2
        eb = int(chunk['end'] * sample_rate) * 2
        cp = f"{chunk_dir}/chunk_{i:03d}.wav"

        with wave.open(cp, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_bytes[sb:eb])

        text = ""
        if chunk['duration'] >= 0.25:
            with open(cp, "rb") as f:
                text = client.audio.transcriptions.create(
                    model="whisper-1", file=f,
                    response_format="text", language="en"
                ).strip()

        all_chunks.append({
            'id': i,
            'start': chunk['start'],
            'end': chunk['end'],
            'duration': chunk['duration'],
            'text': text
        })

    return all_chunks


def find_final_run(all_chunks):
    """Find the last complete run-through by auto-detecting repeated intros.

    Strategy: check if any of the first 5 substantial chunks reappear later
    in the recording (indicating the speaker restarted from the top).
    If a repeated intro is found, start from the LAST occurrence.
    If no full restart detected, use ALL chunks (let retake detection handle it).
    """
    if len(all_chunks) < 10:
        return all_chunks

    # Grab first few substantial chunks as potential intro markers
    intro_candidates = []
    for c in all_chunks[:15]:
        if c['duration'] >= 2.0 and len(c['text'].split()) >= 6:
            intro_candidates.append(c)
        if len(intro_candidates) >= 5:
            break

    if not intro_candidates:
        return all_chunks

    # Check if any intro candidate reappears later (full restart)
    best_restart_idx = None
    for ic in intro_candidates:
        ic_text = ic['text'].lower().replace(',', '').replace('.', '')
        ic_kw = extract_key_words(ic['text'])

        # Only look in the second half onward for restarts
        halfway = len(all_chunks) // 2
        for c in all_chunks[halfway:]:
            if c['id'] == ic['id']:
                continue
            c_text = c['text'].lower().replace(',', '').replace('.', '')

            # High similarity = same sentence re-recorded
            sim = fuzz.token_sort_ratio(ic_text, c_text)
            if sim > 70:
                if best_restart_idx is None or c['id'] > best_restart_idx:
                    best_restart_idx = c['id']
                break

            # Also check key word overlap for paraphrased restarts
            c_kw = extract_key_words(c['text'])
            if ic_kw and c_kw:
                overlap = len(ic_kw & c_kw) / min(len(ic_kw), len(c_kw))
                if overlap > 0.75 and sim > 50:
                    if best_restart_idx is None or c['id'] > best_restart_idx:
                        best_restart_idx = c['id']
                    break

    if best_restart_idx is not None:
        return [c for c in all_chunks if c['id'] >= best_restart_idx]

    # No full restart detected -- use all chunks
    return all_chunks


def extract_key_words(text):
    """Extract significant words for comparison."""
    stops = {
        'the', 'this', 'that', 'with', 'from', 'into', 'will', 'have', 'your',
        'they', 'them', 'then', 'than', 'there', 'their', 'these', 'those',
        'what', 'when', 'where', 'which', 'while', 'after', 'before', 'about',
        'been', 'being', 'both', 'each', 'every', 'more', 'most', 'much',
        'many', 'some', 'such', 'only', 'just', 'also', 'very', 'even',
        'still', 'already', 'always', 'never', 'often', 'actually', 'really',
        'basically', 'honestly', 'realistically', 'over', 'and', 'but', 'for',
        'not', 'you', 'are', 'was', 'were', 'has', 'had', 'can', 'could',
        'would', 'should', 'may', 'might', 'shall', 'does', 'did', 'its',
        'our', 'his', 'her', 'all', 'any', 'few', 'own', 'same', 'too',
        'like', 'once', 'called', 'something', 'number', 'check', 'want',
        'send', 'entire', 'list', 'looking', 'make', 'right', 'now', 'first',
        'well', 'back', 'step', 'take', 'stop', 'start', 'going', 'give',
        'know', 'think', 'look', 'keep', 'come', 'made', 'built', 'gets',
        'don', 'it', 'so', 'if', 'is', 'be', 'do', 'go', 'my', 'me',
        'he', 'we', 'us', 'up', 'no', 'or', 'an', 'on', 'at', 'by', 'as',
        'in', 'of', 'to'
    }
    words = set()
    for w in text.lower().replace(',', '').replace('.', '').replace('!', '').replace('?', '').replace("'", '').split():
        if len(w) > 2 and w not in stops:
            words.add(w)
    return words


def detect_retakes(final_chunks, chunk_dir, client):
    """Apply last-take rule with partial containment and overlap coefficient."""

    # Generic side conversation markers -- talking TO the editor/Claude, not recording
    side_keywords = [
        'rewrite', 'bullshit', 'looking like ai', 'too short', 'unnecessary',
        'what else we can write', 'sentence structure', 'make it like',
        'let me redo', 'one more time', 'that was bad', 'that sucked',
        'hold on let me', 'wait let me', 'cut that', 'scratch that',
        'start over', 'do that again', 'not good enough', 'sounds weird',
        'flops', 'take two', 'take three', 'retake',
    ]

    # Phase 1: Filter junk
    candidates = []
    for c in final_chunks:
        if c['duration'] < MIN_CHUNK_DURATION:
            continue
        if len(c['text'].strip()) < 5:
            continue
        if any(kw in c['text'].lower() for kw in side_keywords):
            continue
        candidates.append(c)

    # Phase 2: Retake detection
    keep = []
    skip = []

    for i, ca in enumerate(candidates):
        is_retake = False
        kw_a = extract_key_words(ca['text'])
        a_words_list = ca['text'].lower().replace(',', '').replace('.', '').split()

        for j in range(i + 1, len(candidates)):
            cb = candidates[j]

            # Check 1: Text similarity
            text_sim = fuzz.token_sort_ratio(ca['text'].lower(), cb['text'].lower())
            if text_sim > RETAKE_TEXT_THRESHOLD:
                is_retake = True
                break

            # Check 2: Key word overlap (overlap coefficient)
            kw_b = extract_key_words(cb['text'])
            if kw_a and kw_b:
                intersection = len(kw_a & kw_b)
                smaller = min(len(kw_a), len(kw_b))
                if smaller > 0 and (intersection / smaller) > RETAKE_NOUN_OVERLAP:
                    is_retake = True
                    break

            # Check 3: Partial containment (only for short chunks)
            if ca['duration'] < FRAGMENT_MAX_DURATION and len(a_words_list) >= 3:
                for n in [5, 4, 3]:
                    if len(a_words_list) >= n:
                        prefix = ' '.join(a_words_list[:n])
                        if prefix in cb['text'].lower():
                            is_retake = True
                            break
                if is_retake:
                    break

                # Partial ratio for short fragments
                b_words_list = cb['text'].lower().replace(',', '').replace('.', '').split()
                if len(a_words_list) < len(b_words_list) * 0.5:
                    a_seq = ' '.join(a_words_list[:min(6, len(a_words_list))])
                    b_full = ' '.join(b_words_list)
                    if fuzz.partial_ratio(a_seq, b_full) > 80:
                        is_retake = True
                        break

        if is_retake:
            skip.append(ca)
        else:
            keep.append(ca)

    # Phase 3: CTA -- keep only last
    cta_chunks = [c for c in keep if 'comment' in c['text'].lower()]
    if len(cta_chunks) > 1:
        for c in cta_chunks[:-1]:
            keep.remove(c)
            skip.append(c)

    # Phase 4: Word-level trim on CTA for internal repetition
    if cta_chunks:
        last_cta = cta_chunks[-1]
        cta_path = f"{chunk_dir}/chunk_{last_cta['id']:03d}.wav"
        with open(cta_path, "rb") as f:
            cta_r = client.audio.transcriptions.create(
                model="whisper-1", file=f, response_format="verbose_json",
                timestamp_granularities=["word"], language="en"
            )
        cta_words = [w.word.lower().replace(',', '').replace('.', '') for w in cta_r.words]
        for wi in range(3, len(cta_words)):
            if cta_words[wi:wi+3] == cta_words[0:3]:
                trim_offset = cta_r.words[wi].start
                last_cta['start'] = round(last_cta['start'] + trim_offset, 3)
                last_cta['duration'] = round(last_cta['end'] - last_cta['start'], 3)
                break

    keep.sort(key=lambda x: x['start'])
    return keep, skip


def build_segments(keep, skip):
    """Build raw video segments with smart gap handling."""
    skip_set = set(c['id'] for c in skip)
    raw_segments = []

    for i, c in enumerate(keep):
        pad_start = max(0, c['start'] - 0.05)
        pad_end = c['end'] + 0.05

        if raw_segments:
            prev_end = raw_segments[-1][1]
            gap = pad_start - prev_end

            # Check if anything was skipped between
            something_skipped = any(
                sc['start'] > prev_end - 0.1 and sc['end'] < pad_start + 0.1
                for sc in skip
            )

            if gap < 0:
                raw_segments[-1] = (raw_segments[-1][0], pad_end)
            elif gap <= BREATH_GAP_MAX and not something_skipped:
                raw_segments[-1] = (raw_segments[-1][0], pad_end)
            else:
                raw_segments.append((pad_start, pad_end))
        else:
            raw_segments.append((pad_start, pad_end))

    return raw_segments


def encode_roughcut(video_path, segments, output_dir, output_path):
    """Extract clips, add fades, concat with room tone bed."""

    # Extract room tone
    room_tone = f"{output_dir}/room_tone.wav"
    subprocess.run([
        "/usr/local/bin/ffmpeg", "-y", "-ss", "1.0", "-t", "2.0",
        "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "48000", "-ac", "2",
        room_tone
    ], capture_output=True)

    # Extract clips
    clip_dir = f"{output_dir}/clips"
    os.makedirs(clip_dir, exist_ok=True)

    concat_list = []
    for i, (start, end) in enumerate(segments):
        clip_path = f"{clip_dir}/clip_{i:03d}.ts"
        dur = end - start
        fade_out_st = max(0, dur - AUDIO_FADE_MS / 1000)
        subprocess.run([
            "/usr/local/bin/ffmpeg", "-y",
            "-ss", str(start), "-to", str(end),
            "-i", video_path,
            "-af", f"afade=t=in:d={AUDIO_FADE_MS/1000},afade=t=out:st={fade_out_st:.3f}:d={AUDIO_FADE_MS/1000}",
            "-c:v", "libx264", "-preset", "fast", "-crf", str(CRF_QUALITY),
            "-c:a", "aac", "-b:a", AUDIO_BITRATE,
            "-f", "mpegts", clip_path
        ], capture_output=True)
        concat_list.append(f"file '{clip_path}'")

    concat_path = f"{clip_dir}/concat.txt"
    with open(concat_path, "w") as f:
        f.write("\n".join(concat_list))

    # Final concat with room tone
    subprocess.run([
        "/usr/local/bin/ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_path,
        "-stream_loop", "-1", "-i", room_tone,
        "-filter_complex",
        f"[1:a]volume={ROOM_TONE_VOLUME}[rt];[0:a][rt]amix=inputs=2:duration=first:normalize=0[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "slow", "-crf", str(CRF_QUALITY),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE,
        "-movflags", "+faststart",
        output_path
    ], capture_output=True)


def cross_verify(output_path, client):
    """Re-transcribe output and check for issues."""
    verify_audio = output_path.replace('.mp4', '_verify.mp3')
    subprocess.run([
        "/usr/local/bin/ffmpeg", "-y", "-i", output_path,
        "-vn", "-b:a", "64k", verify_audio
    ], capture_output=True)

    with open(verify_audio, "rb") as f:
        verify = client.audio.transcriptions.create(
            model="whisper-1", file=f, response_format="verbose_json",
            timestamp_granularities=["segment"], language="en"
        )

    # Check for repeated phrases
    full_text = ' '.join(seg.text.strip() for seg in verify.segments).lower()
    words = full_text.split()
    issues = []
    for i in range(len(words) - 5):
        phrase = ' '.join(words[i:i+5])
        rest = ' '.join(words[i+6:])
        if phrase in rest:
            issues.append(phrase)

    return verify, list(set(issues))


def get_duration(path):
    """Get video duration string."""
    r = subprocess.run(
        ["/usr/local/bin/ffmpeg", "-i", path, "-f", "null", "-"],
        capture_output=True, text=True
    )
    for line in r.stderr.split('\n'):
        if 'Duration' in line:
            return line.strip()
    return "unknown"


def produce(video_path):
    """Main entry point -- run full autonomous rough cut pipeline."""
    start_time = time.time()

    # Setup
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = os.path.join(os.getcwd(), "exports", "produce", f"{video_name}_{int(time.time())}")
    os.makedirs(output_dir, exist_ok=True)

    client = OpenAI(api_key=load_api_key())

    # Step 1: Extract audio
    print("STEP 1: Extracting audio...")
    audio_path = f"{output_dir}/audio.wav"
    extract_audio(video_path, audio_path)

    # Step 2: Waveform analysis
    print("STEP 2: Waveform analysis...")
    chunks, sample_rate, audio_bytes = analyze_waveform(audio_path)
    print(f"  {len(chunks)} speech chunks")

    # Step 3: Transcribe
    print("STEP 3: Transcribing chunks...")
    chunk_dir = f"{output_dir}/chunks"
    all_chunks = transcribe_chunks(chunks, sample_rate, audio_bytes, chunk_dir, client)
    print(f"  {len(all_chunks)} chunks transcribed ({time.time()-start_time:.0f}s)")

    # Step 4: Find final run
    print("STEP 4: Finding final run...")
    final_chunks = find_final_run(all_chunks)
    print(f"  {len(final_chunks)} chunks in final run")

    # Step 5: Retake detection
    print("STEP 5: Detecting retakes...")
    keep, skip = detect_retakes(final_chunks, chunk_dir, client)
    print(f"  Keep: {len(keep)}, Skip: {len(skip)}")

    for c in keep:
        mins = int(c['start'] // 60)
        secs = c['start'] % 60
        print(f"    [{mins}:{secs:05.2f}] ({c['duration']:.1f}s) {c['text'][:70]}")

    # Step 6: Build rough cut
    print("STEP 6: Building rough cut...")
    segments = build_segments(keep, skip)
    print(f"  {len(segments)} segments")

    output_path = f"{output_dir}/{video_name}_roughcut.mp4"
    encode_roughcut(video_path, segments, output_dir, output_path)

    # Step 7: Cross-verify
    print("STEP 7: Cross-verifying...")
    verify, issues = cross_verify(output_path, client)
    duration = get_duration(output_path)

    if issues:
        print(f"  WARNING: {len(issues)} repeated phrases detected")
        for iss in issues[:3]:
            print(f"    - '{iss}'")
    else:
        print("  CLEAN -- no issues detected")

    total_time = time.time() - start_time

    print(f"\n{'='*60}")
    print(f"  {duration}")
    print(f"  Kept {len(keep)} chunks, skipped {len(skip)}")
    print(f"  Total time: {total_time:.0f}s ({total_time/60:.1f} min)")
    print(f"  Output: {output_path}")
    print(f"{'='*60}")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python roughcut.py <video_path>")
        sys.exit(1)
    produce(sys.argv[1])
