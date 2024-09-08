import pandas as pd
import streamlit as st
import os
import requests
from bd import file_paths

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
        print(f"Erro ao calcular o coeficiente: {e}")

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
        response = requests.get(url)
        with open(cache_file, 'wb') as f:
            f.write(response.content)
    
    return cache_file

def main():
    st.title("Odd Justa")
    st.sidebar.header("Filtros")
    
    try:
        cached_file = download_and_cache(file_paths[0])
        df = pd.read_csv(cached_file, encoding='utf-8')
    except Exception as e:
        st.error(f"Erro ao processar o arquivo {file_paths[0]}: {e}")
        return

    df['Resultado'] = df.apply(lambda row: classificar_resultado(row, "Home"), axis=1)

    if 'Odd_Home' in df:
        df['Odd_Group'] = df['Odd_Home'].apply(agrupar_odd)
    elif 'Odd_Away' in df:
        df['Odd_Group'] = df['Odd_Away'].apply(agrupar_odd')

    df.dropna(subset=['Gols_Home', 'Gols_Away'], inplace=True)
    df['Gols_Home'] = pd.to_numeric(df['Gols_Home'], errors='coerce').astype(pd.Int64Dtype())
    df['Gols_Away'] = pd.to_numeric(df['Gols_Away'], errors='coerce').astype(pd.Int64Dtype())
    df.dropna(subset=['Gols_Home', 'Gols_Away'], inplace=True)
    df['Placar'] = df['Gols_Home'].astype(str) + 'x' + df['Gols_Away'].astype(str)

    all_teams_home = set(df['Home'])
    all_teams_away = set(df['Away'])
    times_home = sorted(str(team) for team in all_teams_home)
    times_away = sorted(str(team) for team in all_teams_away)
    odds_groups = sorted(df['Odd_Group'].unique())

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

    num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
    num_draws = team_df[team_df['Resultado'] == 'D'].shape[0]
    num_losses = team_df[team_df['Resultado'] == 'L'].shape[0]
    total_matches = num_wins + num_draws + num_losses
    
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0
    lucro_prejuizo = (num_wins * team_df[odds_col].mean()) - total_matches if total_matches > 0 else 0
    odd_justa_wins = 100 / win_percentage if win_percentage > 0 else 0
    num_wins_draws = num_wins + num_draws
    win_draw_percentage = (num_wins_draws / total_matches) * 100 if total_matches > 0 else 0
    odd_justa_wins_draws = 100 / win_draw_percentage if win_draw_percentage > 0 else 0
    coeficiente_eficiencia_medio = team_df['Coeficiente_Eficiencia'].mean() if not team_df['Coeficiente_Eficiencia'].empty else 0
    media_gols = team_df['Gols_Home'].mean() if not team_df['Gols_Home'].empty else 0
    media_gols_sofridos = team_df['Gols_Away'].mean() if not team_df['Gols_Away'].empty else 0
    
    placar_df = calcular_estatisticas_e_exibir(team_df, team_type, odds_column)

    st.subheader(f"Resultados de {time} ({team_type}):")
    st.write(f"Total de Partidas: {total_matches}")
    st.write(f"Vitórias: {num_wins} ({win_percentage:.2f}%)")
    st.write(f"Empates: {num_draws}")
    st.write(f"Derrotas: {num_losses}")
    st.write(f"Lucro/Prejuízo Médio: {lucro_prejuizo:.2f}")
    st.write(f"Odd Justa para Vitória: {odd_justa_wins:.2f}")
    st.write(f"Odd Justa para Vitória/Empate: {odd_justa_wins_draws:.2f}")
    st.write(f"Coeficiente de Eficiência Médio: {coeficiente_eficiencia_medio:.2f}")
    st.write(f"Média de Gols Marcados: {media_gols:.2f}")
    st.write(f"Média de Gols Sofridos: {media_gols_sofridos:.2f}")
    st.write(placar_df)

def mostrar_resultados_h2h(df, time_home, time_away):
    df_h2h = df[((df['Home'] == time_home) & (df['Away'] == time_away)) |
                ((df['Home'] == time_away) & (df['Away'] == time_home))]
    
    if df_h2h.empty:
        st.write(f"Não existem partidas entre {time_home} e {time_away}.")
    else:
        stats_home = df_h2h[df_h2h['Home'] == time_home]
        stats_away = df_h2h[df_h2h['Away'] == time_home]
        total_matches = df_h2h.shape[0]
        
        num_wins_home = stats_home[stats_home['Resultado'] == 'W'].shape[0]
        num_wins_away = stats_away[stats_away['Resultado'] == 'W'].shape[0]
        num_draws = df_h2h[df_h2h['Resultado'] == 'D'].shape[0]
        
        st.write(f"Resultados de Confronto Direto entre {time_home} e {time_away}:")
        st.write(f"Vitórias do {time_home}: {num_wins_home}")
        st.write(f"Vitórias do {time_away}: {num_wins_away}")
        st.write(f"Empates: {num_draws}")
        
        placar_comum = df_h2h.groupby(['Gols_Home', 'Gols_Away']).size().idxmax()
        st.write(f"Placar Mais Comum: {placar_comum[0]}x{placar_comum[1]}")
        
        tempos_primeiro_gol = df_h2h[df_h2h['Gols_Home'] > 0]['Gols_Home'].value_counts()
        st.write(f"Tempos para o Primeiro Gol: {tempos_primeiro_gol.to_dict()}")

if __name__ == "__main__":
    main()
