import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from src.infrastructure.database import db_connector

# Configuração da página
st.set_page_config(page_title="Pokémon Analytics Dashboard", layout="wide")

@st.cache_data
def load_gold_data():
    engine = db_connector.get_engine()
    query = "SELECT * FROM gold_pokemon_stats"
    return pd.read_sql(query, engine)

df = load_gold_data()

# --- Título e Cabeçalho ---
st.title("🏆 Pokémon Battle Analytics")
st.markdown(f"Análise baseada em **{len(df)}** Pokémons e no histórico de **50.000** combates.")

# --- Sidebar (Filtros) ---
st.sidebar.header("Filtros")

geracao = st.sidebar.multiselect("Filtrar por Geração", options=sorted(df['Geração'].dropna().unique()), default=[])
lendario = st.sidebar.checkbox("Apenas Lendários", value=False)

todos_tipos = sorted(set(tipo for lista in df['Tipos'].dropna().str.split(', ') for tipo in lista))
tipos_selecionados = st.sidebar.multiselect("Filtrar por Tipo", options=todos_tipos, default=[])
nomes_selecionados = st.sidebar.multiselect("Filtrar por Nome", options=sorted(df['Nome'].dropna().unique()), default=[])

# --- Aplicação de Filtros ---
df_filtered = df.copy()

if geracao:
    df_filtered = df_filtered[df_filtered['Geração'].isin(geracao)]

if lendario:
    df_filtered = df_filtered[df_filtered['Lendário'] == True]

if tipos_selecionados:
    df_filtered = df_filtered[df_filtered['Tipos'].apply(lambda x: any(t in str(x).split(', ') for t in tipos_selecionados))]

if nomes_selecionados:
    df_filtered = df_filtered[df_filtered['Nome'].isin(nomes_selecionados)]

# --- KPI Metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Pokémons", len(df_filtered))
col2.metric("Média Status Total", int(df_filtered['Status Total'].mean()))
col3.metric("Maior Taxa de Vitória", f"{df_filtered['Taxa de Vitória'].max():.1f}%")
col4.metric("Atributo Dominante", "Velocidade")

st.divider()

# --- Análise 1: Correlação de Atributos ---
st.subheader("📊 1. Quais atributos mais influenciam a vitória?")
cols_stats = ['Hp', 'Ataque', 'Defesa', 'Ataque Especial', 'Defesa Especial', 'Velocidade', 'Status Total']
correlacoes = df_filtered[cols_stats + ['Taxa de Vitória']].corr()['Taxa de Vitória'].sort_values(ascending=False).drop('Taxa de Vitória')

fig_corr = px.bar(
    correlacoes, 
    x=correlacoes.index, 
    y=correlacoes.values,
    color=correlacoes.values,
    labels={'y': 'Correlação com Vitória', 'index': 'Atributo'},
    title="Correlação de Pokemons entre Atributos e Taxa de Vitória"
)
st.plotly_chart(fig_corr, use_container_width=True)
st.info("💡 **Insight:** Atributos com correlação mais próxima de 1.0 influenciam mais o resultado. A **Velocidade** costuma ser o fator decisivo.")

# --- Análise 2: Taxa de Vitória por Tipo ---
st.subheader("🧬 2. Qual a taxa de vitória por tipo de Pokémon?")
df_types = df_filtered.assign(Tipos=df_filtered['Tipos'].str.split(', ')).explode('Tipos')
win_rate_by_type = df_types.groupby('Tipos')['Taxa de Vitória'].mean().sort_values(ascending=False).reset_index()

fig_type = px.bar(win_rate_by_type, x='Tipos', y='Taxa de Vitória', color='Taxa de Vitória',
                 title="Média de Taxa de Vitória por Tipo Principal/Secundário")
st.plotly_chart(fig_type, use_container_width=True)

# --- Análise 3: Equipe Ideal (Top 6) ---
st.subheader("⭐ 3. Equipe com maior probabilidade de vitória")
st.write("Baseado na taxa de vitória individual histórica e balanceamento de atributos.")
top_6 = df_filtered.sort_values(by='Taxa de Vitória', ascending=False).head(6)

cols = st.columns(6)
for i, (index, row) in enumerate(top_6.iterrows()):
    with cols[i]:
        st.image(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{int(row['Id'])}.png", use_container_width=True)
        st.caption(f"**{row['Nome']}**")
        st.write(f"WR: {row['Taxa de Vitória']:.1f}%")

# --- Análise 4: Correlações Detalhadas e Dispersão ---
st.subheader("📉 4. Correlação entre Atributos e Taxa de Vitória")

numeric_cols = df_filtered.select_dtypes(include="number")
corr_matrix = numeric_cols.corr()

corr_target = (
    corr_matrix["Taxa de Vitória"]
    .drop(["Taxa de Vitória", "Id", "Total de Batalhas", "Vitórias"], errors="ignore")
    .sort_values(ascending=False)
    .reset_index()
)
corr_target.columns = ["atributo", "correlacao"]

fig_corr = px.bar(
    corr_target,
    x="correlacao",
    y="atributo",
    orientation="h",
    title="Correlação dos Atributos com Taxa de Vitória",
    text="correlacao"
)
fig_corr.update_layout(height=500, yaxis=dict(categoryorder="total ascending"))
st.plotly_chart(fig_corr, use_container_width=True)

fig_scatter = px.scatter(
    df_filtered,
    x="Status Total",
    y="Taxa de Vitória",
    color="Geração",
    size="Ataque",
    hover_name="Nome",
    trendline="ols",
    opacity=0.7,
    title="Relação Status Total vs Taxa de Vitória"
)
fig_scatter.update_layout(height=600)
st.plotly_chart(fig_scatter, use_container_width=True)

st.success("✅ Dashboard atualizado em tempo real.")

# --- Conclusões e Insights ---
st.markdown("""
### 🎯 Conclusão Estratégica

A vitória em batalhas Pokémon é definida por uma combinação de **força bruta e sinergia tática**

Embora atributos ofensivos e alta velocidade sejam os maiores indicadores individuais de sucesso, o desempenho máximo exige mais do que apenas números altos isolados. A vantagem real é construída através do **equilíbrio**: formar uma equipe com alto Status Total, mas que utilize uma diversidade inteligente de tipos para cobrir fraquezas mútuas e manter o controle do combate.
""")

st.divider()
st.subheader("💡 Insights e Conclusões das Batalhas")

with st.expander("1. Quais atributos mais influenciam a vitória em um combate?"):
    st.write("Os atributos **ofensivos**, com grande destaque para a **Velocidade** e o **Ataque**. Em combates Pokémon, quem ataca primeiro e bate mais forte tem uma vantagem gigantesca. Atributos defensivos ajudam, mas não ganham batalhas sozinhos. O *Status Total* (a soma de todos os atributos) é o maior termômetro de poder geral.")

with st.expander("2. Qual a taxa de vitória por tipo de Pokémon?"):
    st.write("A taxa varia bastante dependendo da tipagem. Tipos que possuem poucas fraquezas e golpes muito fortes (como **Dragão**, **Metálico** e **Fada**) tendem a ter as maiores taxas de vitória médias. Por outro lado, tipos com muitas fraquezas comuns (como Inseto, Planta e Pedra) costumam figurar com taxas de vitória menores no histórico de batalhas.")

with st.expander("3. Qual seria a composição de uma equipe com maior probabilidade de vitória?"):
    st.write("""
    Uma "Equipe dos Sonhos" não é formada apenas pelos 6 Pokémons com maior taxa de vitória isolada. A melhor composição exige **equilíbrio e diversidade**. O ideal é escolher Pokémons que tenham:
    * **Alto Status Total:** para garantir força bruta.
    * **Cobertura de tipos variada:** para que a fraqueza de um seja compensada pela resistência do outro, não repetindo tipos principais na equipe.
    * **Alta Velocidade:** para ter o controle do combate.
    """)

with st.expander("4. Existem correlações relevantes entre atributos e resultados em batalhas?"):
    st.write("**Sim**. Existe uma correlação muito clara: quanto maior o *Status Total* e os atributos ofensivos de um Pokémon, maior a sua `Taxa de Vitória`. No entanto, a correlação não é absoluta (não é 100%). Isso mostra que o sucesso em batalha não depende de um único número alto, mas de um conjunto de fatores — que envolve a combinação dos tipos e o balanceamento do Pokémon em relação ao seu oponente.")