import os
import json
from openai import OpenAI
import pandas as pd
from datetime import datetime
import streamlit as st

class CompetitorAnalyzer:
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        
    def summarize_competitor_content(self, content, company_name):
        """
        Summarize competitor content using OpenAI
        """
        if not self.openai_client.api_key:
            return "OpenAI API key not configured. Cannot generate summary."
        
        try:
            prompt = f"""
            Analyze the following content from {company_name}'s website and provide a concise summary focusing on:
            1. Key products/services offered
            2. Main value propositions
            3. Target market/customers
            4. Competitive advantages mentioned
            5. Recent updates or announcements
            
            Content:
            {content[:3000]}  # Limit content to avoid token limits
            
            Please provide the summary in a structured format.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def analyze_competitive_positioning(self, competitors_data):
        """
        Analyze competitive positioning across all competitors
        """
        if not self.openai_client.api_key:
            return "OpenAI API key not configured. Cannot generate analysis."
        
        try:
            # Prepare competitor summaries for analysis
            competitor_summaries = []
            for _, competitor in competitors_data.iterrows():
                summary = f"""
                Company: {competitor['company']}
                Category: {competitor.get('category', 'Unknown')}
                Price: {competitor.get('price', 'Not specified')}
                Key Info: {competitor.get('content', '')[:500]}
                """
                competitor_summaries.append(summary)
            
            prompt = f"""
            Analyze the following competitor landscape and provide insights on:
            1. Market segments and positioning
            2. Pricing strategies and ranges
            3. Key differentiators across competitors
            4. Market gaps and opportunities
            5. Competitive threats and strengths
            
            Competitors:
            {chr(10).join(competitor_summaries[:10])}  # Limit to first 10 competitors
            
            Provide a strategic analysis in JSON format with the following structure:
            {{
                "market_segments": ["segment1", "segment2"],
                "pricing_analysis": "analysis text",
                "key_differentiators": ["diff1", "diff2"],
                "market_opportunities": ["opp1", "opp2"],
                "competitive_threats": ["threat1", "threat2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strategic business analyst specializing in competitive intelligence. Provide detailed, actionable insights based on competitor data."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return json.loads(content) if content else {}
            
        except Exception as e:
            return {"error": f"Error generating competitive analysis: {str(e)}"}
    
    def identify_trends(self, historical_data):
        """
        Identify trends in competitor data over time
        """
        trends = {
            "pricing_trends": [],
            "feature_trends": [],
            "market_trends": []
        }
        
        try:
            # Analyze pricing trends
            if 'price' in historical_data.columns and not historical_data['price'].isna().all():
                price_data = historical_data.dropna(subset=['price'])
                if not price_data.empty:
                    avg_price_by_date = price_data.groupby(price_data['last_updated'].dt.date)['price'].mean()
                    if len(avg_price_by_date) > 1:
                        price_change = avg_price_by_date.iloc[-1] - avg_price_by_date.iloc[0]
                        trends["pricing_trends"].append({
                            "trend": "increasing" if price_change > 0 else "decreasing",
                            "change": abs(price_change),
                            "description": f"Average price has {'increased' if price_change > 0 else 'decreased'} by ${abs(price_change):.2f}"
                        })
            
            # Analyze new competitor entries
            if 'company' in historical_data.columns:
                companies_by_date = historical_data.groupby(historical_data['last_updated'].dt.date)['company'].nunique()
                if len(companies_by_date) > 1:
                    new_competitors = companies_by_date.iloc[-1] - companies_by_date.iloc[0]
                    if new_competitors > 0:
                        trends["market_trends"].append({
                            "trend": "market_growth",
                            "description": f"{new_competitors} new competitors identified recently"
                        })
            
            # Use AI for deeper trend analysis if API key is available
            if self.openai_client.api_key and not historical_data.empty:
                ai_trends = self._ai_trend_analysis(historical_data)
                if ai_trends and "error" not in ai_trends:
                    trends.update(ai_trends)
            
        except Exception as e:
            st.error(f"Error analyzing trends: {str(e)}")
        
        return trends
    
    def _ai_trend_analysis(self, data):
        """
        Use AI to identify deeper trends in the data
        """
        try:
            # Prepare data summary for AI analysis
            data_summary = {
                "total_competitors": len(data['company'].unique()) if not data.empty else 0,
                "categories": data['category'].value_counts().to_dict() if 'category' in data.columns else {},
                "price_range": {
                    "min": float(data['price'].min()) if 'price' in data.columns and not data['price'].isna().all() else 0,
                    "max": float(data['price'].max()) if 'price' in data.columns and not data['price'].isna().all() else 0,
                    "avg": float(data['price'].mean()) if 'price' in data.columns and not data['price'].isna().all() else 0
                },
                "recent_updates": len(data[data['last_updated'] >= datetime.now() - pd.Timedelta(days=30)]) if not data.empty else 0
            }
            
            prompt = f"""
            Analyze this competitive intelligence data and identify key trends:
            
            Data Summary:
            {json.dumps(data_summary, indent=2)}
            
            Identify trends in the following format:
            {{
                "feature_trends": ["trend1", "trend2"],
                "market_trends": ["trend1", "trend2"],
                "strategic_insights": ["insight1", "insight2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return json.loads(content) if content else {}
            
        except Exception as e:
            return {"error": f"Error in AI trend analysis: {str(e)}"}
    
    def generate_competitive_insights(self, competitor_data):
        """
        Generate actionable competitive insights
        """
        insights = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
        
        if competitor_data.empty:
            return insights
        
        try:
            # Basic analysis
            if 'price' in competitor_data.columns:
                price_data = competitor_data.dropna(subset=['price'])
                if not price_data.empty:
                    median_price = price_data['price'].median()
                    high_price_competitors = price_data[price_data['price'] > median_price * 1.5]
                    low_price_competitors = price_data[price_data['price'] < median_price * 0.5]
                    
                    if not high_price_competitors.empty:
                        insights["opportunities"].append(f"Premium market opportunity - {len(high_price_competitors)} competitors pricing above ${median_price*1.5:.2f}")
                    
                    if not low_price_competitors.empty:
                        insights["threats"].append(f"Price pressure from {len(low_price_competitors)} low-cost competitors")
            
            # Category analysis
            if 'category' in competitor_data.columns:
                category_counts = competitor_data['category'].value_counts()
                dominant_category = category_counts.index[0] if not category_counts.empty else None
                if dominant_category and category_counts.iloc[0] > len(competitor_data) * 0.4:
                    insights["threats"].append(f"Market dominated by {dominant_category} category ({category_counts.iloc[0]} competitors)")
                
                if len(category_counts) > 1:
                    emerging_categories = category_counts.tail(3).index.tolist()
                    insights["opportunities"].extend([f"Emerging opportunity in {cat}" for cat in emerging_categories])
            
            # AI-powered insights if available
            if self.openai_client.api_key:
                ai_insights = self._ai_competitive_insights(competitor_data)
                if ai_insights and "error" not in ai_insights:
                    for key in insights.keys():
                        if key in ai_insights:
                            insights[key].extend(ai_insights[key])
            
        except Exception as e:
            st.error(f"Error generating insights: {str(e)}")
        
        return insights
    
    def _ai_competitive_insights(self, data):
        """
        Generate AI-powered competitive insights
        """
        try:
            # Prepare competitive landscape summary
            summary = []
            for _, competitor in data.head(10).iterrows():  # Limit to first 10
                comp_summary = f"{competitor['company']}: {competitor.get('category', 'Unknown')} - ${competitor.get('price', 'N/A')}"
                summary.append(comp_summary)
            
            prompt = f"""
            Based on this competitive landscape, provide strategic insights:
            
            Competitors:
            {chr(10).join(summary)}
            
            Provide a SWOT-style analysis in JSON format:
            {{
                "strengths": ["strength1", "strength2"],
                "weaknesses": ["weakness1", "weakness2"],
                "opportunities": ["opportunity1", "opportunity2"],
                "threats": ["threat1", "threat2"]
            }}
            
            Focus on actionable insights for strategic decision making.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=600,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return json.loads(content) if content else {}
            
        except Exception as e:
            return {"error": f"Error in AI insights generation: {str(e)}"}
