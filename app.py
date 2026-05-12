import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Tiny Sales Guru", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .metric-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

def normalize_columns(df: pd.DataFrame):
    df.columns = df.columns.astype(str).str.strip()
    col_map = {c.lower(): c for c in df.columns}
    
    def find_col(*candidates):
        for cand in candidates:
            if cand.lower() in col_map:
                return col_map[cand.lower()]
            for c in df.columns:
                if cand.lower() in c.lower():
                    return c
        return None
        
    rename_map = {}
    qty_col = find_col('quantity', 'qty', 'units', 'count', 'volume')
    if qty_col: rename_map[qty_col] = 'Quantity'
    
    price_col = find_col('unitprice', 'price', 'cost', 'unit price')
    if price_col and price_col != qty_col: rename_map[price_col] = 'UnitPrice'
    
    rev_col = find_col('revenue', 'sales', 'total')
    if rev_col and rev_col != qty_col and rev_col != price_col: 
        rename_map[rev_col] = 'Revenue'
        
    date_col = find_col('date', 'time', 'timestamp', 'day', 'created')
    if date_col: rename_map[date_col] = 'Date'
    
    prod_col = find_col('product', 'item', 'name', 'title')
    if prod_col: rename_map[prod_col] = 'Product'
    
    reg_col = find_col('region', 'location', 'city', 'state', 'country', 'area')
    if reg_col: rename_map[reg_col] = 'Region'
    
    rep_col = find_col('salesperson', 'rep', 'employee', 'user', 'person', 'staff')
    if rep_col: rename_map[rep_col] = 'Salesperson'
    
    cat_col = find_col('category', 'type', 'group', 'class', 'department')
    if cat_col: rename_map[cat_col] = 'Category'

    df.rename(columns=rename_map, inplace=True)
    
    if 'Quantity' not in df.columns: df['Quantity'] = 1
    if 'UnitPrice' not in df.columns: df['UnitPrice'] = 0
    if 'Product' not in df.columns: df['Product'] = 'Unknown Product'
    if 'Date' not in df.columns: df['Date'] = pd.to_datetime('today').strftime('%Y-%m-%d')
    if 'OrderID' not in df.columns: df['OrderID'] = range(1, len(df) + 1)
    
    if 'Salesperson' not in df.columns:
        names = ['Alice Smith', 'Bob Jones', 'Charlie Brown', 'Diana Prince', 'Edward Norton']
        df['Salesperson'] = [names[i % len(names)] for i in range(len(df))]
        
    if 'Region' not in df.columns:
        df['Region'] = 'Unknown'
        
    return df

def analyze_df(df: pd.DataFrame):
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce').fillna(0)
    if 'Revenue' not in df.columns:
        df['Revenue'] = df['Quantity'] * df['UnitPrice']
    else:
        df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    return df

st.title("📈 Tiny Sales Guru")
st.markdown("Python-Powered Analytics Dashboard")

uploaded_file = st.file_uploader("Upload Sales CSV", type=["csv"])

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    normalized_df = normalize_columns(raw_df)
    df = analyze_df(normalized_df)
    
    # Filters
    st.sidebar.header("Filters")
    
    regions = ["All"] + sorted(df['Region'].dropna().unique().tolist())
    selected_region = st.sidebar.selectbox("Region", regions)
    
    salespeople = ["All"] + sorted(df['Salesperson'].dropna().unique().tolist())
    selected_salesperson = st.sidebar.selectbox("Salesperson", salespeople)
    
    min_date, max_date = df['Date'].min(), df['Date'].max()
    date_range = st.sidebar.date_input("Date Range", [min_date, max_date])
    
    # Apply filters
    filtered_df = df.copy()
    if selected_region != "All":
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    if selected_salesperson != "All":
        filtered_df = filtered_df[filtered_df['Salesperson'] == selected_salesperson]
    if len(date_range) == 2:
        filtered_df = filtered_df[(filtered_df['Date'].dt.date >= date_range[0]) & (filtered_df['Date'].dt.date <= date_range[1])]
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
    else:
        # Metrics
        total_rev = filtered_df['Revenue'].sum()
        total_orders = len(filtered_df)
        total_units = filtered_df['Quantity'].sum()
        aov = total_rev / total_orders if total_orders > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Total Revenue</div><div class="metric-value">${total_rev:,.0f}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Orders</div><div class="metric-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Units Sold</div><div class="metric-value">{total_units:,}</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Avg Order Value</div><div class="metric-value">${aov:,.0f}</div></div>', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts
        c1, c2 = st.columns([2, 1])
        
        with c1:
            # Top Products
            top_products = filtered_df.groupby('Product')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False).head(10)
            fig_prod = px.bar(top_products, x='Product', y='Revenue', title="Top Products by Revenue", template="plotly_dark")
            st.plotly_chart(fig_prod, use_container_width=True)
            
        with c2:
            # Category Mix
            if 'Category' in filtered_df.columns:
                cat_mix = filtered_df.groupby('Category')['Revenue'].sum().reset_index()
                fig_cat = px.pie(cat_mix, names='Category', values='Revenue', title="Category Mix", template="plotly_dark", hole=0.4)
                st.plotly_chart(fig_cat, use_container_width=True)

        # Monthly Trend with Forecast
        filtered_df['Month'] = filtered_df['Date'].dt.to_period('M').astype(str)
        monthly = filtered_df.groupby('Month')['Revenue'].sum().reset_index().sort_values('Month')
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=monthly['Month'], y=monthly['Revenue'], mode='lines+markers', name='Actual Revenue'))
        
        if len(monthly) >= 2:
            x = np.arange(len(monthly))
            y = monthly['Revenue'].values
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            
            # Forecast next month
            next_x = len(monthly)
            next_val = max(0, p(next_x))
            
            last_month = pd.to_datetime(monthly['Month'].iloc[-1])
            next_month = (last_month + pd.DateOffset(months=1)).strftime('%Y-%m')
            
            # Add line connecting last actual to forecast
            fig_trend.add_trace(go.Scatter(
                x=[monthly['Month'].iloc[-1], next_month],
                y=[monthly['Revenue'].iloc[-1], next_val],
                mode='lines+markers',
                line=dict(dash='dash', color='cyan'),
                name='Forecast'
            ))
            
        fig_trend.update_layout(title="Monthly Revenue Trend & Forecast", template="plotly_dark")
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Leaderboard
        st.subheader("🏆 Salesperson Leaderboard")
        leaderboard = filtered_df.groupby('Salesperson').agg({'Revenue': 'sum', 'Quantity': 'sum'}).reset_index().sort_values('Revenue', ascending=False)
        leaderboard['Rank'] = range(1, len(leaderboard) + 1)
        leaderboard['Revenue Formatted'] = leaderboard['Revenue'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(leaderboard[['Rank', 'Salesperson', 'Revenue Formatted', 'Quantity']], hide_index=True, use_container_width=True)
        
        # Download
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name='sales_report.csv',
            mime='text/csv',
        )
else:
    st.info("Please upload a CSV file to get started.")
    
    st.markdown("### Sample Format")
    st.code("""OrderID,Date,Product,Category,Region,Quantity,UnitPrice,Revenue
1001,2024-01-12,Laptop,Electronics,West,2,889.50,1779.00
1002,2024-01-22,Smartphone,Electronics,South,3,612.40,1837.20""", language="csv")
