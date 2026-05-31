---
name: ytdescription
description: Generate a YouTube video description in your locked organic-video format. Use whenever the user types "/ytdescription", "yt description", "YouTube description", "video description with chapters", or provides a transcript/video/audio file and asks to package it for YouTube. ALWAYS pull the transcript first from whatever source you provides (audio file, video file, SRT, or prior conversation) — never ask which source to use, never ask clarifying questions. Just do it.
---

# YouTube Description Generator

Generate a YouTube video description in your locked organic-video format. This skill is for HIS OWN long-form tutorials (not sponsored videos — see the old Cotera reference in git history if a sponsored format is needed).

## Hard Rules

1. **NEVER ASK CLARIFYING QUESTIONS.** you gives a file path or pastes a transcript — get to work immediately. Trust the input. If the file doesn't exist, only then report back.
2. **Transcribe first if needed.** If you provides a video/audio path, run Whisper to extract a word-level transcript before mapping chapters.
3. **Block order is LOCKED.** Do not reorder. See template below.
4. **Chapters are accurate and concise.** Maximum 6-8 chapters for a 10-20 min video. Do NOT create one chapter per tool — group by section/layer/topic. Each chapter title lists what's covered in parentheses if multiple sub-items.
5. **First chapter MUST be `0:00`** or YouTube won't render chapters.
6. **No email in socials.** Use the 5 social platforms plus the Community line only (Instagram, LinkedIn, Facebook, TikTok, YouTube, Community). Exact order locked.
7. **No em dashes (`—`)** or double hyphens in user-facing copy. Use commas/periods/parentheses. Two short sentences > one with a dash. (Exception: chapter titles may use `—` as a separator between section number and content, as it reads cleanly in YouTube's chapter UI. Locked.)
8. **No emojis in the body** (except inside chapter labels if you adds them). Plain text headers — no 🎓 🛠️ 📬 ⏱️ at section heads.
9. **Hashtags**: exactly 3, all lowercase, on one line, at the very bottom.
10. **Output as a single fenced code block** so you can copy-paste straight into YouTube Studio.

## Locked Template

```
Learn more {Skool Community}: https://www.skool.com/ai-inner-circle/about

{TITLE — the actual YouTube video title, e.g. "Why Vibe Coding Fails Without the Full SaaS Stack"}

{One-paragraph description, 2-4 sentences. Plain English. Names the products built with the stack/method. NO em dashes. NO hype words.}

In this video you'll learn:
• {Benefit 1 — 5-10 words}
• {Benefit 2 — 5-10 words}
• {Benefit 3 — 5-10 words}
• {Benefit 4 — 5-10 words}

MY SAAS PRODUCTS (built with this exact stack)
TiltIt: https://tiltit.video [3D animation software]
PenAnywhere: https://apps.apple.com/us/app/penanywhere/id6760774183 [Annotator App]
Impromptly AI: https://impromptly.ai/ [English Speaking Coach, Impromptu Generator]

Comment "{KEYWORD}" and I'll DM you the full Notion checklist with {what the checklist contains — 5-10 words}.

If this saved you weeks of trial-and-error, hit subscribe — I drop one builder-to-builder tutorial every week.

CONNECT WITH ME
* Instagram: https://www.instagram.com/leadgenman/
* LinkedIn: https://www.linkedin.com/in/leadgenmanthan/
* Facebook: https://www.facebook.com/leadgenman/
* TikTok: https://www.tiktok.com/@leadgenmanthan
* YouTube: https://www.youtube.com/@LeadGenMan
* Community: https://www.skool.com/ai-inner-circle/about

CHAPTERS
0:00 {Hook / Intro chapter title}
{MM:SS} {Section 1 — short label (tools/topics inside in parens if multiple)}
{MM:SS} {Section 2 — short label}
{MM:SS} {Section 3 — short label}
{MM:SS} {Section 4 — short label}
{MM:SS} {Section 5 — short label}
{MM:SS} {Final chapter — usually the CTA / payoff / outro}

#{hashtag1} #{hashtag2} #{hashtag3}
```

## Block Order (LOCKED — never deviate)

1. **Skool community link** — `Learn more {Skool Community}: https://www.skool.com/ai-inner-circle/about`
2. **Title** — the actual YouTube title, no quotes around it, plain line
3. **One-paragraph description** — 2-4 sentences, plain English, names the products
4. **"In this video you'll learn:"** — 4 bullets, each 5-10 words, benefit-driven
5. **MY SAAS PRODUCTS** — the 3 products with bracketed descriptors (locked exact format)
6. **Comment bait CTA** — `Comment "KEYWORD" and I'll DM you...`
7. **Subscribe line** — `If this saved you weeks of trial-and-error, hit subscribe...`
8. **CONNECT WITH ME** — 5 socials + Community line, all with bullet asterisks. Community line is labeled `Community` (never `Skool`).
9. **CHAPTERS** — 6-8 chapters max, first one is `0:00`
10. **Hashtags** — 3, lowercase, single line

## Hard-Coded Lines (NEVER change these)

These lines are templated and do NOT vary between videos. Reuse verbatim:

```
Learn more {Skool Community}: https://www.skool.com/ai-inner-circle/about
```

```
MY SAAS PRODUCTS (built with this exact stack)
TiltIt: https://tiltit.video [3D animation software]
PenAnywhere: https://apps.apple.com/us/app/penanywhere/id6760774183 [Annotator App]
Impromptly AI: https://impromptly.ai/ [English Speaking Coach, Impromptu Generator]
```

```
If this saved you weeks of trial-and-error, hit subscribe — I drop one builder-to-builder tutorial every week.
```

```
CONNECT WITH ME
* Instagram: https://www.instagram.com/leadgenman/
* LinkedIn: https://www.linkedin.com/in/leadgenmanthan/
* Facebook: https://www.facebook.com/leadgenman/
* TikTok: https://www.tiktok.com/@leadgenmanthan
* YouTube: https://www.youtube.com/@LeadGenMan
* Community: https://www.skool.com/ai-inner-circle/about
```

## Variable Lines (write fresh per video)

- **Title** — pull from your stated title or derive from transcript topic
- **Description paragraph** — 2-4 sentences summarizing the video's promise
- **"In this video you'll learn"** — 4 benefit bullets
- **Comment keyword** — pick one strong keyword from the video (STACK, CLAUDE, AGENTS, etc.) + describe what the giveaway is
- **Chapters** — 6-8 max, mapped from transcript
- **Hashtags** — 3 lowercase tags, all relevant to the video topic

## Workflow

### Step 1 — Get the transcript
If you provides a video/audio file:
```bash
# extract audio if video
/usr/local/bin/ffmpeg -i <input> -vn -acodec pcm_s16le -ar 16000 -ac 1 /tmp/ytdesc_audio.wav -y

# Whisper word-level timestamps
cd <your-project>/scripts/sfx-engine
uv run python -c "
import whisper
m = whisper.load_model('base')
r = m.transcribe('/tmp/ytdesc_audio.wav', word_timestamps=True, language='en')
for seg in r['segments']:
    print(f'[{seg[\"start\"]:7.2f}s] {seg[\"text\"].strip()}')
"
```
If transcript is in the conversation already (e.g. just generated for /soundeffects on same video), reuse it. Don't re-transcribe.

### Step 2 — Map chapters (max 6-8)
Read the transcript and find 6-8 natural section breaks. For tutorial videos, group by topic/layer/section, NOT by individual tool. Example for a 17-tool video → 6 chapters (intro + 5 layers + outro), not 19 chapters.

Format: `MM:SS Section name` or `MM:SS LAYER N — Section (tool1, tool2, tool3, tool4)`.

First chapter is always `0:00`. Chapter titles are 4-10 words, no clickbait punctuation.

### Step 3 — Write the variable lines
- Title (from your direction or transcript)
- 2-4 sentence description
- 4 benefit bullets
- Comment keyword + checklist promise
- 3 hashtags

### Step 4 — Assemble and ship
Print the entire description in ONE fenced code block. End the response with one short line like "Ship it." — no commentary on what changed unless you asks.

## Reference Example (locked golden output, 2026-05-14)

```
Learn more {Skool Community}: https://www.skool.com/ai-inner-circle/about

Why Vibe Coding Fails Without the Full SaaS Stack

Vibe coding alone won't ship a real SaaS. Here's the full 17-tool stack I use to take a vibe coded app from idea to a production-ready SaaS handling thousands of paying users, the same stack behind TiltIt, PenAnywhere, and Impromptly AI.

In this video you'll learn:
• The 5 layers of a production-ready vibe coding stack
• Why Cursor / Claude Code alone is not enough
• The exact tools for hosting, payments, monitoring, and growth
• How to ship 3 paid apps in 3 months as a solo founder

MY SAAS PRODUCTS (built with this exact stack)
TiltIt: https://tiltit.video [3D animation software]
PenAnywhere: https://apps.apple.com/us/app/penanywhere/id6760774183 [Annotator App]
Impromptly AI: https://impromptly.ai/ [English Speaking Coach, Impromptu Generator]

Comment "STACK" and I'll DM you the full Notion checklist with every tool, pricing tier, and setup order.

If this saved you weeks of trial-and-error, hit subscribe — I drop one builder-to-builder tutorial every week.

CONNECT WITH ME
* Instagram: https://www.instagram.com/leadgenman/
* LinkedIn: https://www.linkedin.com/in/leadgenmanthan/
* Facebook: https://www.facebook.com/leadgenman/
* TikTok: https://www.tiktok.com/@leadgenmanthan
* YouTube: https://www.youtube.com/@LeadGenMan
* Community: https://www.skool.com/ai-inner-circle/about

CHAPTERS
0:00 Why most vibe coded apps die
1:06 LAYER 1 — Build (Claude Code, Cursor, Next.js, GitHub)
4:25 LAYER 2 — The Spine (Vercel, Supabase, Stripe, Cloudflare)
9:03 LAYER 3 — Monitoring (Sentry, BetterStack, PostHog, Upstash)
12:03 LAYER 4 — Communication (Resend, Loops, Intercom, Trigger.dev)
14:14 LAYER 5 — Growth (Headless WordPress, Google Search Console)
15:23 The real cheat sheet

#vibecoding #saasbuilder #leadgenman
```

## What this skill never does

- Never asks "which source?" or "what title?" — uses what you provided
- Never adds an Email line to CONNECT WITH ME
- Never adds X/Twitter (deleted account)
- Never creates more than 8 chapters
- Never creates one chapter per tool (group by section/layer)
- Never adds emoji section markers (🎓 🛠️ 📬 ⏱️)
- Never reorders the locked blocks
- Never changes the hard-coded product/social/Skool/subscribe lines
- Never invents product descriptors — TiltIt = "3D animation software", PenAnywhere = "Annotator App", Impromptly AI = "English Speaking Coach, Impromptu Generator" (LOCKED)
- Always uses the full `https://impromptly.ai/` URL for Impromptly AI (with the https:// prefix and trailing slash) so it links cleanly in YouTube
- Never labels the Skool entry as "Skool" in CONNECT WITH ME — always `* Community: https://www.skool.com/ai-inner-circle/about`
