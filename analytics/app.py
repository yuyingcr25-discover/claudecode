"""
Renewable Energy Analytics Dashboard

A Streamlit-based analytics dashboard for renewable energy project
financial model evaluation and analysis.
"""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Configuration
DB_PATH = Path(__file__).parent / "renewable_energy.db"

st.set_page_config(
    page_title="Renewable Energy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data(ttl=300)
def load_projects():
    """Load all projects from database."""
    conn = get_connection()
    query = """
        SELECT p.*, fa.capex_per_mw, fa.capacity_factor, fa.electricity_price_mwh,
               fa.discount_rate, fa.debt_ratio,
               km.total_capex, km.npv, km.irr, km.payback_period_years, km.lcoe,
               km.dscr_min, km.dscr_avg, km.equity_irr, km.total_generation_gwh,
               km.carbon_offset_tonnes
        FROM projects p
        LEFT JOIN financial_assumptions fa ON p.id = fa.project_id
        LEFT JOIN key_metrics km ON p.id = km.project_id
    """
    return pd.read_sql_query(query, conn)


@st.cache_data(ttl=300)
def load_cash_flows(project_id=None):
    """Load cash flows for projects."""
    conn = get_connection()
    if project_id:
        query = "SELECT * FROM annual_cash_flows WHERE project_id = ?"
        return pd.read_sql_query(query, conn, params=(project_id,))
    return pd.read_sql_query("SELECT * FROM annual_cash_flows", conn)


@st.cache_data(ttl=300)
def load_monthly_generation(project_id=None):
    """Load monthly generation data."""
    conn = get_connection()
    if project_id:
        query = "SELECT * FROM monthly_generation WHERE project_id = ?"
        return pd.read_sql_query(query, conn, params=(project_id,))
    return pd.read_sql_query("SELECT * FROM monthly_generation", conn)


@st.cache_data(ttl=300)
def load_market_data():
    """Load market price data."""
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM market_data", conn)


@st.cache_data(ttl=300)
def load_technology_benchmarks():
    """Load technology benchmark data."""
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM technology_benchmarks", conn)


def format_currency(value, prefix="$", suffix=""):
    """Format number as currency."""
    if pd.isna(value):
        return "N/A"
    if abs(value) >= 1e9:
        return f"{prefix}{value/1e9:.1f}B{suffix}"
    if abs(value) >= 1e6:
        return f"{prefix}{value/1e6:.1f}M{suffix}"
    if abs(value) >= 1e3:
        return f"{prefix}{value/1e3:.1f}K{suffix}"
    return f"{prefix}{value:.0f}{suffix}"


def main():
    """Main application."""
    # Sidebar
    st.sidebar.title("⚡ RE Analytics")
    st.sidebar.markdown("---")

    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Portfolio Overview", "Project Details", "Financial Analysis",
         "Generation Analytics", "Market Analysis", "Technology Trends"]
    )

    # Load data
    try:
        projects = load_projects()
    except Exception as e:
        st.error(f"Database not found. Please run init_database.py first.\n\nError: {e}")
        st.code("python analytics/init_database.py", language="bash")
        return

    if page == "Portfolio Overview":
        show_portfolio_overview(projects)
    elif page == "Project Details":
        show_project_details(projects)
    elif page == "Financial Analysis":
        show_financial_analysis(projects)
    elif page == "Generation Analytics":
        show_generation_analytics(projects)
    elif page == "Market Analysis":
        show_market_analysis()
    elif page == "Technology Trends":
        show_technology_trends()


def show_portfolio_overview(projects):
    """Display portfolio overview dashboard."""
    st.title("📊 Portfolio Overview")
    st.markdown("---")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    total_capacity = projects["capacity_mw"].sum()
    total_capex = projects["total_capex"].sum()
    avg_irr = projects["irr"].mean() * 100
    total_carbon = projects["carbon_offset_tonnes"].sum()

    with col1:
        st.metric("Total Capacity", f"{total_capacity:,.0f} MW")
    with col2:
        st.metric("Total CAPEX", format_currency(total_capex))
    with col3:
        st.metric("Average IRR", f"{avg_irr:.1f}%")
    with col4:
        st.metric("Carbon Offset", f"{total_carbon/1000:,.0f}K tonnes")

    st.markdown("---")

    # Charts row 1
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Capacity by Technology")
        capacity_by_type = projects.groupby("project_type")["capacity_mw"].sum().reset_index()
        fig = px.pie(
            capacity_by_type,
            values="capacity_mw",
            names="project_type",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Projects by Status")
        status_counts = projects["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        fig = px.bar(
            status_counts,
            x="status",
            y="count",
            color="status",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Charts row 2
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("IRR vs NPV by Project")
        fig = px.scatter(
            projects,
            x="npv",
            y=projects["irr"] * 100,
            size="capacity_mw",
            color="project_type",
            hover_name="name",
            labels={"npv": "NPV ($)", "y": "IRR (%)"},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig.add_hline(y=8, line_dash="dash", line_color="gray", annotation_text="8% Hurdle Rate")
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("LCOE by Technology")
        fig = px.box(
            projects,
            x="project_type",
            y="lcoe",
            color="project_type",
            labels={"lcoe": "LCOE ($/MWh)", "project_type": "Technology"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Projects table
    st.subheader("All Projects")
    display_cols = ["name", "project_type", "location", "country", "capacity_mw",
                    "status", "irr", "npv", "lcoe", "payback_period_years"]
    display_df = projects[display_cols].copy()
    display_df["irr"] = (display_df["irr"] * 100).round(1).astype(str) + "%"
    display_df["npv"] = display_df["npv"].apply(lambda x: format_currency(x))
    display_df.columns = ["Project", "Type", "Location", "Country", "Capacity (MW)",
                          "Status", "IRR", "NPV", "LCOE", "Payback (yrs)"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def show_project_details(projects):
    """Display individual project details."""
    st.title("🔍 Project Details")
    st.markdown("---")

    # Project selector
    project_name = st.selectbox(
        "Select Project",
        projects["name"].tolist(),
        index=0
    )

    project = projects[projects["name"] == project_name].iloc[0]
    project_id = project["id"]

    # Project info cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Project Info")
        st.markdown(f"""
        - **Type:** {project['project_type']}
        - **Location:** {project['location']}, {project['country']}
        - **Capacity:** {project['capacity_mw']:.1f} MW
        - **Status:** {project['status']}
        - **Project Life:** {project['project_life_years']} years
        """)

    with col2:
        st.markdown("### Financial Assumptions")
        st.markdown(f"""
        - **CAPEX/MW:** {format_currency(project['capex_per_mw'])}
        - **Capacity Factor:** {project['capacity_factor']*100:.1f}%
        - **PPA Price:** ${project['electricity_price_mwh']:.2f}/MWh
        - **Discount Rate:** {project['discount_rate']*100:.1f}%
        - **Debt Ratio:** {project['debt_ratio']*100:.0f}%
        """)

    with col3:
        st.markdown("### Key Metrics")
        st.markdown(f"""
        - **Total CAPEX:** {format_currency(project['total_capex'])}
        - **NPV:** {format_currency(project['npv'])}
        - **IRR:** {project['irr']*100:.1f}%
        - **LCOE:** ${project['lcoe']:.2f}/MWh
        - **Payback:** {project['payback_period_years']:.1f} years
        """)

    st.markdown("---")

    # Cash flow analysis
    st.subheader("Cash Flow Analysis")
    cash_flows = load_cash_flows(project_id)

    if not cash_flows.empty:
        col1, col2 = st.columns(2)

        with col1:
            # Revenue and EBITDA chart
            fig = go.Figure()
            fig.add_trace(go.Bar(x=cash_flows["year"], y=cash_flows["revenue"],
                                  name="Revenue", marker_color="#2E86AB"))
            fig.add_trace(go.Bar(x=cash_flows["year"], y=cash_flows["ebitda"],
                                  name="EBITDA", marker_color="#A23B72"))
            fig.update_layout(
                title="Revenue & EBITDA",
                xaxis_title="Year",
                yaxis_title="Amount ($)",
                barmode="group",
                margin=dict(t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Cumulative cash flow
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=cash_flows["year"],
                y=cash_flows["cumulative_cash_flow"],
                mode="lines+markers",
                name="Cumulative Cash Flow",
                line=dict(color="#28A745", width=3),
                fill="tozeroy"
            ))
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            fig.update_layout(
                title="Cumulative Cash Flow",
                xaxis_title="Year",
                yaxis_title="Cumulative Cash Flow ($)",
                margin=dict(t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Cash flow waterfall
        st.subheader("Annual Cash Flow Breakdown")
        year_select = st.slider("Select Year", 1, len(cash_flows), 5)
        year_data = cash_flows[cash_flows["year"] == year_select].iloc[0]

        fig = go.Figure(go.Waterfall(
            name="Cash Flow",
            orientation="v",
            measure=["relative", "relative", "total", "relative", "relative", "relative", "relative", "total"],
            x=["Revenue", "OPEX", "EBITDA", "Depreciation", "Interest", "Tax", "Principal", "FCF"],
            y=[year_data["revenue"], -year_data["opex"], year_data["ebitda"],
               -year_data["depreciation"], -year_data["interest_expense"],
               -year_data["tax"], -year_data["principal_repayment"], year_data["free_cash_flow"]],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#28A745"}},
            decreasing={"marker": {"color": "#DC3545"}},
            totals={"marker": {"color": "#007BFF"}}
        ))
        fig.update_layout(
            title=f"Year {year_select} Cash Flow Waterfall",
            showlegend=False,
            margin=dict(t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)


def show_financial_analysis(projects):
    """Display financial analysis across projects."""
    st.title("💰 Financial Analysis")
    st.markdown("---")

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        selected_types = st.multiselect(
            "Filter by Technology",
            projects["project_type"].unique().tolist(),
            default=projects["project_type"].unique().tolist()
        )
    with col2:
        selected_status = st.multiselect(
            "Filter by Status",
            projects["status"].unique().tolist(),
            default=projects["status"].unique().tolist()
        )

    filtered = projects[
        (projects["project_type"].isin(selected_types)) &
        (projects["status"].isin(selected_status))
    ]

    # Summary metrics
    st.subheader("Portfolio Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Projects", len(filtered))
    with col2:
        st.metric("Total NPV", format_currency(filtered["npv"].sum()))
    with col3:
        weighted_irr = (filtered["irr"] * filtered["total_capex"]).sum() / filtered["total_capex"].sum()
        st.metric("Weighted Avg IRR", f"{weighted_irr*100:.1f}%")
    with col4:
        weighted_lcoe = (filtered["lcoe"] * filtered["capacity_mw"]).sum() / filtered["capacity_mw"].sum()
        st.metric("Weighted Avg LCOE", f"${weighted_lcoe:.2f}/MWh")

    st.markdown("---")

    # Comparison charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("IRR Distribution")
        fig = px.histogram(
            filtered,
            x=filtered["irr"] * 100,
            nbins=15,
            color="project_type",
            labels={"x": "IRR (%)"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.add_vline(x=8, line_dash="dash", line_color="red", annotation_text="Hurdle Rate")
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Payback Period Analysis")
        fig = px.histogram(
            filtered,
            x="payback_period_years",
            nbins=15,
            color="project_type",
            labels={"payback_period_years": "Payback Period (years)"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # DSCR analysis
    st.subheader("Debt Service Coverage Ratio (DSCR)")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.scatter(
            filtered,
            x="dscr_min",
            y="dscr_avg",
            color="project_type",
            size="total_capex",
            hover_name="name",
            labels={"dscr_min": "Minimum DSCR", "dscr_avg": "Average DSCR"},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig.add_hline(y=1.3, line_dash="dash", line_color="orange", annotation_text="Min Covenant (1.3x)")
        fig.add_vline(x=1.2, line_dash="dash", line_color="red", annotation_text="Min Threshold")
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # CAPEX efficiency
        fig = px.scatter(
            filtered,
            x="total_capex",
            y="total_generation_gwh",
            color="project_type",
            size="capacity_mw",
            hover_name="name",
            labels={"total_capex": "Total CAPEX ($)", "total_generation_gwh": "Lifetime Generation (GWh)"},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)


def show_generation_analytics(projects):
    """Display generation analytics."""
    st.title("⚡ Generation Analytics")
    st.markdown("---")

    # Project selector
    project_name = st.selectbox(
        "Select Project",
        projects["name"].tolist(),
        key="gen_project"
    )

    project = projects[projects["name"] == project_name].iloc[0]
    project_id = project["id"]

    monthly_data = load_monthly_generation(project_id)

    if monthly_data.empty:
        st.warning("No generation data available for this project.")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_gen = monthly_data["generation_mwh"].sum()
    avg_cf = monthly_data["capacity_factor"].mean()
    avg_availability = monthly_data["availability"].mean()
    total_curtailment = monthly_data["curtailment_mwh"].sum()

    with col1:
        st.metric("Total Generation", f"{total_gen/1000:,.0f} GWh")
    with col2:
        st.metric("Avg Capacity Factor", f"{avg_cf*100:.1f}%")
    with col3:
        st.metric("Avg Availability", f"{avg_availability*100:.1f}%")
    with col4:
        st.metric("Total Curtailment", f"{total_curtailment:,.0f} MWh")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Generation Trend")
        monthly_data["date"] = pd.to_datetime(
            monthly_data["year"].astype(str) + "-" + monthly_data["month"].astype(str) + "-01"
        )
        fig = px.line(
            monthly_data,
            x="date",
            y="generation_mwh",
            labels={"date": "Date", "generation_mwh": "Generation (MWh)"},
            color_discrete_sequence=["#2E86AB"]
        )
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Capacity Factor by Month")
        monthly_avg = monthly_data.groupby("month")["capacity_factor"].mean().reset_index()
        monthly_avg["month_name"] = monthly_avg["month"].apply(
            lambda x: ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][x-1]
        )
        fig = px.bar(
            monthly_avg,
            x="month_name",
            y=monthly_avg["capacity_factor"] * 100,
            labels={"month_name": "Month", "y": "Capacity Factor (%)"},
            color_discrete_sequence=["#28A745"]
        )
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    st.subheader("Generation Heatmap (Monthly x Yearly)")
    pivot_data = monthly_data.pivot_table(
        values="generation_mwh",
        index="year",
        columns="month",
        aggfunc="sum"
    )
    pivot_data.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = px.imshow(
        pivot_data,
        labels=dict(x="Month", y="Year", color="Generation (MWh)"),
        color_continuous_scale="Greens",
        aspect="auto"
    )
    fig.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)


def show_market_analysis():
    """Display market analysis."""
    st.title("📈 Market Analysis")
    st.markdown("---")

    market_data = load_market_data()

    if market_data.empty:
        st.warning("No market data available.")
        return

    market_data["date"] = pd.to_datetime(market_data["date"])

    # Region selector
    regions = market_data["region"].unique().tolist()
    selected_regions = st.multiselect("Select Regions", regions, default=regions[:3])

    filtered = market_data[market_data["region"].isin(selected_regions)]

    # Price trends
    st.subheader("Wholesale Price Trends")
    fig = px.line(
        filtered,
        x="date",
        y="wholesale_price_mwh",
        color="region",
        labels={"date": "Date", "wholesale_price_mwh": "Price ($/MWh)", "region": "Region"},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("PPA vs Wholesale Price")
        fig = px.scatter(
            filtered.sample(min(1000, len(filtered))),
            x="wholesale_price_mwh",
            y="ppa_price_mwh",
            color="region",
            labels={"wholesale_price_mwh": "Wholesale Price ($/MWh)",
                    "ppa_price_mwh": "PPA Price ($/MWh)"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.add_trace(go.Scatter(x=[0, 150], y=[0, 150], mode="lines",
                                  name="Parity", line=dict(dash="dash", color="gray")))
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Carbon Price Trends")
        carbon_trend = filtered.groupby([pd.Grouper(key="date", freq="M"), "region"])["carbon_price"].mean().reset_index()
        fig = px.line(
            carbon_trend,
            x="date",
            y="carbon_price",
            color="region",
            labels={"date": "Date", "carbon_price": "Carbon Price ($/tonne)"},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Price statistics
    st.subheader("Price Statistics by Region")
    stats = filtered.groupby("region").agg({
        "wholesale_price_mwh": ["mean", "min", "max", "std"],
        "ppa_price_mwh": ["mean"],
        "carbon_price": ["mean"]
    }).round(2)
    stats.columns = ["Avg Wholesale", "Min Wholesale", "Max Wholesale", "Std Dev", "Avg PPA", "Avg Carbon"]
    st.dataframe(stats, use_container_width=True)


def show_technology_trends():
    """Display technology trend analysis."""
    st.title("🔬 Technology Trends")
    st.markdown("---")

    benchmarks = load_technology_benchmarks()

    if benchmarks.empty:
        st.warning("No benchmark data available.")
        return

    # LCOE trends
    st.subheader("LCOE Trends by Technology")
    fig = px.line(
        benchmarks,
        x="year",
        y="avg_lcoe",
        color="technology",
        markers=True,
        labels={"year": "Year", "avg_lcoe": "LCOE ($/MWh)", "technology": "Technology"},
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("CAPEX Trends")
        fig = px.line(
            benchmarks,
            x="year",
            y="avg_capex_per_mw",
            color="technology",
            markers=True,
            labels={"year": "Year", "avg_capex_per_mw": "CAPEX ($/MW)", "technology": "Technology"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Capacity Factor Improvement")
        fig = px.line(
            benchmarks,
            x="year",
            y=benchmarks["avg_capacity_factor"] * 100,
            color="technology",
            markers=True,
            labels={"year": "Year", "y": "Capacity Factor (%)", "technology": "Technology"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Learning rates
    st.subheader("Technology Learning Rates")
    learning_rates = benchmarks.groupby("technology")["learning_rate"].first().reset_index()
    learning_rates["learning_rate"] = learning_rates["learning_rate"] * 100

    fig = px.bar(
        learning_rates,
        x="technology",
        y="learning_rate",
        color="technology",
        labels={"technology": "Technology", "learning_rate": "Learning Rate (%)"},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(showlegend=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Learning Rate** represents the percentage cost reduction for each doubling of cumulative installed capacity.
    Higher learning rates indicate faster cost reductions as the technology matures.
    """)


if __name__ == "__main__":
    main()
