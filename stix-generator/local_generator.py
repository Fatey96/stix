"""Offline STIX object generator.

Deterministic, dependency-light fallback used when OPENAI_API_KEY is not set.
It produces the same attribute surface as the LLM-backed ``generate_*``
functions in ``StixObjectLang/`` so ``stix_object_builder`` wraps the results
into real ``stix2`` objects without changes.

Values are drawn from the STIX 2.1 open vocabularies where those exist
(threat-actor-type-ov, attack-motivation-ov, malware-type-ov, ...), so the
output stays schema-valid without a language model.
"""

import random
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from faker import Faker

fake = Faker()

THREAT_ACTOR_TYPES = [
    "activist", "competitor", "crime-syndicate", "criminal", "hacker",
    "insider-accidental", "insider-disgruntled", "nation-state",
    "sensationalist", "spy", "terrorist", "unknown",
]
MOTIVATIONS = [
    "accidental", "coercion", "dominance", "ideology", "notoriety",
    "organizational-gain", "personal-gain", "personal-satisfaction",
    "revenge", "unpredictable", "unknown",
]
RESOURCE_LEVELS = ["individual", "club", "contest", "team", "organization", "government", "unknown"]
SOPHISTICATION = ["none", "minimal", "intermediate", "advanced", "expert", "innovator", "strategic", "unknown"]
ROLES = ["director", "independent", "infrastructure-operator", "malware-author", "agent", "sponsor", "executor", "planner"]
IDENTITY_CLASSES = ["individual", "group", "system", "organization", "class", "unknown"]
SECTORS = [
    "agriculture", "aerospace", "automotive", "chemical", "commercial",
    "communications", "construction", "defense", "education", "energy",
    "entertainment", "financial-services", "government", "healthcare",
    "hospitality", "insurance", "manufacturing", "mining", "non-profit",
    "pharmaceuticals", "retail", "technology", "telecommunications",
    "transportation", "utilities",
]
MALWARE_TYPES = [
    "adware", "backdoor", "bot", "bootkit", "ddos", "downloader", "dropper",
    "exploit-kit", "keylogger", "ransomware", "remote-access-trojan",
    "resource-exploitation", "rootkit", "screen-capture", "spyware",
    "trojan", "unknown", "virus", "webshell", "wiper", "worm",
]
TOOL_TYPES = [
    "denial-of-service", "exploitation", "information-gathering",
    "network-capture", "credential-exploitation", "reconnaissance", "unknown",
]
INFRASTRUCTURE_TYPES = [
    "amplification", "anonymization", "beaconing", "command-and-control",
    "content-delivery", "control-system", "exfiltration", "firewall",
    "hosting", "load-balancing", "malware-distribution", "routing",
]
INDICATOR_TYPES = ["anomalous-activity", "benign", "compromised", "malicious-activity", "unknown"]
REPORT_TYPES = [
    "attack-pattern", "campaign", "identity", "indicator", "intrusion-set",
    "malware", "observed-data", "threat-actor", "threat-report", "tool", "vulnerability",
]
OPINIONS = ["strongly-disagree", "disagree", "neutral", "agree", "strongly-agree"]
REGIONS = [
    "africa", "central-asia", "eastern-asia", "europe", "latin-america-caribbean",
    "middle-east", "north-america", "south-asia", "southeast-asia", "southwestern-asia",
]
KILL_PHASES = [
    "reconnaissance", "resource-development", "initial-access", "execution",
    "persistence", "privilege-escalation", "defense-evasion",
    "credential-access", "discovery", "lateral-movement", "collection",
    "command-and-control", "exfiltration", "impact",
]
ATTACK_PATTERNS = [
    "Spearphishing Attachment", "Command and Scripting Interpreter",
    "Remote Services", "Valid Accounts", "Obfuscated Files or Information",
    "OS Credential Dumping", "Exploitation for Client Execution",
    "Data Encrypted for Impact", "Exfiltration Over Web Service",
    "Create or Modify System Process", "Phishing", "Brute Force",
]
MALWARE_NAMES = ["Nightshade", "CopperHollow", "RustVector", "GlassLatch", "SableMoth",
                 "IronWeed", "PaleRook", "HollowGate", "EmberDrift", "VaultSnare"]
VULN_PREFIXES = ["CVE-2024-", "CVE-2025-", "CVE-2026-"]


def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _window(days=120):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=random.randint(1, days))
    return start.isoformat() + "Z", end.isoformat() + "Z"


def _pick(values, k=1):
    return random.sample(values, k=min(k, len(values)))


def _actor_name():
    style = random.random()
    if style < 0.4:
        return f"{random.choice(['Silent', 'Crimson', 'Glass', 'Iron', 'Hollow', 'Pale', 'Cobalt'])} {random.choice(['Wolf', 'Harbor', 'Mantis', 'Lantern', 'Rook', 'Falcon', 'Drift'])}"
    if style < 0.7:
        return f"APT-{random.randint(10, 99)}"
    return fake.company()


def _description(name, extra=""):
    templates = [
        f"{name} is a threat group observed conducting intrusions against {random.choice(SECTORS)} organizations, "
        f"typically beginning with spearphishing and pivoting into credential theft. {extra}",
        f"{name} maintains tooling for {random.choice(KILL_PHASES)} operations and has been linked to "
        f"{random.randint(2, 9)} campaigns attributed by public reporting. {extra}",
        f"{name} focuses on {random.choice(['espionage', 'financial theft', 'data destruction', 'ransomware deployment'])} "
        f"against {random.choice(REGIONS).replace('-', ' ')} targets. {extra}",
    ]
    return random.choice(templates).strip()


def generate_threat_actors(count):
    actors = []
    for _ in range(count):
        name = _actor_name()
        first_seen, last_seen = _window(700)
        actors.append(SimpleNamespace(
            type="threat-actor",
            name=name,
            description=_description(name),
            threat_actor_types=_pick(THREAT_ACTOR_TYPES, random.randint(1, 2)),
            aliases=_pick(MALWARE_NAMES, random.randint(0, 2)) if random.random() < 0.5 else None,
            roles=_pick(ROLES, random.randint(1, 2)),
            goals=[f"{random.choice(['Collect', 'Disrupt', 'Exfiltrate', 'Monetize'])} {random.choice(['intelligence', 'infrastructure', 'customer data', 'source code'])}"],
            sophistication=random.choice(SOPHISTICATION),
            resource_level=random.choice(RESOURCE_LEVELS),
            primary_motivation=random.choice(MOTIVATIONS),
            secondary_motivations=_pick(MOTIVATIONS, 1),
            personal_motivations=_pick(MOTIVATIONS, 1),
            first_seen=first_seen,
            last_seen=last_seen,
        ))
    return actors


def generate_identities(count):
    identities = []
    for _ in range(count):
        if random.random() < 0.5:
            name = fake.company()
            identity_class = random.choice(["organization", "group"])
        else:
            name = fake.name()
            identity_class = "individual"
        identities.append(SimpleNamespace(
            type="identity",
            name=name,
            description=f"{name} is a {identity_class} operating in the {random.choice(SECTORS)} sector.",
            roles=_pick(["customer", "provider", "victim", "target", "researcher"], 1),
            identity_class=identity_class,
            sectors=_pick(SECTORS, random.randint(1, 2)),
            contact_information=f"{fake.email()} / {fake.phone_number()}",
        ))
    return identities


def generate_malwares(count):
    malwares = []
    for _ in range(count):
        name = random.choice(MALWARE_NAMES) + (f" {random.randint(1, 9)}" if random.random() < 0.3 else "")
        malwares.append(SimpleNamespace(
            type="malware",
            name=name,
            description=f"{name} is a {random.choice(MALWARE_TYPES)} family used for {random.choice(['credential theft', 'remote access', 'data encryption', 'lateral movement'])}.",
            malware_types=_pick(MALWARE_TYPES, random.randint(1, 2)),
            is_family=random.random() < 0.7,
            aliases=_pick(MALWARE_NAMES, random.randint(0, 2)),
        ))
    return malwares


def generate_indicators(count):
    indicators = []
    for _ in range(count):
        kind = random.choice(["ipv4-addr", "domain-name", "url", "file"])
        if kind == "ipv4-addr":
            pattern = f"[ipv4-addr:value = '{fake.ipv4_public()}']"
        elif kind == "domain-name":
            pattern = f"[domain-name:value = '{fake.domain_name()}']"
        elif kind == "url":
            pattern = f"[url:value = '{fake.url()}']"
        else:
            pattern = f"[file:hashes.'SHA-256' = '{fake.sha256()}']"
        indicators.append(SimpleNamespace(
            type="indicator",
            name=f"{kind} indicator {uuid.uuid4().hex[:8]}",
            description=f"Observed {kind} associated with {random.choice(['C2 traffic', 'payload delivery', 'exfiltration'])}.",
            indicator_types=_pick(INDICATOR_TYPES[:-1], 1),
            pattern=pattern,
            pattern_type="stix",
            valid_from=_now(),
            valid_until=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat() + "Z",
        ))
    return indicators


def generate_tools(count):
    tools = []
    for _ in range(count):
        name = f"{random.choice(['Sharp', 'Ghost', 'Blue', 'Kek', 'Mimik', 'Net', 'Rube'])}{random.choice(['Sight', 'Hound', 'Cat', 'Loader', 'Kit', 'Scan'])}"
        tools.append(SimpleNamespace(
            type="tool",
            name=name,
            description=f"{name} is a {random.choice(TOOL_TYPES).replace('-', ' ')} utility observed in intrusions.",
            tool_version=f"{random.randint(1, 5)}.{random.randint(0, 9)}",
            tool_types=_pick(TOOL_TYPES[:-1], 1),
            aliases=[name.lower().replace(" ", "-")],
        ))
    return tools


def generate_campaigns(count):
    campaigns = []
    for _ in range(count):
        name = f"Operation {random.choice(['Amber', 'Cobalt', 'Silent', 'Broken', 'Frozen', 'Hollow'])} {random.choice(['Tide', 'Ledger', 'Crown', 'Harvest', 'Signal'])}"
        first_seen, last_seen = _window(400)
        campaigns.append(SimpleNamespace(
            type="campaign",
            name=name,
            description=f"{name} targets {random.choice(SECTORS)} organizations for {random.choice(['data theft', 'extortion', 'espionage'])}.",
            objective=f"{random.choice(['Intellectual property theft', 'Financial extortion', 'Credential harvesting', 'Disruption of operations'])}",
            aliases=_pick(MALWARE_NAMES, random.randint(0, 1)),
            first_seen=first_seen,
            last_seen=last_seen,
        ))
    return campaigns


def generate_intrusion_sets(count):
    sets = []
    for _ in range(count):
        name = _actor_name()
        first_seen, last_seen = _window(900)
        sets.append(SimpleNamespace(
            type="intrusion-set",
            name=name,
            description=f"{name} clusters tooling and infrastructure used across multiple intrusions.",
            aliases=_pick(MALWARE_NAMES, random.randint(0, 2)),
            first_seen=first_seen,
            last_seen=last_seen,
        ))
    return sets


def generate_attack_patterns(count):
    patterns = []
    for _ in range(count):
        name = random.choice(ATTACK_PATTERNS)
        patterns.append(SimpleNamespace(
            type="attack-pattern",
            name=name,
            description=f"Adversaries may use {name.lower()} to achieve their objectives.",
        ))
    return patterns


def generate_course_of_action(count):
    actions = []
    for _ in range(count):
        phase = random.choice(KILL_PHASES)
        name = f"Mitigate {phase.replace('-', ' ').title()} Techniques"
        actions.append(SimpleNamespace(
            type="course-of-action",
            name=name,
            description=f"Controls that reduce the likelihood or impact of {phase.replace('-', ' ')} activity.",
        ))
    return actions


def generate_locations(count):
    locations = []
    for _ in range(count):
        country = fake.country()
        locations.append(SimpleNamespace(
            type="location",
            name=country,
            description=f"Location referencing {country}.",
            latitude=round(random.uniform(-60, 70), 4),
            longitude=round(random.uniform(-170, 170), 4),
            precision=round(random.uniform(0.5, 0.99), 2),
            region=random.choice(REGIONS),
            country=country.upper()[:2] if len(country) >= 2 else "ZZ",
            administrative_area=None,
            city=fake.city(),
            street_address=None,
            postal_code=None,
        ))
    return locations


def generate_vulnerability(count):
    vulns = []
    for _ in range(count):
        cve = f"{random.choice(VULN_PREFIXES)}{random.randint(1000, 49999)}"
        vulns.append(SimpleNamespace(
            type="vulnerability",
            name=cve,
            description=f"{cve} allows {random.choice(['remote code execution', 'privilege escalation', 'information disclosure', 'denial of service'])} in affected products.",
        ))
    return vulns


def generate_infrastructure(count):
    infra = []
    for _ in range(count):
        kind = random.choice(INFRASTRUCTURE_TYPES)
        name = f"{kind.replace('-', ' ').title()} node {uuid.uuid4().hex[:6]}"
        first_seen, last_seen = _window(300)
        infra.append(SimpleNamespace(
            type="infrastructure",
            name=name,
            infrastructure_types=[kind],
            aliases=[fake.domain_name()],
            first_seen=first_seen,
            last_seen=last_seen,
        ))
    return infra


def generate_opinion(count):
    opinions = []
    for _ in range(count):
        opinions.append(SimpleNamespace(
            type="opinion",
            authors=[f"analyst-{uuid.uuid4().hex[:6]}"],
            explanation=f"Assessment based on {random.randint(2, 8)} corroborating observations.",
            opinion=random.choice(OPINIONS),
            object_refs=[f"indicator--{uuid.uuid4()}" for _ in range(random.randint(1, 3))],
        ))
    return opinions


def generate_report(count):
    reports = []
    for _ in range(count):
        reports.append(SimpleNamespace(
            type="report",
            name=f"Threat report {datetime.now(timezone.utc).date()} #{uuid.uuid4().hex[:4]}",
            description=f"Reporting on {random.choice(['ransomware', 'espionage', 'phishing', 'supply chain'])} activity.",
            report_types=_pick(REPORT_TYPES[:-1], random.randint(1, 2)),
            object_refs=[f"identity--{uuid.uuid4()}" for _ in range(random.randint(2, 5))],
        ))
    return reports


def generate_malware_analysis(count):
    analyses = []
    for _ in range(count):
        analyses.append(SimpleNamespace(
            type="malware-analysis",
            product=f"{random.choice(['Sandbox', 'Static', 'Hybrid'])} analysis run {uuid.uuid4().hex[:6]}",
            result=random.choice(["malicious", "suspicious", "benign", "unknown"]),
        ))
    return analyses


def generate_observed_data(count):
    data = []
    for _ in range(count):
        now = datetime.utcnow()
        data.append(SimpleNamespace(
            type="observed-data",
            first_observed=(now - timedelta(hours=random.randint(1, 72))).isoformat() + "Z",
            last_observed=now.isoformat() + "Z",
            number_observed=random.randint(1, 50),
        ))
    return data


def generate_note(count):
    notes = []
    for _ in range(count):
        notes.append(SimpleNamespace(
            type="note",
            abstract=f"Analyst note {uuid.uuid4().hex[:6]}",
            authors=[f"analyst-{uuid.uuid4().hex[:4]}"],
            object_refs=[f"malware--{uuid.uuid4()}"],
        ))
    return notes


# Aliases matching the exact names used by the StixObjectLang modules.
generate_attack_pattern = generate_attack_patterns
generate_campaign = generate_campaigns
generate_course_of_action = generate_course_of_action
generate_identity = generate_identities
generate_indicator = generate_indicators
generate_infrastructure = generate_infrastructure
generate_intrusion_set = generate_intrusion_sets
generate_location = generate_locations
generate_malware = generate_malwares
generate_opinion = generate_opinion
generate_report = generate_report
generate_tool = generate_tools
generate_vulnerability = generate_vulnerability
