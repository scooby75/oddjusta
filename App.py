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
    else:  # Caso seja "Away"
        if row['Gols_Away'] > row['Gols_Home']:
            return 'W'
        elif row['Gols_Away'] < row['Gols_Home']:
            return 'L'
        else:
            return 'D'

# Função para calcular o lucro/prejuízo por jogo com base no resultado e na odd_home
def calcular_lucro_por_jogo(row):
    if row['Resultado'] == 'W':
        return row['Odd_Home'] - 1
    elif row['Resultado'] == 'D' or row['Resultado'] == 'L':
        return -1
    else:
        return 0

# Função para agrupar a odd em intervalos
def agrupar_odd(odd):
    for i in range(0, 120):  # Itera através de uma faixa de valores
        lower = 1 + i * 0.06  # Calcula o limite inferior do intervalo
        upper = lower + 0.05  # Calcula o limite superior do intervalo
        if lower <= odd <= upper:  # Verifica se a odd está dentro do intervalo
            return f"{lower:.2f} - {upper:.2f}"  # Formata e retorna o intervalo
    return 'Outros'  # Se a odd não se encaixar em nenhum intervalo pré-definido, retorna 'Outros'

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

# Função para calcular o coeficiente de eficiência
def calcular_coeficiente(row, team_type):
    if team_type == "Home":
        return row['Gols_Home'] / row['Gols_Away'] if row['Gols_Away'] != 0 else 0
    else:
        return row['Gols_Away'] / row['Gols_Home'] if row['Gols_Home'] != 0 else 0

# Carregar o arquivo CSV
try:
    cached_file = download_and_cache(file_paths[0])  # Supondo que haja apenas um arquivo
    df = pd.read_csv(cached_file, encoding='utf-8')  # Especificar a codificação UTF-8
except Exception as e:
    st.error(f"Erro ao processar o arquivo {file_paths[0]}: {e}")

# Adicionar coluna de resultado com a lógica correta para o tipo de equipe selecionada
df['Resultado'] = df.apply(lambda row: classificar_resultado(row, "Home"), axis=1)

# Adicionar coluna de agrupamento de odds
if 'Odd_Home' in df:
    df['Odd_Group'] = df['Odd_Home'].apply(agrupar_odd)
elif 'Odd_Away' in df:
    df['Odd_Group'] = df['Odd_Away'].apply(agrupar_odd)

# Remover linhas com valores nulos em 'Gols_Home' e 'Gols_Away'
df.dropna(subset=['Gols_Home', 'Gols_Away'], inplace=True)

# Converter valores para inteiros, tratando valores não numéricos como nulos
df['Gols_Home'] = pd.to_numeric(df['Gols_Home'], errors='coerce').astype(pd.Int64Dtype())
df['Gols_Away'] = pd.to_numeric(df['Gols_Away'], errors='coerce').astype(pd.Int64Dtype())

# Remover linhas com valores nulos após a conversão
df.dropna(subset=['Gols_Home', 'Gols_Away'], inplace=True)

# Adicionar coluna de placar no formato desejado (por exemplo, "2x0", "1x1", "1x2", etc.)
df['Placar'] = df['Gols_Home'].astype(str) + 'x' + df['Gols_Away'].astype(str)

# Calcular lucro/prejuízo por jogo
df['Lucro_Por_Jogo'] = df.apply(calcular_lucro_por_jogo, axis=1)

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
    analysis_type = st.sidebar.selectbox("Selecione o tipo de análise:", options=["Padrão", "Head to Head (H2H)"])
    
    if analysis_type == "Padrão":
        team_type = st.sidebar.selectbox("Selecione qual deseja analisar:", options=["Home", "Away"])
        if team_type == "Home":
            time = st.sidebar.selectbox("Selecione o Time da Casa:", options=times_home)
            odds_column = 'Odd_Home'  # Selecionar a coluna de odds correspondente
        else:
            time = st.sidebar.selectbox("Selecione o Time Visitante:", options=times_away)
            odds_column = 'Odd_Away'  # Selecionar a coluna de odds correspondente
        
        # Selectbox para selecionar o intervalo de odds
        st.sidebar.subheader("Faixa de Odds")
        selected_odds_range = st.sidebar.selectbox("Selecione um intervalo de odds:", options=odds_groups)

        # Extrair os limites inferior e superior do intervalo selecionado
        if selected_odds_range == "Outros":
            min_odds, max_odds = -1, -1  # Para o caso "Outros", significa que não há intervalo específico
        else:
            min_odds, max_odds = map(float, selected_odds_range.split(' - '))

        mostrar_resultados(team_type, time, odds_column, (min_odds, max_odds))
    
    elif analysis_type == "Head to Head (H2H)":
        time_home = st.sidebar.selectbox("Selecione o Time da Casa:", options=times_home)
        time_away = st.sidebar.selectbox("Selecione o Time Visitante:", options=times_away)
        mostrar_h2h(time_home, time_away)

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
    
    # Aplicar o filtro de odds
    if odds_group[0] == -1 and odds_group[1] == -1:  # Se a opção for "Outros"
        # Selecionar jogos em que as odds não estejam dentro do range selecionado
        team_df = team_df[(team_df[odds_col] < odds_group[0]) | (team_df[odds_col] > odds_group[1])]
    else:
        team_df = team_df[(team_df[odds_col] >= odds_group[0]) & (team_df[odds_col] <= odds_group[1])]

    # Reindexar o DataFrame para garantir que os índices estejam corretos após o filtro
    team_df.reset_index(drop=True, inplace=True)

    # Remover duplicatas após aplicar o filtro
    team_df.drop_duplicates(inplace=True)

    # Adicionar coluna de resultado com a lógica correta para o tipo de equipe selecionada
    team_df['Resultado'] = team_df.apply(lambda row: classificar_resultado(row, team_type), axis=1)
    
    # Adicionar coluna de coeficiente de eficiência se não existir
    if 'Gols_Home' in team_df.columns and 'Gols_Away' in team_df.columns:
        team_df['Coeficiente_Eficiencia'] = team_df.apply(lambda row: calcular_coeficiente(row, team_type), axis=1)

    st.header(f"Estatísticas do {time} - {team_type}")

    # Mostrar DataFrame com os dados filtrados e processados
    st.write(team_df)

    # Calcular e exibir estatísticas adicionais se a coluna de coeficiente de eficiência existir
    if 'Coeficiente_Eficiencia' in team_df.columns:
        coeficiente_eficiencia_medio = team_df['Coeficiente_Eficiencia'].mean()
        st.write(f"Coeficiente de Eficiência Médio: {coeficiente_eficiencia_medio:.2f}")

def mostrar_h2h(time_home, time_away):
    # Filtrar jogos onde o time da casa e o time visitante são os selecionados
    h2h_df = df[(df['Home'] == time_home) & (df['Away'] == time_away)]
    
    st.header(f"Head to Head entre {time_home} (Casa) vs {time_away} (Visitante)")

    # Mostrar DataFrame com os jogos selecionados
    st.write(h2h_df)

    # Calcular estatísticas do head to head
    num_wins = h2h_df[h2h_df['Resultado'] == 'W'].shape[0]
    total_matches = h2h_df.shape[0]
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0

    # Adicionar análises destacadas usando Markdown
    st.write("### Análise:")
    if not h2h_df.empty:
        st.markdown(f"- Com as características do jogo de hoje, o {time_home} ganhou {num_wins} vez(es) em {total_matches} jogo(s), aproveitamento de ({win_percentage:.2f}%).")
    else:
        st.write("Nenhum jogo encontrado para os filtros selecionados.")

# Chamada para iniciar o aplicativo
if __name__ == "__main__":
    main()
