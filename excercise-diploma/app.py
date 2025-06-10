import os
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import math

from langchain import hub
from langchain.agents import Tool, create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
#from langchain_ollama import ChatOllama

load_dotenv()


# ╔════════════════════════════════════════════════════════════════════╗
# ║ 🚧✏️ MODIFY ONLY THIS SECTION BELOW — DO NOT TOUCH ANYTHING ELSE ✏️🚧 ║
# ╚════════════════════════════════════════════════════════════════════╝


# --- Define tools ---
def evaluate_math_expression(input: str) -> str:
    try:
        result = eval(input.strip())
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

def calculate_date_difference(input: str) -> str:
    try:
        input_date = datetime.strptime(input, "%Y-%m-%d")
        today = datetime.now()
        difference = (today - input_date).days
        return f"{difference} days have passed since {input}"
    except ValueError:
        return "Please enter a valid date in YYYY-MM-DD format"
    except Exception as e:
        return f"Error calculating date difference: {str(e)}"

def convert_fahrenheit_to_celsius(input: str) -> str:
    try:
        fahrenheit = float(input)
        celsius = (fahrenheit - 32) * 5 / 9
        return f"{fahrenheit}°F is equal to {celsius:.2f}°C"
    except ValueError:
        return "Please enter a valid number"
    except Exception as e:
        return f"Error converting temperature: {str(e)}"

def solve_quadratic_equation(input: str) -> str:
    try:
        a, b, c = map(float, input.split())
        
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:
            return "No real roots exist (discriminant < 0)"
        elif discriminant == 0:
            x = -b / (2*a)
            return f"One real root: x = {x:.2f}"
        else:
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            return f"Two real roots: x₁ = {x1:.2f}, x₂ = {x2:.2f}"
    except ValueError:
        return "Please enter three numbers separated by spaces (a b c)"
    except Exception as e:
        return f"Error solving quadratic equation: {str(e)}"

tools = [
    Tool(
        name="MathExpressionEvaluator",
        func=evaluate_math_expression,
        description="Use this tool to evaluate mathematical expressions. Input should be a valid mathematical expression.",
    ),
    Tool(
        name="DateDifferenceCalculator",
        func=calculate_date_difference,
        description="Use this tool to calculate the number of days between a given date and today. Input should be a date in YYYY-MM-DD format.",
    ),
    Tool(
        name="TemperatureConverter",
        func=convert_fahrenheit_to_celsius,
        description="Use this tool to convert temperature from Fahrenheit to Celsius. Input should be a number representing temperature in Fahrenheit.",
    ),
    Tool(
        name="QuadraticEquationSolver",
        func=solve_quadratic_equation,
        description="Use this tool to solve quadratic equations. Input should be three numbers separated by spaces (a b c) representing the coefficients of ax² + bx + c = 0.",
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
