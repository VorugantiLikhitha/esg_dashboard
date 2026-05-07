import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_emissions_data, get_summary_stats

st.set_page_config(
    page_title="ESG Emissions Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

.stApp { background: #060d1a; color: #e2e8f0; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070e1c 0%, #0a1628 100%);
    border-right: 1px solid rgba(56,189,248,0.1);
}

.logo-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #38bdf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.logo-sub {
    font-size: 0.65rem;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 2px;
}

.kpi-card {
    background: linear-gradient(135deg, #0d1f35 0%, #0f2640 100%);
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 20px;
    padding: 28px 24px;
    position: relative;
    overflow: hidden;
    margin-bottom: 8px;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #38bdf8, #34d399);
}

.kpi-icon {
    font-size: 1.8rem;
    margin-bottom: 12px;
    display: block;
}

.kpi-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #f0f9ff;
    line-height: 1;
    margin-bottom: 6px;
}

.kpi-label {
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 500;
}

.kpi-delta {
    font-size: 0.8rem;
    color: #34d399;
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.page-header {
    margin-bottom: 32px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(56,189,248,0.08);
}

.page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #f0f9ff;
    margin-bottom: 4px;
}

.page-sub {
    font-size: 0.85rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

.chart-card {
    background: #0d1f35;
    border: 1px solid rgba(56,189,248,0.1);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 16px;
}

.chart-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
}

.suggest-btn {
    background: rgba(56,189,248,0.05) !important;
    border: 1px solid rgba(56,189,248,0.2) !important;
    border-radius: 12px !important;
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
    padding: 8px 12px !important;
}

div[data-testid="stButton"] > button {
    background: rgba(56,189,248,0.06);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 10px;
    color: #94a3b8;
    font-size: 0.8rem;
    transition: all 0.2s;
    width: 100%;
}

div[data-testid="stButton"] > button:hover {
    background: rgba(56,189,248,0.15);
    border-color: #38bdf8;
    color: #e2e8f0;
}

.stRadio > div { gap: 4px; }
.stRadio label {
    background: rgba(255,255,255,0.02);
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 0.85rem;
}

div[data-testid="stChatMessage"] {
    background: #0d1f35;
    border: 1px solid rgba(56,189,248,0.1);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# Plot theme
DARK = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(13,31,53,0.5)',
    font=dict(family='Inter', color='#64748b', size=11),
    xaxis=dict(gridcolor='rgba(56,189,248,0.06)', linecolor='rgba(56,189,248,0.1)', tickcolor='#334155', tickfont=dict(color='#64748b')),
    yaxis=dict(gridcolor='rgba(56,189,248,0.06)', linecolor='rgba(56,189,248,0.1)', tickcolor='#334155', tickfont=dict(color='#64748b')),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#64748b', size=11)),
    title_font=dict(family='Space Grotesk', color='#94a3b8', size=13)
)

CYAN_SCALE = [[0,'#0c2a4a'],[0.3,'#0e4272'],[0.6,'#1e6bb8'],[0.8,'#38bdf8'],[1,'#7dd3fc']]
COLORS = ['#38bdf8','#34d399','#f59e0b','#f472b6','#a78bfa','#fb7185','#4ade80','#facc15']

@st.cache_data
def get_data():
    return load_emissions_data()

df = get_data()
stats = get_summary_stats(df)

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="logo-text">🌍 ESG Intel</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">EPA GHGRP · 2010–2023</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    years = sorted(df['year'].unique())
    y1, y2 = st.slider("Year Range", int(min(years)), int(max(years)), (2010, 2023))

    states = ['All States'] + sorted(df['state'].dropna().unique().tolist())
    sel_state = st.selectbox("State", states)

    industries = ['All Industries'] + sorted(df['industry_sector'].dropna().unique().tolist())
    sel_industry = st.selectbox("Industry", industries)

    gas_map = {
        'Total Emissions': 'total_emissions',
        'CO₂': 'co2_emissions',
        'CH₄ Methane': 'ch4_emissions',
        'N₂O Nitrous Oxide': 'n2o_emissions'
    }
    sel_gas = st.selectbox("Emission Type", list(gas_map.keys()))
    gas_col = gas_map[sel_gas]

    st.markdown("---")
    page = st.radio("Navigate", [
        "📊 Overview",
        "🏭 By Industry",
        "📈 Trends",
        "🗺️ Heatmap",
        "🤖 AI Assistant"
    ])

# FILTER
df_f = df[(df['year'] >= y1) & (df['year'] <= y2)].copy()
if sel_state != 'All States':
    df_f = df_f[df_f['state'] == sel_state]
if sel_industry != 'All Industries':
    df_f = df_f[df_f['industry_sector'] == sel_industry]

# ── PAGE 1: OVERVIEW ──────────────────────────────────────
if page == "📊 Overview":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Emissions Intelligence</div>
        <div class="page-sub">EPA Greenhouse Gas Reporting Program · 2010–2023</div>
    </div>""", unsafe_allow_html=True)

    total = df_f[gas_col].sum()
    facilities = df_f['facility_id'].nunique()
    top_state = df_f.groupby('state')[gas_col].sum().idxmax() if len(df_f) > 0 else 'N/A'
    top_ind = df_f.groupby('industry_sector')[gas_col].sum().idxmax() if len(df_f) > 0 else 'N/A'
    avg = df_f[gas_col].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "🏭", f"{facilities:,}", "Facilities", "Unique reporting sites"),
        (c2, "💨", f"{total/1e9:.1f}B", "Total Emissions", "Metric tons CO₂e"),
        (c3, "📍", top_state, "Top State", "Highest emitter"),
        (c4, "🏗️", top_ind[:12]+"..." if len(top_ind)>12 else top_ind, "Top Industry", "Highest sector"),
        (c5, "📊", f"{avg/1e3:.0f}K", "Avg/Facility", "Metric tons CO₂e"),
    ]
    for col, icon, val, label, sub in cards:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <span class="kpi-icon">{icon}</span>
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-delta">↗ {sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="chart-title">Top 10 Emitting States</div>', unsafe_allow_html=True)
        top_states = df_f.groupby('state')[gas_col].sum().nlargest(10).reset_index()
        fig = px.bar(top_states, x='state', y=gas_col,
                     color=gas_col, color_continuous_scale=CYAN_SCALE)
        fig.update_layout(**DARK, height=320)
        fig.update_coloraxes(showscale=False)
        fig.update_traces(marker_line_width=0, marker_cornerradius=4)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="chart-title">Sector Breakdown</div>', unsafe_allow_html=True)
        by_ind = df_f.groupby('industry_sector')[gas_col].sum().nlargest(7).reset_index()
        fig2 = px.pie(by_ind, values=gas_col, names='industry_sector',
                      hole=0.6, color_discrete_sequence=COLORS)
        fig2.update_layout(**DARK, height=320)
        fig2.update_traces(textinfo='percent', textfont_size=10,
                           marker=dict(line=dict(color='#060d1a', width=2)))
        st.plotly_chart(fig2, use_container_width=True)

    # Yearly trend mini chart
    st.markdown('<div class="chart-title">Emissions Over Time</div>', unsafe_allow_html=True)
    yr = df_f.groupby('year')[gas_col].sum().reset_index()
    fig3 = go.Figure(go.Scatter(
        x=yr['year'], y=yr[gas_col],
        fill='tozeroy', fillcolor='rgba(56,189,248,0.07)',
        line=dict(color='#38bdf8', width=2.5),
        marker=dict(size=6, color='#7dd3fc',
                    line=dict(color='#38bdf8', width=1.5))
    ))
    fig3.update_layout(**DARK, height=200)
    st.plotly_chart(fig3, use_container_width=True)

# ── PAGE 2: BY INDUSTRY ───────────────────────────────────
elif page == "🏭 By Industry":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Industry Analysis</div>
        <div class="page-sub">Emissions breakdown by industrial sector</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        by_ind = df_f.groupby('industry_sector')[gas_col].sum().reset_index().sort_values(gas_col)
        fig = px.bar(by_ind, x=gas_col, y='industry_sector', orientation='h',
                     color=gas_col, color_continuous_scale=CYAN_SCALE)
        fig.update_layout(**DARK, height=420,
                          title='Total Emissions by Industry')
        fig.update_coloraxes(showscale=False)
        fig.update_traces(marker_line_width=0, marker_cornerradius=3)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        by_ind2 = df_f.groupby('industry_sector')[gas_col].sum().nlargest(8).reset_index()
        fig2 = px.pie(by_ind2, values=gas_col, names='industry_sector',
                      hole=0.5, color_discrete_sequence=COLORS)
        fig2.update_layout(**DARK, height=420, title='Share by Industry')
        fig2.update_traces(textinfo='percent+label', textfont_size=9,
                           marker=dict(line=dict(color='#060d1a', width=2)))
        st.plotly_chart(fig2, use_container_width=True)

    ind_yr = df_f.groupby(['year','industry_sector'])[gas_col].sum().reset_index()
    fig3 = px.line(ind_yr, x='year', y=gas_col, color='industry_sector',
                   markers=True, color_discrete_sequence=COLORS,
                   title='Industry Trends Over Time')
    fig3.update_layout(**DARK, height=350)
    st.plotly_chart(fig3, use_container_width=True)

# ── PAGE 3: TRENDS ────────────────────────────────────────
elif page == "📈 Trends":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Emissions Trends</div>
        <div class="page-sub">Year-over-year analysis</div>
    </div>""", unsafe_allow_html=True)

    yr = df_f.groupby('year')[gas_col].sum().reset_index()
    yr['pct_change'] = yr[gas_col].pct_change() * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yr['year'], y=yr[gas_col],
        fill='tozeroy', fillcolor='rgba(56,189,248,0.08)',
        line=dict(color='#38bdf8', width=3),
        marker=dict(size=9, color='#7dd3fc',
                    line=dict(color='#38bdf8', width=2)),
        name=sel_gas
    ))
    fig.update_layout(**DARK, height=350,
                      title=f'{sel_gas} — Total Emissions 2010–2023')
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        top5 = df_f.groupby('state')[gas_col].sum().nlargest(5).index
        st_yr = df_f[df_f['state'].isin(top5)].groupby(['year','state'])[gas_col].sum().reset_index()
        fig2 = px.line(st_yr, x='year', y=gas_col, color='state',
                       markers=True, color_discrete_sequence=COLORS,
                       title='Top 5 States Trend')
        fig2.update_layout(**DARK, height=320)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        em = df_f[['co2_emissions','ch4_emissions','n2o_emissions']].sum()
        em_df = pd.DataFrame({'type':['CO₂','CH₄','N₂O'],'value':em.values})
        fig3 = px.bar(em_df, x='type', y='value', color='type',
                      color_discrete_sequence=COLORS[:3],
                      title='Emission Type Breakdown')
        fig3.update_layout(**DARK, height=320)
        fig3.update_traces(marker_line_width=0, marker_cornerradius=6)
        st.plotly_chart(fig3, use_container_width=True)

# ── PAGE 4: HEATMAP ───────────────────────────────────────
elif page == "🗺️ Heatmap":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Geographic Heatmap</div>
        <div class="page-sub">Emissions density across the United States</div>
    </div>""", unsafe_allow_html=True)

    # State choropleth heatmap
    state_totals = df_f.groupby('state')[gas_col].sum().reset_index()
    state_totals.columns = ['state', 'emissions']

    fig = px.choropleth(
        state_totals,
        locations='state',
        locationmode='USA-states',
        color='emissions',
        scope='usa',
        color_continuous_scale=[
            [0, '#060d1a'],
            [0.2, '#0c2a4a'],
            [0.4, '#0e4272'],
            [0.6, '#1e6bb8'],
            [0.8, '#38bdf8'],
            [1, '#7dd3fc']
        ],
        labels={'emissions': 'Emissions (metric tons CO₂e)'},
        title=f'{sel_gas} by State'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            lakecolor='rgba(6,13,26,1)',
            landcolor='rgba(13,31,53,0.8)',
            subunitcolor='rgba(56,189,248,0.2)',
            showlakes=True
        ),
        coloraxis_colorbar=dict(
            tickfont=dict(color='#64748b'),
            title=dict(font=dict(color='#64748b'))
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=500,
        font=dict(color='#64748b')
    )
    st.plotly_chart(fig, use_container_width=True)

    # Bubble map below
    st.markdown('<div class="chart-title">Facility Emissions Hotspots</div>', unsafe_allow_html=True)
    df_map = df_f.dropna(subset=['latitude','longitude'])
    df_map = df_map[df_map[gas_col] > 0].nlargest(3000, gas_col)

    fig2 = px.density_mapbox(
        df_map, lat='latitude', lon='longitude',
        z=gas_col, radius=15,
        mapbox_style='carto-darkmatter',
        zoom=3, height=450,
        color_continuous_scale=[
            [0,'rgba(56,189,248,0)'],
            [0.3,'rgba(56,189,248,0.4)'],
            [0.7,'rgba(52,211,153,0.7)'],
            [1,'rgba(251,191,36,1)']
        ]
    )
    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── PAGE 5: AI ASSISTANT ──────────────────────────────────
elif page == "🤖 AI Assistant":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">AI Assistant</div>
        <div class="page-sub">Powered by Groq · Llama 3.3</div>
    </div>""", unsafe_allow_html=True)

    from chatbot import ask_chatbot

    suggestions = [
        "Which state emits the most CO₂?",
        "What's the trend from 2010–2023?",
        "Which industry pollutes the most?",
        "Compare Texas and California",
        "What are Scope 1 emissions?",
        "Which year had peak emissions?"
    ]

    st.markdown('<div class="chart-title">Quick Questions</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, s in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(s, key=f"sug_{i}"):
                st.session_state.pending_q = s

    st.markdown("<br>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "messages_display" not in st.session_state:
        st.session_state.messages_display = []
    if "pending_q" not in st.session_state:
        st.session_state.pending_q = None

    for msg in st.session_state.messages_display:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Ask about EPA emissions data...")
    if st.session_state.pending_q:
        question = st.session_state.pending_q
        st.session_state.pending_q = None

    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = ask_chatbot(question, df_f, st.session_state.chat_history)
            st.write(response)
        st.session_state.chat_history.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": response}
        ])
        st.session_state.messages_display.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": response}
        ])