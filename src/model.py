import pandas as pd
import logging
from .eba_config import RISK_WEIGHTS, RISK_LEVELS

class EBACreditModel:
    """
    EBA 2025 Risk Model
    Calculates Risk Score and Stress Capital using debt, interest, and detailed ESG factors.
    Keeps it simple and tied to EBA stress tests.
    """
    
    def __init__(self):
        self.weights = RISK_WEIGHTS
        self.high_risk_limit = RISK_LEVELS['high_risk']
        self.logger = logging.getLogger(__name__)

    def calculate_risk(self, df):
        """
        Computes Risk Score (0-1) with ESG breakdown.
        Returns DataFrame with:
        - RiskScore: Overall risk (higher = worse)
        - RiskLevel: 'High Risk' or 'Safe'
        - Component contributions for transparency
        """
        needed = ['Debt/Equity', 'InterestCoverage', 'CarbonImpact', 
                  'EmissionsTrend', 'SocialScore', 'GovernanceScore']
        missing = [col for col in needed if col not in df.columns]
        if missing:
            self.logger.error(f"Missing columns: {missing}")
            raise ValueError(f"Need these: {missing}")

        # Normalize components (0-1 range, higher = riskier)
        df['DebtNorm'] = df['Debt/Equity'] / df['Debt/Equity'].max()
        df['InterestNorm'] = (1 / df['InterestCoverage']) / (1 / df['InterestCoverage']).max()
        df['CarbonNorm'] = df['CarbonImpact'] / df['CarbonImpact'].max()
        df['EmTrendNorm'] = (df['EmissionsTrend'] + 50) / 100  # -50 to 50 → 0 to 1
        df['SocialNorm'] = (100 - df['SocialScore']) / 100     # Lower score = higher risk
        df['GovNorm'] = (100 - df['GovernanceScore']) / 100    # Lower score = higher risk

        # Calculate Risk Score with weights
        df['RiskScore'] = (
            self.weights['Debt/Equity'] * df['DebtNorm'] +
            self.weights['InterestCoverage'] * df['InterestNorm'] +
            self.weights['CarbonImpact'] * df['CarbonNorm'] +
            self.weights['EmissionsTrend'] * df['EmTrendNorm'] +
            self.weights['SocialScore'] * df['SocialNorm'] +
            self.weights['GovernanceScore'] * df['GovNorm']
        )

        # Risk Level
        df['RiskLevel'] = df['RiskScore'].apply(
            lambda x: 'High Risk' if x >= self.high_risk_limit else 'Safe'
        )

        # Component contributions for analysis
        df['DebtImpact'] = self.weights['Debt/Equity'] * df['DebtNorm']
        df['InterestImpact'] = self.weights['InterestCoverage'] * df['InterestNorm']
        df['CarbonImpactScore'] = self.weights['CarbonImpact'] * df['CarbonNorm']
        df['EmTrendImpact'] = self.weights['EmissionsTrend'] * df['EmTrendNorm']
        df['SocialImpact'] = self.weights['SocialScore'] * df['SocialNorm']
        df['GovImpact'] = self.weights['GovernanceScore'] * df['GovNorm']

        return df

    def estimate_capital(self, df):
        """
        Estimates Stress Capital—extra funds needed for ESG risks under stress.
        EBA 2025: Capital to cover potential losses (Section 4.3).
        """
        if 'TotalAssets' not in df.columns:
            self.logger.error("Need TotalAssets for Stress Capital")
            raise ValueError("Missing TotalAssets")

        # RiskScore × Assets × 50% loss rate (simplified EBA proxy)
        return df['RiskScore'] * df['TotalAssets'] * 0.5