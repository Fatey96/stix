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

"""# Schema for generating Grouping



"""

class Indicator(BaseModel):
    type: str
    spec_version: str
    id: str
    created: str
    modified: str
    pattern: str
    pattern_type: str
    valid_from: str
    #object_refs: str
    valid_until: str
    #kill_chain_phases: Optional[str] = None
    pattern_version: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    created_by_ref: Optional[str] = None
    indicator_types: Optional[str] = None

"""# Sample Data as example"""

examples = [
    {"example": """Type: indicator, spec_version: 2.1, id: indicator--8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f, created: 2016-04-06T20:03:48.000Z, modified: 2016-04-06T20:03:48.000Z, name: Poison Ivy malware, description: This file is part of Poision Ivy, pattern: [file:hashes.'SHA-256' = 'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592'], pattern_type: stix, valid_from: 2016-01-01T00:00:00Z"""},
    {"example": """Type: indicator, spec_version: 2.1, id: indicator--e8094b09-7df4-4b13-b207-1e27af3c4bde, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, pattern: [file:hashes.'SHA-256' = 'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592'], pattern_type: stix, valid_from: 2015-05-15T09:12:16.432678Z"""},
    {"example": """Type: indicator, spec_version: 2.1, id: indicator--329ae6e9-25bd-49e8-89d1-aae4ca52e4a7, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, pattern: [file:hashes.'SHA-256' = 'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592'], pattern_type: stix, valid_from: 2015-05-15T09:12:16.432678Z"""},
    {"example": """Type: indicator, spec_version: 2.1, id:indicator--54e1e351-fec0-41a4-b62c-d7f86101e241, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, pattern: [file:hashes.'SHA-256' = 'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592'], pattern_type: stix, valid_from: 2015-05-15T09:12:16.432678Z"""},
    {"example": """Type: indicator, spec_version: 2.1, id: indicator--2e59f00b-0986-437e-9ebd-e0d61900d688, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, pattern: [file:hashes.'SHA-256' = 'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592'], pattern_type: stix, valid_from: 2015-05-15T09:12:16.432678Z"""},
    {"example": """Type: indicator, spec_version: 2.1, id: indicator--8da68996-f175-4ae0-bd74-aad4913873b8, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z, pattern: [file:hashes.'SHA-256' = 'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592'], pattern_type: stix, valid_from: 2015-05-15T09:12:16.432678Z"""},
    {"example": """Type: indicator, spec_version: 2.1, id: indicator--4e11b23f-732b-418e-b786-4dbf65459d50, created: 2015-05-15T09:12:16.432Z, modified: 2015-05-15T09:12:16.432Z", pattern: [file:hashes.'SHA-256' = 'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592'], pattern_type: stix, valid_from: 2015-05-15T09:12:16.432678Z"""}
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
    output_schema=Indicator,
    llm=ChatOpenAI(temperature=1,model='gpt-4-turbo-preview'),
    prompt=prompt_template,
)

"""# Parameters"""

def generate_indicator(count): 
    synthetic_results = synthetic_data_generator.generate(
        subject="Indicator",
        extra="Choose a unique and unconventional type, name, description, indicator_types, pattern, pattern_type, pattern_version, valid_from, valid_until, kill_chain_phases for each Indicator. Avoid common or typical names. Ensure that the 'pattern' field always contains a valid SHA-256 hash representing the cryptographic signature of malware or other cybersecurity threats. This hash must accurately reflect a plausible and specific cybersecurity threat pattern. Make sure that the value provided for the pattern attribute is a valid SHA-256 hash, and that the hash is in the correct format. Make sure it DOES NOT contains characters that are not hexadecimal (kr), and keep in mind that a valid SHA-256 hash is a 64-character string consisting only of hexadecimal characters (0-9, a-f).",
        runs=count,
    )

    return synthetic_results