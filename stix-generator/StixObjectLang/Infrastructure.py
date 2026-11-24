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


"""# Schema for generating Infrastructure"""

#class KillChainPhase(BaseModel):
 #   kill_chain_name: str
 #   phase_name: str

class Infrastructure(BaseModel):
    type: str
    spec_version: str
    id: str
    created: str
    modified: str
    name: str
    infrastructure_types: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    #kill_chain_phases : List[str]

"""# Sample Data as example"""

examples = [
    {"example": """Type: infrastructure, spec_version: 2.1, id: infrastructure--7e33a43e-e34b-40ec-89da-36c9bb2cacd5, created: 2016-05-12T08:17:27.000Z, modified: 2016-05-12T08:17:27.000Z, name: Command and Control Server, infrastructure_types: ['command-and-control'], aliases: ['C2 Server'], first_seen: '2016-01-01T00:00:00Z', last_seen: '2016-06-01T00:00:00Z'"""},

    {"example": """Type: infrastructure, spec_version: 2.1, id: infrastructure--19da6e1c-71ab-4c2f-886d-d620d09d3b5a, created: 2016-08-08T15:50:10.983Z, modified: 2017-01-30T21:15:04.127Z, name: Phishing Domain, infrastructure_types: ['phishing'], aliases: ['Fake Banking Site'], first_seen: '2016-02-15T00:00:00Z', last_seen: '2016-04-15T00:00:00Z'"""},

    {"example": """Type: infrastructure, spec_version: 2.1, id: infrastructure--f6050ea6-a9a3-4524-93ed-c27858d6cb3c, created: 2016-08-08T15:50:10.983Z, modified: 2017-01-30T21:15:04.127Z, name: Malware Distribution Network, infrastructure_types: ['malware-distribution'], aliases: ['Malware CDN'], first_seen: '2016-03-01T00:00:00Z', last_seen: '2016-05-01T00:00:00Z'"""},

    {"example": """Type: infrastructure, spec_version: 2.1, id: infrastructure--8ac90ff3-ecf8-4835-95b8-6aea6a623df5, created: 2015-05-07T14:22:14.760Z, modified: 2015-05-07T14:22:14.760Z, name: Exploit Kit Hosting Site, infrastructure_types: ['exploit-kit'], aliases: ['EK Site'], first_seen: '2015-01-20T00:00:00Z', last_seen: '2015-04-20T00:00:00Z'"""},

    {"example": """Type: infrastructure, spec_version: 2.1, id: infrastructure--3098c57b-d623-4c11-92f4-5905da66658b, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, name: Botnet Network, infrastructure_types: ['botnet'], aliases: ['Zombie Network'], first_seen: '2015-02-10T00:00:00Z', last_seen: '2015-06-10T00:00:00Z'"""}
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
            output_schema=Infrastructure,
            llm=ChatOpenAI(temperature=1, model=os.getenv("GENERATOR_MODEL", "gpt-4o-mini")),
            prompt=prompt_template,
        )
    return _synthetic_data_generator

"""# Parameters"""

def generate_infrastructure(count):
    if not os.getenv("OPENAI_API_KEY"):
        from local_generator import generate_infrastructure as _offline
        return _offline(count)

    synthetic_results = _get_generator().generate(
        subject="infrastructure",
        extra="Generate each infrastructure entry with a distinct name and a clear description of its purpose and usage in cyber operations. Each entry should include appropriate infrastructure types from the open vocabulary, such as 'command-and-control', 'phishing', or 'malware-distribution'. Also, provide realistic first_seen and last_seen dates to simulate operational timelines.",
        runs=count,
    )
    return synthetic_results