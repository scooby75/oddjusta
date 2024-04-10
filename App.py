import pandas as pd
from datetime import datetime
import streamlit as st
import os
import requests
from bd import file_paths  # Importing file_paths from bd.py

# Função para classificar o resultado com base nos gols das equipes da casa e visitantes
def classificar_resultado(row, team_type):
    if team_type == "Home":
        if row['Gols_Home'] > row['Gols_Away']:
            return 'W'
        elif row['Gols_Home'] < row['Gols_Away']:
            return 'L'
        else:
            return 'D'
    else:  # Caso seja "Away"
        if row['Gols_Away'] > row['Gols_Home']:
            return 'W'
        elif row['Gols_Away'] < row['Gols_Home']:
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

# Carregar os arquivos CSV
dfs = []
for file_path in file_paths:
    try:
        cached_file = download_and_cache(file_path)
        df = pd.read_csv(cached_file)
        dfs.append(df)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

    
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

    # Adicionar coluna de resultado com a lógica correta para o tipo de equipe selecionada
    df['Resultado'] = df.apply(lambda row: classificar_resultado(row, "Home"), axis=1)
    
    # Calcular coeficiente de eficiência da equipe da casa
    df['Coeficiente_Eficiencia'] = df.apply(calcular_coeficiente, axis=1)

    # Adicionar coluna de agrupamento de odds
    if 'Odd_Home' in df:
        if team_type == "Home":
            df['Odd_Group'] = df['Odd_Home'].apply(agrupar_odd)
    elif 'Odd_Away' in df:
        if team_type == "Away":
            df['Odd_Group'] = df['Odd_Away'].apply(agrupar_odd)
    
    dfs.append(df)

# Concatenar todos os dataframes
df = pd.concat(dfs)

# Obter todas as equipes envolvidas nos jogos
all_teams_home = set(df['Home'])
all_teams_away = set(df['Away'])

# Ordenar os times em ordem alfabética
times_home = sorted(str(team) for team in all_teams_home)
times_away = sorted(str(team) for team in all_teams_away)

# Ordenar as faixas de odds
odds_groups = sorted(df['Odd_Group'].unique())

# Interface do Streamlit
def main():
    st.title("Odd Justa")
    st.sidebar.header("Filtros")
    team_type = st.sidebar.selectbox("Selecione qual deseja analisar:", options=["Home", "Away"])
    if team_type == "Home":
        time = st.sidebar.selectbox("Selecione o Time da Casa:", options=times_home)
        odds_column = 'Odd_Home'  # Selecionar a coluna de odds correspondente
    else:
        time = st.sidebar.selectbox("Selecione o Time Visitante:", options=times_away)
        odds_column = 'Odd_Away'  # Selecionar a coluna de odds correspondente
    odds_group = st.sidebar.selectbox("Selecione a Faixa de Odds:", options=odds_groups)
    
    # Verificar se a opção selecionada não é "Outros"
    if odds_group != "Outros":
        odds_group_values = [float(val) for val in odds_group.split(" - ")]  # Converter string de faixa de odds em lista de valores numéricos
    else:
        odds_group_values = [-1, -1]  # Define um valor especial para indicar que a opção é "Outros"
    
    mostrar_resultados(team_type, time, odds_column, odds_group_values)

def mostrar_resultados(team_type, time, odds_column, odds_group):
    if team_type == "Home":
        team_df = df[df['Home'] == time]
        odds_col = 'Odd_Home'
        team_name_col = 'Home'
        opponent_name_col = 'Away'
    else:
        team_df = df[df['Away'] == time]
        odds_col = 'Odd_Away'
        team_name_col = 'Away'
        opponent_name_col = 'Home'
    
    if odds_group[0] == -1 and odds_group[1] == -1:  # Se a opção for "Outros"
        # Selecionar jogos em que as odds não estejam dentro do range selecionado
        team_df = team_df[(team_df[odds_col] < odds_group[0]) | (team_df[odds_col] > odds_group[1])]
    else:
        team_df = team_df[(team_df[odds_col] >= odds_group[0]) & (team_df[odds_col] <= odds_group[1])]
    
    # Adicionar coluna de resultado com a lógica correta para o tipo de equipe selecionada
    team_df['Resultado'] = team_df.apply(lambda row: classificar_resultado(row, team_type), axis=1)
    
    team_df = team_df[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Empate', 'Odd_Away', 'Gols_Home', 'Gols_Away', 'Resultado', 'Coeficiente_Eficiencia']]

    # Drop duplicate rows
    team_df = team_df.drop_duplicates()

    # Convert 'Data' column to datetime format with error handling
    team_df['Data'] = pd.to_datetime(team_df['Data'], errors='coerce')

    # Remove rows with invalid dates (NaT)
    team_df = team_df.dropna(subset=['Data'])

    # Format 'Data' column for display
    team_df['Data'] = team_df['Data'].dt.strftime('%d-%m-%Y')

    # Exibir resultados em uma tabela
    st.write("### Partidas:")
    st.dataframe(team_df)

    # Calcular quantas vezes o time ganhou
    num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
    total_matches = team_df.shape[0]
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0

    # Calcular lucro/prejuízo total
    team_df['Lucro_Prejuizo'] = team_df.apply(lambda row: row[odds_column] - 1 if row['Resultado'] == 'W' else -1, axis=1)
    lucro_prejuizo_total = team_df['Lucro_Prejuizo'].sum()

    # Calcular médias
    media_gols = team_df['Gols_Home'].mean() if team_type == "Home" else team_df['Gols_Away'].mean()
    media_gols_sofridos = team_df['Gols_Away'].mean() if team_type == "Home" else team_df['Gols_Home'].mean()
    
    # Calcular coeficiente de eficiência médio ajustado
    coeficiente_eficiencia_total = team_df['Coeficiente_Eficiencia'].sum()
    coeficiente_eficiencia_medio = coeficiente_eficiencia_total / total_matches if total_matches > 0 else 0

    # Calcular odd justa
    odd_justa = 100 / win_percentage if win_percentage > 0 else 0
    
    # Destacar resultados importantes usando markdown
    st.write("### Analise:")
    st.markdown(f"- Com as características do jogo de hoje, o {time} ganhou {num_wins} vez(es) em {total_matches} jogo(s), aproveitamento de ({win_percentage:.2f}%).")
    st.markdown(f"- Odd justa: {odd_justa:.2f}.")
    st.markdown(f"- Coeficiente de eficiência: {coeficiente_eficiencia_medio:.2f}.")
    st.markdown(f"- Lucro/prejuízo total: {lucro_prejuizo_total:.2f}.")
    st.markdown(f"- Média de gols marcados: {media_gols:.2f}.")
    st.markdown(f"- Média de gols sofridos: {media_gols_sofridos:.2f}.")

if __name__ == "__main__":
    main()
