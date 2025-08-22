import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import json
import os
from modules.scraper import CompetitorScraper
from modules.analyzer import CompetitorAnalyzer

class DataManager:
    def __init__(self):
        self.data_file = "competitor_data.json"
        self.scraper = CompetitorScraper()
        self.analyzer = CompetitorAnalyzer()
        self._initialize_data()
    
    def _initialize_data(self):
        """Initialize data storage"""
        if 'competitor_data' not in st.session_state:
            st.session_state.competitor_data = self._load_data()
    
    def _load_data(self):
        """Load data from file or return empty DataFrame"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    df = pd.DataFrame(data)
                    if not df.empty and 'last_updated' in df.columns:
                        df['last_updated'] = pd.to_datetime(df['last_updated'])
                    return df
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
        
        return pd.DataFrame()
    
    def _save_data(self, data):
        """Save data to file"""
        try:
            # Convert datetime columns to string for JSON serialization
            save_data = data.copy()
            if not save_data.empty:
                datetime_columns = save_data.select_dtypes(include=['datetime']).columns
                for col in datetime_columns:
                    save_data[col] = save_data[col].dt.isoformat()
            
            with open(self.data_file, 'w') as f:
                json.dump(save_data.to_dict('records'), f, indent=2)
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")
    
    def add_competitor_data(self, competitor_data):
        """Add new competitor data"""
        if not competitor_data:
            return False
        
        try:
            # Convert competitor data to DataFrame format
            df_data = []
            
            # Handle single product/service
            if isinstance(competitor_data.get('products'), list) and competitor_data['products']:
                for product in competitor_data['products']:
                    row = competitor_data.copy()
                    row['product_name'] = product
                    row.pop('products', None)  # Remove the products list
                    df_data.append(row)
            else:
                # No specific products found, create generic entry
                row = competitor_data.copy()
                row['product_name'] = f"{competitor_data['company']} Service"
                row.pop('products', None)
                df_data.append(row)
            
            new_df = pd.DataFrame(df_data)
            
            # Generate summaries for new data
            for idx, row in new_df.iterrows():
                content_value = row.get('content', '')
                if content_value and pd.notna(content_value) and str(content_value).strip():
                    summary = self.analyzer.summarize_competitor_content(
                        str(content_value), row['company']
                    )
                    new_df.at[idx, 'summary'] = summary
            
            # Append to existing data
            current_data = st.session_state.competitor_data
            if current_data.empty:
                st.session_state.competitor_data = new_df
            else:
                st.session_state.competitor_data = pd.concat([current_data, new_df], ignore_index=True)
            
            # Save to file
            self._save_data(st.session_state.competitor_data)
            
            return True
            
        except Exception as e:
            st.error(f"Error adding competitor data: {str(e)}")
            return False
    
    def get_all_data(self):
        """Get all competitor data"""
        return st.session_state.competitor_data.copy()
    
    def get_competitor_data(self, company_name):
        """Get data for a specific competitor"""
        data = st.session_state.competitor_data
        if data.empty:
            return pd.DataFrame()
        return data[data['company'] == company_name].copy()
    
    def get_category_data(self, category):
        """Get data for a specific category"""
        data = st.session_state.competitor_data
        if data.empty:
            return pd.DataFrame()
        return data[data['category'] == category].copy()
    
    def update_competitor(self, company_name, url=None):
        """Update data for a specific competitor"""
        try:
            current_data = st.session_state.competitor_data
            if current_data.empty:
                return False
            
            competitor_rows = current_data[current_data['company'] == company_name]
            if competitor_rows.empty:
                return False
            
            # Get the URL (use provided or existing)
            source_url = url or competitor_rows.iloc[0].get('source_url')
            category = competitor_rows.iloc[0].get('category', 'Unknown')
            
            if source_url:
                # Scrape fresh data
                new_data = self.scraper.scrape_competitor(source_url, company_name, category)
                if new_data:
                    # Remove old data for this company
                    st.session_state.competitor_data = current_data[current_data['company'] != company_name]
                    # Add new data
                    return self.add_competitor_data(new_data)
            
            return False
            
        except Exception as e:
            st.error(f"Error updating competitor {company_name}: {str(e)}")
            return False
    
    def remove_competitor(self, company_name):
        """Remove a competitor's data"""
        try:
            current_data = st.session_state.competitor_data
            if current_data.empty:
                return False
            
            st.session_state.competitor_data = current_data[current_data['company'] != company_name]
            self._save_data(st.session_state.competitor_data)
            return True
            
        except Exception as e:
            st.error(f"Error removing competitor {company_name}: {str(e)}")
            return False
    
    def refresh_all_data(self):
        """Refresh all competitor data by re-scraping"""
        try:
            current_data = st.session_state.competitor_data
            if current_data.empty:
                return False
            
            # Get unique companies and their URLs
            companies = current_data[['company', 'source_url', 'category']].drop_duplicates()
            
            # Clear current data
            st.session_state.competitor_data = pd.DataFrame()
            
            # Re-scrape each competitor
            for _, row in companies.iterrows():
                if pd.notna(row['source_url']):
                    new_data = self.scraper.scrape_competitor(
                        row['source_url'], 
                        row['company'], 
                        row['category']
                    )
                    if new_data:
                        self.add_competitor_data(new_data)
            
            return True
            
        except Exception as e:
            st.error(f"Error refreshing all data: {str(e)}")
            return False
    
    def clear_all_data(self):
        """Clear all competitor data"""
        try:
            st.session_state.competitor_data = pd.DataFrame()
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            return True
        except Exception as e:
            st.error(f"Error clearing data: {str(e)}")
            return False
    
    def get_summary_stats(self):
        """Get summary statistics of the data"""
        data = st.session_state.competitor_data
        if data.empty:
            return {}
        
        stats = {
            'total_competitors': len(data['company'].unique()),
            'total_products': len(data),
            'categories': len(data['category'].unique()) if 'category' in data.columns else 0,
            'last_update': data['last_updated'].max().strftime('%Y-%m-%d %H:%M') if 'last_updated' in data.columns else 'Never',
            'avg_price': data['price'].mean() if 'price' in data.columns and not data['price'].isna().all() else 0,
            'price_range': {
                'min': data['price'].min() if 'price' in data.columns and not data['price'].isna().all() else 0,
                'max': data['price'].max() if 'price' in data.columns and not data['price'].isna().all() else 0
            }
        }
        
        return stats
    
    def get_recent_updates(self, days=7):
        """Get recently updated competitor data"""
        data = st.session_state.competitor_data
        if data.empty or 'last_updated' not in data.columns:
            return pd.DataFrame()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        return data[data['last_updated'] >= cutoff_date].copy()
    
    def export_data(self, format='csv'):
        """Export data in specified format"""
        data = st.session_state.competitor_data
        if data.empty:
            return None
        
        try:
            if format == 'csv':
                return data.to_csv(index=False)
            elif format == 'json':
                # Convert datetime to string for JSON
                export_data = data.copy()
                datetime_columns = export_data.select_dtypes(include=['datetime']).columns
                for col in datetime_columns:
                    export_data[col] = export_data[col].dt.isoformat()
                return export_data.to_json(orient='records', indent=2)
            else:
                return None
        except Exception as e:
            st.error(f"Error exporting data: {str(e)}")
            return None
