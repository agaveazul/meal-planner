from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from dotenv import load_dotenv
from tools.sql import run_query_tool, list_tables, describe_tables_tool
from handlers.chat_model_start_handler import ChatModelStartHandler
from typing import Any, List, Tuple


load_dotenv()


handler = ChatModelStartHandler()
chat = ChatOpenAI(
    callbacks=[handler],
    model_name="gpt-4"
)

tables = list_tables()

def run_llm(query: str, msgs: StreamlitChatMessageHistory, chat_history: List[Tuple[str,Any]]=[]) -> Any:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=(
                "You are an AI that has access to a SQLite database.\n"
                f"The database has tables of: {tables}\n"
                "Do not make any assumptions about what tables exist "
                "When asked to prepare a meal plan, search the SQL database for recipes."
                "Provide me with a proposal of recipes, with their name and their number of calories and ask me to confirm."
                "Once I confirm, provide me with the list of ingredients and the preparation steps for those recipes."
                )),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ]
    )
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, chat_memory=msgs)

    tools = [run_query_tool, 
            describe_tables_tool]

    agent = OpenAIFunctionsAgent(
        llm=chat,
        prompt=prompt,
        tools=tools
    )

    agent_executor = AgentExecutor(
        agent=agent,
        verbose=True,
        tools=tools,
        memory=memory
    )

    return agent_executor(query)