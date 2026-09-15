import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration with a modern, wide layout
st.set_page_config(
    page_title="Rasuwa WASH Emergency Response Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling aligned with the reference WASH monitoring dashboard.
st.markdown("""
<style>
    :root {
        --ink: #243331;
        --muted: #7b8986;
        --teal: #0f626b;
        --line: #d9e2e0;
        --paper: #ffffff;
        --canvas: #f3f6f5;
    }
    .stApp { background: var(--canvas); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { display: none; }
    .block-container { max-width: 1350px; padding: 18px 32px 56px; }
    .hero { background: var(--teal); border-radius: 20px; color: white; padding: 24px 28px 25px; margin-bottom: 28px; }
    .hero-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; }
    .hero-brand { display: flex; align-items: center; gap: 15px; }
    .hero-mark { width: 50px; height: 50px; border-radius: 15px; background: #3a8189; display: grid; place-items: center; font-size: 28px; }
    .hero h1 { margin: 0; color: white; font-size: 27px; line-height: 1.1; letter-spacing: 0; }
    .hero p { margin: 6px 0 0; color: #d8e8e9; font-size: 16px; }
    .export-label { border: 1px solid rgba(255,255,255,.45); border-radius: 11px; padding: 11px 17px; font-weight: 700; font-size: 14px; white-space: nowrap; }
    .hero-meta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }
    .hero-pill { background: rgba(255,255,255,.14); border-radius: 999px; padding: 9px 14px; color: #f3fbfb; font-size: 14px; }
    .filter-label { color: var(--muted); font-size: 14px; margin: 0 0 9px; }
    .summary-card { display: flex; justify-content: space-between; align-items: center; gap: 24px; background: var(--paper); border: 1px solid var(--line); border-radius: 20px; padding: 25px 28px; margin: 8px 0 24px; }
    .summary-value { color: var(--teal); font-size: 54px; font-weight: 800; line-height: 1; }
    .summary-copy { color: #687673; font-size: 16px; margin-top: 8px; }
    .summary-status { display: grid; gap: 10px; min-width: 145px; color: var(--ink); font-size: 14px; }
    .status-dot { display: inline-block; width: 18px; margin-right: 8px; font-weight: 800; }
    .status-done { color: #20965a; } .status-progress { color: #1594a2; } .status-pending { color: #7d8987; }
    .stButton > button { border: 1px solid var(--line); border-radius: 999px; background: white; color: #485653; font-weight: 600; min-height: 40px; padding: 0 17px; }
    .stButton > button:hover { border-color: var(--teal); color: var(--teal); }
    .stTabs [data-baseweb="tab-list"] { gap: 36px; background: transparent; border-bottom: 1px solid var(--line); }
    .stTabs [data-baseweb="tab"], .stTabs [role="tab"], .stTabs [role="tab"] button { color: #667572 !important; font-size: 16px; font-weight: 700; padding: 0 1px 14px; }
    .stTabs [role="tab"] p, .stTabs [role="tab"] span, .stTabs [role="tab"] div { color: inherit !important; }
    .stTabs [aria-selected="true"], .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span { color: var(--ink) !important; border-bottom: 2px solid var(--teal); }
    .metric-card {
        background: var(--paper); border: 1px solid var(--line); border-radius: 12px;
        padding: 16px;
    }
    .metric-title {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 12px;
        color: #10b981;
        font-weight: 600;
        margin-top: 2px;
    }
    .dashboard-section {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px 4px 18px;
        margin: 18px 0 10px 0;
    }
    .dashboard-section h4 {
        color: #0f172a;
        font-size: 16px;
        margin: 0 0 2px 0;
    }
    .dashboard-section p {
        color: #64748b;
        font-size: 13px;
        margin: 0 0 10px 0;
    }
    .priority-table {
        background: #fff7ed;
        border-left: 4px solid #f97316;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 8px 0 14px 0;
        color: #7c2d12;
        font-size: 13px;
    }
    /* Keep Plotly's SVG labels readable when the active theme supplies light text. */
    .js-plotly-plot .plotly text {
        fill: #243331 !important;
        opacity: 1 !important;
    }
    .js-plotly-plot .plotly .legendtext,
    .js-plotly-plot .plotly .gtitle,
    .js-plotly-plot .plotly .xtitle,
    .js-plotly-plot .plotly .ytitle {
        fill: #243331 !important;
    }
    .js-plotly-plot .plotly .bg {
        fill: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

def apply_chart_theme(figure):
    figure.update_layout(
        template='plotly_white',
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        font=dict(color='#243331'),
        title_font=dict(color='#243331'),
        legend_font=dict(color='#243331')
    )
    figure.update_xaxes(title_font=dict(color='#243331'), tickfont=dict(color='#243331'))
    figure.update_yaxes(title_font=dict(color='#243331'), tickfont=dict(color='#243331'))
    return figure

# ---------------------------------------------------------
# DATA PROCESSING & INITIALIZATION
# ---------------------------------------------------------
PALIKAS = ["Gosaikunda", "Uttargaya", "Kalika", "Aamachhodingmo"]

@st.cache_data
def load_base_data():
    file_path = "Chaya_Monitoring Matrix.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        df_d = pd.read_excel(xls, sheet_name="WASH Response_Daily_Chaya", skiprows=1)
        df_d = df_d.dropna(how='all', axis=1)
        df_d.columns = [
            "SN", "Agency", "Province", "District", "Municipality", "Ward",
            "Result_Statement", "Indicator", "Unit", "Target", "Progress", "Activities"
        ]
        df_d = df_d[
            df_d['Indicator'].notnull()
            & (df_d['Indicator'] != 'Performance indicator/s')
        ].copy()
        df_d['Result_Area'] = df_d['Result_Statement'].ffill().apply(
            lambda x: x.split('\n')[0] if pd.notnull(x) else "General"
        )
        df_d['Target'] = pd.to_numeric(df_d['Target'], errors='coerce').fillna(0)
        df_d['Progress'] = pd.to_numeric(df_d['Progress'], errors='coerce').fillna(0)
        return df_d
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return pd.DataFrame()

raw_df = load_base_data()

# Initialize the data once; future changes come only from the Data editor.
DATA_MATRIX_VERSION = 5
if st.session_state.get('data_matrix_version') != DATA_MATRIX_VERSION and not raw_df.empty:
    if 'data_matrix' in st.session_state and st.session_state.get('data_matrix_version') == 4:
        st.session_state.data_matrix['Weekly Progress'] = 0
        st.session_state.data_matrix['Monthly Progress'] = 0
    else:
        rows = []
        for idx, row in raw_df.iterrows():
            target = int(row['Target'])
            base_target, remainder = divmod(target, len(PALIKAS))
            for palika_index, palika in enumerate(PALIKAS):
                p_target = base_target + (1 if palika_index < remainder else 0)
                rows.append({
                    'SN': row['SN'],
                    'CCC Output': row['Result_Area'],
                    'Result Statement': row['Result_Statement'],
                    'Indicator': row['Indicator'],
                    'Activity': row['Activities'] if pd.notna(row['Activities']) else '',
                    'Palika': palika,
                    'Unit': row['Unit'],
                    'Target': p_target,
                    'Progress': 0,
                    'Weekly Progress': 0,
                    'Monthly Progress': 0,
                    'Status': 'Not Started'
                })
        st.session_state.data_matrix = pd.DataFrame(rows)
    st.session_state.data_matrix_version = DATA_MATRIX_VERSION

# Reference-style header and inline municipality controls.
st.markdown("""
<div class="hero">
  <div class="hero-top">
    <div class="hero-brand"><div class="hero-mark">💧</div><div><h1>Rasuwa Flood Response</h1><p>WASH monitoring dashboard</p></div></div>
    <div class="export-label">⇩ &nbsp; Export CSV</div>
  </div>
  <div class="hero-meta"><span class="hero-pill">⌖ &nbsp;Rasuwa District, Bagmati Province</span><span class="hero-pill">Agency: UNICEF</span><span class="hero-pill">◷ &nbsp;Last update: No updates yet</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="filter-label">Filter by municipality</div>', unsafe_allow_html=True)
filter_cols = st.columns(5)
if 'active_palika' not in st.session_state:
    st.session_state.active_palika = 'All Rasuwa'
for index, palika in enumerate(['All Rasuwa'] + PALIKAS):
    with filter_cols[index if index < 5 else 4]:
        if st.button(
            palika,
            key=f"palika_{palika}",
            type="primary" if st.session_state.active_palika == palika else "secondary"
        ):
            st.session_state.active_palika = palika
selected_palikas = PALIKAS if st.session_state.active_palika == 'All Rasuwa' else [st.session_state.active_palika]

# Output filter remains available in the data editor workflow.
outputs = list(st.session_state.data_matrix['CCC Output'].unique()) if 'data_matrix' in st.session_state else []
selected_outputs = outputs

# Filter Dataframe
df_active = st.session_state.data_matrix[
    (st.session_state.data_matrix['Palika'].isin(selected_palikas)) &
    (st.session_state.data_matrix['CCC Output'].isin(selected_outputs))
].copy()

df_active['Achievement_%'] = (df_active['Progress'] / df_active['Target'].replace(0, 1) * 100).round(1)

indicator_summary = df_active.groupby('Indicator')[['Target', 'Progress']].sum()
achieved_count = int((indicator_summary['Progress'] >= indicator_summary['Target']).sum())
progress_count = int(((indicator_summary['Progress'] > 0) & (indicator_summary['Progress'] < indicator_summary['Target'])).sum())
not_started_count = int((indicator_summary['Progress'] <= 0).sum())
indicator_count = len(indicator_summary)
overall_pct = (df_active['Progress'].sum() / df_active['Target'].sum() * 100) if df_active['Target'].sum() else 0

st.markdown(f"""
<div class="summary-card">
    <div><div class="summary-value">{overall_pct:.0f}%</div><div class="summary-copy">Overall progress across {indicator_count} daily indicators</div></div>
    <div class="summary-status">
        <div><span class="status-dot status-done">✓</span>{achieved_count} achieved</div>
        <div><span class="status-dot status-progress">⌁</span>{progress_count} in progress</div>
        <div><span class="status-dot status-pending">ⓘ</span>{not_started_count} not started</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN DASHBOARD TABS
# ---------------------------------------------------------
tab_exec, tab_palika, tab_output, tab_timelapse, tab_monitoring, tab_editor = st.tabs([
    "Overview", "Activities", "Daily Log", "Trends", "Monitoring", "Data editor"
])

# =========================================================
# TAB 1: EXECUTIVE SUMMARY
# =========================================================
with tab_exec:
    st.subheader("High-Level Strategic Overview")
    st.caption("Use the summary cards for scale, the charts for performance, and the priority view to identify where support is needed.")
    
    tot_target = df_active['Target'].sum()
    tot_progress = df_active['Progress'].sum()
    overall_pct = (tot_progress / tot_target * 100) if tot_target > 0 else 0
    gap = tot_target - tot_progress
    
    st.markdown('<div class="dashboard-section"><h4>At a glance</h4><p>Key response numbers for the selected municipalities and output areas.</p></div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4, gap="medium")
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Targeted Reach</div>
            <div class="metric-value">{tot_target:,}</div>
            <div class="metric-sub">Across {len(selected_palikas)} Palikas</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Cumulative Achieved</div>
            <div class="metric-value">{tot_progress:,}</div>
            <div class="metric-sub">Verified Progress</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Response Achievement Rate</div>
            <div class="metric-value">{overall_pct:.1f}%</div>
            <div class="metric-sub">Completion Level</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Unmet Gap (Target - Actual)</div>
            <div class="metric-value">{gap:,}</div>
            <div class="metric-sub" style="color:#ef4444;">Needs Coverage</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('<div class="dashboard-section"><h4>Performance by indicator</h4><p>Compare planned reach with verified progress for each WASH indicator.</p></div>', unsafe_allow_html=True)
    
    c_left, c_right = st.columns([6, 4])
    
    with c_left:
        st.markdown("**Target vs achieved progress**")
        fig_summary = go.Figure()
        
        ind_group = df_active.groupby('Indicator')[['Target', 'Progress']].sum().reset_index()
        
        fig_summary.add_trace(go.Bar(
            y=ind_group['Indicator'],
            x=ind_group['Target'],
            name='Target',
            orientation='h',
            marker_color='#e4a11b',
            text=ind_group['Target'],
            texttemplate='%{text:,.0f}',
            textposition='outside',
            cliponaxis=False
        ))
        fig_summary.add_trace(go.Bar(
            y=ind_group['Indicator'],
            x=ind_group['Progress'],
            name='Achieved Progress',
            orientation='h',
            marker_color='#0f626b',
            text=ind_group['Progress'],
            texttemplate='%{text:,.0f}',
            textposition='outside',
            cliponaxis=False
        ))
        fig_summary.update_layout(
            template='plotly_white',
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color='#243331'),
            barmode='group',
            height=420,
            margin=dict(l=10, r=55, t=35, b=20),
            xaxis_title='Target / people or events reached',
            yaxis_title='Activity / indicator',
            legend=dict(orientation="h", y=1.1, x=0)
        )
        st.plotly_chart(apply_chart_theme(fig_summary), use_container_width=True)

    with c_right:
        st.markdown("**Overall completion**")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = overall_pct,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Response Completion %"},
            delta = {'reference': 100, 'increasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#0284c7"},
                'steps': [
                    {'range': [0, 50], 'color': "#fee2e2"},
                    {'range': [50, 80], 'color': "#fef9c3"},
                    {'range': [80, 100], 'color': "#dcfce7"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))
        fig_gauge.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(apply_chart_theme(fig_gauge), use_container_width=True)

    st.markdown('<div class="dashboard-section"><h4>Target and progress by output area</h4><p>A simple output-level view of planned reach versus achieved progress.</p></div>', unsafe_allow_html=True)
    overview_output = df_active.groupby('CCC Output')[['Target', 'Progress']].sum().reset_index()
    overview_output_long = overview_output.melt(
        id_vars='CCC Output',
        value_vars=['Target', 'Progress'],
        var_name='Measure',
        value_name='Value'
    )
    overview_output_long['Measure'] = overview_output_long['Measure'].replace({'Progress': 'Achieved'})
    fig_overview_output = px.bar(
        overview_output_long,
        x='Value',
        y='CCC Output',
        color='Measure',
        orientation='h',
        barmode='group',
        text='Value',
        height=max(360, min(620, 55 * len(overview_output) + 120)),
        color_discrete_map={'Target': '#e4a11b', 'Achieved': '#0f626b'}
    )
    fig_overview_output.update_traces(texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
    fig_overview_output.update_layout(
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#243331'),
        margin=dict(l=10, r=55, t=20, b=20),
        xaxis_title='Target / people or events reached',
        yaxis_title='Output area',
        yaxis={'categoryorder': 'array', 'categoryarray': overview_output['CCC Output'].tolist()},
        legend=dict(orientation='h', y=1.08, x=0)
    )
    st.plotly_chart(apply_chart_theme(fig_overview_output), use_container_width=True)

    st.markdown('<div class="dashboard-section"><h4>Coverage by municipality</h4><p>Find uneven coverage quickly and focus follow-up on the largest remaining gaps.</p></div>', unsafe_allow_html=True)
    palika_summary = df_active.groupby('Palika')[['Target', 'Progress']].sum().reset_index()
    palika_summary['Completion %'] = (
        palika_summary['Progress'] / palika_summary['Target'].replace(0, 1) * 100
    ).round(1)
    palika_summary['Gap'] = palika_summary['Target'] - palika_summary['Progress']

    coverage_left, coverage_right = st.columns([6, 4])
    with coverage_left:
        fig_coverage = px.bar(
            palika_summary.sort_values('Completion %'),
            x='Palika',
            y='Completion %',
            text='Completion %',
            color='Completion %',
            color_continuous_scale=['#f97316', '#facc15', '#16a34a'],
            range_color=[0, 100],
            title="Completion rate by municipality",
            height=340
        )
        fig_coverage.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_coverage.update_layout(
            yaxis=dict(range=[0, 110], ticksuffix='%'),
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=55, b=20)
        )
        st.plotly_chart(apply_chart_theme(fig_coverage), use_container_width=True)

    with coverage_right:
        priority = palika_summary.sort_values('Gap', ascending=False).head(4).copy()
        priority['Gap'] = priority['Gap'].map('{:,.0f}'.format)
        priority['Completion %'] = priority['Completion %'].map('{:.1f}%'.format)
        st.markdown("**Priority follow-up list**")
        st.markdown('<div class="priority-table">Sorted by unmet target, so the biggest coverage gaps are visible first.</div>', unsafe_allow_html=True)
        st.dataframe(
            priority[['Palika', 'Gap', 'Completion %']],
            column_config={
                'Palika': 'Municipality',
                'Gap': 'Unmet target',
                'Completion %': 'Completion'
            },
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# TAB 2: PALIKA-WISE PROGRESS
# =========================================================
with tab_palika:
    st.subheader("Rasuwa District Municipality Breakdown")
    st.caption("Comparative monitoring across Gosaikunda, Uttargaya, Kalika, and Aamachhodingmo")
    
    palika_summary = df_active.groupby('Palika')[['Target', 'Progress']].sum().reset_index()
    palika_summary['Completion %'] = (palika_summary['Progress'] / palika_summary['Target'] * 100).round(1)
    
    col_p1, col_p2 = st.columns([6, 4])
    
    with col_p1:
        fig_palika = px.bar(
            palika_summary,
            x='Palika',
            y=['Target', 'Progress'],
            barmode='group',
            title="Target vs Achieved by Palika",
            color_discrete_map={'Target': '#cbd5e1', 'Progress': '#0d9488'},
            height=400
        )
        st.plotly_chart(apply_chart_theme(fig_palika), use_container_width=True)
        
    with col_p2:
        fig_pie = px.pie(
            palika_summary,
            names='Palika',
            values='Progress',
            title="Share of Total Response Reached",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(apply_chart_theme(fig_pie), use_container_width=True)

    st.markdown("#### Palika Monitoring Matrix")
    st.dataframe(
        palika_summary,
        column_config={
            "Completion %": st.column_config.ProgressColumn(
                "Completion Rate",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "Target": st.column_config.NumberColumn("Target", format="%d"),
            "Progress": st.column_config.NumberColumn("Progress", format="%d")
        },
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# TAB 3: OUTPUT-WISE COVERAGE
# =========================================================
with tab_output:
    st.subheader("CCC Output-Wise Detailed Analysis")

    output_totals = df_active.groupby('CCC Output')[['Target', 'Progress']].sum().reset_index()
    output_chart_data = output_totals.melt(
        id_vars='CCC Output',
        value_vars=['Target', 'Progress'],
        var_name='Measure',
        value_name='Value'
    )
    output_chart_data['Measure'] = output_chart_data['Measure'].replace({
        'Target': 'Target',
        'Progress': 'Achieved'
    })

    fig_output = px.bar(
        output_chart_data,
        x='Value',
        y='CCC Output',
        color='Measure',
        orientation='h',
        barmode='group',
        text='Value',
        title="Target and achieved progress by output area",
        height=max(360, min(620, 55 * len(output_totals) + 120)),
        color_discrete_map={'Target': '#f0a202', 'Achieved': '#1594a2'}
    )
    fig_output.update_traces(texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
    fig_output.update_layout(
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#243331'),
        margin=dict(l=10, r=35, t=55, b=20),
        xaxis_title='Target / people or events reached',
        yaxis_title='Output area',
        yaxis={'categoryorder': 'array', 'categoryarray': output_totals['CCC Output'].tolist()},
        legend=dict(orientation='h', y=1.08, x=0)
    )
    st.plotly_chart(apply_chart_theme(fig_output), use_container_width=True)

    # Detailed Data Table by Output
    st.markdown("#### Output Performance Breakdown")
    out_table = output_totals.copy()
    out_table['Achievement %'] = (out_table['Progress'] / out_table['Target'] * 100).round(1)
    st.dataframe(out_table, use_container_width=True, hide_index=True)

# =========================================================
# TAB 4: TIME-LAPSE & TRENDS
# =========================================================
with tab_timelapse:
    st.subheader("Time-Lapse & Response Velocity")
    st.caption("Simulated daily/weekly cumulative trajectory over emergency period")
    
    # Generate Time Series Simulation
    dates = pd.date_range(start="2025-08-01", periods=12, freq="W")
    time_data = []
    
    for i, date in enumerate(dates):
        factor = (i + 1) / len(dates)
        time_data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Water Supply': int(tot_progress * 0.4 * factor),
            'Sanitation': int(tot_progress * 0.3 * factor),
            'Hygiene & SBC': int(tot_progress * 0.3 * factor),
            'Cumulative Progress': int(tot_progress * factor)
        })
        
    df_time = pd.DataFrame(time_data)
    
    fig_time = px.line(
        df_time,
        x='Date',
        y=['Water Supply', 'Sanitation', 'Hygiene & SBC', 'Cumulative Progress'],
        markers=True,
        title="Weekly Cumulative Achievement Trajectory",
        height=420
    )
    st.plotly_chart(apply_chart_theme(fig_time), use_container_width=True)

    period_summary = df_active.groupby('Indicator')[
        ['Target', 'Weekly Progress', 'Monthly Progress']
    ].sum().reset_index()
    st.markdown("#### Weekly and monthly progress")
    st.caption("Update these period values from the Data editor to track progress against each indicator target.")
    fig_period = go.Figure()
    for column, label, color in [
        ('Target', 'Target', '#b8c4c1'),
        ('Weekly Progress', 'This week', '#1594a2'),
        ('Monthly Progress', 'This month', '#0f626b')
    ]:
        fig_period.add_trace(go.Bar(
            y=period_summary['Indicator'],
            x=period_summary[column],
            name=label,
            orientation='h',
            marker_color=color
        ))
    fig_period.update_layout(
        barmode='group',
        height=max(320, min(620, 45 * len(period_summary) + 100)),
        margin=dict(l=10, r=20, t=20, b=20),
        xaxis_title='People / events reached',
        yaxis_title='Activity / indicator',
        legend=dict(orientation='h', y=1.08, x=0)
    )
    st.plotly_chart(apply_chart_theme(fig_period), use_container_width=True)

    # Compare each activity indicator with the completion expected by the elapsed timeline.
    timeline_start = dates.min()
    timeline_end = dates.max()
    elapsed_ratio = min(max((pd.Timestamp.today() - timeline_start) / (timeline_end - timeline_start), 0), 1)
    expected_pct = max(10, elapsed_ratio * 100)

    risk_table = df_active.groupby('Indicator')[['Target', 'Progress']].sum().reset_index()
    risk_table['Completion %'] = (
        risk_table['Progress'] / risk_table['Target'].replace(0, 1) * 100
    ).clip(0, 100).round(1)
    risk_table['Risk gap'] = (expected_pct - risk_table['Completion %']).round(1)
    risk_table['Risk status'] = risk_table['Risk gap'].apply(
        lambda gap: 'At risk' if gap >= 20 else ('Watch' if gap > 0 else 'On track')
    )
    risk_table = risk_table.sort_values(['Risk gap', 'Completion %'], ascending=[False, True])

    st.markdown("#### Activities at risk")
    st.caption(f"Expected completion by the elapsed timeline: {expected_pct:.0f}%")
    fig_risk = px.bar(
        risk_table,
        x='Completion %',
        y='Indicator',
        orientation='h',
        color='Risk status',
        color_discrete_map={'At risk': '#d97706', 'Watch': '#eab308', 'On track': '#20965a'},
        range_x=[0, 100],
        labels={'Indicator': 'Activity / indicator', 'Completion %': 'Completion (%)'},
        height=max(320, min(620, 45 * len(risk_table) + 100))
    )
    fig_risk.add_vline(
        x=expected_pct,
        line_dash='dash',
        line_color='#0f626b',
        annotation_text='Expected by now',
        annotation_position='top'
    )
    fig_risk.update_layout(
        margin=dict(l=10, r=20, t=35, b=20),
        legend=dict(orientation='h', y=1.08, x=0),
        yaxis={'categoryorder': 'array', 'categoryarray': risk_table['Indicator'].tolist()}
    )
    st.plotly_chart(apply_chart_theme(fig_risk), use_container_width=True)

# =========================================================
# TAB 5: MONITORING VIEW
# =========================================================
with tab_monitoring:
    st.subheader("Progress Monitoring Center")
    st.caption("Use the heatmap to compare municipalities, the trend to track movement, and the alerts to prioritize follow-up.")

    monitor_left, monitor_right = st.columns([6, 4])
    with monitor_left:
        st.markdown("#### Completion heatmap")
        heatmap_data = df_active.pivot_table(
            index='Indicator',
            columns='Palika',
            values=['Target', 'Progress'],
            aggfunc='sum',
            fill_value=0
        )
        heatmap_pct = pd.DataFrame(index=heatmap_data.index.get_level_values(0).unique())
        for palika in selected_palikas:
            target_values = heatmap_data.get(('Target', palika), 0)
            progress_values = heatmap_data.get(('Progress', palika), 0)
            heatmap_pct[palika] = (
                progress_values / target_values.replace(0, 1) * 100
            ).round(1)
        heatmap_pct = heatmap_pct.sort_index()
        fig_heatmap = px.imshow(
            heatmap_pct,
            text_auto='.1f',
            aspect='auto',
            color_continuous_scale=['#fee2e2', '#fef3c7', '#bbf7d0', '#15803d'],
            range_color=[0, 100,
            ],
            labels={'x': 'Municipality', 'y': 'Indicator', 'color': 'Completion %'},
            height=max(420, min(760, 42 * len(heatmap_pct) + 140))
        )
        fig_heatmap.update_traces(texttemplate='%{z:.1f}%', textfont={'color': '#243331'})
        st.plotly_chart(apply_chart_theme(fig_heatmap), use_container_width=True)

    with monitor_right:
        st.markdown("#### Progress trend")
        recorded_week = int(df_active['Weekly Progress'].sum())
        recorded_month = int(df_active['Monthly Progress'].sum())
        recorded_total = int(df_active['Progress'].sum())
        trend_data = pd.DataFrame({
            'Period': ['This week', 'This month', 'Cumulative'],
            'Progress': [recorded_week, recorded_month, recorded_total]
        })
        fig_trend = px.line(
            trend_data,
            x='Period',
            y='Progress',
            markers=True,
            text='Progress',
            labels={'Progress': 'People / events reached'},
            height=320
        )
        fig_trend.update_traces(texttemplate='%{text:,.0f}', textposition='top center', line_color='#0f626b')
        st.plotly_chart(apply_chart_theme(fig_trend), use_container_width=True)
        st.caption("Values are based on the period totals entered in the Data editor.")

    st.markdown("#### Follow-up alerts")
    alert_table = df_active.groupby('Indicator')[['Target', 'Progress']].sum().reset_index()
    alert_table['Completion %'] = (
        alert_table['Progress'] / alert_table['Target'].replace(0, 1) * 100
    ).round(1)
    alert_table['Remaining'] = (alert_table['Target'] - alert_table['Progress']).clip(lower=0)
    alert_table['Priority'] = alert_table.apply(
        lambda row: 'High' if row['Completion %'] < 25 else ('Medium' if row['Completion %'] < 75 else 'On track'),
        axis=1
    )
    alert_table = alert_table[alert_table['Priority'] != 'On track'].sort_values(
        ['Priority', 'Remaining'], ascending=[True, False]
    )
    if alert_table.empty:
        st.success("No low-progress indicators need follow-up for the selected municipalities.")
    else:
        st.dataframe(
            alert_table[['Priority', 'Indicator', 'Target', 'Progress', 'Remaining', 'Completion %']],
            column_config={
                'Priority': 'Priority',
                'Indicator': 'Activity / indicator',
                'Target': st.column_config.NumberColumn('Target', format='%d'),
                'Progress': st.column_config.NumberColumn('Progress', format='%d'),
                'Remaining': st.column_config.NumberColumn('Remaining', format='%d'),
                'Completion %': st.column_config.NumberColumn('Completion', format='%.1f%%')
            },
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# TAB 6: TARGET & PROGRESS EDITOR (LIVE UPDATE)
# =========================================================
with tab_editor:
    st.subheader("Live Data Matrix & Target Editor")
    st.info("Modify Targets or Progress in the table, then apply the changes to refresh the dashboard.")

    edited_df = st.data_editor(
        st.session_state.data_matrix[['Palika', 'CCC Output', 'Result Statement', 'Indicator', 'Activity', 'Unit', 'Target', 'Progress', 'Weekly Progress', 'Monthly Progress']],
        num_rows="dynamic",
        use_container_width=True,
        key="matrix_editor"
    )

    if st.button("Apply & Update Dashboard Visuals", type="primary"):
        st.session_state.data_matrix['Target'] = edited_df['Target']
        st.session_state.data_matrix['Progress'] = edited_df['Progress']
        st.session_state.data_matrix['Activity'] = edited_df['Activity']
        st.session_state.data_matrix['Weekly Progress'] = edited_df['Weekly Progress']
        st.session_state.data_matrix['Monthly Progress'] = edited_df['Monthly Progress']
        st.success("Dashboard successfully updated with your new target and progress values.")
        st.rerun()

    csv_data = st.session_state.data_matrix.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Updated Monitoring Matrix (CSV)",
        data=csv_data,
        file_name="Rasuwa_WASH_Updated_Monitoring_Matrix.csv",
        mime="text/csv"
    )

