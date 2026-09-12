# ============================================================
# FILE: src/agents/researcher.py
# PURPOSE: Agent 1 — Lead Researcher (Universal Granular Intelligence Scourer)
# ============================================================

from typing import List, Dict, Any
from src.state import PipelineState
from src.llm_client import LLMClient
from src.tools import parallel_search_web, format_search_dossier


class ResearcherAgent:
    NAME = "Lead Researcher"
    ICON = "🔍"

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def run(self, state: PipelineState) -> PipelineState:
        state.status = "researching"
        state.log(self.NAME, self.ICON, "Intelligence Mining", f"Formulating deep substance search vectors for: '{state.topic}'")

        topic_lower = state.topic.lower()
        is_media = any(w in topic_lower for w in ["movie", "film", "game", "book", "character", "batman", "spiderman", "spider-man", "actor", "director", "synopsis", "review"])

        if is_media:
            queries = [
                state.topic,
                f"{state.topic} story background breakdown",
                f"{state.topic} origin history key events",
                f"{state.topic} latest news developments"
            ]
        else:
            queries = [
                state.topic,
                f"{state.topic} overview key developments",
                f"{state.topic} technical analysis mechanisms",
                f"{state.topic} latest news report"
            ]

        state.search_queries_used = queries

        # Execute parallel search across Google News, Wikipedia & verified indexes
        results = parallel_search_web(queries, max_results_per_query=4)
        state.sources = results
        state.log(self.NAME, self.ICON, "Sources Captured & Scraped", f"Gathered {len(results)} verified intelligence sources.")

        # Compile Ground-Truth Research Dossier
        dossier = format_search_dossier(results)
        state.research_dossier = dossier
        state.log(self.NAME, self.ICON, "Dossier Finalized", f"Compiled research dossier ({len(dossier)} characters, {len(results)} live links).")
        return state
