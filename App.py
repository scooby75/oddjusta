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

# Função para calcular estatísticas e exibir
def calcular_estatisticas_e_exibir(team_df, team_type, odds_column):
    # Calcular estatísticas
    num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
    num_draws = team_df[team_df['Resultado'] == 'D'].shape[0]
    num_wins_draws = num_wins + num_draws  # Total de partidas sem derrota (W + D)
    total_matches = team_df.shape[0]
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0
    
    # Calcular lucro/prejuízo com base no tipo de equipe selecionada e no resultado de cada jogo
    if team_type == "Home":
        # Calcular lucro/prejuízo para jogos ganhos
        lucro_prejuizo_wins = ((team_df['Odd_Home'][team_df['Resultado'] == 'W'] - 1)).sum()
        # Calcular lucro/prejuízo para jogos perdidos
        lucro_prejuizo_losses = (-1 * ((team_df['Resultado'] == 'L') | (team_df['Resultado'] == 'L'))).sum()
        lucro_prejuizo_total = lucro_prejuizo_wins + lucro_prejuizo_losses
    else:
        # Calcular lucro/prejuízo para jogos ganhos
        lucro_prejuizo_wins = ((team_df['Odd_Away'][team_df['Resultado'] == 'W'] - 1)).sum()
        # Calcular lucro/prejuízo para jogos perdidos
        lucro_prejuizo_losses = (-1 * ((team_df['Resultado'] == 'L') | (team_df['Resultado'] == 'L'))).sum()
        lucro_prejuizo_total = lucro_prejuizo_wins + lucro_prejuizo_losses

    # Verificar se lucro_prejuizo_total é um valor numérico antes de formatá-lo
    if isinstance(lucro_prejuizo_total, (int, float)):
        lucro_prejuizo_total = lucro_prejuizo_total
    else:
        lucro_prejuizo_total = 0

    # Calcular médias
    media_gols = team_df['Gols_Home'].mean() if team_type == "Home" else team_df['Gols_Away'].mean()
    media_gols_sofridos = team_df['Gols_Away'].mean() if team_type == "Home" else team_df['Gols_Home'].mean()
    coeficiente_eficiencia_medio = team_df['Coeficiente_Eficiencia'].mean()

    # Calcular odd justa para o total de partidas sem derrota
    odd_justa_wins_draws = total_matches / num_wins_draws if num_wins_draws > 0 else 0
    # Calcular odd justa apenas para as vitórias
    odd_justa_wins = total_matches / num_wins if num_wins > 0 else 0
    
    # Contar a ocorrência de cada placar
    placar_counts = team_df['Placar'].value_counts()

    # Destacar resultados importantes usando markdown
    st.write("### Análise:")
    if not team_df.empty:
        st.markdown(f"- Com as características do jogo de hoje, o {team_df['Home'].iloc[0] if team_type == 'Home' else team_df['Away'].iloc[0]} ganhou {num_wins} vez(es) em {total_matches} jogo(s), aproveitamento de ({win_percentage:.2f}%).")
    else:
        st.write("Nenhum jogo encontrado para os filtros selecionados.")
    st.markdown(f"- Lucro/prejuízo total: {lucro_prejuizo_total:.2f}.")
    st.markdown(f"- Odd justa para MO: {odd_justa_wins:.2f}.")
    st.write(f"- Total de partidas sem derrota: {num_wins_draws} ({num_wins} vitórias, {num_draws} empates)")
    st.markdown(f"- Odd justa para HA +0.25: {odd_justa_wins_draws:.2f}.")
    st.markdown(f"- Coeficiente de eficiência: {coeficiente_eficiencia_medio:.2f}.")
    st.markdown(f"- Média de gols marcados: {media_gols:.2f}.")
    st.markdown(f"- Média de gols sofridos: {media_gols_sofridos:.2f}.")
    st.write("### Frequência dos Placares:")
    st.write(placar_counts)

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

# Função principal para executar o aplicativo
def main():
    # Título do aplicativo
    st.title("Análise Estatística de Resultados de Partidas Esportivas")

    # Sidebar para seleção de opções
    st.sidebar.title("Opções de Análise")
    team_type = st.sidebar.selectbox("Selecione o tipo de equipe", ["Home", "Away"])
    min_odds, max_odds = st.sidebar.slider("Selecione o intervalo de odds", float(df['Odd_Home'].min()), float(df['Odd_Home'].max()), (float(df['Odd_Home'].min()), float(df['Odd_Home'].max())))

    # Filtrar os dados com base nas opções selecionadas
    time = st.sidebar.text_input("Digite o nome do time", "Digite o nome do time")
    team_df = df[(df['Home'] == time) | (df['Away'] == time)]
    odds_column = 'Odd_Home' if team_type == 'Home' else 'Odd_Away'
    
    # Mostrar os resultados com base nas opções selecionadas
    mostrar_resultados(team_type, time, odds_column, (min_odds, max_odds), team_df)

def mostrar_resultados(team_type, time, odds_column, odds_range, team_df):
    # Filtrar o DataFrame com base no tipo de equipe selecionada e no intervalo de odds
    if team_type == 'Home':
        team_df = team_df[(team_df['Home'] == time) & (team_df[odds_column] >= odds_range[0]) & (team_df[odds_column] <= odds_range[1])]
    else:
        team_df = team_df[(team_df['Away'] == time) & (team_df[odds_column] >= odds_range[0]) & (team_df[odds_column] <= odds_range[1])]
    
    # Verificar se há dados para mostrar
    if team_df.empty:
        st.warning("Nenhum dado disponível com as opções selecionadas.")
        return

    # Calcular o coeficiente de eficiência se a coluna existir no DataFrame
    if 'Coeficiente_Eficiencia' in team_df.columns:
        team_df['Coeficiente_Eficiencia'] = team_df.apply(lambda row: calcular_coeficiente(row, team_type), axis=1)

    # Exibir estatísticas e análises detalhadas
    calcular_estatisticas_e_exibir(team_df, team_type, odds_column)

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
