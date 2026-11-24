import os
"""# Imports"""

from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

from langchain_openai import ChatOpenAI

from pydantic import BaseModel

from datetime import datetime
from typing import List, Optional
from langchain_experimental.tabular_synthetic_data.base import SyntheticDataGenerator
from langchain_experimental.tabular_synthetic_data.openai import create_openai_data_generator, OPENAI_TEMPLATE
from langchain_experimental.tabular_synthetic_data.prompts import SYNTHETIC_FEW_SHOT_SUFFIX, SYNTHETIC_FEW_SHOT_PREFIX

"""# Schema for generating Location

"""

class Location(BaseModel):
    type: str
    spec_version: str
    id: str
    created: str
    modified: str
    name: str
    description: str
    latitude: float
    precision: float
    longitude: float
    region: str
    country: str
    administrative_area : str
    city: str
    street_address: str
    
    postal_code: str
    created_by_ref: Optional[str] = None
    revoked: Optional[str] = None
    confidence: Optional[str] = None
    lang: Optional[str] = None

"""# Sample Data as example"""

examples = [
   {"example": """Type: location, Name: Downtown Cyber Cafe, Description: A popular cyber cafe located in the heart of the city known for its high-speed internet and privacy booths., Latitude: '34.0522', Longitude: '-118.2437', Precision: '1.45', Region: 'Urban', Country: 'USA', Administrative_area: 'California', City: 'Los Angeles', Street_address: '123 Main St, UNIT: 42/B', Postal_code: '90015'"""},
   {"example": """Type: location, Name: Suburban Home Office, Description: A residential building in a quiet suburban neighborhood frequently used for remote work., Latitude: '51.5074', Longitude: '-0.1278', Precision: '50.4', Region: 'Suburban', Country: 'UK', Administrative_area: 'Greater London', City: 'London', Street_address: '47 Acacia Rd, UNIT: 4/C', Postal_code: 'SW2 3GT'"""},
   {"example": """Type: location, Name: City Park Wi-Fi Zone, Description: An open park area with public Wi-Fi access, often used by individuals seeking quiet outdoor workspaces., Latitude: '40.7128', Longitude: '-74.0060', Precision: '23.1', Region: 'Urban Park', Country: 'USA', Administrative_area: 'New York', City: 'New York City', Street_address: 'Central Park West', UNIT: 13, Postal_code: '10023'"""},
   {"example": """Type: location, Name: Mobile Tech Van, Description: A modified van equipped with advanced communication and hacking tools, used for mobile operations., Latitude: '52.5200', Longitude: '13.4050', Precision: '53.1', Region: 'Mobile', Country: 'Germany', Administrative_area: 'Berlin', City: 'Berlin', Street_address: 'Various Locations', Postal_code: '10117'"""},
   {"example": """Type: location, Name: Patel Brothers Call Center, Description: An indian call center that scams people and senior citizens., Latitude: '48.8566', Longitude: '2.3522', Precision: '0.1', Region: 'Commercial', Country: 'India', Administrative_area: 'Shahdara Road', City: 'Delhi', Street_address: 'Patel Brothers Electronics, UNIT: 3', Postal_code: '110019'"""},
   {"example": """Type: location, Name: Riverside Bench, Description: A secluded spot by the river known for its calm environment and occasional use by remote workers., Latitude: '35.6895', Longitude: '139.6917', Precision: '95.1', Region: 'Outdoor', Country: 'Japan', Administrative_area: 'Tokyo', City: 'Tokyo', Street_address: 'Near Kachidoki Bridge', Postal_code: '104-0061'"""},
   {"example": """Type: location, Name: Communal Library Study Room, Description: A study room in the local library, often used by students and remote workers for its quiet atmosphere., Latitude: '55.7558', Longitude: '37.6173', Precision: '10.0', Region: 'Urban', Country: 'Russia', Administrative_area: 'Moscow', City: 'Moscow', Street_address: 'Lenin Library', Postal_code: '101000'"""},
   {"example": """Type: location, Name: Underground Parking Garage, Description: A parking garage beneath a commercial complex, occasionally used for discreet meetings or operations., Latitude: '39.9042', Longitude: '116.4074', Precision: '25.5', Region: 'Subterranean', Country: 'China', Administrative_area: 'Beijing', City: 'Beijing', Street_address: 'Complex B8', Postal_code: '100044'"""},
   {"example": """Type: location, Name: Tech Startup Incubator, Description: A workspace in a tech startup incubator, known for its creative environment and high concentration of tech professionals., Latitude: '37.7749', Longitude: '-122.4194', Precision: '11.7', Region: 'Urban', Country: 'USA', Administrative_area: 'California', City: 'San Francisco', Street_address: 'Tech Hub Center', Postal_code: '94103'"""}
]

"""# Prompt Template for GPT-4"""

OPENAI_TEMPLATE = PromptTemplate(input_variables=["example"], template="{example}")

prompt_template = FewShotPromptTemplate(
    prefix=SYNTHETIC_FEW_SHOT_PREFIX,
    examples=examples,
    suffix=SYNTHETIC_FEW_SHOT_SUFFIX,
    input_variables=["subject", "extra"],
    example_prompt=OPENAI_TEMPLATE,
)

"""# Data Generator"""

_synthetic_data_generator = None

def _get_generator():
    """Build the LLM-backed generator on first use, never at import time."""
    global _synthetic_data_generator
    if _synthetic_data_generator is None:
        _synthetic_data_generator = create_openai_data_generator(
            output_schema=Location,
            llm=ChatOpenAI(temperature=1, model=os.getenv("GENERATOR_MODEL", "gpt-4o-mini")),
            prompt=prompt_template,
        )
    return _synthetic_data_generator

"""# Parameters"""

def generate_location(count):
    if not os.getenv("OPENAI_API_KEY"):
        from local_generator import generate_location as _offline
        return _offline(count)

    synthetic_results = _get_generator().generate(
        subject="Location",
        extra="Make the name, description, location data, postal code, precision, city, street_address, longtitude, latitude, region, administrative_area realistic. Never use any unrealistic place like Lost city of Atlantis. Make sure its from raal world geography (land) But only make the street_address non-existent, add a fake apartment number after the street address like UNIT number. Avoid Landmark places like Effiel Tower, etc.",
        runs=count,
    )

    return synthetic_results

