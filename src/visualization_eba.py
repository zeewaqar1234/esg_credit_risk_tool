import plotly.express as px
import plotly.graph_objects as go
from .eba_config import RISK_LEVELS

class EBAVisualizer:
    """
    Visuals for EBA 2025 ESG Risk Tool
    Highlights risk spread, carbon impact, and what drives risk scores.
    """

    @staticmethod
    def risk_score_distribution(df):
        """
        Histogram of Risk Scores with EBA high-risk threshold.
        Colors by Risk Level for clear impact.
        """
        fig = px.histogram(
            df,
            x='RiskScore',
            color='RiskLevel',
            nbins=20,
            title="Risk Score Spread Across Firms",
            labels={'RiskScore': 'Risk Score (0-1)'},
            color_discrete_map={'High Risk': '#FF4136', 'Safe': '#2ECC40'},
            opacity=0.8
        )
        fig.add_vline(
            x=RISK_LEVELS['high_risk'],
            line_dash="dash",
            line_color="black",
            annotation_text="EBA High Risk Threshold",
            annotation_position="top right"
        )
        fig.update_layout(
            bargap=0.1,
            title_font_size=18,
            showlegend=True
        )
        return fig

    @staticmethod
    def carbon_risk_scatter(df):
        """
        Scatter plot of Carbon Impact vs Risk Score.
        Sizes by assets, colors high emitters.
        """
        fig = px.scatter(
            df,
            x='CarbonImpact',
            y='RiskScore',
            size='TotalAssets',
            color='HighEmitter',
            hover_name='Ticker',
            hover_data=['Industry'],
            title="Carbon Impact vs Risk Score",
            labels={'CarbonImpact': 'Carbon Impact (tCO₂/€M)', 'RiskScore': 'Risk Score (0-1)'},
            color_discrete_map={True: '#FF4136', False: '#2ECC40'}
        )
        fig.add_vline(
            x=RISK_LEVELS['high_emitter'],
            line_dash="dash",
            line_color="black",
            annotation_text="EBA High Emitter Limit",
            annotation_position="top left"
        )
        fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        fig.update_layout(title_font_size=18)
        return fig

    @staticmethod
    def risk_drivers(df):
        """
        Stacked bar chart showing what drives Risk Scores.
        Breaks down Debt, Interest, Carbon, ESG contributions.
        """
        drivers = df[['Ticker', 'DebtImpact', 'InterestImpact', 'CarbonImpactScore', 
                      'EmTrendImpact', 'SocialImpact', 'GovImpact']].melt(
            id_vars=['Ticker'],
            value_vars=['DebtImpact', 'InterestImpact', 'CarbonImpactScore', 
                        'EmTrendImpact', 'SocialImpact', 'GovImpact'],
            var_name='Driver',
            value_name='Contribution'
        )
        
        fig = px.bar(
            drivers,
            x='Ticker',
            y='Contribution',
            color='Driver',
            title="What’s Driving Risk Scores?",
            labels={'Contribution': 'Risk Contribution (0-1)'},
            color_discrete_map={
                'DebtImpact': '#1F77B4',        # Blue
                'InterestImpact': '#FF7F0E',    # Orange
                'CarbonImpactScore': '#D62728', # Red
                'EmTrendImpact': '#9467BD',     # Purple
                'SocialImpact': '#2CA02C',      # Green
                'GovImpact': '#E377C2'          # Pink
            }
        )
        fig.update_layout(
            barmode='stack',
            title_font_size=18,
            xaxis_title="Firm",
            yaxis_title="Risk Contribution",
            legend_title="Risk Drivers"
        )
        return fig