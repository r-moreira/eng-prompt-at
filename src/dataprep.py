import requests
import pandas as pd
import json
from llm.gemini import Gemini
from dotenv import load_dotenv
import argparse
from tqdm import tqdm

load_dotenv('.env')

CAMARA_BASE_URL = 'https://dadosabertos.camara.leg.br/api/v2/'

def fetch_and_save_deputados_data() -> None:
    """
        Exercício 3 a): 
    """
    
    response = requests.get(f'{CAMARA_BASE_URL}/deputados')
    
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
    
    with open('docs/distribuicao_deputados.json', 'w') as f:
        f.write(json)

def fetch_deputados_expenses(id_legislatura='57', ano_despesa='2024', mes_despesa='8', max_itens='100'):
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI to execute functions.')
    parser.add_argument('--fetch', action='store_true', help='Fetch and save deputados data')
    parser.add_argument('--plot', action='store_true', help='Generate partidos pizza plot')
    parser.add_argument('--insights', action='store_true', help='Generate insights dist deputados')
    parser.add_argument('--fetch_expenses', action='store_true', help='Fetch deputados expenses')

    args = parser.parse_args()

    if args.fetch:
        fetch_and_save_deputados_data()
    if args.plot:
        generated_partidos_pizza_plot()
    if args.insights:
        insights_dist_deputados()
    if args.fetch_expenses:
        fetch_deputados_expenses()