---
name: srt
description: Fix spelling, punctuation, and proper-noun capitalization errors in SRT subtitle/caption files while preserving timestamps, block indices, and line structure exactly as-is. Use whenever the user invokes /srt followed by a file path, drags an .srt file, or asks to clean, fix, correct, or proofread a caption/subtitle/transcript file. Workflow always: read the file, derive context keywords from THAT file only (never from any hardcoded list), present keywords to the user for approval and additions, then rewrite only misspellings and punctuation and save as Updated_<original>.srt in ~/Downloads/.
---

# SRT Caption Fixer

Fix spelling + punctuation errors in auto-generated subtitle files (YouTube auto-captions, video editor transcribers, Whisper output, etc.) without touching timestamps, block indices, or line structure.

## Absolute Rules — Read First

1. **Nothing is hardcoded, global, or universal.** There is no baked-in dictionary of terms. Every single correction is derived fresh from the specific file being processed. Never assume a word like "cloud code" should become "Claude Code" based on prior conversations or other files — only act on evidence inside the current file and the user's confirmed keyword list.
2. **Never alter timestamps.** Not the hours, minutes, seconds, milliseconds, `-->` arrow, or comma decimal separator.
3. **Never alter block indices.** The `1`, `2`, `3`... numbering stays byte-identical.
4. **Never merge or split blocks.** Block count in = block count out.
5. **Never reflow text within a block.** If a block has two lines, keep two lines with the same break point.
6. **Never rewrite phrasing, reorder words, or "improve" grammar.** Only fix: spelling typos, missing/wrong punctuation, apostrophes, sentence-start capitalization, and user-confirmed proper-noun capitalization.
7. **Never invent content** that isn't in the original.

## Workflow

### Step 1 — Receive input
User invokes the skill with an absolute path, typically by dragging an `.srt` file into the prompt. Example: `/srt ~/Desktop/episode-42.srt`

### Step 2 — Read the file
Use the Read tool with the absolute path. If the path is missing, ask for it once.

### Step 3 — Validate SRT structure
Confirm the file matches SRT format: repeating blocks of
```
<index>
<HH:MM:SS,mmm> --> <HH:MM:SS,mmm>
<text line 1>
[optional text line 2+]
<blank line>
```
If it isn't valid SRT, stop and tell the user what's wrong.

### Step 4 — Derive context keywords AND punctuation/capitalization fixes FROM THIS FILE ONLY
Read through the entire transcript and identify TWO categories of corrections:

**A. Proper-noun / spelling corrections (require user approval):**
- The topic/domain of the video (one line summary)
- Recurring proper nouns, product names, tool names, people names, company names, acronyms
- Terms that look like mis-transcriptions (phonetic mismatches, unusual spacing, nonsense words repeated multiple times)
- Technical jargon specific to the video's subject

Do NOT pull terms from memory, prior conversations, other SRT files, or any hardcoded list. Every keyword must be traceable to text that exists in the current file.

Count occurrences of each candidate term so the user can see impact.

**B. Punctuation + capitalization issues (apply by default — surface in approval list so user can veto specific ones):**

Scan EVERY block for these issues. This step is mandatory on every run, not optional:

- **Missing sentence-end punctuation** when a block clearly ends a complete thought and the next block starts a new one. (e.g. block ending "if you want" → "if you want.")
- **Run-on without separator** where a capital letter starts mid-block with no preceding punctuation. (e.g. "magnifier Now let's say" → "magnifier. Now let's say")
- **Lowercase sentence start** at the beginning of a block when the prior block ended with a period/question/exclamation. (e.g. "and feel free" after a "." → "And feel free")
- **Wrong separator before a new clause-start word like "So" / "It" / "Now" capitalized after a comma** — usually means the comma should be a period. (e.g. "pointer trail, So let's say" → "pointer trail. So let's say")
- **Missing apostrophes** in contractions: `dont` → `don't`, `cant` → `can't`, `wont` → `won't`, `Im` → `I'm`, `youre` → `you're`, `its` → `it's` ONLY when context makes "it is" unambiguous.
- **Obvious spelling typos** that don't depend on domain knowledge (e.g. "teh" → "the", "recieve" → "receive").
- **Dangling fragments** from transcription glitches like "and . That" or " . " mid-sentence — propose a clean fix.

Do NOT fix:
- Spoken grammar errors (e.g. "which will having", "I have keep it", "this is will be") — those are speech patterns, not transcription errors. Leave them.
- Filler words (um, uh, like).
- Stylistic comma choices when the sentence is already readable.
- Anything that would change phrasing or reorder words.

### Step 5 — Present BOTH lists for approval
Output a plain structure (no markdown table) in this shape:

```
Topic: <one-sentence guess at what the video is about>

A. Proper-noun / spelling corrections (please confirm, edit, or add):

1. "<as-found spelling>" → "<my proposed correction>"  (appears Nx)
2. "<as-found spelling>" → "<my proposed correction>"  (appears Nx)
...

B. Punctuation + capitalization fixes I plan to apply:

1. Block N: "<original snippet>" → "<corrected snippet>"  (reason: missing period / sentence start / etc.)
2. Block N: "<original snippet>" → "<corrected snippet>"
...

C. Spoken phrasing I will NOT touch (per rule 6):
- Block N: "<phrase>"  (reason: speech pattern, not a typo)
...

Confirm both lists, edit, or veto specific items.
```

Then STOP and wait. Do not write the output file yet.

If section B is empty after a full scan, that's fine — just say "No punctuation/capitalization issues detected." Never skip the scan; only skip the output line when there genuinely are no issues.

### Step 6 — Apply user feedback
The user will either:
- Approve both lists as-is, OR
- Edit entries, remove entries, veto specific punctuation fixes, or add new terms you missed

Merge their feedback into a final correction set. If they add a term that doesn't appear verbatim in the file, include it anyway (they may have caught a variant you missed). Punctuation/capitalization fixes default to "apply unless vetoed."

### Step 7 — Rewrite the file
Walk through every block. For each text line:
- Replace each as-found term with its confirmed correction (case-sensitive where it matters for proper nouns)
- Fix obvious spelling typos that don't depend on domain knowledge (e.g. "teh" → "the", "recieve" → "receive")
- Add missing sentence-end punctuation (`.`, `?`, `!`) only when the block clearly ends a thought
- Add missing commas only where grammatically required (list separators, clause boundaries) — when in doubt, leave it
- Fix apostrophes (`dont` → `don't`, `its` → `it's` only when it's clearly "it is")
- Capitalize the first letter of a sentence
- Capitalize confirmed proper nouns everywhere they appear

Preserve every other character exactly, including:
- Indices
- Timestamp lines (byte-for-byte)
- Line breaks within a block
- Blank lines between blocks
- Trailing newline at end of file
- BOM if present
- CRLF vs LF line endings (match the source)

### Step 8 — Write the output
Save to `~/Downloads/Updated_<original-filename>.srt` using the Write tool.
- If original is `episode-42.srt`, output is `Updated_episode-42.srt`
- Path is always `~/Downloads/` regardless of where the source lived.

### Step 9 — Open the Downloads folder in Finder (mandatory)
Immediately after saving the file, run:

```
open ~/Downloads/
```

via the Bash tool. This is how you knows the skill is done — he does NOT want the .srt file itself opened, and he does NOT want any video player or editor launched. **Open the folder, never the file.** This step is non-negotiable — every successful run ends with the Downloads folder visible in Finder.

### Step 10 — Report
Tell the user:
- Absolute output path (clickable markdown link)
- Total blocks processed
- Total corrections made, broken down by: proper-noun fixes, spelling typos, punctuation fixes, capitalization fixes
- Any blocks you left untouched because you weren't confident
- Spoken phrasing errors you deliberately preserved (per rule 6)

### Step 11 — Confirm completion (do NOT print the SRT)
After saving the file and opening the Downloads folder, end with a short confirmation message only (e.g. "Done — saved to <path>.").

**Hard rules for this step:**
- NEVER paste the SRT content back into the chat. Not in full, not in part, not truncated, not in a code block.
- Do not summarize the file contents. The file on disk is the deliverable.
- you opens the saved file himself. No verification dump needed.

## Block-Preservation Checklist (run mentally before writing output)

- [ ] Same number of blocks as input
- [ ] Every index line is identical to input
- [ ] Every timestamp line is identical to input (including `,` ms separator and `-->` spacing)
- [ ] Every block has the same number of text lines as input
- [ ] No block's text was reordered or merged across blocks
- [ ] File ends with the same whitespace pattern as input

If any checkbox fails, do not write the file. Diagnose and retry.

## Edge cases

- **Empty text blocks**: leave them empty, don't try to "fix" them.
- **Non-English characters / emoji**: preserve as-is unless the user specifically confirms a correction for them.
- **Numbers written as words**: don't convert ("two" stays "two", not "2", unless user asks).
- **Filler words** (um, uh, like): leave them. They're not errors.
- **Speaker labels** (e.g. `[MANTHAN]:`): preserve exactly.
- **Inline tags** (`<i>`, `<b>`, `{\an8}`): preserve exactly.
- **File with only one block**: workflow is the same — read, ask about keywords, fix, write.
- **File with thousands of blocks**: still read entirely. Don't sample or skip.

## What this skill never does

- Never hardcodes specific brand names, product names, tools, or terminology
- Never carries context from previous invocations
- Never changes the meaning of any sentence
- Never adds or removes blocks
- Never touches timestamps
- Never writes to a path other than `~/Downloads/`
- Never skips the keyword-approval step
- Never skips opening the Downloads folder in Finder at the end
- Never opens the .srt file itself — always the containing folder
- Never prints the corrected SRT content back in the chat — the saved file is the only deliverable
