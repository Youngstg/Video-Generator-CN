# Project schema and commands (v2.1)

`studio.py init` copies editable source and fonts outside the installed skill. `series.json` maps safe lowercase episode keys to records; each needs a distinct number and filename.

| Field | Requirement |
|---|---|
| `number`, `filename`, `title` | Positive number, safe output stem, human title. |
| `angle`, `branding` | Optional history angle; default brand `SEBENTAR, PAHAM.`. |
| `theme` | `bg`, `ink`, `accent`, `soft`, `dark` as hex colors. |
| `scripts` | Seven connected narration strings, usually 145–180 words total. |
| `headers` | Seven pairs of short lines, each fitting 934 px at 48 px. |
| `minimums` | Seven scene minimum durations; voice and pauses may extend them. |
| `visuals` | Seven object-led specs; see below. |
| `sources` | `[source name, HTTPS URL]` pairs supporting the claims. |
| `notes` | Accuracy caveats; essential qualifications also belong in narration. |
| `music_bpm`, `music_transpose` | Optional original-score controls; default 76 BPM and zero semitones. |

Titles/hashtags/descriptions are no longer required. Do not create publication files by default.

## Visual schema

Every scene needs `kind`, `subject`, `features` (at least two distinguishing visible details), `action` and `purpose`. Those fields plan the artwork; they do not prove its quality. Supported kinds:

- `objects`: compose actual illustrated sprites or image assets, with causal motion/links.
- `mouse`: seven worked example phases, specifically for the recovered optical-mouse explanation.
- `custom`: implement the topic's mechanism in `artwork.py`; the stock renderer rejects it until implemented.

Old `stack`, `flow`, `compare`, `stat`, `code` card-only kinds fail preflight. Draw genuine code/data within an explanatory object scene when the subject requires it.

```json
{
  "kind": "objects",
  "subject": "A GPS satellite broadcasting to a phone receiver",
  "features": ["solar panel wings and antenna dish", "phone screen and map pin"],
  "action": "Radio signal travels from satellite to receiver",
  "purpose": "Explain one-way reception, not a phone request to the satellite",
  "objects": [
    {"id":"sat","sprite":"satellite","x":320,"y":780,"width":420},
    {"id":"phone","sprite":"phone","x":760,"y":1230,"width":330}
  ],
  "links":[{"from":"sat","to":"phone","meaning":"satellite radio broadcast","cue":"sinyal","at":1}]
}
```

Scene-level presentation fields (all optional; every one has a safe default):

| Field | Values | Effect |
|---|---|---|
| `mood` | `light` (default), `dark` | `dark` inverts the palette for a focus scene. Max three per video; the init template uses it for the mechanism scene. |
| `backdrop` | `spot`, `rings`, `blobs`, `grid`, `sparkle`, `none` | Flat shapes behind the subject. Default cycles per scene index. |
| `focus` | `[x, y]` | Spotlight centre. Default: centre of the scene's objects. |
| `transition` | `dissolve`, `push`, `zoom` | How this scene is entered. Default cycles `push, zoom, push, zoom, push, dissolve`. |

Object fields: unique `id`; exactly one of `sprite` or `asset`; center `x,y`; square tile `width`; optional `angle`, `label`, `label_width`, `motion`, `at`/`cue` (when it pops in; default staggered), `float` (idle bob, default true), `shadow` (default true). Labels wrap to two lines and must sit between x 165 and 915. Sprites have transparent margins, so judge the actual visible silhouette. Image assets use a project-relative path and a `credit` stating license/original-generation provenance. Retain original files in project `assets/` for cache invalidation and later revision.

Built-ins: `earth`, `satellite`, `mouse`, `mouse_under`, `phone`, `laptop`, `server`, `chip`, `router`, `clock`, `receipt`, `mug`. Extend this library for new subjects; never relabel an unrelated object.

Motion:

```json
{"kind":"move","dx":120,"dy":0,"duration":3,"cue":"bergerak","at":1}
{"kind":"orbit","radius":[320,190],"period":18,"phase":0}
```

Optional `cue` uses real caption timing with `at` as a storyboard fallback. `move` is a single state change; add further meaningful changes or a custom scene for long holds. `orbit` is continuous around `x,y`. Signal dots always travel `from` → `to`. Optional annotations have `x,y,text,width,at,cue,style`. They render as an auto-sized chip (`style: "chip"`, default), a box built from the wrapped text so it cannot overflow; `style: "plain"` draws bare text. Keep them to four words. Layout/motion quality still requires visual inspection.

## Layout helpers for custom `artwork.py` (`e` is the engine module)

| Helper | Use |
|---|---|
| `e.chip(d, cx, y, text, bg, fg, n=48, max_w=900)` | Auto-sized rounded label built from the wrapped text; returns the box. |
| `e.box_text(d, (x1,y1,x2,y2), text, n=64)` | Fit text into a fixed box (64→48 px, wraps, centres); raises `LayoutError` if impossible. |
| `e.wrap(text, n, width, max_lines=2)` | Balanced line breaking; raises instead of overflowing. |
| `e.fit(text, n, width)` | Largest size that fits; raises below 48 px. |
| `e.mark_object(box)` | Register a custom-drawn object's bounding box so lint can detect labels on top of it. `illustrations.place()` returns its visible box. |
| `e.pop(u)` / `artwork.appear()` | Overshoot scale curve and per-object entry time. |

## Workflow

```bash
python <skill>/scripts/studio.py init <project> --topic "Chosen fact" --history <prior>/history.json
python <skill>/scripts/studio.py check <project>
python <skill>/scripts/studio.py storyboard <project>      # also runs the layout lint
python <skill>/scripts/studio.py lint <project>            # rerun after every artwork edit
# preferred (1 provider request): voice.py gemini -> align-full -> split   (see audio.md)
python <skill>/scripts/voice.py requests <project> --key episode
python <skill>/scripts/voice.py import <project> --key episode --audio-dir <clips> --alignment <words.json> --provider "voice-source"
python <skill>/scripts/studio.py prepare <project>
python <skill>/scripts/studio.py render <project> --draft --workers 2   # lints subtitles too (--captions)
python <skill>/scripts/studio.py validate <project>
python <skill>/scripts/studio.py render <project> --workers 2
python <skill>/scripts/studio.py deliver <project>
```

Use `--key` for one episode. `init --example` loads old episode 6 without voice; use it only in an isolated example project, not as a new-number topic. `package` aliases `deliver` and creates no archive. `deliver --draft` verifies a clearly labeled review pair without marking history complete; never call it final.

`production.json` flags are project-wide. Review all included episodes before setting true; store observations and watched timestamps in `qa/review.md`. The input signature includes source modules, scripts, asset files, original audio and timing. Delivery rejects changes since render, and requires a clean, current `qa/<key>_layout_captions.json` from `lint --captions` (run automatically by `render`).

## Files

Only these two user-facing files may be in `key/output/`:

- `<filename>.mp4`: 1080×1920, 30 fps, H.264/AAC, full audio mix, burned subtitles.
- `<filename>_Narasi.wav`: PCM 16-bit, 48 kHz, mono, clean voice with the same pauses/timeline as the video.

`key/internal/`: captions SRT, narration text and mixed soundtrack. `key/storyboard/`, `qa/`: planning sheets, layout reports (`<key>_layout*.json`, red-boxed failures), label-free recognition check, encoded frames, technical and human review. `delivery-manifest.json` and `history.json` stay internal. Deliver direct media files, no ZIP or horizontal export by default.

Do not overwrite old custom source projects with this template. For a migration, work in a copy, preserve their genuine audio/alignment and adapt the old artwork to this schema. Move previous extra deliverables out of the new output directory without deleting the originals. Run complete validation before replacing any delivered video.
