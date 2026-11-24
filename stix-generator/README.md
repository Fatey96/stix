# STIX generator

Web service that generates synthetic STIX 2.1 threat-intelligence bundles:
randomized-but-schema-valid SDOs, a plausible relationship graph, validator
scoring and an optional LLM-written narrative.

This is the current revision of the STIX-Gen-May → SAKURA lineage. It keeps the
object builders and prompt engineering, restores the UI layer that was missing
from the newest copy, and adds an offline generator so the app runs with no API
key and no network.

## How it works

1. **Field generation** — `StixObjectLang/*.py` produce the *fields* for each
   SDO type. With `OPENAI_API_KEY` set they call an LLM through
   `langchain_experimental`'s tabular synthetic-data generator; without a key
   they delegate to `local_generator.py`, which draws from the STIX 2.1 open
   vocabularies (threat-actor-type-ov, malware-type-ov, attack-motivation-ov,
   …) plus Faker for names, sectors and coordinates.
2. **Assembly** — `stix_object_builder.py` coerces the generated fields and
   constructs real `stix2` objects. Malformed items are logged and skipped, not
   fatal.
3. **Relationships** — `relationship_builder.py` walks a source-type →
   target-type → relationship-type map and emits `relationship` SROs.
4. **Bundle + metrics** — `stix_bundler.py` packs the bundle; `app.py` scores
   completeness, `stix2-validator` consistency, timeliness, object-type
   distribution and relationship richness.
5. **Story (optional)** — an LLM narrates the bundle as a threat scenario.
   Purely cosmetic: the bundle and metrics never depend on it.

Supported SDO types: threat-actor, intrusion-set, campaign, identity, malware,
tool, attack-pattern, indicator, infrastructure, vulnerability, location,
course-of-action, malware-analysis, report, opinion.

## Run

```bash
cd stix-generator
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                                    # http://127.0.0.1:5000
```

Environment variables (all optional except the key for LLM mode):

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | unset | enables LLM field generation and the story |
| `GENERATOR_MODEL` | `gpt-4o-mini` | model used for object fields |
| `STORY_MODEL` | `gpt-4o-mini` | model used for the narrative |
| `PORT` | `5000` | Flask port |

Copy `.env.example` to `.env` to set them.

## API

`POST /generate-graph` (form-encoded, counts per SDO type):

```bash
curl -X POST http://127.0.0.1:5000/generate-graph \
  -d threat-actor-count=3 -d malware-count=2 -d indicator-count=4
```

Returns:

```json
{"stix_bundle": "...", "metrics": {...}, "story": null}
```

`GET /healthz` for liveness. `samples/sample_bundle.json` is a real offline
run (15 types, 56 objects, 26 relationships, 0 validator errors).

## Tests

```bash
pip install pytest
python -m pytest -q
```

Covers page rendering, the offline generation path, full 15-type bundle
validation against `stix2-validator`, and the empty-selection guard.

## Provenance

Built on the SAKURA / STIX-Gen-May generators (UNC Pembroke LAS). Fixes in this
copy: hardcoded API key removed, imports moved to `langchain_core` /
`langchain_openai` / `pydantic`, LLM clients built lazily instead of at import,
SDO assembly rewritten against `stix2` classes, `targrts` typo in the
relationship map corrected, offline generator added, UI extended to all 15
types, metrics rendered in the UI.
