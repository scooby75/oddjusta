# Importe as bibliotecas necessárias
import pandas as pd
from datetime import datetime
import streamlit as st
import os
import requests

# Importe os file_paths de bd.py
from bd import file_paths

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

# Função para converter a data do formato "Sep 03 2022 - 1:00pm" para "dd/mm/yyyy"
def converter_data_gmt(date_str):
    # Analisar a string de data no formato fornecido
    date_obj = datetime.strptime(date_str, '%b %d %Y - %I:%M%p')
    # Converter para o formato "dd/mm/yyyy" e retornar como string
    return date_obj.strftime('%d-%m-%Y')

# Importe os file_paths de bd.py
from bd import file_paths

# Carregar os arquivos CSV
dfs = []
for file_path in file_paths:
    cached_file = download_and_cache(file_path)
    df = pd.read_csv(cached_file)
    
    # Verificar e ajustar o formato do arquivo conforme necessário
    if 'FTHG' in df.columns:
        # Formato do primeiro arquivo
        df.rename(columns={
            'Date': 'Data',
            'HomeTeam': 'Home',
            'AwayTeam': 'Away',
            'FTHG': 'Gols_Home',
            'FTAG': 'Gols_Away',
            'FTR': 'Resultado',
            'PSCH': 'Odd_Home',
            'PSCD': 'Odd_Empate',
            'PSCA': 'Odd_Away'
        }, inplace=True)
    elif 'home_team_name' in df.columns:
        # Formato do terceiro arquivo
        df.rename(columns={
            'date_GMT': 'Data',
            'home_team_name': 'Home',
            'away_team_name': 'Away',
            'home_team_goal_count': 'Gols_Home',
            'away_team_goal_count': 'Gols_Away',
            'Res': 'Resultado',
            'odds_ft_home_team_win': 'Odd_Home',
            'odds_ft_draw': 'Odd_Empate',
            'odds_ft_away_team_win': 'Odd_Away'
        }, inplace=True)
        # Converter a coluna 'Data' para o formato 'dd/mm/yyyy'
        df['Data'] = df['Data'].apply(converter_data_gmt)
    else:
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

    # Convert 'Data' column to datetime format with error handling
    team_df['Data'] = pd.to_datetime(team_df['Data'], errors='coerce')

    # Remove rows with invalid dates (NaT)
    team_df = team_df.dropna(subset=['Data'])

    # Format 'Data' column for display
    team_df['Data'] = team_df['Data'].dt.strftime('%d/%m/%Y')

    st.write("### Resultados do Time da Casa:", time)
    st.write("#### Faixa de Odds:", odds_group)
    st.write(team_df)

if __name__ == "__main__":
    main()
