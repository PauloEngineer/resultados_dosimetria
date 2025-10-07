import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configuração da página
st.set_page_config(page_title="Validação Limite 5µSv/h - GLP", layout="wide")

# Sidebar para navegação entre páginas
st.sidebar.title("📑 Navegação")
pagina_selecionada = st.sidebar.radio(
    "Selecione a página:",
    ["📊 Análise Principal", "🔬 Estudo Detalhado"]
)

# Função para carregar dados (mantida igual)
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

# Função para calcular estatísticas (mantida igual)
def calcular_estatisticas_radionuclideos(df):
    stats_dict = {}
    
    # Para Ra-226
    ra226_valid = df['Resultado_ra226'].notna()
    stats_dict['Ra226'] = {
        'total': ra226_valid.sum(),
        'ate_1bq': (df[ra226_valid]['Resultado_ra226'] <= 1.0).sum(),
        '1_3bq': ((df[ra226_valid]['Resultado_ra226'] > 1.0) & (df[ra226_valid]['Resultado_ra226'] <= 3.0)).sum(),
        '3_5bq': ((df[ra226_valid]['Resultado_ra226'] > 3.0) & (df[ra226_valid]['Resultado_ra226'] <= 5.0)).sum(),
        '5_8bq': ((df[ra226_valid]['Resultado_ra226'] > 5.0) & (df[ra226_valid]['Resultado_ra226'] <= 8.0)).sum(),
        'media': df[ra226_valid]['Resultado_ra226'].mean(),
        'maxima': df[ra226_valid]['Resultado_ra226'].max()
    }
    
    # Para Ra-228
    ra228_valid = df['Resultado_ra228'].notna()
    stats_dict['Ra228'] = {
        'total': ra228_valid.sum(),
        'ate_1bq': (df[ra228_valid]['Resultado_ra228'] <= 1.0).sum(),
        '1_3bq': ((df[ra228_valid]['Resultado_ra228'] > 1.0) & (df[ra228_valid]['Resultado_ra228'] <= 3.0)).sum(),
        '3_5bq': ((df[ra228_valid]['Resultado_ra228'] > 3.0) & (df[ra228_valid]['Resultado_ra228'] <= 5.0)).sum(),
        '5_8bq': ((df[ra228_valid]['Resultado_ra228'] > 5.0) & (df[ra228_valid]['Resultado_ra228'] <= 8.0)).sum(),
        'media': df[ra228_valid]['Resultado_ra228'].mean(),
        'maxima': df[ra228_valid]['Resultado_ra228'].max()
    }
    
    return stats_dict

# PÁGINA PRINCIPAL
if pagina_selecionada == "📊 Análise Principal":
    
    # Título da aplicação
    titulo = "📊 Validação do Limite Operacional de 5 µSv/h"
    sub_titulo = "Análise com base em concentrações até 8 Bq/g de Ra-226 e Ra-228"

    # Usa st.markdown para renderizar a tag <h1> com alinhamento centralizado
    st.markdown(f"<h1 style='text-align: center;'>{titulo}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{sub_titulo}</h3>", unsafe_allow_html=True)

    # Carregar dados
    df_original, df = load_data()

    # Sidebar com informações
    st.sidebar.header("🎯 Objetivo da Análise")
    st.sidebar.info("""
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

    # Calcular estatísticas para o dataframe em análise
    stats_radionuclideos = calcular_estatisticas_radionuclideos(df_analysis)

    # Layout principal - RESUMO EXECUTIVO SIMPLES
    st.header("📋 VISÃO GERAL DOS RESULTADOS")

    # PRIMEIRA LINHA: Métricas principais
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

    # SEGUNDA LINHA: Estatísticas dos Radionuclídeos
    st.subheader("📊 Estatísticas por Radionuclídeo")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Ra-226**")
        ra226 = stats_radionuclideos['Ra226']
        st.write(f"""
        - **Total de amostras:** {ra226['total']}
        - **Distribuição por faixa:**
          - ≤ 1.0 Bq/g: {ra226['ate_1bq']} amostras
          - 1.1 - 3.0 Bq/g: {ra226['1_3bq']} amostras  
          - 3.1 - 5.0 Bq/g: {ra226['3_5bq']} amostras
          - 5.1 - 8.0 Bq/g: {ra226['5_8bq']} amostras
        - **Média:** {ra226['media']:.2f} Bq/g
        - **Máxima:** {ra226['maxima']:.2f} Bq/g
        """)

    with col2:
        st.write("**Ra-228**")
        ra228 = stats_radionuclideos['Ra228']
        st.write(f"""
        - **Total de amostras:** {ra228['total']}
        - **Distribuição por faixa:**
          - ≤ 1.0 Bq/g: {ra228['ate_1bq']} amostras
          - 1.1 - 3.0 Bq/g: {ra228['1_3bq']} amostras  
          - 3.1 - 5.0 Bq/g: {ra228['3_5bq']} amostras
          - 5.1 - 8.0 Bq/g: {ra228['5_8bq']} amostras
        - **Média:** {ra228['media']:.2f} Bq/g
        - **Máxima:** {ra228['maxima']:.2f} Bq/g
        """)

    # ANÁLISE SIMPLIFICADA - O QUE OS NÚMEROS SIGNIFICAM
    st.header("O QUE OS NÚMEROS SIGNIFICAM PARA VOCÊ?")

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
            **MENOR OU IGUAL A 3.0**
            
            **{baixo_risco} amostras** ({perc_baixo:.1f}%)
            
            *Dose ≤ 3.0 µSv/h*
            """)
        
        with col2:
            medio_risco = len(df_analysis[(df_analysis['Taxa de Dose Máxima (µSv/h)'] > 3.0) & 
                                        (df_analysis['Taxa de Dose Máxima (µSv/h)'] <= 5.0)])
            perc_medio = (medio_risco / total_amostras * 100)
            st.warning(f"""
            **MAIOR QUE 3.0 E MENOR OU IGUAL 5.0**
            
            **{medio_risco} amostras** ({perc_medio:.1f}%)
            
            *Dose entre 3.1-5.0 µSv/h*
            """)
        
        with col3:
            alto_risco = len(df_analysis[df_analysis['Taxa de Dose Máxima (µSv/h)'] > 5.0])
            perc_alto = (alto_risco / total_amostras * 100)
            st.error(f"""
            **MAIOR QUE 5.0**
            
            **{alto_risco} amostras** ({perc_alto:.1f}%)
            
            *Dose > 5.0 µSv/h*
            """)
        
        # EXPLICAÇÃO DOS PERCENTIS COM LINGUAGEM SIMPLES
        st.subheader("Entendendo os Percentis")
        
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
        st.header("RECOMENDAÇÃO PRÁTICA")
        
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
            **⚠️ AVALIE COM CUIDADE O LIMITE DE 5 µSv/h**
            
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
        st.header("Relação: Concentração vs Dose")
        
        st.write(f"""
        **Contexto das amostras analisadas:**
        - **Ra-226:** {stats_radionuclideos['Ra226']['total']} amostras válidas
        - **Ra-228:** {stats_radionuclideos['Ra228']['total']} amostras válidas  
        - **Análise:** Vamos ver se amostras com maior concentração têm maior dose
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
    - **Amostras por radionuclídeo** mostram a distribuição real das concentrações
    """)

# PÁGINA DE ESTUDO DETALHADO
else:
    st.title("🔬 Estudo Detalhado - Metodologia e Parâmetros")
    
    st.markdown("""
    ## 📋 Metodologia Completa da Análise
    
    Esta página detalha os parâmetros e metodologias utilizados no estudo de validação do limite operacional.
    """)
    
    # Abas para organizar o conteúdo
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Objetivos", 
        "📊 Metodologia", 
        "⚙️ Parâmetros", 
        "📈 Análises"
    ])
    
    with tab1:
        st.header("🎯 Objetivos do Estudo")
        
        st.markdown("""
        ### **Objetivo Principal**
        Validar estatisticamente a adequação do **limite operacional de 5 µSv/h** para materiais 
        com concentrações de até **8 Bq/g** de Ra-226 e Ra-228.
        
        ### **Objetivos Específicos**
        1. **Avaliar a distribuição** das taxas de dose nas amostras
        2. **Calcular percentis** (P90, P95, P99) para entender o comportamento da maioria das amostras
        3. **Analisar a relação** entre concentração de radionuclídeos e taxa de dose
        4. **Fornecer recomendações** baseadas em evidências estatísticas
        5. **Criar critérios objetivos** para decisão sobre manutenção ou ajuste do limite
        """)
        
        st.info("""
        **💡 Contexto Operacional:** 
        Este estudo é crucial para garantir que os limites estabelecidos protegem adequadamente 
        os trabalhadores enquanto mantêm a viabilidade operacional.
        """)
    
    with tab2:
        st.header("📊 Metodologia Estatística")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Análise Descritiva")
            st.markdown("""
            - **Contagem por faixas** de concentração
            - **Cálculo de médias** e valores máximos
            - **Percentuais** de amostras dentro/acima do limite
            - **Distribuição** por radionuclídeo
            """)
            
            st.subheader("🎯 Critérios de Decisão")
            st.markdown("""
            - **✅ Mantém limite:** P95 ≤ 5.0 µSv/h E ≥95% dentro do limite
            - **⚠️ Avalia cuidado:** ≥90% dentro do limite  
            - **❌ Reavalia limite:** <90% dentro do limite
            """)
        
        with col2:
            st.subheader("📊 Análise de Percentis")
            st.markdown("""
            - **P90:** 90% das amostras têm dose ≤ X µSv/h
            - **P95:** 95% das amostras têm dose ≤ X µSv/h  
            - **P99:** 99% das amostras têm dose ≤ X µSv/h
            """)
            
            st.subheader("🎨 Visualização")
            st.markdown("""
            - **Histogramas** com zonas de risco coloridas
            - **Gráficos de dispersão** concentração vs dose
            - **Sistema semáforo** para classificação de risco
            - **Métricas visuais** para tomada de decisão
            """)
        
        st.success("""
        **✅ Abordagem Prática:** A metodologia foi desenvolvida para ser compreensível 
        por profissionais operacionais enquanto mantém rigor estatístico.
        """)
    
    with tab3:
        st.header("⚙️ Parâmetros e Configurações")
        
        st.subheader("🔧 Filtros Aplicados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### **Critérios de Inclusão**
            - **Concentração máxima:** ≤ 8 Bq/g para Ra-226 e Ra-228
            - **Dados completos:** Valores numéricos em todas as colunas analisadas
            - **Faixa operacional:** Concentrações relevantes para operação normal
            
            ### **Variáveis Analisadas**
            - **Taxa de Dose Máxima (µSv/h)**
            - **Resultado_ra226 (Bq/g)**
            - **Resultado_ra228 (Bq/g)**
            """)
        
        with col2:
            st.markdown("""
            ### **Limites de Referência**
            - **Limite operacional:** 5 µSv/h
            - **Zona de atenção:** 3.1 - 5.0 µSv/h
            - **Zona segura:** ≤ 3.0 µSv/h
            - **Zona crítica:** > 5.0 µSv/h
            
            ### **Faixas de Concentração**
            - **Baixa:** ≤ 1.0 Bq/g
            - **Média:** 1.1 - 3.0 Bq/g
            - **Alta:** 3.1 - 5.0 Bq/g
            - **Muito alta:** 5.1 - 8.0 Bq/g
            """)
        
        st.warning("""
        **⚠️ Nota Importante:** 
        Os parâmetros podem ser ajustados na sidebar da página principal para incluir 
        todos os dados ou apenas aqueles dentro da faixa especificada.
        """)
    
    with tab4:
        st.header("📈 Análises Realizadas")
        
        st.subheader("🔍 Tipos de Análise")
        
        analysis_types = {
            "📊 Análise de Distribuição": "Histogramas e estatísticas descritivas das taxas de dose",
            "🎯 Análise de Percentis": "Cálculo de P90, P95, P99 para entender a maioria das amostras",
            "📈 Análise de Correlação": "Relação entre concentração de radionuclídeos e taxa de dose",
            "⚠️ Análise de Risco": "Classificação em zonas de risco (verde, amarelo, vermelho)",
            "📋 Análise por Radionuclídeo": "Estatísticas separadas para Ra-226 e Ra-228"
        }
        
        for analysis, description in analysis_types.items():
            with st.expander(analysis):
                st.write(description)
        
        st.subheader("📋 Fluxo de Análise")
        
        st.markdown("""
        1. **Carregamento e limpeza** dos dados
        2. **Aplicação de filtros** conforme critérios estabelecidos
        3. **Cálculo de estatísticas** descritivas
        4. **Análise de percentis** e distribuição
        5. **Classificação de risco** baseada em critérios pré-definidos
        6. **Geração de recomendações** automatizadas
        7. **Visualização** dos resultados
        """)
        
        st.info("""
        **🔬 Rigor Científico:** 
        Todas as análises utilizam bibliotecas científicas consolidadas (pandas, numpy, scipy) 
        garantindo precisão e confiabilidade dos resultados.
        """)
    
    # Seção de referências
    st.markdown("---")
    st.header("📚 Referências e Base Técnica")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### **Normas e Diretrizes**
        - CNEN-NN-3.01: Diretrizes Básicas de Radioproteção
        - Normas Internacionais: IAEA Safety Standards
        - Boas Práticas: Guidelines internacionais para monitoramento
        """)
    
    with col2:
        st.markdown("""
        ### **Ferramentas Utilizadas**
        - **Python 3.x** com bibliotecas científicas
        - **Pandas:** Manipulação e análise de dados
        - **NumPy:** Cálculos numéricos e estatísticos
        - **Matplotlib/Seaborn:** Visualização de dados
        - **Streamlit:** Interface web interativa
        """)
    
    st.success("""
    **🎯 Próximos Passos:** 
    Esta metodologia pode ser expandida para incluir outros radionuclídeos, 
    diferentes faixas de concentração ou análises temporais.
    """)

# Rodapé comum
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Desenvolvido por**  
*Equipe de SMS e NORM*  
*Análise Estatística para Validação de Limites Operacionais*
""")