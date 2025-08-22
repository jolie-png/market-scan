import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.scraper import CompetitorScraper
from modules.analyzer import CompetitorAnalyzer
from modules.visualizer import CompetitorVisualizer
from utils.helpers import format_currency
import time

# Page configuration
st.set_page_config(
    page_title="Market Intelligence",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'scraper' not in st.session_state:
    st.session_state.scraper = CompetitorScraper()
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = CompetitorAnalyzer()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = CompetitorVisualizer()

def find_competitor_websites(company_name):
    """Find competitor websites for a given company"""
    
    # Predefined competitor mappings for common companies
    competitor_db = {
        'salesforce': {
            'HubSpot': 'https://hubspot.com',
            'Pipedrive': 'https://pipedrive.com',
            'Zoho CRM': 'https://zoho.com/crm',
            'Microsoft Dynamics': 'https://dynamics.microsoft.com'
        },
        'hubspot': {
            'Salesforce': 'https://salesforce.com',
            'Marketo': 'https://marketo.com',
            'Pardot': 'https://pardot.com',
            'Mailchimp': 'https://mailchimp.com'
        },
        'slack': {
            'Microsoft Teams': 'https://teams.microsoft.com',
            'Discord': 'https://discord.com',
            'Zoom': 'https://zoom.us',
            'Google Meet': 'https://meet.google.com'
        },
        'zoom': {
            'Microsoft Teams': 'https://teams.microsoft.com',
            'Google Meet': 'https://meet.google.com',
            'Webex': 'https://webex.com',
            'GoToMeeting': 'https://gotomeeting.com'
        },
        'shopify': {
            'WooCommerce': 'https://woocommerce.com',
            'Magento': 'https://magento.com',
            'BigCommerce': 'https://bigcommerce.com',
            'Squarespace': 'https://squarespace.com'
        },
        'stripe': {
            'PayPal': 'https://paypal.com',
            'Square': 'https://square.com',
            'Adyen': 'https://adyen.com',
            'Braintree': 'https://braintreepayments.com'
        }
    }
    
    # Try to find competitors
    company_lower = company_name.lower()
    
    for key, competitors in competitor_db.items():
        if key in company_lower or company_lower in key:
            return competitors
    
    # Default tech competitors if no specific mapping found
    return {
        'Microsoft': 'https://microsoft.com',
        'Google': 'https://google.com',
        'Amazon': 'https://amazon.com',
        'Apple': 'https://apple.com'
    }

st.title("🔍 Market Intelligence Platform")
st.markdown("**Enter a company name to get comprehensive market analysis, competitor insights, and pricing analytics**")

# Simple input interface
company_name = st.text_input("Company Name", placeholder="e.g., Salesforce, HubSpot, Slack")

if st.button("🚀 Analyze Market", type="primary") and company_name:
    with st.spinner(f"Analyzing market for {company_name}..."):
        
        # Step 1: Find competitor websites
        st.info("🔍 Finding competitor websites...")
        competitor_urls = find_competitor_websites(company_name)
        
        if not competitor_urls:
            st.error("No competitor websites found. Try a different company name.")
            st.stop()
        
        st.success(f"Found {len(competitor_urls)} competitors")
        
        # Step 2: Scrape competitor data
        st.info("📊 Scraping competitor data...")
        all_data = []
        
        progress_bar = st.progress(0)
        for i, (comp_name, url) in enumerate(competitor_urls.items()):
            try:
                data = st.session_state.scraper.scrape_competitor(url, comp_name, "Technology")
                if data:
                    all_data.append(data)
                    st.write(f"✅ Scraped {comp_name}")
                else:
                    st.write(f"⚠️ Failed to scrape {comp_name}")
            except Exception as e:
                st.write(f"❌ Error with {comp_name}: {str(e)}")
            
            progress_bar.progress((i + 1) / len(competitor_urls))
            time.sleep(1)  # Rate limiting
        
        if not all_data:
            st.error("No competitor data could be scraped. Please try again.")
            st.stop()
        
        # Convert to DataFrame
        df_data = []
        for competitor in all_data:
            if competitor.get('products'):
                for product in competitor['products']:
                    row = competitor.copy()
                    row['product_name'] = product
                    row.pop('products', None)
                    df_data.append(row)
            else:
                row = competitor.copy()
                row['product_name'] = f"{competitor['company']} Service"
                row.pop('products', None)
                df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Step 3: Generate comprehensive analysis
        st.success("🤖 Generating AI insights...")
        
        # Display results
        st.markdown("---")
        st.header(f"📊 Market Analysis for {company_name}")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Competitors Found", len(df['company'].unique()))
        
        with col2:
            if 'price' in df.columns and not df['price'].isna().all():
                avg_price = df['price'].mean()
                st.metric("Average Price", format_currency(avg_price))
            else:
                st.metric("Average Price", "N/A")
        
        with col3:
            st.metric("Products/Services", len(df))
        
        with col4:
            categories = len(df['category'].unique()) if 'category' in df.columns else 1
            st.metric("Categories", categories)
        
        # Market overview visualization
        st.subheader("🗺️ Market Overview")
        market_fig = st.session_state.visualizer.create_market_overview(df)
        st.plotly_chart(market_fig, use_container_width=True)
        
        # Competitive positioning
        st.subheader("🎯 Competitive Positioning")
        pos_fig = st.session_state.visualizer.create_competitor_map(df)
        st.plotly_chart(pos_fig, use_container_width=True)
        
        # Pricing analysis (if available)
        if 'price' in df.columns and not df['price'].isna().all():
            st.subheader("💰 Pricing Analysis")
            price_fig = st.session_state.visualizer.create_pricing_analysis(df)
            st.plotly_chart(price_fig, use_container_width=True)
        
        # AI-powered insights
        st.subheader("🧠 AI Market Insights")
        try:
            insights = st.session_state.analyzer.generate_competitive_insights(df)
            positioning = st.session_state.analyzer.analyze_competitive_positioning(df)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if insights.get('opportunities'):
                    st.success("🚀 **Market Opportunities**")
                    for opp in insights['opportunities'][:5]:
                        st.write(f"• {opp}")
                
                if positioning and positioning.get('market_opportunities'):
                    st.success("💎 **Strategic Opportunities**")
                    for opp in positioning['market_opportunities'][:3]:
                        st.write(f"• {opp}")
            
            with col2:
                if insights.get('threats'):
                    st.warning("⚠️ **Competitive Threats**")
                    for threat in insights['threats'][:5]:
                        st.write(f"• {threat}")
                
                if positioning and positioning.get('competitive_threats'):
                    st.warning("🎯 **Strategic Threats**")
                    for threat in positioning['competitive_threats'][:3]:
                        st.write(f"• {threat}")
            
            # Market analysis summary
            if positioning and positioning.get('pricing_analysis'):
                st.info("📈 **Pricing Strategy Analysis**")
                st.write(positioning['pricing_analysis'])
                
        except Exception as e:
            st.error(f"AI analysis failed: {str(e)}")
        
        # Competitor details table
        st.subheader("🏢 Competitor Details")
        display_df = df[['company', 'product_name', 'price', 'category']].copy()
        if 'price' in display_df.columns:
            display_df['price'] = display_df['price'].apply(lambda x: format_currency(x) if pd.notna(x) else 'N/A')
        
        st.dataframe(display_df, use_container_width=True)
        
        # Export option
        st.subheader("📤 Export Results")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download Full Report (CSV)",
            data=csv,
            file_name=f"{company_name}_market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Market Intelligence Platform | Enter any company name to get instant competitive analysis"
    "</div>", 
    unsafe_allow_html=True
)