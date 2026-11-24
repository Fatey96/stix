# STIX synthetic data generation

Private workspace for the synthetic cyber-threat-intelligence (CTI) data
generators: software that manufactures STIX 2.1 bundles — threat actors,
malware, campaigns, indicators, infrastructure and the relationship graph
between them — for training data, detection engineering tests and graph
research.

## Projects

| Folder | What it is |
| --- | --- |
| [`stix-generator/`](stix-generator/) | Latest generator: Flask service + web UI that spawns randomized-but-valid STIX 2.1 objects, wires relationships, validates the bundle, scores quality metrics and (optionally) narrates the scenario with an LLM. |
| [`legacy/`](legacy/) | Archived earlier copies (STIX-Gen-May, SAKURA, the UNCP/LAS Django+Angular knowledge-graph app, and two 2024 Flask prototypes), kept for provenance only. |

`stix-generator/` is the current revision of the STIX-Gen-May → SAKURA line:
it keeps the 15 SDO builders, restores the missing UI layer, ships an offline
generator so it runs with no API key, and fixes the schema/import breakage that
made the older copies unrunnable on current `stix2` / `langchain`.

## Status

- Offline mode: verified end-to-end — 15 SDO types + relationships, bundle
  passes `stix2-validator` with 0 errors (see `tests/`).
- LLM mode: prompt/generator wiring retained; requires `OPENAI_API_KEY`
  (not exercised here).

## Security note

The legacy `SAKURA` copy committed a live `OPENAI_API_KEY` in
`StixObjectLang/*.py`. It is stripped from every file here and from the
archived copies, but the key is still in SAKURA's git history — revoke it in
the OpenAI dashboard and treat anything it authorized as exposed.
