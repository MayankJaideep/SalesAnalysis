# Tiny Sales Guru 📈

A high-fidelity sales analytics dashboard built entirely in **Python** using **Streamlit**, **Pandas**, and **Plotly**.

## Features
- **Smart Data Ingestion**: Automatically detects and maps CSV columns (Date, Revenue, Quantity, etc.) using fuzzy matching.
- **Interactive Filtering**: Filter by Region, Salesperson, and Date Range with real-time updates.
- **Advanced Forecasting**: Uses linear regression to predict next-month sales trends.
- **Leaderboard**: Ranked salesperson performance tracking with units and revenue metrics.
- **Export**: Download filtered reports directly as CSV.
- **Rich Visuals**: Beautiful dark-themed charts for monthly trends, category mix, and product performance.

## Getting Started

### Prerequisites
- Python 3.8+
- Pip

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/MayankJaideep/SalesAnalysis.git
   cd SalesAnalysis
   ```

2. Install dependencies:
   ```bash
   pip install streamlit pandas numpy plotly
   ```

### Running the App
```bash
streamlit run app.py
```

## How it Works
The project uses a single-file architecture (`app.py`) to handle:
1. **Frontend**: Streamlit components for the sidebar, metrics, and layout.
2. **Analysis**: Pandas for data cleaning, normalization, and grouping.
3. **Visualization**: Plotly for high-performance interactive charts.
