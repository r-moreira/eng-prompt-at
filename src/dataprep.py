import requests
import pandas as pd
import json
from llm.gemini import Gemini
from utils.chunk_summary import ChunkSummary
from utils.vector_storage import dataframe_to_text_list, write_texts_to_file, create_faiss_index, search_vector_storage
from dotenv import load_dotenv
import argparse
from tqdm import tqdm

load_dotenv('.env')

CAMARA_BASE_URL = 'https://dadosabertos.camara.leg.br/api/v2/'

def fetch_and_save_deputados_data() -> None:
    """
        Exercício 3 a): 
    """
    
    params = {
        'dataInicio': "2024-08-01", 
        'dataFim': "2024-08-30",
    }
    
    response = requests.get(f'{CAMARA_BASE_URL}/deputados', params=params)
    
    if not response.ok:
        raise Exception('Nao foi possivel recuperar os dados')
    
    df_deputados = pd.DataFrame().from_dict(json.loads(response.text)['dados'])
    
    df_deputados[['id', 'nome', 'siglaPartido']].to_parquet('data/deputados.parquet') 
    
    print('Dados dos deputados salvos com sucesso')

def generated_partidos_pizza_plot() -> None:
    """
        Exercício 3 b): 
    """
    
    sys_prompt = """
        You are expert in generate python code to be executed in an application by exec() function.
    """
    
    prompt = """
        You need to read a file as pandas dataframe in the format parquet in the path 'data/deputados.parquet'
        
        The dataframe has the following columns:
        id                  nome    siglaPartido
        123        Abilio Brunini             PL
        124        Acácio Favacho            MDB
        125           Adail Filho   REPUBLICANOS
        126       Adilson Barroso             PL
        
        After generating the dataframe, you need to create a new dataframe grouping by 'siglaPartido' that will be needed to generated insights of 'siglaPartido' distribution.
        
        Using the new generated dataframe, you need to create a pizza chart with the column 'siglaPartido' as the labels and the percentage of each 'siglaPartido', 
        save the plot as docs/distribuicao_deputados.png file.
        
        Don't use markdown, and do not provide any code or example that is not necessary to solve the problem. 
    """
    
    model = Gemini(system_prompt=sys_prompt)

    code = model.generate(prompt).replace('```python', '').replace('```', '')
    
    print("Generated code:\n", code)
    
    exec(code)
    
    print('Code executed successfully')

def insights_dist_deputados() -> None:
    """
        Exercício 3 c):        
    """

    # Mesmo código gerado no exercício 3 b), removido apenas a parte de salvar o plot
    df = pd.read_parquet('data/deputados.parquet')
    partidos_df = df.groupby('siglaPartido')['nome'].count().reset_index()
    partidos_df = partidos_df.rename(columns={'nome': 'total'})
    partidos_df['percentual'] = partidos_df['total'] / partidos_df['total'].sum()
    
    sys_prompt = """
        You are an expert in generating insights about Brazilian politics. 
    """
    
    insights_example = """
          {
            "insights": [
                {
                    "description": "The party with the most deputados is MDB with 20 deputados"
                },
                {
                    "description": "The party with the least deputados is PL with 10 deputados"
                },
                {
                    "description": "The party with the highest percentage of deputados is MDB with 20%"
                },
                {
                    "description": "The party with the lowest percentage of deputados is PL with 10%"
                }
            ]
        }
    """
    
    prompt = f"""
        You need to generate insights about the distribution of 'siglaPartido' in the dataframe 'partidos_df' that has the following columns:
        
        Example of the dataframe:
            siglaPartido  total  percentual
            PL            10     0.1
            MDB           20     0.2
            
        The insights should be in .json() format, your response must contain only json data.
        
        Example of insights:
        {insights_example}
        
        Here is the dataframe:
        {partidos_df}
    """
    
    model = Gemini(system_prompt=sys_prompt)

    json = model.generate(prompt).replace('```json', '').replace('```', '')
    
    print("Generated insights:\n", json)
    
    with open('data/insights_distribuicao_deputados.json', 'w') as f:
        f.write(json)

def fetch_deputados_expenses(id_legislatura='57', ano_despesa='2024', mes_despesa='8', max_itens='100'):
    """
        Exercício 4 a)
    """
    
    list_expenses = []
    df_deputados = pd.read_parquet('data/deputados.parquet')

    def fetch_expenses_for_deputado(id):
        url = f'{CAMARA_BASE_URL}/deputados/{id}/despesas'
        params = {
            'idLegislatura': id_legislatura, 
            'ano': ano_despesa,
            'mes': mes_despesa,
            'itens': int(max_itens),
        }
        while url:
            response = requests.get(url, params=params)
            data = json.loads(response.text)
            df_resp = pd.DataFrame().from_dict(data['dados'])
            df_resp['id'] = id
            list_expenses.append(df_resp)
            url = next((link['href'] for link in data['links'] if link['rel'] == 'next'), None)
            params = None  

    for id in tqdm(df_deputados.id.unique()):
        fetch_expenses_for_deputado(id)
        
    df_expenses = pd.concat(list_expenses)
    df_expenses = df_expenses.merge(df_deputados, on=['id'])
    df_expenses[[
        'tipoDespesa',
        'dataDocumento',
        'valorDocumento', 
        'nomeFornecedor', 
        'id',
        'nome',
        'siglaPartido'
    ]].to_parquet('data/serie_despesas_diárias_deputados.parquet')
    
def fetch_propositions(data_inicio="2024-08-01", data_fim="2024-08-30", cod_tema="40,46,62"):
    """
        Exercício 5 a)
    """
    
    url = f'{CAMARA_BASE_URL}/proposicoes'
    params = {
                'dataInicio': data_inicio, 
                'dataFim': data_fim,
                'codTema': cod_tema
            }

    response = requests.get(url, params=params)
    
    if not response.ok:
        raise Exception('Nao foi possivel recuperar os dados')

    df_proposicoes = pd.DataFrame().from_dict(json.loads(response.text)['dados'])
    df_proposicoes.head(10).to_parquet('data/proposicoes_deputados.parquet')
    
def propositions_summarizer():
    system_prompt = """
    You are an expert in the Chamber of Deputies in Brazil.
    You will receive chunk of propositions from the Chamber of Deputies in Brazil.

    You must create a summary of the propositions, pointing out the most
    relevant information in each chunk.
    
    The output should be in JSON format, like this:     
        {
            "summary": "The summary of the propositions"
        }
    """

    generation_config = {
        'temperature': 0.2,
        'max_output_tokens': 200
    }
    
    df_proposicoes = pd.read_parquet('data/proposicoes_deputados.parquet')

    summarizer = ChunkSummary(    
        text = df_proposicoes['ementa'].tolist(),
        window_size = 5,
        overlap_size = 3,
        system_prompt=system_prompt,
        generation_config=generation_config,
    )

    summary, _ = summarizer.summarize()
    
    print(summary)
    
    with open('docs/sumarizacao_proposicoes.json', 'w') as f:
        f.write(summary.replace('```json', '').replace('```', ''))


def generate_vector_storage():
    """
        Exercício 8
    """

    def insights_despesas_to_text_list(json_data):
        """
            Transforma o json de insights de despesas em uma lista de strings para ser salvo na base de dados vetorizada
        """
        text_list = []

        biggest_expense = json_data['biggest_expense']
        text_list.append(f"Biggest Expense: {biggest_expense['expense_type']} on {biggest_expense['document_date']} with value {biggest_expense['document_value']} by {biggest_expense['supplier_name']} for deputy {biggest_expense['deputy_name']} from party {biggest_expense['party']}.")

        lowest_expense = json_data['lowest_expense']
        text_list.append(f"Lowest Expense: {lowest_expense['expense_type']} on {lowest_expense['document_date']} with value {lowest_expense['document_value']} by {lowest_expense['supplier_name']} for deputy {lowest_expense['deputy_name']} from party {lowest_expense['party']}.")

        most_frequent_expense = json_data['most_frequent_expense']
        text_list.append(f"Most Frequent Expense: {most_frequent_expense['expense_type']} - {most_frequent_expense['description']}")

        highest_expense_summary = json_data['expense_summary']['highest_expense']
        text_list.append(f"Expense Summary - Highest Expense: Deputy {highest_expense_summary['deputy']} from party {highest_expense_summary['party']} with amount {highest_expense_summary['amount']} by {highest_expense_summary['supplier']}.")

        lowest_expense_summary = json_data['expense_summary']['lowest_expense']
        text_list.append(f"Expense Summary - Lowest Expense: Deputy {lowest_expense_summary['deputy']} from party {lowest_expense_summary['party']} with amount {lowest_expense_summary['amount']} by {lowest_expense_summary['supplier']}.")

        insights = json_data['insights']
        for insight in insights:
            text_list.append(f"Insight: {insight}")

        return text_list

    try:
        df_parquet = pd.read_parquet('data/deputados.parquet')
        df_expenses = pd.read_parquet('data/serie_despesas_diárias_deputados.parquet')
        df_proposicoes = pd.read_parquet('data/proposicoes_deputados.parquet')
        with open("data/insights_distribuicao_deputados.json", "r") as json_file:
            insights_dist_deputados_json_content = json.load(json_file)
        with open("data/insights_despesas_deputados.json", "r") as json_file:
            despesas_json_content = json.load(json_file)
        with open("docs/sumarizacao_proposicoes.json", "r") as json_file:
            sumarizacao_proposicoes_json_content = json.load(json_file)
            
        texts = (
            dataframe_to_text_list(df_parquet) 
            + dataframe_to_text_list(df_expenses)
            + dataframe_to_text_list(df_proposicoes)
            + [x['description'] for x in insights_dist_deputados_json_content['insights']]
            + insights_despesas_to_text_list(despesas_json_content)
            + [sumarizacao_proposicoes_json_content['summary']]
        )
    
        write_texts_to_file(texts, 'data/combined_texts.txt')
        create_faiss_index(texts, 'neuralmind/bert-base-portuguese-cased', 'data/faiss_index.bin')
        
        print('Vector storage generated successfully')
    except Exception as e:
        print(f'Error generating vector storage: {e}')
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI to execute functions.')
    parser.add_argument('--fetch_deputies', action='store_true', help='Fetch and save deputados data')
    parser.add_argument('--plot', action='store_true', help='Generate partidos pizza plot')
    parser.add_argument('--insights', action='store_true', help='Generate insights dist deputados')
    parser.add_argument('--fetch_expenses', action='store_true', help='Fetch deputados expenses')
    parser.add_argument('--fetch_propositions', action='store_true', help='Fetch propositions')
    parser.add_argument('--summarize_propositions', action='store_true', help='Summarize propositions')
    parser.add_argument('--generate_vector_storage', action='store_true', help='Generate vector storage')
    parser.add_argument('--search_vector_storage', action='store_true', help='Search vector storage')

    args = parser.parse_args()

    if args.fetch_deputies:
        fetch_and_save_deputados_data()
    if args.plot:
        generated_partidos_pizza_plot()
    if args.insights:
        insights_dist_deputados()
    if args.fetch_expenses:
        fetch_deputados_expenses()
    if args.fetch_propositions:
        fetch_propositions()
    if args.summarize_propositions:
        propositions_summarizer()
    if args.generate_vector_storage:
        generate_vector_storage()
    if args.search_vector_storage:
        # apenas para teste
        results = search_vector_storage('educação')
        print(results)