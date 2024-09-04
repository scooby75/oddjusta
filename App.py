import pandas as pd
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
    elif team_type == "Away":
        if row['Gols_Away'] > row['Gols_Home']:
            return 'W'
        elif row['Gols_Away'] < row['Gols_Home']:
            return 'L'
        else:
            return 'D'
    else:
        return 'N/A'  # Para H2H, logic can be added here if needed

# Função para calcular o coeficiente de eficiência de acordo com o tipo de equipe selecionado
def calcular_coeficiente(row, team_type):
    try:
        if team_type == "Home":
            return row['Gols_Home'] - row['Gols_Away']
        elif team_type == "Away":
            return row['Gols_Away'] - row['Gols_Home']
    except Exception as e:
        st.error(f"Erro ao calcular o coeficiente: {e}")

# Função para agrupar odds em intervalos
def agrupar_odd(odd):
    lower = 1
    step = 0.06
    while lower <= 120:
        upper = lower + 0.05
        if lower <= odd < upper:
            return f"{lower:.2f} - {upper:.2f}"
        lower += step
    return 'Outros'

# Função para fazer o download de um arquivo e armazená-lo em cache
def download_and_cache(url):
    cache_folder = "cache"
    cache_file = os.path.join(cache_folder, os.path.basename(url))
    
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    
    if not os.path.exists(cache_file):
        response = requests.get(url)
        response.raise_for_status()  # Garante que erros na requisição sejam tratados
        with open(cache_file, 'wb') as f:
            f.write(response.content)
    
    return cache_file

# Carregar o arquivo CSV
try:
    cached_file = download_and_cache(file_paths[0])  # Supondo que haja apenas um arquivo
    df = pd.read_csv(cached_file, encoding='utf-8')  # Especificar a codificação UTF-8
    # Definir tipos de dados
    df['Gols_Home'] = pd.to_numeric(df['Gols_Home'], errors='coerce')
    df['Gols_Away'] = pd.to_numeric(df['Gols_Away'], errors='coerce')
except Exception as e:
    st.error(f"Erro ao processar o arquivo {file_paths[0]}: {e}")

# Adicionar coluna de resultado com a lógica correta para o tipo de equipe selecionado
df['Resultado'] = df.apply(lambda row: classificar_resultado(row, "Home"), axis=1)

# Adicionar coluna de agrupamento de odds
if 'Odd_Home' in df:
    df['Odd_Group'] = df['Odd_Home'].apply(agrupar_odd)
elif 'Odd_Away' in df:
    df['Odd_Group'] = df['Odd_Away'].apply(agrupar_odd)

# Remover linhas com valores nulos em 'Gols_Home' e 'Gols_Away'
df.dropna(subset=['Gols_Home', 'Gols_Away'], inplace=True)

# Converter valores para inteiros, tratando valores não numéricos como nulos
df['Gols_Home'] = df['Gols_Home'].astype(pd.Int64Dtype())
df['Gols_Away'] = df['Gols_Away'].astype(pd.Int64Dtype())

# Remover linhas com valores nulos após a conversão
df.dropna(subset=['Gols_Home', 'Gols_Away'], inplace=True)

# Adicionar coluna de placar no formato desejado (por exemplo, "2x0", "1x1", "1x2", etc.)
df['Placar'] = df['Gols_Home'].astype(str) + 'x' + df['Gols_Away'].astype(str)

# Obter todas as equipes envolvidas nos jogos
all_teams_home = set(df['Home'])
all_teams_away = set(df['Away'])

# Ordenar os times em ordem alfabética
times_home = sorted(str(team) for team in all_teams_home)
times_away = sorted(str(team) for team in all_teams_away)

# Ordenar as faixas de odds
odds_groups = sorted(df['Odd_Group'].unique())

# Função para calcular estatísticas e exibir resultados
def calcular_estatisticas_e_exibir(team_df, team_type, odds_column):
    placar_counts = team_df['Placar'].value_counts()
    total_eventos = placar_counts.sum()

    placar_df = pd.DataFrame({
        'Placar': placar_counts.index,
        'Frequencia': placar_counts.values
    })

    placar_df['Probabilidade (%)'] = (placar_df['Frequencia'] / total_eventos) * 100
    placar_df['Odd_Lay'] = 100 / placar_df['Probabilidade (%)']

    placar_df['Probabilidade (%)'] = placar_df['Probabilidade (%)'].round(2)
    placar_df['Odd_Lay'] = placar_df['Odd_Lay'].round(2)

    return placar_df

# Interface do Streamlit
def main():
    st.title("Odd Justa")
    st.sidebar.header("Filtros")
    team_type = st.sidebar.selectbox("Selecione qual deseja analisar:", options=["Home", "Away", "H2H"])
    
    if team_type == "H2H":
        time_home = st.sidebar.selectbox("Selecione o Time da Casa:", options=times_home)
        time_away = st.sidebar.selectbox("Selecione o Time Visitante:", options=times_away)
        mostrar_resultados_h2h(df, time_home, time_away)
    else:
        if team_type == "Home":
            time = st.sidebar.selectbox("Selecione o Time da Casa:", options=times_home)
            odds_column = 'Odd_Home'
        else:
            time = st.sidebar.selectbox("Selecione o Time Visitante:", options=times_away)
            odds_column = 'Odd_Away'
        
        # Selectbox para selecionar o intervalo de odds
        st.sidebar.subheader("Faixa de Odds")
        selected_odds_range = st.sidebar.selectbox("Selecione um intervalo de odds:", options=odds_groups)

        # Extrair os limites inferior e superior do intervalo selecionado
        if selected_odds_range == "Outros":
            min_odds, max_odds = -1, -1
        else:
            min_odds, max_odds = map(float, selected_odds_range.split(' - '))

        mostrar_resultados(df, team_type, time, odds_column, (min_odds, max_odds))

def mostrar_resultados(df, team_type, time, odds_column, odds_group):
    if team_type == "Home":
        team_df = df[df['Home'] == time]
    else:
        team_df = df[df['Away'] == time]
    
    # Aplicar o filtro de odds
    if odds_group[0] == -1 and odds_group[1] == -1:
        team_df = team_df[(team_df[odds_column] < odds_group[0]) | (team_df[odds_column] > odds_group[1])]
    else:
        team_df = team_df[(team_df[odds_column] >= odds_group[0]) & (team_df[odds_column] <= odds_group[1])]

    if team_df.empty:
        st.write(f"Nenhum dado disponível para o time {time} com as odds selecionadas.")
        return
    
    placar_df = calcular_estatisticas_e_exibir(team_df, team_type, odds_column)
    st.dataframe(placar_df)

def mostrar_resultados_h2h(df, home_team, away_team):
    h2h_df = df[((df['Home'] == home_team) & (df['Away'] == away_team)) | ((df['Home'] == away_team) & (df['Away'] == home_team))]
    if h2h_df.empty:
        st.write(f"Não existem partidas entre {home_team} e {away_team}.")
        return

    # Calcular e exibir as estatísticas de H2H
    placar_df = calcular_estatisticas_e_exibir(h2h_df, 'H2H', 'Odd_Home')  # 'Odd_Home' usado como placeholder
    st.dataframe(placar_df)

if __name__ == "__main__":
    main()
