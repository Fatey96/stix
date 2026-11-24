from stix2 import Relationship
import random

# Relationship map
relationship_map = {
    "threat-actor": {"identity": ["attributed-to"], "attack-pattern": ["uses"], "malware": ["uses"], "tool": ["uses"], "vulnerability": ["targets"]},
    "identity": {"threat-actor": ["attributed-to"], "campaign": ["attributed-to"], "campaign": ["targets"]},  
    "malware": {"vulnerability": ["exploits"], "tool": ["uses"], "attack-pattern": ["uses"], "campaign": ["originates-from"], "threat-actor": ["authored-by"]},
    "indicator": {"campaign": ["indicates"], "malware": ["indicates"], "threat-actor": ["indicates"], "tool": ["indicates"], "intrusion-set": ["indicates"]},
    "campaign": {"threat-actor": ["attributed-to"], "intrusion-set": ["attributed-to"], "identity": ["targets"], "vulnerability": ["targets"], "tool": ["uses"], "malware": ["uses"]},
    "intrusion-set": {"campaign": ["part-of"], "threat-actor": ["attributed-to"]},
    #"attack-pattern": {"malware": ["delivers"], "identity": ["targets"], "vulnerability": ["targets"], "tool": ["uses"]},
    "tool": {"threat-actor": ["uses"], "malware": ["uses"]},
    #"report": {"identity": ["related-to"], "malware-analysis": ["related-to"]},
    "course-of-action": {"indicator": ["investigates"], "observed-data": ["based-on"], "indicator": ["mitigates"], "attack-pattern": ["mitigates"], "malware": ["remediates"], "vulnerability": ["remediates"], "tool": ["mitigates"]},
    "location": {"identity": ["located-at"], "threat-actor": ["located-at"], "campaign": ["originates-from"], "malware": ["originates-from"], "intrusion-set": ["originates-from"], "attack-pattern": ["targets"], "tool": ["targets"], "campaign": ["targets"], "intrusion-set": ["targets"], "malware": ["targets"], "threat-actor": ["targets"]},
    "malware-analysis": {"malware": ["characterizes"], "malware": ["analysis-of"], "malware": ["static-analysis-of"], "malware": ["dynamic-analysis-of"]},
    "infrastructure": {"threat-actor": ["compromised-by"], "infrastructure": ["consists-of"], "tool": ["hosts"], "malware": ["hosts"], "campaign": ["used-by", "hosts"]},
    "opinion": {"indicator": ["related-to"], "threat-actor": ["related-to"], "attack-pattern": ["related-to"], "campaign": ["related-to"], "incident": ["related-to"], "malware": ["related-to"], "tool": ["related-to"], "vulnerability": ["related-to"], "infrastructure": ["related-to"], "intrusion-set": ["related-to"], "malware-analysis": ["related-to"], "threat-report": ["related-to"], "identity": ["related-to"]},
    "vulnerability": {"attack-pattern": ["targets"], "campaign": ["targets"], "intrusion-set": ["targets"], "malware": ["targets"], "threat-actor": ["targets"], "tool": ["targets"],"malware": ["exploits"], "course-of-action": ["mitigates"], "infrastructure": ["has"]}
    #"note": {"attack-pattern": ["related-to"], "vulnerability": ["related-to"], "malware-analysis": ["related-to"]}
}

def randomly_connect_objects(stix_objects, max_relationships_per_object=3, probability_map=None):
    if probability_map is None:
        probability_map = {rel: 1.0 for rel in relationship_map.keys()} 

    relationships = []
    for source_obj in stix_objects:
        source_type = source_obj.type
        if source_type not in relationship_map:
            print(f"Skipping unsupported source type: {source_type}")
            continue

        potential_targets = [(target_obj, relationship_map[source_type].get(target_obj.type, []))
                             for target_obj in stix_objects if source_obj.id != target_obj.id]
        random.shuffle(potential_targets)
        potential_targets = potential_targets[:max_relationships_per_object]

        for target_obj, rel_types in potential_targets:
            if rel_types:
                weighted_rel_types = [(rel, probability_map.get(rel, 1.0)) for rel in rel_types]
                total_weight = sum(weight for rel, weight in weighted_rel_types)
                r = random.uniform(0, total_weight)
                upto = 0
                for rel, weight in weighted_rel_types:
                    if upto + weight >= r:
                        rel_type = rel
                        break
                    upto += weight

                try:
                    relationship = Relationship(relationship_type=rel_type, source_ref=source_obj.id, target_ref=target_obj.id)
                    relationships.append(relationship)
                except Exception as e:
                    print(f"Failed to create relationship: {e} (source: {source_obj.id}, target: {target_obj.id}, type: {rel_type})")

    return relationships
