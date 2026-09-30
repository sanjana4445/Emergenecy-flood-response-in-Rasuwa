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
DEMOGRAPHIC_COLUMNS = ['Households', 'Male', 'Female', 'Children', 'Boys', 'Girls', 'PWD']

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

st.markdown("#### Output-wise daily performance", unsafe_allow_html=True)
st.caption("Each activity shows its Excel target, achieved progress, and completion percentage.")
for row_start in range(0, len(OUTPUT_ORDER), 2):
    card_columns = st.columns(2, gap="medium")
    for column_index, output_name in enumerate(OUTPUT_ORDER[row_start:row_start + 2]):
        output_activities = df_active[df_active['CCC Output'] == output_name]
        activity_markup = []
        for _, activity_row in output_activities.iterrows():
            target = float(activity_row['Target'])
            achieved = float(activity_row['Progress'])
            progress_pct = achieved / target * 100 if target else 0
            status = 'Met target' if target > 0 and achieved >= target else ('No target recorded' if target == 0 else 'Target not met')
            indicator = escape(str(activity_row['Indicator']))
            activity = str(activity_row['Activity']).strip()
            description = f'<div class="activity-description">{escape(activity)}</div>' if activity else ''
            activity_markup.append(
                f'<div class="activity-item">'
                f'<div class="activity-name">{indicator}</div>'
                f'{description}'
                f'<div class="output-card-row"><span>Target</span><strong>{target:,.0f}</strong></div>'
                f'<div class="output-card-row"><span>Achieved</span><strong>{achieved:,.0f}</strong></div>'
                f'<div class="output-card-row"><span>Progress</span><strong>{progress_pct:.1f}%</strong></div>'
                f'<div class="output-status {"output-met" if status == "Met target" else "output-pending"}">{status}</div>'
                f'</div>'
            )
        with card_columns[column_index]:
            card_markup = (
                f'<div class="metric-card output-card">'
                f'<div class="metric-title">{escape(output_name)}</div>'
                f'{"".join(activity_markup)}'
                f'</div>'
            )
            st.html(card_markup)

# ---------------------------------------------------------
# MAIN DASHBOARD TABS
# ---------------------------------------------------------
tab_exec, tab_activity_log, tab_palika, tab_output, tab_timelapse, tab_monitoring, tab_editor = st.tabs([
    "Overview", "Activity Log", "Activities", "Daily Log", "Trends", "Monitoring", "Data editor"
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
            'Output', 'Palika', 'Ward', 'Sub-activity', 'People benefited',
            'Households', 'Male', 'Female', 'Children', 'Boys', 'Girls', 'PWD'
        ]
        for column in dashboard_columns:
            if column not in dashboard_records:
                dashboard_records[column] = pd.NA
        for column in ['Output', 'Palika', 'Ward', 'Sub-activity']:
            dashboard_records[column] = (
                dashboard_records[column].fillna('Not recorded').astype(str).str.strip()
                .replace('', 'Not recorded')
            )
        dashboard_numeric_columns = [
            'People benefited', 'Households', 'Male', 'Female', 'Children', 'Boys', 'Girls', 'PWD'
        ]
        for column in dashboard_numeric_columns:
            dashboard_records[column] = pd.to_numeric(dashboard_records[column], errors='coerce')

        output_filter_col, palika_filter_col, ward_filter_col, activity_filter_col = st.columns(4)
        output_options = ['All outputs'] + sorted(dashboard_records['Output'].unique().tolist())
        with output_filter_col:
            dashboard_output = st.selectbox('Output', output_options, key='overview_activity_output')
        output_scope = dashboard_records if dashboard_output == 'All outputs' else dashboard_records[
            dashboard_records['Output'] == dashboard_output
        ]

        palika_options = ['All palikas'] + sorted(output_scope['Palika'].unique().tolist())
        with palika_filter_col:
            dashboard_palika = st.selectbox('Palika', palika_options, key='overview_activity_palika')
        palika_scope = output_scope if dashboard_palika == 'All palikas' else output_scope[
            output_scope['Palika'] == dashboard_palika
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
    st.subheader("Record an activity")
    st.caption("Create one entry for one completed activity in one ward. For example: repaired taps in Kalika, Ward 2.")

    selected_log_output = st.selectbox(
        "Output / result area",
        OUTPUT_ORDER,
        key="activity_log_output",
        help="Choose the result area this activity supports."
    )
    activity_records = load_activity_log()

    with st.form("add_output_activity", clear_on_submit=True):
        st.markdown("#### What was done and where?")
        subactivity = st.text_input(
            "Activity / intervention",
            placeholder="For example: Repaired household taps",
            help="Describe the work completed, not the result total."
        )
        location_col, ward_col = st.columns(2)
        with location_col:
            activity_palika = st.text_input(
                "Palika",
                placeholder="For example: Kalika",
                help="Use the same spelling each time so entries group together."
            )
        with ward_col:
            activity_ward = st.text_input("Ward number", placeholder="For example: 2")

        st.markdown("#### Quantity and people reached")
        quantity_col, unit_col = st.columns(2)
        with quantity_col:
            delivered_quantity = st.number_input(
                "Items or events delivered",
                min_value=0,
                value=None,
                step=1,
                help="Count items or events, such as 12 taps or 1 training. This is not a people count."
            )
        with unit_col:
            quantity_unit = st.text_input("Unit", placeholder="For example: taps, kits, trainings")
        people_col, notes_col = st.columns(2)
        with people_col:
            people_benefited = st.number_input(
                "People reached",
                min_value=0,
                value=None,
                step=1,
                help="Enter the number of people reached by this activity, if known. Leave blank if it was not recorded."
            )
        with notes_col:
            activity_notes = st.text_input(
                "Site or notes (optional)",
                placeholder="For example: Thulo Gaun health post"
            )

        with st.expander("Optional: demographic breakdown", expanded=False):
            st.caption("Enter counts from your source records. Leave unknown counts blank. Record categories as defined by your reporting form; some groups may overlap.")
            demographic_labels = {
                'Households': 'Households reached',
                'Male': 'Male people',
                'Female': 'Female people',
                'Children': 'Children (total)',
                'Boys': 'Boys',
                'Girls': 'Girls',
                'PWD': 'People with disabilities',
            }
            demographic_inputs = {}
            demographic_columns = st.columns(2)
            for index, demographic in enumerate(DEMOGRAPHIC_COLUMNS):
                with demographic_columns[index % len(demographic_columns)]:
                    demographic_inputs[demographic] = st.number_input(
                        demographic_labels[demographic],
                        min_value=0,
                        value=None,
                        step=1,
                        key=f"activity_{demographic.lower()}"
                    )

        add_activity = st.form_submit_button("Save activity", type="primary")

    if add_activity:
        if not subactivity.strip() or not activity_palika.strip() or not activity_ward.strip():
            st.error("Enter a sub-activity, palika, and ward before adding it.")
        else:
            new_activity = {
                "id": uuid4().hex,
                "Output": selected_log_output,
                "Sub-activity": subactivity.strip(),
                "Palika": activity_palika.strip(),
                "Ward": activity_ward.strip(),
                "Quantity": int(delivered_quantity) if delivered_quantity is not None else None,
                "Unit": quantity_unit.strip(),
                "People benefited": int(people_benefited) if people_benefited is not None else None,
                "Location / notes": activity_notes.strip(),
                "Recorded": datetime.now().strftime('%Y-%m-%d %H:%M'),
            }
            new_activity.update({
                column: int(value) if value is not None else None
                for column, value in demographic_inputs.items()
            })
            activity_records.append(new_activity)
            try:
                save_activity_log(activity_records)
                st.success("Sub-activity saved.")
            except OSError as error:
                activity_records.pop()
                st.error(f"Could not save the activity log: {error}")

    output_records = [
        (index, record) for index, record in enumerate(activity_records)
        if record.get("Output") == selected_log_output
    ]
    if output_records:
        record_frame = pd.DataFrame([record for _, record in output_records])
        for column in [
            'Recorded', 'Palika', 'Ward', 'Sub-activity', 'Quantity', 'Unit',
            'People benefited', 'Location / notes', *DEMOGRAPHIC_COLUMNS
        ]:
            if column not in record_frame:
                record_frame[column] = pd.NA
        for column in DEMOGRAPHIC_COLUMNS:
            record_frame[column] = pd.to_numeric(record_frame[column], errors='coerce')
        record_frame['People benefited'] = pd.to_numeric(record_frame['People benefited'], errors='coerce')
        total_people = record_frame['People benefited'].sum(min_count=1)
        metric_columns = st.columns(2)
        metric_columns[0].metric("Sub-activities recorded", len(record_frame))
        metric_columns[1].metric(
            "People reached",
            "Not reported" if pd.isna(total_people) else f"{total_people:,.0f}"
        )

        st.markdown("#### People reached by activity")
        chart_data = (
            record_frame.groupby('Sub-activity')['People benefited']
            .sum(min_count=1)
            .reset_index()
            .sort_values('People benefited', ascending=False)
        )
        chart_data = chart_data[chart_data['People benefited'].fillna(0) > 0]
        if chart_data.empty:
            st.info("Enter a people-reached count to show this chart.")
        else:
            figure = px.pie(
                chart_data,
                values='People benefited',
                names='Sub-activity',
                hole=0.45,
                title=f"People reached across {selected_log_output} activities"
            )
            figure.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(apply_chart_theme(figure), width="stretch")

        st.markdown("#### Recorded sub-activities")
        st.caption("Each row is one activity entry. Blank counts mean they were not reported; the activity quantity is separate from the people-reached count.")
        st.dataframe(
            record_frame[[
                'Recorded', 'Palika', 'Ward', 'Sub-activity', 'Quantity', 'Unit',
                'People benefited', *DEMOGRAPHIC_COLUMNS, 'Location / notes'
            ]],
            width="stretch",
            hide_index=True
        )

        location_records = record_frame[
            record_frame['Palika'].fillna('').astype(str).str.strip().ne('')
            & record_frame['Ward'].fillna('').astype(str).str.strip().ne('')
        ].copy()
        if not location_records.empty:
            st.markdown("#### People reached by palika and ward")
            st.caption("Blank demographic values mean they were not reported. Older entries without location or demographic details are not included in these totals.")
            location_totals = (
                location_records.groupby(['Palika', 'Ward'])[DEMOGRAPHIC_COLUMNS]
                .sum(min_count=1)
                .reset_index()
            )
            st.dataframe(location_totals, width="stretch", hide_index=True)

            st.markdown("#### People reached by activity and location")
            activity_location_totals = (
                location_records.groupby(['Palika', 'Ward', 'Sub-activity'])[DEMOGRAPHIC_COLUMNS]
                .sum(min_count=1)
                .reset_index()
            )
            st.dataframe(activity_location_totals, width="stretch", hide_index=True)
        else:
            st.info("Add a new activity with its palika and ward to see location-based demographic totals.")

        remove_options = [index for index, _ in output_records]
        remove_index = st.selectbox(
            "Select a record to remove",
            remove_options,
            format_func=lambda index: (
                f"{activity_records[index]['Sub-activity']} "
                f"({int(activity_records[index]['People benefited']):,} people)"
                if pd.notna(activity_records[index].get('People benefited'))
                else f"{activity_records[index]['Sub-activity']} (people not reported)"
            ),
            key="activity_log_remove"
        )
        if st.button("Remove selected record", key="remove_activity_record"):
            activity_records.pop(remove_index)
            try:
                save_activity_log(activity_records)
                st.rerun()
            except OSError as error:
                st.error(f"Could not update the activity log: {error}")
    else:
        st.info("No sub-activities have been recorded for this output yet.")

    output_targets = df_active[df_active['CCC Output'] == selected_log_output][[
        'Indicator', 'Unit', 'Target', 'Weekly Target'
    ]].rename(columns={
        'Indicator': 'Excel indicator',
        'Unit': 'Unit',
        'Target': 'Daily target',
        'Weekly Target': 'Weekly target'
    })
    st.markdown("#### Existing workbook targets")
    st.dataframe(output_targets, width="stretch", hide_index=True)

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

