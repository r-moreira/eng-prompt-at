import streamlit as st
import yaml
import json
import pandas as pd
import matplotlib.pyplot as plt

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
