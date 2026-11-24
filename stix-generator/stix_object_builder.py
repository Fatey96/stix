"""Assemble STIX 2.1 Domain Objects from generated field bundles.

Field values come from ``StixObjectLang/*.py``: the LLM-backed generators when
``OPENAI_API_KEY`` is set, otherwise the offline ``local_generator``. Those
modules only produce *fields*; this file is the single place that turns them
into real ``stix2`` objects, so the bundle always serializes and validates.

Values are coerced because LLMs drift between str and list on optional
multi-value fields, and STIX timestamps must be real datetimes.
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from stix2 import (
    AttackPattern,
    Campaign,
    CourseOfAction,
    Identity,
    Indicator,
    Infrastructure,
    IntrusionSet,
    Location,
    Malware,
    MalwareAnalysis,
    Opinion,
    Report,
    ThreatActor,
    Tool,
    Vulnerability,
)

from StixObjectLang.AttackPattern import generate_attack_pattern
from StixObjectLang.Campaign import generate_campaign
from StixObjectLang.CourseOfAction import generate_course_of_action
from StixObjectLang.Identity import generate_identity
from StixObjectLang.Indicator import generate_indicator
from StixObjectLang.Infrastructure import generate_infrastructure
from StixObjectLang.IntrusionSet import generate_intrusion_set
from StixObjectLang.Location import generate_location
from StixObjectLang.Malware import generate_malware
from StixObjectLang.MalwareAnalysis import generate_malware_analysis
from StixObjectLang.Opinion import generate_opinion
from StixObjectLang.Report import generate_report
from StixObjectLang.ThreatActor import generate_threat_actors
from StixObjectLang.Vulnerability import generate_vulnerability
from StixObjectLang.tool import generate_tool

logger = logging.getLogger(__name__)


def _now():
    return datetime.now(timezone.utc)


def _str(value, default=None):
    """Coerce a generated value to a single string (LLMs sometimes return lists)."""
    if value is None:
        return default
    if isinstance(value, (list, tuple, set)):
        value = next((v for v in value if v), None)
    if value is None:
        return default
    return str(value).strip() or default


def _list(value):
    """Coerce a generated value to a list of strings, or None."""
    if value is None:
        return None
    if isinstance(value, str):
        value = [v.strip() for v in value.split(",") if v.strip()]
    try:
        items = [str(v).strip() for v in value if str(v).strip()]
    except TypeError:
        return None
    return items or None


def _ts(value, fallback=None):
    """Coerce a generated timestamp to an aware datetime."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = _str(value)
    if text:
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(text.replace("+00:00", "Z"), fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return fallback or _now()


def _fresh_ids(count, prefix):
    return [f"{prefix}--{uuid.uuid4()}" for _ in range(max(1, count))]


def _build_many(generated, maker):
    """Run one generator call, map each item through ``maker``, drop failures."""
    objects = []
    for item in generated:
        try:
            obj = maker(item)
        except Exception as exc:  # noqa: BLE001 - skip objects the generator malformed
            logger.warning("Skipping invalid object: %s", exc)
            continue
        if obj is not None:
            objects.append(obj)
    return objects


def create_threat_actors(count):
    return _build_many(generate_threat_actors(count), lambda item: ThreatActor(
        name=_str(getattr(item, "name", None), f"Threat actor {uuid.uuid4().hex[:6]}"),
        description=_str(getattr(item, "description", None)),
        threat_actor_types=_list(getattr(item, "threat_actor_types", None)),
        aliases=_list(getattr(item, "aliases", None)),
        roles=_list(getattr(item, "roles", None)),
        goals=_list(getattr(item, "goals", None)),
        sophistication=_str(getattr(item, "sophistication", None)),
        resource_level=_str(getattr(item, "resource_level", None)),
        primary_motivation=_str(getattr(item, "primary_motivation", None)),
        secondary_motivations=_list(getattr(item, "secondary_motivations", None)),
        personal_motivations=_list(getattr(item, "personal_motivations", None)),
    ))


def create_identities(count):
    return _build_many(generate_identity(count), lambda item: Identity(
        name=_str(getattr(item, "name", None), f"Identity {uuid.uuid4().hex[:6]}"),
        description=_str(getattr(item, "description", None)),
        identity_class=_str(getattr(item, "identity_class", None), "unknown"),
        roles=_list(getattr(item, "roles", None)),
        sectors=_list(getattr(item, "sectors", None)),
        contact_information=_str(getattr(item, "contact_information", None)),
    ))


def create_malwares(count):
    def maker(item):
        is_family = getattr(item, "is_family", True)
        if isinstance(is_family, str):
            is_family = is_family.strip().lower() in ("true", "1", "yes", "y")
        return Malware(
            name=_str(getattr(item, "name", None), f"Malware {uuid.uuid4().hex[:6]}"),
            description=_str(getattr(item, "description", None)),
            malware_types=_list(getattr(item, "malware_types", None)),
            is_family=bool(is_family),
            aliases=_list(getattr(item, "aliases", None)),
        )

    return _build_many(generate_malware(count), maker)


def create_indicators(count):
    def maker(item):
        pattern = _str(getattr(item, "pattern", None))
        if not pattern:
            raise ValueError("indicator without pattern")
        return Indicator(
            name=_str(getattr(item, "name", None), f"Indicator {uuid.uuid4().hex[:6]}"),
            description=_str(getattr(item, "description", None)),
            indicator_types=_list(getattr(item, "indicator_types", None)),
            pattern=pattern,
            pattern_type=_str(getattr(item, "pattern_type", None), "stix"),
            valid_from=_ts(getattr(item, "valid_from", None)),
            valid_until=_ts(getattr(item, "valid_until", None), _now() + timedelta(days=30)),
        )

    return _build_many(generate_indicator(count), maker)


def create_tools(count):
    return _build_many(generate_tool(count), lambda item: Tool(
        name=_str(getattr(item, "name", None), f"Tool {uuid.uuid4().hex[:6]}"),
        description=_str(getattr(item, "description", None)),
        tool_types=_list(getattr(item, "tool_types", None)),
        tool_version=_str(getattr(item, "tool_version", None)),
        aliases=_list(getattr(item, "aliases", None)),
    ))


def create_campaigns(count):
    return _build_many(generate_campaign(count), lambda item: Campaign(
        name=_str(getattr(item, "name", None), f"Campaign {uuid.uuid4().hex[:6]}"),
        description=_str(getattr(item, "description", None)),
        aliases=_list(getattr(item, "aliases", None)),
        objective=_str(getattr(item, "objective", None)),
        first_seen=_ts(getattr(item, "first_seen", None), _now() - timedelta(days=90)),
        last_seen=_ts(getattr(item, "last_seen", None)),
    ))


def create_intrusion_sets(count):
    return _build_many(generate_intrusion_set(count), lambda item: IntrusionSet(
        name=_str(getattr(item, "name", None), f"Intrusion set {uuid.uuid4().hex[:6]}"),
        description=_str(getattr(item, "description", None)),
        aliases=_list(getattr(item, "aliases", None)),
        first_seen=_ts(getattr(item, "first_seen", None), _now() - timedelta(days=180)),
        last_seen=_ts(getattr(item, "last_seen", None)),
    ))


def create_attack_patterns(count):
    return _build_many(generate_attack_pattern(count), lambda item: AttackPattern(
        name=_str(getattr(item, "name", None), f"Attack pattern {uuid.uuid4().hex[:6]}"),
        description=_str(getattr(item, "description", None)),
    ))


def create_course_of_actions(count):
    return _build_many(generate_course_of_action(count), lambda item: CourseOfAction(
        name=_str(getattr(item, "name", None), f"Course of action {uuid.uuid4().hex[:6]}"),
        description=_str(getattr(item, "description", None)),
    ))


def create_locations(count):
    def maker(item):
        latitude = getattr(item, "latitude", None)
        longitude = getattr(item, "longitude", None)
        return Location(
            name=_str(getattr(item, "name", None), f"Location {uuid.uuid4().hex[:6]}"),
            description=_str(getattr(item, "description", None)),
            region=_str(getattr(item, "region", None)),
            country=_str(getattr(item, "country", None)),
            administrative_area=_str(getattr(item, "administrative_area", None)),
            city=_str(getattr(item, "city", None)),
            latitude=float(latitude) if latitude is not None else None,
            longitude=float(longitude) if longitude is not None else None,
            precision=float(getattr(item, "precision", None) or 0.8),
        )

    return _build_many(generate_location(count), maker)


def create_vulnerabilities(count):
    return _build_many(generate_vulnerability(count), lambda item: Vulnerability(
        name=_str(getattr(item, "name", None), f"CVE-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:6]}"),
        description=_str(getattr(item, "description", None)),
    ))


def create_infrastructures(count):
    return _build_many(generate_infrastructure(count), lambda item: Infrastructure(
        name=_str(getattr(item, "name", None), f"Infrastructure {uuid.uuid4().hex[:6]}"),
        description=_str(getattr(item, "description", None)),
        infrastructure_types=_list(getattr(item, "infrastructure_types", None)),
        aliases=_list(getattr(item, "aliases", None)),
        first_seen=_ts(getattr(item, "first_seen", None), _now() - timedelta(days=60)),
        last_seen=_ts(getattr(item, "last_seen", None)),
    ))


def _refs(previous_ids, desired):
    """Pick ``desired`` distinct refs from the objects already generated."""
    if not previous_ids:
        return []
    count = min(len(previous_ids), max(1, desired))
    return list(dict.fromkeys(previous_ids))[:count]


def create_reports(count, previous_ids):
    def maker(item):
        refs = _refs(previous_ids, len(getattr(item, "object_refs", []) or [1, 2, 3]))
        if not refs:
            raise ValueError("report without object_refs")
        return Report(
            name=_str(getattr(item, "name", None), f"Report {uuid.uuid4().hex[:6]}"),
            description=_str(getattr(item, "description", None)),
            report_types=_list(getattr(item, "report_types", None)),
            published=_now(),
            object_refs=refs,
        )

    return _build_many(generate_report(count), maker)


def create_opinion(count, previous_ids):
    def maker(item):
        refs = _refs(previous_ids, len(getattr(item, "object_refs", []) or [1, 2]))
        if not refs:
            raise ValueError("opinion without object_refs")
        return Opinion(
            opinion=_str(getattr(item, "opinion", None), "neutral"),
            explanation=_str(getattr(item, "explanation", None)),
            authors=_list(getattr(item, "authors", None)),
            object_refs=refs,
        )

    return _build_many(generate_opinion(count), maker)


def create_malware_analysis(count):
    return _build_many(generate_malware_analysis(count), lambda item: MalwareAnalysis(
        product=_str(getattr(item, "product", None), f"Analysis {uuid.uuid4().hex[:6]}"),
        result=_str(getattr(item, "result", None)),
        submitted=_now(),
    ))
