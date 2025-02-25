import pandas as pd
import os
import logging
import sys
from pathlib import Path

# Fix import path for standalone execution
project_root = Path(__file__).parent.parent  # Root of esg_credit_risk_tool/
sys.path.append(str(project_root))
from src.eba_config import MUST_HAVE_COLUMNS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DAX companies
DAX_TICKERS = ["SAP", "ALV.DE", "DTE.DE", "BAS.DE", "BAYN.DE", 
               "BMW.DE", "DAI.DE", "SIE.DE", "ADS.DE", "MUV2.DE"]

# Output file
OUTPUT_FILE = "data/final_dataset.csv"

# Manual data with exact ESG fields
MANUAL_DATA = {
    "SAP": {
        "Debt/Equity": 0.32, "InterestCoverage": 8.5, "CarbonImpact": 80, 
        "EmissionsTrend": -10, "SocialScore": 85, "GovernanceScore": 90, 
        "TotalAssets": 68.3e9, "Industry": "Technology"
    },
    "ALV.DE": {
        "Debt/Equity": 0.28, "InterestCoverage": 9.1, "CarbonImpact": 45, 
        "EmissionsTrend": 5, "SocialScore": 80, "GovernanceScore": 75, 
        "TotalAssets": 1.2e12, "Industry": "Financials"
    },
    "DTE.DE": {
        "Debt/Equity": 1.15, "InterestCoverage": 3.8, "CarbonImpact": 180, 
        "EmissionsTrend": 0, "SocialScore": 70, "GovernanceScore": 65, 
        "TotalAssets": 300e9, "Industry": "Telecommunications"
    },
    "BAS.DE": {
        "Debt/Equity": 0.65, "InterestCoverage": 6.8, "CarbonImpact": 850, 
        "EmissionsTrend": 15, "SocialScore": 60, "GovernanceScore": 70, 
        "TotalAssets": 85.4e9, "Industry": "Chemicals"
    },
    "BAYN.DE": {
        "Debt/Equity": 0.82, "InterestCoverage": 7.1, "CarbonImpact": 320, 
        "EmissionsTrend": 8, "SocialScore": 75, "GovernanceScore": 68, 
        "TotalAssets": 112e9, "Industry": "Pharmaceuticals"
    },
    "BMW.DE": {
        "Debt/Equity": 1.15, "InterestCoverage": 4.2, "CarbonImpact": 480, 
        "EmissionsTrend": -5, "SocialScore": 82, "GovernanceScore": 80, 
        "TotalAssets": 246e9, "Industry": "Automotive"
    },
    "DAI.DE": {
        "Debt/Equity": 1.75, "InterestCoverage": 5.2, "CarbonImpact": 510, 
        "EmissionsTrend": -2, "SocialScore": 78, "GovernanceScore": 76, 
        "TotalAssets": 260e9, "Industry": "Automotive"
    },
    "SIE.DE": {
        "Debt/Equity": 0.45, "InterestCoverage": 6.2, "CarbonImpact": 220, 
        "EmissionsTrend": 3, "SocialScore": 72, "GovernanceScore": 74, 
        "TotalAssets": 145e9, "Industry": "Industrial"
    },
    "ADS.DE": {
        "Debt/Equity": 0.55, "InterestCoverage": 5.5, "CarbonImpact": 150, 
        "EmissionsTrend": 0, "SocialScore": 68, "GovernanceScore": 70, 
        "TotalAssets": 22.5e9, "Industry": "Consumer"
    },
    "MUV2.DE": {
        "Debt/Equity": 0.31, "InterestCoverage": 8.8, "CarbonImpact": 50, 
        "EmissionsTrend": 2, "SocialScore": 77, "GovernanceScore": 78, 
        "TotalAssets": 280e9, "Industry": "Financials"
    }
}

def build_dataset():
    """
    Builds dataset with exact columns for EBA ESG Risk Tool.
    Saves to final_dataset.csv with logging.
    """
    logger.info("Starting dataset build...")

    data = []
    for ticker in DAX_TICKERS:
        firm_data = MANUAL_DATA.get(ticker, {})
        record = {
            'Ticker': ticker,
            'Debt/Equity': firm_data.get('Debt/Equity', 0),
            'InterestCoverage': firm_data.get('InterestCoverage', 0),
            'CarbonImpact': firm_data.get('CarbonImpact', 0),
            'EmissionsTrend': firm_data.get('EmissionsTrend', 0),
            'SocialScore': firm_data.get('SocialScore', 0),
            'GovernanceScore': firm_data.get('GovernanceScore', 0),
            'TotalAssets': firm_data.get('TotalAssets', 0),
            'Industry': firm_data.get('Industry', 'Unknown')
        }
        data.append(record)
        logger.debug(f"Added {ticker}")

    df = pd.DataFrame(data)
    logger.info(f"Generated columns: {list(df.columns)}")

    # Verify columns
    missing = [col for col in MUST_HAVE_COLUMNS if col not in df.columns]
    if missing:
        logger.error(f"Missing columns: {missing}")
        raise ValueError(f"Missing: {missing}")

    # Save with overwrite
    output_path = os.path.join(project_root, OUTPUT_FILE)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Dataset saved to {output_path}")

    return df

def main():
    df = build_dataset()
    logger.info("Dataset generation complete")
    print("First 3 rows of the dataset:")
    print(df.head(3))

if __name__ == "__main__":
    main()