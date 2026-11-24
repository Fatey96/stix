import os
# OPENAI_API_KEY must come from the environment (hardcoded key stripped when archived).
"""# Imports"""

from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.pydantic_v1 import BaseModel
from datetime import datetime
from typing import List, Optional
from langchain_experimental.tabular_synthetic_data.base import SyntheticDataGenerator
from langchain_experimental.tabular_synthetic_data.openai import create_openai_data_generator, OPENAI_TEMPLATE
from langchain_experimental.tabular_synthetic_data.prompts import SYNTHETIC_FEW_SHOT_SUFFIX, SYNTHETIC_FEW_SHOT_PREFIX

"""# Schema for generating Identity"""

class Identity(BaseModel):
    type: str
    spec_version: str
    id: str
    created: str
    modified: str
    name: str
    description: str
    roles: str
    identity_class: Optional[str] = None
    sectors: Optional[List[str]] = None
    contact_information: Optional[str] = None

"""# Sample Data as example"""

examples = [
    {"example": """Type: identity, Name: Red Team Group, Description: A specialized group within the organization focused on simulating cyber attacks to test and improve security measures. They conduct controlled, authorized attacks to identify vulnerabilities.""", "Roles": "Attack Simulation Team", "Identity Class": "group", "Sectors": ["Technology", "Security"], "Contact Information": "redteam@tascorps.com"},
    {"example": """Type: identity, Name: Incident Response Team, Description: A team responsible for managing security breaches and incidents. They assess, mitigate, and recover from security incidents to minimize their impact.""", "Roles": "Incident Handling", "Identity Class": "group", "Sectors": ["Corporate", "Security"], "Contact Information": "incidentresponse@msisacare.com"},
    {"example": """Type: identity, Name: Chief Information Security Officer, Description: An executive who oversees the corporate security direction and ensures compliance with security policies and standards. The role includes leading the security team and advising on risk management.""", "Roles": "Executive", "Identity Class": "individual", "Sectors": ["Corporate", "Security"], "Contact Information": "ciso@dodcorp.com"},
    {"example": """Type: identity, Name: Cybersecurity Policy Analyst, Description: A professional responsible for analyzing and developing security policies. They work to ensure that security measures align with business objectives and regulatory requirements.""", "Roles": "Policy Development", "Identity Class": "individual", "Sectors": ["Government", "Corporate"], "Contact Information": "policyanalyst@cyber.gov"},
    {"example": """Type: identity, Name: Software Development Team, Description: A team of developers responsible for creating and maintaining software applications. They ensure that security is integrated into all phases of software development.""", "Roles": "Software Development", "Identity Class": "group", "Sectors": ["Technology"], "Contact Information": "devteam@softwaresolutions.com"},
    {"example": """Type: identity, Name: Network Administrator, Description: An IT professional tasked with managing and maintaining the organization's computer networks. Their responsibilities include ensuring network security and optimizing network performance.""", "Roles": "Network Management", "Identity Class": "individual", "Sectors": ["Technology", "Corporate"], "Contact Information": "networkadmin@techcorp.com"},
    {"example": """Type: identity, Name: Regulatory Compliance Team, Description: A group focused on ensuring that the organization meets all applicable laws, regulations, and guidelines regarding cybersecurity and data protection.""", "Roles": "Compliance Management", "Identity Class": "group", "Sectors": ["Healthcare", "Finance"], "Contact Information": "compliance@financehealth.org"},
    {"example": """Type: identity, Name: Security Operations Center (SOC), Description: The central unit that deals with security issues on an organizational and technical level. The SOC monitors, assesses, and defends against cybersecurity threats.""", "Roles": "Security Monitoring", "Identity Class": "group", "Sectors": ["Technology", "Security"], "Contact Information": "soc@globaltech.com"},
    {"example": """Type: identity, Name: Data Protection Officer, Description: An individual responsible for overseeing data protection strategy and implementation to ensure compliance with data protection regulations.""", "Roles": "Data Protection", "Identity Class": "individual", "Sectors": ["Corporate", "Healthcare"], "Contact Information": "dpo@healthcorporate.com"}
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
    output_schema=Identity,
    llm=ChatOpenAI(temperature=1,model='gpt-4-turbo-preview'),
    prompt=prompt_template,
)

"""# Parameters"""

def generate_identity(count):
    synthetic_results = synthetic_data_generator.generate(
        subject="identity",
        extra="Ensure each identity has role and represents diverse sectors. Include realistic but non-existent contact information for each, don't use 'example.com' as a domain in the contact information and make sure the domain is a fake made up name that looks like a cybersecurity related organization.",
        runs=count,
    )
    return synthetic_results