import os
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from bd import file_paths  # Importando file_paths do arquivo bd.py

# Função para baixar um arquivo e armazená-lo em cache
def baixar_e_armazenar(url):
    pasta_cache = "cache"
    arquivo_cache = os.path.join(pasta_cache, os.path.basename(url))
    
    if not os.path.exists(pasta_cache):
        os.makedirs(pasta_cache)
    
    if not os.path.exists(arquivo_cache):
        resposta = requests.get(url)
        with open(arquivo_cache, 'wb') as f:
            f.write(resposta.content)
    
    return arquivo_cache

# Função para converter a data do formato "Sep 03 2022 - 1:00pm" para "dd/mm/yyyy"
def converter_data_gmt(data_str):
    data_obj = datetime.strptime(data_str, '%b %d %Y - %I:%M%p')
    return data_obj.strftime('%d-%m-%Y')

# Função para classificar o resultado com base nos gols das equipes da casa e visitantes
def classificar_resultado(linha, tipo_time):
    if tipo_time == "Casa":
        if linha['Gols_Casa'] > linha['Gols_Visitante']:
            return 'V'
        elif linha['Gols_Casa'] < linha['Gols_Visitante']:
            return 'D'
        else:
            return 'E'
    else:  
        if linha['Gols_Visitante'] > linha['Gols_Casa']:
            return 'V'
        elif linha['Gols_Visitante'] < linha['Gols_Casa']:
            return 'D'
        else:
            return 'E'

# Função principal para executar a interface Streamlit
def principal():
    st.title("Odd Justa")
    st.sidebar.header("Filtros")
    tipo_time = st.sidebar.selectbox("Selecione qual deseja analisar:", options=["Casa", "Visitante"])
    
    if tipo_time == "Casa":
        opcoes_time = sorted(str(time) for time in set(df['Casa']))
        label_time = "Time da Casa"
    else:
        opcoes_time = sorted(str(time) for time in set(df['Visitante']))
        label_time = "Time Visitante"
    
    time = st.sidebar.selectbox(f"Selecione o {label_time}:", options=opcoes_time)
    
    # Slider para selecionar o intervalo de odds
    st.sidebar.subheader("Faixa de Odds")
    min_odds, max_odds = st.sidebar.slider("Selecione um intervalo de odds:", min_value=df[odds_column].min(), max_value=df[odds_column].max(), value=(df[odds_column].min(), df[odds_column].max()))
    
    # Criar um DataFrame consolidado
    df_consolidado = criar_df_consolidado()

    # Aplicar filtros e lógica subsequente
    mostrar_resultados(df_consolidado, tipo_time, time, odds_column, (min_odds, max_odds))

# Função para criar um DataFrame consolidado
def criar_df_consolidado():
    df_consolidado = pd.DataFrame()  
    
    for caminho_arquivo in file_paths:
        try:
            arquivo_cache = baixar_e_armazenar(caminho_arquivo)
            df = pd.read_csv(arquivo_cache)
            
            # Ajustar dataframe antes de concatenar
            if 'FTHG' in df.columns:
                # Formato do primeiro arquivo
                df = formatar_primeiro_arquivo(df)
            elif 'home_team_name' in df.columns:
                # Formato do terceiro arquivo
                df = formatar_terceiro_arquivo(df)
            else:
                # Formato do segundo arquivo
                df = formatar_segundo_arquivo(df)

            df = df.groupby(['Data', 'Casa', 'Visitante']).first().reset_index()

            # Mesclar com DataFrame consolidado
            df_consolidado = pd.concat([df_consolidado, df])  
        except Exception as e:
            print(f"Erro ao processar arquivo {caminho_arquivo}: {e}")

    df_consolidado = df_consolidado[['Data', 'Casa', 'Visitante', 'Odd_Casa', 'Odd_Empate', 'Odd_Visitante', 'Gols_Casa', 'Gols_Visitante']]

    return df_consolidado

# Função para formatar o primeiro arquivo
def formatar_primeiro_arquivo(df):
    df.rename(columns={
        'Date': 'Data',
        'HomeTeam': 'Casa',
        'AwayTeam': 'Visitante',
        'FTHG': 'Gols_Casa',
        'FTAG': 'Gols_Visitante',
        'FTR': 'Resultado',
        'PSCH': 'Odd_Casa',
        'PSCD': 'Odd_Empate',
        'PSCA': 'Odd_Visitante'
    }, inplace=True)
    return df

# Função para formatar o segundo arquivo
def formatar_segundo_arquivo(df):
    df.rename(columns={
        'Date': 'Data',
        'Home': 'Casa',
        'Away': 'Visitante',
        'HG': 'Gols_Casa',
        'AG': 'Gols_Visitante',
        'Res': 'Resultado',
        'PH': 'Odd_Casa',
        'PD': 'Odd_Empate',
        'PA': 'Odd_Visitante'
    }, inplace=True)
    return df

# Função para formatar o terceiro arquivo
def formatar_terceiro_arquivo(df):
    df.rename(columns={
        'date_GMT': 'Data',
        'home_team_name': 'Casa',
        'away_team_name': 'Visitante',
        'home_team_goal_count': 'Gols_Casa',
        'away_team_goal_count': 'Gols_Visitante',
        'Res': 'Resultado',
        'odds_ft_home_team_win': 'Odd_Casa',
        'odds_ft_draw': 'Odd_Empate',
        'odds_ft_away_team_win': 'Odd_Visitante'
    }, inplace=True)
    df['Data'] = df['Data'].apply(converter_data_gmt)
    return df

# Função para exibir resultados
def mostrar_resultados(df_consolidado, tipo_time, time, odds_column, odds_group):
    df_time = df_consolidado.copy()

    if tipo_time == "Casa":
        df_time = df_time[df_time['Casa'] == time]
        odds_col = 'Odd_Casa'
        nome_time_col = 'Casa'
        nome_adversario_col = 'Visitante'
    else:
        df_time = df_time[df_time['Visitante'] == time]
        odds_col = 'Odd_Visitante'
        nome_time_col = 'Visitante'
        nome_adversario_col = 'Casa'
    
    if odds_group[0] == -1 and odds_group[1] == -1:
        df_time = df_time[(df_time[odds_col] < odds_group[0]) | (df_time[odds_col] > odds_group[1])]
    else:
        df_time = df_time[(df_time[odds_col] >= odds_group[0]) & (df_time[odds_col] <= odds_group[1])]
    
    st.write("### Partidas:")
    st.dataframe(df_time)

    num_vitorias = df_time[df_time['Resultado'] == 'V'].shape[0]
    total_jogos = df_time.shape[0]
    porcentagem_vitorias = (num_vitorias / total_jogos) * 100 if total_jogos > 0 else 0

    df_time['Lucro_Prejuizo'] = df_time.apply(lambda linha: linha[odds_column] - 1 if linha['Resultado'] == 'V' else -1, axis=1)
    lucro_prejuizo_total = df_time['Lucro_Prejuizo'].sum()

    media_gols = df_time['Gols_Casa'].mean() if tipo_time == "Casa" else df_time['Gols_Visitante'].mean()
    media_gols_sofridos = df_time['Gols_Visitante'].mean() if tipo_time == "Casa" else df_time['Gols_Casa'].mean()
    
    st.write("### Análise:")
    st.markdown(f"- Com as características do jogo de hoje, o {time} ganhou {num_vitorias} vez(es) em {total_jogos} jogo(s), aproveitamento de ({porcentagem_vitorias:.2f}%).")
    st.markdown(f"- Lucro/prejuízo total: {lucro_prejuizo_total:.2f}.")
    st.markdown(f"- Média de gols marcados: {media_gols:.2f}.")
    st.markdown(f"- Média de gols sofridos: {media_gols_sofridos:.2f}.")

if __name__ == "__main__":
    principal()
