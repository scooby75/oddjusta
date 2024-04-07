import pandas as pd
from datetime import datetime
import streamlit as st
import os
import requests
from bd import file_paths  # Importing file_paths from bd.py

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
all_teams_away = set(df['Away'])

# Ordenar os times em ordem alfabética
times_home = sorted(str(team) for team in all_teams_home)
times_away = sorted(str(team) for team in all_teams_away)

# Ordenar as faixas de odds
odds_groups = sorted(df['Odd_Group'].unique())

# Interface do Streamlit
def main():
    st.title("Winrate Odds")
    st.sidebar.header("Filtros")
    team_type = st.sidebar.selectbox("Selecione o Tipo de Time:", options=["Home", "Away"])
    if team_type == "Home":
        time = st.sidebar.selectbox("Selecione o Time da Casa:", options=times_home)
    else:
        time = st.sidebar.selectbox("Selecione o Time Visitante:", options=times_away)
    odds_group = st.sidebar.selectbox("Selecione a Faixa de Odds:", options=odds_groups)
    mostrar_resultados(team_type, time, odds_group)

def mostrar_resultados(tipo_time, time, faixa_odds):
    if faixa_odds == "Outros":
        odds_filtradas = df[df['Odd_Group'].apply(lambda x: float(x.split()[0])) < 1.0]
        odds_filtradas = pd.concat([odds_filtradas, df[df['Odd_Group'].apply(lambda x: float(x.split()[-1])) > 6.0]])
    else:
        odds_filtradas = df[df['Odd_Group'] == faixa_odds]

    if tipo_time == "Casa":
        df_time = odds_filtradas[odds_filtradas['Home'] == time]
    else:
        df_time = odds_filtradas[odds_filtradas['Away'] == time]

    df_time = df_time[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Empate', 'Odd_Away', 'Gols_Home', 'Gols_Away', 'Resultado', 'Coeficiente_Eficiencia']]

    # Remover linhas duplicadas
    df_time = df_time.drop_duplicates()

    # Converter coluna 'Data' para o formato datetime com tratamento de erro
    df_time['Data'] = pd.to_datetime(df_time['Data'], errors='coerce')

    # Remover linhas com datas inválidas (NaT)
    df_time = df_time.dropna(subset=['Data'])

    # Formatar coluna 'Data' para exibição
    df_time['Data'] = df_time['Data'].dt.strftime('%d-%m-%Y')

    # Exibir resultados em uma tabela
    st.write("### Partidas:")
    st.dataframe(df_time)

    # Calcular quantas vezes o time da casa ganhou
    num_vitorias = df_time[df_time['Resultado'] == 'V'].shape[0]
    total_partidas = df_time.shape[0]
    porcentagem_vitorias = (num_vitorias / total_partidas) * 100 if total_partidas > 0 else 0

    # Calcular lucro/prejuízo total
    df_time['Lucro_Prejuizo'] = df_time.apply(lambda row: row['Odd_Home'] - 1 if row['Resultado'] == 'V' else -1, axis=1)
    lucro_prejuizo_total = df_time['Lucro_Prejuizo'].sum()

    # Calcular médias
    media_gols_casa = df_time['Gols_Home'].mean()
    media_gols_sofridos = df_time['Gols_Away'].mean()
    
    # Calcular coeficiente de eficiência médio ajustado
    coeficiente_eficiencia_total = df_time['Coeficiente_Eficiencia'].sum()
    coeficiente_eficiencia_medio = coeficiente_eficiencia_total / total_partidas if total_partidas > 0 else 0

    # Calcular odd justa
    odd_justa = 100 / porcentagem_vitorias if porcentagem_vitorias > 0 else 0
    
    # Destacar resultados importantes usando markdown
    st.write("### Resumo:")
    if tipo_time == "Casa":
        st.markdown(f"- Com as características do jogo de hoje, o {time} ganhou {num_vitorias} vez(es) em {total_partidas} partida(s), aproveitamento de ({porcentagem_vitorias:.2f}%).")
    else:
        st.markdown(f"- Com as características do jogo de hoje, o time visitante {time} ganhou {num_vitorias} vez(es) em {total_partidas} partida(s), aproveitamento de ({porcentagem_vitorias:.2f}%).")
    st.markdown(f"- Odd justa: {odd_justa:.2f}.")
    st.markdown(f"- Coeficiente de eficiência: {coeficiente_eficiencia_medio:.2f}.")
    st.markdown(f"- Lucro/prejuízo total: {lucro_prejuizo_total:.2f}.")
    st.markdown(f"- Média de gols marcados pelo time da casa: {media_gols_casa:.2f}.")
    st.markdown(f"- Média de gols sofridos pelo time visitante: {media_gols_sofridos:.2f}.")

if __name__ == "__main__":
    main()
