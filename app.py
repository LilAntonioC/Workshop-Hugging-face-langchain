import os
import streamlit as st
from dotenv import load_dotenv

from langchain import hub
from langchain.agents import Tool, create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

load_dotenv()


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 🚧✏️ MODIFY ONLY THIS SECTION BELOW — DO NOT TOUCH ANYTHING ELSE ✏️🚧 ║
# ╚════════════════════════════════════════════════════════════════════╝


# --- Define a simple tool ---
def SquareNumbers(input: str) -> str:
    try:
        number = float(input)
        return number**2
    except ValueError:
        return "Please enter a valid number."


tools = [
    Tool(
        name="SquareCalculator",
        func=SquareNumbers,
        description="Use this tool to calculate the square of a number. Input should be a number.",
    )
]


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 🤖 MODEL SETUP — Choose ONE of the options below to initialize the LLM ║
# ╚════════════════════════════════════════════════════════════════════╝

# 👉 Option 1: Use OpenAI (recommended if you have API access)
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)

# 👉 Option 2: Use Ollama (for local models like LLaMA3)
# Uncomment the line below and comment out the OpenAI line above if you're using Ollama:
# llm = ChatOllama(temperature=0, model="llama3.1")


# ╔════════════════════════════════════════════════════════════════════╗
# ║ ✅ YOU'RE DONE! DON'T MODIFY BELOW THIS LINE UNLESS INSTRUCTED ✅ ║
# ╚════════════════════════════════════════════════════════════════════╝


# --- Load agent prompt from LangChain Hub ---
prompt = hub.pull("hwchase17/openai-functions-agent")

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Streamlit UI ---
st.title("LangChain Agent (Homework)")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi! Ask me questions.",
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Enter a number to square...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        try:
            response = agent_executor.invoke({"input": user_input})
            print(response)
            st.session_state.messages.append(
                {"role": "assistant", "content": response["output"]}
            )
        except Exception as e:
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Oops! Something went wrong: {e}"}
            )

    st.rerun()
