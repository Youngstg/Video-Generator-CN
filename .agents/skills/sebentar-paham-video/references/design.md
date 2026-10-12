# Object-led visual direction

## Plan the visible explanation

Before coding, identify the **thing**, its **recognizable features**, the **action**, and the **result**. Write these in each visual spec. Make the illustration carry the explanation; headers and numbers are supporting information.

| Subject | Draw it so viewers recognize it | Animate the mechanism |
|---|---|---|
| Earth / GPS | Blue sphere, land shapes, atmosphere; satellites with a bus, panel wings and antenna | Show signals travelling satellite → receiver. Keep a clear line of sight; do not draw a radio path through Earth. Add clock comparisons only when discussing time. Label scale/time exaggeration. |
| Optical mouse | Curved body, split buttons, scroll wheel; underside optical opening | Show light on the desk, magnified texture in consecutive frames, displacement and cursor movement. |
| Server / network | Hardware rack with drive bays, ports and lights; cable/routes with meaningful endpoints | Show a request arriving, an actual route choice, a queue or a failed connection. |
| API / LLM | Actual interface/example, app or device and the requested operation; a concrete analogy when useful | Show what input changes, what the model/tool does and what reaches the user. Do not imply the analogy is physical model architecture. |
| Data / numbers | Use the actual receipt, file content, structured output or measured object | Show the operation producing the result. A numeric fact alone is not a substitute for the subject. |

A phone or laptop next to several unlabeled cards is not enough. Choose the object closest to the claim. Do not recycle Earth/satellite or mouse scenes for unrelated subjects merely because the template supports them.

## Choose the asset method

1. Use custom vector/code artwork for clean flat shapes, exact diagrams, labels and controllable motion. The bundled `illustrations.py` provides original logo-free shapes.
2. For an unfamiliar/complex subject, create original raster artwork with an available image-generation tool when useful, or use a verified licensed asset. Match the palette, lighting, angle and visual weight across scenes. Prefer separate transparent layers for motion.
3. Keep precise text, code, counts and paths out of generative imagery; composite them yourself. Inspect generated geometry and relevant identifying details before use.
4. If a tool is unavailable, draw a recognizable original illustration in code. Do not downgrade to a rectangle with the subject's name. For a capability-dependent request, explain the specific limitation instead of pretending it was fulfilled.

Record origin/licensing for imported assets internally. No logos or unnecessary product branding. Schematic illustrations are allowed; photographic realism is not required.

## Composition and legibility

- Portrait only by default: 1080×1920. Brand near x78/y146, episode near x886/y144. Two-line header near y313/y419. Main illustration inside x65–1015/y560–1527. Subtitles around y1584–1735, leaving the bottom clear for platform controls.
- Make recognizable objects the dominant illustration, typically occupying half to two-thirds of the central stage. Avoid a postage-stamp icon next to large text cards.
- Headers 68–88 px, subtitles 55 px, other educational labels at least 48 px. Only brand/episode marker may be 31 px. Shorten overflow; never shrink important text below 48 px.
- Use `brand.json` palettes, off-white space, gentle shadows and muted contrast. Keep a stable subject/color identity between scenes. Use an accent for the current explanatory focus.
- A rounded rectangle is appropriate for an actual screen, package, chip or UI region. Include identifying details. Do not make seven interchangeable text slides.

## Motion and timing

Use actual object displacement, light paths, changing surface images, orbit motion, packet travel or a visible state transition. Make the result follow its cause. Anchor narration-specific reveals with `engine.cue_time(scene, phrase, default)`; use the observed words in `cues.json`, not invented timing. Never show a conclusion before the phrase that explains it.

Change a meaningful element within three seconds, or use a continuous causal process. Floating icons and background dots alone are not an explanation. Do not loop a before/after action that implies a false process. A sustained demonstration may repeat, but its direction and relationship must remain correct.

Scene changes last 0.5 s with the quiet whoosh. The engine cycles `push` (new scene slides up), `zoom` (gentle push-in through the background colour) and `dissolve` (fade through the background); override per scene with `transition`. They fade *through* the background on purpose: a cross-dissolve shows two different headers on top of each other. Avoid glitches, flashes and progress bars. Omit unrelated stock footage and dramatic explosions when the event was not an explosion.

## Implement and inspect

`draw(im,key,i,t,e)` in project `artwork.py` receives the image, scene and local time. Use `e.T`, `e.SERIES`, `e.cue_time`, `e.arrow`, `e.path`, `e.packets`, `e.txt`, `e.font`, `e.ease`. Use `illustrations.place()` for original objects. `assets/scene-recipes.json` gives a GPS composition; the default worked example illustrates an optical mouse. The older `reference-artwork.py` is historical inspiration only and may contain obsolete layouts.

Set `kind: custom` only after adding an actual drawing branch. Label helpers must respect `e.SHOW_LABELS` so the recognition sheet can hide educational text; do not bake labels into object sprites. For custom UIs, keep necessary interface structure visible in that check.

Before final rendering inspect:

- **Recognition:** can you name the central subjects with labels hidden? Are Earth, satellite and mouse actual recognizable drawings?
- **Meaning:** can you describe the action and causal relationship without reading all subtitles? Are diagrams and metaphors accurate?
- **Variety:** do scenes add useful changes in view, scale or state? At least five of seven scenes, including hook and central mechanism, must depict the actual subject or a clearly explained concrete analogy.
- **Phone scale:** no clipped labels, illegible content, competing overlays or subtitles covering the subject.

Automated preflight can reject generic card kinds and missing assets. It cannot certify semantic recognition. Inspect the actual rendered frames and record concrete observations in `qa/review.md`; do not approve from JSON fields alone.


## Text must stay inside its box (hard rules)

Overflow was the most common defect. It came from three things: shrinking text below 48 px and then forcing it back up, positioning labels without checking the screen edge, and measuring with the wrong font weight. The engine now prevents the first two and `lint` catches the rest.

- **Never draw a box and then place text by hand.** Build the box *from* the text with `e.chip(d, cx, y, text)` (auto-sized pill/callout, wraps to two lines, shifts itself inside the safe area) or fit text *into* a fixed box with `e.box_text(d, (x1,y1,x2,y2), text, n=64)` (tries 64→48 px, wraps, centres, and raises if it cannot fit). These return the box so you can attach a pointer.
- **Labels:** call `label()`; it wraps to two lines and refuses an `x` closer than 165 px to a screen edge. Keep label centres between x 165 and 915.
- **Budget the words, not the pixels.** At 48 px bold Inter a line holds ~24 capital letters in a 560 px box and ~34 in 880 px. Two lines maximum. If it does not fit, rewrite the label; never reduce the size.
- **Use only helpers that raise.** `fit()` now raises instead of returning a size below 48. `txt()` clamps to 48 for a reason; do not call it to place text inside a box you drew yourself. If you must, pass the same box through `lint` and read the result.
- **Reserved zones:** y 1570–1750 belongs to the subtitles; nothing else may touch it. Text must stay in x 65–1015.
- **Run `studio.py lint` after every artwork edit.** It records every text and box, then fails on: `text_crosses_box`, `outside_canvas`, `covers_caption_zone`, `text_overlaps_text`, `does_not_fit`. It warns on `tight_padding`, `text_over_object`, `outside_safe_area`, `object_in_caption_zone`, `small_subject`, `off_centre`. Failing frames are saved with red boxes in `qa/<key>_layout*_scene<N>.png`.
- Lint cannot judge taste. After it passes, still look at the encoded frames at phone size.

## Make it eye-catching (without leaving the brand)

Calm does not mean flat. Pastel editorial motion still needs one clear focal point, contrast and rhythm.

**Already built into the engine (free for every scene):** a soft spotlight/backdrop behind the subject (`backdrop`: spot, rings, blobs, grid, sparkle, none, cycled per scene; spotlight follows the objects or `focus:[x,y]`); a highlighter swipe that draws itself under the second header line; objects that pop in with an overshoot, idle-float and cast a soft shadow; arrows that draw themselves with streaming dots; karaoke subtitles where the spoken word sits on a highlight chip; varied scene transitions.

**What you must still design per episode:**

1. **Hook in the first 1.5 s.** Scene 1 shows the surprising thing, big: the subject at 55–70 % of stage width, one clear action, the header phrased as a question or a contradiction. No logo build-up, no empty opening.
2. **One focal point per scene.** One hero object (width 500–700) and at most two supporting objects. If you need a third thing, it is probably a second scene.
3. **Vary the composition across the seven scenes.** Cycle through: *hero close-up* (one huge object), *split compare* (two things side by side, before/after), *zoom-in detail* (a circle magnifying a part), *flow* (three nodes with directional signals), *scale jump* (tiny vs huge), *recap* (the hero again, resolved). Do not use the same layout twice in a row. `assets/scene-recipes.json` has starting points.
4. **Use the dark scene once.** Set `mood: "dark"` on the mechanism scene (the engine's init template does this). It resets the viewer's attention at the midpoint. At most three dark scenes per video.
5. **Colour carries meaning.** Use the accent only for the thing the narration is talking about *right now* (use `cue` to move it). Everything else stays quiet.
6. **Something changes at least every 2 seconds:** an object arrives (`cue`), a signal fires, a value changes, the camera swaps to a detail. Staggered `at`/`cue` values are the cheapest rhythm.
7. **Callouts instead of paragraphs.** Put one short phrase (≤ 4 words) in an `annotations` chip, timed to the narration, instead of extra words on screen.
8. **Subject size.** `lint` warns `small_subject` when the drawing fills less than 40 % of the stage height *and* under 85 % of its width. Treat that warning as a design bug.

Before rendering, look at `storyboard/portrait.jpg` as a thumbnail: if you cannot tell scenes apart or name the hero in each at thumbnail size, it will not hold attention in a feed.
