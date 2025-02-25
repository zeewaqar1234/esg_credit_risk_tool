# dax_data_pipeline.py
import pandas as pd
import numpy as np
import logging
import os
import time
from pathlib import Path
from alpha_vantage.fundamentaldata import FundamentalData
from src.data_validation import EBAValidator
from src.eba_config import COLUMN_MAP, RISK_THRESHOLDS

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =====================
# EBA 2025 CONFIGURATION
# =====================
API_KEY = 'T9373AC0MC6FROK3'  
DAX_TICKERS = ["SAP", "ALV.DE", "DTE.DE", "BAS.DE", "BAYN.DE", 
              "BMW.DE", "DAI.DE", "SIE.DE", "ADS.DE", "MUV2.DE"]
OUTPUT_FILE = "data/eba_dataset.csv"  # New EBA-compliant output
FALLBACK_MODE = True  # Use manual data if API fails

# EBA Manual Data Entries (Extended)
MANUAL_DATA = {
    "SAP": {
        # Financials
        "Debt/Equity": 0.32,
        "InterestCoverage": 8.5,
        "TotalAssets": 68.3e9,
        
        # EBA ESG Factors
        "CarbonIntensity": 80,        # tCO2/€M revenue
        "ESG_Score": 82,              # 0-100 scale (higher=better)
        "BoardDiversity": 0.40,       # 40% female board members
        "ControversyFlag": 0,         # 1=active controversies
        
        "Industry": "Technology"
    },
    "ALV.DE": {
        "Debt/Equity": 0.28,
        "InterestCoverage": 9.1,
        "TotalAssets": 1.2e12,
        "CarbonIntensity": 45,
        "ESG_Score": 76,
        "BoardDiversity": 0.35,
        "ControversyFlag": 0,
        "Industry": "Financials"
    },
    # ... (complete entries for all DAX firms)
}

def fetch_eba_financials() -> pd.DataFrame:
    """Fetch EBA-required financial metrics with robust error handling"""
    fd = FundamentalData(API_KEY, output_format='pandas')
    records = []
    
    logger.info("Starting EBA financial data collection...")
    
    for ticker in DAX_TICKERS:
        try:
            # API Rate Limiting
            time.sleep(20)  # Alpha Vantage limit: 5 calls/minute
            
            # Fetch fundamental data
            bs = fd.get_balance_sheet_annual(ticker)[0]
            is_ = fd.get_income_statement_annual(ticker)[0]
            
            # EBA-specific calculations
            record = {
                'Ticker': ticker,
                'Debt/Equity': bs['totalDebt'][0] / bs['totalShareholderEquity'][0],
                'InterestCoverage': is_['ebit'][0] / abs(is_['interestExpense'][0]),
                'TotalAssets': bs['totalAssets'][0]
            }
            records.append(record)
            logger.info(f"API success: {ticker}")
            
        except Exception as e:
            if FALLBACK_MODE:
                logger.warning(f"Using manual data for {ticker}")
                manual_entry = {
                    k: v for k, v in MANUAL_DATA[ticker].items() 
                    if k in ['Debt/Equity', 'InterestCoverage', 'TotalAssets']
                }
                records.append({'Ticker': ticker, **manual_entry})
            else:
                logger.error(f"Failed {ticker}: {str(e)}")
                continue
                
    return pd.DataFrame(records)

def add_eba_esg_features(df: pd.DataFrame) -> pd.DataFrame:
    """Integrate EBA-required ESG metrics with validation"""
    # Validate input structure
    if 'Ticker' not in df.columns:
        raise ValueError("Ticker column required for ESG mapping")
    
    # Carbon Intensity (Transition Risk)
    df['CarbonIntensity'] = df['Ticker'].map(
        lambda x: MANUAL_DATA[x]['CarbonIntensity']
    )
    
    # Governance Metrics
    df['ESG_Score'] = df['Ticker'].map(
        lambda x: MANUAL_DATA[x]['ESG_Score']
    )
    df['BoardDiversity'] = df['Ticker'].map(
        lambda x: MANUAL_DATA[x]['BoardDiversity']
    )
    
    # Controversy Tracking (SFDR Compliance)
    df['ControversyFlag'] = df['Ticker'].map(
        lambda x: MANUAL_DATA[x]['ControversyFlag']
    )
    
    # Industry Classification
    df['Industry'] = df['Ticker'].map(
        lambda x: MANUAL_DATA[x]['Industry']
    )
    
    return df

def generate_eba_dataset() -> pd.DataFrame:
    """End-to-end EBA 2025 compliant dataset generation"""
    logger.info("Initializing EBA 2025 dataset pipeline...")
    
    # Phase 1: Financial Data
    financial_df = fetch_eba_financials()
    
    # Phase 2: ESG Integration
    esg_df = add_eba_esg_features(financial_df)
    
    # Phase 3: Validation
    validator = EBAValidator()
    valid, report = validator.validate_dataset(esg_df)
    
    if not valid:
        logger.error(f"EBA validation failed:\n{report}")
        raise ValueError("Dataset non-compliant with EBA 2025 standards")
    
    # Phase 4: Persistence
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    esg_df.to_csv(output_path, index=False)
    
    logger.info(f"EBA dataset generated successfully at {output_path}")
    logger.debug(f"Validation report:\n{report}")
    
    return esg_df

if __name__ == "__main__":
    try:
        df = generate_eba_dataset()
        print("\nFirst 3 EBA-compliant records:")
        print(df[COLUMN_MAP['required']].head(3))
    except Exception as e:
        logger.critical(f"Pipeline failed: {str(e)}")
        raise