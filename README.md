# 🤖 DeepResearch AI — Autonomous Multi-Agent Research & Fact-Verification System

> **Portfolio Project #02** | An autonomous 4-agent collaborative intelligence pipeline engineered with CrewAI, adversarial reflection, dynamic rubric scoring, and anti-hallucination verification powered by Google Gemini 3.8 Flash.

[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CrewAI](https://img.shields.io/badge/Orchestration-CrewAI_Agents-FF6B6B?style=for-the-badge&logo=crewai&logoColor=white)](https://crewai.com)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.8_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)

---

## 🌟 Architecture Overview

DeepResearch AI features a **CrewAI collaborative multi-agent architecture**:
1. **CrewAI Multi-Agent Pipeline**: Autonomous collaborative agents with specialized role-playing, custom tools, and sequential reflection loops.
2. **Ground-Truth Fact Verification**: Rigorous cross-examination of drafted claims against primary web and encyclopedic evidence dossiers to eliminate hallucinations.

```
[User Query] ➔ [1. Lead Researcher] (Google News + Wikipedia Index)
                        │
                        ▼
                 [2. Senior Writer] (Draft v1 Synthesis)
                        │
                        ▼
                 [3. Editorial Critic] ◄──────────────┐ (Self-Correction Loop: Score < 85)
                        │                             │
                        ├─────────────────────────────┘
                        ▼ (Score ≥ 85)
                 [4. Fact-Checker] (Anti-Hallucination Audit)
                        │
                        ▼
                 [Verified Report + Live Citations]
```

### 👥 The 4 Specialized Agents
1. **🔍 Lead Researcher**: Formulates multi-angle search vectors and extracts verified live web evidence.
2. **✍️ Senior Writer**: Synthesizes high-density executive intelligence reports structured for C-suite readability.
3. **🧐 Editorial Critic**: Audits drafts against a 4-dimension rubric (Depth, Structure, Evidence, Strategy) and enforces self-correction.
4. **🛡️ Fact Auditor**: Validates every claim against the ground-truth research dossier to prevent hallucinations.

---

## ⚡ Key Features
* **CrewAI Multi-Agent Coordination**: Autonomous orchestration across 4 specialized agent personas with shared memory.
* **Title-Strict Relevance Filtering**: Discards spam, mismatched domains, and off-topic sources automatically.
* **Adversarial Self-Correction**: Configurable critique loops (1–3 iterations) to balance speed and exhaustive depth.
* **High-Density Typography**: Generous line-height, clear paragraph margins, and executive summaries.
* **Instant Clipboard Export**: 1-click full report copying.

---

## 🚀 Quickstart (Local Setup)

### 1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/deepresearch-ai.git
cd deepresearch-ai
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure environment:
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Launch the dashboard:
```bash
streamlit run src/app.py
```

---

## 🌐 Deploy to Streamlit Community Cloud (Free)

1. Fork or push this repository to your GitHub account.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and click **New App**.
3. Select your repository, branch (`main`), and set the main file path to:
   ```text
   src/app.py
   ```
4. Under **Advanced Settings ➔ Secrets**, add your Gemini API Key:
   ```toml
   GEMINI_API_KEY = "your_key_here"
   ```
5. Click **Deploy!** 🚀
