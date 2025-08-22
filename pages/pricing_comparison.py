import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def render_pricing_comparison():
    """Render the pricing comparison page"""
    st.title("💰 Pricing Comparison Analysis")
    
    # Get data
    data = st.session_state.data_manager.get_all_data()
    
    if data.empty:
        st.info("No competitor data available. Please add competitors in the Data Management section.")
        return
    
    # Check if price data exists
    if 'price' not in data.columns or data['price'].isna().all():
        st.warning("No pricing data available. Add competitors with pricing information to see analysis.")
        return
    
    price_data = data.dropna(subset=['price'])
    
    if price_data.empty:
        st.warning("No valid pricing data found.")
        return
    
    # Sidebar filters
    st.sidebar.subheader("🔍 Pricing Filters")
    
    # Category filter
    if 'category' in price_data.columns:
        categories = ['All'] + sorted(price_data['category'].unique().tolist())
        selected_category = st.sidebar.selectbox("Select Category", categories)
        
        if selected_category != 'All':
            price_data = price_data[price_data['category'] == selected_category]
    
    # Company filter
    companies = ['All'] + sorted(price_data['company'].unique().tolist())
    selected_companies = st.sidebar.multiselect(
        "Select Companies (leave empty for all)", 
        [comp for comp in companies if comp != 'All']
    )
    
    if selected_companies:
        price_data = price_data[price_data['company'].isin(selected_companies)]
    
    # Price range selector
    min_price, max_price = float(price_data['price'].min()), float(price_data['price'].max())
    price_range = st.sidebar.slider(
        "Price Range",
        min_price, max_price,
        (min_price, max_price),
        step=1.0
    )
    
    price_data = price_data[
        (price_data['price'] >= price_range[0]) & 
        (price_data['price'] <= price_range[1])
    ]
    
    st.info(f"Analyzing {len(price_data)} products with pricing data")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analysis", "🏆 Comparison", "💡 Insights"])
    
    with tab1:
        render_pricing_overview(price_data)
    
    with tab2:
        render_pricing_analysis(price_data)
    
    with tab3:
        render_pricing_comparison_tab(price_data)
    
    with tab4:
        render_pricing_insights(price_data)

def render_pricing_overview(price_data):
    """Render pricing overview tab"""
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_price = price_data['price'].mean()
        st.metric("Average Price", f"${avg_price:.2f}")
    
    with col2:
        median_price = price_data['price'].median()
        st.metric("Median Price", f"${median_price:.2f}")
    
    with col3:
        min_price = price_data['price'].min()
        st.metric("Lowest Price", f"${min_price:.2f}")
    
    with col4:
        max_price = price_data['price'].max()
        st.metric("Highest Price", f"${max_price:.2f}")
    
    # Price distribution visualization
    st.subheader("📊 Price Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram
        fig = px.histogram(
            price_data,
            x='price',
            nbins=20,
            title="Price Distribution",
            labels={'price': 'Price ($)', 'count': 'Number of Products'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Box plot by category
        if 'category' in price_data.columns and len(price_data['category'].unique()) > 1:
            fig = px.box(
                price_data,
                x='category',
                y='price',
                title="Price Distribution by Category"
            )
            fig.update_xaxes(tickangle=45)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Overall box plot
            fig = go.Figure()
            fig.add_trace(go.Box(y=price_data['price'], name='All Products'))
            fig.update_layout(title="Price Distribution", height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Price statistics table
    st.subheader("📋 Pricing Statistics")
    
    if 'category' in price_data.columns:
        stats_by_category = price_data.groupby('category')['price'].agg([
            'count', 'mean', 'median', 'min', 'max', 'std'
        ]).round(2)
        stats_by_category.columns = ['Count', 'Mean ($)', 'Median ($)', 'Min ($)', 'Max ($)', 'Std Dev ($)']
        st.dataframe(stats_by_category, use_container_width=True)
    else:
        overall_stats = price_data['price'].describe()
        stats_df = pd.DataFrame({
            'Statistic': ['Count', 'Mean', 'Std Dev', 'Min', '25%', 'Median', '75%', 'Max'],
            'Value ($)': [f"${val:.2f}" if val != overall_stats['count'] else f"{val:.0f}" for val in overall_stats]
        })
        st.dataframe(stats_df, use_container_width=True)

def render_pricing_analysis(price_data):
    """Render detailed pricing analysis"""
    st.subheader("📈 Detailed Pricing Analysis")
    
    # Create comprehensive pricing dashboard
    pricing_fig = st.session_state.visualizer.create_pricing_analysis(price_data)
    st.plotly_chart(pricing_fig, use_container_width=True)
    
    # Price trends over time
    if 'last_updated' in price_data.columns:
        st.subheader("📅 Price Trends Over Time")
        
        # Group by date and calculate average price
        price_data['update_date'] = price_data['last_updated'].dt.date
        daily_avg_price = price_data.groupby('update_date')['price'].mean().reset_index()
        
        if len(daily_avg_price) > 1:
            fig = px.line(
                daily_avg_price,
                x='update_date',
                y='price',
                title='Average Price Trend',
                labels={'update_date': 'Date', 'price': 'Average Price ($)'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Price trend analysis
            price_change = daily_avg_price['price'].iloc[-1] - daily_avg_price['price'].iloc[0]
            price_change_pct = (price_change / daily_avg_price['price'].iloc[0]) * 100
            
            if abs(price_change_pct) > 5:  # Significant change
                trend_direction = "📈 increasing" if price_change > 0 else "📉 decreasing"
                st.info(f"Price trend is {trend_direction} by {abs(price_change_pct):.1f}% (${abs(price_change):.2f})")
            else:
                st.info("🔄 Prices are relatively stable with minimal fluctuation")
        else:
            st.info("Not enough historical data to show price trends")
    
    # Price competitiveness analysis
    st.subheader("🏆 Price Competitiveness Analysis")
    
    # Calculate price percentiles
    price_data_copy = price_data.copy()
    price_data_copy['price_percentile'] = price_data_copy['price'].rank(pct=True) * 100
    price_data_copy['competitiveness'] = pd.cut(
        price_data_copy['price_percentile'],
        bins=[0, 25, 50, 75, 100],
        labels=['Very Competitive (Bottom 25%)', 'Competitive (25-50%)', 
               'Premium (50-75%)', 'Very Premium (Top 25%)']
    )
    
    competitiveness_counts = price_data_copy['competitiveness'].value_counts()
    
    fig = px.bar(
        x=competitiveness_counts.values,
        y=competitiveness_counts.index,
        orientation='h',
        title='Price Competitiveness Distribution',
        labels={'x': 'Number of Products', 'y': 'Price Category'},
        color=competitiveness_counts.values,
        color_continuous_scale='RdYlBu_r'
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def render_pricing_comparison_tab(price_data):
    """Render side-by-side pricing comparison"""
    st.subheader("🏆 Side-by-Side Pricing Comparison")
    
    # Company comparison
    if len(price_data['company'].unique()) > 1:
        st.subheader("🏢 Company Price Comparison")
        
        company_stats = price_data.groupby('company')['price'].agg([
            'count', 'mean', 'min', 'max'
        ]).round(2)
        company_stats.columns = ['Products', 'Avg Price', 'Min Price', 'Max Price']
        company_stats = company_stats.sort_values('Avg Price')
        
        # Format prices
        for col in ['Avg Price', 'Min Price', 'Max Price']:
            company_stats[col] = company_stats[col].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(company_stats, use_container_width=True)
        
        # Visual comparison
        company_avg_prices = price_data.groupby('company')['price'].mean().sort_values(ascending=True)
        
        fig = px.bar(
            x=company_avg_prices.values,
            y=company_avg_prices.index,
            orientation='h',
            title='Average Price by Company',
            labels={'x': 'Average Price ($)', 'y': 'Company'},
            color=company_avg_prices.values,
            color_continuous_scale='RdYlBu'
        )
        fig.update_layout(height=max(300, len(company_avg_prices) * 30))
        st.plotly_chart(fig, use_container_width=True)
    
    # Category comparison
    if 'category' in price_data.columns and len(price_data['category'].unique()) > 1:
        st.subheader("🏷️ Category Price Comparison")
        
        category_stats = price_data.groupby('category')['price'].agg([
            'count', 'mean', 'min', 'max'
        ]).round(2)
        category_stats.columns = ['Products', 'Avg Price', 'Min Price', 'Max Price']
        category_stats = category_stats.sort_values('Avg Price')
        
        # Format prices
        for col in ['Avg Price', 'Min Price', 'Max Price']:
            category_stats[col] = category_stats[col].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(category_stats, use_container_width=True)
        
        # Visual comparison
        fig = px.violin(
            price_data,
            x='category',
            y='price',
            title='Price Distribution by Category',
            box=True
        )
        fig.update_xaxes(tickangle=45)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top/Bottom performers
    st.subheader("🥇 Price Leaders and Laggards")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🔥 Most Competitive (Lowest Prices)**")
        lowest_prices = price_data.nsmallest(5, 'price')[['company', 'product_name', 'price', 'category']]
        lowest_prices['price'] = lowest_prices['price'].apply(lambda x: f"${x:.2f}")
        st.dataframe(lowest_prices, use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**💎 Premium Options (Highest Prices)**")
        highest_prices = price_data.nlargest(5, 'price')[['company', 'product_name', 'price', 'category']]
        highest_prices['price'] = highest_prices['price'].apply(lambda x: f"${x:.2f}")
        st.dataframe(highest_prices, use_container_width=True, hide_index=True)

def render_pricing_insights(price_data):
    """Render pricing insights and recommendations"""
    st.subheader("💡 Pricing Insights & Recommendations")
    
    # Generate pricing insights
    insights = generate_pricing_insights(price_data)
    
    # Display insights in organized sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("🚀 **Opportunities**")
        for opportunity in insights['opportunities']:
            st.write(f"• {opportunity}")
        
        st.info("💪 **Competitive Advantages**")
        for advantage in insights['advantages']:
            st.write(f"• {advantage}")
    
    with col2:
        st.warning("⚠️ **Market Threats**")
        for threat in insights['threats']:
            st.write(f"• {threat}")
        
        st.error("🎯 **Areas of Concern**")
        for concern in insights['concerns']:
            st.write(f"• {concern}")
    
    # Pricing recommendations
    st.subheader("📋 Pricing Strategy Recommendations")
    
    recommendations = generate_pricing_recommendations(price_data)
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"**{i}. {rec['title']}**")
        st.write(rec['description'])
        if 'action' in rec:
            st.write(f"*Action:* {rec['action']}")
        st.write("---")
    
    # Market positioning analysis
    st.subheader("📊 Market Positioning Analysis")
    
    if st.button("🔮 Generate AI-Powered Pricing Analysis"):
        with st.spinner("Analyzing pricing strategy with AI..."):
            # This would use the OpenAI integration for deeper analysis
            try:
                ai_analysis = st.session_state.analyzer.analyze_competitive_positioning(price_data)
                
                if ai_analysis and "error" not in ai_analysis:
                    if 'pricing_analysis' in ai_analysis:
                        st.write("**🤖 AI Analysis:**")
                        st.write(ai_analysis['pricing_analysis'])
                    
                    if 'market_opportunities' in ai_analysis:
                        st.write("**🎯 AI-Identified Opportunities:**")
                        for opp in ai_analysis['market_opportunities']:
                            st.success(f"• {opp}")
                else:
                    st.warning("AI analysis not available. Check OpenAI API configuration.")
            except Exception as e:
                st.error(f"Error in AI analysis: {str(e)}")

def generate_pricing_insights(price_data):
    """Generate pricing insights based on data analysis"""
    insights = {
        'opportunities': [],
        'threats': [],
        'advantages': [],
        'concerns': []
    }
    
    # Basic statistical analysis
    mean_price = price_data['price'].mean()
    median_price = price_data['price'].median()
    std_price = price_data['price'].std()
    
    # Price spread analysis
    price_range = price_data['price'].max() - price_data['price'].min()
    cv = std_price / mean_price if mean_price > 0 else 0  # Coefficient of variation
    
    # Generate insights based on analysis
    if cv > 0.5:
        insights['opportunities'].append("High price variance indicates market fragmentation - opportunity for strategic positioning")
    
    if median_price < mean_price * 0.8:
        insights['opportunities'].append("Price distribution skewed toward lower end - premium positioning opportunity exists")
    
    if price_range > mean_price * 2:
        insights['threats'].append("Extreme price competition exists in the market")
    
    # Category-based insights
    if 'category' in price_data.columns and len(price_data['category'].unique()) > 1:
        category_means = price_data.groupby('category')['price'].mean()
        highest_cat = category_means.idxmax()
        lowest_cat = category_means.idxmin()
        
        if category_means[highest_cat] > category_means[lowest_cat] * 2:
            insights['opportunities'].append(f"Significant pricing gap between {highest_cat} and {lowest_cat} categories")
    
    # Company-based insights
    if len(price_data['company'].unique()) > 2:
        company_means = price_data.groupby('company')['price'].mean()
        market_leaders = company_means[company_means > company_means.quantile(0.75)]
        
        if len(market_leaders) < len(company_means) * 0.3:
            insights['opportunities'].append("Market dominated by few high-priced players - disruption opportunity exists")
    
    return insights

def generate_pricing_recommendations(price_data):
    """Generate actionable pricing recommendations"""
    recommendations = []
    
    mean_price = price_data['price'].mean()
    median_price = price_data['price'].median()
    
    # Market positioning recommendation
    if mean_price > median_price * 1.2:
        recommendations.append({
            'title': 'Consider Value-Based Positioning',
            'description': 'The market shows premium pricing potential with average prices significantly above median.',
            'action': 'Focus on communicating unique value propositions to justify premium pricing.'
        })
    
    # Competitive pricing recommendation
    low_price_threshold = price_data['price'].quantile(0.25)
    high_price_threshold = price_data['price'].quantile(0.75)
    
    recommendations.append({
        'title': 'Competitive Price Range Analysis',
        'description': f'Competitive sweet spot appears to be between ${low_price_threshold:.2f} and ${high_price_threshold:.2f}.',
        'action': 'Consider positioning within or strategically outside this range based on value proposition.'
    })
    
    # Market gap analysis
    if 'category' in price_data.columns:
        category_counts = price_data['category'].value_counts()
        underserved_categories = category_counts[category_counts < category_counts.median()]
        
        if not underserved_categories.empty:
            recommendations.append({
                'title': 'Market Gap Opportunity',
                'description': f'Categories like {", ".join(underserved_categories.index[:3])} appear underserved.',
                'action': 'Consider expanding into underserved categories with targeted pricing strategies.'
            })
    
    # Dynamic pricing recommendation
    recommendations.append({
        'title': 'Implement Dynamic Pricing Monitoring',
        'description': 'Regular competitor price tracking shows market volatility patterns.',
        'action': 'Set up automated price monitoring alerts for key competitors and price change triggers.'
    })
    
    return recommendations
