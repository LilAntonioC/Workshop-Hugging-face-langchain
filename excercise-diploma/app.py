
import streamlit as st
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.agents import Tool, tool
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from datetime import date, datetime

load_dotenv()


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 🚧✏️ MODIFY ONLY THIS SECTION BELOW — DO NOT TOUCH ANYTHING ELSE ✏️🚧 ║
# ╚════════════════════════════════════════════════════════════════════╝
def solve_operations(input: str):
    return str(eval(input))

def date_differences(inputdate : str) : 
    
    d1 = datetime.strptime(inputdate, r"%Y-%m-%d").date()
    d2 = date.today()
    return str( abs((d2 - d1).days) )

def temperature_conversion(temp : str) : 
    return str(( float(temp) - 32 )  * 5 / 9 )

def quadratic_equation(input: str):
    parts = input.strip().split(",")
    
    if len(parts) != 3:
        return "ERROR: You must input exactly 3 comma-separated numbers like '1,2,-3'\n"
    
    try:
        a, b, c = map(float, parts)
    except ValueError:
        return "ERROR: All inputs must be numeric. Use format like '1,2,-3'\n"

    if a == 0:
        return "ERROR: 'a' must not be 0 in a quadratic equation\n"

    disc = b**2 - 4*a*c
    if disc < 0:
        return "No real roots\n"
    if disc == 0:
        return f"The solution is {-b / ( 2 * a )}\n"
    sqrt_disc = disc**0.5
    r1 = (-b + sqrt_disc) / (2*a)
    r2 = (-b - sqrt_disc) / (2*a)
    return f"First solution is {r1} and the second solution is {r2}\n"

    
    

tools = [
Tool(
    name="TemperatureConversion",
    func=temperature_conversion,
    description="Convert farenheit degrees into Celsius . JUST Input a decimal value like '113.5'."
),
Tool(
    name="Calculator",
    func=solve_operations,
    description="Evaluates simple math expressions like '10 / 8 + 4 * (2 + 1)'."
),
Tool(
    name="DateDifference",
    func=date_differences,
    description="Get how many days have passed since a date. You have to format the given date into YYYY-MM-DD"
),

Tool(
    name="QuadraticSolver",
    func=quadratic_equation,
    description="""
    Solves a quadriatic equation in the form ax^2 + bx + c where a,b,c are the quofficients
    
    INPUT : a STRING of 3 (THREE, the THIRD number) comma separated values in the form a,b,c EG. 10,2,-3
    If a quofficient is missing use 0 for that quofficient. If there is no quofficient and just the term, use 0
    EXAMPLES : 10x^2 + 9x - 3 becomes 10,9,-3
    EXAMPLES : 5x^2- 2 becomes 5, 0, -2 because there is no b
    EXAMPLES : x^2 becomes 1, 0, 0 Because there is no b or c
    
    """
),

]

# ╔════════════════════════════════════════════════════════════════════╗
# ║ 🤖 MODEL SETUP — Choose ONE of the options below to initialize the LLM ║
# ╚════════════════════════════════════════════════════════════════════╝

llm = ChatOllama(model="llama3.2")


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
