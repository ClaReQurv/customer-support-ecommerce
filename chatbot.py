from langgraph.graph import StateGraph, MessagesState
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from tools import (
    query_knowledge_base,
    data_protection_check,
    create_new_customer,
    place_appointment,
    retrieve_existing_customer_orders,
)

import os


prompt = """#Scopo

Sei un chatbot per il servizio clienti di un salone di bellezza italiano. Puoi aiutare il cliente a raggiungere gli obiettivi elencati di seguito.

#Obiettivi

1. Rispondere alle domande dell'utente relative ai servizi offerti
2. Consigliare prodotti all'utente in base alle sue preferenze
3. Aiutare il cliente a controllare un ordine esistente o a effettuare un nuovo ordine
4. Per gestire gli ordini, avrai bisogno di un profilo cliente (con un ID associato). Se il cliente ha già un profilo, esegui un controllo di protezione dei dati per recuperare i suoi dettagli. In caso contrario, creagli un profilo.

#Tono

Essere utile e amichevole. Usa emoji della Gen-Z per mantenere un tono leggero.
"""

chat_template = ChatPromptTemplate.from_messages(
    [("system", prompt), ("placeholder", "{messages}")]
)

with open("./.env", "r", encoding="utf-8") as f:
    for line in f:
        key, value = line.strip().split("=")
        os.environ[key] = value

tools = [
    query_knowledge_base,
    data_protection_check,
    create_new_customer,
    place_appointment,
    retrieve_existing_customer_orders,
]

llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.environ["OPENAI_API_KEY"])

llm_with_prompt = chat_template | llm.bind_tools(tools)


def call_agent(message_state: MessagesState):

    response = llm_with_prompt.invoke(message_state)

    return {"messages": [response]}


def is_there_tool_calls(state: MessagesState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool_node"
    else:
        return "__end__"


graph = StateGraph(MessagesState)

tool_node = ToolNode(tools)

graph.add_node("agent", call_agent)
graph.add_node("tool_node", tool_node)

graph.add_conditional_edges("agent", is_there_tool_calls)
graph.add_edge("tool_node", "agent")

graph.set_entry_point("agent")

app = graph.compile()
