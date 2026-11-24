import os
# OPENAI_API_KEY must come from the environment (hardcoded key stripped when archived).
"""# Imports"""
import uuid
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.pydantic_v1 import BaseModel
from datetime import datetime
from typing import List, Optional
from langchain_experimental.tabular_synthetic_data.base import SyntheticDataGenerator
from langchain_experimental.tabular_synthetic_data.openai import create_openai_data_generator, OPENAI_TEMPLATE
from langchain_experimental.tabular_synthetic_data.prompts import SYNTHETIC_FEW_SHOT_SUFFIX, SYNTHETIC_FEW_SHOT_PREFIX

"""# Schema for generating Report"""

class Report(BaseModel):
    type: str
    spec_version: str
    id: str
    created: str
    modified: str
    name: str
    description: Optional[str] = None
    report_types: Optional[List[str]] = None
    published: str
    object_refs: List[str] = None

"""# Sample Data as example"""

examples = [
    {"example": """Type: report, Name: Annual Security Analysis, Description: A comprehensive review of the security incidents and measures implemented over the past year. This report helps in identifying trends and areas for improvement in the organization's cybersecurity practices.""", "Report Types": ["Annual Review", "Security"], "Published": "2024-05-25", "Object Refs": ["incident--5ba9d7f7-6dad-4b4c-927a-9d817c896cda", "response--5e0c66d1-8a0b-4bc7-90f3-3e22d540c076", "policy--3fcd5b5d-b911-4f47-a1f9-920f8639f3c8"]},
    {"example": """Type: report, Name: Quarterly Threat Landscape, Description: An analysis of the emerging cybersecurity threats and vulnerabilities discovered in the last quarter. This report guides the security team in updating defenses and training programs.""", "Report Types": ["Quarterly Update", "Threat Assessment"], "Published": "2024-04-01", "Object Refs": ["incident--5ba9d7f7-6dad-4b4c-927a-9d817c896cda", "response--5e0c66d1-8a0b-4bc7-90f3-3e22d540c076", "policy--3fcd5b5d-b911-4f47-a1f9-920f8639f3c8"]},
    {"example": """Type: report, Name: Incident Response Summary, Description: A detailed account of the response to a specific high-profile cybersecurity incident, including the steps taken to mitigate and lessons learned.""", "Report Types": ["Incident Report", "Response Analysis"], "Published": "2024-03-15", "Object Refs": ["incident--5ba9d7f7-6dad-4b4c-927a-9d817c896cda", "response--5e0c66d1-8a0b-4bc7-90f3-3e22d540c076", "policy--3fcd5b5d-b911-4f47-a1f9-920f8639f3c8"]},
    {"example": """Type: report, Name: Compliance Audit Findings, Description: Results from the latest compliance audit, detailing adherence to regulatory requirements and recommendations for addressing any gaps.""", "Report Types": ["Compliance", "Audit"], "Published": "2024-01-20", "Object Refs": ["incident--5ba9d7f7-6dad-4b4c-927a-9d817c896cda", "response--5e0c66d1-8a0b-4bc7-90f3-3e22d540c076", "policy--3fcd5b5d-b911-4f47-a1f9-920f8639f3c8"]},
    {"example": """Type: report, Name: Phishing Attack Trends, Description: An analysis focusing on the methods, frequency, and impact of phishing attacks against the organization, with strategies for enhancing phishing awareness and defense.""", "Report Types": ["Trend Analysis", "Phishing"], "Published": "2024-02-28", "Object Refs": ["incident--5ba9d7f7-6dad-4b4c-927a-9d817c896cda", "response--5e0c66d1-8a0b-4bc7-90f3-3e22d540c076", "policy--3fcd5b5d-b911-4f47-a1f9-920f8639f3c8"]},
    {"example": """Type: report, Name: Technology Adoption Report, Description: Evaluates the adoption rates and effectiveness of new technologies implemented within the organization over the past year.""", "Report Types": ["Technology Review", "Adoption Analysis"], "Published": "2024-05-10", "Object Refs": ["incident--5ba9d7f7-6dad-4b4c-927a-9d817c896cda", "response--5e0c66d1-8a0b-4bc7-90f3-3e22d540c076", "policy--3fcd5b5d-b911-4f47-a1f9-920f8639f3c8"]}
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
    output_schema=Report,
    llm=ChatOpenAI(temperature=1,model='gpt-4-turbo-preview'),
    prompt=prompt_template,
)

"""# Parameters"""

def generate_report(count):
    synthetic_results = synthetic_data_generator.generate(
        subject="report",
        extra="Generate each report with a unique name and a clear, detailed description that outlines its specific focus and relevance. Ensure object_refs is a valid STIX identifier. Each report should represent a different aspect of cybersecurity, and include a variety of object references to demonstrate breadth and depth of coverage.",
        runs=count,
    )
    return synthetic_results