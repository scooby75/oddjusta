import pandas as pd
import streamlit as st
import io

# Função para classificar o resultado com base nos gols das equipes da casa e visitantes
def classificar_resultado(row):
    if row['FTHG'] > row['FTAG']:
        return 'W'
    elif row['FTHG'] < row['FTAG']:
        return 'L'
    else:
        return 'D'

def agrupar_odd(odd):
    for i in range(1, 60):
        lower = 1 + (i - 1) * 0.10
        upper = 1 + i * 0.10
        if lower <= odd <= upper:
            return f"{lower:.2f} - {upper:.2f}"
    return 'Outros'

# Carregar os arquivos CSV
file_paths = [
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/Italy%20Serie%20A%20Geral.csv",
    "https://raw.githubusercontent.com/scooby75/bdfootball/main/Italy%20Serie%20B%20Geral.csv",
    # Adicione outros campeonatos conforme necessário
]

dfs = []
for file_path in file_paths:
    df = pd.read_csv(file_path)
    dfs.append(df)

# Concatenar todos os dataframes
df = pd.concat(dfs)

# Adicionar coluna de resultado
df['Resultado_FT'] = df.apply(classificar_resultado, axis=1)

# Adicionar coluna de agrupamento de odds
df['Odd_Group'] = df['PSH'].apply(agrupar_odd)

# Renomear as colunas
df.rename(columns={
    'Date': 'Data',
    'HomeTeam': 'Home',
    'AwayTeam': 'Away',
    'PSCH': 'Odd_Home',
    'PSCD': 'Odd_Empate',
    'PSCA': 'Odd_Away',
    'HTHG': 'Gols_HT_Home',
    'HTAG': 'Gols_HT_Away',
    'FTHG': 'Gols_Home',
    'FTAG': 'Gols_Away',
    'HST': 'Chutes_a_Gol_Home',
    'AST': 'Chutes_a_Gol_Away',
    'Resultado_FT': 'Resultado'
}, inplace=True)

# Ordenar os times em ordem alfabética
times = sorted(df['Home'].unique())

# Ordenar as faixas de odds
odds_groups = sorted(df['Odd_Group'].unique())

# Função para calcular o coeficiente de eficiência da equipe Home
def coeficiente_eficiencia(row):
    gols_marcados = row['Gols_Home']
    gols_sofridos = row['Gols_Away']

    diferenca_gols = gols_marcados - gols_sofridos

    coeficiente = diferenca_gols * 0.25

    return coeficiente

# Função para mostrar os resultados ao selecionar um time e uma faixa de odds
def mostrar_resultados(time, odds_group):
    team_df = df[(df['Home'] == time) & (df['Odd_Group'] == odds_group)]
    team_df = team_df[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Empate', 'Odd_Away', 'Gols_HT_Home', 'Gols_HT_Away', 'Gols_Home', 'Gols_Away', 'Chutes_a_Gol_Home', 'Chutes_a_Gol_Away', 'Resultado']]

    # Calcular quantas vezes o time da casa ganhou
    num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
    total_matches = team_df.shape[0]
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0

    # Exibir resultados
    st.write(team_df)
    st.write(f"\033[1mNa faixa de odd {odds_group}, o '{time}' ganhou {num_wins} vez(es) em {total_matches} jogo(s) ({win_percentage:.2f}%).")
    st.write(f"Outros cálculos aqui...")
    # Adicione outros cálculos conforme necessário

# Interface do Streamlit
def main():
    st.title("Análise de Resultados de Futebol")
    st.sidebar.header("Filtros")
    time = st.sidebar.selectbox("Selecione o Time da Casa:", options=times)
    odds_group = st.sidebar.selectbox("Selecione a Faixa de Odds:", options=odds_groups)
    mostrar_resultados(time, odds_group)

if __name__ == "__main__":
    main()
