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

"""# Schema for generating Opinion

"""

class Opinion(BaseModel):
    type: str
    spec_version: str
    id: str
    created: str
    modified: str
    opinion: str
    authors: List[str]
    explanation: str
    object_refs: List[str]

"""# Sample Data as example"""

examples = [
    {"example": """Type: opinion, spec_version: 2.1, id: opinion--8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f, created: 2016-04-06T20:03:48.000Z, modified: 2016-04-06T20:03:48.000Z, opinion: 'agree', authors: ['Alice Johnson'], explanation: 'The analysis aligns well with our current understanding of the threat actor.', object_refs: ['indicator--329ae6e9-25bd-49e8-89d1-aae4ca52e4a7'], name: 'Threat Actor Analysis'"""},

    {"example": """Type: opinion, spec_version: 2.1, id: opinion--e8094b09-7df4-4b13-b207-1e27af3c4bde, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, opinion: 'strongly-agree', authors: ['Bob Smith'], explanation: 'The evidence provided clearly supports the claims made about the malware.', object_refs: ['malware--2345b2d4-607e-4c6c-9247-123654b7c1d2'], name: 'Malware Capability Review'"""},

    {"example": """Type: opinion, spec_version: 2.1, id: opinion--329ae6e9-25bd-49e8-89d1-aae4ca52e4a7, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, opinion: 'neutral', authors: ['Carol Lee'], explanation: 'There is insufficient data to support or refute the hypothesis.', object_refs: ['campaign--3456def1-2345-6789-abcd-ef1234567890'], name: 'Campaign Impact Assessment'"""},

    {"example": """Type: opinion, spec_version: 2.1, id: opinion--54e1e351-fec0-41a4-b62c-d7f86101e241, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, opinion: 'disagree', authors: ['David Frank'], explanation: 'The conclusions drawn are premature given the current dataset.', object_refs: ['tool--4567d1e2-89ab-42f3-b3b5-f456789abcd1'], name: 'Tool Efficacy Discussion'"""},

    {"example": """Type: opinion, spec_version: 2.1, id: opinion--2e59f00b-0986-437e-9ebd-e0d61900d688, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, opinion: 'strongly-disagree', authors: ['Eve Stuart'], explanation: 'The report does not accurately reflect the known behaviors of the intrusion set.', object_refs: ['intrusion-set--5678abcd-9101-2345-efgh-ijklmnopqrst'], name: 'Intrusion Set Behavior Analysis'"""}
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
    output_schema=Opinion,
    llm=ChatOpenAI(temperature=1,model='gpt-4-turbo-preview'),
    prompt=prompt_template,
)

"""# Parameters"""

def generate_opinion(count):
    synthetic_results = synthetic_data_generator.generate(
        subject="Opinion",
        extra="Generate each Opinion with a valid opinion value from the enumeration: strongly-disagree, disagree, neutral, agree, strongly-agree. Include a comprehensive explanation supporting the opinion, alongside appropriate references to STIX objects with valid STIX identifiers (e.g., 'indicator--329ae6e9-25bd-49e8-89d1-aae4ca52e4a7'). Ensure each opinion reflects a clear and plausible perspective on the referenced cybersecurity issues or incidents, with all referenced object identifiers adhering to the required format.. Make sure the opinion is one of these things: strongly-disagree, disagree, neutral, agree, strongly-agree.",
        runs=count,
    )

    return synthetic_results

