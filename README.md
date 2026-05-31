# 🎬 LeadGenMan Video Skills — Automated Content Pipeline for Claude Code

**By Manthan Patel (@LeadGenMan)**

🔗 [LinkedIn](https://www.linkedin.com/in/leadgenmanthan/) • 📸 [Instagram](https://www.instagram.com/leadgenman/) • 🎥 [YouTube](https://www.youtube.com/@LeadGenMan) • 🎵 [TikTok](https://www.tiktok.com/@leadgenmanthan) • 🎓 [Skool Community](https://www.skool.com/ai-inner-circle/about) • 🎬 [TiltIt](https://tiltit.video) • ✏️ [PenAnywhere](https://apps.apple.com/us/app/penanywhere/id6760774183) • 🗣️ [Impromptly AI](https://impromptly.ai/)

* * *

Six Claude Code skills I use to take a video from a raw face-cam recording all the way to a posted Reel or YouTube upload, almost entirely hands-free. Drop them into Claude Code and run them by name.

> Looking for the sound-effects skill? It lives in its own repo: **[soundeffects-claude-code](https://github.com/manthanpatelll/soundeffects-claude-code)**.

## 🧰 The skills

| Skill | What it does | Runs standalone? |
|-------|--------------|------------------|
| **`/produce`** | Autonomous rough cut. Removes retakes, false starts, dead air, and side conversations from a raw face-cam recording. Waveform-first + per-chunk Whisper. | ✅ Yes (bundled Python engine) |
| **`/srt`** | Caption cleaner. Fixes spelling, punctuation, and proper-noun capitalization in `.srt` files without ever touching timestamps or block structure. | ✅ Yes (pure workflow) |
| **`/ytdescription`** | Generates a full YouTube description in a locked organic-video format: hook, benefits, products, comment CTA, socials, and accurate chapters from the transcript. | ✅ Yes (pure workflow) |
| **`/igcaption`** | Writes 3 distinct Instagram caption variants in a real human voice, each with a different structural shape, with a built-in humanizer pass. | ✅ Yes (pure workflow) |
| **`/reel-overlay`** | Generates a 4K vertical ProRes 4444 **alpha** overlay (`.mov`) for split-screen reels: top half is the overlay, bottom half is your face cam. | 📘 Reference (needs a renderer) |
| **`/new-series`** | Scaffolds a complete Canvas 2D content series (carousel, IG reel, or YouTube video) with animations and export buttons. | 📘 Reference (needs an engine) |

`/reel-overlay` and `/new-series` were extracted from a private content-production app. They reference an internal Canvas 2D engine, renderer, fonts, and brand assets that are not bundled here, so they ship as **reference blueprints**: read them to see the full workflow and adapt the patterns to your own stack.

## 📁 Structure

```
leadgenman-video-skills/
├── .claude-plugin/
│   └── plugin.json
├── engine/                 # Python rough-cut engine for /produce
│   ├── roughcut.py
│   └── pyproject.toml
├── skills/
│   ├── produce/SKILL.md
│   ├── srt/SKILL.md
│   ├── ytdescription/SKILL.md
│   ├── igcaption/SKILL.md
│   ├── reel-overlay/SKILL.md
│   └── new-series/SKILL.md
├── LICENSE
└── README.md
```

## 📦 Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- For `/produce`: Python 3.10+, [uv](https://docs.astral.sh/uv/), ffmpeg, and an `OPENAI_API_KEY` (per-chunk Whisper transcription)

## 🚀 Install

Add it directly from GitHub in Claude Code:

```
/plugin install github:manthanpatelll/leadgenman-video-skills
```

Or clone and install locally:

```bash
git clone https://github.com/manthanpatelll/leadgenman-video-skills.git

# Install the /produce engine deps
cd leadgenman-video-skills/engine
uv sync

# Install the plugin in Claude Code
claude plugin install /path/to/leadgenman-video-skills
```

## 💬 Usage

In Claude Code:

```
/produce:produce /path/to/raw-video.mp4
/srt:srt /path/to/captions.srt
/ytdescription:ytdescription            # paste or point at a transcript
/igcaption:igcaption                    # paste or point at a transcript
```

The `/ytdescription` and `/igcaption` skills keep my own socials, products, and Skool community as a working example. Edit the locked lines in their `SKILL.md` to make them yours.

## 📺 The pipeline (how I use them together)

1. Record a raw face cam (retakes and all).
2. `/produce` → clean rough cut.
3. Edit / animate (`/new-series`, `/reel-overlay`, and the separate sound-effects skill).
4. `/srt` → clean the burnt-in captions.
5. `/ytdescription` + `/igcaption` → package and post.

## 🔗 Connect with me

* Instagram: https://www.instagram.com/leadgenman/
* LinkedIn: https://www.linkedin.com/in/leadgenmanthan/
* Facebook: https://www.facebook.com/leadgenman/
* TikTok: https://www.tiktok.com/@leadgenmanthan
* YouTube: https://www.youtube.com/@LeadGenMan
* Community: https://www.skool.com/ai-inner-circle/about

## 🛠️ My products

* TiltIt: https://www.tiltit.video
* PenAnywhere: https://apps.apple.com/app/penanywhere/id6760774183
* Impromptly AI: https://impromptly.ai/

## 📄 License

MIT
