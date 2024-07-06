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

    mostrar_resultados(team_type, time, odds_column, (min_odds, max_odds))

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
    
    # Adicionar coluna de coeficiente de eficiência
    team_df['Coeficiente_Eficiencia'] = team_df.apply(calcular_coeficiente, args=(team_type,), axis=1)

    # Selecionar apenas as colunas relevantes para exibição
    team_df = team_df[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Empate', 'Odd_Away', 'Gols_Home', 'Gols_Away', 'Resultado', 'Coeficiente_Eficiencia', 'Placar']]

    # Calcular estatísticas e exibir
    calcular_estatisticas_e_exibir(team_df, team_type, odds_column)

    # Exibir análise personalizada
    if not team_df.empty:
        num_matches = team_df.shape[0]
        num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
        num_draws = team_df[team_df['Resultado'] == 'D'].shape[0]
        win_percentage = (num_wins / num_matches) * 100 if num_matches > 0 else 0

        lucro_prejuizo_total = calcular_lucro_prejuizo_total(team_df, team_type)
        odd_justa_wins = calcular_odd_justa_wins(team_df, num_wins)
        odd_justa_wins_draws = calcular_odd_justa_wins_draws(team_df, num_wins, num_draws)
        
        coeficiente_eficiencia_medio = team_df['Coeficiente_Eficiencia'].mean()
        media_gols = team_df['Gols_Home'].mean() if team_type == "Home" else team_df['Gols_Away'].mean()
        media_gols_sofridos = team_df['Gols_Away'].mean() if team_type == "Home" else team_df['Gols_Home'].mean()

        # Definir os textos baseados nos critérios definidos
        if win_percentage < 40.00:
            desempenho = "baixo desempenho"
        elif win_percentage > 41.00 and win_percentage < 60.00:
            desempenho = "médio desempenho"
        elif win_percentage > 61.00:
            desempenho = "bom desempenho"
        else:
            desempenho = "desempenho não determinado"

        if coeficiente_eficiencia_medio < 0.50:
            eficiencia = "baixa capacidade de marcar gol e alta capacidade de sofrer gols"
        elif coeficiente_eficiencia_medio > 0.51 and coeficiente_eficiencia_medio < 1.0:
            eficiencia = "média capacidade de marcar gol e média capacidade de sofrer gols"
        elif coeficiente_eficiencia_medio > 1.01:
            eficiencia = "alta capacidade de marcar gol e baixa capacidade de sofrer gols"
        else:
            eficiencia = "capacidade de eficiência não determinada"

        st.write("### Análise Personalizada:")
        st.markdown(f"A análise revela que o \"{team_df[team_name_col].iloc[0]}\" teve um {desempenho} como {'mandante' if team_type == 'Home' else 'visitante'} nas últimas {num_matches} partidas, com {num_wins} vitória(s), {num_draws} empate(s) e {num_matches - num_wins - num_draws} derrota(s), aproveitamento de {win_percentage:.0f}%.")
        st.markdown(f"O lucro/prejuízo total foi {lucro_prejuizo_total:.2f}, com odd justa para MO de {odd_justa_wins:.2f} e para HA +0.25 de {odd_justa_wins_draws:.2f}.")
        st.markdown(f"O coeficiente de eficiência médio foi de {coeficiente_eficiencia_medio:.2f}, indicando {eficiencia}.")
        st.markdown(f"A frequência de placares mostra que o \"{team_df[team_name_col].iloc[0]}\" venceu com mais frequência por placares apertados, como {', '.join(team_df['Placar'].value_counts().head(3).index)}.")

    else:
        st.write("Nenhuma partida encontrada para os filtros selecionados.")


def calcular_lucro_prejuizo_total(df, team_type):
    if team_type == "Home":
        lucro_prejuizo = (df['Odd_Home'] - 1)[df['Resultado'] == 'W'].sum() + (df['Odd_Empate'] - 1)[df['Resultado'] == 'D'].sum()
    else:
        lucro_prejuizo = (df['Odd_Away'] - 1)[df['Resultado'] == 'W'].sum() + (df['Odd_Empate'] - 1)[df['Resultado'] == 'D'].sum()
    return lucro_prejuizo

def calcular_odd_justa_wins(df, num_wins):
    if num_wins > 0:
        odd_justa_wins = (df[df['Resultado'] == 'W']['Odd_Home'].sum() + df[df['Resultado'] == 'W']['Odd_Away'].sum()) / num_wins
    else:
        odd_justa_wins = 0
    return odd_justa_wins

def calcular_odd_justa_wins_draws(df, num_wins, num_draws):
    if num_wins + num_draws > 0:
        odd_justa_wins_draws = (df[(df['Resultado'] == 'W') | (df['Resultado'] == 'D')]['Odd_Home'].sum() + df[(df['Resultado'] == 'W') | (df['Resultado'] == 'D')]['Odd_Away'].sum()) / (num_wins + num_draws)
    else:
        odd_justa_wins_draws = 0
    return odd_justa_wins_draws

def calcular_estatisticas_e_exibir(df, team_type, odds_column):
    # Calcular estatísticas gerais
    num_matches = df.shape[0]
    num_wins = df[df['Resultado'] == 'W'].shape[0]
    num_draws = df[df['Resultado'] == 'D'].shape[0]
    num_losses = num_matches - num_wins - num_draws
    win_percentage = (num_wins / num_matches) * 100 if num_matches > 0 else 0
    lucro_prejuizo_total = calcular_lucro_prejuizo_total(df, team_type)
    coeficiente_eficiencia_medio = df['Coeficiente_Eficiencia'].mean()
    media_gols = df['Gols_Home'].mean() if team_type == "Home" else df['Gols_Away'].mean()
    media_gols_sofridos = df['Gols_Away'].mean() if team_type == "Home" else df['Gols_Home'].mean()


# Executar a aplicação principal
if __name__ == "__main__":
    main()
