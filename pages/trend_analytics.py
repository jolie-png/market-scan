import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

def render_trend_analytics():
    """Render the trend analytics page"""
    st.title("📈 Trend Analytics")
    
    # Get data
    data = st.session_state.data_manager.get_all_data()
    
    if data.empty:
        st.info("No competitor data available. Please add competitors in the Data Management section.")
        return
    
    # Sidebar filters
    st.sidebar.subheader("🔍 Trend Filters")
    
    # Time range filter
    if 'last_updated' in data.columns:
        min_date = data['last_updated'].min().date()
        max_date = data['last_updated'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            data = data[
                (data['last_updated'].dt.date >= start_date) & 
                (data['last_updated'].dt.date <= end_date)
            ]
    
    # Category filter
    if 'category' in data.columns:
        categories = ['All'] + sorted(data['category'].unique().tolist())
        selected_category = st.sidebar.selectbox("Select Category", categories)
        
        if selected_category != 'All':
            data = data[data['category'] == selected_category]
    
    # Trend analysis type
    trend_type = st.sidebar.radio(
        "Trend Analysis Type",
        ["Market Activity", "Pricing Trends", "Competitive Dynamics", "AI-Powered Insights"]
    )
    
    st.info(f"Analyzing trends for {len(data)} data points")
    
    # Render content based on selected trend type
    if trend_type == "Market Activity":
        render_market_activity_trends(data)
    elif trend_type == "Pricing Trends":
        render_pricing_trends(data)
    elif trend_type == "Competitive Dynamics":
        render_competitive_dynamics(data)
    elif trend_type == "AI-Powered Insights":
        render_ai_trend_insights(data)

def render_market_activity_trends(data):
    """Render market activity trends"""
    st.subheader("📊 Market Activity Trends")
    
    if 'last_updated' not in data.columns:
        st.warning("No timestamp data available for trend analysis.")
        return
    
    # Prepare time-based data
    data['update_date'] = data['last_updated'].dt.date
    data['update_week'] = data['last_updated'].dt.to_period('W')
    data['update_month'] = data['last_updated'].dt.to_period('M')
    
    # Daily activity trend
    daily_activity = data.groupby('update_date').size().reset_index(name='updates')
    daily_activity['update_date'] = pd.to_datetime(daily_activity['update_date'])
    
    # Calculate moving averages
    daily_activity['3_day_avg'] = daily_activity['updates'].rolling(window=3, min_periods=1).mean()
    daily_activity['7_day_avg'] = daily_activity['updates'].rolling(window=7, min_periods=1).mean()
    
    # Create activity trend chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_activity['update_date'],
        y=daily_activity['updates'],
        mode='lines+markers',
        name='Daily Updates',
        line=dict(color='lightblue'),
        marker=dict(size=4)
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_activity['update_date'],
        y=daily_activity['7_day_avg'],
        mode='lines',
        name='7-Day Average',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title='Market Activity Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Updates',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Activity metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_updates = len(data)
        st.metric("Total Updates", total_updates)
    
    with col2:
        avg_daily = daily_activity['updates'].mean()
        st.metric("Avg Daily Activity", f"{avg_daily:.1f}")
    
    with col3:
        max_day = daily_activity.loc[daily_activity['updates'].idxmax()]
        st.metric("Peak Activity", f"{max_day['updates']} updates", 
                 help=f"on {max_day['update_date'].strftime('%Y-%m-%d')}")
    
    with col4:
        recent_trend = calculate_trend(daily_activity['updates'].tail(7).values)
        trend_emoji = "📈" if recent_trend > 0 else "📉" if recent_trend < 0 else "➡️"
        st.metric("Recent Trend", f"{trend_emoji} {abs(recent_trend):.1f}%")
    
    # Company activity heatmap
    if len(data['company'].unique()) > 1:
        st.subheader("🏢 Company Activity Patterns")
        
        company_activity = data.groupby(['company', 'update_date']).size().reset_index(name='updates')
        activity_pivot = company_activity.pivot(index='company', columns='update_date', values='updates')
        activity_pivot = activity_pivot.fillna(0)
        
        fig = px.imshow(
            activity_pivot.values,
            labels=dict(x="Date", y="Company", color="Updates"),
            y=activity_pivot.index,
            x=[date.strftime('%m/%d') for date in activity_pivot.columns],
            title="Company Activity Heatmap",
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=max(300, len(activity_pivot.index) * 30))
        st.plotly_chart(fig, use_container_width=True)

def render_pricing_trends(data):
    """Render pricing trend analysis"""
    st.subheader("💰 Pricing Trends Analysis")
    
    if 'price' not in data.columns or data['price'].isna().all():
        st.warning("No pricing data available for trend analysis.")
        return
    
    price_data = data.dropna(subset=['price'])
    
    if price_data.empty:
        st.warning("No valid pricing data found.")
        return
    
    # Time-based pricing analysis
    price_data['update_date'] = price_data['last_updated'].dt.date
    
    # Daily average price trend
    daily_avg_price = price_data.groupby('update_date').agg({
        'price': ['mean', 'min', 'max', 'count']
    }).round(2)
    daily_avg_price.columns = ['avg_price', 'min_price', 'max_price', 'count']
    daily_avg_price = daily_avg_price.reset_index()
    daily_avg_price['update_date'] = pd.to_datetime(daily_avg_price['update_date'])
    
    # Create price trend visualization
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Average Price Trend', 'Price Range Trend'),
        vertical_spacing=0.1
    )
    
    # Average price trend
    fig.add_trace(
        go.Scatter(
            x=daily_avg_price['update_date'],
            y=daily_avg_price['avg_price'],
            mode='lines+markers',
            name='Average Price',
            line=dict(color='blue', width=3)
        ),
        row=1, col=1
    )
    
    # Price range (min/max) trend
    fig.add_trace(
        go.Scatter(
            x=daily_avg_price['update_date'],
            y=daily_avg_price['max_price'],
            mode='lines',
            name='Max Price',
            line=dict(color='red', dash='dash')
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=daily_avg_price['update_date'],
            y=daily_avg_price['min_price'],
            mode='lines',
            name='Min Price',
            line=dict(color='green', dash='dash'),
            fill='tonexty'
        ),
        row=2, col=1
    )
    
    fig.update_layout(height=600, title_text="Pricing Trends Over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    # Pricing metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_avg = daily_avg_price['avg_price'].iloc[-1]
        st.metric("Current Avg Price", f"${current_avg:.2f}")
    
    with col2:
        if len(daily_avg_price) > 1:
            price_change = daily_avg_price['avg_price'].iloc[-1] - daily_avg_price['avg_price'].iloc[0]
            price_change_pct = (price_change / daily_avg_price['avg_price'].iloc[0]) * 100
            st.metric("Price Change", f"${price_change:.2f}", f"{price_change_pct:+.1f}%")
        else:
            st.metric("Price Change", "N/A")
    
    with col3:
        price_volatility = daily_avg_price['avg_price'].std()
        st.metric("Price Volatility", f"${price_volatility:.2f}")
    
    with col4:
        current_range = daily_avg_price['max_price'].iloc[-1] - daily_avg_price['min_price'].iloc[-1]
        st.metric("Current Price Range", f"${current_range:.2f}")
    
    # Category-wise pricing trends
    if 'category' in price_data.columns and len(price_data['category'].unique()) > 1:
        st.subheader("📊 Category Pricing Trends")
        
        category_price_trends = price_data.groupby(['update_date', 'category'])['price'].mean().reset_index()
        
        fig = px.line(
            category_price_trends,
            x='update_date',
            y='price',
            color='category',
            title='Average Price Trends by Category',
            labels={'update_date': 'Date', 'price': 'Average Price ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)

def render_competitive_dynamics(data):
    """Render competitive dynamics analysis"""
    st.subheader("🏆 Competitive Dynamics Analysis")
    
    # Market share evolution
    if len(data['company'].unique()) > 1:
        st.subheader("📈 Market Share Evolution")
        
        # Calculate market share over time
        data['update_date'] = data['last_updated'].dt.date
        market_share_data = data.groupby(['update_date', 'company']).size().reset_index(name='activity')
        
        # Calculate percentage share for each date
        total_by_date = market_share_data.groupby('update_date')['activity'].transform('sum')
        market_share_data['share_pct'] = (market_share_data['activity'] / total_by_date) * 100
        
        fig = px.area(
            market_share_data,
            x='update_date',
            y='share_pct',
            color='company',
            title='Market Share Evolution (%)',
            labels={'update_date': 'Date', 'share_pct': 'Market Share (%)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # New entrants analysis
    st.subheader("🚪 New Market Entrants")
    
    # Find companies by their first appearance date
    first_appearance = data.groupby('company')['last_updated'].min().reset_index()
    first_appearance['entry_date'] = first_appearance['last_updated'].dt.date
    first_appearance = first_appearance.sort_values('last_updated')
    
    # Group by month for new entrants
    first_appearance['entry_month'] = first_appearance['last_updated'].dt.to_period('M')
    new_entrants_by_month = first_appearance.groupby('entry_month').size().reset_index(name='new_companies')
    
    if len(new_entrants_by_month) > 1:
        fig = px.bar(
            new_entrants_by_month,
            x='entry_month',
            y='new_companies',
            title='New Competitors Entering Market',
            labels={'entry_month': 'Month', 'new_companies': 'New Companies'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Display recent entrants
    recent_entrants = first_appearance[
        first_appearance['last_updated'] >= datetime.now() - timedelta(days=30)
    ]
    
    if not recent_entrants.empty:
        st.write("**🆕 New Competitors (Last 30 Days):**")
        for _, entrant in recent_entrants.iterrows():
            st.write(f"• **{entrant['company']}** (entered {entrant['entry_date']})")
    else:
        st.info("No new competitors identified in the last 30 days.")
    
    # Competitive intensity analysis
    st.subheader("⚡ Competitive Intensity")
    
    # Calculate competitive intensity metrics
    data['update_week'] = data['last_updated'].dt.to_period('W')
    weekly_metrics = data.groupby('update_week').agg({
        'company': 'nunique',  # Number of active companies
        'price': ['count', 'std'],  # Number of price updates and price volatility
    }).round(2)
    
    weekly_metrics.columns = ['active_companies', 'price_updates', 'price_volatility']
    weekly_metrics = weekly_metrics.reset_index()
    weekly_metrics['intensity_score'] = (
        weekly_metrics['active_companies'] * 0.3 + 
        weekly_metrics['price_updates'] * 0.4 + 
        weekly_metrics['price_volatility'].fillna(0) * 0.3
    )
    
    fig = px.line(
        weekly_metrics,
        x='update_week',
        y='intensity_score',
        title='Competitive Intensity Score Over Time',
        labels={'update_week': 'Week', 'intensity_score': 'Intensity Score'}
    )
    st.plotly_chart(fig, use_container_width=True)

def render_ai_trend_insights(data):
    """Render AI-powered trend insights"""
    st.subheader("🤖 AI-Powered Trend Insights")
    
    if st.button("🔮 Generate AI Trend Analysis", type="primary"):
        with st.spinner("Analyzing market trends with AI..."):
            # Use the analyzer to identify trends
            trends = st.session_state.analyzer.identify_trends(data)
            
            if trends:
                # Display different types of trends
                col1, col2 = st.columns(2)
                
                with col1:
                    if trends.get('pricing_trends'):
                        st.subheader("💰 Pricing Trends")
                        for trend in trends['pricing_trends']:
                            trend_icon = "📈" if trend.get('trend') == 'increasing' else "📉"
                            st.success(f"{trend_icon} {trend.get('description', 'No description')}")
                    
                    if trends.get('feature_trends'):
                        st.subheader("⚡ Feature Trends")
                        for trend in trends['feature_trends']:
                            st.info(f"🔧 {trend}")
                
                with col2:
                    if trends.get('market_trends'):
                        st.subheader("🌍 Market Trends")
                        for trend in trends['market_trends']:
                            if isinstance(trend, dict):
                                st.warning(f"📊 {trend.get('description', 'Market trend identified')}")
                            else:
                                st.warning(f"📊 {trend}")
                    
                    if trends.get('strategic_insights'):
                        st.subheader("💡 Strategic Insights")
                        for insight in trends['strategic_insights']:
                            st.success(f"🎯 {insight}")
                
                # Generate predictions
                st.subheader("🔮 Market Predictions")
                predictions = generate_market_predictions(data)
                
                for prediction in predictions:
                    st.write(f"**{prediction['timeframe']}:** {prediction['prediction']}")
                    if prediction.get('confidence'):
                        st.progress(prediction['confidence'] / 100)
                        st.caption(f"Confidence: {prediction['confidence']}%")
                    st.write("---")
                
            else:
                st.info("No significant trends identified in the current dataset.")
    
    # Manual trend analysis tools
    st.subheader("🔧 Trend Analysis Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Detect Price Anomalies"):
            anomalies = detect_price_anomalies(data)
            if anomalies:
                st.warning("⚠️ Price Anomalies Detected:")
                for anomaly in anomalies:
                    st.write(f"• {anomaly}")
            else:
                st.success("✅ No significant price anomalies detected")
    
    with col2:
        if st.button("🔍 Identify Market Gaps"):
            gaps = identify_market_gaps(data)
            if gaps:
                st.info("💡 Market Gaps Identified:")
                for gap in gaps:
                    st.write(f"• {gap}")
            else:
                st.info("ℹ️ No clear market gaps identified")
    
    # Trend correlation analysis
    if len(data) > 10:  # Need sufficient data for correlation
        st.subheader("🔗 Trend Correlations")
        
        if st.button("📈 Analyze Trend Correlations"):
            correlations = analyze_trend_correlations(data)
            if correlations:
                for correlation in correlations:
                    st.write(f"📊 {correlation}")
            else:
                st.info("No significant correlations found")

def calculate_trend(values):
    """Calculate trend percentage change"""
    if len(values) < 2:
        return 0
    
    start_val = values[0] if values[0] != 0 else 1
    end_val = values[-1]
    
    return ((end_val - start_val) / start_val) * 100

def detect_price_anomalies(data):
    """Detect price anomalies in the data"""
    anomalies = []
    
    if 'price' not in data.columns or data['price'].isna().all():
        return anomalies
    
    price_data = data.dropna(subset=['price'])
    
    if len(price_data) < 5:
        return anomalies
    
    # Statistical anomaly detection
    mean_price = price_data['price'].mean()
    std_price = price_data['price'].std()
    
    # Z-score based anomalies
    z_scores = np.abs((price_data['price'] - mean_price) / std_price)
    anomalous_prices = price_data[z_scores > 2.5]  # 2.5 standard deviations
    
    if not anomalous_prices.empty:
        for _, anomaly in anomalous_prices.iterrows():
            anomalies.append(
                f"{anomaly['company']} pricing ${anomaly['price']:.2f} "
                f"({((anomaly['price'] - mean_price) / mean_price * 100):+.1f}% from average)"
            )
    
    return anomalies

def identify_market_gaps(data):
    """Identify potential market gaps"""
    gaps = []
    
    # Price gap analysis
    if 'price' in data.columns and not data['price'].isna().all():
        price_data = data.dropna(subset=['price']).sort_values('price')
        
        # Find large gaps in pricing
        price_diffs = price_data['price'].diff()
        large_gaps = price_diffs[price_diffs > price_diffs.quantile(0.8)]
        
        if not large_gaps.empty:
            gaps.append(f"Pricing gap between ${large_gaps.index[0]:.2f} and ${large_gaps.iloc[0]:.2f}")
    
    # Category gap analysis
    if 'category' in data.columns:
        category_counts = data['category'].value_counts()
        underserved = category_counts[category_counts < category_counts.quantile(0.25)]
        
        if not underserved.empty:
            gaps.append(f"Underserved categories: {', '.join(underserved.index[:3])}")
    
    # Geographic or other gaps could be added here
    
    return gaps

def analyze_trend_correlations(data):
    """Analyze correlations between different trends"""
    correlations = []
    
    try:
        # Prepare daily aggregated data
        if 'last_updated' in data.columns:
            data['update_date'] = data['last_updated'].dt.date
            daily_data = data.groupby('update_date').agg({
                'price': 'mean',
                'company': 'nunique'
            }).dropna()
            
            if len(daily_data) > 3:
                # Price vs market activity correlation
                price_activity_corr = daily_data['price'].corr(daily_data['company'])
                
                if abs(price_activity_corr) > 0.5:
                    direction = "positive" if price_activity_corr > 0 else "negative"
                    correlations.append(
                        f"Strong {direction} correlation ({price_activity_corr:.2f}) "
                        f"between pricing and market activity"
                    )
    except Exception as e:
        st.error(f"Error in correlation analysis: {str(e)}")
    
    return correlations

def generate_market_predictions(data):
    """Generate market predictions based on trends"""
    predictions = []
    
    # Basic trend-based predictions
    if 'price' in data.columns and not data['price'].isna().all():
        price_data = data.dropna(subset=['price'])
        
        if len(price_data) > 5:
            recent_prices = price_data['price'].tail(5).values
            trend = calculate_trend(recent_prices)
            
            if abs(trend) > 5:  # Significant trend
                direction = "increase" if trend > 0 else "decrease"
                predictions.append({
                    'timeframe': 'Short-term (Next 30 days)',
                    'prediction': f'Prices likely to {direction} by {abs(trend):.1f}% based on recent trends',
                    'confidence': min(85, 50 + abs(trend))
                })
    
    # Market entry predictions
    if len(data['company'].unique()) > 2:
        recent_entrants = len(data[data['last_updated'] >= datetime.now() - timedelta(days=30)]['company'].unique())
        
        if recent_entrants > 0:
            predictions.append({
                'timeframe': 'Medium-term (Next 3 months)',
                'prediction': f'Market attractiveness suggests {recent_entrants + 1} new competitors may enter',
                'confidence': 60
            })
    
    # Default prediction if no specific trends
    if not predictions:
        predictions.append({
            'timeframe': 'General Market',
            'prediction': 'Market appears stable with no significant disruption indicators',
            'confidence': 70
        })
    
    return predictions
