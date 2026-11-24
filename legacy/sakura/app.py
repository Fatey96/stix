from flask import Flask, render_template, request, jsonify
from stix_object_builder import (
    create_threat_actors, create_identities, create_malwares,
    create_indicators, create_tools, create_reports, create_infrastructures,
    create_intrusion_sets, create_course_of_actions, create_campaigns, create_opinion, create_attack_patterns, create_locations, create_malware_analysis,
    create_vulnerabilities
)
from relationship_builder import randomly_connect_objects
from stix_bundler import create_bundle
from flask_cors import CORS
from flask_cors import cross_origin
from collections import Counter
from datetime import datetime
from stix2validator import validate_instance
from STIXRelationshipAgent import STIXRelationshipAgent
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
import logging
import json

app = Flask(__name__)
CORS(app)

def calculate_metrics(stix_bundle):
    stix_data = json.loads(stix_bundle)
    
    # Metric 1: Completeness
    total_objects = len(stix_data['objects'])
    objects_with_all_required_fields = sum(1 for obj in stix_data['objects'] if all(field in obj for field in ['id', 'type', 'created']))
    completeness_score = (objects_with_all_required_fields / total_objects) * 100

    # Metric 2: Consistency
    validation_results = validate_instance(stix_data)
    # Count the number of errors
    error_count = len(validation_results.errors)
    consistency_score = 100 - (error_count / total_objects * 100)

    # Metric 3: Timeliness
    current_time = datetime.now()
    objects_with_recent_timestamp = sum(1 for obj in stix_data['objects'] if 'created' in obj and (current_time - datetime.strptime(obj['created'], "%Y-%m-%dT%H:%M:%S.%fZ")).days < 30)
    timeliness_score = (objects_with_recent_timestamp / total_objects) * 100

    # Metric 4: Object Type Distribution
    object_types = Counter(obj['type'] for obj in stix_data['objects'])

    # Metric 5: Relationship Richness
    relationship_count = sum(1 for obj in stix_data['objects'] if obj['type'] == 'relationship')
    relationship_ratio = relationship_count / total_objects

    return {
        "total_objects": total_objects,
        "completeness_score": completeness_score,
        "consistency_score": consistency_score,
        "timeliness_score": timeliness_score,
        "object_type_distribution": dict(object_types),
        "relationship_ratio": relationship_ratio
    }

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_story_from_bundle(stix_bundle):
    # Parse the STIX bundle
    bundle_data = json.loads(stix_bundle)
    objects = bundle_data['objects']

    # Extract relevant information
    threat_actors = [obj for obj in objects if obj['type'] == 'threat-actor']
    malwares = [obj for obj in objects if obj['type'] == 'malware']
    indicators = [obj for obj in objects if obj['type'] == 'indicator']
    relationships = [obj for obj in objects if obj['type'] == 'relationship']

    # Create a summary of the objects and relationships
    summary = []
    summary.append(f"Threat Actors: {len(threat_actors)}")
    summary.append(f"Malware: {len(malwares)}")
    summary.append(f"Indicators: {len(indicators)}")
    summary.append(f"Relationships: {len(relationships)}")

    for relationship in relationships:
        source_obj = next((obj for obj in objects if obj['id'] == relationship['source_ref']), None)
        target_obj = next((obj for obj in objects if obj['id'] == relationship['target_ref']), None)
        if source_obj and target_obj:
            summary.append(f"{source_obj['type']} ({source_obj.get('name', 'Unnamed')}) {relationship['relationship_type']} {target_obj['type']} ({target_obj.get('name', 'Unnamed')})")

    # Create a prompt for the language model
    story_prompt = PromptTemplate(
        input_variables=["summary"],
        template="""Based on the following summary of a STIX bundle:

{summary}

Please provide a brief, coherent story that describes the cyber threat scenario represented by these objects and relationships. Focus on the key actors, their motivations, and the progression of their activities. The story should be easily understandable by a non-technical audience.

Limit your response to 3-5 paragraphs."""
    )
    
    llm = ChatOpenAI(temperature=0.7, model_name='gpt-4')
    story_chain = story_prompt | llm
    
    try:
        result = story_chain.invoke({"summary": "\n".join(summary)})
        story = result.content
        logger.info(f"Generated Story: {story}")
        return story
    except Exception as e:
        logger.error(f"Error generating story: {e}")
        return "Unable to generate story due to an error."
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select-objects', methods=['GET'])
def select_objects():
    return render_template('select_objects.html')

@app.route('/generate-graph', methods=['POST'])
@cross_origin()
def generate_graph():
    data = request.form
    threat_actor_count = int(data.get('threat-actor-count', 0))
    identity_count = int(data.get('identity-count', 0))
    malware_count = int(data.get('malware-count', 0))
    indicators_count = int(data.get('indicator-count', 0))
    infrastructure_count = int(data.get('infrastructure-count', 0))
    tools_count = int(data.get('tool-count', 0))
    campaigns_count = int(data.get('campaign-count', 0))
    intrusion_sets_count = int(data.get('intrusion-set-count', 0))
    course_of_actions_count = int(data.get('course-of-action-count', 0))
    reports_count = int(data.get('report-count', 0))
    opinions_count = int(data.get('opinion-count', 0))
    attack_patterns_count = int(data.get('attack-pattern-count', 0))
    locations_count = int(data.get('location-count', 0))
    malware_analysis_count = int(data.get('malware-analysis-count', 0))
    vulnerabilities_count = int(data.get('vulnerability-count', 0))


    threat_actors = create_threat_actors(threat_actor_count) if threat_actor_count > 0 else []
    identities = create_identities(identity_count) if identity_count > 0 else []
    malwares = create_malwares(malware_count) if malware_count > 0 else []
    indicators = create_indicators(indicators_count) if indicators_count > 0 else []
    infrastructures = create_infrastructures(infrastructure_count) if infrastructure_count > 0 else []
    tools = create_tools(tools_count) if tools_count > 0 else []
    campaigns = create_campaigns(campaigns_count) if campaigns_count > 0 else []
    intrusion_sets = create_intrusion_sets(intrusion_sets_count) if intrusion_sets_count > 0 else []
    course_of_actions = create_course_of_actions(course_of_actions_count) if course_of_actions_count > 0 else []
    attack_patterns = create_attack_patterns(attack_patterns_count) if attack_patterns_count > 0 else []
    locations = create_locations(locations_count) if locations_count > 0 else []
    malware_analysis = create_malware_analysis(malware_analysis_count) if malware_analysis_count > 0 else []
    vulnerabilities = create_vulnerabilities(vulnerabilities_count) if vulnerabilities_count > 0 else []

    # Initialize reports and opinions as empty lists
    reports = []
    opinions = []

    # Collect all generated objects
    stix_objects = (
        threat_actors + identities + malwares + indicators + tools +
        intrusion_sets + course_of_actions + infrastructures + campaigns + attack_patterns + locations + malware_analysis + vulnerabilities
    )

    # Collect all IDs
    previous_ids = [obj.id for obj in stix_objects]

    # Generate reports using the collected IDs
    if reports_count > 0:
        reports = create_reports(reports_count, previous_ids)

    # Generate opinions using the collected IDs
    if opinions_count > 0:
        opinions = create_opinion(opinions_count, previous_ids)

    # Add reports and opinions to the list of STIX objects
    stix_objects += reports + opinions

    for obj in stix_objects:
        print(obj)

    relationships = randomly_connect_objects(stix_objects)

    stix_bundle = create_bundle(stix_objects, relationships)
    
    # Calculate metrics
    metrics = calculate_metrics(stix_bundle)

    # Generate story
    story = generate_story_from_bundle(stix_bundle)
    # Calculate metrics
    metrics = calculate_metrics(stix_bundle)

    return jsonify({
        "stix_bundle": stix_bundle,
        "metrics": metrics,
        "story": story
    })

if __name__ == '__main__':
    app.run(debug=True)
