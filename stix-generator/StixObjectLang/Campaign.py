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

"""# Schema for generating Campaign"""

class Campaign(BaseModel):
    type: str
    spec_version: str
    id: str
    created: str
    modified: str
    name: str
    description: str
    objective: str
    first_seen: Optional[str] = None
    aliases: Optional[List[str]] = None
    last_seen: Optional[str] = None

"""# Sample Data as example"""

examples = [
    {"example": """Type: campaign, spec_version: 2.1, id: campaign--7e33a43e-e34b-40ec-89da-36c9bb2cacd5, created: 2016-05-12T08:17:27.000Z, modified: 2016-05-12T08:17:27.000Z, name: Operation Phantom Phish, description: A coordinated campaign targeting financial institutions to steal credentials through sophisticated phishing attacks., objective: 'Credential theft', first_seen: '2016-01-01T00:00:00Z', aliases: ['Phantom Phishing Operation'], last_seen: '2016-06-01T00:00:00Z'"""},
    {"example": """Type: campaign, spec_version: 2.1, id: campaign--19da6e1c-71ab-4c2f-886d-d620d09d3b5a, created: 2016-08-08T15:50:10.983Z, modified: 2017-01-30T21:15:04.127Z, name: Silent Prowler, description: Silent Prowler focuses on infiltrating corporate networks to deploy ransomware without detection., objective: 'Ransomware deployment', first_seen: '2016-02-15T00:00:00Z', aliases: ['Prowler Campaign'], last_seen: '2016-04-15T00:00:00Z'"""},
    {"example": """Type: campaign, spec_version: 2.1, id: campaign--f6050ea6-a9a3-4524-93ed-c27858d6cb3c, created: 2016-08-08T15:50:10.983Z, modified: 2017-01-30T21:15:04.127Z, name: Midnight Espionage, description: This campaign involves espionage against political figures, aiming to influence elections through the acquisition and leak of sensitive communications., objective: 'Political influence and espionage', first_seen: '2016-03-01T00:00:00Z', aliases: ['Midnight Leak'], last_seen: '2016-05-01T00:00:00Z'"""},
    {"example": """Type: campaign, spec_version: 2.1, id: campaign--8ac90ff3-ecf8-4835-95b8-6aea6a623df5, created: 2015-05-07T14:22:14.760Z, modified: 2015-05-07T14:22:14.760Z, name: Echoes of Silence, description: Echoes of Silence targets telecommunications infrastructure to intercept and manipulate communications covertly., objective: 'Communications interception and manipulation', first_seen: '2015-01-20T00:00:00Z', aliases: ['Echoes Campaign'], last_seen: '2015-04-20T00:00:00Z'"""},
    {"example": """Type: campaign, spec_version: 2.1, id: campaign--3098c57b-d623-4c11-92f4-5905da66658b, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, name: Operation Data Dominion, description: Operation Data Dominion aims to exfiltrate intellectual property from tech companies to gain competitive advantages in the market., objective: 'Intellectual property theft', first_seen: '2015-02-10T00:00:00Z', aliases: ['Data Dominion'], last_seen: '2015-06-10T00:00:00Z'"""}
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
            output_schema=Campaign,
            llm=ChatOpenAI(temperature=1, model=os.getenv("GENERATOR_MODEL", "gpt-4o-mini")),
            prompt=prompt_template,
        )
    return _synthetic_data_generator

"""# Parameters"""

def generate_campaign(count):
    if not os.getenv("OPENAI_API_KEY"):
        from local_generator import generate_campaign as _offline
        return _offline(count)

    synthetic_results = _get_generator().generate(
        subject="campaign",
        extra="Generate each campaign with a unique name and detailed description that illustrates its specific tactics, targets, and objectives. Ensure that each entry provides a clear objective, such as 'intellectual property theft' or 'political influence', and include realistic timelines for when the campaign was first and last seen. Also, include aliases to reflect other known names for the campaign, enhancing realism and depth in the dataset.",
        runs=count,
    )
    return synthetic_results