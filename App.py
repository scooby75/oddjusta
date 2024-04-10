import pandas as pd
from datetime import datetime
import streamlit as st
import os
import requests
from bd import file_paths  # Importando file_paths de bd.py

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

# Função para fazer o download de um arquivo e armazená-lo em cache
def download_and_cache(url, cache_folder="cache"):
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    
    cache_file = os.path.join(cache_folder, os.path.basename(url))
    
    if not os.path.exists(cache_file):
        response = requests.get(url)
        if response.status_code == 200:
            with open(cache_file, 'wb') as f:
                f.write(response.content)
        else:
            raise ValueError(f"Failed to download file from {url}")
    
    return cache_file

# Carregar os arquivos CSV
def load_dataframes(file_paths):
    dfs = []
    for file_path in file_paths:
        try:
            cached_file = download_and_cache(file_path)
            df = pd.read_csv(cached_file)
            dfs.append(df)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}") 

    return pd.concat(dfs, ignore_index=True)

def main():
    df = load_dataframes(file_paths)

    # Obter todas as equipes envolvidas nos jogos
    all_teams_home = set(df['Home'])
    all_teams_away = set(df['Away'])

    # Ordenar os times em ordem alfabética
    times_home = sorted(str(team) for team in all_teams_home)
    times_away = sorted(str(team) for team in all_teams_away)

    # Ordenar as faixas de odds
    odds_groups = sorted(df['Odd_Group'].unique())

    st.title("Odd Justa")
    st.sidebar.header("Filtros")
    team_type = st.sidebar.selectbox("Selecione qual deseja analisar:", options=["Home", "Away"])
    time = st.sidebar.selectbox(f"Selecione o Time {'da Casa' if team_type == 'Home' else 'Visitante'}:", options=times_home if team_type == "Home" else times_away)
    odds_column = 'Odd_Home' if team_type == "Home" else 'Odd_Away'
    
    # Selectbox para selecionar o intervalo de odds
    st.sidebar.subheader("Faixa de Odds")
    selected_odds_range = st.sidebar.selectbox("Selecione um intervalo de odds:", options=odds_groups)

    # Extrair os limites inferior e superior do intervalo selecionado
    if selected_odds_range == "Outros":
        min_odds, max_odds = -float('inf'), float('inf')  # Para o caso "Outros", significa que não há intervalo específico
    else:
        min_odds, max_odds = map(float, selected_odds_range.split(' - '))

    mostrar_resultados(df, team_type, time, odds_column, (min_odds, max_odds))

def mostrar_resultados(df, team_type, time, odds_column, odds_group):
    team_df = df[df['Home'] == time] if team_type == "Home" else df[df['Away'] == time]
    odds_col = 'Odd_Home' if team_type == "Home" else 'Odd_Away'
    
    # Aplicar o filtro de odds
    team_df = team_df[(team_df[odds_col] >= odds_group[0]) & (team_df[odds_col] <= odds_group[1])]

    # Reindexar o DataFrame para garantir que os índices estejam corretos após o filtro
    team_df.reset_index(drop=True, inplace=True)

    # Adicionar coluna de resultado com a lógica correta para o tipo de equipe selecionada
    team_df['Resultado'] = team_df.apply(lambda row: classificar_resultado(row, team_type), axis=1)
    
    # Selecionar apenas as colunas relevantes para exibição
    team_df = team_df[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Empate', 'Odd_Away', 'Gols_Home', 'Gols_Away', 'Resultado', 'Coeficiente_Eficiencia']]

    # Exibir o DataFrame resultante
    st.write("### Partidas:")
    st.dataframe(team_df)

    # Calcular estatísticas e exibir
    calcular_estatisticas_e_exibir(team_df, team_type, odds_column)

def calcular_estatisticas_e_exibir(team_df, team_type, odds_column):
    # Calcular estatísticas
    num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
    total_matches = team_df.shape[0]
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0
    lucro_prejuizo_total = team_df[odds_column].sum() - total_matches

    # Calcular médias
    media_gols = team_df['Gols_Home'].mean() if team_type == "Home" else team_df['Gols_Away'].mean()
    media_gols_sofridos = team_df['Gols_Away'].mean() if team_type == "Home" else team_df['Gols_Home'].mean()
    coeficiente_eficiencia_medio = team_df['Coeficiente_Eficiencia'].mean()

    # Calcular odd justa
    odd_justa = 100 / win_percentage if win_percentage > 0 else 0
    
    # Destacar resultados importantes usando markdown
    st.write("### Analise:")
    st.markdown(f"- Com as características do jogo de hoje, o {team_df['Home'].iloc[0] if team_type == 'Home' else team_df['Away'].iloc[0]} ganhou {num_wins} vez(es) em {total_matches} jogo(s), aproveitamento de ({win_percentage:.2f}%).")
    st.markdown(f"- Odd justa: {odd_justa:.2f}.")
    st.markdown(f"- Coeficiente de eficiência: {coeficiente_eficiencia_medio:.2f}.")
    st.markdown(f"- Lucro/prejuízo total: {lucro_prejuizo_total:.2f}.")
    st.markdown(f"- Média de gols marcados: {media_gols:.2f}.")
    st.markdown(f"- Média de gols sofridos: {media_gols_sofridos:.2f}.")

if __name__ == "__main__":
    main()
