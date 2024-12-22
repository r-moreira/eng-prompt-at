# INFNET
## Engenharia de Prompts para Ciência de Dados [24E4_4] - AT
### Rodrigo Avila - 22/12/2024
---

[Repositório GIT](https://github.com/r-moreira/eng-prompt-at)

---
### Sobre o projeto:
Aplicação que visa resolver os exercícios propostos na atividade de Engenharia de Prompts para Ciência de Dados.

Obs: Não subi para o git o índice do Faiss pois o arquivo ficou muito grande.

### Estrutura do projeto:
```README.md``` - Este arquivo.

```rodrigo_avila_DR4_AT.ipynb```- Contém a resolução dos exercícios teóricos e de notebook.

```./src/*``` - Contém o código fonte da aplicação com a resolução de todos os exercícios.

```./requirements.txt``` - Contém as dependências do projeto.

```./data```- Contém os arquivos gerados pelos exercícios.

```./docs```- Contém os arquivos gerados pelos exercícios.

```./images```- Contém os prints de prompts de alguns exercícios.


### Como rodar o projeto:
1. Configurando versão do python:
```bash
pyenv local 3.11.9
```

2. Crie um ambiente virtual:
```bash
python -m venv .venv
```

3. Ative o ambiente virtual:
```bash
source .venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Execute a aplicação (dataprep):
```bash
# No diretório raiz do projeto
python3 src/dataprep.py --help #Exibe a ajuda, especificando os argumentos necessários
```

6. Execute a aplicação (Streamlit):
```bash
# No diretório raiz do projeto
streamlit run src/dashboard.py       
```