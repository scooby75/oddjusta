import pandas as pd
import streamlit as st
import io

# Função para classificar o resultado com base nos gols das equipes da casa e visitantes
def classificar_resultado(row):
    if 'FTHG' in row:  # Verifica se a coluna FTHG está presente
        if row['FTHG'] > row['FTAG']:
            return 'W'
        elif row['FTHG'] < row['FTAG']:
            return 'L'
        else:
            return 'D'
    elif 'HG' in row:  # Verifica se a coluna HG está presente
        if row['HG'] > row['AG']:
            return 'W'
        elif row['HG'] < row['AG']:
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
    "https://www.football-data.co.uk/mmz4281/2324/D1.csv",
    "https://www.football-data.co.uk/mmz4281/2223/D1.csv",
    "https://www.football-data.co.uk/new/BRA.csv"
]

dfs = []
for file_path in file_paths:
    df = pd.read_csv(file_path)
    dfs.append(df)

# Concatenar todos os dataframes
df = pd.concat(dfs)

# Adicionar coluna de resultado
df['Resultado'] = df.apply(classificar_resultado, axis=1)

# Adicionar coluna de agrupamento de odds
df['Odd_Group'] = df['PSH'].apply(agrupar_odd)

# Renomear as colunas
df.rename(columns={
    'Date': 'Data',
    'HomeTeam': 'Home',
    'AwayTeam': 'Away',
    'HG': 'Gols_Home',
    'AG': 'Gols_Away',
    'FTHG': 'Gols_Home',  # Considerando ambos os formatos de cabeçalho
    'FTAG': 'Gols_Away',  # Considerando ambos os formatos de cabeçalho
    'FTR': 'Resultado',
    'PH': 'Odd_Home',
    'PD': 'Odd_Empate',
    'PA': 'Odd_Away'
}, inplace=True)

# Obter todas as equipes envolvidas nos jogos
all_teams = df['Home'].unique()

# Ordenar os times em ordem alfabética
times = sorted(all_teams)

# Ordenar as faixas de odds
odds_groups = sorted(df['Odd_Group'].unique())

# Interface do Streamlit
def main():
    st.title("Winrate Odds")
    st.sidebar.header("Filtros")
    time = st.sidebar.selectbox("Selecione o Time da Casa:", options=times)
    odds_group = st.sidebar.selectbox("Selecione a Faixa de Odds:", options=odds_groups)
    mostrar_resultados(time, odds_group)

def mostrar_resultados(time, odds_group):
    team_df = df[(df['Home'] == time) & (df['Odd_Group'] == odds_group)]
    team_df = team_df[['Data', 'Home', 'Away', 'Odd_Home', 'Odd_Empate', 'Odd_Away', 'Gols_Home', 'Gols_Away', 'Resultado']]

    # Exibir resultados em uma tabela
    st.write("### Partidas:")
    st.dataframe(team_df)

    # Calcular quantas vezes o time da casa ganhou
    num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
    total_matches = team_df.shape[0]
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0

    # Calcular lucro/prejuízo total
    team_df['Lucro_Prejuizo'] = team_df.apply(lambda row: row['Odd_Home'] - 1 if row['Resultado'] == 'W' else -1, axis=1)
    lucro_prejuizo_total = team_df['Lucro_Prejuizo'].sum()

    # Calcular soma dos coeficientes de eficiência
    soma_coeficientes = team_df.apply(coeficiente_eficiencia, axis=1).sum()

    # Calcular médias
    media_gols_casa = team_df['Gols_Home'].mean()
    media_gols_tomados = team_df['Gols_Away'].mean()
    
    # Destacar resultados importantes usando markdown
    st.write("### Resumo:")
    st.markdown(f"- Na faixa de odd {odds_group}, o '{time}' ganhou {num_wins} vez(es) em {total_matches} jogo(s) ({win_percentage:.2f}%).")
    st.markdown(f"- Lucro/prejuízo total: {lucro_prejuizo_total:.2f}.")
    st.markdown(f"- Coeficiente de eficiência da equipe '{time}': {soma_coeficientes:.2f}")
    st.markdown(f"- Média de gols marcados pelo time da casa: {media_gols_casa:.2f}.")
    st.markdown(f"- Média de gols sofridos pelo time visitante: {media_gols_tomados:.2f}.")
    
if __name__ == "__main__":
    main()
