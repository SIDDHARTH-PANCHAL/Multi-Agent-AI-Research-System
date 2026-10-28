
import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, scrape_url

load_dotenv()

# Validate Mistral API key
if not os.getenv("MISTRAL_API_KEY"):
    raise ValueError(
        "MISTRAL_API_KEY missing in .env file."
    )

# Shared Mistral LLM for all agents and chains
llm = ChatMistralAI(
    model=os.getenv(
        "MISTRAL_MODEL",
        "mistral-small-latest"
    ),
    temperature=0,
)


# 1. Search Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are a web research agent. "
            "Use web_search to find relevant, reliable and recent "
            "information. Return source titles, URLs, dates and "
            "evidence. Never invent sources or facts."
        ),
    )


# 2. Reader Agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are a research reader agent. "
            "Read relevant URLs from the supplied search results "
            "using scrape_url. Extract facts, dates, statistics and "
            "supporting evidence. Preserve the source URLs. "
            "Clearly state when a page cannot be accessed. "
            "Never invent information."
        ),
    )


# 3. Writer Chain
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert research writer.
        Write structured, factual and evidence-based reports.
        Use the supplied research for factual claims.
        Do not invent citations, URLs, statistics or quotes.
        Clearly state uncertainty and evidence limitations."""
    ),
    (
        "human",
        """Write a research report on this topic.

Topic: {topic}

Research gathered:
{research}

Required structure:
1. Introduction
2. Key Findings (at least 3 detailed points)
3. Evidence and Analysis
4. Limitations and Conflicting Information
5. Conclusion
6. Sources (only URLs present in the research)

If the evidence is insufficient, say so explicitly."""
    ),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# 4. Critic Chain
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a strict and constructive research critic.
        Evaluate evidence quality, relevance, completeness,
        unsupported claims and citation accuracy.
        Do not assume a claim is true merely because the report states it."""
    ),
    (
        "human",
        """Review the report below.

Report:
{report}

Use this format:

Score: X/10

Strengths:
- ...

Areas to Improve:
- ...

Unsupported Claims:
- ...

One line verdict:
..."""
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()
