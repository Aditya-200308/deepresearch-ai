# ============================================================
# FILE: src/agents/writer.py
# PURPOSE: Agent 2 — Senior Writer (Exhaustive Intelligence Author)
# ============================================================

from src.state import PipelineState
from src.llm_client import LLMClient


class WriterAgent:
    NAME = "Senior Writer"
    ICON = "✍️"

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def run(self, state: PipelineState) -> PipelineState:
        state.revision_count += 1
        state.status = "drafting"
        state.log(self.NAME, self.ICON, "Drafting Executive Intelligence", f"Synthesizing substantive analysis for Draft v{state.revision_count}...")

        system_prompt = """You are an Elite Intelligence Analyst and Technical Author. You provide razor-sharp, concrete, straight-to-the-point breakdowns of ANY subject. You NEVER write fluff, generic corporate padding, or vague meta-commentary. You immediately dive into the actual substance: core principles, granular mechanics, empirical data, narrative/structural elements, and real-world implications. You ALWAYS directly answer the user's question with concrete specifics."""

        user_prompt = f"""Write an authoritative, high-density, substantive intelligence report on:
TOPIC: "{state.topic}"

GROUND-TRUTH RESEARCH DOSSIER:
{state.research_dossier}

STRUCTURE REQUIRED:
# In-Depth Analysis: {state.topic}

## 1. Overview & Core Foundation
- Direct context: Core creators/engineers/entities involved, primary thesis, foundational principles, and significance.

## 2. In-Depth Breakdown & Core Mechanics
- The actual substance of the subject matter:
  * If Technology / Science: Architecture, technical specifications, material physics, algorithms, and empirical metrics.
  * If Politics / Current Events: Systemic causes, protest dynamics, institutional investigations, ministerial impact, and ground mobilization.
  * If Cinema / Media / Comics: Narrative progression, character psychology, ideological conflicts, practical craftsmanship, and major revelations.
  * If Finance / Business: Economic mechanisms, structural models, quantitative findings, and operational dynamics.
  * If LIST-type query (e.g. "top 10", "best 5", "ranking"): PROVIDE THE ACTUAL NUMBERED LIST with specific names, dates, figures, and data points.

## 3. Practical Execution & Technical Rigor
- Concrete implementation: How it performs under real-world conditions, tactical execution, and strategic response.

## 4. Key Strengths, Trade-Offs & Critical Considerations
- Objective assessment: Clear breakdown of major breakthroughs/advantages versus technical bottlenecks, risks, or limitations.

## 5. Strategic Evaluation & Verdict
- **Core Architecture & Premise**: [Concrete finding & status rating e.g. High / 9/10]
- **Technical & Narrative Rigor**: [Concrete finding & status rating e.g. Strong / 8.5/10]
- **Scalability & Cultural Impact**: [Concrete finding & status rating e.g. Exceptional / 9.5/10]
- **Final Consensus & Trajectory**: [Definitive takeaway and lasting significance]

CRITICAL RULES:
- COME STRAIGHT TO THE POINT. Zero fluff, zero generic corporate padding.
- If the user asks for a LIST, RANKING, or COMPARISON, you MUST provide the actual numbered items with specific names and figures.
- COMPLETE every single section fully. Never cut off or stop midway."""

        draft = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.15,
            max_tokens=8192
        )
        state.draft = draft

        state.log(
            self.NAME,
            self.ICON,
            f"Draft Completed (v{state.revision_count})",
            f"Synthesized comprehensive intelligence brief ({len(draft.split())} words)."
        )
        return state
