# app/streamlit_app.py

import sys
import os
import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import project modules
from src.model import CreditRiskModel
from src.scenario import ClimateScenarioEngine

def main():
    # Configuration
    st.set_page_config(
        page_title="EU Corporate Risk Dashboard",
        page_icon="📈",
        layout="wide"
    )

    # ---- Data Loading ----
    @st.cache_data
    def load_data():
        try:
            data_path = PROJECT_ROOT / "data" / "final_dataset.csv"
            return pd.read_csv(data_path)
        except FileNotFoundError:
            st.error("Critical Error: Dataset not found!")
            st.stop()

    df = load_data()

    # Initialize models
    risk_model = CreditRiskModel()
    scenario_engine = ClimateScenarioEngine()

    # ---- Sidebar Controls ----
    with st.sidebar:
        st.header("Scenario Parameters")
        scenario = st.selectbox(
            "Climate Transition Scenario",
            list(scenario_engine.SCENARIO_MULTIPLIERS.keys()),
            index=0
        )
        # Removed the old carbon tax slider
        # Added a new 'carbon_sensitivity' slider
        carbon_sensitivity = st.slider(
            "Carbon Sensitivity (%)",
            50,    # minimum
            300,   # maximum
            100,   # default
            step=10,
            help="Multiply existing carbon intensity by this percentage"
        )
        st.divider()
        st.markdown("**Developed by:** Syed Zee Waqar Hussain")
        st.markdown("**Data Source:** ECB Climate Risk Database")

    # ---- Apply Scenario & Recompute PDs ----
    # 1) Make a copy so we don't overwrite the original DataFrame
    scenario_df = df.copy()

    # 2) Apply the chosen scenario (adjust CarbonIntensity by scenario multiplier + user slider)
    scenario_df = scenario_engine.apply_scenario(
    scenario_df,
    scenario_name=scenario,
    carbon_sensitivity=carbon_sensitivity
)


    # 3) Predict PD after scenario adjustments
    scenario_df["PD Baseline"] = risk_model.predict_pd(scenario_df, include_esg=False)
    scenario_df["PD ESG Adjusted"] = risk_model.predict_pd(scenario_df, include_esg=True)

    # 4) Calculate capital with scenario-updated PD
    scenario_df["Capital Requirement"] = risk_model.calculate_capital(scenario_df)

    # ---- Main Interface ----
    st.title("EU Corporate Credit Risk Analysis Dashboard")

    # Key Metrics
    cols = st.columns(4)
    metrics = {
        "Avg Baseline PD": scenario_df["PD Baseline"].mean(),
        "Avg ESG Adj PD": scenario_df["PD ESG Adjusted"].mean(),
        "High Risk Firms": (scenario_df["PD ESG Adjusted"] > 0.25).sum(),
        "Total Capital Impact": scenario_df["Capital Requirement"].sum()
    }

    with cols[0]:
        st.metric(
            "Baseline Risk",
            f"{metrics['Avg Baseline PD']:.2%}",
            help="Average default probability without ESG factors"
        )
    with cols[1]:
        delta = metrics["Avg ESG Adj PD"] - metrics["Avg Baseline PD"]
        st.metric(
            "ESG Adjusted Risk",
            f"{metrics['Avg ESG Adj PD']:.2%}",
            f"{delta:+.2%}",
            delta_color="inverse"
        )
    with cols[2]:
        st.metric(
            "High Risk Firms",
            metrics["High Risk Firms"],
            help="Firms with PD > 25%"
        )
    with cols[3]:
        st.metric(
            "Capital Impact",
            f"€{metrics['Total Capital Impact']/1e6:.1f}M",
            help="Total Basel III capital requirements"
        )

    # ---- Visualizations ----
    tab1, tab2, tab3 = st.tabs(["Risk Distribution", "ESG Impact", "Sector Analysis"])

    with tab1:
        fig = px.histogram(
            scenario_df,
            x="PD ESG Adjusted",
            nbins=20,
            color="Industry",
            title="Probability of Default Distribution",
            labels={"PD ESG Adjusted": "Default Probability"},
            hover_data=["Ticker"]
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(
                scenario_df,
                x="ESG_Score",
                y="PD ESG Adjusted",
                color="Industry",
                size="CarbonIntensity",
                title="ESG Score vs Default Risk",
                hover_name="Ticker"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                scenario_df.sort_values("PD ESG Adjusted", ascending=False)[:10],
                x="Ticker",
                y=["PD Baseline", "PD ESG Adjusted"],
                title="Top 10 Riskiest Firms",
                barmode="group"
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        sector_analysis = scenario_df.groupby("Industry").agg({
            "PD ESG Adjusted": "mean",
            "Capital Requirement": "sum"
        }).reset_index()

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                sector_analysis,
                names="Industry",
                values="Capital Requirement",
                title="Capital Allocation by Sector"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                sector_analysis.sort_values("PD ESG Adjusted", ascending=False),
                x="Industry",
                y="PD ESG Adjusted",
                title="Sector Risk Profile"
            )
            st.plotly_chart(fig, use_container_width=True)

    # ---- Data Table ----
    st.subheader("Portfolio Details")
    st.dataframe(
        scenario_df.sort_values("PD ESG Adjusted", ascending=False),
        column_config={
            "Ticker": "Company",
            "PD Baseline": st.column_config.NumberColumn(
                "Baseline PD",
                format="%.2f%%",
                help="Default probability without ESG factors"
            ),
            "PD ESG Adjusted": st.column_config.NumberColumn(
                "ESG Adjusted PD",
                format="%.2f%%"
            ),
            "ESG_Score": st.column_config.ProgressColumn(
                "ESG Score",
                format="%d",
                min_value=0,
                max_value=100
            ),
            "Capital Requirement": st.column_config.NumberColumn(
                "Capital (€M)",
                format="€%.1fM"
            )
        },
        hide_index=True,
        use_container_width=True
    )

if __name__ == "__main__":
    main()
