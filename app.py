import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
from sklearn.metrics import roc_auc_score
import warnings
warnings.filterwarnings('ignore')

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WorkforceBI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label { color: #94a3b8 !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }

/* Main bg */
.main { background: #0f172a; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* Hero header */
.hero {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 50%, #162032 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.02em;
}
.hero-sub {
    color: #64748b;
    font-size: 0.95rem;
    margin: 0;
}
.hero-pill {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    color: #818cf8;
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 999px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    font-weight: 500;
    margin-right: 0.4rem;
    margin-top: 0.8rem;
}

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #1e293b, #162032);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #6366f1; }
.kpi-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.kpi-delta-up   { color: #34d399; font-size: 0.78rem; font-weight: 500; }
.kpi-delta-down { color: #f87171; font-size: 0.78rem; font-weight: 500; }
.kpi-delta-neu  { color: #94a3b8; font-size: 0.78rem; font-weight: 500; }
.kpi-accent {
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 12px 0 0 12px;
}

/* Section headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e2e8f0;
    margin: 1.5rem 0 0.75rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e293b;
}

/* Insight card */
.insight-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-left: 3px solid #6366f1;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    font-size: 0.88rem;
    color: #cbd5e1;
    line-height: 1.6;
}
.insight-card strong { color: #f1f5f9; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #1e293b;
    padding: 4px;
    border-radius: 10px;
    border: 1px solid #334155;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748b;
    border-radius: 7px;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 0.4rem 1rem;
}
.stTabs [aria-selected="true"] {
    background: #6366f1 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("HR_Employee_Cleaned_Data.csv")
    df.columns = df.columns.str.strip()
    df["Department"] = df["Department"].str.strip()
    df["Sex"] = df["Sex"].str.strip()
    df["PerformanceScore"] = df["PerformanceScore"].str.strip()
    df["RecruitmentSource"] = df["RecruitmentSource"].str.strip()
    df["EmploymentStatus"] = df["EmploymentStatus"].str.strip()
    df["DateofHire"] = pd.to_datetime(df["DateofHire"], errors="coerce")
    df["DateofTermination"] = pd.to_datetime(df["DateofTermination"], errors="coerce")
    df["HireYear"] = df["DateofHire"].dt.year
    df["TenureYears"] = (
        df["DateofTermination"].fillna(pd.Timestamp.now()) - df["DateofHire"]
    ).dt.days / 365
    df["IsTerminated"] = (df["EmploymentStatus"] != "Active").astype(int)
    df["DailyRate"] = df["Salary"] / 260
    df["AbsenceCost"] = df["DailyRate"] * df["Absences"]
    return df

df = load_data()

# ── ML Model Training ────────────────────────────────────────────────────────
@st.cache_resource
def train_model(dataframe):
    """Train a Gradient Boosting classifier to predict attrition probability.
    Returns: model, feature columns, label encoders, cross-val AUC"""
    mdf = dataframe.copy()

    # Encode categoricals
    cat_cols = ["Department", "Sex", "PerformanceScore", "MaritalDesc",
                "RecruitmentSource", "EmploymentStatus"]
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        mdf[col + "_enc"] = le.fit_transform(mdf[col].astype(str))
        encoders[col] = le

    # Performance ordinal
    perf_map = {"PIP": 0, "Needs Improvement": 1, "Fully Meets": 2, "Exceeds": 3}
    mdf["PerfOrdinal"] = mdf["PerformanceScore"].map(perf_map).fillna(1)

    feature_cols = [
        "Salary", "TenureYears", "EngagementSurvey", "EmpSatisfaction",
        "Absences", "DaysLateLast30", "SpecialProjectsCount",
        "Department_enc", "Sex_enc", "PerfOrdinal",
        "MaritalDesc_enc", "RecruitmentSource_enc", "FromDiversityJobFairID"
    ]

    X = mdf[feature_cols].fillna(0)
    y = mdf["IsTerminated"]

    model = GradientBoostingClassifier(
        n_estimators=200, learning_rate=0.05,
        max_depth=4, subsample=0.8,
        random_state=42
    )
    model.fit(X, y)

    # Cross-validated AUC
    cv_auc = cross_val_score(model, X, y, cv=5, scoring="roc_auc").mean()

    return model, feature_cols, encoders, cv_auc, perf_map

model, feature_cols, encoders, cv_auc, perf_map = train_model(df)

def get_risk_scores(dataframe, salary_override=None):
    """Score every employee in dataframe. Optionally override salary for simulation."""
    mdf = dataframe.copy()
    if salary_override is not None:
        mdf["Salary"] = salary_override
    for col, le in encoders.items():
        # Handle unseen labels safely
        mdf[col + "_enc"] = mdf[col].astype(str).apply(
            lambda x: le.transform([x])[0] if x in le.classes_ else 0
        )
    mdf["PerfOrdinal"] = mdf["PerformanceScore"].map(perf_map).fillna(1)
    X = mdf[feature_cols].fillna(0)
    proba = model.predict_proba(X)[:, 1]
    return (proba * 100).round(1)

# ── Plotly theme ──────────────────────────────────────────────────────────────
PALETTE = ["#6366f1", "#34d399", "#f59e0b", "#f87171", "#38bdf8", "#a78bfa", "#fb923c"]
CHART_BG = "#0f172a"
GRID_COLOR = "#1e293b"
TEXT_COLOR = "#94a3b8"

def chart_layout(fig, title="", height=360):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#e2e8f0", family="Inter"), x=0, pad=dict(l=0, b=12)),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="Inter", color=TEXT_COLOR, size=11),
        height=height,
        margin=dict(l=12, r=12, t=40 if title else 12, b=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(size=10)),
    )
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.5rem">
        <div style="font-size:1.2rem;font-weight:700;color:#f1f5f9;letter-spacing:-0.02em">⚡ WorkforceBI</div>
        <div style="font-size:0.75rem;color:#475569;margin-top:2px">HR Analytics Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-bottom:0.5rem">Filters</div>', unsafe_allow_html=True)

    all_depts = sorted(df["Department"].unique())
    sel_depts = st.multiselect("Department", all_depts, default=all_depts, key="dept")

    all_status = sorted(df["EmploymentStatus"].unique())
    sel_status = st.multiselect("Employment Status", all_status, default=all_status, key="status")

    all_perf = ["Exceeds", "Fully Meets", "Needs Improvement", "PIP"]
    sel_perf = st.multiselect("Performance Score", all_perf, default=all_perf, key="perf")

    sal_min, sal_max = int(df["Salary"].min()), int(df["Salary"].max())
    sel_sal = st.slider("Salary Range ($)", sal_min, sal_max, (sal_min, sal_max), step=1000, key="sal")

    st.markdown('<div style="margin-top:2rem;padding-top:1rem;border-top:1px solid #1e293b"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.7rem;color:#334155;text-align:center">Built by Ashay Vairat</div>', unsafe_allow_html=True)

# ── Filter data ───────────────────────────────────────────────────────────────
fdf = df[
    df["Department"].isin(sel_depts) &
    df["EmploymentStatus"].isin(sel_status) &
    df["PerformanceScore"].isin(sel_perf) &
    df["Salary"].between(*sel_sal)
].copy()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <div class="hero-title">📊 WorkforceBI Dashboard</div>
    <p class="hero-sub">Downstream HR reporting pipeline · Python · MySQL · Power BI</p>
    <span class="hero-pill">🧑‍💼 {len(fdf)} employees</span>
    <span class="hero-pill">🏢 {fdf['Department'].nunique()} departments</span>
    <span class="hero-pill">📅 2006 – 2018</span>
    <span class="hero-pill">Ashay Vairat</span>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
active = fdf[fdf["EmploymentStatus"] == "Active"]
terminated = fdf[fdf["IsTerminated"] == 1]
attrition_rate = len(terminated) / len(fdf) * 100 if len(fdf) else 0
avg_salary = fdf["Salary"].mean()
avg_engagement = fdf["EngagementSurvey"].mean()
avg_tenure = fdf["TenureYears"].mean()

k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, label, value, delta, delta_type, accent):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background:{accent}"></div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta-{delta_type}">{delta}</div>
    </div>""", unsafe_allow_html=True)

kpi(k1, "Active Employees", f"{len(active):,}", f"{len(active)/len(fdf)*100:.0f}% of total", "neu", "#34d399")
kpi(k2, "Attrition Rate", f"{attrition_rate:.1f}%", "↑ Highest in Production", "down", "#f87171")
kpi(k3, "Avg Annual Salary", f"${avg_salary:,.0f}", "M: $70.6K  F: $67.8K", "neu", "#6366f1")
kpi(k4, "Avg Engagement", f"{avg_engagement:.2f}/5", "Dataset mean · 4.11", "up", "#f59e0b")
kpi(k5, "Avg Tenure", f"{avg_tenure:.1f} yrs", "Active median: 12.6 yrs", "neu", "#38bdf8")

st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔁 Attrition", "💰 Compensation", "🎯 Performance",
    "🔍 Recruitment", "🤖 Risk Scores", "🎛️ Salary Simulator"
])

# ════════════════════════════════════════════════════
# TAB 1 — ATTRITION
# ════════════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns([1, 1], gap="medium")

    with c1:
        # Attrition rate by dept
        dept_attr = fdf.groupby("Department").agg(
            total=("EmpID", "count"),
            terminated=("IsTerminated", "sum")
        ).reset_index()
        dept_attr["rate"] = dept_attr["terminated"] / dept_attr["total"] * 100
        dept_attr = dept_attr.sort_values("rate", ascending=True)

        fig = go.Figure(go.Bar(
            x=dept_attr["rate"], y=dept_attr["Department"],
            orientation="h",
            marker=dict(
                color=dept_attr["rate"],
                colorscale=[[0, "#1e293b"], [0.5, "#6366f1"], [1, "#f87171"]],
                line=dict(width=0)
            ),
            text=dept_attr["rate"].map(lambda x: f"{x:.1f}%"),
            textposition="outside",
            textfont=dict(color="#94a3b8", size=11),
        ))
        fig = chart_layout(fig, "Attrition Rate by Department", 300)
        fig.update_xaxes(title_text="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Termination reasons
        reasons = (
            fdf[fdf["IsTerminated"] == 1]["TermReason"]
            .value_counts()
            .head(8)
            .reset_index()
        )
        reasons.columns = ["reason", "count"]

        fig = go.Figure(go.Bar(
            x=reasons["count"], y=reasons["reason"],
            orientation="h",
            marker=dict(color=PALETTE[0], opacity=0.85, line=dict(width=0)),
            text=reasons["count"],
            textposition="outside",
            textfont=dict(color="#94a3b8", size=11),
        ))
        fig = chart_layout(fig, "Top Exit Reasons", 300)
        fig.update_xaxes(title_text="Employees")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns([1.4, 1], gap="medium")

    with c3:
        # Hires and terminations by year
        hire_yr = fdf.groupby("HireYear").size().reset_index(name="hires")
        fdf["TermYear"] = fdf["DateofTermination"].dt.year
        term_yr = fdf[fdf["IsTerminated"] == 1].groupby("TermYear").size().reset_index(name="terminations")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hire_yr["HireYear"], y=hire_yr["hires"],
            name="Hires", mode="lines+markers",
            line=dict(color="#34d399", width=2.5),
            marker=dict(size=7, color="#34d399"),
            fill="tozeroy", fillcolor="rgba(52,211,153,0.07)"
        ))
        fig.add_trace(go.Scatter(
            x=term_yr["TermYear"], y=term_yr["terminations"],
            name="Terminations", mode="lines+markers",
            line=dict(color="#f87171", width=2.5),
            marker=dict(size=7, color="#f87171"),
            fill="tozeroy", fillcolor="rgba(248,113,113,0.07)"
        ))
        fig = chart_layout(fig, "Hiring vs. Termination Trend (by Year)", 280)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Active vs terminated donut
        status_counts = fdf["EmploymentStatus"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        colors = {"Active": "#34d399", "Voluntarily Terminated": "#f59e0b", "Terminated for Cause": "#f87171"}
        fig = go.Figure(go.Pie(
            labels=status_counts["status"],
            values=status_counts["count"],
            hole=0.62,
            marker=dict(colors=[colors.get(s, "#6366f1") for s in status_counts["status"]]),
            textinfo="percent",
            textfont=dict(size=11, color="#f1f5f9"),
        ))
        fig.add_annotation(text=f"<b>{len(fdf)}</b><br><span style='font-size:10px'>Employees</span>",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=18, color="#f1f5f9", family="Inter"))
        fig = chart_layout(fig, "Workforce Status Breakdown", 280)
        fig.update_layout(showlegend=True, legend=dict(orientation="v", x=1, y=0.5))
        st.plotly_chart(fig, use_container_width=True)

    # Insight card
    st.markdown("""
    <div class="insight-card">
        💡 <strong>Key Finding:</strong> Production has the highest attrition rate at <strong>39.7%</strong> — 
        more than double the Sales department (16.1%). Combined, <strong>"Another position" and "more money"</strong>
        account for 30% of all exits — both are addressable through compensation benchmarking and internal mobility programs.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 2 — COMPENSATION
# ════════════════════════════════════════════════════
with tab2:
    c1, c2 = st.columns([1, 1], gap="medium")

    with c1:
        # Salary by dept box
        fig = px.box(
            fdf, x="Department", y="Salary",
            color="Department",
            color_discrete_sequence=PALETTE,
            points="outliers",
        )
        fig.update_traces(marker=dict(size=5, opacity=0.6))
        fig = chart_layout(fig, "Salary Distribution by Department", 340)
        fig.update_layout(showlegend=False)
        fig.update_xaxes(tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Gender pay gap by dept
        pay_gap = fdf[fdf["EmploymentStatus"] == "Active"].groupby(
            ["Department", "Sex"])["Salary"].mean().reset_index()
        pay_gap = pay_gap.sort_values("Salary")

        fig = px.bar(
            pay_gap, x="Salary", y="Department",
            color="Sex", barmode="group",
            color_discrete_map={"M": "#6366f1", "F": "#f472b6"},
            orientation="h",
        )
        fig = chart_layout(fig, "Avg Salary by Department & Gender (Active)", 340)
        fig.update_xaxes(title_text="Avg Salary ($)")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns([1, 1], gap="medium")

    with c3:
        # Salary histogram
        fig = px.histogram(
            fdf, x="Salary", nbins=30,
            color_discrete_sequence=[PALETTE[0]],
        )
        fig.update_traces(marker_line_width=0, opacity=0.85)
        fig = chart_layout(fig, "Salary Distribution (All Employees)", 280)
        fig.update_xaxes(title_text="Annual Salary ($)")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Absence cost by dept
        abs_cost = fdf[fdf["EmploymentStatus"] == "Active"].groupby("Department").agg(
            total_absence_cost=("AbsenceCost", "sum"),
            avg_absences=("Absences", "mean")
        ).reset_index().sort_values("total_absence_cost", ascending=False)

        fig = go.Figure(go.Bar(
            x=abs_cost["Department"],
            y=abs_cost["total_absence_cost"],
            marker=dict(color=PALETTE[2], opacity=0.85, line=dict(width=0)),
            text=abs_cost["total_absence_cost"].map(lambda x: f"${x:,.0f}"),
            textposition="outside",
            textfont=dict(color="#94a3b8", size=10),
        ))
        fig = chart_layout(fig, "Estimated Absence Cost by Department ($)", 280)
        fig.update_xaxes(tickangle=-15)
        fig.update_yaxes(title_text="Cost ($)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-card">
        💡 <strong>Key Finding:</strong> A <strong>$2,842/yr (4.2%) gender pay gap</strong> exists across the dataset
        (M avg $70,629 vs F avg $67,787). Production's payroll represents the largest cost exposure due to headcount size.
        Absence-adjusted cost should be reviewed quarterly for departments with avg absences &gt; 10 days/year.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 3 — PERFORMANCE
# ════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns([1, 1], gap="medium")

    with c1:
        # Performance distribution donut
        perf_order = ["Exceeds", "Fully Meets", "Needs Improvement", "PIP"]
        perf_colors = {"Exceeds": "#34d399", "Fully Meets": "#6366f1",
                       "Needs Improvement": "#f59e0b", "PIP": "#f87171"}
        perf_counts = fdf["PerformanceScore"].value_counts().reindex(perf_order).dropna().reset_index()
        perf_counts.columns = ["score", "count"]

        fig = go.Figure(go.Pie(
            labels=perf_counts["score"],
            values=perf_counts["count"],
            hole=0.55,
            marker=dict(colors=[perf_colors[s] for s in perf_counts["score"]]),
            textinfo="label+percent",
            textfont=dict(size=11, color="#f1f5f9"),
        ))
        fig = chart_layout(fig, "Performance Score Distribution", 320)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Performance vs Satisfaction scatter
        perf_num = {"Exceeds": 4, "Fully Meets": 3, "Needs Improvement": 2, "PIP": 1}
        scatter_df = fdf.copy()
        scatter_df["PerfNum"] = scatter_df["PerformanceScore"].map(perf_num)
        scatter_df = scatter_df.dropna(subset=["EngagementSurvey", "EmpSatisfaction"])

        fig = px.scatter(
            scatter_df,
            x="EngagementSurvey", y="EmpSatisfaction",
            color="PerformanceScore",
            color_discrete_map=perf_colors,
            size_max=10,
            opacity=0.75,
            hover_data=["Department", "Salary"],
        )
        fig = chart_layout(fig, "Engagement Score vs. Satisfaction (by Performance)", 320)
        fig.update_xaxes(title_text="Engagement Survey Score")
        fig.update_yaxes(title_text="Employee Satisfaction")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns([1, 1], gap="medium")

    with c3:
        # Avg salary by performance score
        sal_perf = fdf.groupby("PerformanceScore")["Salary"].mean().reindex(perf_order).reset_index()
        sal_perf.columns = ["score", "avg_salary"]

        fig = go.Figure(go.Bar(
            x=sal_perf["score"], y=sal_perf["avg_salary"],
            marker=dict(
                color=[perf_colors[s] for s in sal_perf["score"]],
                opacity=0.85, line=dict(width=0)
            ),
            text=sal_perf["avg_salary"].map(lambda x: f"${x:,.0f}"),
            textposition="outside",
            textfont=dict(color="#94a3b8", size=11),
        ))
        fig = chart_layout(fig, "Avg Salary by Performance Score", 280)
        fig.update_yaxes(title_text="Avg Salary ($)")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Absences by performance
        abs_perf = fdf.groupby("PerformanceScore")["Absences"].mean().reindex(perf_order).reset_index()

        fig = go.Figure(go.Bar(
            x=abs_perf["PerformanceScore"], y=abs_perf["Absences"],
            marker=dict(
                color=[perf_colors.get(s, "#6366f1") for s in abs_perf["PerformanceScore"]],
                opacity=0.85, line=dict(width=0)
            ),
            text=abs_perf["Absences"].map(lambda x: f"{x:.1f} days"),
            textposition="outside",
            textfont=dict(color="#94a3b8", size=11),
        ))
        fig = chart_layout(fig, "Avg Absences by Performance Score", 280)
        fig.update_yaxes(title_text="Avg Absence Days")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-card">
        💡 <strong>Key Finding:</strong> <strong>78.1%</strong> of employees "Fully Meet" expectations.
        The correlation between satisfaction and absences is very weak (r = 0.075) — absence behaviour
        is driven by factors other than satisfaction, meaning it requires targeted manager-level intervention,
        not a blanket engagement initiative.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 4 — RECRUITMENT
# ════════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns([1, 1], gap="medium")

    with c1:
        # Hires by source
        src_counts = fdf["RecruitmentSource"].value_counts().reset_index()
        src_counts.columns = ["source", "count"]

        fig = px.bar(
            src_counts, x="count", y="source",
            orientation="h",
            color="count",
            color_continuous_scale=[[0, "#1e293b"], [1, "#6366f1"]],
            text="count",
        )
        fig.update_traces(textposition="outside", textfont=dict(color="#94a3b8", size=11))
        fig = chart_layout(fig, "Total Hires by Recruitment Source", 340)
        fig.update_coloraxes(showscale=False)
        fig.update_xaxes(title_text="Employees Hired")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Exceeds rate by source
        exceeds_rate = fdf.groupby("RecruitmentSource").apply(
            lambda x: (x["PerformanceScore"] == "Exceeds").sum() / len(x) * 100
        ).reset_index()
        exceeds_rate.columns = ["source", "exceeds_rate"]
        exceeds_rate = exceeds_rate.sort_values("exceeds_rate", ascending=True)

        fig = go.Figure(go.Bar(
            x=exceeds_rate["exceeds_rate"],
            y=exceeds_rate["source"],
            orientation="h",
            marker=dict(
                color=exceeds_rate["exceeds_rate"],
                colorscale=[[0, "#1e293b"], [0.5, "#6366f1"], [1, "#34d399"]],
                line=dict(width=0)
            ),
            text=exceeds_rate["exceeds_rate"].map(lambda x: f"{x:.1f}%"),
            textposition="outside",
            textfont=dict(color="#94a3b8", size=11),
        ))
        fig = chart_layout(fig, "\"Exceeds\" Performance Rate by Source", 340)
        fig.update_xaxes(title_text="% of Hires Exceeding Expectations")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns([1, 1], gap="medium")

    with c3:
        # Diversity hire breakdown
        div_perf = fdf.copy()
        div_perf["DiversityLabel"] = div_perf["FromDiversityJobFairID"].map(
            {0: "Standard Hire", 1: "Diversity Hire"}
        )
        div_grouped = div_perf.groupby(["DiversityLabel", "PerformanceScore"]).size().reset_index(name="count")

        fig = px.bar(
            div_grouped, x="PerformanceScore", y="count",
            color="DiversityLabel",
            barmode="group",
            color_discrete_map={"Standard Hire": "#6366f1", "Diversity Hire": "#34d399"},
            category_orders={"PerformanceScore": perf_order}
        )
        fig = chart_layout(fig, "Performance Score: Diversity vs. Standard Hires", 280)
        fig.update_yaxes(title_text="Employee Count")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Avg tenure by source
        tenure_src = fdf.groupby("RecruitmentSource")["TenureYears"].mean().reset_index()
        tenure_src = tenure_src.sort_values("TenureYears", ascending=False)

        fig = go.Figure(go.Bar(
            x=tenure_src["RecruitmentSource"],
            y=tenure_src["TenureYears"],
            marker=dict(color=PALETTE[4], opacity=0.85, line=dict(width=0)),
            text=tenure_src["TenureYears"].map(lambda x: f"{x:.1f}y"),
            textposition="outside",
            textfont=dict(color="#94a3b8", size=10),
        ))
        fig = chart_layout(fig, "Avg Employee Tenure by Recruitment Source", 280)
        fig.update_xaxes(tickangle=-20)
        fig.update_yaxes(title_text="Avg Tenure (Years)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-card">
        💡 <strong>Key Finding:</strong> <strong>Diversity Job Fair</strong> has the highest "Exceeds" performance rate at
        <strong>20.7%</strong> — the best yield per hire of any channel. <strong>Google Search</strong>, despite being 
        the 3rd-largest source by volume, has the lowest Exceeds rate at 4.1%, suggesting a targeting or 
        screening problem worth investigating before the next hiring cycle.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 5 — RISK SCORES (ML)
# ════════════════════════════════════════════════════
with tab5:
    # Score all employees
    all_scores = get_risk_scores(df)
    df_scored = df.copy()
    df_scored["RiskScore"] = all_scores
    df_scored["RiskLabel"] = pd.cut(
        df_scored["RiskScore"],
        bins=[0, 30, 60, 100],
        labels=["🟢 Low", "🟡 Medium", "🔴 High"]
    )

    active_scored = df_scored[df_scored["EmploymentStatus"] == "Active"].copy()

    # ── Model metrics banner ─────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    avg_risk = active_scored["RiskScore"].mean()
    high_risk_n = (active_scored["RiskScore"] >= 60).sum()
    high_risk_pct = high_risk_n / len(active_scored) * 100

    m1.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background:#6366f1"></div>
        <div class="kpi-label">Model Type</div>
        <div class="kpi-value" style="font-size:1.1rem">Gradient Boosting</div>
        <div class="kpi-delta-neu">GBM · 200 estimators</div>
    </div>""", unsafe_allow_html=True)
    m2.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background:#34d399"></div>
        <div class="kpi-label">Cross-Val ROC-AUC</div>
        <div class="kpi-value">{cv_auc:.3f}</div>
        <div class="kpi-delta-up">5-fold · Strong discrimination</div>
    </div>""", unsafe_allow_html=True)
    m3.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background:#f87171"></div>
        <div class="kpi-label">High-Risk Employees</div>
        <div class="kpi-value">{high_risk_n}</div>
        <div class="kpi-delta-down">{high_risk_pct:.1f}% of active workforce</div>
    </div>""", unsafe_allow_html=True)
    m4.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background:#f59e0b"></div>
        <div class="kpi-label">Avg Risk Score (Active)</div>
        <div class="kpi-value">{avg_risk:.1f}%</div>
        <div class="kpi-delta-neu">0 = No risk · 100 = Certain exit</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.1, 1], gap="medium")

    with c1:
        # Feature importance
        feat_names = [
            "Salary", "Tenure (Years)", "Engagement Score", "Satisfaction Score",
            "Absences", "Days Late (30d)", "Special Projects",
            "Department", "Gender", "Performance", "Marital Status",
            "Recruitment Source", "Diversity Hire"
        ]
        importances = model.feature_importances_
        fi_df = pd.DataFrame({"Feature": feat_names, "Importance": importances})
        fi_df = fi_df.sort_values("Importance", ascending=True)

        fig = go.Figure(go.Bar(
            x=fi_df["Importance"],
            y=fi_df["Feature"],
            orientation="h",
            marker=dict(
                color=fi_df["Importance"],
                colorscale=[[0, "#1e293b"], [0.5, "#6366f1"], [1, "#34d399"]],
                line=dict(width=0)
            ),
            text=fi_df["Importance"].map(lambda x: f"{x:.3f}"),
            textposition="outside",
            textfont=dict(color="#94a3b8", size=10),
        ))
        fig = chart_layout(fig, "Feature Importance — What Drives Attrition Risk", 380)
        fig.update_xaxes(title_text="Importance Score")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Risk distribution by department
        dept_risk = active_scored.groupby("Department")["RiskScore"].mean().reset_index()
        dept_risk = dept_risk.sort_values("RiskScore", ascending=False)

        fig = go.Figure(go.Bar(
            x=dept_risk["Department"],
            y=dept_risk["RiskScore"],
            marker=dict(
                color=dept_risk["RiskScore"],
                colorscale=[[0, "#34d399"], [0.5, "#f59e0b"], [1, "#f87171"]],
                line=dict(width=0)
            ),
            text=dept_risk["RiskScore"].map(lambda x: f"{x:.1f}%"),
            textposition="outside",
            textfont=dict(color="#94a3b8", size=11),
        ))
        fig = chart_layout(fig, "Avg Attrition Risk Score by Department (Active Only)", 280)
        fig.update_xaxes(tickangle=-15)
        fig.update_yaxes(title_text="Risk Score (%)")
        st.plotly_chart(fig, use_container_width=True)

        # Risk tier breakdown donut
        tier_counts = active_scored["RiskLabel"].value_counts().reset_index()
        tier_counts.columns = ["tier", "count"]
        tier_colors = {"🟢 Low": "#34d399", "🟡 Medium": "#f59e0b", "🔴 High": "#f87171"}
        fig = go.Figure(go.Pie(
            labels=tier_counts["tier"],
            values=tier_counts["count"],
            hole=0.58,
            marker=dict(colors=[tier_colors.get(t, "#6366f1") for t in tier_counts["tier"]]),
            textinfo="label+percent",
            textfont=dict(size=10, color="#f1f5f9"),
        ))
        fig.add_annotation(text=f"<b>{len(active_scored)}</b><br><span style='font-size:10px'>Active</span>",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=16, color="#f1f5f9", family="Inter"))
        fig = chart_layout(fig, "Risk Tier Distribution (Active Employees)", 240)
        st.plotly_chart(fig, use_container_width=True)

    # ── High-risk employee table ──────────────────────
    st.markdown('<div class="section-header">🔴 Top 20 At-Risk Active Employees</div>', unsafe_allow_html=True)
    top_risk = (
        active_scored
        .sort_values("RiskScore", ascending=False)
        .head(20)[["Employee_Name", "Department", "Position", "Salary",
                   "PerformanceScore", "Absences", "TenureYears", "RiskScore", "RiskLabel"]]
        .reset_index(drop=True)
    )
    top_risk["TenureYears"] = top_risk["TenureYears"].round(1)
    top_risk["Salary"] = top_risk["Salary"].map(lambda x: f"${x:,.0f}")
    top_risk["RiskScore"] = top_risk["RiskScore"].map(lambda x: f"{x:.1f}%")

    # Risk score bar column as HTML
    def risk_bar(row):
        pct = float(row["RiskScore"].replace("%", ""))
        color = "#f87171" if pct >= 60 else "#f59e0b" if pct >= 30 else "#34d399"
        return f'<div style="background:#1e293b;border-radius:4px;height:8px;width:100%"><div style="background:{color};width:{pct}%;height:8px;border-radius:4px"></div></div>{row["RiskScore"]}'

    top_risk.index = top_risk.index + 1
    st.dataframe(
        top_risk.rename(columns={
            "Employee_Name": "Name", "RiskLabel": "Risk Tier",
            "TenureYears": "Tenure (Yrs)", "PerformanceScore": "Performance"
        }),
        use_container_width=True,
        height=460,
    )

    st.markdown("""
    <div class="insight-card">
        🤖 <strong>Model:</strong> Gradient Boosting Classifier trained on 311 employee records.
        <strong>Top predictors of attrition:</strong> Tenure, Engagement Score, Salary, and Absences.
        Risk Score = probability (0–100%) that an employee will leave based on their current profile.
        Use this table to prioritise retention conversations before the next pay cycle.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 6 — SALARY SIMULATOR
# ════════════════════════════════════════════════════
with tab6:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e293b,#162032);border:1px solid #334155;
    border-left:3px solid #6366f1;border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1rem">
        <div style="font-size:1rem;font-weight:600;color:#e2e8f0;margin-bottom:0.4rem">🎛️ What-If Salary Simulator</div>
        <div style="font-size:0.85rem;color:#64748b">
        Adjust salary for one or more departments and see how the model re-scores attrition risk in real time.
        Use this to estimate the retention ROI of a pay increase before presenting to Finance or HR Operations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    all_depts_sim = sorted(df["Department"].unique())

    sim_col1, sim_col2 = st.columns([1, 2], gap="large")

    with sim_col1:
        st.markdown('<div style="font-size:0.8rem;color:#94a3b8;font-weight:600;margin-bottom:0.5rem">SIMULATION CONTROLS</div>', unsafe_allow_html=True)

        sim_dept = st.selectbox("Target Department", ["All Departments"] + all_depts_sim, key="sim_dept")

        salary_pct = st.slider(
            "Salary Increase (%)", min_value=0, max_value=40, value=10, step=1, key="sal_pct"
        )

        # Compute baseline and simulated scores for active employees
        active_df = df[df["EmploymentStatus"] == "Active"].copy()

        baseline_scores = get_risk_scores(active_df)
        active_df["BaselineRisk"] = baseline_scores

        # Apply salary increase to selected department only
        sim_salary = active_df["Salary"].copy()
        if sim_dept == "All Departments":
            sim_salary = sim_salary * (1 + salary_pct / 100)
        else:
            mask = active_df["Department"] == sim_dept
            sim_salary[mask] = sim_salary[mask] * (1 + salary_pct / 100)

        sim_scores = get_risk_scores(active_df, salary_override=sim_salary)
        active_df["SimulatedRisk"] = sim_scores
        active_df["RiskDelta"] = active_df["SimulatedRisk"] - active_df["BaselineRisk"]

        # Summary stats
        target_df = active_df if sim_dept == "All Departments" else active_df[active_df["Department"] == sim_dept]
        baseline_avg = target_df["BaselineRisk"].mean()
        sim_avg = target_df["SimulatedRisk"].mean()
        risk_reduction = baseline_avg - sim_avg

        baseline_high = (target_df["BaselineRisk"] >= 60).sum()
        sim_high = (target_df["SimulatedRisk"] >= 60).sum()
        avoided_exits = baseline_high - sim_high

        # Cost of salary increase
        if sim_dept == "All Departments":
            payroll_impact = active_df["Salary"].sum() * (salary_pct / 100)
        else:
            payroll_impact = active_df[active_df["Department"] == sim_dept]["Salary"].sum() * (salary_pct / 100)

        # Avg replacement cost estimate ($15k per employee as conservative proxy)
        replacement_savings = avoided_exits * 15000

        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

        def sim_kpi(label, val, sub, color):
            st.markdown(f"""
            <div class="kpi-card" style="margin-bottom:0.6rem">
                <div class="kpi-accent" style="background:{color}"></div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="font-size:1.4rem">{val}</div>
                <div class="kpi-delta-neu">{sub}</div>
            </div>""", unsafe_allow_html=True)

        sim_kpi("Risk Reduction", f"{risk_reduction:.1f}pp", f"{baseline_avg:.1f}% → {sim_avg:.1f}% avg risk", "#34d399")
        sim_kpi("High-Risk Employees", f"{baseline_high} → {sim_high}", f"{avoided_exits} employees de-risked", "#6366f1")
        sim_kpi("Annual Payroll Cost", f"+${payroll_impact:,.0f}", f"+{salary_pct}% salary increase", "#f59e0b")
        sim_kpi("Est. Replacement Savings", f"${replacement_savings:,.0f}", f"@ $15K avg replacement cost", "#34d399")

    with sim_col2:
        # Before vs after risk distribution
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=active_df["BaselineRisk"], name="Baseline Risk",
            marker_color="#f87171", opacity=0.65, nbinsx=25,
            xbins=dict(start=0, end=100, size=4),
        ))
        fig.add_trace(go.Histogram(
            x=active_df["SimulatedRisk"], name=f"After +{salary_pct}% Salary",
            marker_color="#34d399", opacity=0.65, nbinsx=25,
            xbins=dict(start=0, end=100, size=4),
        ))
        fig.update_layout(barmode="overlay")
        fig = chart_layout(fig, "Risk Score Distribution: Baseline vs. Simulated", 280)
        fig.update_xaxes(title_text="Attrition Risk Score (%)")
        fig.update_yaxes(title_text="Employee Count")
        st.plotly_chart(fig, use_container_width=True)

        # Department-level before / after
        dept_sim = active_df.groupby("Department").agg(
            baseline=("BaselineRisk", "mean"),
            simulated=("SimulatedRisk", "mean")
        ).reset_index().sort_values("baseline", ascending=False)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Baseline Risk",
            x=dept_sim["Department"],
            y=dept_sim["baseline"],
            marker_color="#f87171",
            opacity=0.75,
        ))
        fig.add_trace(go.Bar(
            name=f"Simulated (+{salary_pct}%)",
            x=dept_sim["Department"],
            y=dept_sim["simulated"],
            marker_color="#34d399",
            opacity=0.75,
        ))
        fig.update_layout(barmode="group")
        fig = chart_layout(fig, "Avg Risk Score by Department: Before vs. After", 260)
        fig.update_yaxes(title_text="Avg Risk Score (%)")
        fig.update_xaxes(tickangle=-15)
        st.plotly_chart(fig, use_container_width=True)

        # Individual delta table — who improved most
        st.markdown('<div class="section-header">👥 Employees with Largest Risk Reduction</div>', unsafe_allow_html=True)
        top_improved = (
            target_df.sort_values("RiskDelta")
            .head(10)[["Employee_Name", "Department", "Position", "Salary",
                       "BaselineRisk", "SimulatedRisk", "RiskDelta"]]
            .copy()
        )
        top_improved["Salary"] = top_improved["Salary"].map(lambda x: f"${x:,.0f}")
        top_improved["BaselineRisk"] = top_improved["BaselineRisk"].map(lambda x: f"{x:.1f}%")
        top_improved["SimulatedRisk"] = top_improved["SimulatedRisk"].map(lambda x: f"{x:.1f}%")
        top_improved["RiskDelta"] = top_improved["RiskDelta"].map(lambda x: f"{x:+.1f}pp")
        top_improved = top_improved.rename(columns={
            "Employee_Name": "Name", "BaselineRisk": "Risk Before",
            "SimulatedRisk": "Risk After", "RiskDelta": "Δ Risk"
        })
        top_improved.index = range(1, len(top_improved) + 1)
        st.dataframe(top_improved, use_container_width=True, height=340)

    st.markdown(f"""
    <div class="insight-card">
        🎛️ <strong>Simulator Result:</strong> A <strong>+{salary_pct}%</strong> salary increase 
        {'across all departments' if sim_dept == 'All Departments' else f'in {sim_dept}'} 
        reduces average attrition risk from <strong>{baseline_avg:.1f}%</strong> to 
        <strong>{sim_avg:.1f}%</strong> ({risk_reduction:.1f} percentage points), 
        de-risking <strong>{avoided_exits}</strong> high-risk employees. 
        Additional annual payroll cost: <strong>${payroll_impact:,.0f}</strong>.
        Estimated replacement cost avoided: <strong>${replacement_savings:,.0f}</strong>
        (@ $15K avg rehire cost). Net financial case for the salary adjustment: 
        <strong>${(replacement_savings - payroll_impact):+,.0f}</strong>.
    </div>
    """, unsafe_allow_html=True)
