import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configuração da página
st.set_page_config(page_title="Análise Radiométrica - GLP", layout="wide")

# Título da aplicação
st.title("📊 Análise Estatística de Resultados Radiométricos")
st.subheader("Relação entre Taxa de Dose e Concentrações de Ra-226 e Ra-228")

# Processamento dos dados
@st.cache_data
def load_data():
    # Carregar os dados do arquivo Excel
    df = pd.read_excel("Resultados de análises radiométricas - GLP.xlsx", sheet_name="Macaé")
    
    # Limpeza e preparação dos dados
    # Renomear colunas para facilitar o trabalho
    df.columns = [str(col).strip() for col in df.columns]
    
    # Converter colunas numéricas - usando os nomes corretos da sua planilha
    numeric_columns = ['Taxa de Dose Máxima (µSv/h)', 'Resultado_ra226', 
                      'Incerteza', 'Resultado_ra228', 
                      'Incerteza.1', 'Massa Líquida (kg)']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filtrar dados válidos para análise
    df = df.dropna(subset=['Taxa de Dose Máxima (µSv/h)', 'Resultado_ra226', 
                          'Resultado_ra228'])
    
    return df

df = load_data()

# Sidebar com filtros
st.sidebar.header("🔧 Filtros de Análise")

# Filtro por concentração máxima
max_concentration = st.sidebar.slider(
    "Concentração máxima para análise (Bq/g)",
    min_value=0.1, max_value=20.0, value=8.0, step=0.1
)

# Filtro por taxa de dose máxima
max_dose_rate = st.sidebar.slider(
    "Taxa de dose máxima para análise (µSv/h)",
    min_value=0.1, max_value=10.0, value=5.0, step=0.1
)

# Aplicar filtros
filtered_df = df[
    (df['Resultado_ra226'] <= max_concentration) & 
    (df['Resultado_ra228'] <= max_concentration) &
    (df['Taxa de Dose Máxima (µSv/h)'] <= max_dose_rate)
]

# Layout principal
col1, col2 = st.columns(2)

with col1:
    st.metric("Total de Amostras", len(df))
    st.metric("Amostras Filtradas", len(filtered_df))
    if len(df) > 0:
        st.metric("Percentual Utilizado", f"{(len(filtered_df)/len(df)*100):.1f}%")
    else:
        st.metric("Percentual Utilizado", "0%")

with col2:
    if len(filtered_df) > 0:
        st.metric("Ra-226 Máximo (Bq/g)", f"{filtered_df['Resultado_ra226'].max():.2f}")
        st.metric("Ra-228 Máximo (Bq/g)", f"{filtered_df['Resultado_ra228'].max():.2f}")
        st.metric("Dose Máxima (µSv/h)", f"{filtered_df['Taxa de Dose Máxima (µSv/h)'].max():.2f}")
    else:
        st.metric("Ra-226 Máximo (Bq/g)", "N/A")
        st.metric("Ra-228 Máximo (Bq/g)", "N/A")
        st.metric("Dose Máxima (µSv/h)", "N/A")

# Análise estatística
st.header("📈 Análise Estatística Detalhada")

if len(filtered_df) > 0:
    # Estatísticas descritivas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Ra-226 (Bq/g)")
        ra226_stats = filtered_df['Resultado_ra226'].describe()
        st.write(f"Média: {ra226_stats['mean']:.3f}")
        st.write(f"Mediana: {ra226_stats['50%']:.3f}")
        st.write(f"Desvio Padrão: {ra226_stats['std']:.3f}")
        st.write(f"Mínimo: {ra226_stats['min']:.3f}")
        st.write(f"Máximo: {ra226_stats['max']:.3f}")

    with col2:
        st.subheader("Ra-228 (Bq/g)")
        ra228_stats = filtered_df['Resultado_ra228'].describe()
        st.write(f"Média: {ra228_stats['mean']:.3f}")
        st.write(f"Mediana: {ra228_stats['50%']:.3f}")
        st.write(f"Desvio Padrão: {ra228_stats['std']:.3f}")
        st.write(f"Mínimo: {ra228_stats['min']:.3f}")
        st.write(f"Máximo: {ra228_stats['max']:.3f}")

    with col3:
        st.subheader("Taxa de Dose (µSv/h)")
        dose_stats = filtered_df['Taxa de Dose Máxima (µSv/h)'].describe()
        st.write(f"Média: {dose_stats['mean']:.3f}")
        st.write(f"Mediana: {dose_stats['50%']:.3f}")
        st.write(f"Desvio Padrão: {dose_stats['std']:.3f}")
        st.write(f"Mínimo: {dose_stats['min']:.3f}")
        st.write(f"Máximo: {dose_stats['max']:.3f}")

    # Visualizações
    st.header("📊 Visualizações")

    # Gráfico 1: Dispersão Ra-226 vs Taxa de Dose
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Scatter plot Ra-226
    scatter1 = ax1.scatter(filtered_df['Resultado_ra226'], 
                          filtered_df['Taxa de Dose Máxima (µSv/h)'],
                          alpha=0.6, c='blue', s=50)
    ax1.set_xlabel('Ra-226 (Bq/g)')
    ax1.set_ylabel('Taxa de Dose (µSv/h)')
    ax1.set_title('Ra-226 vs Taxa de Dose')
    ax1.grid(True, alpha=0.3)

    # Scatter plot Ra-228
    scatter2 = ax2.scatter(filtered_df['Resultado_ra228'], 
                          filtered_df['Taxa de Dose Máxima (µSv/h)'],
                          alpha=0.6, c='red', s=50)
    ax2.set_xlabel('Ra-228 (Bq/g)')
    ax2.set_ylabel('Taxa de Dose (µSv/h)')
    ax2.set_title('Ra-228 vs Taxa de Dose')
    ax2.grid(True, alpha=0.3)

    st.pyplot(fig)

    # Gráfico 2: Histogramas
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    # Histograma Ra-226
    ax1.hist(filtered_df['Resultado_ra226'], bins=20, alpha=0.7, color='blue', edgecolor='black')
    ax1.set_xlabel('Ra-226 (Bq/g)')
    ax1.set_ylabel('Frequência')
    ax1.set_title('Distribuição de Ra-226')
    ax1.grid(True, alpha=0.3)

    # Histograma Ra-228
    ax2.hist(filtered_df['Resultado_ra228'], bins=20, alpha=0.7, color='red', edgecolor='black')
    ax2.set_xlabel('Ra-228 (Bq/g)')
    ax2.set_ylabel('Frequência')
    ax2.set_title('Distribuição de Ra-228')
    ax2.grid(True, alpha=0.3)

    # Histograma Taxa de Dose
    ax3.hist(filtered_df['Taxa de Dose Máxima (µSv/h)'], bins=20, alpha=0.7, color='green', edgecolor='black')
    ax3.set_xlabel('Taxa de Dose (µSv/h)')
    ax3.set_ylabel('Frequência')
    ax3.set_title('Distribuição da Taxa de Dose')
    ax3.grid(True, alpha=0.3)

    st.pyplot(fig)

    # Análise de correlação
    st.header("🔗 Análise de Correlação")

    # Matriz de correlação
    corr_matrix = filtered_df[['Resultado_ra226', 'Resultado_ra228', 
                              'Taxa de Dose Máxima (µSv/h)']].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax,
                square=True, fmt='.3f', cbar_kws={"shrink": .8})
    ax.set_title('Matriz de Correlação')
    st.pyplot(fig)

    # Análise de regressão
    st.subheader("Análise de Regressão")

    col1, col2 = st.columns(2)

    with col1:
        # Regressão Ra-226 vs Dose
        slope_226, intercept_226, r_value_226, p_value_226, std_err_226 = stats.linregress(
            filtered_df['Resultado_ra226'], 
            filtered_df['Taxa de Dose Máxima (µSv/h)']
        )
        
        st.write("**Ra-226 vs Taxa de Dose:**")
        st.write(f"Coeficiente angular: {slope_226:.4f}")
        st.write(f"Coeficiente linear: {intercept_226:.4f}")
        st.write(f"R²: {r_value_226**2:.4f}")
        st.write(f"Valor-p: {p_value_226:.4f}")

    with col2:
        # Regressão Ra-228 vs Dose
        slope_228, intercept_228, r_value_228, p_value_228, std_err_228 = stats.linregress(
            filtered_df['Resultado_ra228'], 
            filtered_df['Taxa de Dose Máxima (µSv/h)']
        )
        
        st.write("**Ra-228 vs Taxa de Dose:**")
        st.write(f"Coeficiente angular: {slope_228:.4f}")
        st.write(f"Coeficiente linear: {intercept_228:.4f}")
        st.write(f"R²: {r_value_228**2:.4f}")
        st.write(f"Valor-p: {p_value_228:.4f}")

    # Análise de limites
    st.header("🎯 Análise de Limites Operacionais")

    # Calcular percentis
    dose_90th = np.percentile(filtered_df['Taxa de Dose Máxima (µSv/h)'], 90)
    dose_95th = np.percentile(filtered_df['Taxa de Dose Máxima (µSv/h)'], 95)
    dose_99th = np.percentile(filtered_df['Taxa de Dose Máxima (µSv/h)'], 99)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Percentil 90%", f"{dose_90th:.2f} µSv/h")

    with col2:
        st.metric("Percentil 95%", f"{dose_95th:.2f} µSv/h")

    with col3:
        st.metric("Percentil 99%", f"{dose_99th:.2f} µSv/h")

    # Recomendações
    st.header("💡 Recomendações e Conclusões")

    # Análise da viabilidade do limite de 5 µSv/h
    samples_below_5 = len(filtered_df[filtered_df['Taxa de Dose Máxima (µSv/h)'] <= 5.0])
    percentage_below_5 = (samples_below_5 / len(filtered_df)) * 100

    st.write(f"**Amostras com taxa de dose ≤ 5 µSv/h:** {samples_below_5} ({percentage_below_5:.1f}%)")

    if percentage_below_5 >= 95:
        st.success("✅ O limite de 5 µSv/h é viável para a maioria das amostras analisadas.")
    elif percentage_below_5 >= 80:
        st.warning("⚠️ O limite de 5 µSv/h pode ser aplicado, mas requer monitoramento cuidadoso.")
    else:
        st.error("❌ O limite de 5 µSv/h pode não ser adequado para estas condições operacionais.")

else:
    st.warning("⚠️ Não há dados suficientes para análise com os filtros atuais.")

# Download dos dados filtrados
st.header("📥 Download dos Dados")

if len(filtered_df) > 0:
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Baixar dados filtrados como CSV",
        data=csv,
        file_name="dados_radiometricos_filtrados.csv",
        mime="text/csv"
    )
else:
    st.info("Não há dados para download com os filtros atuais.")

# Informações adicionais
st.sidebar.header("ℹ️ Sobre a Análise")
st.sidebar.info("""
Esta análise foca na relação entre concentrações de Ra-226/Ra-228 
e taxas de dose, com ênfase no limite operacional de 5 µSv/h.

**Parâmetros padrão:**
- Concentração máxima: 8 Bq/g
- Taxa de dose máxima: 5 µSv/h

**Colunas utilizadas:**
- Resultado_ra226: Concentração de Ra-226
- Resultado_ra228: Concentração de Ra-228  
- Taxa de Dose Máxima (µSv/h): Taxa de dose medida
""")