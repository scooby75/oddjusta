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
df['Resultado_Home'] = df.apply(lambda row: classificar_resultado(row, "Home"), axis=1)
df['Resultado_Away'] = df.apply(lambda row: classificar_resultado(row, "Away"), axis=1)

# Adicionar coluna de agrupamento de odds
if 'Odd_Home' in df:
    df['Odd_Group_Home'] = df['Odd_Home'].apply(agrupar_odd)
if 'Odd_Away' in df:
    df['Odd_Group_Away'] = df['Odd_Away'].apply(agrupar_odd)

# Remover linhas com valores nulos em 'Gols_Home' e 'Gols_Away'
df.dropna(subset=['Gols_Home', 'Gols_Away'], inplace=True)

# Converter valores para inteiros, tratando valores não numéricos como nulos
df['Gols_Home'] = pd.to_numeric(df['Gols_Home'], errors='coerce').astype(pd.Int64Dtype())
df['Gols_Away'] = pd.to_numeric(df['Gols_Away'], errors='coerce').astype(pd.Int64Dtype())

# Remover linhas com valores nulos após a conversão
df.dropna(subset=['Gols_Home', 'Gols_Away'], inplace=True)

# Adicionar coluna de placar no formato desejado (por exemplo, "2x0", "1x1", "1x2", etc.)
df['Placar_Home'] = df['Gols_Home'].astype(str) + 'x' + df['Gols_Away'].astype(str)
df['Placar_Away'] = df['Gols_Away'].astype(str) + 'x' + df['Gols_Home'].astype(str)

# Obter todas as equipes envolvidas nos jogos
all_teams_home = set(df['Home'])
all_teams_away = set(df['Away'])

# Ordenar os times em ordem alfabética
times_home = sorted(str(team) for team in all_teams_home)
times_away = sorted(str(team) for team in all_teams_away)

# Ordenar as faixas de odds
odds_groups_home = sorted(df['Odd_Group_Home'].unique()) if 'Odd_Group_Home' in df else []
odds_groups_away = sorted(df['Odd_Group_Away'].unique()) if 'Odd_Group_Away' in df else []

# Interface do Streamlit
def main():
    st.title("Odd Justa")
    st.sidebar.header("Filtros")
    analysis_type = st.sidebar.selectbox("Selecione o tipo de análise:", options=["Home", "Away", "H2H"])

    if analysis_type == "Home":
        time = st.sidebar.selectbox("Selecione o Time da Casa:", options=times_home)
        odds_column = 'Odd_Home'  # Selecionar a coluna de odds correspondente
        df_selected = df[df['Home'] == time]
        team_type = "Home"

    elif analysis_type == "Away":
        time = st.sidebar.selectbox("Selecione o Time Visitante:", options=times_away)
        odds_column = 'Odd_Away'  # Selecionar a coluna de odds correspondente
        df_selected = df[df['Away'] == time]
        team_type = "Away"

    elif analysis_type == "H2H":
        team_home = st.sidebar.selectbox("Selecione o Time da Casa:", options=times_home)
        team_away = st.sidebar.selectbox("Selecione o Time Visitante:", options=times_away)
        df_selected = df[(df['Home'] == team_home) & (df['Away'] == team_away)]
        team_type = "H2H"

    if analysis_type == "Home" or analysis_type == "Away":
        mostrar_resultados(df_selected, team_type, time, odds_column)

    elif analysis_type == "H2H":
        mostrar_resultados_h2h(df_selected, team_home, team_away)

def mostrar_resultados(df, team_type, time, odds_column):
    st.write(f"### Resultados ({team_type}):")
    if not df.empty:
        st.dataframe(df)

        # Calcular estatísticas e exibir
        calcular_estatisticas_e_exibir(df, team_type, odds_column)

        # Realizar análise personalizada
        num_matches = df.shape[0]
        if num_matches > 0:
            num_wins = df[df[f'Resultado_{team_type}'] == 'W'].shape[0]
            num_draws = df[df[f'Resultado_{team_type}'] == 'D'].shape[0]

            lucro_prejuizo_total = calcular_lucro_prejuizo_total(df, team_type)

            odd_justa_wins = calcular_odd_justa_wins(df, num_wins)
            odd_justa_wins_draws = calcular_odd_justa_wins_draws(df, num_wins, num_draws)

            coeficiente_eficiencia_medio = df[f'Coeficiente_Eficiencia_{team_type}'].mean()
            media_gols = df['Gols_Home'].mean() if team_type == "Home" else df['Gols_Away'].mean()
            media_gols_sofridos = df['Gols_Away'].mean() if team_type == "Home" else df['Gols_Home'].mean()

            placar_counts = df[f'Placar_{team_type}'].value_counts().head(6)

            st.write(f"### Análise Personalizada ({team_type}):")
            st.markdown(f"Com as características do jogo de hoje, a análise revela que o \"{time}\" teve um bom desempenho como {'mandante' if team_type == 'Home' else 'visitante'} nas últimas {num_matches} partidas, com {num_wins} vitória(s), {num_draws} empate(s) e {num_matches - num_wins - num_draws} derrota(s).")
            st.markdown(f"O lucro/prejuízo total foi {lucro_prejuizo_total:.2f}, com odd justa para MO de {odd_justa_wins:.2f} e para HA +0.25 de {odd_justa_wins_draws:.2f}.")
            st.markdown(f"O coeficiente de eficiência médio foi de {coeficiente_eficiencia_medio:.2f}, indicando boa capacidade de marcar gols e sofrer poucos.")
            st.markdown(f"A frequência de placares mostra que o \"{time}\" venceu com mais frequência por placares como {', '.join(placar_counts.index)}.")

        else:
            st.write("Nenhuma partida encontrada para os filtros selecionados.")

def mostrar_resultados_h2h(df, team_home, team_away):
    st.write(f"### Resultados (H2H entre {team_home} x {team_away}):")
    if not df.empty:
        st.dataframe(df)

        # Calcular estatísticas para H2H
        st.write("### Estatísticas Gerais (H2H):")
        st.markdown(f"Total de confrontos entre {team_home} e {team_away}: {df.shape[0]}")

        st.write("### Placares Mais Frequentes (H2H):")
        placar_counts_home = df['Placar_Home'].value_counts().head(6)
        placar_counts_away = df['Placar_Away'].value_counts().head(6)

        st.markdown(f"Placares mais frequentes como mandante ({team_home} vs {team_away}):")
        st.dataframe(placar_counts_home)

        st.markdown(f"Placares mais frequentes como visitante ({team_away} vs {team_home}):")
        st.dataframe(placar_counts_away)

        # Realizar análise personalizada para H2H
        st.write(f"### Análise Personalizada (H2H entre {team_home} x {team_away}):")
        # Adicione aqui a análise personalizada para H2H, se necessário

    else:
        st.write(f"Nenhum confronto entre {team_home} e {team_away} encontrado.")

def calcular_lucro_prejuizo_total(team_df, team_type):
    if team_type == "Home":
        lucro_prejuizo_wins = ((team_df['Odd_Home'][team_df['Resultado_Home'] == 'W'] - 1)).sum()
        lucro_prejuizo_losses = (-1 * ((team_df['Resultado_Home'] == 'L') | (team_df['Resultado_Home'] == 'L'))).sum()
        lucro_prejuizo_total = lucro_prejuizo_wins + lucro_prejuizo_losses
    elif team_type == "Away":
        lucro_prejuizo_wins = ((team_df['Odd_Away'][team_df['Resultado_Away'] == 'W'] - 1)).sum()
        lucro_prejuizo_losses = (-1 * ((team_df['Resultado_Away'] == 'L') | (team_df['Resultado_Away'] == 'L'))).sum()
        lucro_prejuizo_total = lucro_prejuizo_wins + lucro_prejuizo_losses
    elif team_type == "H2H":
        lucro_prejuizo_wins_home = ((team_df['Odd_Home'][team_df['Resultado_Home'] == 'W'] - 1)).sum()
        lucro_prejuizo_wins_away = ((team_df['Odd_Away'][team_df['Resultado_Away'] == 'W'] - 1)).sum()
        lucro_prejuizo_losses_home = (-1 * ((team_df['Resultado_Home'] == 'L') | (team_df['Resultado_Home'] == 'L'))).sum()
        lucro_prejuizo_losses_away = (-1 * ((team_df['Resultado_Away'] == 'L') | (team_df['Resultado_Away'] == 'L'))).sum()
        lucro_prejuizo_total = lucro_prejuizo_wins_home + lucro_prejuizo_wins_away + lucro_prejuizo_losses_home + lucro_prejuizo_losses_away
    
    return lucro_prejuizo_total

def calcular_odd_justa_wins(team_df, num_wins):
    odd_justa_wins = team_df.shape[0] / num_wins if num_wins > 0 else 0
    return odd_justa_wins

def calcular_odd_justa_wins_draws(team_df, num_wins, num_draws):
    total_matches = team_df.shape[0]
    odd_justa_wins_draws = total_matches / (num_wins + num_draws) if (num_wins + num_draws) > 0 else 0
    return odd_justa_wins_draws

def calcular_estatisticas_e_exibir(df, team_type, odds_column):
    st.write(f"### Estatísticas Gerais ({team_type}):")
    if team_type == "Home":
        st.markdown(f"Total de jogos em casa: {df.shape[0]}")
    elif team_type == "Away":
        st.markdown(f"Total de jogos fora de casa: {df.shape[0]}")
    elif team_type == "H2H":
        st.markdown(f"Total de confrontos entre as equipes: {df.shape[0]}")

    st.markdown(f"Média de gols marcados por jogo: {df['Gols_Home'].mean() if team_type == 'Home' else df['Gols_Away'].mean():.2f}")
    st.markdown(f"Média de gols sofridos por jogo: {df['Gols_Away'].mean() if team_type == 'Home' else df['Gols_Home'].mean():.2f}")

# Executar o aplicativo principal
if __name__ == "__main__":
    main()
