"""Synthetic STIX 2.1 threat-intelligence bundle generator.

Flask service that spawns randomized-but-schema-valid STIX Domain Objects
(threat actors, malware, tools, campaigns, ...), wires them into a plausible
relationship graph, packs everything into a STIX 2.1 bundle and reports
quality metrics (completeness, stix2-validator consistency, timeliness,
type distribution, relationship richness).

Provenance: latest revision of the STIX generator lineage
(STIX-Gen-May -> SAKURA), with the UI layer restored and small robustness
fixes. See ../README.md.
"""

from collections import Counter
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS, cross_origin
from stix2validator import validate_instance

from stix_object_builder import (
    create_attack_patterns,
    create_campaigns,
    create_course_of_actions,
    create_identities,
    create_indicators,
    create_infrastructures,
    create_intrusion_sets,
    create_locations,
    create_malware_analysis,
    create_malwares,
    create_opinion,
    create_reports,
    create_threat_actors,
    create_tools,
    create_vulnerabilities,
)
from relationship_builder import randomly_connect_objects
from stix_bundler import create_bundle

try:  # langchain-openai first, legacy community shim as fallback
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - depends on installed langchain
    from langchain_community.chat_models import ChatOpenAI

from langchain_core.prompts import PromptTemplate

import json
import logging
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - dotenv is optional
    pass

# STIX reference only allows timestamps with millisecond precision and a Z suffix.
STIX_TS = "%Y-%m-%dT%H:%M:%S.%fZ"

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _parse_stix_ts(value):
    """Parse a STIX timestamp, tolerating second precision and missing fraction."""
    if not value:
        return None
    text = str(value).replace("+00:00", "Z")
    for fmt in (STIX_TS, "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def calculate_metrics(stix_bundle):
    stix_data = json.loads(stix_bundle)
    objects = stix_data["objects"]
    total_objects = len(objects)

    if total_objects == 0:
        return {
            "total_objects": 0,
            "completeness_score": 0.0,
            "consistency_score": 0.0,
            "timeliness_score": 0.0,
            "object_type_distribution": {},
            "relationship_ratio": 0.0,
        }

    # Metric 1: Completeness
    objects_with_all_required_fields = sum(
        1 for obj in objects if all(field in obj for field in ("id", "type", "created"))
    )
    completeness_score = (objects_with_all_required_fields / total_objects) * 100

    # Metric 2: Consistency (stix2-validator)
    validation_results = validate_instance(stix_data)
    error_count = len(validation_results.errors)
    consistency_score = max(0.0, 100 - (error_count / total_objects * 100))

    # Metric 3: Timeliness (share of objects created in the last 30 days)
    now = datetime.now(timezone.utc)
    recent = 0
    for obj in objects:
        created = _parse_stix_ts(obj.get("created"))
        if created is not None and (now - created).days < 30:
            recent += 1
    timeliness_score = (recent / total_objects) * 100

    # Metric 4: Object type distribution
    object_types = Counter(obj["type"] for obj in objects)

    # Metric 5: Relationship richness
    relationship_count = sum(1 for obj in objects if obj["type"] == "relationship")
    relationship_ratio = relationship_count / total_objects

    return {
        "total_objects": total_objects,
        "completeness_score": completeness_score,
        "consistency_score": consistency_score,
        "timeliness_score": timeliness_score,
        "object_type_distribution": dict(object_types),
        "relationship_ratio": relationship_ratio,
    }


def generate_story_from_bundle(stix_bundle):
    """Narrate the bundle with an LLM. Returns None when no LLM is configured.

    The generator never depends on the LLM: the bundle and metrics are always
    returned, the story is an optional extra.
    """
    if not os.getenv("OPENAI_API_KEY"):
        logger.info("OPENAI_API_KEY not set - skipping story generation")
        return None

    bundle_data = json.loads(stix_bundle)
    objects = bundle_data["objects"]

    threat_actors = [obj for obj in objects if obj["type"] == "threat-actor"]
    malwares = [obj for obj in objects if obj["type"] == "malware"]
    indicators = [obj for obj in objects if obj["type"] == "indicator"]
    relationships = [obj for obj in objects if obj["type"] == "relationship"]

    summary = [
        f"Threat Actors: {len(threat_actors)}",
        f"Malware: {len(malwares)}",
        f"Indicators: {len(indicators)}",
        f"Relationships: {len(relationships)}",
    ]

    by_id = {obj["id"]: obj for obj in objects}
    for relationship in relationships:
        source_obj = by_id.get(relationship["source_ref"])
        target_obj = by_id.get(relationship["target_ref"])
        if source_obj and target_obj:
            summary.append(
                f"{source_obj['type']} ({source_obj.get('name', 'Unnamed')}) "
                f"{relationship['relationship_type']} "
                f"{target_obj['type']} ({target_obj.get('name', 'Unnamed')})"
            )

    story_prompt = PromptTemplate(
        input_variables=["summary"],
        template="""Based on the following summary of a STIX bundle:

{summary}

Please provide a brief, coherent story that describes the cyber threat scenario represented by these objects and relationships. Focus on the key actors, their motivations, and the progression of their activities. The story should be easily understandable by a non-technical audience.

Limit your response to 3-5 paragraphs.""",
    )

    try:
        llm = ChatOpenAI(temperature=0.7, model_name=os.getenv("STORY_MODEL", "gpt-4o-mini"))
        story_chain = story_prompt | llm
        result = story_chain.invoke({"summary": "\n".join(summary)})
        logger.info("Generated story")
        return result.content
    except Exception as exc:  # noqa: BLE001 - story is best effort
        logger.error("Error generating story: %s", exc)
        return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/select-objects", methods=["GET"])
def select_objects():
    return render_template("select_objects.html")


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})


@app.route("/generate-graph", methods=["POST"])
@cross_origin()
def generate_graph():
    data = request.form

    def count(field):
        raw = data.get(field, 0) or 0
        try:
            return max(0, int(raw))
        except (TypeError, ValueError):
            return 0

    threat_actor_count = count("threat-actor-count")
    identity_count = count("identity-count")
    malware_count = count("malware-count")
    indicators_count = count("indicator-count")
    infrastructure_count = count("infrastructure-count")
    tools_count = count("tool-count")
    campaigns_count = count("campaign-count")
    intrusion_sets_count = count("intrusion-set-count")
    course_of_actions_count = count("course-of-action-count")
    reports_count = count("report-count")
    opinions_count = count("opinion-count")
    attack_patterns_count = count("attack-pattern-count")
    locations_count = count("location-count")
    malware_analysis_count = count("malware-analysis-count")
    vulnerabilities_count = count("vulnerability-count")

    threat_actors = create_threat_actors(threat_actor_count) if threat_actor_count else []
    identities = create_identities(identity_count) if identity_count else []
    malwares = create_malwares(malware_count) if malware_count else []
    indicators = create_indicators(indicators_count) if indicators_count else []
    infrastructures = create_infrastructures(infrastructure_count) if infrastructure_count else []
    tools = create_tools(tools_count) if tools_count else []
    campaigns = create_campaigns(campaigns_count) if campaigns_count else []
    intrusion_sets = create_intrusion_sets(intrusion_sets_count) if intrusion_sets_count else []
    course_of_actions = create_course_of_actions(course_of_actions_count) if course_of_actions_count else []
    attack_patterns = create_attack_patterns(attack_patterns_count) if attack_patterns_count else []
    locations = create_locations(locations_count) if locations_count else []
    malware_analysis = create_malware_analysis(malware_analysis_count) if malware_analysis_count else []
    vulnerabilities = create_vulnerabilities(vulnerabilities_count) if vulnerabilities_count else []

    stix_objects = (
        threat_actors + identities + malwares + indicators + tools +
        intrusion_sets + course_of_actions + infrastructures + campaigns +
        attack_patterns + locations + malware_analysis + vulnerabilities
    )

    previous_ids = [obj.id for obj in stix_objects]

    reports = create_reports(reports_count, previous_ids) if reports_count and previous_ids else []
    opinions = create_opinion(opinions_count, previous_ids) if opinions_count and previous_ids else []

    stix_objects += reports + opinions

    if not stix_objects:
        return jsonify({"error": "select at least one object type with a count above zero"}), 400

    relationships = randomly_connect_objects(stix_objects)
    stix_bundle = create_bundle(stix_objects, relationships)
    metrics = calculate_metrics(stix_bundle)
    story = generate_story_from_bundle(stix_bundle)

    return jsonify({
        "stix_bundle": stix_bundle,
        "metrics": metrics,
        "story": story,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
