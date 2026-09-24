"""
AI System Architect Advisor with DeepSeek R1 and Claude.

This module provides an agentic system for software architecture analysis
using DeepSeek R1 for reasoning and Claude 3.5 Sonnet for synthesis.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union

import anthropic
import streamlit as st
from agno.agent import Agent, RunResponse
from agno.models.anthropic import Claude
from dotenv import load_dotenv
from enum import Enum
from openai import OpenAI
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Model constants
DEEPSEEK_MODEL: str = "deepseek-reasoner"
CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"


class ArchitecturePattern(str, Enum):
    """Architectural patterns for system design."""
    MICROSERVICES = "microservices"
    MONOLITHIC = "monolithic"
    SERVERLESS = "serverless"
    EVENT_DRIVEN = "event_driven"


class DatabaseType(str, Enum):
    """Types of database systems."""
    SQL = "sql"
    NOSQL = "nosql"
    HYBRID = "hybrid"


class ComplianceStandard(str, Enum):
    """Regulatory compliance standards."""
    HIPAA = "hipaa"
    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"


class ArchitectureDecision(BaseModel):
    """Represents architectural decisions and their justifications."""

    pattern: ArchitecturePattern
    rationale: str = Field(..., min_length=50)
    trade_offs: Dict[str, List[str]] = Field(..., alias="trade_offs")
    estimated_cost: Dict[str, float]


class SecurityMeasure(BaseModel):
    """Security controls and implementation details."""

    measure_type: str
    implementation_priority: int = Field(..., ge=1, le=5)
    compliance_standards: List[ComplianceStandard]
    data_classification: str


class InfrastructureResource(BaseModel):
    """Infrastructure components and specifications."""

    resource_type: str
    specifications: Dict[str, str]
    scaling_policy: Dict[str, str]
    estimated_cost: float


class TechnicalAnalysis(BaseModel):
    """Complete technical analysis of the system architecture."""

    architecture_decision: ArchitectureDecision
    infrastructure_resources: List[InfrastructureResource]
    security_measures: List[SecurityMeasure]
    database_choice: DatabaseType
    compliance_requirements: List[ComplianceStandard] = []
    performance_requirements: List[Dict[str, Union[str, float]]] = []
    risk_assessment: Dict[str, str] = {}


class ModelChain:
    """Chain of models for architecture analysis."""

    def __init__(self, deepseek_api_key: str, anthropic_api_key: str) -> None:
        """
        Initialize the ModelChain.

        Args:
            deepseek_api_key: DeepSeek API key
            anthropic_api_key: Anthropic API key
        """
        self.client = OpenAI(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com"
        )
        self.claude_client = anthropic.Anthropic(api_key=anthropic_api_key)

        claude_model = Claude(
            id="claude-3-5-sonnet-20241022",
            api_key=anthropic_api_key,
            system_prompt="""Given the user's query and the DeepSeek reasoning:
            1. Provide a detailed analysis of the architecture decisions
            2. Generate a project implementation roadmap
            3. Create a comprehensive technical specification document
            4. Format the output in clean markdown with proper sections
            5. Include diagrams descriptions in mermaid.js format"""
        )

        self.agent = Agent(
            model=claude_model,
            markdown=True
        )

        self.deepseek_messages: List[Dict[str, str]] = []
        self.claude_messages: List[Dict[str, Any]] = []
        self.current_model: str = CLAUDE_MODEL

    def get_deepseek_reasoning(self, user_input: str) -> tuple[str, str]:
        """
        Get reasoning from DeepSeek R1.

        Args:
            user_input: User's architecture query

        Returns:
            tuple: (reasoning_content, normal_content)
        """
        start_time = time.time()

        system_prompt = """You are an expert software architect and technical advisor. Analyze the user's project requirements
        and provide structured reasoning about architecture, tools, and implementation strategies.

        IMPORTANT: Reason why you are choosing a particular architecture pattern, database type, etc. for user understanding in your reasoning.

        IMPORTANT: Your response must be a valid JSON object (not a string or any other format) that matches the schema provided below.
        Do not include any explanatory text, markdown formatting, or code blocks - only return the JSON object.

        Schema:
        {
            "architecture_decision": {
                "pattern": "one of: microservices|monolithic|serverless|event_driven|layered",
                "rationale": "string",
                "trade_offs": {"advantage": ["list of strings"], "disadvantage": ["list of strings"]},
                "estimated_cost": {"implementation": float, "maintenance": float}
            },
            "infrastructure_resources": [{
                "resource_type": "string",
                "specifications": {"key": "value"},
                "scaling_policy": {"key": "value"},
                "estimated_cost": float
            }],
            "security_measures": [{
                "measure_type": "string",
                "implementation_priority": "integer 1-5",
                "compliance_standards": ["hipaa", "gdpr", "soc2", "iso27001"],
                "data_classification": "string"
            }],
            "database_choice": "one of: sql|nosql|graph|time_series|hybrid",
            "performance_requirements": [{
                "metric_name": "string",
                "target_value": float,
                "measurement_unit": "string",
                "priority": "integer 1-5"
            }],
            "risk_assessment": {"risk": "mitigation"},
            "compliance_requirements": ["list of compliance standards"]
        }

        Consider scalability, security, maintenance, and technical debt in your analysis.
        Focus on practical, modern solutions while being mindful of trade-offs."""

        try:
            deepseek_response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=3000,
                stream=False
            )

            reasoning_content = deepseek_response.choices[0].message.reasoning_content
            normal_content = deepseek_response.choices[0].message.content

            with st.expander("DeepSeek Reasoning", expanded=True):
                st.markdown(reasoning_content)

            with st.expander("💭 Technical Analysis", expanded=True):
                st.markdown(normal_content)
                elapsed_time = time.time() - start_time
                time_str = (
                    f"{elapsed_time/60:.1f} minutes"
                    if elapsed_time >= 60
                    else f"{elapsed_time:.1f} seconds"
                )
                st.caption(f"⏱️ Analysis completed in {time_str}")

            return reasoning_content, normal_content

        except Exception as e:
            logger.error(f"Error in DeepSeek analysis: {str(e)}")
            st.error(f"Error in DeepSeek analysis: {str(e)}")
            return "Error occurred while analyzing", ""

    def get_claude_response(
        self,
        user_input: str,
        deepseek_output: tuple[str, str]
    ) -> str:
        """
        Get synthesis from Claude.

        Args:
            user_input: User's architecture query
            deepseek_output: DeepSeek reasoning and analysis

        Returns:
            Claude's response
        """
        try:
            reasoning_content, normal_content = deepseek_output

            with st.expander("🤖 Claude's Response", expanded=True):
                response_placeholder = st.empty()

                message = f"""User Query: {user_input}

                DeepSeek Reasoning: {reasoning_content}

                DeepSeek Technical Analysis: {normal_content}
                Give detailed explanation for each key value pair in brief in the JSON object, and why we chose it clearly.
                Dont use your own opinions, use the reasoning and the structured output to explain the choices."""

                response: RunResponse = self.agent.run(message=message)

                dub = response.content
                st.markdown(dub)
                return dub

        except Exception as e:
            logger.error(f"Error in Claude response: {str(e)}")
            st.error(f"Error in Claude response: {str(e)}")
            return "Error occurred while getting response"


def main() -> None:
    """Main application entry point."""
    st.title("🤖 AI System Architect Advisor with R1")

    st.info("""
    📝 For best results, structure your prompt with:

    1. **Project Context**: Brief description of your project/system
    2. **Requirements**: Key functional and non-functional requirements
    3. **Constraints**: Any technical, budget, or time constraints
    4. **Scale**: Expected user base and growth projections
    5. **Security/Compliance**: Any specific security or regulatory needs

    Example:
    ```
    I need to build a healthcare data management system that:
    - Handles patient records and appointments
    - Needs to scale to 10,000 users
    - Must be HIPAA compliant
    - Budget constraint of $50k for initial setup
    - Should integrate with existing hospital systems
    ```
    """)

    with st.sidebar:
        st.header("⚙️ Configuration")
        deepseek_api_key = st.text_input("DeepSeek API Key", type="password")
        anthropic_api_key = st.text_input("Anthropic API Key", type="password")

        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to know?"):
        if not deepseek_api_key or not anthropic_api_key:
            st.error("⚠️ Please enter both API keys in the sidebar.")
            return

        chain = ModelChain(deepseek_api_key, anthropic_api_key)

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                deepseek_output = chain.get_deepseek_reasoning(prompt)

            with st.spinner("✍️ Responding..."):
                response = chain.get_claude_response(prompt, deepseek_output)
                st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
