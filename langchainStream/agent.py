from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from tools import summarize_occurrences
import pandas as pd

from dotenv import load_dotenv
load_dotenv() 

def create_agent(df: pd.DataFrame):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    def chat_with_table(question: str) -> str:
        context = df.to_markdown()
        prompt = f"""
You are a data analyst.
Answer ONLY using this table.

Table:
{context}

Question:
{question}
"""
        return llm.predict(prompt)

    tools = [
        Tool(
            name="ChatWithNHMTable",
            func=chat_with_table,
            description="Answer questions about NHM GBIF records table"
        )
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        verbose=False
    )

    return agent
