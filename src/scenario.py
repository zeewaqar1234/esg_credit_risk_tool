# src/scenario.py
class ClimateScenarioEngine:
    SCENARIO_MULTIPLIERS = {
        "Orderly Transition": 1.2,
        "Disorderly Transition": 1.8,
        "Hot House World": 2.5
    }

    def apply_scenario(self, df, scenario_name, carbon_sensitivity=100):  # This is correct
        """
        Apply climate scenario impacts to carbon intensity based on:
          1) scenario multiplier (1.2, 1.8, 2.5)
          2) user slider carbon_sensitivity (50%-300%)
        """
        # Create copy to avoid modifying original DataFrame
        df = df.copy()
        
        # Apply scenario multipliers
        df["CarbonIntensity"] *= self.SCENARIO_MULTIPLIERS[scenario_name]
        
        # Apply user sensitivity adjustment
        df["CarbonIntensity"] *= (carbon_sensitivity / 100.0)
        
        # Adjust financial metrics based on new carbon intensity
        df["EBIT_Margin"] -= df["CarbonIntensity"] / 10000.0
        
        return df