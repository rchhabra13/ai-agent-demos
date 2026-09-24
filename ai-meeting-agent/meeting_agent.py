"""
AI Meeting Preparation Agent using CrewAI.

This module implements a multi-agent system powered by CrewAI and Claude
for comprehensive meeting preparation. It provides analysis, research,
strategy development, and executive briefings.
"""

import logging
import os
from typing import Optional

import streamlit as st
from anthropic import Anthropic
from crewai import Agent, Crew, Task
from crewai.process import Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def initialize_page_config() -> None:
    """Initialize Streamlit page configuration."""
    st.set_page_config(
        page_title="AI Meeting Agent 📝",
        layout="wide"
    )
    st.title("AI Meeting Preparation Agent 📝")


def get_api_keys_from_sidebar() -> tuple[Optional[str], Optional[str]]:
    """
    Retrieve API keys from Streamlit sidebar.

    Returns:
        tuple: (anthropic_api_key, serper_api_key)
    """
    with st.sidebar:
        st.header("API Keys")
        anthropic_api_key = st.text_input("Anthropic API Key", type="password")
        serper_api_key = st.text_input("Serper API Key", type="password")

    return anthropic_api_key, serper_api_key


def create_agents(
    api_key: str
) -> tuple[Agent, Agent, Agent, Agent]:
    """
    Create all meeting preparation agents.

    Args:
        api_key: Anthropic API key

    Returns:
        tuple: (context_analyzer, industry_insights_generator,
                strategy_formulator, executive_briefing_creator)
    """
    from crewai import LLM

    claude = LLM(
        model="claude-3-5-sonnet-20240620",
        temperature=0.7,
        api_key=api_key
    )
    search_tool = SerperDevTool()

    context_analyzer = Agent(
        role="Meeting Context Specialist",
        goal="Analyze and summarize key background information for the meeting",
        backstory=(
            "You are an expert at quickly understanding complex business contexts "
            "and identifying critical information."
        ),
        verbose=True,
        allow_delegation=False,
        llm=claude,
        tools=[search_tool]
    )

    industry_insights_generator = Agent(
        role="Industry Expert",
        goal="Provide in-depth industry analysis and identify key trends",
        backstory=(
            "You are a seasoned industry analyst with a knack for spotting "
            "emerging trends and opportunities."
        ),
        verbose=True,
        allow_delegation=False,
        llm=claude,
        tools=[search_tool]
    )

    strategy_formulator = Agent(
        role="Meeting Strategist",
        goal="Develop a tailored meeting strategy and detailed agenda",
        backstory=(
            "You are a master meeting planner, known for creating highly "
            "effective strategies and agendas."
        ),
        verbose=True,
        allow_delegation=False,
        llm=claude
    )

    executive_briefing_creator = Agent(
        role="Communication Specialist",
        goal="Synthesize information into concise and impactful briefings",
        backstory=(
            "You are an expert communicator, skilled at distilling complex "
            "information into clear, actionable insights."
        ),
        verbose=True,
        allow_delegation=False,
        llm=claude
    )

    return (context_analyzer, industry_insights_generator,
            strategy_formulator, executive_briefing_creator)


def create_tasks(
    agents: tuple[Agent, Agent, Agent, Agent],
    company_name: str,
    meeting_objective: str,
    attendees: str,
    meeting_duration: int,
    focus_areas: str
) -> tuple[Task, Task, Task, Task]:
    """
    Create all meeting preparation tasks.

    Args:
        agents: Tuple of created agents
        company_name: Name of the company
        meeting_objective: The objective of the meeting
        attendees: List of attendees and their roles
        meeting_duration: Duration of the meeting in minutes
        focus_areas: Specific areas of focus or concerns

    Returns:
        tuple: (context_analysis_task, industry_analysis_task,
                strategy_development_task, executive_brief_task)
    """
    context_analyzer, industry_insights_generator, strategy_formulator, \
        executive_briefing_creator = agents

    context_analysis_task = Task(
        description=(
            f"Analyze the context for the meeting with {company_name}, considering:\n"
            f"1. The meeting objective: {meeting_objective}\n"
            f"2. The attendees: {attendees}\n"
            f"3. The meeting duration: {meeting_duration} minutes\n"
            f"4. Specific focus areas or concerns: {focus_areas}\n\n"
            f"Research {company_name} thoroughly, including:\n"
            f"1. Recent news and press releases\n"
            f"2. Key products or services\n"
            f"3. Major competitors\n\n"
            f"Provide a comprehensive summary of your findings, highlighting the most "
            f"relevant information for the meeting context.\n"
            f"Format your output using markdown with appropriate headings and subheadings."
        ),
        agent=context_analyzer,
        expected_output=(
            "A detailed analysis of the meeting context and company background, "
            "including recent developments, financial performance, and relevance "
            "to the meeting objective, formatted in markdown."
        )
    )

    industry_analysis_task = Task(
        description=(
            f"Based on the context analysis for {company_name} and the meeting "
            f"objective: {meeting_objective}, provide an in-depth industry analysis:\n"
            f"1. Identify key trends and developments in the industry\n"
            f"2. Analyze the competitive landscape\n"
            f"3. Highlight potential opportunities and threats\n"
            f"4. Provide insights on market positioning\n\n"
            f"Ensure the analysis is relevant to the meeting objective and attendees' roles.\n"
            f"Format your output using markdown with appropriate headings and subheadings."
        ),
        agent=industry_insights_generator,
        expected_output=(
            "A comprehensive industry analysis report, including trends, "
            "competitive landscape, opportunities, threats, and relevant insights "
            "for the meeting objective, formatted in markdown."
        )
    )

    strategy_development_task = Task(
        description=(
            f"Using the context analysis and industry insights, develop a tailored "
            f"meeting strategy and detailed agenda for the {meeting_duration}-minute "
            f"meeting with {company_name}. Include:\n"
            f"1. A time-boxed agenda with clear objectives for each section\n"
            f"2. Key talking points for each agenda item\n"
            f"3. Suggested speakers or leaders for each section\n"
            f"4. Potential discussion topics and questions to drive the conversation\n"
            f"5. Strategies to address the specific focus areas and concerns: {focus_areas}\n\n"
            f"Ensure the strategy and agenda align with the meeting objective: "
            f"{meeting_objective}\n"
            f"Format your output using markdown with appropriate headings and subheadings."
        ),
        agent=strategy_formulator,
        expected_output=(
            "A detailed meeting strategy and time-boxed agenda, including objectives, "
            "key talking points, and strategies to address specific focus areas, "
            "formatted in markdown."
        )
    )

    executive_brief_task = Task(
        description=(
            f"Synthesize all the gathered information into a comprehensive yet concise "
            f"executive brief for the meeting with {company_name}. Create the following "
            f"components:\n\n"
            f"1. A detailed one-page executive summary including:\n"
            f"   - Clear statement of the meeting objective\n"
            f"   - List of key attendees and their roles\n"
            f"   - Critical background points about {company_name} and relevant "
            f"     industry context\n"
            f"   - Top 3-5 strategic goals for the meeting, aligned with the objective\n"
            f"   - Brief overview of the meeting structure and key topics to be covered\n\n"
            f"2. An in-depth list of key talking points, each supported by:\n"
            f"   - Relevant data or statistics\n"
            f"   - Specific examples or case studies\n"
            f"   - Connection to the company's current situation or challenges\n\n"
            f"3. Anticipate and prepare for potential questions:\n"
            f"   - List likely questions from attendees based on their roles and "
            f"     the meeting objective\n"
            f"   - Craft thoughtful, data-driven responses to each question\n"
            f"   - Include any supporting information or additional context needed\n\n"
            f"4. Strategic recommendations and next steps:\n"
            f"   - Provide 3-5 actionable recommendations based on the analysis\n"
            f"   - Outline clear next steps for implementation or follow-up\n"
            f"   - Suggest timelines or deadlines for key actions\n"
            f"   - Identify potential challenges or roadblocks and propose mitigations\n\n"
            f"Ensure the brief is comprehensive yet concise, highly actionable, and "
            f"precisely aligned with the meeting objective: {meeting_objective}.\n"
            f"Format your output using markdown with appropriate headings and subheadings."
        ),
        agent=executive_briefing_creator,
        expected_output=(
            "A comprehensive executive brief including summary, key talking points, "
            "Q&A preparation, and strategic recommendations, formatted in markdown "
            "with main headings (H1), section headings (H2), and subsection headings "
            "(H3) where appropriate."
        )
    )

    return (context_analysis_task, industry_analysis_task,
            strategy_development_task, executive_brief_task)


def get_meeting_inputs() -> dict[str, str | int]:
    """
    Get meeting details from user input.

    Returns:
        dict: Meeting details
    """
    st.subheader("Meeting Details")

    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Enter the company name:")
        meeting_objective = st.text_input("Enter the meeting objective:")

    with col2:
        meeting_duration = st.number_input(
            "Enter the meeting duration (in minutes):",
            min_value=15,
            max_value=180,
            value=60,
            step=15
        )

    attendees = st.text_area(
        "Enter the attendees and their roles (one per line):"
    )
    focus_areas = st.text_input(
        "Enter any specific areas of focus or concerns:"
    )

    return {
        "company_name": company_name,
        "meeting_objective": meeting_objective,
        "attendees": attendees,
        "meeting_duration": meeting_duration,
        "focus_areas": focus_areas
    }


def display_usage_instructions() -> None:
    """Display usage instructions in sidebar."""
    with st.sidebar:
        st.markdown("""
        ## How to use this app:
        1. Enter your API keys above.
        2. Provide the requested information about the meeting.
        3. Click 'Prepare Meeting' to generate your comprehensive meeting preparation.

        The AI agents will work together to:
        - Analyze the meeting context and company background
        - Provide industry insights and trends
        - Develop a tailored meeting strategy and agenda
        - Create an executive brief with key talking points

        This process may take a few minutes. Please be patient!
        """)


def main() -> None:
    """Main application entry point."""
    initialize_page_config()

    anthropic_api_key, serper_api_key = get_api_keys_from_sidebar()

    if not (anthropic_api_key and serper_api_key):
        st.warning("Please enter all API keys in the sidebar before proceeding.")
        return

    # Set environment variables
    os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
    os.environ["SERPER_API_KEY"] = serper_api_key

    meeting_inputs = get_meeting_inputs()

    if st.button("Prepare Meeting"):
        if not all([
            meeting_inputs["company_name"],
            meeting_inputs["meeting_objective"],
            meeting_inputs["attendees"]
        ]):
            st.error("Please fill in all required fields.")
            return

        logger.info(f"Preparing meeting for {meeting_inputs['company_name']}")

        with st.spinner("AI agents are preparing your meeting..."):
            try:
                agents = create_agents(anthropic_api_key)
                tasks = create_tasks(
                    agents,
                    meeting_inputs["company_name"],
                    meeting_inputs["meeting_objective"],
                    meeting_inputs["attendees"],
                    meeting_inputs["meeting_duration"],
                    meeting_inputs["focus_areas"]
                )

                crew = Crew(
                    agents=list(agents),
                    tasks=list(tasks),
                    verbose=True,
                    process=Process.sequential
                )

                result = crew.kickoff()
                st.markdown(result)
                logger.info("Meeting preparation completed successfully")

            except Exception as e:
                logger.error(f"Error during meeting preparation: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

    display_usage_instructions()


if __name__ == "__main__":
    main()
