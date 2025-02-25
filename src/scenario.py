import pandas as pd
import logging
from .eba_config import SCENARIOS, RISK_LEVELS

class EBAStressEngine:
    """
    EBA 2025 Stress Testing
    Applies Normal, Transition, and Physical scenarios with ESG impacts.
    """
    
    def __init__(self):
        self.scenarios = SCENARIOS
        self.high_emitter_limit = RISK_LEVELS['high_emitter']
        self.logger = logging.getLogger(__name__)

    def apply_scenario(self, df, scenario_name):
        """
        Adjusts financials and ESG under EBA scenarios.
        Adds: CarbonImpact, EmissionsTrend, SocialScore, GovernanceScore adjustments.
        """
        if scenario_name not in self.scenarios:
            self.logger.error(f"Unknown scenario: {scenario_name}")
            raise ValueError(f"Pick: {list(self.scenarios.keys())}")

        needed = ['CarbonImpact', 'InterestCoverage', 'EmissionsTrend', 'SocialScore', 'GovernanceScore']
        missing = [col for col in needed if col not in df.columns]
        if missing:
            self.logger.error(f"Missing columns: {missing}")
            raise ValueError(f"Need: {missing}")

        df = df.copy()
        carbon_mult = self.scenarios[scenario_name]['carbon_multiplier']
        coverage_mult = self.scenarios[scenario_name]['coverage_multiplier']

        # Apply scenario effects
        df['CarbonImpact'] *= carbon_mult
        df['InterestCoverage'] *= coverage_mult
        if scenario_name == 'Transition Stress':
            df['EmissionsTrend'] += 10  # Carbon rules push emissions up
            df['GovernanceScore'] -= 5  # Pressure on management
        elif scenario_name == 'Physical Stress':
            df['SocialScore'] -= 10     # Community disruption
            df['EmissionsTrend'] -= 5   # Operations cut emissions slightly

        # Cap ESG scores
        df['SocialScore'] = df['SocialScore'].clip(0, 100)
        df['GovernanceScore'] = df['GovernanceScore'].clip(0, 100)
        df['EmissionsTrend'] = df['EmissionsTrend'].clip(-50, 50)

        # Flags and audit
        df['HighEmitter'] = df['CarbonImpact'] > self.high_emitter_limit
        df['Scenario'] = scenario_name

        self.logger.info(f"Applied {scenario_name}: Carbon x{carbon_mult}, Coverage x{coverage_mult}")
        return df