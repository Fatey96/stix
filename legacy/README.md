# Legacy copies

Archived copies of the earlier STIX generators, kept for provenance. None of
these are the working code — use [`../stix-generator/`](../stix-generator/),
which fixes their schema, import and UI breakage.

| Folder | Original repo | Last commit | What it is |
| --- | --- | --- | --- |
| `stix-gen-may/` | `Fatey96/STIX-Gen-May` | 2024-07-11 | Flask app + 15 `StixObjectLang` builders; the first version with the full SDO set. Has templates/static but no LLM relationship agent. |
| `sakura/` | `Fatey96/SAKURA` | 2024-07-25 | Same generator plus `STIXRelationshipAgent.py` (LLM picks each relationship type) and `stix2-validator` metrics. Ships no templates/static, so the UI cannot render. |
| `stix-main-fork/` | `Fatey96/STIX-MAIN-FORK` | 2024-01-02 | UNCP/LAS "Synthetic Cyber Knowledge Graph" full stack: Django backend (`backend/`) + Angular frontend (`frontend/`). |
| `stix-flask-2024/` | `Fatey96/STIX-Flask-2024` | 2024-01-26 | Early Flask prototype, STIX builders + UI. |
| `stix-building-webapp-flask/` | `Fatey96/STIX-Building-Webapp-Flask` | 2024-01-11 | Even earlier prototype, same lineage, plus a small Node package for the front end. |

## What was changed when archiving

These are verbatim copies except:

- `.git/` removed (history stays in the original repos).
- `__pycache__/`, `node_modules/`, `.idea/`, `.vscode/`, `dist/`, `.env` removed.
  `stix-main-fork/frontend/node_modules` alone was ~360 MB; install from
  `package.json` if you want to build it.
- `sakura/StixObjectLang/*.py` — the hardcoded
  `os.environ["OPENAI_API_KEY"] = "sk-proj-…"` assignment was replaced with a
  comment. That key was committed in SAKURA's git history; treat it as
  compromised and revoke it, even though the repo is private.

Nothing else was reformatted, so dead imports (`langchain.prompts`,
`langchain.chat_models`, `langchain.pydantic_v1`) are still there — that is
exactly what `../stix-generator/` fixes.
