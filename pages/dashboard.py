import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def render_dashboard():
    """Render the main dashboard page"""
    st.title("📊 Market Intelligence Dashboard")
    
    # Get data
    data_manager = st.session_state.data_manager
    data = data_manager.get_all_data()
    
    # Summary statistics
    stats = data_manager.get_summary_stats()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Competitors", 
            stats.get('total_competitors', 0),
            help="Number of unique competitors tracked"
        )
    
    with col2:
        st.metric(
            "Products/Services", 
            stats.get('total_products', 0),
            help="Total number of products/services tracked"
        )
    
    with col3:
        st.metric(
            "Categories", 
            stats.get('categories', 0),
            help="Number of different market categories"
        )
    
    with col4:
        avg_price = stats.get('avg_price', 0)
        st.metric(
            "Avg Price", 
            f"${avg_price:.2f}" if avg_price > 0 else "N/A",
            help="Average price across all tracked products"
        )
    
    if not data.empty:
        # Market overview visualization
        st.subheader("📈 Market Overview")
        market_fig = st.session_state.visualizer.create_market_overview(data)
        st.plotly_chart(market_fig, use_container_width=True)
        
        # Two-column layout for additional insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏢 Top Competitors")
            if 'company' in data.columns:
                company_counts = data['company'].value_counts().head(10)
                fig = px.bar(
                    x=company_counts.values,
                    y=company_counts.index,
                    orientation='h',
                    title="Products/Services per Competitor"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Category Distribution")
            if 'category' in data.columns:
                category_counts = data['category'].value_counts()
                fig = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Market Share by Category"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.subheader("🔥 Recent Market Activity")
        recent_data = data_manager.get_recent_updates(days=30)
        
        if not recent_data.empty:
            st.write(f"**{len(recent_data)} updates** in the last 30 days")
            
            # Display recent updates in expandable cards
            for idx, (_, row) in enumerate(recent_data.head(5).iterrows()):
                with st.expander(f"{row['company']} - {row.get('product_name', 'Service')} ({row['last_updated'].strftime('%m/%d/%Y')})"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if 'summary' in row and pd.notna(row['summary']):
                            st.write("**Summary:**")
                            st.write(row['summary'][:300] + "..." if len(row['summary']) > 300 else row['summary'])
                        else:
                            st.write("**Content Preview:**")
                            content = row.get('content', 'No content available')
                            st.write(content[:200] + "..." if len(content) > 200 else content)
                    
                    with col2:
                        st.write(f"**Category:** {row.get('category', 'N/A')}")
                        if 'price' in row and pd.notna(row['price']):
                            st.write(f"**Price:** ${row['price']:.2f}")
                        if 'source_url' in row:
                            st.write(f"**Source:** [Link]({row['source_url']})")
        else:
            st.info("No recent updates found. Add competitors or refresh existing data.")
        
        # Competitive insights
        st.subheader("🧠 AI-Powered Insights")
        
        if st.button("🔮 Generate Market Insights"):
            with st.spinner("Analyzing competitive landscape..."):
                insights = st.session_state.analyzer.generate_competitive_insights(data)
                
                if insights:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if insights.get('opportunities'):
                            st.success("**🚀 Opportunities**")
                            for opp in insights['opportunities']:
                                st.write(f"• {opp}")
                        
                        if insights.get('strengths'):
                            st.info("**💪 Market Strengths**")
                            for strength in insights['strengths']:
                                st.write(f"• {strength}")
                    
                    with col2:
                        if insights.get('threats'):
                            st.warning("**⚠️ Threats**")
                            for threat in insights['threats']:
                                st.write(f"• {threat}")
                        
                        if insights.get('weaknesses'):
                            st.error("**🎯 Areas to Watch**")
                            for weakness in insights['weaknesses']:
                                st.write(f"• {weakness}")
    else:
        # Empty state
        st.info("👋 Welcome to the Market Intelligence Platform!")
        st.markdown("""
        **Get started by:**
        1. 📝 Go to 'Data Management' to add your first competitor
        2. 🔍 Add competitor URLs to start tracking
        3. 📊 Return here to see your market intelligence dashboard
        
        **What you'll get:**
        - 🏢 Competitor tracking and analysis
        - 💰 Pricing intelligence and trends
        - 📈 Market opportunity identification
        - 🤖 AI-powered competitive insights
        """)
        
        # Sample competitor suggestions
        st.subheader("💡 Need inspiration? Try these sample competitors:")
        sample_competitors = [
            {"name": "Salesforce", "url": "https://salesforce.com", "category": "CRM"},
            {"name": "HubSpot", "url": "https://hubspot.com", "category": "Marketing"},
            {"name": "Slack", "url": "https://slack.com", "category": "Communication"},
            {"name": "Zoom", "url": "https://zoom.us", "category": "Video Conferencing"}
        ]
        
        for comp in sample_competitors:
            st.write(f"• **{comp['name']}** - {comp['category']} - `{comp['url']}`")
