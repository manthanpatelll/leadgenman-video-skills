---
name: produce
description: "Autonomous rough cut engine. Takes a raw face cam video with retakes and outputs a clean rough cut with all retakes, false starts, and side conversations removed. Uses waveform-first architecture + OpenAI Whisper API. Invoke as /produce with a video file path."
---

# Autonomous Rough Cut Engine

## Usage
```
/produce:produce /path/to/raw-video.mp4
```

## What it does
Takes a raw face cam recording (any length, with retakes) and outputs a clean rough cut in original resolution. Removes:
- Retakes (keeps only the last take of each section)
- False starts and fragments
- Side conversations (talking to the AI about the script, not recording)
- Internal repetitions (e.g., double CTA starts)

Adds:
- 30ms audio fades at cut points (no clicks/pops)
- Room tone bed at 12% volume (fills micro-gaps naturally)
- Smart gap handling (preserves natural breaths between sentences)

## Requirements
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- ffmpeg
- An `OPENAI_API_KEY` environment variable (used for per-chunk Whisper transcription)

## How to run

1. **Get the video path** from the user argument
2. **Verify file exists**: check with `ls`
3. **Run the pipeline** from the bundled engine:
```bash
cd <path-to-this-plugin>/engine
OPENAI_API_KEY=sk-... uv run python roughcut.py "<video_path>"
```
4. The script will:
   - Extract audio and analyze waveform (0.3s threshold)
   - Transcribe each speech chunk individually via OpenAI Whisper API
   - Find the last complete run-through
   - Detect and remove retakes (rapidfuzz + key word overlap + partial containment)
   - Build the rough cut with audio fades and room tone
   - Cross-verify by re-transcribing the output
   - Open the final file automatically
5. **Report results** to the user: duration, chunks kept/skipped, any issues detected

## Output
- File saved to: `exports/produce/<video_name>_<timestamp>/<video_name>_roughcut.mp4`
- Original resolution (1920x1080 or whatever the source is)
- CRF 16, AAC 256kbps (near-lossless quality)
- Ready to import into Descript, Premiere, or any editor for final assembly

## Architecture
- **Waveform-first**: 10ms RMS energy windows find exact speech boundaries
- **Per-chunk transcription**: Each speech chunk sent to OpenAI Whisper API separately (prevents merging retakes)
- **Last-take rule**: You record multiple takes, keep repeating until satisfied, then move on. Last take before a topic change = keeper.
- **Three-layer retake detection**:
  1. Text similarity (rapidfuzz token_sort_ratio > 60)
  2. Key word overlap coefficient > 0.60
  3. Partial containment (short chunk's first words appear in a later chunk)
- **Smart gap handling**: Natural breaths between kept chunks preserved, gaps where content was removed get room tone fill

## Settings
These defaults are tuned for a natural conversational speaking style. Adjust in `engine/roughcut.py` if your cadence differs:
- Silence merge threshold: 0.3s
- Min chunk duration: 1.0s
- Fragment max duration for partial containment: 3.0s
- Breath gap max: 1.5s
- Room tone volume: 12%
