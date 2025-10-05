import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configuração da página
st.set_page_config(page_title="Validação Limite 5µSv/h - GLP", layout="wide")

# Título da aplicação
st.title("📊 Validação do Limite Operacional de 5 µSv/h")
st.subheader("Análise com base em concentrações até 8 Bq/g de Ra-226 e Ra-228")

# Processamento dos dados
@st.cache_data
def load_data():
    # Carregar os dados do arquivo Excel
    df = pd.read_excel("Resultados de análises radiométricas - GLP.xlsx", sheet_name="Macaé")
    
    # Limpeza e preparação dos dados
    df.columns = [str(col).strip() for col in df.columns]
    
    # Converter colunas numéricas
    numeric_columns = ['Taxa de Dose Máxima (µSv/h)', 'Resultado_ra226', 'Resultado_ra228']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # FILTRAR APENAS DADOS ATÉ 8 Bq/g (conforme solicitação do gerente)
    df_filtrado = df[
        (df['Resultado_ra226'] <= 8.0) & 
        (df['Resultado_ra228'] <= 8.0) &
        (df['Resultado_ra226'].notna()) &
        (df['Resultado_ra228'].notna()) &
        (df['Taxa de Dose Máxima (µSv/h)'].notna())
    ].copy()
    
    return df, df_filtrado

df_original, df = load_data()

# Sidebar com informações
st.sidebar.header("🎯 Objetivo da Análise")
st.sidebar.info("""
**Solicitação do Gerente:**
Validar se o limite de 5 µSv/h é adequado, analisando dados com concentrações até 8 Bq/g.
""")

st.sidebar.header("🔧 Configurações")
show_all_data = st.sidebar.checkbox("Mostrar análise com todos os dados", value=False)

if show_all_data:
    df_analysis = df_original
    st.sidebar.warning("⚠️ Mostrando TODOS os dados (incluindo acima de 8 Bq/g)")
else:
    df_analysis = df
    st.sidebar.success("✅ Analisando apenas dados ≤ 8 Bq/g")

# Layout principal - RESUMO EXECUTIVO SIMPLES
st.header("📋 VISÃO GERAL DOS RESULTADOS")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_amostras = len(df_analysis)
    st.metric("Total de Amostras Analisadas", total_amostras)

with col2:
    amostras_ate_5usv = len(df_analysis[df_analysis['Taxa de Dose Máxima (µSv/h)'] <= 5.0])
    percentual_ate_5usv = (amostras_ate_5usv / total_amostras * 100) if total_amostras > 0 else 0
    st.metric("Dentro do Limite", f"{amostras_ate_5usv} ({percentual_ate_5usv:.1f}%)")

with col3:
    amostras_acima_5usv = len(df_analysis[df_analysis['Taxa de Dose Máxima (µSv/h)'] > 5.0])
    percentual_acima_5usv = (amostras_acima_5usv / total_amostras * 100) if total_amostras > 0 else 0
    st.metric("Acima do Limite", f"{amostras_acima_5usv} ({percentual_acima_5usv:.1f}%)")

with col4:
    max_dose = df_analysis['Taxa de Dose Máxima (µSv/h)'].max() if total_amostras > 0 else 0
    st.metric("Maior Dose Encontrada", f"{max_dose:.2f} µSv/h")

# ANÁLISE SIMPLIFICADA - O QUE OS NÚMEROS SIGNIFICAM
st.header("🎯 O QUE OS NÚMEROS SIGNIFICAM PARA VOCÊ?")

if total_amostras > 0:
    # Cálculos importantes
    dose_90th = np.percentile(df_analysis['Taxa de Dose Máxima (µSv/h)'], 90)
    dose_95th = np.percentile(df_analysis['Taxa de Dose Máxima (µSv/h)'], 95)
    dose_99th = np.percentile(df_analysis['Taxa de Dose Máxima (µSv/h)'], 99)
    
    # VISUALIZAÇÃO SIMPLES COM SEMÁFORO
    st.subheader("📊 Situação das Amostras")
    
    # Criar colunas para o semáforo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        baixo_risco = len(df_analysis[df_analysis['Taxa de Dose Máxima (µSv/h)'] <= 3.0])
        perc_baixo = (baixo_risco / total_amostras * 100)
        st.success(f"""
        **✅ BAIXO RISCO**
        
        **{baixo_risco} amostras** ({perc_baixo:.1f}%)
        
        *Dose ≤ 3.0 µSv/h*
        """)
    
    with col2:
        medio_risco = len(df_analysis[(df_analysis['Taxa de Dose Máxima (µSv/h)'] > 3.0) & 
                                    (df_analysis['Taxa de Dose Máxima (µSv/h)'] <= 5.0)])
        perc_medio = (medio_risco / total_amostras * 100)
        st.warning(f"""
        **⚠️ ATENÇÃO**
        
        **{medio_risco} amostras** ({perc_medio:.1f}%)
        
        *Dose entre 3.1-5.0 µSv/h*
        """)
    
    with col3:
        alto_risco = len(df_analysis[df_analysis['Taxa de Dose Máxima (µSv/h)'] > 5.0])
        perc_alto = (alto_risco / total_amostras * 100)
        st.error(f"""
        **❌ ALTO RISCO**
        
        **{alto_risco} amostras** ({perc_alto:.1f}%)
        
        *Dose > 5.0 µSv/h*
        """)
    
    # EXPLICAÇÃO DOS PERCENTIS COM LINGUAGEM SIMPLES
    st.subheader("💡 Entendendo os Percentis")
    
    st.write("""
    **Pense nos percentis como forma de responder:**
    - **"Quantas amostras ficam abaixo de cada valor de dose?"**
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **📈 O que os percentis mostram:**
        
        **P90 = {dose_90th:.2f} µSv/h**  
        👉 90% das amostras têm dose ≤ {dose_90th:.2f} µSv/h
        
        **P95 = {dose_95th:.2f} µSv/h**  
        👉 95% das amostras têm dose ≤ {dose_95th:.2f} µSv/h
        
        **P99 = {dose_99th:.2f} µSv/h**  
        👉 99% das amostras têm dose ≤ {dose_99th:.2f} µSv/h
        """)
    
    with col2:
        st.write("""
        **🎯 Comparação com exemplos do dia a dia:**
        
        | Situação | Equivalente na Análise |
        |----------|------------------------|
        | **95% chegam no trabalho até 8h** | P95 = 8h |
        | **90% dos produtos pesam até 1kg** | P90 = 1kg |
        | **95% têm dose ≤ 4.5 µSv/h** | P95 = 4.5 µSv/h |
        """)
    
    # GRÁFICO SIMPLES DE DISTRIBUIÇÃO
    st.subheader("📊 Visualização da Distribuição das Doses")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Criar áreas coloridas
    ax.axvspan(0, 3.0, alpha=0.3, color='green', label='Baixo Risco (≤ 3.0 µSv/h)')
    ax.axvspan(3.0, 5.0, alpha=0.3, color='yellow', label='Atenção (3.1-5.0 µSv/h)')
    ax.axvspan(5.0, max(10, max_dose), alpha=0.3, color='red', label='Alto Risco (> 5.0 µSv/h)')
    
    # Histograma
    n, bins, patches = ax.hist(df_analysis['Taxa de Dose Máxima (µSv/h)'], 
                              bins=15, alpha=0.7, color='blue', edgecolor='black')
    
    # Linhas dos percentis
    ax.axvline(x=dose_90th, color='orange', linestyle='--', linewidth=2, 
               label=f'90% das amostras ≤ {dose_90th:.1f} µSv/h')
    ax.axvline(x=dose_95th, color='red', linestyle='--', linewidth=2, 
               label=f'95% das amostras ≤ {dose_95th:.1f} µSv/h')
    
    ax.set_xlabel('Taxa de Dose (µSv/h)')
    ax.set_ylabel('Número de Amostras')
    ax.set_title('Distribuição das Taxas de Dose - Visão Simplificada')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)

    # RECOMENDAÇÃO PRÁTICA E CLARA
    st.header("🎯 RECOMENDAÇÃO PRÁTICA")
    
    if percentual_ate_5usv >= 95 and dose_95th <= 5.0:
        st.success(f"""
        **✅ MANTENHA O LIMITE DE 5 µSv/h**
        
        **Por que essa recomendação?**
        
        ✅ **{percentual_ate_5usv:.1f}% das amostras** estão DENTRO do limite  
        ✅ **95% das amostras** têm dose ≤ **{dose_95th:.2f} µSv/h**  
        ✅ **Margem de segurança** adequada  
        ✅ Limite está **funcionando bem**
        
        **Próximos passos:** Continue monitorando normalmente.
        """)
        
    elif percentual_ate_5usv >= 90:
        st.warning(f"""
        **⚠️ AVALIE COM CUIDADO O LIMITE DE 5 µSv/h**
        
        **Por que essa recomendação?**
        
        ⚠️ **{percentual_ate_5usv:.1f}% das amostras** estão dentro do limite  
        ⚠️ **95% das amostras** têm dose ≤ **{dose_95th:.2f} µSv/h**  
        ⚠️ **Pouca margem** de segurança  
        ⚠️ **{amostras_acima_5usv} amostras** ({percentual_acima_5usv:.1f}%) acima do limite
        
        **Próximos passos:** Aumente a frequência de monitoramento.
        """)
        
    else:
        st.error(f"""
        **❌ REAVALIE O LIMITE DE 5 µSv/h**
        
        **Por que essa recomendação?**
        
        ❌ Apenas **{percentual_ate_5usv:.1f}%** dentro do limite  
        ❌ **{amostras_acima_5usv} amostras** ({percentual_acima_5usv:.1f}%) acima do limite  
        ❌ **95% das amostras** têm dose ≤ **{dose_95th:.2f} µSv/h**  
        ❌ **Risco frequente** de ultrapassar o limite
        
        **Próximos passos:** Considere ajustar o limite ou melhorar controles.
        """)

    # RELAÇÃO ENTRE CONCENTRAÇÃO E DOSE (SIMPLES)
    st.header("🔍 Relação: Concentração vs Dose")
    
    st.write("""
    **Vamos ver se amostras com maior concentração têm maior dose:**
    """)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Ra-226 vs Dose
    scatter1 = ax1.scatter(df_analysis['Resultado_ra226'], 
                          df_analysis['Taxa de Dose Máxima (µSv/h)'],
                          alpha=0.6, c='blue', s=50)
    ax1.axhline(y=5.0, color='red', linestyle='--', linewidth=2, label='Limite 5 µSv/h')
    ax1.set_xlabel('Concentração de Ra-226 (Bq/g)')
    ax1.set_ylabel('Taxa de Dose (µSv/h)')
    ax1.set_title('Ra-226: Maior concentração = Maior dose?')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Ra-228 vs Dose
    scatter2 = ax2.scatter(df_analysis['Resultado_ra228'], 
                          df_analysis['Taxa de Dose Máxima (µSv/h)'],
                          alpha=0.6, c='red', s=50)
    ax2.axhline(y=5.0, color='red', linestyle='--', linewidth=2, label='Limite 5 µSv/h')
    ax2.set_xlabel('Concentração de Ra-228 (Bq/g)')
    ax2.set_ylabel('Taxa de Dose (µSv/h)')
    ax2.set_title('Ra-228: Maior concentração = Maior dose?')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    st.pyplot(fig)

else:
    st.warning("Não há dados para análise com os critérios selecionados.")

# DOWNLOAD SIMPLIFICADO
st.header("📥 Baixar Dados da Análise")

if len(df_analysis) > 0:
    csv = df_analysis[['Taxa de Dose Máxima (µSv/h)', 'Resultado_ra226', 'Resultado_ra228']].to_csv(index=False)
    st.download_button(
        label="📄 Baixar planilha com os dados analisados",
        data=csv,
        file_name="analise_limite_5usvh.csv",
        mime="text/csv"
    )

# RODAPÉ COM EXPLICAÇÕES
st.markdown("---")
st.markdown("""
**💡 Dicas para entender melhor:**
- **Percentis** mostram "até que valor" vai a maioria das amostras
- **P95** responde: "95% das amostras têm dose menor que quanto?"
- **Limite adequado** = P95 bem abaixo de 5.0 µSv/h + alta % dentro do limite
""")