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

# Obter todas as equipes envolvidas nos jogos
all_teams_home = set(df['Home'])
all_teams_away = set(df['Away'])

# Ordenar os times em ordem alfabética
times_home = sorted(str(team) for team in all_teams_home)
times_away = sorted(str(team) for team in all_teams_away)

# Ordenar as faixas de odds
odds_groups = sorted(df['Odd_Group'].unique())

# Função para calcular e exibir estatísticas
def calcular_estatisticas_e_exibir(team_df, team_type, odds_column):
    total_jogos = len(team_df)
    
    if total_jogos == 0:
        st.write("### Estatísticas")
        st.write("Nenhum jogo encontrado para os filtros selecionados.")
        return

    vitorias = len(team_df[team_df['Resultado'] == 'W'])
    empates = len(team_df[team_df['Resultado'] == 'D'])
    derrotas = len(team_df[team_df['Resultado'] == 'L'])
    
    st.write(f"### Estatísticas ({team_type})")
    st.write(f"Total de Jogos: {total_jogos}")
    st.write(f"Vitórias: {vitorias} ({vitorias / total_jogos:.2%})")
    st.write(f"Empates: {empates} ({empates / total_jogos:.2%})")
    st.write(f"Derrotas: {derrotas} ({derrotas / total_jogos:.2%})")
    
    # Outras estatísticas específicas podem ser calculadas aqui
    # Exemplo: média de gols marcados, coeficiente de eficiência médio, etc.
    media_gols = team_df['Gols_Home'].mean()
    coeficiente_eficiencia_medio = team_df['Coeficiente_Eficiencia'].mean()
    
    st.write(f"Média de gols marcados: {media_gols:.2f}")
    st.write(f"Coeficiente de eficiência médio: {coeficiente_eficiencia_medio:.2f}")

    # Calcular frequência dos placares
    placar_counts = team_df['Placar'].value_counts()
    st.write("### Frequência dos Placares:")
    st.write(placar_counts)

# Função para calcular e exibir estatísticas H2H
def calcular_estatisticas_h2h(team_df, time_home, time_away, odds_column, odds_group):
    total_jogos = len(team_df)
    
    if total_jogos == 0:
        st.write("### Estatísticas H2H")
        st.write(f"Nenhum jogo encontrado entre {time_home} e {time_away} para os filtros selecionados.")
        return

    vitorias_time_home = len(team_df[(team_df['Home'] == time_home) & (team_df['Resultado'] == 'W')])
    vitorias_time_away = len(team_df[(team_df['Away'] == time_away) & (team_df['Resultado'] == 'W')])
    empates = len(team_df[team_df['Resultado'] == 'D'])
    
    st.write(f"### Estatísticas H2H ({time_home} vs {time_away})")
    st.write(f"Total de Jogos: {total_jogos}")
    st.write(f"Vitórias {time_home}: {vitorias_time_home}")
    st.write(f"Vitórias {time_away}: {vitorias_time_away}")
    st.write(f"Empates: {empates}")
    
    # Outras estatísticas específicas podem ser calculadas aqui
    # Exemplo: média de gols marcados, coeficiente de eficiência médio, etc.
    media_gols_time_home = team_df[team_df['Home'] == time_home]['Gols_Home'].mean()
    media_gols_time_away = team_df[team_df['Away'] == time_away]['Gols_Away'].mean()
    
    st.write(f"Média de gols marcados {time_home}: {media_gols_time_home:.2f}")
    st.write(f"Média de gols marcados {time_away}: {media_gols_time_away:.2f}")

    # Calcular frequência dos placares
    placar_counts = team_df['Placar'].value_counts()
    st.write("### Frequência dos Placares:")
    st.write(placar_counts)

# Função principal para exibir resultados com base no tipo de equipe selecionada
def main():
    st.sidebar.title("Filtros")
    team_type = st.sidebar.radio("Selecione o Tipo de Equipe:", ["Home", "Away", "Head-to-Head (H2H)"])

    if team_type == "Home":
        time = st.sidebar.selectbox("Selecione o Time:", options=times_home)
        odds_group = st.sidebar.selectbox("Selecione um intervalo de odds:", options=odds_groups)
        team_df = df[(df['Home'] == time) & (df['Odd_Group'] == odds_group)]
        calcular_estatisticas_e_exibir(team_df, team_type, 'Odd_Home', odds_group)

    elif team_type == "Away":
        time = st.sidebar.selectbox("Selecione o Time:", options=times_away)
        odds_group = st.sidebar.selectbox("Selecione um intervalo de odds:", options=odds_groups)
        team_df = df[(df['Away'] == time) & (df['Odd_Group'] == odds_group)]
        calcular_estatisticas_e_exibir(team_df, team_type, 'Odd_Away', odds_group)

    elif team_type == "Head-to-Head (H2H)":
        time_home = st.sidebar.selectbox("Selecione o Time da Casa:", options=times_home)
        time_away = st.sidebar.selectbox("Selecione o Time Visitante:", options=times_away)
        odds_group = st.sidebar.selectbox("Selecione um intervalo de odds:", options=odds_groups)
        team_df = df[(df['Home'] == time_home) & (df['Away'] == time_away) & (df['Odd_Group'] == odds_group)]
        calcular_estatisticas_h2h(team_df, time_home, time_away, 'Odd_Home', odds_group)

if __name__ == "__main__":
    main()
