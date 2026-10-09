# ============================================================
# FILE: src/orchestrator.py
# PURPOSE: Autonomous Multi-Agent Intelligence Pipeline Orchestrator
# ============================================================

import time
import re
from typing import Callable, Optional
try:
    from src.state import PipelineState
    from src.llm_client import LLMClient
    from src.agents.researcher import ResearcherAgent
    from src.agents.writer import WriterAgent
    from src.agents.critic import CriticAgent
    from src.agents.fact_checker import FactCheckerAgent
    from src.crewai_pipeline import CrewAIPipeline
except ImportError:
    from state import PipelineState
    from llm_client import LLMClient
    from agents.researcher import ResearcherAgent
    from agents.writer import WriterAgent
    from agents.critic import CriticAgent
    from agents.fact_checker import FactCheckerAgent
    from crewai_pipeline import CrewAIPipeline


class MultiAgentOrchestrator:
    """
    Coordinates the 4-agent collaborative intelligence lifecycle:
    Lead Researcher ➔ Senior Writer ➔ Editorial Critic ➔ Fact-Checking Auditor
    """

    def __init__(self, api_key: Optional[str] = None, engine_mode: str = "gemini_flash", framework: str = "crewai"):
        self.api_key = api_key
        self.engine_mode = "gemini_flash"
        self.framework = framework.lower()
        self.llm = LLMClient(api_key=api_key)
        self.researcher = ResearcherAgent(self.llm)
        self.writer = WriterAgent(self.llm)
        self.critic = CriticAgent(self.llm)
        self.fact_checker = FactCheckerAgent(self.llm)

    def run_pipeline(
        self,
        topic: str,
        max_revisions: int = 2,
        on_step_callback: Optional[Callable[[PipelineState], None]] = None
    ) -> PipelineState:
        """
        Executes the complete 4-agent autonomous pipeline powered by Google Gemini Flash.
        """
        state = PipelineState(topic=topic.strip(), max_revisions=max_revisions)
        state.log("System Controller", "🤖", "Mission Initialized", f"Deploying 4-agent collaborative team for: '{topic}'")

        if on_step_callback:
            on_step_callback(state)

        try:
            # 1. RESEARCH PHASE (Web & Wikipedia Grounding)
            state = self.researcher.run(state)
            if on_step_callback:
                on_step_callback(state)

            # 2. WRITING PHASE (Substantive Memo Generation via Gemini Flash)
            state.status = "drafting"
            state.log(self.writer.NAME, self.writer.ICON, "Drafting Executive Briefing", f"Synthesizing substantive intelligence brief for '{topic}'...")
            if on_step_callback:
                on_step_callback(state)

            state = self.writer.run(state)
            if on_step_callback:
                on_step_callback(state)

            # 3. EDITORIAL CRITIQUE & 4-DIMENSION RUBRIC EVALUATION
            state.status = "critiquing"
            state.log(self.critic.NAME, self.critic.ICON, "Rubric Scoring & Reflection", "Auditing draft across 4 editorial dimensions...")
            if on_step_callback:
                on_step_callback(state)

            state = self.critic.run(state)
            if on_step_callback:
                on_step_callback(state)

            # 4. FACT-CHECKING & ANTI-HALLUCINATION AUDIT
            state.status = "fact_checking"
            state.log(self.fact_checker.NAME, self.fact_checker.ICON, "Fact-Check Audit Initiated", "Scanning draft against research evidence...")
            if on_step_callback:
                on_step_callback(state)

            state = self.fact_checker.run(state)
            if on_step_callback:
                on_step_callback(state)

            state.log("System Controller", "🚀", "Mission Complete", "Verified executive intelligence memo published!")
            if on_step_callback:
                on_step_callback(state)

        except Exception as e:
            state.status = "error"
            state.error_message = str(e)
            state.log("System Controller", "❌", "Execution Error", str(e))
            if on_step_callback:
                on_step_callback(state)

        return state
