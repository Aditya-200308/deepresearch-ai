# ============================================================
# FILE: src/state.py
# PURPOSE: Shared State & Memory Contract for the Multi-Agent System
#
# HOW IT WORKS:
#   In multi-agent systems, agents pass information through a
#   "shared state" (like a shared project notebook).
#   Each agent reads from the state, performs its task, and
#   writes its results back into the state for the next agent.
# ============================================================

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time


@dataclass
class AgentLog:
    """Represents a single event or message produced by an agent."""
    timestamp: float = field(default_factory=time.time)
    agent_name: str = ""
    agent_icon: str = "🤖"
    action: str = ""
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "agent_name": self.agent_name,
            "agent_icon": self.agent_icon,
            "action": self.action,
            "details": self.details
        }


@dataclass
class PipelineState:
    """
    The shared state passed between all 4 agents during execution:
    Researcher ➔ Writer ➔ Critic ➔ (Self-Correction Loop) ➔ Fact-Checker
    """
    # User Input
    topic: str = ""
    max_revisions: int = 2

    # Agent Outputs
    research_dossier: str = ""
    search_queries_used: List[str] = field(default_factory=list)
    sources: List[Dict[str, str]] = field(default_factory=list)

    draft: str = ""
    critique: str = ""
    critique_score: int = 0
    critique_history: List[Dict[str, Any]] = field(default_factory=list)
    revision_count: int = 0

    fact_check_passed: bool = False
    fact_check_report: str = ""

    final_report: str = ""

    # Execution Metadata & Logs
    status: str = "idle"  # idle | researching | drafting | critiquing | revising | fact_checking | completed | error
    error_message: Optional[str] = None
    logs: List[Dict[str, Any]] = field(default_factory=list)

    def log(self, agent_name: str, agent_icon: str, action: str, details: str = ""):
        """Adds a structured log event to the pipeline history."""
        entry = AgentLog(
            timestamp=time.time(),
            agent_name=agent_name,
            agent_icon=agent_icon,
            action=action,
            details=details
        )
        self.logs.append(entry.to_dict())
