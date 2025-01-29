# ESG Credit Risk Tool

A **proof-of-concept** Python application that combines **ESG metrics** and **climate scenario analysis** with **traditional credit risk modeling**. Designed to illustrate how carbon intensity, sustainability scores, and macro-level climate changes can influence a company’s default probability and required capital buffers.

## Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Data Sources](#data-sources)
4. [Project Structure](#project-structure)
5. [Installation & Setup](#installation--setup)
6. [How to Run](#how-to-run)
7. [Limitations & Disclaimer](#limitations--disclaimer)
8. [License](#license)

---

## Overview
This project focuses on **DAX-listed** companies to demonstrate how ESG scores and carbon intensities can affect credit risk. The model estimates default probabilities with and without ESG factors, then applies climate scenario multipliers to see how regulatory changes, carbon costs, or user-defined “sensitivity” factors alter corporate risk profiles.

**Why?**
- Growing investor and regulatory pressure (e.g., EU CSRD) means finance professionals need actionable insights into sustainability’s financial impacts.  
- This tool highlights how **poor ESG performance** might translate into **higher capital requirements** and increased risk of default.

---

## Key Features
- **ESG-Integrated Risk Model**: Blends standard financial ratios (Debt/Equity, EBIT Margin, etc.) with carbon intensity and ESG scores.  
- **Scenario Engine**: Simulates “Orderly,” “Disorderly,” or “Hot House” worlds, plus a user-controlled slider (carbon sensitivity).  
- **Default Probability & Capital**: Calculates estimated PD for each firm and a simplified “capital requirement” (e.g., PD × Assets × LGD).  
- **Interactive Dashboard**: Built with Streamlit for a user-friendly interface, visualizations, and real-time scenario toggling.

---

## Data Sources
1. **Financial Data**: Either pulled from Alpha Vantage or manually provided fallback stats for DAX companies (SAP, Allianz, Deutsche Telekom, BASF, Bayer, BMW, Mercedes-Benz Group, Siemens, Adidas, Munich Re).
2. **ESG & Carbon Metrics**: Sourced from public databases, manual inputs, or **synthetic** values for demonstration.
3. **Scenario Multipliers**: Based on *hypothetical* climate pathways (e.g., BIS, ECB studies, or IPCC-inspired assumptions).

---

## Project Structure
```
esg_credit_risk_tool/
│
├── app/
│   └── streamlit_app.py         # Streamlit UI
├── data/
│   ├── final_dataset.csv        # Final merged dataset
│   └── ... (other CSVs)
├── notebooks/
│   └── 01_data_cleaning.ipynb   # Data prep & exploration
│   └── 02_model_development.ipynb
├── src/
│   ├── scenario.py              # Scenario engine
│   ├── model.py                 # CreditRiskModel (logistic regression)
│   └── ...
├── requirements.txt             # Python dependencies
├── README.md                    # <-- (this file!)
└── ...
```

---

## Installation & Setup

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/<your-username>/esg_credit_risk_tool.git
   cd esg_credit_risk_tool
   ```
2. **Create a Virtual Environment** (optional but recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or .venv\Scripts\activate for Windows
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional) **Set Up API Keys**:
   If you’re pulling live data from Alpha Vantage or other APIs, add your keys in an `.env` file or directly in the code (not recommended for production).

---

## How to Run

1. **Generate/Verify Data**:
   - If needed, run data pipeline scripts or notebooks (e.g., `dax_data_pipeline.py`) to fetch fundamental data and merge with ESG info.
2. **Launch Streamlit**:
   ```bash
   streamlit run app/streamlit_app.py
   ```
3. **Open in Browser**:
   - Default URL is typically `http://localhost:8501`.
4. **Explore**:
   - Adjust the **scenario** dropdown (Orderly, Disorderly, Hot House).
   - Move the **carbon sensitivity** slider and observe how PD and capital requirements change.
   - Switch to different tabs for distribution plots, ESG impact, or sector analysis.

---

## Limitations & Disclaimer
- **Prototype-Only**: Not a production-grade model; it’s a conceptual demonstration.
- **Simplified Data**: Some values are synthetic or manually approximated—**real-world** usage requires more robust, verified data sources and thorough validation.
- **Scope**: Focused on selected DAX firms, so it may not generalize to other markets or smaller companies.
- **No Guarantee of Accuracy**: Default flags and PDs are based on logistic regression with limited data and arbitrary thresholds. Use caution if applying in real-world decisions.

---

## License
This project is released under the [MIT License](LICENSE) (or whichever license you prefer). See `LICENSE` for details.

**Questions or Contributions?**  
Feel free to open an issue or pull request. Suggestions and improvements are always welcome!