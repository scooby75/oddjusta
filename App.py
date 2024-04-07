import pandas as pd
import streamlit as st
import os
import requests

# Função para classificar o resultado com base nos gols das equipes da casa e visitantes
def classificar_resultado(row):
    if row['Gols_Home'] > row['Gols_Away']:
        return 'W'
    elif row['Gols_Home'] < row['Gols_Away']:
        return 'L'
    else:
        return 'D'

def calcular_coeficiente(row):
    diferenca_gols = row['Gols_Home'] - row['Gols_Away']
    return diferenca_gols

def agrupar_odd(odd):
    for i in range(1, 60):
        lower = 1 + (i - 1) * 0.10
        upper = 1 + i * 0.10
        if lower <= odd <= upper:
            return f"{lower:.2f} - {upper:.2f}"
    return 'Outros'

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
    
    "https://www.football-data.co.uk/new/ARG.csv",
    "https://www.football-data.co.uk/new/AUT.csv",
    "https://www.football-data.co.uk/new/BRA.csv",
    "https://www.football-data.co.uk/new/CHN.csv",
    "https://www.football-data.co.uk/new/DNK.csv",
    "https://www.football-data.co.uk/new/FIN.csv",
    "https://www.football-data.co.uk/new/IRL.csv"
    
    
]

dfs = []
for file_path in file_paths:
    cached_file = download_and_cache(file_path)
    df = pd.read_csv(cached_file)
    
    # Verificar o formato do arquivo e ajustar as colunas conforme necessário
    if 'FTHG' in df.columns:
        # Formato do primeiro arquivo
        df.rename(columns={
            'Date': "Data",
            'HomeTeam': 'Home',
            'AwayTeam': 'Away',
            'FTHG': 'Gols_Home',
            'FTAG': 'Gols_Away',
            'FTR': 'Resultado',
            'PSCH': 'Odd_Home',
            'PSCD': 'Odd_Empate',
            'PSCA': 'Odd_Away'
        }, inplace=True)
    elif 'Country' in df.columns:
        # Formato do segundo arquivo
        df.rename(columns={
            'Date': 'Data',
            'Home': 'Home',
            'Away': 'Away',
            'HG': 'Gols_Home',
            'AG': 'Gols_Away',
            'Res': 'Resultado',
            'PH': 'Odd_Home',
            'PD': 'Odd_Empate',
            'PA': 'Odd_Away'
        }, inplace=True)
    
    # Adicionar coluna de resultado
    df['Resultado'] = df.apply(classificar_resultado, axis=1)
    
    # Calcular coeficiente de eficiência da equipe da casa
    df['Coeficiente_Eficiencia'] = df.apply(calcular_coeficiente, axis=1)

    # Adicionar coluna de agrupamento de odds
    if 'Odd_Home' in df:
        df['Odd_Group'] = df['Odd_Home'].apply(agrupar_odd)
    
    dfs.append(df)

# Concatenar todos os dataframes
df = pd.concat(dfs)

# Obter todas as equipes envolvidas nos jogos
all_teams_home = set(df['Home'])

# Ordenar os times em ordem alfabética
times = sorted(str(team) for team in all_teams_home)

# Ordenar as faixas de odds
odds_groups = sorted(df['Odd_Group'].unique())

# Interface do Streamlit
def main():
    st.title("Winrate Odds")
    st.sidebar.header("Filtros")
    time = st.sidebar.selectbox("Selecione o Time da Casa:", options=times)
    odds_group = st.sidebar.selectbox("Selecione a Faixa de Odds:", options=odds_groups)
    mostrar_resultados(time, odds_group)

def mostrar_resultados(time, odds_group):
    team_df = df[(df['Home'] == time) & (df['Odd_Group'] == odds_group)]
    team_df = team_df[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Empate', 'Odd_Away', 'Gols_Home', 'Gols_Away', 'Resultado', 'Coeficiente_Eficiencia']]

    # Drop duplicate rows
    team_df = team_df.drop_duplicates()

    # Format 'Data' column for display
    team_df['Data'] = pd.to_datetime(team_df['Data'])
    team_df['Data'] = team_df['Data'].dt.strftime('%d-%m-%Y')

    # Exibir resultados em uma tabela
    st.write("### Partidas:")
    st.dataframe(team_df)

    # Calcular quantas vezes o time da casa ganhou
    num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
    total_matches = team_df.shape[0]
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0

    # Calcular lucro/prejuízo total
    team_df['Lucro_Prejuizo'] = team_df.apply(lambda row: row['Odd_Home'] - 1 if row['Resultado'] == 'W' else -1, axis=1)
    lucro_prejuizo_total = team_df['Lucro_Prejuizo'].sum()

    # Calcular médias
    media_gols_casa = team_df['Gols_Home'].mean()
    media_gols_tomados = team_df['Gols_Away'].mean()
    
    # Calcular coeficiente de eficiência médio ajustado
    coeficiente_eficiencia_total = team_df['Coeficiente_Eficiencia'].sum()
    coeficiente_eficiencia_medio = coeficiente_eficiencia_total / total_matches if total_matches > 0 else 0

    # Calcular odd justa
    odd_justa = 100 / win_percentage if win_percentage > 0 else 0
    
    # Destacar resultados importantes usando markdown
    st.write("### Resumo:")
    st.markdown(f"- O'{time}' ganhou {num_wins} vez(es) em {total_matches} jogo(s), aproveitamento de ({win_percentage:.2f}%).")
    st.markdown(f"- Odd justa: {odd_justa:.2f}.")
    st.markdown(f"- Coeficiente de eficiência médio: {coeficiente_eficiencia_medio:.2f}.")
    st.markdown(f"- Lucro/prejuízo total: {lucro_prejuizo_total:.2f}.")
    st.markdown(f"- Média de gols marcados pelo time da casa: {media_gols_casa:.2f}.")
    st.markdown(f"- Média de gols sofridos pelo time visitante: {media_gols_tomados:.2f}.")

if __name__ == "__main__":
    main()
