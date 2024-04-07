import pandas as pd
import streamlit as st
import os
import requests

# Função para classificar o resultado com base nos gols das equipes da casa e visitantes
def classificar_resultado(row):
    if row['HG'] > row['AG']:
        return 'W'
    elif row['HG'] < row['AG']:
        return 'L'
    else:
        return 'D'

def calcular_coeficiente(row):
    diferenca_gols = row['HG'] - row['AG']
    return diferenca_gols

# Função para fazer o download de um arquivo e armazená-lo em cache
def download_and_cache(url):
    cache_folder = "cache"
    cache_file = os.path.join(cache_folder, os.path.basename(url))
    
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    
    if not os.path.exists(cache_file):
        response = requests.get(url)
        with open(cache_file, 'wb') as f:
            f.write(response.content)
    
    return cache_file

# Carregar os arquivos CSV
file_paths = [
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/2223/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/2122/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/2021/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1920/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1819/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1718/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1617/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1516/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/1415/E0.csv", #England Premier League
    "https://www.football-data.co.uk/mmz4281/2324/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/2223/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/2122/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/2021/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1920/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1819/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1718/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1617/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1516/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/1415/E1.csv", #England Championship 
    "https://www.football-data.co.uk/mmz4281/2324/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/2223/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/2122/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/2021/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/1920/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/1819/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/1718/E2.csv", #England League 1 
    "https://www.football-data.co.uk/mmz4281/1617/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/1516/E2.csv", #England League 1
    "https://www.football-data.co.uk/mmz4281/1415/E2.csv", #England League 1

    "https://www.football-data.co.uk/mmz4281/2324/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/2223/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/2122/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/2021/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1920/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1819/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1718/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1617/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1516/SC0.csv", #Scotland Premier League
    "https://www.football-data.co.uk/mmz4281/1415/SC0.csv", #Scotland Premier League
    
    "https://www.football-data.co.uk/mmz4281/2324/D1.csv", #Germany Bundesliga
    "https://www.football-data.co.uk/mmz4281/2223/D1.csv",
    "https://www.football-data.co.uk/mmz4281/2122/D1.csv",
    "https://www.football-data.co.uk/mmz4281/2021/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1920/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1819/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1718/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1617/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1516/D1.csv",
    "https://www.football-data.co.uk/mmz4281/1415/D1.csv",

    "https://www.football-data.co.uk/mmz4281/2324/D2.csv", #Germany Bundesliga 2
    "https://www.football-data.co.uk/mmz4281/2223/D2.csv",
    "https://www.football-data.co.uk/mmz4281/2122/D2.csv",
    "https://www.football-data.co.uk/mmz4281/2021/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1920/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1819/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1718/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1617/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1516/D2.csv",
    "https://www.football-data.co.uk/mmz4281/1415/D2.csv",
    
    "https://www.football-data.co.uk/new/BRA.csv"
]

dfs = []
for file_path in file_paths:
    cached_file = download_and_cache(file_path)
    df = pd.read_csv(cached_file)
    
    # Verificar o formato do arquivo e ajustar as colunas conforme necessário
    if 'FTHG' in df.columns:
        # Formato do primeiro arquivo
        df.rename(columns={
            'HomeTeam': 'Home',
            'AwayTeam': 'Away',
            'FTHG': 'HG',
            'FTAG': 'AG',
            'FTR': 'Res',
            'PSCH': 'PH',
            'PSCD': 'PD',
            'PSCA': 'PA'
        }, inplace=True)
    elif 'Country' in df.columns:
        # Formato do segundo arquivo
        df.rename(columns={
            'Date': 'Data',
            'Home': 'Home',
            'Away': 'Away',
            'HG': 'HG',
            'AG': 'AG',
            'Res': 'Res',
            'PH': 'PH',
            'PD': 'PD',
            'PA': 'PA'
        }, inplace=True)
        # Format 'Data' column to datetime
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
    
    # Adicionar coluna de resultado
    df['Resultado'] = df.apply(classificar_resultado, axis=1)
    
    # Calcular coeficiente de eficiência da equipe da casa
    df['Coeficiente_Eficiencia'] = df.apply(calcular_coeficiente, axis=1)
    
    dfs.append(df)

# Concatenar todos os dataframes
df = pd.concat(dfs)

# Obter todas as equipes envolvidas nos jogos
all_teams_home = set(df['Home'])

# Ordenar os times em ordem alfabética
times = sorted(str(team) for team in all_teams_home)

# Interface do Streamlit
def main():
    st.title("Winrate Odds")
    st.sidebar.header("Filtros")
    time = st.sidebar.selectbox("Selecione o Time da Casa:", options=times)
    mostrar_resultados(time)

def mostrar_resultados(time):
    team_df = df[df['Home'] == time]
    team_df = team_df[['Data', 'Home', 'Away', 'PH', 'PD', 'PA', 'HG', 'AG', 'Res', 'Coeficiente_Eficiencia']]

    # Drop duplicate rows
    team_df = team_df.drop_duplicates()

    # Exibir resultados em uma tabela
    st.write("### Partidas:")
    st.dataframe(team_df)

if __name__ == "__main__":
    main()
