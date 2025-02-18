import streamlit as st
from chatbot import app
from langchain_core.messages import AIMessage, HumanMessage


st.set_page_config(layout="wide", page_title="Beaty saloon chatbot", page_icon="💇🏼‍♀️")

if "message_history" not in st.session_state:
    st.session_state.message_history = [
        AIMessage(
            content="Ciao! Sono l'assistente virtuale del salone BlueHair. Come posso aiutarti?"
        )
    ]

left_col, main_col = st.columns([1, 3])

# 1. Buttons for chat - Clear Button

with left_col:
    if st.button("Clear Chat"):
        st.session_state.message_history = []


# 2. Chat history and input
with main_col:
    user_input = st.chat_input("Scrivi qui...")

    if user_input:
        st.session_state.message_history.append(HumanMessage(content=user_input))

        response = app.invoke({"messages": st.session_state.message_history})

        messages = []
        for message in response["messages"]:
            messages.append(message)

        st.session_state.message_history = messages

    for i in range(1, len(st.session_state.message_history) + 1):
        this_message = st.session_state.message_history[-i]
        if (
            len(this_message.content) > 0
            and not this_message.content.startswith("{")
            and not this_message.content.startswith("DPA check")
            and not this_message.content.startswith("[")
            and not this_message.content.startswith("Order with")
        ):
            if isinstance(this_message, AIMessage):
                message_box = st.chat_message("assistant")
            else:
                message_box = st.chat_message("user")

            message_box.markdown(this_message.content)
# 3. State variables

# with right_col:
# st.title("customers database")
# st.write(customers_database)
# st.title("data protection checks")
# st.write(data_protection_checks)
