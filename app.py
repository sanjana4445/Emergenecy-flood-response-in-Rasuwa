import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

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
    .hero h1 { margin: 0; color: white; font-size: 30px; line-height: 1.1; letter-spacing: 0; }
    .hero p { margin: 6px 0 0; color: #d8e8e9; font-size: 17px; }
    .export-label { border: 1px solid rgba(255,255,255,.45); border-radius: 11px; padding: 11px 17px; font-weight: 700; font-size: 14px; white-space: nowrap; }
    .hero-meta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }
    .hero-pill { background: rgba(255,255,255,.14); border-radius: 999px; padding: 9px 14px; color: #f3fbfb; font-size: 14px; }
    .filter-label { color: var(--muted); font-size: 15px; margin: 0 0 9px; }
    .summary-card { display: flex; justify-content: space-between; align-items: center; gap: 24px; background: var(--paper); border: 1px solid var(--line); border-radius: 20px; padding: 25px 28px; margin: 8px 0 24px; }
    .summary-value { color: var(--teal); font-size: 54px; font-weight: 800; line-height: 1; }
    .summary-copy { color: #687673; font-size: 16px; margin-top: 8px; }
    .summary-status { display: grid; gap: 10px; min-width: 145px; color: var(--ink); font-size: 14px; }
    .status-dot { display: inline-block; width: 18px; margin-right: 8px; font-weight: 800; }
    .status-done { color: #20965a; } .status-progress { color: #1594a2; } .status-pending { color: #7d8987; }
    .stButton > button { border: 1px solid var(--line); border-radius: 999px; background: white; color: #485653; font-weight: 600; min-height: 40px; padding: 0 17px; }
    .stButton > button:hover { border-color: var(--teal); color: var(--teal); }
    .stTabs [data-baseweb="tab-list"] { gap: 36px; background: transparent; border-bottom: 1px solid var(--line); }
    .stTabs [data-baseweb="tab"], .stTabs [role="tab"], .stTabs [role="tab"] button { color: #667572 !important; font-size: 17px; font-weight: 700; padding: 0 1px 14px; }
    .stTabs [role="tab"] p, .stTabs [role="tab"] span, .stTabs [role="tab"] div { color: inherit !important; }
    .stTabs [aria-selected="true"], .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span { color: var(--ink) !important; border-bottom: 2px solid var(--teal); }
    .metric-card {
        background: var(--paper); border: 1px solid var(--line); border-radius: 12px;
        padding: 16px;
    }
    .output-card { min-height: 176px; margin-bottom: 16px; }
    .output-card .metric-title { min-height: 38px; color: var(--teal); font-size: 15px; font-weight: 800; }
    .output-card-row { display: flex; justify-content: space-between; gap: 12px; border-top: 1px solid #edf1f0; padding: 8px 0; color: #52635f; font-size: 15px; }
    .output-card-row strong { color: #0f172a; font-size: 18px; font-weight: 800; }
    .output-status { font-size: 14px; font-weight: 800; margin-top: 6px; }
    .output-met { color: #20965a; }
    .output-pending { color: #d97706; }
    .metric-title {
        font-size: 14px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 30px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 13px;
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
        font-size: 18px;
        margin: 0 0 2px 0;
    }
    .dashboard-section p {
        color: #64748b;
        font-size: 14px;
        margin: 0 0 10px 0;
    }
    [data-testid="stCaptionContainer"] p { font-size: 15px; color: #52635f; }
    [data-testid="stDataFrame"] { font-size: 15px; }
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
@st.cache_data
def load_base_data(workbook_mtime):
    file_path = Path(__file__).with_name("Chaya_Monitoring Matrix.xlsx")
    try:
        xls = pd.ExcelFile(file_path)
        def read_response_sheet(sheet_name, weekly=False):
            data = pd.read_excel(xls, sheet_name=sheet_name, skiprows=1)
            data = data.dropna(how='all').dropna(how='all', axis=1)
            if weekly:
                # Weekly workbook columns contain an extra activity description.
                names = [
                    "SN", "Agency", "Province", "District", "Municipality", "Ward",
                    "Result_Statement", "Indicator", "Activities", "Unit", "Target",
                    "Progress", "Notes"
                ]
            else:
                names = [
                    "SN", "Agency", "Province", "District", "Municipality", "Ward",
                    "Result_Statement", "Indicator", "Unit", "Target", "Progress", "Activities"
                ]
            if len(data.columns) != len(names):
                raise ValueError(f"{sheet_name} has {len(data.columns)} usable columns; expected {len(names)}")
            data.columns = names
            return data[
                data['Indicator'].notnull()
                & (data['Indicator'] != 'Performance indicator/s')
            ].copy()

        df_d = read_response_sheet("WASH Response_Daily_Chaya")
        df_w = read_response_sheet("WASH Response_Weekly_Chaya", weekly=True)
        df_d['Result_Area'] = df_d['Result_Statement'].ffill().apply(
            lambda x: x.split('\n')[0] if pd.notnull(x) else "General"
        )
        df_d['Target'] = pd.to_numeric(df_d['Target'], errors='coerce').fillna(0)
        df_d['Progress'] = pd.to_numeric(df_d['Progress'], errors='coerce').fillna(0)
        df_w['Target'] = pd.to_numeric(df_w['Target'], errors='coerce').fillna(0)
        df_w['Progress'] = pd.to_numeric(df_w['Progress'], errors='coerce').fillna(0)
        weekly = df_w[['Indicator', 'Target', 'Progress']].rename(columns={
            'Target': 'Weekly Target', 'Progress': 'Weekly Progress'
        })
        return df_d.merge(weekly, on='Indicator', how='left').fillna({
            'Weekly Target': 0, 'Weekly Progress': 0
        })
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return pd.DataFrame()

workbook_path = Path(__file__).with_name("Chaya_Monitoring Matrix.xlsx")
workbook_mtime = workbook_path.stat().st_mtime_ns
st_autorefresh(interval=30_000, key="excel_workbook_refresh")
raw_df = load_base_data(workbook_mtime)

OUTPUT_ORDER = [
    next(
        (value for value in raw_df['Result_Area'].dropna().unique() if value.startswith(f'CCC W{number}')),
        f'CCC W{number}: No data recorded'
    )
    for number in range(1, 7)
]

def summarize_outputs(frame, value_columns):
    return frame.groupby('CCC Output')[value_columns].sum().reindex(OUTPUT_ORDER, fill_value=0)

def output_interpretation(summary, achieved_column='Progress', target_column='Target', period_label='daily'):
    measured = summary[summary[target_column] > 0].copy()
    if measured.empty:
        return 'No output targets are recorded in the workbook.'
    measured['Progress %'] = (
        measured[achieved_column] / measured[target_column] * 100
    )
    met_count = int((measured[achieved_column] >= measured[target_column]).sum())
    priority = measured.sort_values('Progress %').iloc[0]
    priority_name = priority.name
    priority_pct = priority['Progress %']
    return (
        f"{met_count} of {len(measured)} outputs meet the {period_label} target. "
        f"{priority_name} has the lowest {period_label} progress at {priority_pct:.1f}% and needs the closest review."
    )

# Initialize the data once; future changes come only from the Data editor.
DATA_MATRIX_VERSION = 7
data_needs_refresh = (
    st.session_state.get('data_matrix_version') != DATA_MATRIX_VERSION
    or st.session_state.get('data_matrix_source_mtime') != workbook_mtime
)
if data_needs_refresh and not raw_df.empty:
    st.session_state.data_matrix = raw_df.assign(
        **{
            'CCC Output': raw_df['Result_Area'],
            'Activity': raw_df['Activities'].fillna(''),
            'Palika': 'District total'
        }
    )[[
        'SN', 'CCC Output', 'Result_Statement', 'Indicator', 'Activity', 'Palika',
        'Unit', 'Target', 'Progress', 'Weekly Target', 'Weekly Progress'
    ]].rename(columns={'Result_Statement': 'Result Statement'})
    st.session_state.data_matrix_version = DATA_MATRIX_VERSION
    st.session_state.data_matrix_source_mtime = workbook_mtime

# Reference-style header and inline municipality controls.
st.markdown(f"""
<div class="hero">
  <div class="hero-top">
    <div class="hero-brand"><div class="hero-mark">💧</div><div><h1>Rasuwa Flood Response</h1><p>WASH monitoring dashboard</p></div></div>
    <div class="export-label">⇩ &nbsp; Export CSV</div>
  </div>
    <div class="hero-meta"><span class="hero-pill">⌖ &nbsp;Rasuwa District, Bagmati Province</span><span class="hero-pill">Agency: UNICEF</span><span class="hero-pill">◷ &nbsp;Last update: {datetime.fromtimestamp(workbook_mtime / 1_000_000_000).strftime('%d %B %Y, %I:%M %p')}</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="filter-label">Dashboard scope: Excel output totals</div>', unsafe_allow_html=True)
# Output filter remains available in the data editor workflow.
outputs = list(st.session_state.data_matrix['CCC Output'].unique()) if 'data_matrix' in st.session_state else []
selected_outputs = outputs

# Filter Dataframe
df_active = st.session_state.data_matrix[
    (st.session_state.data_matrix['CCC Output'].isin(selected_outputs))
].copy()

df_active['Achievement_%'] = (df_active['Progress'] / df_active['Target'].replace(0, 1) * 100).round(1)

output_summary = summarize_outputs(df_active, ['Target', 'Progress'])
st.markdown("#### Output-wise daily performance", unsafe_allow_html=True)
st.caption("Each card is calculated from the Excel daily sheet. Met target means achieved progress is at least the output target.")
output_cards = output_summary.reset_index()
card_columns = st.columns(3, gap="medium")
for card_index, output_row in output_cards.iterrows():
    target = output_row['Target']
    achieved = output_row['Progress']
    progress_pct = achieved / target * 100 if target else 0
    status = 'Met target' if target > 0 and achieved >= target else ('No target recorded' if target == 0 else 'Target not met')
    with card_columns[card_index % 3]:
        st.markdown(f"""
        <div class="metric-card output-card">
            <div class="metric-title">{output_row['CCC Output']}</div>
            <div class="output-card-row"><span>Target</span><strong>{target:,.0f}</strong></div>
            <div class="output-card-row"><span>Achieved</span><strong>{achieved:,.0f}</strong></div>
            <div class="output-card-row"><span>Progress</span><strong>{progress_pct:.1f}%</strong></div>
            <div class="output-status {'output-met' if status == 'Met target' else 'output-pending'}">{status}</div>
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
    st.caption("Use the output cards and charts to compare each Excel output target with achieved progress.")
    
    st.markdown('<div class="dashboard-section"><h4>Performance by output</h4><p>Compare each Excel output target with its achieved progress.</p></div>', unsafe_allow_html=True)
    
    st.markdown("**Target vs achieved progress**")
    fig_summary = go.Figure()

    ind_group = summarize_outputs(df_active, ['Target', 'Progress']).reset_index()

    fig_summary.add_trace(go.Bar(
        y=ind_group['CCC Output'],
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
        y=ind_group['CCC Output'],
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
        yaxis_title='Output',
        legend=dict(orientation="h", y=1.1, x=0)
    )
    st.plotly_chart(apply_chart_theme(fig_summary), width="stretch")

    st.info(output_interpretation(ind_group.set_index('CCC Output')))

# =========================================================
# TAB 2: ACTIVITY DETAILS
# =========================================================
with tab_palika:
    st.subheader("Activity Details")
    st.caption("Activity descriptions and progress are loaded directly from the Excel workbook.")

    activity_output = st.selectbox(
        "Filter by output",
        ["All outputs"] + OUTPUT_ORDER,
        key="activity_output_filter"
    )
    activity_details = st.session_state.data_matrix.copy()
    if activity_output != "All outputs":
        activity_details = activity_details[activity_details['CCC Output'] == activity_output]

    activity_details['Daily progress %'] = (
        activity_details['Progress'] / activity_details['Target'].replace(0, 1) * 100
    ).round(1)
    activity_details['Daily status'] = activity_details.apply(
        lambda row: 'Met' if row['Target'] > 0 and row['Progress'] >= row['Target'] else (
            'No target recorded' if row['Target'] == 0 else 'Not met'
        ), axis=1
    )
    activity_table = activity_details.rename(columns={
        'CCC Output': 'Output',
        'Result Statement': 'Result statement',
        'Indicator': 'Indicator',
        'Activity': 'Activity detail',
        'Unit': 'Unit',
        'Target': 'Daily target',
        'Progress': 'Daily achieved',
        'Weekly Target': 'Weekly target',
        'Weekly Progress': 'Weekly achieved'
    })
    st.dataframe(
        activity_table[[
            'Output', 'Result statement', 'Indicator', 'Activity detail', 'Unit',
            'Daily target', 'Daily achieved', 'Daily progress %', 'Daily status',
            'Weekly target', 'Weekly achieved'
        ]],
        column_config={
            'Activity detail': st.column_config.TextColumn('Activity detail', width='large'),
            'Result statement': st.column_config.TextColumn('Result statement', width='large'),
            'Indicator': st.column_config.TextColumn('Indicator', width='large'),
            'Daily target': st.column_config.NumberColumn('Daily target', format='%.0f'),
            'Daily achieved': st.column_config.NumberColumn('Daily achieved', format='%.0f'),
            'Daily progress %': st.column_config.NumberColumn('Daily progress %', format='%.1f%%'),
            'Weekly target': st.column_config.NumberColumn('Weekly target', format='%.0f'),
            'Weekly achieved': st.column_config.NumberColumn('Weekly achieved', format='%.0f')
        },
        width="stretch",
        hide_index=True,
        height=560
    )

# =========================================================
# TAB 3: OUTPUT-WISE COVERAGE
# =========================================================
with tab_output:
    st.subheader("Output Performance Table")
    st.caption("One concise record per output from the Excel daily sheet.")

    output_totals = summarize_outputs(df_active, ['Target', 'Progress']).reset_index()
    out_table = output_totals.copy()
    out_table['Achievement %'] = (out_table['Progress'] / out_table['Target'] * 100).round(1)
    out_table['Target status'] = out_table.apply(
        lambda row: 'Met' if row['Target'] > 0 and row['Progress'] >= row['Target'] else 'Not met', axis=1
    )
    out_table = out_table.rename(columns={
        'CCC Output': 'Output',
        'Target': 'Target',
        'Progress': 'Achieved'
    })
    st.dataframe(
        out_table[['Output', 'Target', 'Achieved', 'Achievement %', 'Target status']],
        column_config={
            'Target': st.column_config.NumberColumn('Target', format='%.0f'),
            'Achieved': st.column_config.NumberColumn('Achieved', format='%.0f'),
            'Achievement %': st.column_config.NumberColumn('Progress %', format='%.1f%%')
        },
        width="stretch",
        hide_index=True
    )
    st.info(output_interpretation(output_totals.set_index('CCC Output')))

# =========================================================
# TAB 4: TIME-LAPSE & TRENDS
# =========================================================
with tab_timelapse:
    st.subheader("Daily and Weekly Target Performance")
    st.caption("All values below are read from the Daily and Weekly sheets in the Excel workbook.")

    period_summary = summarize_outputs(
        df_active, ['Target', 'Progress', 'Weekly Target', 'Weekly Progress']
    ).reset_index()
    period_summary['Daily %'] = (period_summary['Progress'] / period_summary['Target'].replace(0, 1) * 100).round(1)
    period_summary['Weekly %'] = (period_summary['Weekly Progress'] / period_summary['Weekly Target'].replace(0, 1) * 100).round(1)
    period_summary['Daily Target Met'] = period_summary.apply(
        lambda row: 'Met' if row['Target'] > 0 and row['Progress'] >= row['Target'] else ('Not met' if row['Target'] > 0 else 'No target recorded'), axis=1
    )
    period_summary['Weekly Target Met'] = period_summary.apply(
        lambda row: 'Met' if row['Weekly Target'] > 0 and row['Weekly Progress'] >= row['Weekly Target'] else ('Not met' if row['Weekly Target'] > 0 else 'No target recorded'), axis=1
    )

    chart_data = period_summary.melt(
        id_vars='CCC Output',
        value_vars=['Target', 'Progress', 'Weekly Target', 'Weekly Progress'],
        var_name='Measure', value_name='Value'
    )
    chart_data['Measure'] = chart_data['Measure'].replace({
        'Progress': 'Daily achieved', 'Weekly Progress': 'Weekly achieved'
    })
    fig_time = px.bar(
        chart_data, x='Value', y='CCC Output', color='Measure', barmode='group',
        orientation='h', text='Value', title='Daily and weekly target vs achieved by output',
        color_discrete_map={
            'Target': '#e4a11b', 'Daily achieved': '#0f626b',
            'Weekly Target': '#f4c56a', 'Weekly achieved': '#58aeb5'
        }, height=max(360, min(620, 55 * len(period_summary) + 120))
    )
    fig_time.update_traces(texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
    st.plotly_chart(apply_chart_theme(fig_time), width="stretch")
    st.info(output_interpretation(
        period_summary.set_index('CCC Output'),
        achieved_column='Progress',
        target_column='Target',
        period_label='daily'
    ))

    st.markdown("#### Target met by output")
    st.caption("A target is met when achieved progress is greater than or equal to the corresponding Excel target.")
    display_period = period_summary.rename(columns={
        'CCC Output': 'Output', 'Target': 'Daily target', 'Progress': 'Daily achieved',
        'Weekly Target': 'Weekly target', 'Weekly Progress': 'Weekly achieved',
        'Daily %': 'Daily achievement %', 'Weekly %': 'Weekly achievement %'
    })
    st.dataframe(
        display_period[['Output', 'Daily target', 'Daily achieved', 'Daily achievement %', 'Daily Target Met',
                        'Weekly target', 'Weekly achieved', 'Weekly achievement %', 'Weekly Target Met']],
        width="stretch", hide_index=True
    )

# =========================================================
# TAB 5: MONITORING VIEW
# =========================================================
with tab_monitoring:
    st.subheader("Progress Monitoring Center")
    st.caption("Use the output heatmap to compare daily and weekly progress, and the alerts to prioritize follow-up.")

    st.markdown("#### Daily and weekly progress by output")
    tracking = summarize_outputs(
        df_active, ['Target', 'Progress', 'Weekly Target', 'Weekly Progress']
    )
    heatmap_pct = pd.DataFrame(index=tracking.index)
    heatmap_pct['Daily progress %'] = (
        tracking['Progress'] / tracking['Target'].replace(0, 1) * 100
    ).round(1)
    heatmap_pct['Weekly progress %'] = (
        tracking['Weekly Progress'] / tracking['Weekly Target'].replace(0, 1) * 100
    ).round(1)
    fig_heatmap = px.imshow(
        heatmap_pct,
        text_auto='.1f',
        aspect='auto',
        color_continuous_scale=['#fee2e2', '#fef3c7', '#bbf7d0', '#15803d'],
        range_color=[0, 100],
        labels={'x': 'Reporting period', 'y': 'Output', 'color': 'Progress %'},
        height=max(420, min(760, 42 * len(heatmap_pct) + 140))
    )
    fig_heatmap.update_traces(texttemplate='%{z:.1f}%', textfont={'color': '#243331'})
    st.plotly_chart(apply_chart_theme(fig_heatmap), width="stretch")
    st.info("The heatmap compares the recorded daily and weekly progress percentages for each output. Empty weekly targets are shown as 0% until Excel is populated.")

    st.markdown("#### Follow-up alerts")
    alert_table = summarize_outputs(df_active, ['Target', 'Progress']).reset_index()
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
        st.success("No low-progress outputs need follow-up.")
    else:
        st.dataframe(
            alert_table[['Priority', 'CCC Output', 'Target', 'Progress', 'Remaining', 'Completion %']],
            column_config={
                'Priority': 'Priority',
                'CCC Output': 'Output',
                'Target': st.column_config.NumberColumn('Target', format='%d'),
                'Progress': st.column_config.NumberColumn('Progress', format='%d'),
                'Remaining': st.column_config.NumberColumn('Remaining', format='%d'),
                'Completion %': st.column_config.NumberColumn('Completion', format='%.1f%%')
            },
            width="stretch",
            hide_index=True
        )

# =========================================================
# TAB 6: TARGET & PROGRESS EDITOR (LIVE UPDATE)
# =========================================================
with tab_editor:
    st.subheader("Live Data Matrix & Target Editor")
    st.info("Modify Targets or Progress in the table, then apply the changes to refresh the dashboard.")

    edited_df = st.data_editor(
        st.session_state.data_matrix[['SN', 'CCC Output', 'Result Statement', 'Indicator', 'Activity', 'Unit', 'Target', 'Progress', 'Weekly Target', 'Weekly Progress']],
        num_rows="dynamic",
        width="stretch",
        key="matrix_editor",
        disabled=['SN', 'CCC Output', 'Result Statement', 'Indicator', 'Unit']
    )

    if st.button("Apply & Update Dashboard Visuals", type="primary"):
        st.session_state.data_matrix['Target'] = edited_df['Target']
        st.session_state.data_matrix['Progress'] = edited_df['Progress']
        st.session_state.data_matrix['Activity'] = edited_df['Activity']
        st.session_state.data_matrix['Weekly Target'] = edited_df['Weekly Target']
        st.session_state.data_matrix['Weekly Progress'] = edited_df['Weekly Progress']
        st.success("Dashboard successfully updated with your new target and progress values.")
        st.rerun()

    csv_data = st.session_state.data_matrix.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Updated Monitoring Matrix (CSV)",
        data=csv_data,
        file_name="Rasuwa_WASH_Updated_Monitoring_Matrix.csv",
        mime="text/csv"
    )

