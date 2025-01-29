import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

class CreditRiskModel:
    def __init__(self):
        self.baseline_features = [
            'Debt/Equity', 'InterestCoverage', 'EBIT_Margin', 'Volatility'
        ]
        self.esg_features = self.baseline_features + [
            'ESG_Score', 'CarbonIntensity'
        ]
        self.baseline_model = self._train_model(self.baseline_features)
        self.esg_model = self._train_model(self.esg_features)
    
    def _train_model(self, features):
        """Train model with preprocessing pipeline"""
        df = pd.read_csv("data/final_dataset.csv")
        
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('classifier', CalibratedClassifierCV(LogisticRegression()))
        ])
        
        pipeline.fit(df[features], df['Default_Flag'])
        return pipeline
    
    def predict_pd(self, df, include_esg=True):
        """Predict PDs with proper feature handling"""
        features = self.esg_features if include_esg else self.baseline_features
        model = self.esg_model if include_esg else self.baseline_model
        
        X = df[features].copy()
        return model.predict_proba(X)[:,1]

    def calculate_capital(self, df, include_esg=True):
        """Calculate capital requirements with error handling"""
        try:
            df = df.copy()
            df['PD'] = self.predict_pd(df, include_esg=include_esg)
            return df['PD'] * df['TotalAssets'] * 0.45
        except Exception as e:
            logging.error(f"Error calculating capital: {str(e)}")
            return None