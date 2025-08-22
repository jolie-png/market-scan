import trafilatura
import requests
from datetime import datetime
import pandas as pd
import re
import time
from urllib.parse import urljoin, urlparse
import streamlit as st

class CompetitorScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_competitor(self, url, company_name, category=None):
        """
        Scrape competitor data from a given URL
        """
        try:
            # Fetch the main content
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return None
                
            # Extract main text content
            text_content = trafilatura.extract(downloaded)
            if not text_content:
                return None
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(downloaded)
            
            # Try to extract pricing information
            price = self._extract_price(text_content)
            
            # Extract product/service names
            products = self._extract_products(text_content)
            
            # Create competitor data structure
            competitor_data = {
                'company': company_name,
                'source_url': url,
                'category': category or 'Unknown',
                'last_updated': datetime.now(),
                'content': text_content[:5000],  # Limit content length
                'title': getattr(metadata, 'title', '') if metadata else '',
                'description': getattr(metadata, 'description', '') if metadata else '',
                'price': price,
                'products': products,
                'scraped_at': datetime.now().isoformat()
            }
            
            return competitor_data
            
        except Exception as e:
            st.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_price(self, content):
        """
        Extract price information from content using regex patterns
        """
        price_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,000.00
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars?)',  # 1000 USD
            r'(?:price|cost|from|starting)\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Price: $100
            r'\$(\d+)(?:/month|/mo|/year|/yr)?',  # $99/month
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    # Convert first match to float
                    price_str = matches[0].replace(',', '')
                    return float(price_str)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _extract_products(self, content):
        """
        Extract product/service names from content
        """
        # Simple extraction - look for capitalized words that might be product names
        product_patterns = [
            r'(?:product|service|solution)s?\s*:?\s*([A-Z][a-zA-Z\s]{2,30})',
            r'(?:introducing|announcing|launch(?:ing)?)\s+([A-Z][a-zA-Z\s]{2,30})',
            r'([A-Z][a-zA-Z]{2,20})\s+(?:platform|software|app|tool|service)',
        ]
        
        products = []
        for pattern in product_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            products.extend([match.strip() for match in matches if len(match.strip()) > 2])
        
        # Remove duplicates and return first 5
        return list(dict.fromkeys(products))[:5]
    
    def scrape_multiple_competitors(self, competitor_list):
        """
        Scrape multiple competitors with rate limiting
        """
        results = []
        
        for i, competitor in enumerate(competitor_list):
            st.write(f"Scraping {competitor['company']} ({i+1}/{len(competitor_list)})")
            
            result = self.scrape_competitor(
                competitor['url'], 
                competitor['company'],
                competitor.get('category')
            )
            
            if result:
                results.append(result)
            
            # Rate limiting - wait 2 seconds between requests
            if i < len(competitor_list) - 1:
                time.sleep(2)
        
        return results
    
    def update_competitor_data(self, existing_data):
        """
        Update existing competitor data by re-scraping
        """
        updated_data = []
        
        for _, competitor in existing_data.iterrows():
            updated_result = self.scrape_competitor(
                competitor['source_url'],
                competitor['company'],
                competitor['category']
            )
            
            if updated_result:
                updated_data.append(updated_result)
            
            time.sleep(1)  # Rate limiting
        
        return updated_data
