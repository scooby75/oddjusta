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

# Função para calcular o coeficiente de eficiência (ajuste conforme necessário)
def calcular_coeficiente(row, team_type):
    # Exemplo de cálculo simples de coeficiente de eficiência
    if team_type == "Home":
        return row['Gols_Home'] - row['Gols_Away']
    else:
        return row['Gols_Away'] - row['Gols_Home']

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
    
    # Porcentagem de vitórias
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0
    
    # Cálculo de lucro/prejuízo
    lucro_prejuizo = (num_wins * team_df[odds_col].mean()) - total_matches if total_matches > 0 else 0
    
    # Cálculo da odd justa para vitórias (baseada na probabilidade)
    odd_justa_wins = 100 / win_percentage if win_percentage > 0 else 0
    
    # Cálculo da odd justa para vitórias + empates
    num_wins_draws = num_wins + num_draws
    win_draw_percentage = (num_wins_draws / total_matches) * 100 if total_matches > 0 else 0
    odd_justa_wins_draws = 100 / win_draw_percentage if win_draw_percentage > 0 else 0
    
    # Coeficiente de eficiência médio
    coeficiente_eficiencia_medio = team_df['Coeficiente_Eficiencia'].mean() if not team_df['Coeficiente_Eficiencia'].empty else 0
    
    # Média de gols marcados
    media_gols = team_df['Gols_Home'].mean() if not team_df['Gols_Home'].empty else 0
    
    # Média de gols sofridos
    media_gols_sofridos = team_df['Gols_Away'].mean() if not team_df['Gols_Away'].empty else 0
    
    # Calcular a frequência dos placares
    placar_df = team_df.groupby(['Gols_Home', 'Gols_Away']).size().reset_index(name='Frequência')
    placar_df['Placar'] = placar_df['Gols_Home'].astype(str) + 'x' + placar_df['Gols_Away'].astype(str)
    placar_df = placar_df[['Placar', 'Frequência']]

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
    st.markdown(f"- Xg Home: {media_gols:.2f}.")
    st.markdown(f"- Xg Away: {media_gols_sofridos:.2f}.")

    st.write("### Frequência dos Placares:")
    st.table(placar_df)

# Função para exibir resultados de confrontos diretos (H2H)
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

        st.write("### Frequência dos Placares H2H:")
        st.table(placar_df)

if __name__ == "__main__":
    main()
