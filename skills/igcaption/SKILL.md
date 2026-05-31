---
name: igcaption
description: "Generate Instagram captions for your reels and videos. Invoke as /igcaption with a transcript. Produces 3 unique caption variants, your real voice, tool-per-line format, closing mindset line + optional CTA. Use when: user says /igcaption, wants an Instagram caption, needs a caption for a reel, or mentions writing a caption for a post."
---

# Instagram Caption Generator

## Inputs

The user provides ONE of these:
1. **Transcript** -- full video/reel transcript, OR
2. **Session context** -- the current carousel/series/project we've been building this session. If the session is clearly focused on one content piece (a carousel, a reel series, a specific topic), that IS the transcript-equivalent. Use it.
3. **CTA keyword** (optional, usually inferable)

## NEVER ask obvious questions. NEVER ask for a transcript if session context already tells you what the content is about.

**HARD RULE:** If the user invokes `/igcaption` and we have been actively building a specific piece of content this session (a 15 Research Papers carousel, a Claude Code reel, a SaaS Recipe series, etc.), you already know:
- **The topic** -- it's the thing we're building
- **The core concepts** -- they're in the source files, the data arrays, the slide content we wrote
- **The CTA keyword** -- it's whatever the CTA slide says ("PAPER", "GUIDE", "SETUP", etc.)
- **The tools/items** -- they're already listed in the project data (e.g. the 15 papers with their arxiv links)

**Use the session context as the transcript.** Write captions about the content we've been building. Do NOT ask "please paste the transcript" when you already know exactly what the video is about.

Things NEVER to ask:
- "What's the transcript?" -- Use session context if we're mid-project
- "What's the CTA keyword?" -- Check the CTA slide in the current project
- "What's the topic?" -- It's the series we're building
- "What's the city/location/date/background?" -- Irrelevant to caption writing
- "Is there a lead magnet?" -- Assume yes, use the current series' CTA

Only ask if:
- `/igcaption` is invoked with ZERO session context (first message, fresh conversation, no project in progress) AND
- No transcript was pasted AND
- No content area is being worked on

In that one rare case, ask for "a transcript OR topic." Never use the word "required."

Otherwise: one-shot the 3 captions from what you already know.

## Process

1. **Infer** all inputs (CTA, topic, tone) from context and the transcript. Do NOT ask.
2. **Read the transcript** to understand the TOPIC and CONCEPT -- not to copy words from it
3. **Identify the core idea** in one sentence (don't write this down, just internalize it)
4. **Write 3 caption variants** following your EXACT format below
5. **Run /humanizer on each variant** -- apply the full humanizer skill to remove all AI writing patterns
6. **Output all 3 variants** labeled A, B, C with character count next to each

## Character Rules

- **Target: 350-500 characters** per caption (letters, spaces, punctuation all count)
- **Hard minimum: 300 characters** -- never go below this
- **Hard maximum: 500 characters** -- never exceed
- Show the exact character count next to each variant like: **(487 chars)**

## The Golden Rule

**NEVER transcribe.** The transcript is context, not source material. You understand what the video is about, then you write something original about that topic. If any sentence in the caption could be found in the transcript, you've failed. Write from the concept, not from the words.

## Format — RANDOM SHAPE PER VARIANT (HARD RULE)

**Every caption variant MUST use a different shape.** your captions don't follow one template — they vary in rhythm, structure, opening style, and closing style. Three variants in the SAME shape = failure. The reader should feel like three different humans wrote A, B, and C.

### Shape pool — pick a different one for each variant

Pick A, B, C from THREE DIFFERENT entries in this pool. Never repeat a shape across the same output. Rotate which shapes you use across sessions so your feed never feels templated.

1. **Tool-per-line list with personal opening** (the classic — only ONE of three captions can use this)
   ```
   Vibe coding has me building things I never thought I could.
   Claude writes the code,
   Supabase handles the data,
   Vercel deploys it live,
   and n8n automates everything behind the scenes 🔥

   Pick your stack and stop overthinking... that's the whole game.
   ```

2. **Stat / number drop opening** — lead with a hard number, then unpack
   ```
   147 sub agents. One repo. Sorted by department.

   Engineering builds. Marketing writes. Sales sells. Support closes.
   Each one with its own personality, role, and way of working.

   Comment AGENCY and the GitHub link lands in your DMs 🔥
   ```

3. **Contrarian / pattern-interrupt opening** — call out what most people get wrong
   ```
   Most people are still running one overworked AI agent and wondering why the output feels flat.

   Meanwhile someone just open-sourced a full agency. 147 specialists. Org chart structure. Plug-and-play with Claude Code, Cursor, or Codex.

   It's not a display repo. It's the real org you've been trying to build solo for six months.

   Comment AGENCY → DM 🚀
   ```

4. **One-liner thesis + paragraph unpack** — a single bold sentence, then one tight paragraph
   ```
   You don't need a smarter agent. You need an org chart.

   That's the whole shift. Stop asking one model to be the engineer, the designer, the marketer, and the support rep. Give each role its own agent and let them work in parallel.

   Drop "AGENCY" in the comments and I'll send it your way ⚡
   ```

5. **Question hook opening** — open with a real question the viewer is asking
   ```
   Why does your AI agent feel exhausted after every prompt?

   Because you're asking one model to do the job of 147. Engineering, design, marketing, sales, support — all in one chat window.

   This repo splits the load. Comment AGENCY for the link 🔥
   ```

6. **Story / scene opening** — drop the reader into a moment
   ```
   Was scrolling GitHub last night and someone open-sourced a full AI agency.

   Not a prompt template. Not a starter pack. A real org chart with 147 specialized agents — engineering, sales, marketing, support — each with their own personality and deliverables.

   Plug it into Claude Code or Cursor and you're running a team. Comment AGENCY 🚀
   ```

7. **Two-column comparison** — old way vs new way, written as prose lines
   ```
   Old way: one AI agent juggling everything. Burns tokens. Forgets context. Hallucinates the brief.

   New way: 147 specialists, each with one job, working in parallel through an org chart.

   Free, MIT, plugs into Claude Code. Comment AGENCY for the repo ⚡
   ```

8. **Direct address / second-person callout** — speaks directly to the reader's situation
   ```
   If your agent feels overworked, it's because you're using it like a chatbot.

   Stop. Give it an org chart instead. 147 specialized sub agents. Engineering, design, sales, marketing, support — each in their own lane, all running in parallel.

   Comment AGENCY and I'll send the GitHub link 🔥
   ```

9. **Curiosity gap opening** — tease the thing without naming it
   ```
   Someone just shipped the wildest open-source AI repo I've seen this month.

   147 sub agents. Sorted into 6 departments. Each with a defined role, personality, and deliverable. Drops straight into Claude Code or Cursor.

   This is what AI teams are supposed to feel like. Comment AGENCY 🚀
   ```

10. **Realization / before-and-after personal arc**
    ```
    The day I stopped using AI like a chatbot and started running it like a company, everything changed.

    147 specialists instead of one generalist. An engineering team, a marketing team, a support team — all working in parallel, each owning one domain.

    Comment AGENCY and the link is yours ⚡
    ```

### Variant requirements

- **Each variant uses a different shape from the pool above.** A, B, C must come from three distinct entries.
- **The CTA still lands at the end** in every shape — but how it lands changes (a closing line, a one-liner, a → arrow, a parenthetical, integrated into the final thought).
- **One emoji max** per caption, placed wherever fits the shape (end of list, end of CTA, end of closing line).
- **No template-feel.** If A, B, C all open with a personal sentence, you've failed. Vary opening style: number / question / story / contrarian / direct-address / etc.

### CTA handling

The CTA keyword (when provided) must appear in every variant but the framing changes per shape:
- Shape 2: "Comment AGENCY and the GitHub link lands in your DMs 🔥"
- Shape 3: "Comment AGENCY → DM 🚀"
- Shape 4: "Drop \"AGENCY\" in the comments and I'll send it your way ⚡"
- Shape 7: "Free, MIT, plugs into Claude Code. Comment AGENCY for the repo ⚡"
- Etc. Never bolt the CTA on identically across all three.

## Voice Rules

- Write like you texts his audience -- casual, direct, confident
- Short sentences. Fragments are fine.
- "has me", "got me", "changed how I" -- natural contractions
- ONE emoji per caption, placed at the end of the tool list (not the opening, not the closing)
- Allowed emojis: pick ONE that fits the vibe. Common ones you uses: fire, mind-blown, rocket, check mark, lightning

## Each Variant Must Be Different — IN SHAPE AND IN SOUL

The 3 variants MUST differ in BOTH:
- **Shape** -- pull from three distinct entries in the shape pool above (number drop / contrarian / story / question / one-liner thesis / etc.)
- **Soul** -- different opening emotion, different framing, different closing philosophy

If A, B, and C all use the same structural skeleton (e.g. all three are "personal opening + tool-per-line list + closing mindset"), the output is a failure. Re-roll until each variant is genuinely different in form, not just word choice.

## NEVER Do

- No hashtags. Zero. Ever.
- No more than ONE emoji per caption
- Never start any sentence with "I" as the first word of the caption
- Never use "In this video" or "Here's what I cover" or "Let me explain"
- Never use filler: "So basically", "The thing is", "Here's the deal"
- Never use corporate speak: "leverage", "optimize", "streamline", "utilize"
- Never use AI vocabulary: "delve", "landscape", "tapestry", "crucial", "foster"
- Never use em dashes
- Never copy phrases directly from the transcript
- Never write dense paragraphs -- use the line-per-tool format
- Never use "Not only X, but also Y" (negative parallelism)
- Never use promotional language: "game-changer", "revolutionary", "powerful"
- Never feel templated -- if someone read all 3 variants and thought "these follow the same formula", you've failed. Same shape, different soul.

## Humanizer Pass (MANDATORY)

After writing each variant, apply the /humanizer skill mentally:
1. Check for AI writing patterns (per the humanizer skill's full checklist)
2. Remove any sycophantic tone, filler phrases, excessive hedging
3. Add personality -- opinions, varied rhythm, specificity
4. Read it out loud mentally -- does it sound like you posted this?
5. If it sounds like ChatGPT wrote it, rewrite from scratch

## Output Format

Output exactly this:

---

**A** (XXX chars)

[caption text]

---

**B** (XXX chars)

[caption text]

---

**C** (XXX chars)

[caption text]

---

No extra commentary before or after. Just the 3 variants.
