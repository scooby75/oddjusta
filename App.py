import pandas as pd
import streamlit as st
from bd import FILE_PATHS

# Carregar arquivos CSV usando o arquivo externo bd.py
data_paths = FILE_PATHS

# Criar função para carregar os dados do CSV
def load_data(file_path):
    return pd.read_csv(file_path)

# Criar função para processar os dados e gerar estatísticas
def process_data(data):
    # Adicionar processamento aqui
    return data

# Aplicação Streamlit
def main():
    st.title("Análise de Dados de Futebol")

    # Sidebar para seleção de arquivo CSV
    selected_file = st.sidebar.selectbox("Selecione o arquivo CSV:", list(data_paths.keys()))

    # Carregar e processar os dados selecionados
    data = load_data(data_paths[selected_file])
    processed_data = process_data(data)

    # Exibir os dados processados
    st.write("## Dados Processados")
    st.write(processed_data)

    # Exibir estatísticas adicionais
    st.write("## Estatísticas Adicionais")

    # Definir nome do time (substituir por um valor real)
    time = "Time X"

    # Calcular quantas vezes o time da casa ganhou
    num_wins = team_df[team_df['Resultado'] == 'W'].shape[0]
    total_matches = team_df.shape[0]
    win_percentage = (num_wins / total_matches) * 100 if total_matches > 0 else 0

    # Calcular lucro/prejuízo total
    team_df['Lucro_Prejuizo'] = team_df.apply(lambda row: row['Odd_Home'] - 1 if row['Resultado'] == 'W' else -1, axis=1)
    lucro_prejuizo_total = team_df['Lucro_Prejuizo'].sum()

    # Calcular médias
    media_gols_casa = team_df['Gols_Home'].mean()
    media_gols_tomados = team_df['Gols_Away'].mean()
    
    # Calcular coeficiente de eficiência médio ajustado
    coeficiente_eficiencia_total = team_df['Coeficiente_Eficiencia'].sum()
    coeficiente_eficiencia_medio = coeficiente_eficiencia_total / total_matches if total_matches > 0 else 0

    # Calcular odd justa
    odd_justa = 100 / win_percentage if win_percentage > 0 else 0
    
    # Destacar resultados importantes usando markdown
    st.write("### Resumo:")
    st.markdown(f"- Com as características do jogo de hoje, o {time} ganhou {num_wins} vez(es) em {total_matches} jogo(s), com aproveitamento de {win_percentage:.2f}%.")
    st.markdown(f"- Odd justa: {odd_justa:.2f}.")
    st.markdown(f"- Coeficiente de eficiência médio: {coeficiente_eficiencia_medio:.2f}.")
    st.markdown(f"- Lucro/prejuízo total: {lucro_prejuizo_total:.2f}.")
    st.markdown(f"- Média de gols marcados pelo time da casa: {media_gols_casa:.2f}.")
    st.markdown(f"- Média de gols sofridos pelo time visitante: {media_gols_tomados:.2f}.")

if __name__ == "__main__":
    main()
