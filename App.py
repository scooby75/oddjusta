import pandas as pd
import streamlit as st
import os
import requests
import plotly.graph_objects as go

from bd import file_paths  # Importando file_paths de bd.py

# Função para carregar e preparar os dados
def load_data():
    cached_file = download_and_cache(file_paths[0])  # Supondo que haja apenas um arquivo
    df = pd.read_csv(cached_file, encoding='utf-8')  # Especificar a codificação UTF-8
    
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
    
    return df

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

# Função para agrupar odds em faixas
def agrupar_odd(odd):
    for i in range(0, 120):  # Itera através de uma faixa de valores
        lower = 1 + i * 0.06  # Calcula o limite inferior do intervalo
        upper = lower + 0.05  # Calcula o limite superior do intervalo
        if lower <= odd <= upper:  # Verifica se a odd está dentro do intervalo
            return f"{lower:.2f} - {upper:.2f}"  # Formata e retorna o intervalo
    return 'Outros'  # Se a odd não se encaixar em nenhum intervalo pré-definido, retorna 'Outros'

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
    
    # Selectbox para selecionar o intervalo de odds
    st.sidebar.subheader("Faixa de Odds")
    selected_odds_range = st.sidebar.selectbox("Selecione um intervalo de odds:", options=odds_groups)

    # Extrair os limites inferior e superior do intervalo selecionado
    if selected_odds_range == "Outros":
        min_odds, max_odds = -1, -1  # Para o caso "Outros", significa que não há intervalo específico
    else:
        min_odds, max_odds = map(float, selected_odds_range.split(' - '))
    
    df = load_data()  # Carregar os dados

    mostrar_resultados(team_type, time, odds_column, (min_odds, max_odds), df)

def mostrar_resultados(team_type, time, odds_column, odds_group, df):
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
    
    # Adicionar coluna de coeficiente de eficiência
    team_df['Coeficiente_Eficiencia'] = team_df.apply(calcular_coeficiente, args=(team_type,), axis=1)
    
    # Selecionar apenas as colunas relevantes para exibição
    team_df = team_df[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Empate', 'Odd_Away', 'Gols_Home', 'Gols_Away', 'Resultado', 'Coeficiente_Eficiencia', 'Placar']]
    
    # Exibir o DataFrame resultante
    st.write("### Partidas:")
    st.dataframe(team_df)
    
    # Plotar variação das odds ao longo do tempo
    plot_odds_variation(team_df, time, odds_column)

    # Calcular estatísticas e exibir
    calcular_estatisticas_e_exibir(team_df, team_type, odds_column)

def plot_odds_variation(df, team_name, odds_column):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Data'], y=df[odds_column], mode='lines', name=odds_column))
    fig.update_layout(title=f'Variação das Odds para {team_name}',
                      xaxis_title='Tempo',
                      yaxis_title='Odds')
    st.plotly_chart(fig)

def calcular_estatisticas_e_exibir(team_df, team_type, odds_column):
    # Implemente conforme necessário para calcular estatísticas adicionais

if __name__ == "__main__":
    main()
