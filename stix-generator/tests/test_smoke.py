"""Smoke tests for the offline (no API key) generation path.

Run with:  python -m pytest -q
"""

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.pop("OPENAI_API_KEY", None)

import app as service  # noqa: E402


@pytest.fixture()
def client():
    service.app.config.update(TESTING=True)
    return service.app.test_client()


def test_pages_render(client):
    assert client.get("/").status_code == 200
    assert client.get("/select-objects").status_code == 200
    assert client.get("/healthz").get_json() == {"status": "ok"}


def test_generate_core_types(client):
    response = client.post("/generate-graph", data={
        "threat-actor-count": "3",
        "malware-count": "2",
        "identity-count": "2",
        "attack-pattern-count": "2",
    })
    assert response.status_code == 200
    payload = response.get_json()
    bundle = json.loads(payload["stix_bundle"])
    types = {obj["type"] for obj in bundle["objects"]}
    assert {"threat-actor", "malware", "identity", "attack-pattern", "relationship"} <= types
    assert payload["metrics"]["consistency_score"] == 100.0
    assert payload["metrics"]["total_objects"] == len(bundle["objects"])


def test_generate_all_types_validates(client):
    fields = [
        "threat-actor-count", "intrusion-set-count", "campaign-count",
        "identity-count", "malware-count", "tool-count", "attack-pattern-count",
        "indicator-count", "infrastructure-count", "vulnerability-count",
        "location-count", "course-of-action-count", "malware-analysis-count",
        "report-count", "opinion-count",
    ]
    response = client.post("/generate-graph", data={field: "1" for field in fields})
    assert response.status_code == 200
    payload = response.get_json()
    bundle = json.loads(payload["stix_bundle"])

    from stix2validator import validate_instance

    assert not validate_instance(bundle).errors
    assert payload["metrics"]["completeness_score"] == 100.0

    relationship_types = {
        obj["relationship_type"] for obj in bundle["objects"] if obj["type"] == "relationship"
    }
    assert relationship_types
    assert "targrts" not in relationship_types


def test_empty_selection_is_rejected(client):
    response = client.post("/generate-graph", data={})
    assert response.status_code == 400
