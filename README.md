# Multilingual Welfare Scheme Assistant

<p align="center">
<img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge" />
  <img alt="LangChain" src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge" />
  <img alt="ChromaDB" src="https://img.shields.io/badge/ChromaDB-5B3FD6?style=for-the-badge" />
  <img alt="Twilio" src="https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge" />
  <img alt="NLP" src="https://img.shields.io/badge/NLP-4B5563?style=for-the-badge" />
</p>

<p align="center">
  <strong>A low-bandwidth multilingual assistant that helps users discover government welfare schemes through conversational channels.</strong>
</p>

This project focuses on accessibility: users should be able to ask simple questions in familiar languages and receive grounded guidance about relevant welfare schemes. It combines retrieval, translation, speech handling, and messaging integration for practical public-service discovery.

## Core Capabilities

- Supports multilingual conversational access to welfare scheme information.
- Uses retrieval workflows to ground responses in indexed scheme data.
- Includes audio handling and translation support for low-bandwidth contexts.
- Integrates messaging workflows suitable for WhatsApp or SMS deployment.

## Technical Architecture

The FastAPI app is organized around chatbot logic, audio handling, database population, and API routing. Retrieval dependencies support a vector-backed knowledge base, while translation and messaging integrations widen access channels.

## Architecture Diagram

```mermaid
%%{init: {"flowchart": {"nodeSpacing": 55, "rankSpacing": 70, "curve": "basis"}, "themeVariables": {"fontSize": "16px", "fontFamily": "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"}}}%%
flowchart TD
  User["Citizen via Text or<br/>Voice"] --> Channel["WhatsApp or SMS Channel"]
  Channel --> API["FastAPI Application"]
  API --> Language["Language Detection and<br/>Translation"]
  API --> Audio["Audio Handling"]
  Language --> Retrieval["LangChain Retrieval Workflow"]
  Retrieval --> VectorDB["ChromaDB Scheme Index"]
  VectorDB --> Response["Grounded Scheme Guidance"]
  Response --> Channel

  classDef inputs fill:#FEF3C7,stroke:#D97706,color:#78350F,stroke-width:2.5px;
  classDef process fill:#DBEAFE,stroke:#2563EB,color:#1E3A8A,stroke-width:2.5px;
  classDef data fill:#DCFCE7,stroke:#16A34A,color:#14532D,stroke-width:2.5px;
  classDef agent fill:#F3E8FF,stroke:#9333EA,color:#581C87,stroke-width:2.5px;
  classDef output fill:#FFE4E6,stroke:#E11D48,color:#881337,stroke-width:2.5px;
  class User inputs;
  class Channel,API,Language,Audio,Retrieval process;
  class VectorDB data;
  class Response output;
  linkStyle default stroke:#64748B,stroke-width:2.5px;
```

## Technology Stack

- FastAPI backend with LangChain orchestration.
- ChromaDB vector storage and sentence-transformer embeddings.
- Translation and language-detection libraries for multilingual support.
- Twilio integration for messaging workflows.
- Audio processing through pydub and multipart upload support.

## Repository Structure

- `app/main.py` - API entry point.
- `app/chatbot.py` - Conversation and retrieval workflow.
- `app/audio_handler.py` - Audio processing utilities.
- `populate_db.py` - Knowledge base population script.
- `requirements.txt` - Python dependencies.
- `USER_FLOW_DIAGRAM.md` - User journey documentation.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
uvicorn app.main:app --reload
```

## Professional Context

This project demonstrates applied NLP, retrieval, multilingual product design, and social-impact oriented backend engineering.
