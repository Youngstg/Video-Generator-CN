# Narration and audio

Use `assets/voice-direction.json`. Preserve speaker identity and recording tone between scenes.

| Beat | Direction |
|---|---|
| Opening | Curious, lightly surprised; emphasize the question and pause before revealing. |
| Background | Warm and approachable, with time to build context. |
| Mechanism | Engaged, slightly slower on technical terms, emphasize cause and consequence. |
| Caveat | Matter-of-fact but engaged, without a robotic tone. |
| Ending | Slightly slower, warm satisfaction, resolved downward cadence; friendly CTA if requested. |

Aim for 130–155 words/minute during voiced sections, allowing scene pauses. Actual duration is authoritative. Rewrite dense text instead of accelerating speech.

## Provider selection

Prefer an expressive provider already authorized and available without added charges. Discover current host tools and verify styles/free limits in official provider documentation. A Gemini or ChatGPT Pro subscription is not proof of API entitlement or a TTS tool. Never silently spend credits or enable billing.

The adapter exports provider-neutral requests and imports audio; it does **not** log in to Gemini, contain an API key or supply a free TTS service itself. Use secure host authentication; keep passwords, cookies and keys out of this skill and source projects.

If only a flat voice is available, label it an audition/preview. Do not substitute it for an expressive final without acceptance. Gain, pitch shift and tempo alone do not create natural expression. Do not imitate a real person's voice without authorization.

## Request budget and fallbacks (read before generating)

Free TTS tiers limit **requests** (per minute and per day), usually not text length. A typical episode is ~1,100 characters, far below any token limit, but seven scene clips are seven requests.

1. **One take per episode.** `voice.py gemini` sends the whole narration in one request (`--mode beats`: one text block per scene, each with its own `speech_metadata.style`; `--mode single`: one block). Then `align-full` and `split` produce the seven clips and per-scene timestamps. A single take also keeps one consistent voice.
2. **Dry-run first, listen before retrying.** `--dry-run` prints the exact request at no cost. A rejected take costs another request, so audition with a short excerpt first when unsure.
3. **No retry loops.** `voice.py gemini` makes one attempt, records every attempt (failures included) in `tts-ledger.json`, and writes the provider's error to `<key>/tts/last-error.json`. A 429 means: read which limit it names (per minute vs per day, or a limit of 0, which means the model has no free allocation for that project), then switch.
4. **Local guard.** Defaults `--rpd 10 --rpm 3` match the free-tier numbers observed in AI Studio; set them to what your dashboard shows. The ledger only sees this project on this machine; provider quotas are per cloud project, so a new API key in the same project adds nothing.
5. **The dashboard chart is not a countdown.** AI Studio's "Rate limits by model" shows peak usage over the last 28 days. Daily quotas (RPD) reset at midnight Pacific time (14:00 WIB while the US is on daylight time, 15:00 WIB after the first Sunday of November). Per-minute limits recover within about a minute. `voice.py quota` prints the next reset.
6. **Fallback chain, per whole episode:** Gemini 3.8 Flash TTS → Gemini 3.8 Flash-Lite TTS (separate model quota) → ElevenLabs free tier (check its commercial-use terms) → other web tools only as a last resort. Every fallback must supply one single-take audio file for `align-full` + `split`. Record the provider per episode; audition before accepting a fallback voice, since series voice consistency matters.

### Gemini 3.8 TTS specifics

- Input text is a **verbatim transcript**: put delivery directions in `speech_metadata.style`, never in the text, or they may be spoken aloud. Use inline `<short pause>` / `<breath>` only for momentary events.
- Create one persona with Voice design (`voice-direction.json` → `voice_design_persona`, an original voice, never a real person) and pass its `voice_...` id as `--voice` for every episode; keep per-beat styles short.
- Unary responses are WAV by default; headerless PCM (`audio/l16`) is wrapped automatically.
- Requires the SDK: `python -m pip install -r scripts/requirements-tts.txt` (optional; the core engine does not need it).
- Word timestamps are not part of the response; use `align-full` (local faster-whisper) and check technical terms.

## Files and real timing

Store seven scene clips as `project/key/audio/0.wav` through `6.wav`. MP3, M4A and FLAC also work. Exactly one file per scene. Supply narration only; the engine adds music/SFX. When wrapping raw PCM, use the provider's actual sample rate, channels and format.

Keep displayed script in `series.json.scripts`; save phonetic pronunciation notes separately. Do not display phonetic spellings of API, JSON or technical English in subtitles.

`alignment.json` contains seven arrays of `{word,start,end}` records. Times are seconds relative to that scene's audio, with positive duration and ordered words. Each real scene must be nonempty. Example record: `{"word":"Cache","start":0.12,"end":0.48}`.

Use provider word boundaries, a trusted forced aligner or transcription of the audio. Never spread words uniformly across clip duration or use character counts as final timing. Minor pronunciation/transcription differences map back to the written script; inspect larger differences manually.

```bash
python <skill>/scripts/voice.py requests <project> --key episode
python <skill>/scripts/voice.py import <project> --key episode --audio-dir <clips> --alignment <words.json> --provider "approved-provider"
python <skill>/scripts/voice.py verify <project> --key episode
```

For existing audio with genuine timestamps, `register` with `--provider` records provenance and resets reviews. Registration is not a listening review. Hash verification rejects changed text/audio/alignment until regenerated and registered.

## Optional local transcription

If provider timestamps are unavailable, install `faster-whisper` in the project environment:

```bash
python -m pip install faster-whisper
python <skill>/scripts/voice.py align <project> --key episode --model <local-model-directory>
```

The adapter uses CPU int8 and actual word timestamps. A model name such as `small` downloads weights when uncached, requiring network and disk. Prefer an existing local model. ASR can misrecognize technical terms and digits; listen and repair using observed times. Primary dependency documentation is linked in `sources-and-licenses.md`.

## Mix and approval

The engine synthesizes original gentle instrumental music and transition/reveal sounds. Keep them beneath speech and quieter in the closing. Final normalization targets about −15 LUFS integrated, −1.5 dB true peak. Listen for intelligibility, clipping, abrupt joins and a flat ending; measurements cannot judge these alone.

Before a new voice goes into a batch, audition an opening, a mechanism sentence and an ending. Record provider, voice label, date and acceptance evidence. Replacing voice requires new timing, internal SRT and re-rendered scenes; never retain old captions blindly.

## Default audio delivery

Deliver one `<filename>_Narasi.wav`: clean mono PCM 16-bit narration at 48 kHz, with the same scene pauses and total timeline as the video. The MP4 has narration plus the original music/SFX mix. Keep `internal/mix.wav`, scene clips, SRT and audio requests in the editable project; do not deliver extra stems unless requested. This two-file contract replaces the earlier publishing pack.
