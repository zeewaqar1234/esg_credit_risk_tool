import pandas as pd
import logging
from .eba_config import MUST_HAVE_COLUMNS, RISK_LEVELS

class EBAValidator:
    """
    Validates data for EBA 2025 ESG Risk Tool
    Checks financials, ESG fields, and flags issues.
    """
    
    def __init__(self):
        self.required_columns = MUST_HAVE_COLUMNS
        self.high_emitter_limit = RISK_LEVELS['high_emitter']
        self.logger = logging.getLogger(__name__)

    def check_data(self, df):
        """
        Validates dataset with detailed ESG checks.
        Returns: (bool: valid?, str: report)
        """
        report = []

        # Check required columns
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            report.append(f"Missing columns: {', '.join(missing)}")
            self.logger.error(f"Data missing: {missing}")
            return False, "\n".join(report)

        # Check for empty values
        null_cols = df.columns[df.isnull().any()].tolist()
        if null_cols:
            report.append(f"Empty values in: {', '.join(null_cols)}")
            self.logger.warning("Found empty values")

        # ESG range checks
        if (df['EmissionsTrend'] < -50).any() or (df['EmissionsTrend'] > 50).any():
            report.append("EmissionsTrend out of range (-50 to 50)")
            self.logger.warning("EmissionsTrend values invalid")
        if (df['SocialScore'] < 0).any() or (df['SocialScore'] > 100).any():
            report.append("SocialScore out of range (0-100)")
            self.logger.warning("SocialScore values invalid")
        if (df['GovernanceScore'] < 0).any() or (df['GovernanceScore'] > 100).any():
            report.append("GovernanceScore out of range (0-100)")
            self.logger.warning("GovernanceScore values invalid")

        # High emitters
        high_emitters = df['CarbonImpact'].gt(self.high_emitter_limit).sum()
        report.append(f"High Emitters: {high_emitters} firms (over {self.high_emitter_limit} tCO₂/€M)")

        return True, "\n".join(report)

def validate_file(file_path):
    """
    Validates a CSV file.
    Returns: (bool: valid?, str: message)
    """
    try:
        df = pd.read_csv(file_path)
        validator = EBAValidator()
        is_valid, report = validator.check_data(df)
        return is_valid, report
    except Exception as e:
        return False, f"Error reading file: {str(e)}"