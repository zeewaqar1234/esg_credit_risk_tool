import pandas as pd
from pathlib import Path
import sys
import logging
from fpdf import FPDF  # Requires `pip install fpdf`

# Fix path for src imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.eba_config import SCENARIOS, RISK_LEVELS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def export_report(risk_df, scenario_name, output_format='csv', output_dir="reports"):
    """
    Exports risk data to CSV or PDF for EBA 2025 reporting.
    Args:
        risk_df: DataFrame with risk data from streamlit_app.py
        scenario_name: Name of the scenario (e.g., 'Transition Stress')
        output_format: 'csv' or 'pdf'
        output_dir: Directory to save the report
    """
    # Prepare report data
    report_df = risk_df[[
        'Ticker', 'Industry', 'RiskScore', 'RiskLevel', 'RiskChange',
        'CarbonImpact', 'EmissionsTrend', 'SocialScore', 'GovernanceScore', 'StressCapital'
    ]].sort_values('RiskScore', ascending=False)

    # Create output directory
    output_path = project_root / output_dir
    output_path.mkdir(exist_ok=True)

    # File name
    file_name = f"eba_risk_report_{scenario_name.replace(' ', '_').lower()}.{output_format}"
    full_path = output_path / file_name

    if output_format == 'csv':
        report_df.to_csv(full_path, index=False)
        logger.info(f"CSV report saved to {full_path}")
    elif output_format == 'pdf':
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Title
        pdf.cell(200, 10, txt=f"EBA 2025 ESG Risk Report - {scenario_name}", ln=True, align='C')
        pdf.ln(10)
        
        # Headers
        headers = report_df.columns.tolist()
        col_widths = [30, 30, 20, 20, 20, 25, 25, 20, 20, 30]
        for header, width in zip(headers, col_widths):
            pdf.cell(width, 10, header, border=1)
        pdf.ln()
        
        # Data
        for _, row in report_df.iterrows():
            pdf.cell(col_widths[0], 10, str(row['Ticker']), border=1)
            pdf.cell(col_widths[1], 10, str(row['Industry']), border=1)
            pdf.cell(col_widths[2], 10, f"{row['RiskScore']:.2f}", border=1)
            pdf.cell(col_widths[3], 10, str(row['RiskLevel']), border=1)
            pdf.cell(col_widths[4], 10, f"{row['RiskChange']:.2f}", border=1)
            pdf.cell(col_widths[5], 10, f"{row['CarbonImpact']:.0f}", border=1)
            pdf.cell(col_widths[6], 10, f"{row['EmissionsTrend']}%", border=1)
            pdf.cell(col_widths[7], 10, f"{row['SocialScore']}", border=1)
            pdf.cell(col_widths[8], 10, f"{row['GovernanceScore']}", border=1)
            pdf.cell(col_widths[9], 10, f"€{row['StressCapital']/1e6:.0f}M", border=1)
            pdf.ln()
        
        pdf.output(str(full_path))
        logger.info(f"PDF report saved to {full_path}")
    else:
        raise ValueError("Output format must be 'csv' or 'pdf'")

    return full_path

def main():
    # Example usage (normally called from streamlit_app.py)
    sample_df = pd.DataFrame({
        'Ticker': ['SAP'], 'Industry': ['Technology'], 'RiskScore': [0.25],
        'RiskLevel': ['Safe'], 'RiskChange': [0.05], 'CarbonImpact': [80],
        'EmissionsTrend': [-10], 'SocialScore': [85], 'GovernanceScore': [90],
        'StressCapital': [1000000000]
    })
    export_report(sample_df, "Normal", output_format='csv')
    export_report(sample_df, "Normal", output_format='pdf')

if __name__ == "__main__":
    main()