"""
EBA 2025 Settings for ESG Risk Tool
Defines weights, thresholds, and required columns—aligned with EBA guidelines.
"""

# Weights for Risk Score (sum to 1.0)
RISK_WEIGHTS = {
    'Debt/Equity': 0.35,       # Debt signals default risk
    'InterestCoverage': 0.25,  # Low interest coverage = cash flow trouble
    'CarbonImpact': 0.20,      # High emissions = cost risk (EBA transition focus)
    'EmissionsTrend': 0.10,    # Rising emissions = future liability
    'SocialScore': 0.05,       # Social issues = operational risk
    'GovernanceScore': 0.05    # Weak governance = management risk
}

# Thresholds for Risk Flags
RISK_LEVELS = {
    'high_risk': 0.4,         # Risk Score ≥ 0.4 = High Risk
    'high_emitter': 500       # Carbon Impact > 500 tCO₂/€M = High Emitter
}

# Scenarios for Stress Testing
SCENARIOS = {
    'Normal': {
        'carbon_multiplier': 1.0,    # No extra carbon cost
        'coverage_multiplier': 1.0   # No revenue hit
    },
    'Transition Stress': {
        'carbon_multiplier': 1.5,    # 50% carbon cost hike (EBA policy shock)
        'coverage_multiplier': 1.0   # No revenue hit
    },
    'Physical Stress': {
        'carbon_multiplier': 1.0,    # No extra carbon cost
        'coverage_multiplier': 0.9   # 10% revenue drop (EBA climate event)
    }
}

# Required Data Columns (exact match for Streamlit)
MUST_HAVE_COLUMNS = [
    'Ticker', 'Debt/Equity', 'InterestCoverage', 'CarbonImpact',
    'EmissionsTrend', 'SocialScore', 'GovernanceScore', 'TotalAssets'
]