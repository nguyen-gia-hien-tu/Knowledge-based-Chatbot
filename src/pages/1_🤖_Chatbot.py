import streamlit as st
from langchain_core.runnables import Runnable

from utils.utils import setup_rag_chain, setup_tools


def main():

    # Set up page configuration
    st.sidebar.success("Select if you want to chat with the bot or upload documents")
    st.title("Knowledge-based Chatbot")

    # Setup LLM and Retriever
    llm, retriever = setup_tools()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display chat messages from history on app rerun
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message("human"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("ai"):
            rag_chain: Runnable = setup_rag_chain(llm, retriever)
            chain = rag_chain.pick("answer")

            history = [
                (message["role"], message["content"])
                for message in st.session_state["messages"]
            ]
            stream = chain.stream({"input": prompt, "chat_history": history})

            response = st.write_stream(stream)

        # Add user message to chat history
        st.session_state["messages"].append({"role": "human", "content": prompt})

        # Add assistant response to chat history
        st.session_state["messages"].append({"role": "ai", "content": response})


if __name__ == "__main__":
    main()
