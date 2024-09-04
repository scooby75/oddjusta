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

# Função para calcular o coeficiente de eficiência de acordo com o tipo de equipe selecionado
def calcular_coeficiente(row, team_type):
    try:
        if team_type == "Home":
            diferenca_gols = row['Gols_Home'] - row['Gols_Away']
        else:  # Se for "Away"
            diferenca_gols = row['Gols_Away'] - row['Gols_Home']
        return diferenca_gols
    except Exception as e:
        print(f"Erro ao calcular o coeficiente: {e}")

# Função para agrupar odds em intervalos
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

# Carregar o arquivo CSV
try:
    cached_file = download_and_cache(file_paths[0])  # Supondo que haja apenas um arquivo
    df = pd.read_csv(cached_file, encoding='utf-8')  # Especificar a codificação UTF-8
except Exception as e:
    st.error(f"Erro ao processar o arquivo {file_paths[0]}: {e}")

# Adicionar coluna de resultado com a lógica correta para o tipo de equipe selecionado
df['Resultado'] = df.apply(lambda row: classificar_resultado(row, "Home"), axis=1)

# Adicionar coluna de agrupamento de odds
if 'Odd_Home' in df.columns:
    df['Odd_Group'] = df['Odd_Home'].apply(agrupar_odd)
elif 'Odd_Away' in df.columns:
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
    team_type = st.sidebar.selectbox("Selecione qual deseja analisar:", options=["Home", "Away", "H2H"])
    
    if team_type == "H2H":
        time_home = st.sidebar.selectbox("Selecione o Time da Casa:", options=times_home)
        time_away = st.sidebar.selectbox("Selecione o Time Visitante:", options=times_away)
        mostrar_resultados_h2h(df, time_home, time_away)
    else:
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

        mostrar_resultados(df, team_type, time, odds_column, (min_odds, max_odds))

def mostrar_resultados(df, team_type, time, odds_column, odds_group):
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

    # Reindexar o DataFrame resultante após a filtragem
    team_df.reset_index(drop=True, inplace=True)

    # Calcular o coeficiente de eficiência para cada jogo
    team_df['Coeficiente_Eficiencia'] = team_df.apply(lambda row: calcular_coeficiente(row, team_type), axis=1)

    # Mostrar os resultados na interface do Streamlit
    st.write(f"### Resultados para o time {time} como {team_type}:")
    st.dataframe(team_df[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Away', 'Gols_Home', 'Gols_Away', 'Resultado', 'Coeficiente_Eficiencia', 'Placar']])
    
    calcular_estatisticas_e_exibir(team_df, team_type, odds_column)

def mostrar_resultados_h2h(df, time_home, time_away):
    # Filtrar DataFrame para exibir apenas confrontos diretos entre as equipes selecionadas
    h2h_df = df[(df['Home'] == time_home) & (df['Away'] == time_away)]

    if h2h_df.empty:
        st.write("Não existem partidas entre as equipes.")
    else:
        # Verificar se todas as colunas estão presentes no DataFrame h2h_df antes de acessá-las
        columns_to_display = df.columns

        # Mostrar os resultados na interface do Streamlit
        st.write("### Partidas H2H:")
        st.dataframe(h2h_df[columns_to_display])
        
        # Calcular o coeficiente de eficiência para cada jogo em H2H
        h2h_df['Coeficiente_Eficiencia'] = h2h_df.apply(lambda row: calcular_coeficiente(row, "Home"), axis=1)

        calcular_estatisticas_e_exibir(h2h_df, "H2H", None)

def calcular_estatisticas_e_exibir(df, team_type, odds_column):
    # Cálculo da média de gols marcados e sofridos
    media_gols_marcados = df['Gols_Home'].mean() if team_type == "Home" else df['Gols_Away'].mean()
    media_gols_sofridos = df['Gols_Away'].mean() if team_type == "Home" else df['Gols_Home'].mean()

    st.write(f"#### Estatísticas para o time como {team_type}:")
    st.write(f"Média de gols marcados: {media_gols_marcados:.2f}")
    st.write(f"Média de gols sofridos: {media_gols_sofridos:.2f}")

    # Cálculo de outras estatísticas e exibição
    if odds_column:
        st.write(f"Odds média: {df[odds_column].mean():.2f}")
        st.write(f"Coeficiente de eficiência médio: {df['Coeficiente_Eficiencia'].mean():.2f}")

# Executar a função principal
if __name__ == "__main__":
    main()
