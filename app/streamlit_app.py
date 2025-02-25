import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import logging
import subprocess
import plotly.express as px

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fix path for src imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.model import EBACreditModel
from src.scenario import EBAStressEngine
from src.eba_config import SCENARIOS, RISK_LEVELS
from src.visualization_eba import EBAVisualizer

def main():
    st.set_page_config(page_title="EBA ESG Risk Dashboard", page_icon="🌍", layout="wide")

    # Load data with option to regenerate
    @st.cache_data
    def load_data():
        data_path = project_root / "data" / "final_dataset.csv"
        logger.info(f"Loading data from: {data_path}")
        try:
            df = pd.read_csv(data_path)
            required = ['Ticker', 'Debt/Equity', 'InterestCoverage', 'CarbonImpact', 
                        'EmissionsTrend', 'SocialScore', 'GovernanceScore', 'TotalAssets']
            logger.info(f"Loaded columns: {list(df.columns)}")
            missing = [col for col in required if col not in df.columns]
            if missing:
                st.error(f"Data missing: {', '.join(missing)}. Update src/data_pipeline.py and run it.")
                st.write("Current columns in final_dataset.csv:", list(df.columns))
                if st.button("Run Data Pipeline Now"):
                    try:
                        result = subprocess.run(['python3', 'src/data_pipeline.py'], 
                                             cwd=str(project_root), capture_output=True, text=True)
                        st.write("Pipeline Output:", result.stdout)
                        if result.stderr:
                            st.error(f"Pipeline Error: {result.stderr}")
                        else:
                            st.success("Pipeline ran successfully! Refresh the page.")
                    except Exception as e:
                        st.error(f"Failed to run pipeline: {e}")
                st.stop()
            return df
        except FileNotFoundError:
            st.error("No final_dataset.csv found! Run src/data_pipeline.py first.")
            st.stop()

    base_df = load_data()

    # Model and scenarios
    model = EBACreditModel()
    engine = EBAStressEngine()

    # Sidebar
    with st.sidebar:
        st.header("Stress Test Options")
        scenario = st.selectbox("Choose Scenario", list(SCENARIOS.keys()), index=0)
        st.markdown(f"**High Risk:** {RISK_LEVELS['high_risk']} | **High Emitter:** {RISK_LEVELS['high_emitter']} tCO₂/€M")
        st.info("EBA 2025: Tests transition (carbon costs) and physical (climate events) risks.")

    # Process data
    normal_df = engine.apply_scenario(base_df, 'Normal')
    normal_risk = model.calculate_risk(normal_df)
    scenario_df = engine.apply_scenario(base_df, scenario)
    risk_df = model.calculate_risk(scenario_df)
    risk_df['StressCapital'] = model.estimate_capital(risk_df)
    risk_df['RiskChange'] = risk_df['RiskScore'] - normal_risk['RiskScore']

    # Dashboard
    st.title("EBA 2025 ESG Risk Dashboard")
    st.markdown("See how ESG risks affect DAX firms—aligned with EBA 2025 guidelines.")

    # Metrics with better layout
    st.subheader("Key Insights")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        risky = int(risk_df['RiskLevel'].eq('High Risk').sum())  # Convert to Python int
        delta_risky = int(risky - normal_risk['RiskLevel'].eq('High Risk').sum())  # Convert to Python int
        st.metric("High Risk Firms", risky, delta=delta_risky, delta_color="inverse")
    with col2:
        carbon = float(risk_df['CarbonImpact'].mean())  # Convert to Python float
        delta_carbon = float(carbon - normal_df['CarbonImpact'].mean())  # Convert to Python float
        st.metric("Avg Carbon Impact", f"{carbon:.1f} tCO₂/€M", delta=f"{delta_carbon:.1f}")
    with col3:
        capital = float(risk_df['StressCapital'].sum() / 1e6)  # Convert to Python float
        st.metric("Stress Capital", f"€{capital:,.0f}M", help="Extra funds for ESG losses (EBA stress test)")
    with col4:
        avg_risk = float(risk_df['RiskScore'].mean())  # Convert to Python float
        delta_risk = float(risk_df['RiskChange'].mean())  # Convert to Python float
        st.metric("Avg Risk Score", f"{avg_risk:.2f}", delta=f"{delta_risk:+.2f}")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Risk Overview", "Industry Insights", "Firm Details"])

    with tab1:
        st.subheader("Risk and ESG Breakdown")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(EBAVisualizer.risk_score_distribution(risk_df), use_container_width=True)
        with col2:
            st.plotly_chart(EBAVisualizer.carbon_risk_scatter(risk_df), use_container_width=True)
        st.plotly_chart(EBAVisualizer.risk_drivers(risk_df), use_container_width=True)

    with tab2:
        st.subheader("How Industries Compare")
        industry_avg = risk_df.groupby('Industry').agg({
            'RiskScore': 'mean', 'CarbonImpact': 'mean', 'StressCapital': 'sum'
        }).reset_index()
        industry_avg['StressCapital'] = industry_avg['StressCapital'] / 1e6  # Convert to €M
        st.plotly_chart(
            px.bar(industry_avg, x='Industry', y='RiskScore', title="Average Risk by Industry",
                   color='RiskScore', color_continuous_scale='RdYlGn_r', text_auto='.2f'),
            use_container_width=True
        )
        st.dataframe(industry_avg.rename(columns={'StressCapital': 'Total Stress Capital (€M)'}))

    with tab3:
        st.subheader("Firm-by-Firm View")
        display_df = risk_df[[
            'Ticker', 'Industry', 'RiskScore', 'RiskLevel', 'RiskChange',
            'CarbonImpact', 'EmissionsTrend', 'SocialScore', 'GovernanceScore', 'StressCapital'
        ]].sort_values('RiskScore', ascending=False)
        st.dataframe(
            display_df,
            column_config={
                'RiskScore': st.column_config.NumberColumn("Risk Score", format="%.2f"),
                'RiskChange': st.column_config.NumberColumn("Change vs Normal", format="%.2f"),
                'CarbonImpact': st.column_config.NumberColumn("Carbon (tCO₂/€M)", format="%.0f"),
                'EmissionsTrend': st.column_config.ProgressColumn("Emissions Trend", min_value=-50, max_value=50, format="%d%%"),
                'SocialScore': st.column_config.ProgressColumn("Social Score", min_value=0, max_value=100, format="%d"),
                'GovernanceScore': st.column_config.ProgressColumn("Governance", min_value=0, max_value=100, format="%d"),
                'StressCapital': st.column_config.NumberColumn("Stress Capital (€)", format="€%.0f")
            },
            hide_index=True,
            use_container_width=True
        )

if __name__ == "__main__":
    main()