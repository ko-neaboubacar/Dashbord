import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="📊 Dashboard des Ventes",
    page_icon="📊",
    layout="wide"
)

# Palette de couleurs personnalisée
COLORS = {
    'primary': ['#0085ff', '#69b4ff', '#e0ffff'],
    'accent': ['#006fff', '#e1ffff'],
    'text': ['#FFFFFF', '#9e9e9e'],
    'bg': ['#1E1E1E', '#2d2d2d', '#454545']
}

# CSS personnalisé
st.markdown(f"""
    <style>
    :root {{
        --primary-100: {COLORS['primary'][0]};
        --primary-200: {COLORS['primary'][1]};
        --primary-300: {COLORS['primary'][2]};
        --accent-100: {COLORS['accent'][0]};
        --accent-200: {COLORS['accent'][1]};
        --text-100: {COLORS['text'][0]};
        --text-200: {COLORS['text'][1]};
        --bg-100: {COLORS['bg'][0]};
        --bg-200: {COLORS['bg'][1]};
        --bg-300: {COLORS['bg'][2]};
    }}
    .stApp {{
        background-color: var(--bg-100);
        color: var(--text-100);
    }}
    </style>
""", unsafe_allow_html=True)

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv('Données_propres (1).csv')
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['revenue'] = df['quantity'] * df['price']
    df['month_year'] = df['order_date'].dt.to_period('M').astype(str)
    return df

df = load_data()

# Titre du tableau de bord
st.title("📊 Tableau de Bord des Ventes")
st.markdown("Analyse interactive des données de vente en ligne")

# KPI
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Chiffre d'affaires total", f"${df['revenue'].sum():,.0f}")
with col2:
    st.metric("📦 Commandes", len(df))
with col3:
    st.metric("👥 Clients", df['customer_name'].nunique())
with col4:
    st.metric("🛍️ Produits", df['product'].nunique())

# Filtres
st.sidebar.header("🔍 Filtres")
date_range = st.sidebar.date_input(
    "📅 Période",
    value=(df['order_date'].min().date(), df['order_date'].max().date()),
    min_value=df['order_date'].min().date(),
    max_value=df['order_date'].max().date()
)
products = st.sidebar.multiselect("📦 Produits", df['product'].unique(), default=df['product'].unique())
cities = st.sidebar.multiselect("🏙️ Villes", df['city'].unique(), default=df['city'].unique())

if len(date_range) == 2:
    filtered_df = df[
        (df['order_date'].dt.date >= date_range[0]) & 
        (df['order_date'].dt.date <= date_range[1]) & 
        (df['product'].isin(products)) & 
        (df['city'].isin(cities))
    ]
else:
    filtered_df = df[(df['product'].isin(products)) & (df['city'].isin(cities))]

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Aperçu", "📊 Analyse Produits", "🌍 Analyse Géographique"])

with tab1:
    st.header("📈 Aperçu Global")
    # Pie Chart: Méthodes de paiement
    st.subheader("💳 Méthodes de Paiement")
    fig1 = px.pie(
        filtered_df,
        names='payment_method',
        hole=0.3,
        color_discrete_sequence=COLORS['primary']
    )
    fig1.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color=COLORS['bg'][0], width=2))
    )
    fig1.update_layout(
        plot_bgcolor=COLORS['bg'][1],
        paper_bgcolor=COLORS['bg'][0],
        font_color=COLORS['text'][0],
        legend=dict(bgcolor=COLORS['bg'][1], font=dict(color=COLORS['text'][0]))
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Line Chart: CA par mois
    st.subheader("📈 Évolution du Chiffre d'Affaires")
    revenue_by_month = filtered_df.groupby('month_year')['revenue'].sum().reset_index()
    fig2 = px.line(
        revenue_by_month,
        x='month_year',
        y='revenue',
        markers=True,
        color_discrete_sequence=[COLORS['accent'][0]]
    )
    fig2.update_layout(
        xaxis_title='Mois',
        yaxis_title='Chiffre d\'affaires ($)',
        plot_bgcolor=COLORS['bg'][1],
        paper_bgcolor=COLORS['bg'][0],
        font_color=COLORS['text'][0],
        hovermode='x unified'
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("📊 Analyse par Produit")
    # Scatter: Quantité vs Prix
    st.subheader("📊 Relation Quantité/Prix")
    fig3 = px.scatter(
        filtered_df,
        x='quantity',
        y='price',
        color='product',
        hover_data=['order_id', 'customer_name', 'city'],
        color_discrete_sequence=COLORS['primary'] + COLORS['accent']
    )
    fig3.update_layout(
        xaxis_title='Quantité',
        yaxis_title='Prix ($)',
        plot_bgcolor=COLORS['bg'][1],
        paper_bgcolor=COLORS['bg'][0],
        font_color=COLORS['text'][0],
        legend=dict(bgcolor=COLORS['bg'][1], font=dict(color=COLORS['text'][0]))
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Area: Ventes par produit
    st.subheader("📦 Ventes par Produit")
    sales_by_product = filtered_df.groupby(['month_year', 'product'])['quantity'].sum().reset_index()
    fig4 = px.area(
        sales_by_product,
        x='month_year',
        y='quantity',
        color='product',
        color_discrete_sequence=COLORS['primary'] + COLORS['accent']
    )
    fig4.update_layout(
        xaxis_title='Mois',
        yaxis_title='Quantité vendue',
        plot_bgcolor=COLORS['bg'][1],
        paper_bgcolor=COLORS['bg'][0],
        font_color=COLORS['text'][0],
        legend=dict(bgcolor=COLORS['bg'][1], font=dict(color=COLORS['text'][0]))
    )
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.header("🌍 Analyse Géographique")
    # Bar: Commandes par ville
    st.subheader("🏙️ Commandes par Ville")
    city_counts = filtered_df.groupby('city').size().reset_index(name='count')
    fig5 = px.bar(
        city_counts,
        x='city',
        y='count',
        color='city',
        color_discrete_sequence=COLORS['primary'] + COLORS['accent']
    )
    fig5.update_layout(
        xaxis_title='Ville',
        yaxis_title='Nombre de commandes',
        xaxis={'categoryorder': 'total descending'},
        plot_bgcolor=COLORS['bg'][1],
        paper_bgcolor=COLORS['bg'][0],
        font_color=COLORS['text'][0],
        showlegend=False
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Bar: CA par ville
    st.subheader("💰 Chiffre d'Affaires par Ville")
    revenue_by_city = filtered_df.groupby('city')['revenue'].sum().reset_index()
    fig6 = px.bar(
        revenue_by_city,
        x='city',
        y='revenue',
        color='city',
        color_discrete_sequence=COLORS['primary'] + COLORS['accent']
    )
    fig6.update_layout(
        xaxis_title='Ville',
        yaxis_title='Chiffre d\'affaires ($)',
        xaxis={'categoryorder': 'total descending'},
        plot_bgcolor=COLORS['bg'][1],
        paper_bgcolor=COLORS['bg'][0],
        font_color=COLORS['text'][0],
        showlegend=False
    )
    st.plotly_chart(fig6, use_container_width=True)

# Pied de page
st.markdown("---")
st.markdown(f"🔄 Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown("📊 Tableau de bord créé avec Streamlit et Plotly Express")
