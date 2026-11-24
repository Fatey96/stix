from faker import Faker
import re
#from stix2 import Identity
from StixObjectLang.ThreatActor import generate_threat_actors, ThreatActor
from StixObjectLang.Identity import generate_identity, Identity
from StixObjectLang.AttackPattern import AttackPattern, generate_attack_pattern
from StixObjectLang.CourseOfAction import CourseOfAction, generate_course_of_action
from StixObjectLang.Campaign import Campaign, generate_campaign
from StixObjectLang.Indicator import Indicator, generate_indicator
from StixObjectLang.IntrusionSet import IntrusionSet, generate_intrusion_set
from StixObjectLang.Report import Report, generate_report
from StixObjectLang.Location import Location, generate_location
from StixObjectLang.Malware import Malware, generate_malware
from StixObjectLang.Vulnerability import Vulnerability, generate_vulnerability
from StixObjectLang.Infrastructure import Infrastructure, generate_infrastructure
from StixObjectLang.MalwareAnalysis import MalwareAnalysis, generate_malware_analysis
from StixObjectLang.ObservedData import ObservedData, generate_observed_data
from StixObjectLang.Opinion import Opinion, generate_opinion
#from StixObjectLang.note import Note, generate_note
from StixObjectLang.tool import Tool, generate_tool
from datetime import datetime, timedelta
from dateutil.parser import parse
import random
import uuid
from typing import List, Optional

fake = Faker()

def create_threat_actors(count):
    synthetic_results = generate_threat_actors(count)

    # Convert the synthetic results to the format expected by STIX
    fake_threat_actors = []
    for item in synthetic_results:
        fake_threat_actor = ThreatActor(
            type=item.type,
            spec_version="2.1",
            id="threat-actor--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
            threat_actor_types=item.threat_actor_types,
            aliases=item.aliases,
            first_seen=datetime.utcnow().isoformat() + "Z",
            last_seen=datetime.utcnow().isoformat() + "Z",
            roles=item.roles,
            goals=item.goals,
            sophistication=item.sophistication,
            resource_level=item.resource_level,
            primary_motivation=item.primary_motivation,
            secondary_motivations=item.secondary_motivations,
            personal_motivations=item.personal_motivations
        )
        fake_threat_actors.append(fake_threat_actor)

    return fake_threat_actors


def create_vulnerabilities(count):
    synthetic_results = generate_vulnerability(count)
    fake_vulnerabilities = []
    for item in synthetic_results:
        current_time = datetime.utcnow().isoformat() + "Z"
        fake_vulnerability = Vulnerability(
            type=item.type,
            spec_version="2.1",
            id="vulnerability--" + str(uuid.uuid4()),
            created=current_time,
            modified=current_time,
            name=item.name,
            description=item.description
        )
        fake_vulnerabilities.append(fake_vulnerability)

    return fake_vulnerabilities


def create_infrastructures(count):
    synthetic_results = generate_infrastructure(count)
    fake_infrastructures = []
    for item in synthetic_results:
     #   processed_kill_chain_phases = [
    #        KillChainPhase(**phase) if isinstance(phase, dict) else phase 
    #        for phase in item.kill_chain_phases
    #    ] if item.kill_chain_phases else None
        fake_infrastructure = Infrastructure(
            type=item.type,
            spec_version="2.1",
            id="infrastructure--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            infrastructure_types=item.infrastructure_types,
            aliases=item.aliases,
            first_seen=item.first_seen,
            last_seen=item.last_seen,
     #       kill_chain_phases=processed_kill_chain_phases
        )
        fake_infrastructures.append(fake_infrastructure)

    return fake_infrastructures


def create_identities(count):
    synthetic_results = generate_identity(count)
    fake_identities = []

    print(f"Generated {len(synthetic_results)} synthetic results")

    for item in synthetic_results:
        print(f"Processing item: {item}")
        try:
            fake_identity = Identity(
                type=item.type,
                spec_version="2.1",
                id="identity--" + str(uuid.uuid4()),
                created=datetime.utcnow().isoformat() + "Z",
                modified=datetime.utcnow().isoformat() + "Z",
                name=item.name,
                description=item.description,
                roles=item.roles,
                identity_class=item.identity_class,
                sectors=item.sectors,
                contact_information=item.contact_information
            )
            fake_identities.append(fake_identity)
            print(f"Successfully created Identity: {fake_identity}")
        except Exception as e:
            print(f"Error creating Identity: {e}")

    print(f"Created {len(fake_identities)} fake identities")
    return fake_identities

def create_reports(count, previous_ids: List[str]):
    synthetic_results = generate_report(count)
    fake_reports = []

    id_iterator = iter(previous_ids)  # Create an iterator from the list of previous IDs

    for item in synthetic_results:
        object_refs = []
        try:
            # Assign IDs to object_refs, cycling through the previous IDs list
            for _ in range(len(item.object_refs)):
                object_refs.append(next(id_iterator))
        except StopIteration:
            # If the iterator is exhausted, reinitialize it to start from the beginning
            id_iterator = iter(previous_ids)
            for _ in range(len(item.object_refs)):
                object_refs.append(next(id_iterator))
        
        # Directly set object_refs without validation
        fake_report = Report(
            type=item.type,
            spec_version="2.1",
            id="report--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
            report_types=item.report_types,
            published=datetime.utcnow().isoformat() + "Z",
            object_refs=object_refs,
        )
        fake_reports.append(fake_report)

    return fake_reports

def create_malwares(count):
    synthetic_results = generate_malware(count)
    fake_malwares = []
    for item in synthetic_results:
        fake_malware = Malware(
            type=item.type,
            spec_version="2.1",
            id="malware--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
            malware_types=item.malware_types,
            is_family=bool(item.is_family),  # Ensure is_family is a boolean
            aliases=item.aliases,
            first_seen=datetime.utcnow().isoformat() + "Z",
            last_seen=datetime.utcnow().isoformat() + "Z",
        )
        fake_malwares.append(fake_malware)

    return fake_malwares

def create_campaigns(count):
    synthetic_results = generate_campaign(count)
    fake_campaigns = []
    for item in synthetic_results:
        fake_campaign = Campaign(
            type=item.type,
            spec_version="2.1",
            id="campaign--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
            aliases=item.aliases,
            objective=item.objective,
            first_seen=datetime.utcnow().isoformat() + "Z",
            last_seen=datetime.utcnow().isoformat() + "Z",
        )
        fake_campaigns.append(fake_campaign)

    return fake_campaigns


def create_indicators(count):
    synthetic_results = generate_indicator(count)  # You need to implement this function
    fake_indicators = []
    for item in synthetic_results:
        #object_refs = [f"{ref.type}--{ref.id}" for ref in item.object_refs]
        fake_indicator = Indicator(
            type=item.type,
            spec_version="2.1",
            id="indicator--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
            indicator_types=item.indicator_types,
            pattern=item.pattern,
            pattern_type=item.pattern_type,
            valid_from=datetime.utcnow().isoformat() + "Z",
            valid_until=(datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
        )
        fake_indicators.append(fake_indicator)

    return fake_indicators


def create_attack_patterns(count):
    synthetic_results = generate_attack_pattern(count)
    fake_attack_patterns = []
    for item in synthetic_results:
        fake_attack_pattern = AttackPattern(
            type=item.type,
            spec_version="2.1",
            id="attack-pattern--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
        )
        fake_attack_patterns.append(fake_attack_pattern)

    return fake_attack_patterns



"""def create_campaigns(count):
    synthetic_results = generate_campaign(count)
    fake_campaigns = []
    for item in synthetic_results:
        fake_campaign = Campaign(
            type=item.type,
            spec_version="2.1",
            id="campaign--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
            aliases=item.aliases,
            first_seen=parse(item.first_seen).isoformat() + "Z",
            last_seen=parse(item.last_seen).isoformat() + "Z",
            objective=item.objective
        )
        fake_campaigns.append(fake_campaign)

    return fake_campaigns"""


def create_intrusion_sets(count):
    synthetic_results = generate_intrusion_set(count)
    fake_intrusion_sets = []
    for item in synthetic_results:
        fake_intrusion_set = IntrusionSet(
            type="intrusion-set",
            spec_version="2.1",
            id="intrusion-set--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
            aliases=item.aliases,
            first_seen=datetime.utcnow().isoformat() + "Z",
            last_seen=datetime.utcnow().isoformat() + "Z",
        )
        fake_intrusion_sets.append(fake_intrusion_set)

    return fake_intrusion_sets

"""def create_vulnerabilities(count):
    synthetic_results = generate_vulnerability(count)
    fake_vulnerabilities = []
    for item in synthetic_results:
        fake_vulnerability = Vulnerability(
            type=item.type,
            spec_version="2.1",
            id="vulnerability--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
            vulnerability_types=item.vulnerability_types,
            first_seen=parse(item.first_seen).isoformat() + "Z",
            last_seen=parse(item.last_seen).isoformat() + "Z",
            severity=item.severity,
            impact=item.impact,
            likelihood=item.likelihood
        )
        fake_vulnerabilities.append(fake_vulnerability)

    return fake_vulnerabilities"""


def create_tools(count):
    synthetic_results = generate_tool(count)
    fake_tools = []
    for item in synthetic_results:
        fake_tool = Tool(
            type=item.type,
            spec_version="2.1",
            id="tool--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
            tool_version=item.tool_version,
            tool_types=item.tool_types,
       #     kill_chain_phases=item.kill_chain_phases,
            aliases=item.aliases
        )
        fake_tools.append(fake_tool)

    return fake_tools


from stix2 import CourseOfAction
from datetime import datetime
import uuid

def create_course_of_actions(count):
    synthetic_results = generate_course_of_action(count)
    fake_courses_of_action = []
    for item in synthetic_results:
        fake_course_of_action = CourseOfAction(
            type=item.type,
            spec_version="2.1",
            id="course-of-action--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description
        )
        fake_courses_of_action.append(fake_course_of_action)

    return fake_courses_of_action


def create_opinion(count, previous_ids: List[str]):
    synthetic_results = generate_opinion(count)
    fake_opinions = []
    
    id_iterator = iter(previous_ids)  # Create an iterator from the list of previous IDs

    for item in synthetic_results:
        object_refs = []
        try:
            # Assign IDs to object_refs, cycling through the previous IDs list
            for _ in range(len(item.object_refs)):
                object_refs.append(next(id_iterator))
        except StopIteration:
            # If the iterator is exhausted, reinitialize it to start from the beginning
            id_iterator = iter(previous_ids)
            for _ in range(len(item.object_refs)):
                object_refs.append(next(id_iterator))
        
        # Directly set object_refs without validation
        fake_opinion = Opinion(
            type=item.type,
            spec_version="2.1",
            id="opinion--" + str(uuid.uuid4()), 
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            authors=item.authors,
            explanation=item.explanation,
            opinion=item.opinion,
            object_refs=object_refs
        )
        fake_opinions.append(fake_opinion)

    return fake_opinions


"""def create_notes(count, previous_ids: List[str]):
    synthetic_results = generate_note(count)
    fake_notes = []
    
    for item in synthetic_results:
        object_refs = set()  # Use a set to avoid duplicates
        id_iterator = iter(previous_ids)  # Reinitialize iterator for each note

        while len(object_refs) < len(item.object_refs):
            try:
                potential_ref = next(id_iterator)
                # Ensure the potential_ref is not already in object_refs
                if potential_ref not in object_refs:
                    object_refs.add(potential_ref)
            except StopIteration:
                # Reinitialize iterator if exhausted
                id_iterator = iter(previous_ids)
        
        # Convert object_refs back to a list for compatibility
        object_refs = list(object_refs)
        
        fake_note = Note(
            type=item.type,
            abstract=item.abstract,
            authors=item.authors,
            object_refs=object_refs
        )
        fake_notes.append(fake_note)

    return fake_notes"""



def create_locations(count):
    synthetic_results = generate_location(count)
    fake_locations = []
    for item in synthetic_results:
        fake_location = Location(
            type=item.type,
            spec_version="2.1",
            id="location--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            name=item.name,
            description=item.description,
            latitude=item.latitude,
            longitude=item.longitude,
            precision=item.precision,
            region=item.region,
            country=item.country,
            administrative_area=item.administrative_area,
            city=item.city,
            street_address=item.street_address,
            postal_code=item.postal_code
        )
        fake_locations.append(fake_location)

    return fake_locations


def create_malware_analysis(count):
    synthetic_results = generate_malware_analysis(count)
    fake_malware_analysis = []
    for item in synthetic_results:
        fake_malware_analyses = MalwareAnalysis(
            type=item.type,
            spec_version="2.1",
            id="malware-analysis--" + str(uuid.uuid4()),
            created=datetime.utcnow().isoformat() + "Z",
            modified=datetime.utcnow().isoformat() + "Z",
            product=item.product,
            result=item.result,
        )
        fake_malware_analysis.append(fake_malware_analyses)
    return fake_malware_analysis

