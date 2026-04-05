import pytest
import pandas as pd
import numpy as np
from src.agent.memory import SessionMemory, ConversationMemory, AnalysisMemory
from src.agent.agent_core import ClinicalInsightsAgent


@pytest.fixture
def sample_data():
    """Create sample clinical trial data for testing."""
    data = {
        'patient_id': [f'P{i:03d}' for i in range(1, 11)],
        'trial_day': [5] * 10,
        'dosage_mg': [50, 50, 75, 75, 100, 100, 50, 75, 100, 50],
        'compliance_pct': [95.0, 75.0, 88.0, 65.0, 92.0, 70.0, 90.0, 80.0, 85.0, 78.0],
        'adverse_event_flag': [0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
        'doctor_notes': ['OK', 'Issue', 'OK', 'Issue', 'OK', 'Issue', 'OK', 'OK', 'Issue', 'OK'],
        'outcome_score': [85.0, 65.0, 80.0, 60.0, 88.0, 70.0, 83.0, 78.0, 68.0, 81.0],
        'cohort': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
        'visit_date': pd.to_datetime(['2024-01-05'] * 10)
    }
    return pd.DataFrame(data)


class TestConversationMemory:
    """Tests for ConversationMemory class."""

    def test_conversation_memory_initialization(self):
        """Test ConversationMemory initialization."""
        memory = ConversationMemory()

        assert isinstance(memory, ConversationMemory)
        assert hasattr(memory, 'history')
        assert len(memory.history) == 0

    def test_conversation_memory_add_message(self):
        """Test adding a message to conversation memory."""
        memory = ConversationMemory()
        memory.add_message('user', 'What is the patient count?')

        assert len(memory.history) == 1
        assert memory.history[0]['role'] == 'user'

    def test_conversation_memory_get_history(self):
        """Test retrieving conversation history."""
        memory = ConversationMemory()
        memory.add_message('user', 'Question 1')
        memory.add_message('agent', 'Answer 1')
        memory.add_message('user', 'Question 2')

        history = memory.get_history()

        assert len(history) == 3
        assert history[0]['content'] == 'Question 1'

    def test_conversation_memory_get_last_n_messages(self):
        """Test retrieving last N messages."""
        memory = ConversationMemory()
        memory.add_message('user', 'Q1')
        memory.add_message('agent', 'A1')
        memory.add_message('user', 'Q2')

        last_two = memory.get_history(last_n=2)

        assert len(last_two) == 2
        assert last_two[0]['content'] == 'A1'

    def test_conversation_memory_get_context_string(self):
        """Test getting formatted context string."""
        memory = ConversationMemory()
        memory.add_message('user', 'Hello')
        memory.add_message('agent', 'Hi there')

        context = memory.get_context_string()

        assert 'user' in context
        assert 'agent' in context
        assert 'Hello' in context

    def test_conversation_memory_clear(self):
        """Test clearing conversation history."""
        memory = ConversationMemory()
        memory.add_message('user', 'Message 1')
        memory.add_message('agent', 'Message 2')

        assert len(memory.history) > 0

        memory.clear()

        assert len(memory.history) == 0


class TestAnalysisMemory:
    """Tests for AnalysisMemory class."""

    def test_analysis_memory_initialization(self):
        """Test AnalysisMemory initialization."""
        memory = AnalysisMemory()

        assert isinstance(memory, AnalysisMemory)
        assert len(memory.results) == 0

    def test_analysis_memory_store_result(self):
        """Test storing an analysis result."""
        memory = AnalysisMemory()
        result_data = {'count': 5, 'mean': 75.0}

        memory.store_result('issue_detection', result_data)

        assert memory.has_result('issue_detection')

    def test_analysis_memory_get_result(self):
        """Test retrieving a stored result."""
        memory = AnalysisMemory()
        result_data = {'adverse_events': 3, 'non_compliance': 2}

        memory.store_result('detection_results', result_data)
        retrieved = memory.get_result('detection_results')

        assert retrieved == result_data

    def test_analysis_memory_has_result(self):
        """Test checking if result exists."""
        memory = AnalysisMemory()
        memory.store_result('test_key', {'data': 'value'})

        assert memory.has_result('test_key')
        assert not memory.has_result('nonexistent_key')

    def test_analysis_memory_add_reasoning_step(self):
        """Test adding a reasoning step."""
        memory = AnalysisMemory()
        memory.add_reasoning_step(
            thought='Start with issue detection',
            action='detect_issues',
            observation='Found 5 issues'
        )

        trace = memory.get_reasoning_trace()

        assert len(trace) == 1
        assert trace[0]['step'] == 1
        assert 'issue' in trace[0]['action'].lower()

    def test_analysis_memory_get_summary(self):
        """Test getting summary of memory contents."""
        memory = AnalysisMemory()
        memory.store_result('result1', {'key': 'value1'})
        memory.store_result('result2', {'key': 'value2'})
        memory.add_reasoning_step('T1', 'A1', 'O1')

        summary = memory.get_summary()

        assert summary['num_results'] == 2
        assert summary['num_reasoning_steps'] == 1

    def test_analysis_memory_clear(self):
        """Test clearing analysis memory."""
        memory = AnalysisMemory()
        memory.store_result('key', 'value')
        memory.add_reasoning_step('T', 'A', 'O')

        assert len(memory.results) > 0

        memory.clear()

        assert len(memory.results) == 0
        assert len(memory.reasoning_trace) == 0


class TestSessionMemory:
    """Tests for SessionMemory class."""

    def test_session_memory_initialization(self):
        """Test SessionMemory initialization."""
        memory = SessionMemory()

        assert isinstance(memory, SessionMemory)
        assert hasattr(memory, 'session_id')
        assert hasattr(memory, 'conversation')
        assert hasattr(memory, 'analysis')

    def test_session_memory_has_conversation(self):
        """Test that session has conversation memory."""
        memory = SessionMemory()

        assert isinstance(memory.conversation, ConversationMemory)

    def test_session_memory_has_analysis(self):
        """Test that session has analysis memory."""
        memory = SessionMemory()

        assert isinstance(memory.analysis, AnalysisMemory)

    def test_session_memory_custom_session_id(self):
        """Test creating session with custom ID."""
        custom_id = 'test_session_123'
        memory = SessionMemory(session_id=custom_id)

        assert memory.session_id == custom_id

    def test_session_memory_get_full_context(self):
        """Test getting full session context."""
        memory = SessionMemory()
        memory.conversation.add_message('user', 'Test question')
        memory.analysis.store_result('test_result', {'data': 'value'})

        context = memory.get_full_context()

        assert 'session_id' in context
        assert 'conversation_history' in context
        assert 'analysis_results' in context

    def test_session_memory_reset(self):
        """Test resetting a session."""
        memory = SessionMemory()
        memory.conversation.add_message('user', 'Message')
        memory.analysis.store_result('key', 'value')

        memory.reset()

        assert len(memory.conversation.history) == 0
        assert len(memory.analysis.results) == 0


class TestClinicalInsightsAgent:
    """Tests for ClinicalInsightsAgent class."""

    def test_agent_initialization(self, sample_data):
        """Test ClinicalInsightsAgent initialization."""
        agent = ClinicalInsightsAgent(sample_data)

        assert isinstance(agent, ClinicalInsightsAgent)
        assert hasattr(agent, 'memory')
        assert hasattr(agent, 'df')

    def test_agent_has_memory(self, sample_data):
        """Test that agent has session memory."""
        agent = ClinicalInsightsAgent(sample_data)

        assert isinstance(agent.memory, SessionMemory)

    def test_agent_has_available_tools(self, sample_data):
        """Test that agent has available tools defined."""
        agent = ClinicalInsightsAgent(sample_data)

        assert hasattr(agent, 'AVAILABLE_TOOLS')
        assert 'detect_issues' in agent.AVAILABLE_TOOLS
        assert 'compare_cohorts' in agent.AVAILABLE_TOOLS

    def test_agent_verbose_mode(self, sample_data):
        """Test agent with verbose mode."""
        agent_verbose = ClinicalInsightsAgent(sample_data, verbose=True)
        agent_quiet = ClinicalInsightsAgent(sample_data, verbose=False)

        assert agent_verbose.verbose is True
        assert agent_quiet.verbose is False

    def test_agent_run_analysis(self, sample_data):
        """Test agent running analysis."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        result = agent.run()

        assert isinstance(result, dict)
        assert 'session_id' in result
        assert 'results' in result

    def test_agent_run_returns_session_id(self, sample_data):
        """Test that run returns session ID."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        result = agent.run()

        assert result['session_id'] == agent.memory.session_id

    def test_agent_ask_method_exists(self, sample_data):
        """Test that agent has ask method."""
        agent = ClinicalInsightsAgent(sample_data)

        assert hasattr(agent, 'ask')
        assert callable(agent.ask)

    def test_agent_ask_returns_string(self, sample_data):
        """Test that ask method returns a string."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        response = agent.ask('What is the compliance status?')

        assert isinstance(response, str)

    def test_agent_ask_updates_memory(self, sample_data):
        """Test that ask updates conversation memory."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        initial_len = len(agent.memory.conversation.history)

        agent.ask('Test question')

        # Should have added at least user and agent messages
        assert len(agent.memory.conversation.history) > initial_len

    def test_agent_ask_patient_query(self, sample_data):
        """Test agent with patient-specific query."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        response = agent.ask('Tell me about patient P001')

        assert isinstance(response, str)

    def test_agent_ask_adverse_event_query(self, sample_data):
        """Test agent with adverse event query."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        response = agent.ask('What adverse events have been reported?')

        assert isinstance(response, str)
        assert len(response) > 0

    def test_agent_ask_cohort_query(self, sample_data):
        """Test agent with cohort comparison query."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        response = agent.ask('Compare cohorts A and B')

        assert isinstance(response, str)

    def test_agent_ask_dosage_query(self, sample_data):
        """Test agent with dosage-related query."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        response = agent.ask('What dosage analysis do you recommend?')

        assert isinstance(response, str)

    def test_agent_run_multiple_steps(self, sample_data):
        """Test agent running multiple analysis steps."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        result = agent.run('Perform comprehensive analysis')

        assert 'reasoning_trace' in result
        assert len(result['reasoning_trace']) > 0

    def test_agent_memory_persistence(self, sample_data):
        """Test that memory persists across multiple queries."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)

        agent.ask('How many patients are there?')
        agent.ask('What is the compliance rate?')

        history = agent.memory.conversation.get_history()

        assert len(history) >= 4  # At least 2 user and 2 agent messages

    def test_agent_with_different_data_sizes(self):
        """Test agent with different dataset sizes."""
        # Small dataset
        small_df = pd.DataFrame({
            'patient_id': ['P001', 'P002'],
            'trial_day': [5, 5],
            'dosage_mg': [50, 75],
            'compliance_pct': [95.0, 80.0],
            'adverse_event_flag': [0, 1],
            'doctor_notes': ['OK', 'Issue'],
            'outcome_score': [85.0, 70.0],
            'cohort': ['A', 'B'],
            'visit_date': pd.to_datetime(['2024-01-05', '2024-01-05'])
        })

        agent = ClinicalInsightsAgent(small_df, verbose=False)
        result = agent.run()

        assert isinstance(result, dict)

    def test_agent_handles_questions_without_data(self, sample_data):
        """Test agent handling general questions."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        response = agent.ask('What is machine learning?')

        # Agent should attempt to answer even if question is generic
        assert isinstance(response, str)

    def test_agent_max_steps_respected(self, sample_data):
        """Test that agent respects max steps limit."""
        agent = ClinicalInsightsAgent(sample_data, verbose=False)
        agent.max_steps = 3

        result = agent.run()

        # Reasoning trace should not exceed max steps
        assert len(result['reasoning_trace']) <= 3
