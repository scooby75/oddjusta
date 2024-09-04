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

# Função para calcular estatísticas e exibir resultados
def calcular_estatisticas_e_exibir(team_df, team_type, odds_column):
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

    return placar_df

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

    # Exibir a tabela das partidas filtradas
    st.subheader(f"Resultados de {time} ({team_type}):")
    st.dataframe(team_df)

    # Calcular estatísticas
    num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
    num_draws = team_df[team_df['Resultado'] == 'D'].shape[0]
    num_losses = team_df[team_df['Resultado'] == 'L'].shape[0]
    total_matches = num_wins + num_draws + num_losses
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0
    lucro_prejuizo = (num_wins * team_df[odds_col].mean() - total_matches) if total_matches > 0 else 0
    odd_justa_wins = (num_wins / total_matches) if total_matches > 0 else 0
    num_wins_draws = num_wins + num_draws
    odd_justa_wins_draws = (num_wins_draws / total_matches) if total_matches > 0 else 0
    coeficiente_eficiencia_medio = team_df['Coeficiente_Eficiencia'].mean() if not team_df['Coeficiente_Eficiencia'].empty else 0
    media_gols = team_df['Gols_Home'].mean() if not team_df['Gols_Home'].empty else 0
    media_gols_sofridos = team_df['Gols_Away'].mean() if not team_df['Gols_Away'].empty else 0

    # Calcular a frequência dos placares e exibir as estatísticas
    placar_df = calcular_estatisticas_e_exibir(team_df, team_type, odds_column)

    # Destacar resultados importantes usando markdown
    st.write("### Análise:")
    if not team_df.empty:
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


def mostrar_resultados_h2h(df, time_home, time_away):
    # Filtrar DataFrame para confrontos diretos
    h2h_df = df[((df['Home'] == time_home) & (df['Away'] == time_away)) |
                ((df['Home'] == time_away) & (df['Away'] == time_home))]

    if h2h_df.empty:
        st.write(f"Não existe partidas entre {time_home} e {time_away}.")
    else:
        st.write(f"### Resultados H2H entre {time_home} e {time_away}")
        st.table(h2h_df)

        # Adicionar coluna de placar no formato desejado
        h2h_df['Placar'] = h2h_df['Gols_Home'].astype(str) + 'x' + h2h_df['Gols_Away'].astype(str)
        
        # Calcular estatísticas para o time da casa
        num_wins_home = h2h_df[(h2h_df['Home'] == time_home) & (h2h_df['Resultado'] == 'W')].shape[0]
        num_draws = h2h_df[h2h_df['Resultado'] == 'D'].shape[0]
        num_losses_home = h2h_df[(h2h_df['Home'] == time_home) & (h2h_df['Resultado'] == 'L')].shape[0]
        total_matches = num_wins_home + num_draws + num_losses_home

        win_percentage_home = (num_wins_home / total_matches) * 100 if total_matches > 0 else 0

        # Calcular estatísticas para o time visitante
        num_wins_away = h2h_df[(h2h_df['Home'] == time_away) & (h2h_df['Resultado'] == 'W')].shape[0]
        num_losses_away = h2h_df[(h2h_df['Home'] == time_away) & (h2h_df['Resultado'] == 'L')].shape[0]
        total_matches_away = num_wins_away + num_draws + num_losses_away

        win_percentage_away = (num_wins_away / total_matches_away) * 100 if total_matches_away > 0 else 0
        
        # Destacar resultados importantes usando markdown
        st.write("### Análise:")
        st.markdown(f"- Total de partidas entre {time_home} e {time_away}: {total_matches}.")
        st.markdown(f"- {time_home} ganhou {num_wins_home} vez(es) ({win_percentage_home:.2f}%) e perdeu {num_losses_home} vez(es).")
        st.markdown(f"- {time_away} ganhou {num_wins_away} vez(es) ({win_percentage_away:.2f}%) e perdeu {num_losses_away} vez(es).")
        st.markdown(f"- Empates: {num_draws}.")
        
        # Frequência dos placares
        placar_df = h2h_df['Placar'].value_counts().reset_index(name='Frequência')
        placar_df.columns = ['Placar', 'Frequência']

        # Calcular a Probabilidade (%) e a Odd Lay
        total_eventos = placar_df['Frequência'].sum()
        placar_df['Probabilidade (%)'] = (placar_df['Frequência'] / total_eventos) * 100
        placar_df['Odd_Lay'] = 100 / placar_df['Probabilidade (%)']
        
        # Formatar para duas casas decimais
        placar_df['Probabilidade (%)'] = placar_df['Probabilidade (%)'].round(2)
        placar_df['Odd_Lay'] = placar_df['Odd_Lay'].round(2)

        st.write("### Frequência dos Placares:")
        st.table(placar_df)



if __name__ == "__main__":
    main()
