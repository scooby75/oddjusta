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

# Interface do Streamlit
def main():
    st.title("Odd Justa")
    st.sidebar.header("Filtros")
    analysis_type = st.sidebar.selectbox("Selecione o tipo de análise:", options=["Padrão", "Head to Head (H2H)"])
    
    if analysis_type == "Padrão":
        team_type = st.sidebar.selectbox("Selecione qual deseja analisar:", options=["Home", "Away"])
        if team_type == "Home":
            time = st.sidebar.selectbox("Selecione o Time da Casa:", options=sorted(df['Home'].unique()))
            odds_column = 'Odd_Home'  # Selecionar a coluna de odds correspondente
        else:
            time = st.sidebar.selectbox("Selecione o Time Visitante:", options=sorted(df['Away'].unique()))
            odds_column = 'Odd_Away'  # Selecionar a coluna de odds correspondente
        
        # Selectbox para selecionar o intervalo de odds
        st.sidebar.subheader("Faixa de Odds")
        odds_groups = sorted(df['Odd_Group'].unique())
        selected_odds_range = st.sidebar.selectbox("Selecione um intervalo de odds:", options=odds_groups)

        # Extrair os limites inferior e superior do intervalo selecionado
        if selected_odds_range == "Outros":
            min_odds, max_odds = -1, -1  # Para o caso "Outros", significa que não há intervalo específico
        else:
            min_odds, max_odds = map(float, selected_odds_range.split(' - '))

        mostrar_resultados(team_type, time, odds_column, (min_odds, max_odds))
    
    elif analysis_type == "Head to Head (H2H)":
        time_home = st.sidebar.selectbox("Selecione o Time da Casa:", options=sorted(df['Home'].unique()))
        time_away = st.sidebar.selectbox("Selecione o Time Visitante:", options=sorted(df['Away'].unique()))
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
    
    # Calcular estatísticas e exibir
    calcular_estatisticas_e_exibir(team_df, team_type, odds_column)

def mostrar_h2h(time_home, time_away):
    # Filtrar jogos onde o time da casa e o time visitante são os selecionados
    h2h_df = df[(df['Home'] == time_home) & (df['Away'] == time_away)]
    
    st.header(f"Head to Head entre {time_home} (Casa) vs {time_away} (Visitante)")

    # Mostrar DataFrame com os jogos selecionados
    st.write(h2h_df)

    # Verificar se as colunas necessárias estão presentes
    required_columns = ['Lucro_Por_Jogo', 'Odd_Justa_MO', 'Odd_Justa']
    if h2h_df.columns.isin(required_columns).all():
        st.write(h2h_df[required_columns])
    else:
        st.warning(f"Algumas colunas necessárias não estão presentes no DataFrame: {', '.join(required_columns)}")

def calcular_estatisticas_e_exibir(team_df, team_type, odds_column):
    # Calcular estatísticas
    num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
    num_draws = team_df[team_df['Resultado'] == 'D'].shape[0]
    num_losses = team_df[team_df['Resultado'] == 'L'].shape[0]
    num_wins_draws = num_wins + num_draws  # Total de partidas sem derrota (W + D)
    total_matches = team_df.shape[0]
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0
    
    # Calcular lucro/prejuízo com base no tipo de equipe selecionada e no resultado de cada jogo
    if team_type == "Home":
        lucro_prejuizo_wins = ((team_df[odds_column][team_df['Resultado'] == 'W'] - 1)).sum()
        lucro_prejuizo_losses = (-1 * ((team_df[odds_column][team_df['Resultado'] == 'L']) | (team_df[odds_column][team_df['Resultado'] == 'L']))).sum()
        lucro_prejuizo_total = lucro_prejuizo_wins + lucro_prejuizo_losses
    else:
        lucro_prejuizo_wins = ((team_df[odds_column][team_df['Resultado'] == 'W'] - 1)).sum()
        lucro_prejuizo_losses = (-1 * ((team_df[odds_column][team_df['Resultado'] == 'L']) | (team_df[odds_column][team_df['Resultado'] == 'L']))).sum()
        lucro_prejuizo_total = lucro_prejuizo_wins + lucro_prejuizo_losses

    # Calcular médias
    media_gols = team_df['Gols_Home'].mean() if team_type == "Home" else team_df['Gols_Away'].mean()
    media_gols_sofridos = team_df['Gols_Away'].mean() if team_type == "Home" else team_df['Gols_Home'].mean()
    coeficiente_eficiencia_medio = team_df['Coeficiente_Eficiencia'].mean()

    # Calcular odd justa para o total de partidas sem derrota
    odd_justa_wins_draws = total_matches / num_wins_draws if num_wins_draws > 0 else 0
    # Calcular odd justa apenas para as vitórias
    odd_justa_wins = total_matches / num_wins if num_wins > 0 else 0

    # Mostrar resultados
    st.header(f"Estatísticas para {team_type} team: {time}")
    st.write(f"Total de Jogos: {total_matches}")
    st.write(f"Percentual de Vitórias: {win_percentage}%")
    st.write(f"Lucro/Prejuízo Total: {lucro_prejuizo_total}")
    st.write(f"Média de Gols: {media_gols}")
    st.write(f"Média de Gols Sofridos: {media_gols_sofridos}")
    st.write(f"Odd Justa para Total de Jogos sem Derrota: {odd_justa_wins_draws}")
    st.write(f"Odd Justa Apenas para Vitórias: {odd_justa_wins}")

# Executar o aplicativo
if __name__ == '__main__':
    main()
