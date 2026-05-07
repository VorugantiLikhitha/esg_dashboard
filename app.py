import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_emissions_data, load_trends_data, get_summary_stats

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(
    page_title="ESG Emissions Dashboard",
    page_icon="🌱",
    layout="wide"
)

# ================================
# LOAD DATA (cached so it only loads once)
# ================================
@st.cache_data
def get_data():
    return load_emissions_data()

@st.cache_data
def get_trends():
    return load_trends_data()

df = get_data()
df_trends = get_trends()
stats = get_summary_stats(df)

# ================================
# SIDEBAR FILTERS
# ================================
st.sidebar.title("🌱 ESG Dashboard")
st.sidebar.markdown("---")

# Year filter
years = sorted(df['year'].unique())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

# State filter
states = ['All'] + sorted(df['state'].dropna().unique().tolist())
selected_state = st.sidebar.selectbox("Select State", states)

# Industry filter
industries = ['All'] + sorted(df['industry_sector'].dropna().unique().tolist())
selected_industry = st.sidebar.selectbox("Select Industry", industries)

# Gas type filter
gas_type = st.sidebar.selectbox(
    "Select Emission Type",
    ['Total Emissions', 'CO2', 'Methane (CH4)', 'Nitrous Oxide (N2O)']
)

gas_col_map = {
    'Total Emissions': 'total_emissions',
    'CO2': 'co2_emissions',
    'Methane (CH4)': 'ch4_emissions',
    'Nitrous Oxide (N2O)': 'n2o_emissions'
}
gas_col = gas_col_map[gas_type]

# ================================
# FILTER DATA
# ================================
df_filtered = df[
    (df['year'] >= selected_years[0]) &
    (df['year'] <= selected_years[1])
]
if selected_state != 'All':
    df_filtered = df_filtered[df_filtered['state'] == selected_state]
if selected_industry != 'All':
    df_filtered = df_filtered[df_filtered['industry_sector'] == selected_industry]

# ================================
# PAGE NAVIGATION
# ================================
page = st.sidebar.radio(
    "Navigate",
    ["📊 Overview", "🏭 By Industry", "📈 Trends", "🗺️ Map", "🤖 AI Chatbot"]
)

# ================================
# PAGE 1 - OVERVIEW
# ================================
if page == "📊 Overview":
    st.title("🌱 ESG Emissions Dashboard")
    st.markdown("**EPA Greenhouse Gas Reporting Program — 2010 to 2023**")
    st.markdown("---")

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Facilities", f"{df_filtered['facility_id'].nunique():,}")
    with col2:
        total = df_filtered[gas_col].sum() / 1e6
        st.metric(f"{gas_type}", f"{total:.1f}M metric tons CO2e")
    with col3:
        st.metric("Top Emitting State",
                  df_filtered.groupby('state')[gas_col].sum().idxmax()
                  if len(df_filtered) > 0 else "N/A")
    with col4:
        st.metric("Top Industry",
                  df_filtered.groupby('industry_sector')[gas_col].sum().idxmax()
                  if len(df_filtered) > 0 else "N/A")

    st.markdown("---")

    # Top 10 emitting states bar chart
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Emitting States")
        top_states = (df_filtered.groupby('state')[gas_col]
                      .sum().nlargest(10).reset_index())
        fig = px.bar(top_states, x='state', y=gas_col,
                     color=gas_col, color_continuous_scale='Reds',
                     labels={gas_col: 'Emissions (metric tons CO2e)'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Emissions by Industry")
        by_industry = (df_filtered.groupby('industry_sector')[gas_col]
                       .sum().nlargest(8).reset_index())
        fig2 = px.pie(by_industry, values=gas_col,
                      names='industry_sector', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

# ================================
# PAGE 2 - BY INDUSTRY
# ================================
elif page == "🏭 By Industry":
    st.title("🏭 Emissions by Industry")
    st.markdown("---")

    by_industry = (df_filtered.groupby(['industry_sector', 'year'])[gas_col]
                   .sum().reset_index())
    fig = px.bar(by_industry, x='industry_sector', y=gas_col,
                 color='year', barmode='group',
                 labels={gas_col: 'Emissions (metric tons CO2e)',
                         'industry_sector': 'Industry'},
                 title=f"{gas_type} by Industry Over Time")
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Raw Data")
    st.dataframe(by_industry)

# ================================
# PAGE 3 - TRENDS
# ================================
elif page == "📈 Trends":
    st.title("📈 Emissions Trends Over Time")
    st.markdown("---")

    yearly = (df_filtered.groupby('year')[gas_col]
              .sum().reset_index())
    fig = px.line(yearly, x='year', y=gas_col,
                  markers=True,
                  labels={gas_col: 'Emissions (metric tons CO2e)',
                          'year': 'Year'},
                  title=f"Total {gas_type} 2010–2023")
    fig.update_traces(line_color='green', line_width=3)
    st.plotly_chart(fig, use_container_width=True)

    # By industry trend
    st.subheader("Trend by Industry")
    industry_trend = (df_filtered.groupby(['year', 'industry_sector'])[gas_col]
                      .sum().reset_index())
    fig2 = px.line(industry_trend, x='year', y=gas_col,
                   color='industry_sector', markers=True,
                   labels={gas_col: 'Emissions (metric tons CO2e)'})
    st.plotly_chart(fig2, use_container_width=True)

# ================================
# PAGE 4 - MAP
# ================================
elif page == "🗺️ Map":
    st.title("🗺️ Facility Map")
    st.markdown("---")

    df_map = df_filtered.dropna(subset=['latitude', 'longitude'])
    df_map = df_map[df_map[gas_col] > 0]

    fig = px.scatter_mapbox(
        df_map,
        lat='latitude',
        lon='longitude',
        size=gas_col,
        color=gas_col,
        hover_name='facility_name',
        hover_data=['state', 'industry_sector', gas_col],
        color_continuous_scale='Reds',
        mapbox_style='carto-positron',
        zoom=3,
        title=f"Facility {gas_type} Map"
    )
    st.plotly_chart(fig, use_container_width=True)

# ================================
# PAGE 5 - AI CHATBOT (coming next)
# ================================
elif page == "🤖 AI Chatbot":
    st.title("🤖 ESG AI Assistant")
    st.markdown("Ask me anything about the EPA emissions dataset!")
    st.markdown("---")

    from chatbot import ask_chatbot

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "messages_display" not in st.session_state:
        st.session_state.messages_display = []

    # Display chat history
    for msg in st.session_state.messages_display:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    question = st.chat_input("Ask about emissions data...")

    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_chatbot(
                    question,
                    df_filtered,
                    st.session_state.chat_history
                )
            st.write(response)

        st.session_state.chat_history.append(
            {"role": "user", "content": question}
        )
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )
        st.session_state.messages_display.append(
            {"role": "user", "content": question}
        )
        st.session_state.messages_display.append(
            {"role": "assistant", "content": response}
        )