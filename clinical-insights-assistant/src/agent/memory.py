"""
Agent Memory Module
===================
Context and session memory management for the agentic AI loop.
Stores conversation history, analysis results, and reasoning traces.
"""

from typing import Any, Optional
from datetime import datetime
from collections import deque


class ConversationMemory:
    """
    Manages conversation history and short-term context for the agent.
    """

    def __init__(self, max_history: int = 50):
        self.history = deque(maxlen=max_history)
        self.created_at = datetime.now()

    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })

    def get_history(self, last_n: Optional[int] = None) -> list:
        """Get conversation history, optionally last N messages."""
        history = list(self.history)
        if last_n:
            return history[-last_n:]
        return history

    def get_context_string(self, last_n: int = 10) -> str:
        """Get formatted context string for prompt injection."""
        messages = self.get_history(last_n)
        return "\n".join([
            f"[{m['role']}]: {m['content']}" for m in messages
        ])

    def clear(self):
        """Clear conversation history."""
        self.history.clear()


class AnalysisMemory:
    """
    Stores results from analyses performed by the agent.
    Acts as a cache and knowledge base for multi-step reasoning.
    """

    def __init__(self):
        self.results = {}
        self.reasoning_trace = []

    def store_result(self, key: str, value: Any, metadata: Optional[dict] = None):
        """Store an analysis result with optional metadata."""
        self.results[key] = {
            'value': value,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }

    def get_result(self, key: str) -> Optional[Any]:
        """Retrieve a stored result."""
        entry = self.results.get(key)
        return entry['value'] if entry else None

    def has_result(self, key: str) -> bool:
        """Check if a result exists in memory."""
        return key in self.results

    def add_reasoning_step(self, thought: str, action: str, observation: str):
        """Record a step in the agent's reasoning chain."""
        self.reasoning_trace.append({
            'step': len(self.reasoning_trace) + 1,
            'thought': thought,
            'action': action,
            'observation': observation,
            'timestamp': datetime.now().isoformat()
        })

    def get_reasoning_trace(self) -> list:
        """Get the full reasoning trace."""
        return self.reasoning_trace

    def get_summary(self) -> dict:
        """Get a summary of what's stored in memory."""
        return {
            'num_results': len(self.results),
            'result_keys': list(self.results.keys()),
            'num_reasoning_steps': len(self.reasoning_trace),
            'last_step': self.reasoning_trace[-1] if self.reasoning_trace else None
        }

    def clear(self):
        """Clear all stored results and reasoning."""
        self.results.clear()
        self.reasoning_trace.clear()


class SessionMemory:
    """
    Top-level session memory combining conversation and analysis memory.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or datetime.now().strftime('%Y%m%d_%H%M%S')
        self.conversation = ConversationMemory()
        self.analysis = AnalysisMemory()
        self.metadata = {
            'created_at': datetime.now().isoformat(),
            'session_id': self.session_id
        }

    def get_full_context(self) -> dict:
        """Get the complete session context."""
        return {
            'session_id': self.session_id,
            'conversation_history': self.conversation.get_history(),
            'analysis_results': {
                k: v['value'] for k, v in self.analysis.results.items()
                if not isinstance(v['value'], object) or isinstance(v['value'], (str, int, float, dict, list))
            },
            'reasoning_trace': self.analysis.get_reasoning_trace()
        }

    def reset(self):
        """Reset the session."""
        self.conversation.clear()
        self.analysis.clear()
        self.metadata['reset_at'] = datetime.now().isoformat()
