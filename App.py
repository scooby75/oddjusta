import pandas as pd
import streamlit as st
import os
import requests
from bd import file_paths

# Funções para processamento
def classificar_resultado(row, team_type):
    if team_type == "Home":
        if row['Gols_Home'] > row['Gols_Away']:
            return 'W'
        elif row['Gols_Home'] < row['Gols_Away']:
            return 'L'
        else:
            return 'D'
    else:
        if row['Gols_Away'] > row['Gols_Home']:
            return 'W'
        elif row['Gols_Away'] < row['Gols_Home']:
            return 'L'
        else:
            return 'D'

def calcular_coeficiente(row, team_type):
    try:
        if team_type == "Home":
            return row['Gols_Home'] - row['Gols_Away']
        else:
            return row['Gols_Away'] - row['Gols_Home']
    except Exception as e:
        st.error(f"Erro ao calcular o coeficiente: {e}")

def agrupar_odd(odd):
    for i in range(0, 120):
        lower = 1 + i * 0.06
        upper = lower + 0.05
        if lower <= odd <= upper:
            return f"{lower:.2f} - {upper:.2f}"
    return 'Outros'

def download_and_cache(url):
    cache_folder = "cache"
    cache_file = os.path.join(cache_folder, os.path.basename(url))
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    if not os.path.exists(cache_file):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Adiciona verificação de status HTTP
            with open(cache_file, 'wb') as f:
                f.write(response.content)
        except requests.RequestException as e:
            st.error(f"Erro ao baixar o arquivo: {e}")
            return None
    return cache_file

# Carregar o arquivo CSV
try:
    cached_file = download_and_cache(file_paths[0])
    if cached_file:
        df = pd.read_csv(cached_file, encoding='utf-8')
except Exception as e:
    st.error(f"Erro ao processar o arquivo {file_paths[0]}: {e}")

# Processar e exibir dados
if 'df' in locals():
    df['Resultado'] = df.apply(lambda row: classificar_resultado(row, "Home"), axis=1)

    if 'Odd_Home' in df.columns:
        df['Odd_Group'] = df['Odd_Home'].apply(agrupar_odd)
    elif 'Odd_Away' in df.columns:
        df['Odd_Group'] = df['Odd_Away'].apply(agrupar_odd)

    if 'Gols_Home' in df.columns and 'Gols_Away' in df.columns:
        df['Gols_Home'] = pd.to_numeric(df['Gols_Home'], errors='coerce').astype(pd.Int64Dtype())
        df['Gols_Away'] = pd.to_numeric(df['Gols_Away'], errors='coerce').astype(pd.Int64Dtype())
        df.dropna(subset=['Gols_Home', 'Gols_Away'], inplace=True)

    df['Placar'] = df['Gols_Home'].astype(str) + 'x' + df['Gols_Away'].astype(str)

    all_teams_home = set(df['Home'])
    all_teams_away = set(df['Away'])
    times_home = sorted(str(team) for team in all_teams_home)
    times_away = sorted(str(team) for team in all_teams_away)
    odds_groups = sorted(df['Odd_Group'].unique())

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
            
            st.sidebar.subheader("Faixa de Odds")
            selected_odds_range = st.sidebar.selectbox("Selecione um intervalo de odds:", options=odds_groups)

            if selected_odds_range == "Outros":
                min_odds, max_odds = -1, -1
            else:
                min_odds, max_odds = map(float, selected_odds_range.split(' - '))

            mostrar_resultados(df, team_type, time, odds_column, (min_odds, max_odds))

    def mostrar_resultados(df, team_type, time, odds_column, odds_group):
        if team_type == "Home":
            team_df = df[df['Home'] == time]
            odds_col = 'Odd_Home'
        else:
            team_df = df[df['Away'] == time]
            odds_col = 'Odd_Away'

        if odds_group[0] == -1 and odds_group[1] == -1:
            team_df = team_df[(team_df[odds_col] < odds_group[0]) | (team_df[odds_col] > odds_group[1])]
        else:
            team_df = team_df[(team_df[odds_col] >= odds_group[0]) & (team_df[odds_col] <= odds_group[1])]

        team_df.reset_index(drop=True, inplace=True)
        team_df['Coeficiente_Eficiencia'] = team_df.apply(lambda row: calcular_coeficiente(row, team_type), axis=1)

        st.write(f"### Resultados para o time {time} como {team_type}:")
        st.dataframe(team_df[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Away', 'Gols_Home', 'Gols_Away', 'Resultado', 'Coeficiente_Eficiencia', 'Placar']])
        
        calcular_estatisticas_e_exibir(team_df, team_type, odds_column)

    def mostrar_resultados_h2h(df, time_home, time_away):
        h2h_df = df[(df['Home'] == time_home) & (df['Away'] == time_away)]

        if h2h_df.empty:
            st.write("Não existem partidas entre as equipes.")
        else:
            columns_to_display = df.columns
            st.write("### Partidas H2H:")
            st.dataframe(h2h_df[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Away', 'Gols_Home', 'Gols_Away', 'Resultado', 'Placar']])
            
            calcular_estatisticas_e_exibir(h2h_df, 'H2H', 'Odd_Home')

    def calcular_estatisticas_e_exibir(df, team_type, odds_column):
        if not df.empty:
            # Estatísticas básicas
            st.write(f"### Estatísticas para {team_type}")
            st.write(f"Número de partidas: {df.shape[0]}")
            st.write(f"Total de vitórias: {df['Resultado'].str.count('W').sum()}")
            st.write(f"Total de empates: {df['Resultado'].str.count('D').sum()}")
            st.write(f"Total de derrotas: {df['Resultado'].str.count('L').sum()}")

            # Cálculo de lucro/prejuízo e odds justas
            try:
                df['Expected_Payout'] = (df[odds_column] - 1) * (df['Resultado'] == 'W')
                df['Total_Profit'] = df['Expected_Payout'].sum()
                st.write(f"Lucro/Prejuízo Total: {df['Total_Profit'].sum():.2f}")
            except Exception as e:
                st.error(f"Erro ao calcular lucro/prejuízo: {e}")

    main()
