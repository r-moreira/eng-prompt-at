import streamlit as st
import yaml
import json

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
    st.write("Content for Despesas tab")

# Proposições tab
with tabs[2]:
    st.write("Content for Proposições tab")
