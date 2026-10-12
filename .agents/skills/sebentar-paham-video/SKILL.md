---
name: sebentar-paham-video
description: Produce and revise Indonesian one-fact IT videos in the Sebentar, Paham. series, with recognizable topic illustrations, eye-catching explanatory animation, expressive narration and synchronized subtitles, and text that never overflows its box. Deliver only vertical MP4 and separate narration audio by default. Use for approved videos, continuing episode batches, proposing fresh IT/AI/API/LLM topics, improving generic visuals or fixing flat voices. Portable across Codex and Antigravity.
---

# Sebentar, Paham.

Act as producer, researcher, illustrator and editor. Complete authorized work. Resolve bundled resources relative to this file; create projects outside this installed skill. Preserve existing project artwork and source audio when revising.

## Current series contract

Apply the latest preferences in [series-context.md](references/series-context.md). These supersede the original seven-fact dark-terminal brief.

- Explain **one fact**, with background, an intuitive mechanism and a useful conclusion. Use relaxed Indonesian and familiar technical English, including **source code**, API, LLM, cache and deployment.
- Keep the warm pastel editorial identity, Inter and JetBrains Mono. **Show the actual subject**: an Earth with continents, a satellite with solar panels, a mouse with buttons and a wheel. Generic rectangles containing the subject's name are not an illustration.
- Export **only a 9:16 MP4, 1080×1920 at 30 fps, and one clean narration WAV**. Aim for 70–90 seconds. The MP4 contains voice, music and SFX; the WAV contains timeline-aligned voice only. Honor an explicit request for a different audio stem.
- Burn subtitles into the video, at most two lines, at least 48 px; the engine highlights the spoken word. **No progress bar.** Keep branding unobtrusive; never invent a channel handle.
- Use a curious opening, engaged middle and warmer, slightly slower ending with a resolved cadence. Do not rush to fit the duration or accept flat narration as final.
- Default to free-only production. Use original/licensed assets and bundled OFL fonts; never buy credits or assume Pro chat access includes a TTS API.

- **Text never leaves its box.** Build boxes from text (`e.chip`) or fit text into boxes (`e.box_text`); never draw a box and position text by hand. `studio.py lint` is a hard gate; see design.md.
- **Eye-catching, still on-brand.** One focal subject per scene, a strong hook, varied compositions, one dark focus scene and meaningful motion every ~2 s; design.md lists the toolkit.

Do not deliver SRT, script, thumbnail, titles, hashtags, reports, source project, ZIP or 16:9 video by default. Keep working files internally for revision and verification. Topic proposals and brief status replies are allowed when requested; do not dump a publishing pack into the final reply.

## 1. Resume context and scope

Inspect the latest user instructions and existing `series.json`, `production.json`, `history.json`, source project and process status. Recover earlier assets through the host's file capabilities when needed; old scratch paths may have expired.

- For **topic proposals**, compare history and propose fresh angles with a hook, mechanism, visual idea and primary source. Stop for selection only when topic approval was requested.
- For an **approved topic**, proceed without asking again. For **continue**, resume the first incomplete step and preserve numbering.
- For a **revision**, preserve what was accepted. New voice requires new alignment/timing; new visuals require actual object review and rerendering.

Use the newest shared ledger. If unavailable, read `assets/history-seed.json`; it contains partial recovered history, not a complete account of episodes 1–33. Never invent missing titles or fill gaps by renumbering finished videos. Example episodes are internal references, not fresh topic suggestions.

## 2. Research and write

Check primary sources: official documentation, standards, papers, original incident reports or the team's own explanation. Browse for current AI/API/LLM claims. Record each claim, URL, verification date and caveat in project `sources.md`; set source review true only after checking.

Write roughly 145–180 words across seven connected beats: hook, background, analogy, mechanism, consequence, caveat, ending. Actual speech duration is authoritative. Simplify dense sentences rather than accelerating them. Preserve essential caveats in the narration, not only in notes. Distinguish metaphors from physical architecture. End with a satisfying conclusion; use a gentle CTA only when appropriate/requested.

## 3. Illustrate before narrating

**Read [design.md](references/design.md) before creating any visual.** Read [schema.md](references/schema.md) for implementation and [portability.md](references/portability.md) for runtime/installation.

```bash
python <skill>/scripts/studio.py doctor
python <skill>/scripts/studio.py init <project> --topic "Approved topic" --history <prior-project>/history.json
```

Omit history only for a new series or after restoring its ledger. An explicit `--number` overrides numbering. Complete all script and visual TODOs. For each scene specify: the recognizable subject, at least two identifying visible features, the action the audience sees and what that action explains.

Make a subject-specific illustration using project `illustrations.py`, a custom `artwork.py` scene, or original/licensed raster assets. Use image generation when an available tool can improve organic/detail-heavy artwork; use code for exact diagrams and animation. Do not force every topic into the supplied mouse/GPS examples. If no correct asset exists, create it—do not silently fall back to text cards.

Use the bundled object library as a starting point; it contains Earth, satellite, mouse top/underside, phone, laptop, server, chip, router, clock, receipt and mug. `assets/scene-recipes.json` shows compositions. `init --example` loads the recovered mouse episode as a worked illustration example without voice clips.

```bash
python <skill>/scripts/studio.py check <project>
python <skill>/scripts/studio.py storyboard <project>
```

`storyboard` also runs the layout lint and fails on any text that is outside its box, off-screen, over another text or inside the subtitle zone; fix each reported item (red-boxed frames are saved under `qa/`), and rerun `studio.py lint <project>` after every artwork edit. Passing lint is necessary, not sufficient.

Inspect `key/storyboard/portrait.jpg` **and** `recognition.jpg`. Judge `portrait.jpg` as a thumbnail: each scene needs a clear hero and a different composition from its neighbours. The second hides labels: identify the object and mechanism from its shapes. At least five of seven scenes, including hook and mechanism, must be visually grounded in the topic. If a scene only works after reading text inside rectangles, redraw it. Storyboards are internal working assets, not finished videos or extra deliverables.

## 4. Narrate and align

Read [audio.md](references/audio.md). Discover actual free/authorized TTS capabilities. A model name or subscription does not establish access. Audition opening, middle and ending before using a new voice for a batch; reuse an accepted voice without repeat approval.

**Spend provider requests like money: one request per episode, not seven.** Free tiers cap requests per minute and per day, not text length, so seven clips burn a day's allowance on one episode and each retry burns more. Generate the whole narration as a single take, align it once, then cut it into the seven scene clips:

```bash
python <skill>/scripts/voice.py quota <project>                       # what this project already spent today + next reset
python <skill>/scripts/voice.py gemini <project> --key episode --dry-run   # inspect the request; costs nothing
python <skill>/scripts/voice.py gemini <project> --key episode             # ONE request (GEMINI_API_KEY in the shell)
python <skill>/scripts/voice.py align-full <project> --key episode --model <local-whisper-dir>
python <skill>/scripts/voice.py split <project> --key episode --provider "gemini-3.8-flash-tts"
```

Rules: never retry a quota error in a loop (read `<key>/tts/last-error.json`); listen to the take before spending another request; a fallback provider (ElevenLabs, a web tool, a local model) takes over a *whole episode*, never half of one, and feeds the same `align-full` → `split` path with its single-take audio. The provider dashboard's "Rate limits by model" chart shows **peak usage over 28 days**, not what is left today.

The seven-clip route still works when a provider cannot do a single take:

```bash
python <skill>/scripts/voice.py requests <project> --key episode
python <skill>/scripts/voice.py import <project> --key episode --audio-dir <clips> --alignment <words.json> --provider <provider-label>
```

Generate with one speaker. Import real word boundaries or use an available local aligner. Do not invent timestamps or reuse unrelated audio. Keep technical terms correctly spelled in subtitles. Listen for actual timing and pronunciation; ASR is not automatically correct.

If no expressive free voice is available, finish the internal script, artwork and provider-ready requests; report the remaining blocker briefly. Do not deliver silent previews or flat fallback audio as a completed video. Follow secure host authentication; never store credentials or repeatedly retry blocked logins.

## 5. Render and review

```bash
python <skill>/scripts/studio.py prepare <project> --key episode
python <skill>/scripts/studio.py render <project> --key episode --draft --workers 2
python <skill>/scripts/studio.py validate <project> --key episode
```

Watch the encoded opening, mechanism and ending; inspect `qa/<key>_encoded.jpg`. `render` re-runs the lint on every real subtitle frame and refuses to continue on failure. Check silhouette recognition, meaningful causal motion, actual caption synchronization, hook strength in the first 1.5 s, safe areas and readability at phone size. Listen for voice expression, a distinct ending, pronunciation, music balance and clean joins. Technical checks cannot judge these qualities.

Record observations/timestamps in internal `qa/review.md`. Set source/voice/visual review flags only after actual review of every included episode. Reset affected flags when inputs change. Use at most two render workers by default. Wait for encoders to exit, verify complete frame counts and full decode, then atomically publish files; existence alone is not completion.

## 6. Deliver two files and checkpoint

After source and voice review, run `render` without `--draft`; then review the actual encoded visuals and run:

```bash
python <skill>/scripts/studio.py deliver <project> --key episode
```

The delivery command verifies the unchanged inputs, portrait MP4, clean WAV and internal caption coverage. It records hashes and history internally. `package` is a compatibility alias for this same two-file delivery; it no longer creates a ZIP.

Persist the two files through the host's supported file storage, then give direct links to **MP4 and WAV only**. No extra formats or ZIP unless subsequently requested. Keep the editable project, internal SRT, mix, review evidence and ledger for future revisions. Report any incomplete render or save honestly.

Read [sources-and-licenses.md](references/sources-and-licenses.md) when selecting assets. Older projects do not update automatically: apply these rules to a safe copy, port the real custom artwork, and verify the new pipeline before replacing any delivered file.
