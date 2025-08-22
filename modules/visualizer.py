import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CompetitorVisualizer:
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
        
    def create_market_overview(self, data):
        """
        Create a market overview visualization
        """
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Competitors by Category", "Price Distribution", 
                          "Market Activity", "Company Comparison"),
            specs=[[{"type": "pie"}, {"type": "histogram"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Pie chart - Competitors by Category
        if 'category' in data.columns:
            category_counts = data['category'].value_counts()
            fig.add_trace(
                go.Pie(
                    labels=category_counts.index,
                    values=category_counts.values,
                    name="Categories"
                ),
                row=1, col=1
            )
        
        # Histogram - Price Distribution
        if 'price' in data.columns:
            price_data = data.dropna(subset=['price'])
            if not price_data.empty:
                fig.add_trace(
                    go.Histogram(
                        x=price_data['price'],
                        name="Price Distribution",
                        nbinsx=10
                    ),
                    row=1, col=2
                )
        
        # Bar chart - Market Activity (updates by date)
        if 'last_updated' in data.columns:
            data['update_date'] = data['last_updated'].dt.date
            activity_counts = data['update_date'].value_counts().sort_index()
            fig.add_trace(
                go.Bar(
                    x=activity_counts.index,
                    y=activity_counts.values,
                    name="Daily Updates"
                ),
                row=2, col=1
            )
        
        # Scatter plot - Company comparison (price vs products)
        if 'price' in data.columns and 'company' in data.columns:
            # Calculate products per company (or use a proxy)
            company_data = data.groupby('company').agg({
                'price': 'mean',
                'product_name': 'count'
            }).reset_index()
            
            fig.add_trace(
                go.Scatter(
                    x=company_data['price'],
                    y=company_data['product_name'],
                    mode='markers',
                    text=company_data['company'],
                    name="Companies",
                    marker=dict(size=10)
                ),
                row=2, col=2
            )
        
        fig.update_layout(height=800, showlegend=False, title_text="Market Intelligence Overview")
        return fig
    
    def create_competitor_map(self, data):
        """
        Create a competitive positioning map
        """
        if data.empty or 'price' not in data.columns:
            fig = go.Figure()
            fig.add_annotation(text="Insufficient data for competitor mapping", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Calculate competitive metrics
        price_data = data.dropna(subset=['price'])
        if price_data.empty:
            fig = go.Figure()
            fig.add_annotation(text="No pricing data available", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Create market position scores (mock calculation - in real scenario, use more sophisticated metrics)
        np.random.seed(42)  # For reproducible results
        price_data = price_data.copy()
        price_data['market_position'] = np.random.uniform(1, 10, len(price_data))
        price_data['innovation_score'] = np.random.uniform(1, 10, len(price_data))
        
        fig = go.Figure()
        
        # Add scatter points for each competitor
        for category in price_data['category'].unique():
            category_data = price_data[price_data['category'] == category]
            
            fig.add_trace(
                go.Scatter(
                    x=category_data['market_position'],
                    y=category_data['innovation_score'],
                    mode='markers+text',
                    text=category_data['company'],
                    textposition="middle center",
                    name=category,
                    marker=dict(
                        size=category_data['price'] / category_data['price'].max() * 50 + 10,
                        opacity=0.7,
                        line=dict(width=2)
                    ),
                    hovertemplate="<b>%{text}</b><br>" +
                                "Market Position: %{x:.1f}<br>" +
                                "Innovation Score: %{y:.1f}<br>" +
                                "Price: $%{marker.size}<br>" +
                                "<extra></extra>"
                )
            )
        
        # Add quadrant lines
        fig.add_hline(y=5, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=5, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        fig.add_annotation(x=2.5, y=7.5, text="Challengers", showarrow=False, font=dict(color="gray"))
        fig.add_annotation(x=7.5, y=7.5, text="Leaders", showarrow=False, font=dict(color="gray"))
        fig.add_annotation(x=2.5, y=2.5, text="Niche Players", showarrow=False, font=dict(color="gray"))
        fig.add_annotation(x=7.5, y=2.5, text="Visionaries", showarrow=False, font=dict(color="gray"))
        
        fig.update_layout(
            title="Competitive Positioning Map",
            xaxis_title="Market Position Score",
            yaxis_title="Innovation Score",
            xaxis=dict(range=[0, 10]),
            yaxis=dict(range=[0, 10]),
            height=600
        )
        
        return fig
    
    def create_pricing_analysis(self, data):
        """
        Create pricing analysis visualizations
        """
        if data.empty or 'price' not in data.columns:
            fig = go.Figure()
            fig.add_annotation(text="No pricing data available", x=0.5, y=0.5, showarrow=False)
            return fig
        
        price_data = data.dropna(subset=['price'])
        if price_data.empty:
            fig = go.Figure()
            fig.add_annotation(text="No valid pricing data", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Price by Company", "Price by Category", 
                          "Price Distribution", "Price vs Market Position"),
            specs=[[{"type": "bar"}, {"type": "box"}],
                   [{"type": "histogram"}, {"type": "scatter"}]]
        )
        
        # Bar chart - Price by Company
        company_prices = price_data.groupby('company')['price'].mean().sort_values(ascending=False)
        fig.add_trace(
            go.Bar(
                x=company_prices.index,
                y=company_prices.values,
                name="Avg Price by Company"
            ),
            row=1, col=1
        )
        
        # Box plot - Price by Category
        if 'category' in price_data.columns:
            for category in price_data['category'].unique():
                category_data = price_data[price_data['category'] == category]
                fig.add_trace(
                    go.Box(
                        y=category_data['price'],
                        name=category,
                        boxpoints='all'
                    ),
                    row=1, col=2
                )
        
        # Histogram - Price Distribution
        fig.add_trace(
            go.Histogram(
                x=price_data['price'],
                name="Price Distribution",
                nbinsx=15
            ),
            row=2, col=1
        )
        
        # Scatter - Price vs Market Position (mock data)
        np.random.seed(42)
        market_position = np.random.uniform(1, 10, len(price_data))
        fig.add_trace(
            go.Scatter(
                x=price_data['price'],
                y=market_position,
                mode='markers',
                text=price_data['company'],
                name="Price vs Position",
                marker=dict(size=8)
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False, title_text="Pricing Analysis Dashboard")
        return fig
    
    def create_trend_analysis(self, data):
        """
        Create trend analysis visualizations
        """
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available for trend analysis", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Market Activity Over Time", "Price Trends"),
            specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
        )
        
        # Timeline of market activity
        if 'last_updated' in data.columns:
            data['update_date'] = data['last_updated'].dt.date
            daily_activity = data.groupby('update_date').size().reset_index(name='updates')
            
            fig.add_trace(
                go.Scatter(
                    x=daily_activity['update_date'],
                    y=daily_activity['updates'],
                    mode='lines+markers',
                    name='Daily Updates',
                    line=dict(width=3)
                ),
                row=1, col=1
            )
            
            # Add 7-day rolling average
            daily_activity['rolling_avg'] = daily_activity['updates'].rolling(window=7, min_periods=1).mean()
            fig.add_trace(
                go.Scatter(
                    x=daily_activity['update_date'],
                    y=daily_activity['rolling_avg'],
                    mode='lines',
                    name='7-day Average',
                    line=dict(dash='dash')
                ),
                row=1, col=1
            )
        
        # Price trends
        if 'price' in data.columns and 'last_updated' in data.columns:
            price_data = data.dropna(subset=['price'])
            if not price_data.empty:
                price_data['update_date'] = price_data['last_updated'].dt.date
                daily_avg_price = price_data.groupby('update_date')['price'].mean().reset_index()
                
                fig.add_trace(
                    go.Scatter(
                        x=daily_avg_price['update_date'],
                        y=daily_avg_price['price'],
                        mode='lines+markers',
                        name='Average Price',
                        line=dict(color='red', width=3)
                    ),
                    row=2, col=1
                )
        
        fig.update_layout(height=600, title_text="Market Trend Analysis")
        return fig
    
    def create_feature_comparison(self, data):
        """
        Create feature comparison visualization
        """
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available for feature comparison", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Mock feature analysis (in real scenario, extract from content)
        companies = data['company'].unique()[:10]  # Limit to first 10 companies
        features = ['Analytics', 'API Access', 'Mobile App', 'Integrations', 'Support', 'Scalability']
        
        # Generate mock feature scores
        np.random.seed(42)
        feature_matrix = np.random.randint(1, 6, size=(len(companies), len(features)))
        
        fig = go.Figure(data=go.Heatmap(
            z=feature_matrix,
            x=features,
            y=companies,
            colorscale='RdYlBu_r',
            hoverangles="closest",
            colorbar=dict(title="Feature Score (1-5)")
        ))
        
        fig.update_layout(
            title="Competitive Feature Comparison Matrix",
            xaxis_title="Features",
            yaxis_title="Companies",
            height=max(400, len(companies) * 30)
        )
        
        return fig
