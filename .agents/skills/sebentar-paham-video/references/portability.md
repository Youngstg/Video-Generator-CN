# Runtime and host portability

Use one skill folder for both hosts. Standard `SKILL.md` carries instructions; Python scripts use relative paths and subprocess argument arrays. `agents/openai.yaml` is optional Codex UI metadata for other hosts.

Require Python 3.10+, FFmpeg/FFprobe with libx264/AAC, and Python packages in `scripts/requirements.txt`. Prefer a project virtual environment:

```bash
python -m pip install -r <skill>/scripts/requirements.txt
python <skill>/scripts/studio.py doctor
```

Use `python3` where needed or `py -3` in Windows PowerShell. Quote paths with spaces. Install FFmpeg using the user's package manager and PATH; do not assume administrator rights. CPU rendering requires no Runway or video-generation API.

## Installation

Official paths checked 2026-10-09:

| Scope | Folder |
|---|---|
| Shared project, both agents | `<project>/.agents/skills/sebentar-paham-video/` |
| Codex user | `~/.agents/skills/sebentar-paham-video/` |
| Antigravity IDE user | `~/.gemini/config/skills/sebentar-paham-video/` |
| Antigravity CLI user | `~/.gemini/antigravity-cli/skills/sebentar-paham-video/` |

Antigravity also supports legacy `.agent/skills`; prefer `.agents/skills` for a new shared project. Recheck current official docs if the installed version differs.

```bash
python <skill>/scripts/studio.py install --project <project-folder>
python <skill>/scripts/studio.py install --host codex
python <skill>/scripts/studio.py install --host antigravity
```

Choose one scope. The installer refuses overwrite and self-copy. For Antigravity CLI global use, copy the folder to its explicit CLI path above. Reload the agent if discovery needs it.

Invoke `$sebentar-paham-video` in Codex, or select it in the Skills UI. In Antigravity use `/sebentar-paham-video` when supported, or ask the agent to read the installed `SKILL.md` and follow it. In ChatGPT Work select the saved skill. A shared project folder gives both agents the same version.

The host must offer filesystem access, process execution and web research. Expressive narration additionally needs an accessible TTS provider/tool or supplied audio. This folder does not grant API access, browser login, Library access or credits. Discover capabilities from the host; never invent a connector. Persist through host storage if available, otherwise keep user project files. If execution is unavailable, name the unperformed rendering step explicitly.
