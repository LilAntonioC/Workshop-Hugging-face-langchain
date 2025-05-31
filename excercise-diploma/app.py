import os
import streamlit as st
from dotenv import load_dotenv
import datetime
import math
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

def math_evaluator(input: str) -> str:
    """Evaluate basic math expressions"""
    try:
        return str(eval(input))
    except:
        return "Invalid math expression"

def date_difference(input_date: str) -> str:
    """Calculate days between input date and today"""
    try:
        target_date = datetime.datetime.strptime(input_date, "%Y-%m-%d").date()
        today = datetime.date.today()
        delta = (today - target_date).days
        return str(delta)
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD"

def fahrenheit_to_celsius(temp_f: str) -> str:
    """Convert Fahrenheit to Celsius"""
    try:
        f = float(temp_f)
        c = (f - 32) * 5 / 9
        return f"{c:.1f}°C"
    except ValueError:
        return "Invalid temperature value"

def quadratic_solver(input_str: str) -> str:
    """Solve quadratic equation ax²+bx+c=0"""
    try:
        a, b, c = map(float, input_str.split(","))
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:
            return "No real roots"
        elif discriminant == 0:
            root = (-b) / (2*a)
            return f"One real root: {root:.2f}"
        else:
            root1 = (-b + math.sqrt(discriminant)) / (2*a)
            root2 = (-b - math.sqrt(discriminant)) / (2*a)
            return f"Two real roots: {root1:.2f}, {root2:.2f}"
    except:
        return "Invalid input format. Provide a,b,c as numbers"

tools = [
    Tool(
        name="SquareCalculator",
        func=SquareNumbers,
        description="Use this tool to calculate the square of a number. Input should be a number.",
    ),    Tool(
        name="MathEvaluator",
        func=math_evaluator,
        description="Use for basic math expressions. Input: math expression as string"
    ),
    Tool(
        name="DateDifference",
        func=date_difference,
        description="Calculate days between date and today. Input: YYYY-MM-DD"
    ),
    Tool(
        name="TempConverter",
        func=fahrenheit_to_celsius,
        description="Convert Fahrenheit to Celsius. Input: temperature as string"
    ),
    Tool(
        name="QuadraticSolver",
        func=quadratic_solver,
        description="Solve quadratic equations. Input: three coefficients as comma-separated string"
    )
]


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 🤖 MODEL SETUP — Choose ONE of the options below to initialize the LLM ║
# ╚════════════════════════════════════════════════════════════════════╝

# 👉 Option 1: Use OpenAI (recommended if you have API access)
# llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)

# 👉 Option 2: Use Ollama (for local models like LLaMA3)
# Uncomment the line below and comment out the OpenAI line above if you're using Ollama:
llm = ChatOllama(temperature=0, model="llama3.1")


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
