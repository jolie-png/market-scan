import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from modules.scraper import CompetitorScraper
from modules.analyzer import CompetitorAnalyzer
from modules.visualizer import CompetitorVisualizer
from modules.data_manager import DataManager
from utils.helpers import format_currency, safe_url_parse

# Page configuration
st.set_page_config(
    page_title="Market Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'scraper' not in st.session_state:
    st.session_state.scraper = CompetitorScraper()
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = CompetitorAnalyzer()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = CompetitorVisualizer()

# Sidebar navigation
st.sidebar.title("Market Intelligence Platform")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.selectbox(
    "Navigate to:",
    ["Dashboard", "Competitor Analysis", "Pricing Comparison", "Trend Analytics", "Data Management"]
)

# Quick actions sidebar
st.sidebar.markdown("### Quick Actions")
if st.sidebar.button("🔄 Refresh All Data"):
    with st.spinner("Refreshing competitor data..."):
        st.session_state.data_manager.refresh_all_data()
    st.sidebar.success("Data refreshed!")

if st.sidebar.button("📥 Export Data"):
    data = st.session_state.data_manager.get_all_data()
    if not data.empty:
        csv = data.to_csv(index=False)
        st.sidebar.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"market_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.sidebar.warning("No data available to export")

# Main content based on selected page
if page == "Dashboard":
    st.title("📊 Market Intelligence Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    data = st.session_state.data_manager.get_all_data()
    
    with col1:
        total_competitors = len(data['company'].unique()) if not data.empty else 0
        st.metric("Total Competitors", total_competitors)
    
    with col2:
        total_products = len(data) if not data.empty else 0
        st.metric("Products Tracked", total_products)
    
    with col3:
        recent_updates = len(data[data['last_updated'] >= datetime.now() - timedelta(days=7)]) if not data.empty else 0
        st.metric("Recent Updates", recent_updates)
    
    with col4:
        avg_price = data['price'].mean() if not data.empty and 'price' in data.columns else 0
        st.metric("Avg Price", format_currency(avg_price))
    
    if not data.empty:
        # Market overview chart
        st.subheader("Market Overview")
        fig = st.session_state.visualizer.create_market_overview(data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent competitor activities
        st.subheader("Recent Competitor Activities")
        recent_data = data.sort_values('last_updated', ascending=False).head(10)
        for _, row in recent_data.iterrows():
            with st.expander(f"{row['company']} - {row['product_name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Price:** {format_currency(row.get('price', 0))}")
                    st.write(f"**Category:** {row.get('category', 'N/A')}")
                with col2:
                    st.write(f"**Last Updated:** {row['last_updated'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Source:** {row.get('source_url', 'N/A')}")
                
                if 'summary' in row and pd.notna(row['summary']):
                    st.write(f"**Summary:** {row['summary']}")
    else:
        st.info("No competitor data available. Use the 'Data Management' section to add competitor URLs.")

elif page == "Competitor Analysis":
    from pages.competitor_analysis import render_competitor_analysis
    render_competitor_analysis()

elif page == "Pricing Comparison":
    from pages.pricing_comparison import render_pricing_comparison
    render_pricing_comparison()

elif page == "Trend Analytics":
    from pages.trend_analytics import render_trend_analytics
    render_trend_analytics()

elif page == "Data Management":
    st.title("🔧 Data Management")
    
    # Add new competitor
    st.subheader("Add New Competitor")
    with st.form("add_competitor"):
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name")
            competitor_url = st.text_input("Competitor URL")
        with col2:
            category = st.text_input("Category")
            notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Add Competitor")
        if submitted and company_name and competitor_url:
            if safe_url_parse(competitor_url):
                with st.spinner(f"Scraping {company_name}..."):
                    try:
                        result = st.session_state.scraper.scrape_competitor(competitor_url, company_name, category)
                        if result:
                            st.session_state.data_manager.add_competitor_data(result)
                            st.success(f"Successfully added {company_name}!")
                            st.rerun()
                        else:
                            st.error("Failed to scrape competitor data. Please check the URL.")
                    except Exception as e:
                        st.error(f"Error scraping competitor: {str(e)}")
            else:
                st.error("Please enter a valid URL")
    
    # Current competitors
    st.subheader("Current Competitors")
    data = st.session_state.data_manager.get_all_data()
    if not data.empty:
        # Display competitors table
        display_data = data[['company', 'product_name', 'category', 'price', 'last_updated']].copy()
        display_data['price'] = display_data['price'].apply(lambda x: format_currency(x) if pd.notna(x) else 'N/A')
        display_data['last_updated'] = display_data['last_updated'].dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(display_data, use_container_width=True)
        
        # Bulk operations
        st.subheader("Bulk Operations")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh All Competitor Data"):
                with st.spinner("Refreshing all competitor data..."):
                    st.session_state.data_manager.refresh_all_data()
                st.success("All data refreshed!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All Data"):
                if st.checkbox("I understand this will delete all data"):
                    st.session_state.data_manager.clear_all_data()
                    st.success("All data cleared!")
                    st.rerun()
    else:
        st.info("No competitors added yet. Add your first competitor above!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Market Intelligence Platform | Powered by AI & Web Scraping"
    "</div>", 
    unsafe_allow_html=True
)
