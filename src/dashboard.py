import streamlit as st
import yaml
import json
import pandas as pd
import matplotlib.pyplot as plt
from llm.gemini import Gemini
from utils.vector_storage import search_vector_storage

SELF_ASK_SYS_PROMPT = """
    You are an expert in generating insights about Brazilian politics,
    and you need to help the user to understand the data about the Chamber of Deputies.
    
    You will be asked, and before you generate the insights, you will be given three questions and answers related to the data.
    
    Also you will be given database information with relevant data.
    
    Based on the quetions and answers and database information, you will generate the insights, considering the user input.
    
    Responda em português.
"""  

INTERMEDIATE_SYS_PROMPT = """
    You are an expert in generating insights about Brazilian politics,
    and you need to help the user to understand the data about the Chamber of Deputies.
    
    Your role is to generate insights about the data, creating three questions and answers related to the user question.
"""

SELF_ASK_MODEL = Gemini(system_prompt=SELF_ASK_SYS_PROMPT)
INTERMEDIATE_MODEL = Gemini(system_prompt=INTERMEDIATE_SYS_PROMPT)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Olá, como posso te ajudar?"}]

@st.cache_data(show_spinner=False)
def on_chat_submit(user_message: str) -> None:
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    st.chat_message("user").write(user_message)
    
    intermediate_response: str = INTERMEDIATE_MODEL.generate(user_message) 
    
    print(intermediate_response)
    
    db_response = search_vector_storage(user_message)
    
    self_ask_prompt = f"""
        Here are three questions and answers related to the user question:
        {intermediate_response}
        
        Here is the database information with relevant data:
        {db_response}
    
        Based on the questions and answers, please generate insights about the data considering the user input:    
        {user_message}
    """
    
    final_response: str = SELF_ASK_MODEL.generate(self_ask_prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": final_response})
    
    st.chat_message("assistant").write(final_response)

# Create tabs
tabs = st.tabs(["Overview", "Despesas", "Proposições"])

# Overview tab
with tabs[0]:
    st.title("Chamber of Deputies Overview")
    st.header("Here you can view data about the Chamber of Deputies, and get insights about the deputies activities")

    # Read and display YAML content
    with open("data/config.yml", "r") as yaml_file:
        yaml_content = yaml.safe_load(yaml_file)
    st.write("YAML Content:", yaml_content)

    # Read and display PNG image
    st.image("docs/distribuicao_deputados.png")

    # Read and display JSON content
    with open("data/insights_distribuicao_deputados.json", "r") as json_file:
        json_content = json.load(json_file)
    st.write("JSON Content:", json_content)

# Despesas tab
with tabs[1]:
    # Read and display JSON content
    with open("data/insights_despesas_deputados.json", "r") as json_file:
        despesas_json_content = json.load(json_file)
    st.write("JSON Content:", despesas_json_content)

    # Read and process parquet file for deputados
    deputados_df = pd.read_parquet("data/deputados.parquet")
    selected_nome = st.selectbox("Select a Deputy:", deputados_df["nome"].unique())

    # Read and filter expenses dataframe
    expenses_df = pd.read_parquet("data/serie_despesas_diárias_deputados.parquet")
    filtered_expenses_df = expenses_df[expenses_df["nome"] == selected_nome]

    # Convert date column to datetime and plot time series
    filtered_expenses_df['dataDocumento'] = pd.to_datetime(filtered_expenses_df['dataDocumento'])
    fig, ax = plt.subplots()
    filtered_expenses_df.plot.bar(x='dataDocumento', y='valorDocumento', ax=ax, legend=False)
    ax.set_title(f"Expenses Over Time for {selected_nome}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value (R$)")
    st.pyplot(fig)

# Proposições tab
with tabs[2]:
    # Read and display proposições dataframe
    proposicoes_df = pd.read_parquet("data/proposicoes_deputados.parquet")
    st.dataframe(proposicoes_df)

    # Read and display JSON content
    with open("docs/sumarizacao_proposicoes.json", "r") as json_file:
        proposicoes_json_content = json.load(json_file)
    st.write("JSON Content:", proposicoes_json_content)

st.divider()
    
st.button("Clear chat", on_click=lambda: st.session_state.pop("messages", None))

st.header("💬 Chatbot")

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

if prompt := st.chat_input():
    on_chat_submit(prompt)