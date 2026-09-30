import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
from datetime import datetime
from html import escape
from uuid import uuid4

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    def st_autorefresh(*args, **kwargs):
        return None

# Set page configuration with a modern, wide layout
st.set_page_config(
    page_title="Providing safe WASH facilities & assistance to flood affected population",
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
    .output-summary-card {
        background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
        border: 1px solid #dfe7e4;
        border-radius: 18px;
        padding: 18px 18px 10px;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(15, 98, 107, 0.05);
    }
    .output-summary-title {
        font-size: 15px; font-weight: 800; color: #173b3d; margin-bottom: 12px;
    }
    .output-summary-row {
        display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-top: 1px solid #edf1f0;
        font-size: 16px; color: #243331;
    }
    .output-summary-row strong { font-size: 24px; font-weight: 800; color: #0f172a; }
    .output-summary-row .label { font-weight: 600; color: #52635f; }
    .output-summary-status {
        font-weight: 800; font-size: 17px; margin-top: 12px; color: #d97706;
    }
    .output-summary-status.met { color: #15803d; }
    .output-progress-bar {
        width: 100%; height: 10px; border-radius: 999px; background: #e7efe9; overflow: hidden; margin-top: 10px;
    }
    .output-progress-fill {
        height: 100%; border-radius: inherit; background: linear-gradient(90deg, #86efac 0%, #22c55e 45%, #15803d 100%);
    }
    .output-activity-list {
        margin-top: 12px; display: grid; gap: 10px;
    }
    .output-activity-item {
        background: #f8faf9; border: 1px solid #e7efe9; border-radius: 12px; padding: 10px 12px;
    }
    .output-activity-head {
        display: flex; justify-content: space-between; gap: 8px; align-items: center; font-size: 13px; font-weight: 700; color: #173b3d; margin-bottom: 8px;
    }
    .output-activity-name {
        flex: 1; overflow-wrap: anywhere;
    }
    .output-activity-metrics {
        display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; font-size: 12px; color: #52635f;
    }
    .output-activity-metrics strong {
        color: #0f172a; font-size: 14px; display: block; margin-top: 2px;
    }
    .activity-item { border-top: 1px solid #edf1f0; padding: 10px 0; }
    .activity-name { color: var(--teal); font-size: 13px; font-weight: 700; line-height: 1.35; overflow-wrap: anywhere; }
    .activity-description { color: #687673; font-size: 12px; line-height: 1.35; margin-top: 4px; overflow-wrap: anywhere; }
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
    [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
        color: #243331 !important; font-weight: 650 !important;
    }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input, [data-baseweb="select"] > div {
        background-color: #ffffff !important; color: #243331 !important;
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
@st.cache_data
def load_base_data(workbook_mtime):
    file_path = Path(__file__).with_name("Chaya_Monitoring Matrix.xlsx")
    try:
        xls = pd.ExcelFile(file_path)

        def to_number(value):
            if pd.isna(value):
                return None
            if isinstance(value, (int, float)):
                return float(value)
            text = str(value).strip()
            if text == '':
                return None
            try:
                return float(text.replace(',', '').replace('%', ''))
            except ValueError:
                return None

        def normalize_result_area(value):
            if pd.isna(value):
                return "General"
            text = str(value).strip()
            for match, label in {
                "CCC W1": "W1: Lead & Coordination",
                "CCC W2": "W2: Water Supply",
                "CCC W2.": "W2: Water Supply",
                "CCC W3": "W3: Sanitation",
                "CCC W4": "W4: WASH in Schools & Health Facilities",
                "CCC W5": "W5: Hygiene Promotion & Community Engagement",
                "CCC W6": "W5: Hygiene Promotion & Community Engagement",
            }.items():
                if text.startswith(match):
                    return label
            return text.split('\n')[0]

        def parse_activity_rows(sheet_name, unit_index=9, target_index=10, progress_index=11, activity_index=12):
            raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            rows = []
            current_output = 'General'
            current_result_statement = 'General'

            for row_index, row in raw.iterrows():
                if row_index < 7 or row.iloc[0:13].isna().all():
                    continue

                result_value = row.iloc[7] if len(row) > 7 else None
                if pd.notna(result_value) and 'CCC W' in str(result_value):
                    current_output = normalize_result_area(result_value)
                    current_result_statement = str(result_value).strip().replace('CCC W6', 'CCC W5', 1)

                indicator = row.iloc[8] if len(row) > 8 else None
                if pd.isna(indicator) or not str(indicator).strip():
                    continue

                unit = row.iloc[unit_index] if len(row) > unit_index and pd.notna(row.iloc[unit_index]) else ''
                target = to_number(row.iloc[target_index]) if len(row) > target_index else None
                progress = to_number(row.iloc[progress_index]) if len(row) > progress_index else None
                activity = row.iloc[activity_index] if len(row) > activity_index and pd.notna(row.iloc[activity_index]) else ''
                indicator = str(indicator).strip()
                rows.append({
                    'Result_Area': current_output,
                    'Result_Statement': current_result_statement,
                    'Indicator': indicator,
                    'Activity': str(activity).strip(),
                    'Unit': str(unit).strip(),
                    'Target': float(target) if target is not None else 0,
                    'Progress': float(progress) if progress is not None else 0,
                    'key': f"{current_output}|{indicator}"
                })

            if rows:
                frame = pd.DataFrame(rows)
                frame['SN'] = range(1, len(frame) + 1)
                return frame
            return pd.DataFrame(columns=['Result_Area','Indicator','Activity','Unit','Target','Progress','Result_Statement','SN','key'])

        df_d = parse_activity_rows("WASH Response_Daily_Chaya")
        df_w = parse_activity_rows(
            "WASH Response_Weekly_Chaya",
            unit_index=10,
            target_index=11,
            progress_index=12,
            activity_index=13
        )

        weekly = df_w[['key', 'Target', 'Progress']].rename(columns={
            'Target': 'Weekly Target', 'Progress': 'Weekly Progress'
        })
        merged = df_d.merge(weekly, on='key', how='left').fillna({
            'Weekly Target': 0, 'Weekly Progress': 0
        })
        merged['Activities'] = merged['Activity'].fillna('')
        return merged.drop(columns=['key'])
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return pd.DataFrame()

workbook_path = Path(__file__).with_name("Chaya_Monitoring Matrix.xlsx")
workbook_mtime = workbook_path.stat().st_mtime_ns
st_autorefresh(interval=30_000, key="excel_workbook_refresh")
raw_df = load_base_data(workbook_mtime)

OUTPUT_ORDER = [
    "W1: Lead & Coordination",
    "W2: Water Supply",
    "W3: Sanitation",
    "W4: WASH in Schools & Health Facilities",
    "W5: Hygiene Promotion & Community Engagement",
]

ACTIVITY_LOG_PATH = Path(__file__).with_name("wash_activity_log.json")
DEMOGRAPHIC_COLUMNS = [
    'Households', 'Male', 'Female', 'Children', 'Boys', 'Girls',
    'Under 5', '6-9', '10-19', 'Pregnant', 'Postpartum', 'PWD',
    'PWD Female', 'PWD Male', '60+'
]
DEMOGRAPHIC_LABELS = {
    'Households': 'Households reached',
    'Male': 'Male',
    'Female': 'Female',
    'Children': 'Children under 18 (total)',
    'Boys': 'Boys under 18',
    'Girls': 'Girls under 18',
    'Under 5': 'Children under 5',
    '6-9': 'Children aged 6-9',
    '10-19': 'People aged 10-19',
    'Pregnant': 'Pregnant women',
    'Postpartum': 'Postpartum women',
    'PWD': 'People with disabilities',
    'PWD Female': 'Female people with disabilities',
    'PWD Male': 'Male people with disabilities',
    '60+': 'People aged 60 or older',
}

def load_activity_log():
    if not ACTIVITY_LOG_PATH.exists():
        return []
    try:
        records = json.loads(ACTIVITY_LOG_PATH.read_text(encoding='utf-8'))
        return records if isinstance(records, list) else []
    except (OSError, json.JSONDecodeError):
        return []

def save_activity_log(records):
    ACTIVITY_LOG_PATH.write_text(json.dumps(records, indent=2), encoding='utf-8')

def render_demographic_inputs(record=None, key_prefix='activity_demographics'):
    record = record or {}
    st.caption("Enter counts from your report. Leave a count at 0 if it was not reported; some categories may overlap.")
    demographic_inputs = {}
    demographic_columns = st.columns(3)
    for index, (field, label) in enumerate(DEMOGRAPHIC_LABELS.items()):
        value = pd.to_numeric(record.get(field), errors='coerce')
        default_value = 0 if pd.isna(value) else max(0, int(value))
        with demographic_columns[index % len(demographic_columns)]:
            demographic_inputs[field] = st.number_input(
                label,
                min_value=0,
                value=default_value,
                step=1,
                key=f"{key_prefix}_{field.lower().replace(' ', '_').replace('+', 'plus').replace('-', '_')}"
            )
    return demographic_inputs

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
DATA_MATRIX_VERSION = 10
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
    <div class="hero-brand"><div class="hero-mark">💧</div><div><h1>Providing safe WASH facilities &amp; assistance to flood affected population</h1><p>WASH monitoring dashboard</p></div></div>
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

st.markdown("#### Output-based target and progress", unsafe_allow_html=True)
st.caption("Each output shows its activity-wise targets and progress within the same section.")
total_output_target = float(df_active['Target'].sum())
overview_totals = st.columns(3)
overview_totals[0].metric("Outputs", len(OUTPUT_ORDER))
overview_totals[1].metric("Activities", len(df_active))
overview_totals[2].metric("Combined target", f"{total_output_target:,.0f}")
for row_start in range(0, len(OUTPUT_ORDER), 2):
    card_columns = st.columns(2, gap="medium")
    for column_index, output_name in enumerate(OUTPUT_ORDER[row_start:row_start + 2]):
        output_activities = df_active[df_active['CCC Output'] == output_name].copy()
        total_target = float(output_activities['Target'].sum()) if not output_activities.empty else 0
        total_progress = float(output_activities['Progress'].sum()) if not output_activities.empty else 0
        progress_pct = (total_progress / total_target * 100) if total_target else 0
        is_met = total_target > 0 and total_progress >= total_target
        status_text = 'Target achieved' if is_met else ('No target recorded' if total_target == 0 else 'Target not met')
        status_class = 'met' if is_met else ''
        activity_rows_html = []
        if output_activities.empty:
            activity_rows_html.append('<div class="output-activity-item"><div class="output-activity-head"><span class="output-activity-name">No activity data</span></div></div>')
        else:
            for _, activity_row in output_activities.iterrows():
                activity_name = str(activity_row['Indicator']) if str(activity_row['Indicator']).strip() else str(activity_row['Activity']).strip()
                activity_target = float(activity_row['Target'])
                activity_progress = float(activity_row['Progress'])
                activity_pct = (activity_progress / activity_target * 100) if activity_target else 0
                activity_status = 'Met' if activity_target > 0 and activity_progress >= activity_target else ('No target' if activity_target == 0 else 'Not met')
                activity_rows_html.append(
                    f'''
                    <div class="output-activity-item">
                        <div class="output-activity-head">
                            <span class="output-activity-name">{escape(activity_name)}</span>
                            <span class="output-activity-status">{activity_status}</span>
                        </div>
                        <div class="output-activity-metrics">
                            <div>Target<strong>{activity_target:,.0f}</strong></div>
                            <div>Progress<strong>{activity_progress:,.0f}</strong></div>
                            <div>Achievement<strong>{activity_pct:.1f}%</strong></div>
                            <div>Result<strong>{'Done' if activity_status == 'Met' else 'Pending'}</strong></div>
                        </div>
                    </div>
                    '''
                )
        with card_columns[column_index]:
            st.html(f'''
                <div class="output-summary-card">
                    <div class="output-summary-title">{escape(output_name)}</div>
                    <div class="output-summary-row"><span class="label">Target</span><strong>{total_target:,.0f}</strong></div>
                    <div class="output-summary-row"><span class="label">Progress</span><strong>{total_progress:,.0f}</strong></div>
                    <div class="output-summary-row"><span class="label">Achievement</span><strong>{progress_pct:.1f}%</strong></div>
                    <div class="output-progress-bar"><div class="output-progress-fill" style="width: {min(100, max(0, progress_pct))}%"></div></div>
                    <div class="output-summary-status {status_class}">{status_text}</div>
                    <div class="output-activity-list">{''.join(activity_rows_html)}</div>
                </div>
            ''')

# ---------------------------------------------------------
# MAIN DASHBOARD TABS
# ---------------------------------------------------------
tab_exec, tab_activity_log, tab_palika, tab_output, tab_monitoring, tab_editor = st.tabs([
    "Overview", "Activity Log", "Activities", "Trends", "Monitoring", "Data editor"
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

    st.markdown("#### Activity reach by location and intervention")
    st.caption("These filters and charts use recorded Activity Log entries. Excel target and progress figures above remain district-wide.")
    dashboard_records = pd.DataFrame(load_activity_log())
    if dashboard_records.empty:
        st.info("Record an activity in the Activity Log to see palika, ward, intervention, and demographic summaries here.")
    else:
        dashboard_columns = [
            'Output', 'Output activity', 'Palika', 'Ward', 'Sub-activity', 'People benefited',
            'Households', 'Male', 'Female', 'Children', 'Boys', 'Girls', 'PWD'
        ]
        for column in dashboard_columns:
            if column not in dashboard_records:
                dashboard_records[column] = pd.NA
        for column in ['Output', 'Output activity', 'Palika', 'Ward', 'Sub-activity']:
            dashboard_records[column] = (
                dashboard_records[column].fillna('Not recorded').astype(str).str.strip()
                .replace('', 'Not recorded')
            )
        dashboard_numeric_columns = [
            'People benefited', 'Households', 'Male', 'Female', 'Children', 'Boys', 'Girls', 'PWD'
        ]
        for column in dashboard_numeric_columns:
            dashboard_records[column] = pd.to_numeric(dashboard_records[column], errors='coerce')

        output_filter_col, output_activity_filter_col, palika_filter_col, ward_filter_col, activity_filter_col = st.columns(5)
        output_options = ['All outputs'] + sorted(dashboard_records['Output'].unique().tolist())
        with output_filter_col:
            dashboard_output = st.selectbox('Output', output_options, key='overview_activity_output')
        output_scope = dashboard_records if dashboard_output == 'All outputs' else dashboard_records[
            dashboard_records['Output'] == dashboard_output
        ]

        output_activity_options = ['All output activities'] + sorted(output_scope['Output activity'].unique().tolist())
        with output_activity_filter_col:
            dashboard_output_activity = st.selectbox(
                'Output activity', output_activity_options, key='overview_activity_indicator'
            )
        output_activity_scope = output_scope if dashboard_output_activity == 'All output activities' else output_scope[
            output_scope['Output activity'] == dashboard_output_activity
        ]

        palika_options = ['All palikas'] + sorted(output_activity_scope['Palika'].unique().tolist())
        with palika_filter_col:
            dashboard_palika = st.selectbox('Palika', palika_options, key='overview_activity_palika')
        palika_scope = output_activity_scope if dashboard_palika == 'All palikas' else output_activity_scope[
            output_activity_scope['Palika'] == dashboard_palika
        ]

        ward_options = ['All wards'] + sorted(palika_scope['Ward'].unique().tolist())
        with ward_filter_col:
            dashboard_ward = st.selectbox('Ward', ward_options, key='overview_activity_ward')
        ward_scope = palika_scope if dashboard_ward == 'All wards' else palika_scope[
            palika_scope['Ward'] == dashboard_ward
        ]

        activity_options = ['All activities'] + sorted(ward_scope['Sub-activity'].unique().tolist())
        with activity_filter_col:
            dashboard_activity = st.selectbox('Activity / intervention', activity_options, key='overview_activity_name')
        filtered_activities = ward_scope if dashboard_activity == 'All activities' else ward_scope[
            ward_scope['Sub-activity'] == dashboard_activity
        ]

        def format_reported_total(series):
            total = series.sum(min_count=1)
            return 'Not reported' if pd.isna(total) else f'{total:,.0f}'

        reach_metrics = st.columns(4)
        reach_metrics[0].metric('People benefited', format_reported_total(filtered_activities['People benefited']))
        reach_metrics[1].metric('Households', format_reported_total(filtered_activities['Households']))
        reach_metrics[2].metric('Children', format_reported_total(filtered_activities['Children']))
        reach_metrics[3].metric('People with disabilities', format_reported_total(filtered_activities['PWD']))

        intervention_summary = (
            filtered_activities.groupby(['Output', 'Sub-activity'], as_index=False)['People benefited']
            .sum(min_count=1)
            .dropna(subset=['People benefited'])
            .sort_values('People benefited', ascending=False)
        )
        location_summary = (
            filtered_activities.groupby(['Palika', 'Ward'], as_index=False)['People benefited']
            .sum(min_count=1)
            .dropna(subset=['People benefited'])
        )
        location_summary['Palika / ward'] = location_summary['Palika'] + ' / Ward ' + location_summary['Ward']

        intervention_col, location_col = st.columns(2)
        with intervention_col:
            st.markdown('**People reached by intervention**')
            if intervention_summary.empty:
                st.info('No beneficiary counts have been reported for this selection.')
            else:
                intervention_chart = px.bar(
                    intervention_summary,
                    x='People benefited',
                    y='Sub-activity',
                    color='Output',
                    barmode='group',
                    orientation='h',
                    height=max(340, min(650, 42 * len(intervention_summary) + 120))
                )
                st.plotly_chart(apply_chart_theme(intervention_chart), width='stretch')

        with location_col:
            st.markdown('**People reached by palika and ward**')
            if location_summary.empty:
                st.info('No beneficiary counts have been reported for this selection.')
            else:
                location_chart = px.bar(
                    location_summary.sort_values('People benefited'),
                    x='People benefited',
                    y='Palika / ward',
                    orientation='h',
                    height=max(340, min(650, 42 * len(location_summary) + 120))
                )
                st.plotly_chart(apply_chart_theme(location_chart), width='stretch')

        st.markdown('**Gender and child counts by intervention**')
        st.caption('Male/female and boys/girls are shown as entered. Do not add these categories together unless your reporting definitions make them mutually exclusive.')
        gender_fields = ['Male', 'Female', 'Boys', 'Girls']
        gender_summary = (
            filtered_activities.groupby('Sub-activity')[gender_fields]
            .sum(min_count=1)
            .reset_index()
            .melt(id_vars='Sub-activity', var_name='Reported group', value_name='People')
            .dropna(subset=['People'])
        )
        if gender_summary.empty:
            st.info('No gender or child counts have been reported for this selection.')
        else:
            gender_chart = px.bar(
                gender_summary,
                x='Sub-activity',
                y='People',
                color='Reported group',
                barmode='group',
                height=400
            )
            st.plotly_chart(apply_chart_theme(gender_chart), width='stretch')

        st.markdown('**Disaggregated activity data**')
        breakdown_columns = ['Palika', 'Ward', 'Output', 'Sub-activity'] + dashboard_numeric_columns
        activity_breakdown = (
            filtered_activities.groupby(['Palika', 'Ward', 'Output', 'Sub-activity'])[dashboard_numeric_columns]
            .sum(min_count=1)
            .reset_index()
        )
        st.dataframe(activity_breakdown[breakdown_columns], width='stretch', hide_index=True)

# =========================================================
# TAB 2: SUB-ACTIVITY LOG
# =========================================================
with tab_activity_log:
    st.subheader("Activity Log")
    st.caption("Add entries in the same structure used in your field report: schools, holding centers, child-friendly spaces, and material distribution.")

    activity_records = load_activity_log()
    category_summary = {
        "Schools": 0,
        "Holding Centers": 0,
        "Child-Friendly Spaces": 0,
        "Material Distribution": 0,
        "Other Intervention": 0,
    }
    for record in activity_records:
        category = record.get("Category")
        if category in category_summary:
            category_summary[category] += 1

    summary_cols = st.columns(5)
    summary_cols[0].metric("Total entries", len(activity_records))
    summary_cols[1].metric("Schools", category_summary["Schools"])
    summary_cols[2].metric("Holding centers", category_summary["Holding Centers"])
    summary_cols[3].metric("Child-friendly spaces", category_summary["Child-Friendly Spaces"])
    summary_cols[4].metric("Other interventions", category_summary["Other Intervention"])

    report_category = st.selectbox(
        "Entry type",
        ["Schools", "Holding Centers", "Child-Friendly Spaces", "Material Distribution", "Other Intervention"],
        key="report_entry_category",
        help="Choose the report section that matches the data you want to log."
    )

    selected_output = st.selectbox("Output", OUTPUT_ORDER, key="activity_log_linked_output")
    output_activity_rows = st.session_state.data_matrix[
        st.session_state.data_matrix['CCC Output'] == selected_output
    ]
    output_activity_options = (
        output_activity_rows['Indicator'].dropna().astype(str).str.strip().loc[lambda values: values.ne('')].drop_duplicates().tolist()
    )
    output_activity_options.append("Other activity (specify)")
    selected_output_activity = st.selectbox(
        "Output activity / indicator",
        output_activity_options,
        key="activity_log_linked_indicator",
        help="Choose an activity indicator from the selected output to link this sub-activity to it."
    )
    if selected_output_activity == "Other activity (specify)":
        linked_output_activity = st.text_input(
            "Specify output activity",
            placeholder="Enter an activity that belongs to this output",
            key="activity_log_custom_indicator"
        )
    else:
        linked_output_activity = selected_output_activity

    with st.form("report_entry_form", clear_on_submit=True):
        st.caption("Choose the type of work above, then enter where it happened, what was done, and the people reached. Counts can be left at 0 when not reported.")
        site = st.text_input(
            "Site / location (where was the work done?)",
            placeholder="For example: Nildkantha Secondary School - Uttargaya-5",
            help="Enter the school, health facility, holding center, community, or distribution location."
        )
        location_col, ward_col = st.columns(2)
        with location_col:
            activity_palika = st.text_input("Palika", placeholder="For example: Uttargaya RM")
        with ward_col:
            activity_ward = st.text_input("Ward number", placeholder="For example: 5")

        if report_category == "Material Distribution":
            item = st.text_input("Item / material distributed", placeholder="For example: Hygiene Kit", help="Name the item that was distributed.")
            quantity = st.number_input("Number of items distributed", min_value=0, value=0, step=1, help="Total number of items or kits given out.")
            beneficiaries = st.number_input("People who benefited", min_value=0, value=0, step=1, help="Number of people reached, not the number of items.")
            unit = st.text_input("Item unit", placeholder="For example: kits, buckets, blankets", help="What does the quantity count?")
            remarks = st.text_area("Notes or missing information", placeholder="For example: Uttargaya update pending.")
        elif report_category == "Other Intervention":
            other_intervention = st.text_input(
                "Intervention name (what type of work?)",
                placeholder="For example: Water supply scheme, HCF repair, or hygiene promotion",
                help="Use this to name an activity type not covered by Schools, Holding Centers, Child-Friendly Spaces, or Material Distribution."
            )
            activity = st.text_area(
                "Sub-activity (what action was completed?)",
                height=100,
                placeholder="Describe the work completed, such as repairing a water supply scheme.",
                help="Add the specific action carried out for this intervention."
            )
            beneficiaries = st.number_input("People who benefited", min_value=0, value=0, step=1, help="Number of people reached. Enter 0 if not yet reported.")
            remarks = st.text_area("Notes or missing information", placeholder="For example: Beneficiary breakdown to be updated.")
        else:
            activity = st.text_area(
                "Sub-activity (what action was completed?)",
                height=120,
                placeholder="For example: Full repair & maintenance of water storage reservoir tank",
                help="Describe the activity clearly in the same way as your report table."
            )
            beneficiaries = st.number_input("People who benefited", min_value=0, value=0, step=1, help="Total number of people reached. Enter 0 if not yet reported.")
            remarks = st.text_area("Notes or missing information", placeholder="For example: Segregated data yet to be updated.")

        with st.expander("Demographic information (optional)", expanded=False):
            demographic_inputs = render_demographic_inputs(key_prefix="new_activity_demographics")

        submit_entry = st.form_submit_button("Save entry", type="primary")

    if submit_entry:
        if not site.strip():
            st.error("Please enter the site or location before saving.")
        elif not activity_palika.strip() or not activity_ward.strip():
            st.error("Please enter both the palika and ward so this entry can be filtered by location.")
        elif not linked_output_activity.strip():
            st.error("Choose an output activity or enter a custom activity before saving.")
        elif report_category == "Other Intervention" and not other_intervention.strip():
            st.error("Please enter the name of the other intervention before saving.")
        else:
            record = {
                "id": uuid4().hex,
                "Category": report_category,
                "Output": selected_output,
                "Output activity": linked_output_activity.strip(),
                "Sub-activity": item.strip() if report_category == "Material Distribution" and item.strip() else (
                    activity.strip() if report_category != "Material Distribution" else "Material distribution"
                ),
                "Site": site.strip(),
                "Palika": activity_palika.strip(),
                "Ward": activity_ward.strip(),
                "Recorded": datetime.now().strftime('%Y-%m-%d %H:%M'),
                "Beneficiaries": int(beneficiaries),
                "Remarks": remarks.strip(),
            }
            record.update({field: int(value) for field, value in demographic_inputs.items()})

            if report_category == "Material Distribution":
                record.update({
                    "Activity": item.strip() if item.strip() else "Material distribution",
                    "Item": item.strip(),
                    "Quantity": int(quantity),
                    "Unit": unit.strip(),
                })
            else:
                record.update({
                    "Activity": (
                        f"{other_intervention.strip()}: {activity.strip()}"
                        if report_category == "Other Intervention" and activity.strip()
                        else other_intervention.strip() if report_category == "Other Intervention"
                        else activity.strip()
                    ),
                    "Intervention type": other_intervention.strip() if report_category == "Other Intervention" else "",
                })

            activity_records.append(record)
            try:
                save_activity_log(activity_records)
                st.success(f"{report_category} entry saved.")
                st.rerun()
            except OSError as error:
                st.error(f"Could not save the entry: {error}")

    category_record_indices = [
        index for index, record in enumerate(activity_records)
        if record.get("Category") == report_category
    ]
    if category_record_indices:
        records_df = pd.DataFrame(
            [activity_records[index] for index in category_record_indices],
            index=category_record_indices
        )
        display_columns = [
            "Recorded", "Site", "Palika", "Ward", "Output", "Output activity",
            "Sub-activity", "Beneficiaries", *DEMOGRAPHIC_COLUMNS,
            "Quantity", "Unit", "Item", "Remarks"
        ]
        for column in display_columns:
            if column not in records_df.columns:
                records_df[column] = pd.NA
        records_df["Sub-activity"] = records_df["Sub-activity"].fillna(records_df["Activity"]).fillna("Not recorded")
        for column in ["Palika", "Ward", "Output", "Output activity"]:
            records_df[column] = (
                records_df[column].fillna("Not linked").astype(str).str.strip()
                .replace("", "Not linked")
            )
        records_df["Beneficiaries"] = pd.to_numeric(records_df["Beneficiaries"], errors="coerce")

        filter_columns = st.columns(5)
        with filter_columns[0]:
            output_filter_options = ["All outputs"] + sorted(records_df["Output"].unique().tolist())
            log_output_filter = st.selectbox("Filter by output", output_filter_options, key="activity_log_filter_output")
        output_filtered_records = records_df if log_output_filter == "All outputs" else records_df[
            records_df["Output"] == log_output_filter
        ]
        with filter_columns[1]:
            output_activity_filter_options = ["All output activities"] + sorted(output_filtered_records["Output activity"].unique().tolist())
            log_output_activity_filter = st.selectbox(
                "Filter by output activity", output_activity_filter_options,
                key="activity_log_filter_output_activity"
            )
        output_activity_filtered_records = output_filtered_records if log_output_activity_filter == "All output activities" else output_filtered_records[
            output_filtered_records["Output activity"] == log_output_activity_filter
        ]
        with filter_columns[2]:
            palika_filter_options = ["All palikas"] + sorted(output_activity_filtered_records["Palika"].unique().tolist())
            log_palika_filter = st.selectbox("Filter by palika", palika_filter_options, key="activity_log_filter_palika")
        palika_filtered_records = output_activity_filtered_records if log_palika_filter == "All palikas" else output_activity_filtered_records[
            output_activity_filtered_records["Palika"] == log_palika_filter
        ]
        with filter_columns[3]:
            ward_filter_options = ["All wards"] + sorted(palika_filtered_records["Ward"].unique().tolist())
            log_ward_filter = st.selectbox("Filter by ward", ward_filter_options, key="activity_log_filter_ward")
        ward_filtered_records = palika_filtered_records if log_ward_filter == "All wards" else palika_filtered_records[
            palika_filtered_records["Ward"] == log_ward_filter
        ]
        with filter_columns[4]:
            subactivity_filter_options = ["All sub-activities"] + sorted(ward_filtered_records["Sub-activity"].astype(str).unique().tolist())
            log_subactivity_filter = st.selectbox("Filter by sub-activity", subactivity_filter_options, key="activity_log_filter_subactivity")
        visible_records = ward_filtered_records if log_subactivity_filter == "All sub-activities" else ward_filtered_records[
            ward_filtered_records["Sub-activity"].astype(str) == log_subactivity_filter
        ]

        st.markdown(f"#### {report_category} entries")
        st.dataframe(visible_records[display_columns], width="stretch", hide_index=True)

        st.markdown("#### Edit a saved entry")
        st.caption("Select an entry from the filtered results, update its details or links, then save your changes.")
        if visible_records.empty:
            st.info("No entries match these filters.")
        else:
            editable_indices = visible_records.index.tolist()
            selected_record_index = st.selectbox(
                "Entry to edit",
                editable_indices,
                format_func=lambda index: (
                    f"{activity_records[index].get('Site', 'Unnamed site')} — "
                    f"{activity_records[index].get('Sub-activity', activity_records[index].get('Activity', 'Activity'))}"
                ),
                key="activity_log_edit_selection"
            )
            selected_record = activity_records[selected_record_index]
            edit_id = selected_record.get("id", f"legacy_{selected_record_index}")

            stored_output = selected_record.get("Output", OUTPUT_ORDER[0])
            edited_output = st.selectbox(
                "Output",
                OUTPUT_ORDER,
                index=OUTPUT_ORDER.index(stored_output) if stored_output in OUTPUT_ORDER else 0,
                key=f"edit_output_{edit_id}"
            )
            edit_output_rows = st.session_state.data_matrix[
                st.session_state.data_matrix['CCC Output'] == edited_output
            ]
            edit_output_options = (
                edit_output_rows['Indicator'].dropna().astype(str).str.strip()
                .loc[lambda values: values.ne('')].drop_duplicates().tolist()
            )
            edit_output_options.append("Other activity (specify)")
            stored_output_activity = str(selected_record.get("Output activity", ""))
            selected_edit_activity = st.selectbox(
                "Output activity / indicator",
                edit_output_options,
                index=edit_output_options.index(stored_output_activity) if stored_output_activity in edit_output_options else len(edit_output_options) - 1,
                key=f"edit_output_indicator_{edit_id}"
            )
            if selected_edit_activity == "Other activity (specify)":
                edited_output_activity = st.text_input(
                    "Specify output activity",
                    value=stored_output_activity if stored_output_activity not in edit_output_options else "",
                    key=f"edit_custom_output_activity_{edit_id}"
                )
            else:
                edited_output_activity = selected_edit_activity

            with st.form(f"edit_activity_{edit_id}"):
                edited_site = st.text_input(
                    "Site / location",
                    value=str(selected_record.get("Site", "")),
                    key=f"edit_site_{edit_id}"
                )
                edited_location_col, edited_ward_col = st.columns(2)
                with edited_location_col:
                    edited_palika = st.text_input(
                        "Palika", value=str(selected_record.get("Palika", "")),
                        key=f"edit_palika_{edit_id}"
                    )
                with edited_ward_col:
                    edited_ward = st.text_input(
                        "Ward number", value=str(selected_record.get("Ward", "")),
                        key=f"edit_ward_{edit_id}"
                    )
                if report_category == "Material Distribution":
                    edited_quantity_value = pd.to_numeric(selected_record.get("Quantity"), errors="coerce")
                    edited_item = st.text_input(
                        "Item / material distributed",
                        value=str(selected_record.get("Item", selected_record.get("Activity", ""))),
                        key=f"edit_item_{edit_id}"
                    )
                    edited_quantity = st.number_input(
                        "Number of items distributed", min_value=0,
                        value=0 if pd.isna(edited_quantity_value) else max(0, int(edited_quantity_value)),
                        step=1, key=f"edit_quantity_{edit_id}"
                    )
                    edited_unit = st.text_input(
                        "Item unit", value=str(selected_record.get("Unit", "")),
                        key=f"edit_unit_{edit_id}"
                    )
                else:
                    edited_intervention = ""
                    activity_value = str(selected_record.get("Activity", ""))
                    if report_category == "Other Intervention":
                        edited_intervention = str(selected_record.get("Intervention type", ""))
                        if edited_intervention and activity_value.startswith(f"{edited_intervention}: "):
                            activity_value = activity_value[len(edited_intervention) + 2:]
                        edited_intervention = st.text_input(
                            "Intervention name",
                            value=edited_intervention,
                            key=f"edit_intervention_{edit_id}"
                        )
                    edited_activity = st.text_area(
                        "Sub-activity",
                        value=str(selected_record.get("Sub-activity", activity_value)),
                        height=100,
                        key=f"edit_activity_description_{edit_id}"
                    )

                edited_beneficiaries_value = pd.to_numeric(selected_record.get("Beneficiaries"), errors="coerce")
                edited_beneficiaries = st.number_input(
                    "People who benefited",
                    min_value=0,
                    value=0 if pd.isna(edited_beneficiaries_value) else max(0, int(edited_beneficiaries_value)),
                    step=1,
                    key=f"edit_beneficiaries_{edit_id}"
                )
                with st.expander("Edit demographic information", expanded=False):
                    edited_demographics = render_demographic_inputs(
                        selected_record,
                        key_prefix=f"edit_demographics_{edit_id}"
                    )
                edited_remarks = st.text_area(
                    "Notes or missing information",
                    value=str(selected_record.get("Remarks", "")),
                    key=f"edit_remarks_{edit_id}"
                )
                save_edit = st.form_submit_button("Save changes", type="primary")

            if save_edit:
                if not edited_site.strip():
                    st.error("Please enter the site or location before saving changes.")
                elif not edited_palika.strip() or not edited_ward.strip():
                    st.error("Please enter both the palika and ward before saving changes.")
                elif not edited_output_activity.strip():
                    st.error("Please enter the linked output activity before saving changes.")
                elif report_category == "Other Intervention" and not edited_intervention.strip():
                    st.error("Please enter the intervention name before saving changes.")
                else:
                    updated_record = {
                        **selected_record,
                        "Output": edited_output,
                        "Output activity": edited_output_activity.strip(),
                        "Sub-activity": (
                            edited_item.strip() if report_category == "Material Distribution" and edited_item.strip()
                            else edited_activity.strip() if report_category != "Material Distribution"
                            else "Material distribution"
                        ),
                        "Site": edited_site.strip(),
                        "Palika": edited_palika.strip(),
                        "Ward": edited_ward.strip(),
                        "Beneficiaries": int(edited_beneficiaries),
                        "Remarks": edited_remarks.strip(),
                        "Updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
                        **{field: int(value) for field, value in edited_demographics.items()},
                    }
                    if report_category == "Material Distribution":
                        updated_record.update({
                            "Activity": edited_item.strip() or "Material distribution",
                            "Item": edited_item.strip(),
                            "Quantity": int(edited_quantity),
                            "Unit": edited_unit.strip(),
                        })
                    else:
                        updated_record["Activity"] = (
                            f"{edited_intervention.strip()}: {edited_activity.strip()}"
                            if report_category == "Other Intervention" and edited_activity.strip()
                            else edited_intervention.strip() if report_category == "Other Intervention"
                            else edited_activity.strip()
                        )
                        if report_category == "Other Intervention":
                            updated_record["Intervention type"] = edited_intervention.strip()
                    activity_records[selected_record_index] = updated_record
                    try:
                        save_activity_log(activity_records)
                        st.success("Activity entry updated.")
                        st.rerun()
                    except OSError as error:
                        st.error(f"Could not update the activity log: {error}")

        chart_df = visible_records.groupby("Site", as_index=False)["Beneficiaries"].sum().sort_values("Beneficiaries", ascending=False)
        if not chart_df.empty and (chart_df["Beneficiaries"] > 0).any():
            st.markdown("#### Beneficiaries by site")
            fig = px.bar(
                chart_df,
                x="Site",
                y="Beneficiaries",
                title=f"People reached across {report_category}",
                color="Beneficiaries",
                color_continuous_scale="Teal",
                height=420
            )
            st.plotly_chart(apply_chart_theme(fig), width="stretch")

        if report_category != "Material Distribution":
            gender_source = visible_records.copy()
            for demographic in ["Male", "Female"]:
                gender_source[demographic] = pd.to_numeric(gender_source[demographic], errors="coerce").fillna(0)
            gender_summary = gender_source.groupby("Site", as_index=False)[["Male", "Female"]].sum()
            if not gender_summary.empty:
                st.markdown("#### Male and female beneficiaries by site")
                gender_chart = px.bar(
                    gender_summary.melt(id_vars="Site", var_name="Gender", value_name="Count"),
                    x="Site",
                    y="Count",
                    color="Gender",
                    barmode="group",
                    height=420
                )
                st.plotly_chart(apply_chart_theme(gender_chart), width="stretch")
    else:
        st.info(f"No {report_category.lower()} entries have been added yet.")

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

    activity_paragraphs = activity_details[
        activity_details['Activity'].fillna('').astype(str).str.strip().ne('')
    ]
    st.markdown("#### Activities undertaken to achieve progress")
    if activity_paragraphs.empty:
        st.info("No activity description has been recorded in the Excel sheet for this output.")
    else:
        for _, activity_row in activity_paragraphs.iterrows():
            indicator = str(activity_row['Indicator'])
            with st.expander(indicator):
                st.write(str(activity_row['Activity']))
                st.caption(
                    f"Output: {activity_row['CCC Output']} | "
                    f"Daily achieved: {activity_row['Progress']:,.0f} "
                    f"of {activity_row['Target']:,.0f}"
                )

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
# TAB 4: MONITORING VIEW
# =========================================================
with tab_monitoring:
    st.subheader("Progress Monitoring Center")
    st.caption("Progress rises from light green to fully green as the target is approached and completed.")

    st.markdown("#### Progress by output")
    tracking = summarize_outputs(
        df_active, ['Target', 'Progress']
    )
    heatmap_pct = pd.DataFrame(index=tracking.index)
    heatmap_pct['Progress %'] = (
        tracking['Progress'] / tracking['Target'].replace(0, 1) * 100
    ).round(1)
    fig_heatmap = px.imshow(
        heatmap_pct,
        text_auto='.1f',
        aspect='auto',
        color_continuous_scale=['#dcfce7', '#bbf7d0', '#86efac', '#16a34a', '#166534'],
        range_color=[0, 100],
        labels={'x': 'Metric', 'y': 'Output', 'color': 'Progress %'},
        height=max(420, min(760, 42 * len(heatmap_pct) + 140))
    )
    fig_heatmap.update_traces(texttemplate='%{z:.1f}%', textfont={'color': '#243331'})
    st.plotly_chart(apply_chart_theme(fig_heatmap), width="stretch")
    st.info("Progress is shown on a green scale: lighter green means early progress, and full dark green indicates the target has been achieved.")

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
# TAB 5: TARGET & PROGRESS EDITOR (LIVE UPDATE)
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

