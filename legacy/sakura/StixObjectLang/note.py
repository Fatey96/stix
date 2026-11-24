import os
# OPENAI_API_KEY must come from the environment (hardcoded key stripped when archived).
"""# Imports"""

from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.pydantic_v1 import BaseModel
from datetime import datetime
from typing import List, Optional
from langchain_experimental.tabular_synthetic_data.base import SyntheticDataGenerator
from langchain_experimental.tabular_synthetic_data.openai import create_openai_data_generator, OPENAI_TEMPLATE
from langchain_experimental.tabular_synthetic_data.prompts import SYNTHETIC_FEW_SHOT_SUFFIX, SYNTHETIC_FEW_SHOT_PREFIX

"""# Schema for generating Note

"""

class Note(BaseModel):
    type: str
    abstract: str
    authors: List[str]
    object_refs: List[str]

"""# Sample Data as example"""

examples = [
    {"example": """Type: note, abstract: Detailed analysis of the cyber espionage techniques used by the Phantom Falcon group, authors: ["SOC Analyst David Frank", "Brandon Hunt"], object_refs: ["threat-actor--8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f", "tool--4567d1e2-89ab-42f3-b3b5-f456789abcd1", "vulnerability--2345b2d4-607e-4c6c-9247-123654b7c1d2"]"""},
    {"example": """Type: note, abstract: Overview of the covert operations executed by the Black Shadow Syndicate, authors: ["Analyst Dylan Carpenter", "Ethan Hunt"], object_refs: ["campaign--3456def1-2345-6789-abcd-ef1234567890", "malware--54e1e351-fec0-41a4-b62c-d7f86101e241", "indicator--329ae6e9-25bd-49e8-89d1-aae4ca52e4a7"]"""},
    {"example": """Type: note, abstract: Investigative report on the cyber attack orchestrated by the Crimson Viper group, authors: ["Analyst Tylor Grande", "Jason Bourne"], object_refs: ["identity--5678abcd-9101-2345-efgh-ijklmnopqrst", "malware-analysis--f82356ae-fe6c-437c-9c24-6b64314ae68a"]"""},
    {"example": """Type: note, abstract: Forensic analysis of the data breach involving the Ghost Raven collective, authors: ["Cybersecurity Specialist Quan Yuan", "Hercule Poirot"], object_refs: ["tool--4567d1e2-89ab-42f3-b3b5-f456789abcd1", "campaign--83422c77-904c-4dc1-aff5-5c38f3a2c55c"]"""},
    {"example": """Type: note, abstract: Strategic assessment of the threat posed by the Dark Serpent espionage network, authors: ["FBI Cybersecurity Analyst Name: CLASSIFIED", "Camaron Maartin"], object_refs: ["threat-actor--8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f", "infrastructure--4567d1e2-89ab-42f3-b3b5-f456789abcd1", "tool--2345b2d4-607e-4c6c-9247-123654b7c1d2"]"""},
    {"example": """Type: note, abstract: Tactical review of the cyber warfare capabilities of the Iron Hydra group, authors: ["Natasha Romanoff", "Steve Rogers"], object_refs: ["malware--54e1e351-fec0-41a4-b62c-d7f86101e241", "indicator--329ae6e9-25bd-49e8-89d1-aae4ca52e4a7", "campaign--3456def1-2345-6789-abcd-ef1234567890"]"""},
    {"example": """Type: note, abstract: Case study on the ransomware attacks executed by the Silver Wolf gang, authors: ["Peter Smith", "Clark Kent"], object_refs: ["indicator--2e59f00b-0986-437e-9ebd-e0d61900d688", "tool--f82356ae-fe6c-437c-9c24-6b64314ae68a", "malware--329ae6e9-25bd-49e8-89d1-aae4ca52e4a7"]"""},
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

synthetic_data_generator = create_openai_data_generator(
    output_schema=Note,
    llm=ChatOpenAI(temperature=1,model='gpt-4-turbo-preview'),
    prompt=prompt_template,
)

"""# Parameters"""

def generate_note(count):
    synthetic_results = synthetic_data_generator.generate(
        subject="Note",
        extra="Make sure the object_refs are valid STIX Objects. Include a comprehensive Note supporting the Note, alongside appropriate references to STIX objects with valid STIX identifiers (e.g., 'indicator--329ae6e9-25bd-49e8-89d1-aae4ca52e4a7'). Ensure each opinion reflects a clear and plausible perspective on the referenced cybersecurity issues or incidents, with all referenced object identifiers adhering to the required format.",
        runs=count,
    )

    return synthetic_results

