---
name: reel-overlay
description: Generate a 4K vertical (2160x3840) ProRes 4444 alpha .mov overlay for split-screen reels — top 50% is the overlay, bottom 50% is the face cam. Drag straight into Descript on top of the face cam. Invoke as /reel-overlay <audio-or-video-path>. Audio-only files (.wav/.mp3) are fully supported.
---

# Reel Overlay Generator

> **Note for the public release.** This skill was extracted from a private content-production project. It references an internal Canvas 2D engine, renderer, fonts, and brand assets that are NOT bundled in this repo, so it will not run end-to-end out of the box. It is published as a reference blueprint: read it to see the full workflow and adapt the patterns to your own stack.

> **Note for the public release.** This skill was extracted from a private content-production project. It references an internal Canvas 2D engine, renderer, fonts, and brand assets that are NOT bundled in this repo, so it will not run end-to-end out of the box. It is published as a reference blueprint: read it to see the full workflow and adapt the patterns to your own stack.

> **Note for the public release.** This skill was extracted from a private content-production project. It references an internal Canvas 2D engine, renderer, fonts, and brand assets that are NOT bundled in this repo, so it will not run end-to-end out of the box. It is published as a reference blueprint: read it to see the full workflow and adapt the patterns to your own stack.

## 1. ZERO-QUESTION POLICY

When you gives a path — `.wav`, `.mp3`, `.m4a`, `.mp4`, `.mov`, anything — run the full pipeline immediately. The output is an alpha overlay that sits on top of the face cam in Descript, so the input only needs to provide the audio for transcription. NEVER ask:

- "this is .wav not video, did you mean a different file?"
- "is this the source?", "should I proceed?"
- "do you have the face-cam video?"
- "which style/logos/length/beats?"
- "should I render now or smoke first?"
- "should I use Clawd or emojis?"
- "should I use a custom scene vs pills?"

Make every creative call yourself. you trusts you.

If the file genuinely doesn't exist on disk, only then report back.

## 2. DEFAULT STYLE — LIQUID CHROMATIC PILLS

Each pill has:
- **Body**: animated linear gradient that slowly rotates over time, pulled from the pill's 6-stop palette (deeper half).
- **Outline**: outward-only wave stroke (`strokeLiquidOutline`), same palette family as body. The wave bumps OUTWARD only — never bites the inside.
- **Text**: plain fill, white or near-black depending on bg luminosity. NEVER stroked.
- **3-layer drop shadow** under every pill — premium uplifted feel.

## 3. UNIQUE 6-STOP PALETTE PER PILL (HARD)

Every pill ships its own `props.palette` — a 6-stop hex array. The renderer's `setPillPalette(seedKey, palette)` registry feeds BOTH the body gradient AND the wave outline so they actually change color (just `fill` alone leaves the seeded LIQUID_PALETTES default in place).

```js
const P = {
  hook:  ["#5B1F0E", "#A04A2C", "#D97757", "#F2A684", "#FCDDC9", "#FFE8B8"], // Claude orange
  count: ["#2E1065", "#5B21B6", "#7C3AED", "#A78BFA", "#DDD6FE", "#F5F3FF"], // violet
};

// Per beat:
{ ..., props: { ..., fill: P.hook[1], textColor: "#FFFFFF", palette: P.hook } }
```

Stop order: `[deepShadow, bodyDeep, bodyMid, bodyLight, accentLight, accentBright]`. Body uses 0-3, outline uses all 6. `props.fill` paints the static plate beneath the gradient — set it to `palette[1]` or `[2]`.

Rules:
- **Claude / Claude Code base = `#D97757`** (real Anthropic Claude orange). Use the orange Claude logo PNG (`public/brand-logos/claude-512.png` — re-rasterized in `#D97757`). NEVER ship Claude in black.
- **Never repeat a base color across two pills in the same reel.**
- **Text contrasts bg.** Light bg → near-black (`#1F2937`). Dark bg → `#FFFFFF`.
- **Audit before render**: every pill has its own `palette` array.

## 4. VISUAL ELEMENT NEXT TO EVERY PILL — BALANCED MIX (HARD)

Every pill MUST be paired with a contextual visual in another zone. Use the right tool for the moment, not one tool for everything:

| When | Use | Why |
|------|-----|-----|
| Structural / explanatory beat (org chart, agent grid, parallel lanes, role card, building, IDE mock, overflow stack) | **Custom Canvas 2D illustration** (`type: "primitive"` + `props.draw`) | Premium, exactly matches the topic, looks crafted |
| Specific tool/brand mentioned (Cursor, Claude Code, Codex, GitHub, Vercel, Anthropic) | **Brand logo** (`type: "logo"`) from `public/brand-logos/` | Real product recognition |
| Topic IS Claude / Claude Code / Anthropic | **Clawd mascot** (`type: "clawd"`) alongside the logo | Brand mascot, only when topic warrants |
| Instant-read reaction or single-word concept (sparkle, warning, money, lightning, shrug) | **Apple emoji** (`type: "emoji"`) | Emojis read instantly when they LITERALLY match the word |
| Showing a real product UI moment | **Web-fetched screenshot** rasterized to PNG, used as a logo or primitive | Truth wins |

**Target mix per reel: ~60% custom illustration, ~25% emoji, ~15% logo/Clawd.** Don't go all-illustration (too cold/diagrammy) or all-emoji (too lazy/generic). Match each beat to what reads best.

### Custom illustration aesthetic (premium)
- Soft shadows: `rgba(31, 24, 21, 0.16)` blur 18 offsetY 8.
- Rounded corners 8-14px.
- Subtle motion only: gentle reveals, soft pulses, no busy spin/jitter.
- One idea per illustration. Less is more.
- Pattern: write per-reel illustration functions in a sibling `<reel-name>-illustrations.mjs` exporting `(ctx, t, props) => void` functions. Reference: [scripts/reel-overlay/agency-illustrations.mjs](../../../Desktop/your project/scripts/reel-overlay/agency-illustrations.mjs).

### ⚠️ ILLUSTRATION FONT FAMILY — USE `'Proxima Nova'`, NEVER `-apple-system`/`SF Mono` (HARD — root-caused 2026-05-30)
**This is the #1 cause of "the text inside the illustration is tiny and nothing I change fixes it."** node-canvas (the headless renderer) only has ONE registered font: **`Proxima Nova`** (installed by `installFonts()` in [lib/reel-overlay/render.mjs](../../../Desktop/your project/lib/reel-overlay/render.mjs)). Web font stacks do NOT exist headless and **silently fall back to a fixed ~12px bitmap font whose size DOES NOT CHANGE no matter what px you set.**

Proven: `ctx.font="800 44px -apple-system"` → `measureText("CLAUDE.md").width = 57`; `"800 84px -apple-system"` → **still 57**. The size is ignored. With `'Proxima Nova'`: 44px→121, 88px→242 (scales correctly).

So inside EVERY `draw()` function in `<reel>-illustrations.mjs`:
- ✅ `ctx.font = "800 44px 'Proxima Nova', sans-serif";`
- ❌ `ctx.font = "800 44px -apple-system, 'SF Pro Text', sans-serif";` (renders ~12px, frozen)
- ❌ `ctx.font = "700 40px 'SF Mono', ui-monospace, monospace";` (renders ~12px, frozen — there is NO mono font headless; use Proxima Nova even for terminal/code cards)
- The trailing generic (`sans-serif`) is a no-op fallback; `'Proxima Nova'` MUST be the first family or the size silently breaks.

**Symptom that means you hit this bug:** you increase the px number, re-render, and the text looks identical / still small. STOP guessing at card size — the font family is wrong. Grep `ctx.font` in the illustrations file; any family that isn't `'Proxima Nova'` is the bug.

**Debugging recipe (10 seconds, do this BEFORE touching card dimensions):**
```js
// node /tmp/f.mjs
import { createCanvas, registerFont } from "<your-project>/node_modules/canvas/index.js";
import fs from "fs"; const P="<your-project>/public/fonts/ProximaNova.ttc";
if (fs.existsSync(P)) registerFont(P,{family:"Proxima Nova",weight:"800"});
const x=createCanvas(9,9).getContext("2d");
x.font="800 44px 'YOUR FONT HERE'"; const a=x.measureText("CLAUDE.md").width;
x.font="800 88px 'YOUR FONT HERE'"; const b=x.measureText("CLAUDE.md").width;
console.log(a,b, b>a?"scales ✓":"BROKEN fallback — wrong family");
```

### TEXT INSIDE ILLUSTRATIONS MUST BE MOBILE-READABLE (HARD — locked 2026-05-30)
**Any text rendered inside a custom illustration (`type: "primitive"`) is for someone watching on a phone. It MUST be big enough to read at a glance.** Tiny labels (16-22px) get downscaled with the whole illustration and become an illegible smudge. Burned on the Cloud Code Folder reel: a 19px folder-tree label and 16px "chatbot / 10X" gauge labels were unreadable.

**Illustrations are NOT auto-fit to the zone.** The renderer draws `draw()` at its native pixels at the zone center (`ctx.scale` only applies if you pass `props.scale`). So on-screen text size = the literal `Npx` you set (assuming the font family actually works — see the Proxima Nova rule above). To make text bigger on screen: increase `Npx`. To enlarge the whole card+text together: pass `props.scale` on the beat. Making the card W/H bigger while scaling text by the same ratio changes NOTHING visible (the ratio is fixed) — that's a common dead-end; change the font px, not the card box.

Rules, all required:
- **Minimum 34px** for ANY text inside an illustration on the 1080-wide canvas. There is no such thing as a "small caption" inside a reel illustration.
- **Primary labels (the thing you're meant to read): 40-56px, weight 600-800.** Treat illustration labels like mini-pills, not footnotes.
- **Secondary/structural text** (file names in a tree, axis labels, tags): **34-44px minimum.** If a label can't fit at 34px, the illustration is too dense — cut rows/columns until the remaining labels fit big. Fewer, bigger items beats many tiny ones.
- **If text doesn't fit at 34px+, REMOVE it, don't shrink it.** Use the pill for the words and let the illustration carry the shape/icon only. The pill text is already large; don't duplicate small.
- **Cap the item count.** A file tree shows ≤5 rows, a comparison shows 2 sides, a gauge shows ≤2 labels — each at 40px+. Never a 6-row tree with 19px rows.
- **Self-audit before render:** open your `<reel>-illustrations.mjs`, grep every `ctx.font = "... Npx ..."`, and confirm every `N >= 34`. Any value under 34 inside a `draw` function is a bug — fix it before rendering.

This OVERRIDES "less is more" only on size: keep the composition minimal, but make whatever text survives LARGE.

### Layout
- Pill in `top-center` → visual in `top-left` or `top-right`.
- Pill in `top-left` → visual in `top-right`. Etc.
- Visual accompanies the pill for ~80%+ of the pill window with a slight stagger (e.g. pill `start: 0.10`, visual `start: 0.40`).

## 5. HARD RULES (always)

1. **ProRes 4444 alpha (`yuva444p10le` or `yuva444p12le`).** NEVER green screen. Renderer enforces. Verify with `ffmpeg -i out.mov 2>&1 | grep Stream`.
2. **Output is alpha-only, no audio.** you syncs in Descript.
3. **TOP-HALF SAFE ZONE ONLY.** Bottom 50% (y >= 960) is the face cam. Renderer throws if any element's cy > 900. Three zones: `top-left` (cx=360, cy=360), `top-center` (cx=540, cy=540), `top-right` (cx=720, cy=360).
4. **Max 4 words per text element.** CTA is exactly two words ("COMMENT X").
5. **One element per zone at a time.** Renderer throws on simultaneous same-zone overlap.
6. **Apple Color Emoji only.** Never Twemoji. Renderer calls `swift scripts/reel-overlay/render-apple-emoji.swift`.
7. **Clawd ONLY when topic IS Claude / Claude Code / Anthropic.** No Clawd on generic AI/ML/GPT/automation topics.
8. **Don't auto-commit.** you commits manually.
9. **NEVER auto-open the .mov.** Run `open ~/Downloads/` (reveals folder in Finder) and stop there. Never `open -a IINA`, never `open <file>.mov` — you opens it himself.
10. **Visuals match the literal words spoken.** "click" → cursor. "Cursor" → real Cursor logo. "tokens" → 💸. "147 agents" → agent grid illustration. Audit every beat.
11. **Logo PNGs ≥ 512px, icon-only, AND rasterized at NATIVE source aspect ratio.** Three sub-rules, all required:
    - **Icon-only, never wordmark.** The chip shows the brand name via `label`. A wordmark inside the PNG + label outside reads as a duplicated, overriding wordmark. If the source SVG is a wordmark (e.g. `coresignal.svg` at viewBox `0 0 166 32`), crop the viewBox first: `sed 's|viewBox="0 0 166 32"|viewBox="0 0 32 32"|; s|width="166"|width="32"|' in.svg > iconly.svg`.
    - **Rasterize at native SVG aspect, NEVER forced to 512×512.** Read the source SVG's `viewBox` / `width` / `height`. If aspect ≠ 1:1, render at `512×round(512 * h/w)` or `round(512 * w/h)×512`. Forcing a 22×26 SVG (HubSpot) or 290×200 SVG (n8n) into a 512×512 PNG embeds heavy transparent padding inside the bounding box — the renderer then scales the whole padded box to `logoSize`, so the visible icon ends up looking shrunk/squished while the empty padding eats the chip's interior space. Burned twice (n8n and HubSpot) on the Coresignal CRM reel 2026-05-14. Pattern:
      ```bash
      # source: viewBox="0 0 22 26"  → aspect 22:26 = 0.846
      rsvg-convert -w 512 -h 605 hubspot-bf.svg -o hubspot-iconly-512.png  # 512 * 26/22 ≈ 605
      # source: viewBox="0 0 290 200" → aspect 290:200 = 1.45
      rsvg-convert -w 512 -h 353 n8n-icon.svg -o n8n-icon-512.png         # 512 * 200/290 ≈ 353
      # Verify: bbox should hug the canvas edges. If bbox is (50, 50, 462, 462) on a 512×512 PNG, you padded.
      python3 -c "from PIL import Image; im = Image.open('out.png'); print(im.size, im.getbbox())"
      ```
    - **Save icon-only, native-aspect PNGs** as `<brand>-iconly-512.png` (the width is always 512; height varies with aspect). Audit every `type: "logo"` beat before render.
12. **NEVER ship a dark/solid-fill "counter card" illustration** with small label text (e.g. an INK/black rectangle with a big colored number on top and "data fields / per company" sub-labels). At reel scale inside a small top-zone, the micro-text becomes unreadable and the dark card disappears into dark face-cam footage. Big number reveals belong on a **pill** (`type: "keyword"` with the number as the text) or paired with a clean light-paper card matching the other illustrations — never a dark card with tiny labels in a small zone.
13. **Iterate to a NEW filename** (`v2`, `v3`, …). Don't overwrite — you compares versions.
14. **Variation:** never repeat `(Clawd expression, theme)` in one reel. Don't pile pills in one zone. Don't repeat the same emoji glyph.

## 6. PERFORMANCE (locked 2026-05-13)

The renderer is now **near-instant for iteration**. A 60s reel goes from ~60-90s end-to-end on the old sync path to **~5-10s** with the defaults below.

### What's on by default
- **`parallel: true`** — frames sharded across N worker_threads (auto = `os.cpus().length − 1`, clamped [2, 10]). ~6-8× faster than the sync loop on M-series. Each worker re-runs the entry script, hits the worker branch in `renderOverlay`, renders its slice, `process.exit(0)`s before any post-render code runs. No code change needed in existing scripts.
- **`master4k: true` (default)** — keeps historic 4K master output (1080p frames lanczos-upscaled to 2160×3840). **For fast iteration, override to `master4k: false`** in your script — IG/TikTok downscale to 1080p anyway, and this shaves the entire upscale pass. Flip back to `true` only for the final approved master you ships.
- **Shadow sprite cache** — emoji/Clawd/logo blurred shadows are cached per `(image, size, blur, alpha)`. Repeated raster beats stay cheap. Cache lives in each worker process.
- **Whisper file-hash cache** — `transcribeWithCache(audioPath)` SHA-1s the file and caches word-timestamps to `/tmp/reel-overlay-whisper-cache/<sha>.<model>.json`. Re-runs are instant.

### Override knobs
```js
await renderOverlay({
  name, duration, outputPath, beats,
  parallel: true,    // default. Set false ONLY when debugging a render bug.
  master4k: false,   // OVERRIDE: defaults to true for backwards-compat. Set false during iteration, flip to true on final.
  workers: 8,        // optional override. Default = os.cpus().length − 1, capped at 10.
});
```

### Known next-tier wins (not yet implemented)
If a future reel still feels slow:
1. **Raw RGBA pipe to ffmpeg stdin** (kill PNG encode + filesystem entirely). Expected: +30-50% on top of current. Pipe `canvas.toBuffer('raw')` straight to `ffmpeg -f rawvideo -pix_fmt bgra -i pipe:0`.
2. **`prores_videotoolbox` Apple Silicon hardware encoder** with `-profile:v 4444 -alpha_quality 1.0`. Expected: 3-10× faster encode, visually lossless. Verify output `pix_fmt` is still `yuva*`, fall back to `prores_aw` if VT drops alpha.
3. **Swap `node-canvas` → `@napi-rs/canvas`** (Skia + Metal-backed on macOS). Expected: 1.5-3× render speedup on text/Bezier-heavy passes. Mind premultiplied-vs-straight RGBA when piping raw.

Don't pre-implement — the current pipeline is fast enough for the daily reel cadence.

## 7. WORKFLOW

### 1. Verify file + duration
```bash
/usr/local/bin/ffmpeg -i "<path>" 2>&1 | grep Duration
```

### 2. Transcribe with cache (one call replaces ffmpeg-convert + whisper)
```js
// Inside your reel script:
import { transcribeWithCache } from "../../lib/reel-overlay/render.mjs";
const { text, words } = await transcribeWithCache("/path/to/source.wav");
// words: [{ start, end, word }, ...]
```
First run transcribes; subsequent runs on the same audio hit the cache and return in <50ms. Pass `{ force: true }` to re-transcribe. Pass `{ model: "medium" }` for better proper-noun accuracy on noisy clips (slower first run, then cached forever).

### 3. Decode common Whisper mishearings (don't re-run Whisper, fix in beat config)
- "torquence" / "torquens" → "tokens"
- "ICO" / "I-co" → "Haiku"
- "so net" → "Sonnet" · "open" → "Opus"
- "claud" / "cloud" → "Claude"
- "char gpt" → "ChatGPT"
- "Sledge" → "/" (slash-command prefix)
- "Entropy" → "Anthropic"
- "PlayDot" → "Playwright"

### 4. Map transcript → beats (8-14 beats per 30-60s reel)
Each beat declares: `id`, `type` (`hook` | `keyword` | `cta` | `emoji` | `clawd` | `logo` | `primitive`), `start`, `end`, `zone`, `inAnim`, `outAnim`, `idle`, `props`.

Beat-type guidelines:
- **hook**: First 3-5s. 2-4 words. `top-center`. Big font (70-84px), weight 900. `idle: false`. Use `inAnim: "fade"` + `outAnim: "fade"` with longer durations for a glitch-proof reveal.
- **keyword**: 1-2 words. 2-5s. Auto-picks seeded liquid palette (override with `palette`). Default font 56-76px.
- **emoji**: 2-3s. Apple iOS color glyph. Default size 200-240px. Single Unicode in `props.text`.
- **clawd**: 3-4s. From `scripts/drills/assets/media/clawd-*.png`. Default 240px. **Topic must be Claude.**
- **logo**: Brand logo + label, 3-4s. PNG ≥ 512px.
- **primitive**: Custom Canvas 2D illustration. `props.draw` is `(ctx, t, props) => void` drawing at the origin.
- **cta**: Last 4-6s. Two words. `top-center` with `cyOffset: 280` OR `top-left` with `cyOffset: 360`.

Vary in/out animations across neighbors. Never reuse the same `inAnim` twice in a row.

### 5. Generate per-reel script
Write `<your-project>/scripts/reel-overlay/<reel-name>.mjs`. If using custom illustrations, also write `<reel-name>-illustrations.mjs`. Reference: [agency-illustrations.mjs](../../../Desktop/your project/scripts/reel-overlay/agency-illustrations.mjs).

```js
import { renderOverlay } from "../../lib/reel-overlay/render.mjs";
import { drawOrgChart, drawParallelLanes } from "./<reel-name>-illustrations.mjs";

const LOGOS = "<your-project>/public/brand-logos";
const CLAWD = "<your-project>/scripts/drills/assets/media";

const P = {
  hook:  ["#5B1F0E", "#A04A2C", "#D97757", "#F2A684", "#FCDDC9", "#FFE8B8"],
  // ... one per beat
};

const beats = [
  { id: "hook", type: "hook", start: 0.05, end: 4.2, zone: "top-center",
    inAnim: "fade", outAnim: "fade", inDur: 0.5, outDur: 0.4, idle: false,
    props: { text: "Your Hook", fontSize: 76, fill: P.hook[1], textColor: "#FFFFFF", palette: P.hook } },

  { id: "viz-org", type: "primitive", start: 8.2, end: 12.0, zone: "top-right",
    inAnim: "fade", outAnim: "fade", idle: false,
    props: { draw: drawOrgChart } },

  { id: "logo-cursor", type: "logo", start: 12.2, end: 14.5, zone: "top-left",
    inAnim: "drop", outAnim: "snap-up",
    props: { src: `${LOGOS}/cursor-512.png`, label: "Cursor", logoSize: 90, fontSize: 56,
             fill: P.cursor[1], textColor: "#FFFFFF", palette: P.cursor } },

  { id: "emoji-spark", type: "emoji", start: 17.0, end: 19.0, zone: "top-right",
    inAnim: "pop", outAnim: "fade", idle: "pulse",
    props: { text: "✨", size: 200 } },

  { id: "cta", type: "cta", start: 49.0, end: 54.4, zone: "top-center",
    cyOffset: 280, inAnim: "pop", outAnim: "fade", idle: "pulse",
    props: { cta: "Comment", keyword: "WORD", palette: P.cta } },
];

await renderOverlay({
  name: "your-reel-name",
  duration: 54.5,
  outputPath: "~/Downloads/<source-file-base> - Reel Overlay.mov",
  beats,
  master4k: false, // fast iteration; flip to true (or remove) for the final 4K master.
});
```

### 6. Smoke 3-5 frames before full render
Add `smokeT: [t1, t2, t3]` to `renderOverlay`. Read each PNG to verify zones, palette, no overlap. (Smoke uses the sync path; parallel kicks in only for full renders.) Iterate then remove `smokeT` and run the full render.

### 7. Full render (parallel, 1080p iteration with `master4k: false`)
```bash
cd ~/Desktop/your project && node scripts/reel-overlay/<reel-name>.mjs
```
With `master4k: false` set in the script during iteration, expected wall-clock: ~5-15s for a 60s reel after the first run (Whisper cached, sprite cache warm, 10 workers, no 4K upscale). With `master4k: true` (or default, omitted) the lanczos upscale adds 5-15s depending on duration.

### 8. Final master pass (only when you approves)
Remove `master4k: false` (or set it to `true`) and re-run — produces the 4K lanczos-upscaled master.

### 9. Verify alpha and reveal in Finder
```bash
/usr/local/bin/ffmpeg -i "<output.mov>" 2>&1 | grep Stream
# MUST start with yuva
open ~/Downloads/
```
Folder reveal only. NEVER `open -a IINA` or `open <file>.mov` — you opens it himself.

## 8. LIBRARY CONSTANTS

**Zones** (centroids on 1080x1920 canvas, top-half only):
- `top-left` `(360, 360)`, `top-center` `(540, 540)`, `top-right` `(720, 360)`
- `cyOffset` pushes within top half (CTA `cyOffset: 280` → cy 820, still safe)

**Output**: 4K vertical (2160×3840), 30fps, ProRes 4444 alpha, `-qscale:v 9`. Master is 4K; Instagram downscales to 1080p.

**Performance**: Canvas renders at 1080p, ffmpeg lanczos upscales to 4K. ~2.4-3× realtime on M-series. Smoke 1-3 frames first via `smokeT` before burning full renders.

**Anim envelope props**: `inAnim` (`pop` | `slide-up` | `slide-down` | `slide-left` | `slide-right` | `drop` | `fade`), `outAnim` (`pop` | `snap-up` | `snap-down` | `slide-left` | `slide-right` | `fade`), `idle` (`bob` | `breathe` | `pulse` | `false`).

**Custom illustration helpers** to copy when authoring `<reel>-illustrations.mjs`:
```js
function shadow(ctx, fn, { blur = 18, offsetY = 8, alpha = 0.16 } = {}) { /* … */ }
function roundRect(ctx, x, y, w, h, r) { /* … */ }
const breathe = (t, freq = 1.2, amp = 0.012) => 1 + Math.sin(t * freq) * amp;
```

## 9. FAILURE MODES

- `max 4 words per element` — shorten the text.
- `CTA must be exactly two words` — `cta="Comment"` + `keyword="<single word>"`.
- `simultaneous beats share zone X` — move one OR stagger times.
- `top-half-only safe zone... cy > 900` — raise the beat OR use `cyOffset` to stay in top half.
- `Beat must specify zone or cx/cy` — forgot the `zone` field.
- Apple emoji render failed — `swift` not on PATH OR Apple Color Emoji font missing.
- Non-yuva pixel format → alpha lost. Renderer enforces; if you see this, something bypassed the renderer.
- Whisper misheard a brand/word → correct in beat config (don't re-run Whisper).
- Logo renders blurry → source PNG too small. Re-rasterize from SVG at ≥512px.
- Black square / hard-edge shadow behind emoji or Clawd → node-canvas issue #1696. Use `rasterShadow()` helper, never `ctx.shadowBlur` directly on `drawImage` under a scaled context.
- Pill all renders default coral/cream despite setting `fill` → `palette` not set. Add the 6-stop array to props.
- Claude logo black → use `claude-512.png` (rasterized in `#D97757`), not the raw `lh-claude.svg`.
- "parallel render needs process.argv[1]" → don't call `renderOverlay` from a REPL/eval. Run as a script file (`node scripts/reel-overlay/<reel>.mjs`). Workers re-import that path.
- Output is 1080p when you wanted 4K → flip `master4k: true` on the renderOverlay call for the final master pass.
- Worker count too high → pass `workers: 4` to renderOverlay (default = `os.cpus().length − 1`, capped at 10).

## 10. RELATED SKILLS

- `/clawd-overlay` — Clawd-mascot-only overlay, no pills. When topic IS Claude AND only mascots wanted.
- `/reel-visual` — replaces top half with full custom scene. When topic needs heavy info-visual support.
- `/reel-overlay` (this skill) — sparse premium liquid pills + paired visuals on top of face cam.
