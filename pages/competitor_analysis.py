import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_competitor_analysis():
    """Render the competitor analysis page"""
    st.title("🏢 Competitor Analysis")
    
    # Get data
    data = st.session_state.data_manager.get_all_data()
    
    if data.empty:
        st.info("No competitor data available. Please add competitors in the Data Management section.")
        return
    
    # Sidebar filters
    st.sidebar.subheader("🔍 Filters")
    
    # Company filter
    companies = ['All'] + sorted(data['company'].unique().tolist())
    selected_company = st.sidebar.selectbox("Select Company", companies)
    
    # Category filter
    if 'category' in data.columns:
        categories = ['All'] + sorted(data['category'].unique().tolist())
        selected_category = st.sidebar.selectbox("Select Category", categories)
    else:
        selected_category = 'All'
    
    # Price range filter
    if 'price' in data.columns and not data['price'].isna().all():
        price_data = data.dropna(subset=['price'])
        min_price, max_price = float(price_data['price'].min()), float(price_data['price'].max())
        price_range = st.sidebar.slider(
            "Price Range", 
            min_price, max_price, 
            (min_price, max_price),
            step=1.0
        )
    else:
        price_range = None
    
    # Apply filters
    filtered_data = data.copy()
    
    if selected_company != 'All':
        filtered_data = filtered_data[filtered_data['company'] == selected_company]
    
    if selected_category != 'All':
        filtered_data = filtered_data[filtered_data['category'] == selected_category]
    
    if price_range and 'price' in filtered_data.columns:
        filtered_data = filtered_data[
            (filtered_data['price'] >= price_range[0]) & 
            (filtered_data['price'] <= price_range[1])
        ]
    
    # Display filtered results count
    st.info(f"Showing {len(filtered_data)} out of {len(data)} competitors")
    
    # Main analysis sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🎯 Positioning", "📋 Detailed Analysis", "🤖 AI Insights"])
    
    with tab1:
        render_overview_tab(filtered_data)
    
    with tab2:
        render_positioning_tab(filtered_data)
    
    with tab3:
        render_detailed_analysis_tab(filtered_data)
    
    with tab4:
        render_ai_insights_tab(filtered_data)

def render_overview_tab(data):
    """Render the overview tab"""
    if data.empty:
        st.warning("No data matches the current filters.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Competitors", len(data['company'].unique()))
    
    with col2:
        if 'price' in data.columns:
            avg_price = data['price'].mean()
            st.metric("Avg Price", f"${avg_price:.2f}" if pd.notna(avg_price) else "N/A")
        else:
            st.metric("Avg Price", "N/A")
    
    with col3:
        if 'category' in data.columns:
            st.metric("Categories", len(data['category'].unique()))
        else:
            st.metric("Categories", "N/A")
    
    with col4:
        recent_count = len(data[data['last_updated'] >= pd.Timestamp.now() - pd.Timedelta(days=7)])
        st.metric("Recent Updates", recent_count)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Competitor Distribution")
        company_counts = data['company'].value_counts()
        fig = px.bar(
            x=company_counts.values,
            y=company_counts.index,
            orientation='h',
            title="Products per Competitor",
            labels={'x': 'Number of Products', 'y': 'Company'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Category Breakdown")
        if 'category' in data.columns:
            category_counts = data['category'].value_counts()
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Market Categories"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category information not available")
    
    # Price analysis
    if 'price' in data.columns and not data['price'].isna().all():
        st.subheader("💰 Price Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price distribution
            price_data = data.dropna(subset=['price'])
            fig = px.histogram(
                price_data, 
                x='price',
                nbins=20,
                title="Price Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Price by category
            if 'category' in data.columns:
                fig = px.box(
                    price_data,
                    x='category',
                    y='price',
                    title="Price Distribution by Category"
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

def render_positioning_tab(data):
    """Render the competitive positioning tab"""
    st.subheader("🎯 Competitive Positioning Map")
    
    if data.empty:
        st.warning("No data available for positioning analysis.")
        return
    
    # Create positioning map
    positioning_fig = st.session_state.visualizer.create_competitor_map(data)
    st.plotly_chart(positioning_fig, use_container_width=True)
    
    # Feature comparison matrix
    st.subheader("🔍 Feature Comparison")
    feature_fig = st.session_state.visualizer.create_feature_comparison(data)
    st.plotly_chart(feature_fig, use_container_width=True)
    
    # Competitive strengths analysis
    if len(data) > 1:
        st.subheader("💪 Competitive Strengths Analysis")
        
        # Mock competitive analysis (in real scenario, extract from content)
        companies = data['company'].unique()[:5]  # Top 5 companies
        strengths = ['Market Presence', 'Product Quality', 'Pricing', 'Innovation', 'Customer Service']
        
        # Generate mock scores
        import numpy as np
        np.random.seed(42)
        scores = np.random.randint(1, 6, size=(len(companies), len(strengths)))
        
        # Create radar chart for each company
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set3
        for i, company in enumerate(companies):
            fig.add_trace(go.Scatterpolar(
                r=scores[i],
                theta=strengths,
                fill='toself',
                name=company,
                line_color=colors[i % len(colors)]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )),
            showlegend=True,
            title="Competitive Strengths Radar Chart",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_detailed_analysis_tab(data):
    """Render detailed analysis tab"""
    st.subheader("📋 Detailed Competitor Profiles")
    
    if data.empty:
        st.warning("No competitors found matching the current filters.")
        return
    
    # Company selector for detailed view
    companies = sorted(data['company'].unique())
    selected_company = st.selectbox("Select company for detailed analysis:", companies)
    
    company_data = data[data['company'] == selected_company]
    
    if not company_data.empty:
        # Company overview
        st.subheader(f"🏢 {selected_company} Profile")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Products/Services:** {len(company_data)}")
            categories = company_data['category'].unique() if 'category' in company_data.columns else ['N/A']
            st.write(f"**Categories:** {', '.join(categories)}")
        
        with col2:
            if 'price' in company_data.columns and not company_data['price'].isna().all():
                avg_price = company_data['price'].mean()
                min_price = company_data['price'].min()
                max_price = company_data['price'].max()
                st.write(f"**Avg Price:** ${avg_price:.2f}")
                st.write(f"**Price Range:** ${min_price:.2f} - ${max_price:.2f}")
            else:
                st.write("**Price:** Not available")
        
        with col3:
            last_update = company_data['last_updated'].max()
            st.write(f"**Last Updated:** {last_update.strftime('%Y-%m-%d')}")
            source_urls = company_data['source_url'].unique()
            st.write(f"**Sources:** {len(source_urls)} URL(s)")
        
        # Products/Services table
        st.subheader("📦 Products/Services")
        display_columns = ['product_name', 'category', 'price', 'last_updated']
        available_columns = [col for col in display_columns if col in company_data.columns]
        
        if available_columns:
            display_data = company_data[available_columns].copy()
            if 'price' in display_data.columns:
                display_data['price'] = display_data['price'].apply(
                    lambda x: f"${x:.2f}" if pd.notna(x) else "N/A"
                )
            if 'last_updated' in display_data.columns:
                display_data['last_updated'] = display_data['last_updated'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(display_data, use_container_width=True)
        
        # Content analysis
        if 'summary' in company_data.columns or 'content' in company_data.columns:
            st.subheader("📄 Content Analysis")
            
            for idx, (_, row) in enumerate(company_data.iterrows()):
                with st.expander(f"{row.get('product_name', f'Product {idx+1}')}"):
                    if 'summary' in row and pd.notna(row['summary']):
                        st.write("**AI Summary:**")
                        st.write(row['summary'])
                    
                    if 'content' in row and pd.notna(row['content']):
                        st.write("**Raw Content Preview:**")
                        content_preview = row['content'][:500] + "..." if len(row['content']) > 500 else row['content']
                        st.text(content_preview)
                    
                    if 'source_url' in row:
                        st.write(f"**Source:** [Visit Site]({row['source_url']})")

def render_ai_insights_tab(data):
    """Render AI insights tab"""
    st.subheader("🤖 AI-Powered Competitive Insights")
    
    if data.empty:
        st.warning("No data available for AI analysis.")
        return
    
    # Generate insights button
    if st.button("🔮 Generate Competitive Intelligence", type="primary"):
        with st.spinner("Analyzing competitive landscape with AI..."):
            # Get competitive positioning analysis
            positioning_analysis = st.session_state.analyzer.analyze_competitive_positioning(data)
            
            if positioning_analysis and "error" not in positioning_analysis:
                st.success("✅ Analysis Complete!")
                
                # Display market segments
                if 'market_segments' in positioning_analysis:
                    st.subheader("🎯 Market Segments")
                    segments = positioning_analysis['market_segments']
                    if segments:
                        for segment in segments:
                            st.write(f"• {segment}")
                    else:
                        st.info("No distinct market segments identified")
                
                # Display pricing analysis
                if 'pricing_analysis' in positioning_analysis:
                    st.subheader("💰 Pricing Strategy Analysis")
                    st.write(positioning_analysis['pricing_analysis'])
                
                # Display key differentiators
                if 'key_differentiators' in positioning_analysis:
                    st.subheader("🔑 Key Differentiators")
                    differentiators = positioning_analysis['key_differentiators']
                    if differentiators:
                        for diff in differentiators:
                            st.write(f"• {diff}")
                
                # Display opportunities and threats in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'market_opportunities' in positioning_analysis:
                        st.subheader("🚀 Market Opportunities")
                        opportunities = positioning_analysis['market_opportunities']
                        if opportunities:
                            for opp in opportunities:
                                st.success(f"• {opp}")
                
                with col2:
                    if 'competitive_threats' in positioning_analysis:
                        st.subheader("⚠️ Competitive Threats")
                        threats = positioning_analysis['competitive_threats']
                        if threats:
                            for threat in threats:
                                st.warning(f"• {threat}")
            else:
                error_msg = positioning_analysis.get('error', 'Unknown error occurred') if positioning_analysis else 'Analysis failed'
                st.error(f"Failed to generate insights: {error_msg}")
    
    # Trend analysis
    st.subheader("📈 Trend Analysis")
    
    if st.button("📊 Analyze Market Trends"):
        with st.spinner("Identifying market trends..."):
            trends = st.session_state.analyzer.identify_trends(data)
            
            if trends:
                # Pricing trends
                if trends.get('pricing_trends'):
                    st.subheader("💹 Pricing Trends")
                    for trend in trends['pricing_trends']:
                        trend_icon = "📈" if trend.get('trend') == 'increasing' else "📉"
                        st.write(f"{trend_icon} {trend.get('description', 'No description available')}")
                
                # Market trends
                if trends.get('market_trends'):
                    st.subheader("🌍 Market Trends")
                    for trend in trends['market_trends']:
                        st.info(f"📊 {trend.get('description', 'No description available')}")
                
                # Feature trends (AI-generated)
                if trends.get('feature_trends'):
                    st.subheader("⚡ Feature Trends")
                    for trend in trends['feature_trends']:
                        st.write(f"🔧 {trend}")
                
                # Strategic insights (AI-generated)
                if trends.get('strategic_insights'):
                    st.subheader("💡 Strategic Insights")
                    for insight in trends['strategic_insights']:
                        st.write(f"🎯 {insight}")
            else:
                st.info("No significant trends identified in the current data.")
    
    # Export insights
    st.subheader("📤 Export Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate Report"):
            with st.spinner("Generating comprehensive report..."):
                # This would generate a comprehensive PDF/HTML report
                st.info("Report generation feature coming soon!")
    
    with col2:
        if st.button("📊 Export Data"):
            csv_data = st.session_state.data_manager.export_data('csv')
            if csv_data:
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"competitor_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
