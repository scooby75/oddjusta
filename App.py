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

# Função para agrupar coeficientes de eficiência em intervalos
def agrupar_coeficiente(coef):
    for i in range(-10, 11):  # Ajuste o intervalo de acordo com os possíveis valores
        lower = i * 0.50
        upper = lower + 0.50
        if lower <= coef < upper:
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

# Carregar o arquivo CSV
try:
    cached_file = download_and_cache(file_paths[0])  # Supondo que haja apenas um arquivo
    df = pd.read_csv(cached_file, encoding='utf-8')  # Especificar a codificação UTF-8
except Exception as e:
    st.error(f"Erro ao processar o arquivo {file_paths[0]}: {e}")

# Adicionar coluna de resultado com a lógica correta para o tipo de equipe selecionado
df['Resultado'] = df.apply(lambda row: classificar_resultado(row, "Home"), axis=1)

# Adicionar coluna de agrupamento de odds
if 'Odd_Home' in df:
    df['Odd_Group'] = df['Odd_Home'].apply(agrupar_odd)
elif 'Odd_Away' in df:
    df['Odd_Group'] = df['Odd_Away'].apply(agrupar_odd)

# Adicionar coluna de agrupamento de coeficientes de eficiência
df['Coeficiente_Eficiencia'] = df.apply(lambda row: calcular_coeficiente(row, "Home"), axis=1)
df['Coeficiente_Grupo'] = df['Coeficiente_Eficiencia'].apply(agrupar_coeficiente)

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

# Ordenar as faixas de odds e coeficientes
odds_groups = sorted(df['Odd_Group'].unique())
coef_groups = sorted(df['Coeficiente_Grupo'].unique())

# Função para calcular estatísticas e exibir resultados
def calcular_estatisticas_e_exibir(team_df, team_type, odds_column, min_odds, max_odds, min_coef, max_coef):
    # Filtrar os dados de acordo com a faixa de odds e coeficientes selecionada
    if min_odds >= 0:
        team_df = team_df[(team_df[odds_column] >= min_odds) & (team_df[odds_column] <= max_odds)]
    if min_coef > -float('inf') and max_coef < float('inf'):
        team_df = team_df[(team_df['Coeficiente_Eficiencia'] >= min_coef) & (team_df['Coeficiente_Eficiencia'] <= max_coef)]
    
    # Contar a ocorrência de cada placar
    placar_counts = team_df['Placar'].value_counts()

    # Calcular o total de eventos
    total_eventos = placar_counts.sum()

    # Criar DataFrame para a frequência dos placares
    placar_df = pd.DataFrame({
        'Placar': placar_counts.index,
        'Frequencia': placar_counts.values
    })

    # Calcular a Probabilidade (%) e a Odd Lay
    placar_df['Probabilidade (%)'] = (placar_df['Frequencia'] / total_eventos) * 100
    placar_df['Odd_Lay'] = 100 / placar_df['Probabilidade (%)']

    # Formatar para duas casas decimais
    placar_df['Probabilidade (%)'] = placar_df['Probabilidade (%)'].round(2)
    placar_df['Odd_Lay'] = placar_df['Odd_Lay'].round(2)

    # Destacar resultados importantes usando markdown
    st.write("### Análise:")
    if not team_df.empty:
        num_wins = team_df['Resultado'].value_counts().get('W', 0)
        num_draws = team_df['Resultado'].value_counts().get('D', 0)
        num_losses = team_df['Resultado'].value_counts().get('L', 0)
        total_matches = num_wins + num_draws + num_losses
        win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0
        lucro_prejuizo = num_wins * odd_justa_wins - (num_losses * odd_justa_wins)  # Exemplo de cálculo
        odd_justa_wins = 1 / (1 / (total_matches + 1))  # Exemplo de cálculo
        odd_justa_wins_draws = 1 / (1 / (total_matches + 1))  # Exemplo de cálculo
        coeficiente_eficiencia_medio = team_df['Coeficiente_Eficiencia'].mean()
        media_gols = team_df['Gols_Home'].mean() if team_type == "Home" else team_df['Gols_Away'].mean()
        media_gols_sofridos = team_df['Gols_Away'].mean() if team_type == "Home" else team_df['Gols_Home'].mean()
        num_wins_draws = num_wins + num_draws

        st.markdown(f"- Com as características do jogo de hoje, o {time} ganhou {num_wins} vez(es) em {total_matches} jogo(s), aproveitamento de ({win_percentage:.2f}%).")
    else:
        st.write("Nenhum jogo encontrado para os filtros selecionados.")
    st.markdown(f"- Lucro/prejuízo total: {lucro_prejuizo:.2f}.")
    st.markdown(f"- Odd justa para MO: {odd_justa_wins:.2f}.")
    st.write(f"- Total de partidas sem derrota: {num_wins_draws} ({num_wins} vitórias, {num_draws} empates)")
    st.markdown(f"- Odd justa para HA +0.25: {odd_justa_wins_draws:.2f}.")
    st.markdown(f"- Coeficiente de eficiência: {coeficiente_eficiencia_medio:.2f}.")
    st.markdown(f"- Média de gols marcados: {media_gols:.2f}.")
    st.markdown(f"- Média de gols sofridos: {media_gols_sofridos:.2f}.")

    st.write("### Frequência dos Placares:")
    st.table(placar_df)

# Função principal para a interface do Streamlit
def main():
    st.title("Análise de Jogos de Futebol")
    
    # Seletor de tipo de equipe
    team_type = st.sidebar.selectbox("Selecione o tipo de equipe:", ["Home", "Away"])
    
    # Seletor de equipe
    time = st.sidebar.selectbox("Selecione o time:", options=times_home if team_type == "Home" else times_away)
    
    # Seletor de coluna de odds
    odds_column = st.sidebar.selectbox("Selecione a coluna de odds:", ["Odd_Home", "Odd_Away"])
    
    # Seletor de intervalo de odds
    min_odds = st.sidebar.number_input("Mínima Odd", min_value=0.0, step=0.1, value=1.0)
    max_odds = st.sidebar.number_input("Máxima Odd", min_value=0.0, step=0.1, value=2.0)
    
    # Seletor de intervalo de coeficientes de eficiência
    min_coef = st.sidebar.number_input("Mínimo Coeficiente de Eficiência", value=-float('inf'))
    max_coef = st.sidebar.number_input("Máximo Coeficiente de Eficiência", value=float('inf'))

    team_df = df[df['Home'] == time] if team_type == "Home" else df[df['Away'] == time]
    calcular_estatisticas_e_exibir(team_df, team_type, odds_column, min_odds, max_odds, min_coef, max_coef)

if __name__ == "__main__":
    main()
