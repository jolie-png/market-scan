import re
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import validators
import streamlit as st
from typing import Optional, Dict, List, Any, Union
import json

def format_currency(amount: Union[float, int, None]) -> str:
    """
    Format a numeric amount as currency string
    
    Args:
        amount: Numeric value to format as currency
        
    Returns:
        Formatted currency string (e.g., "$1,234.56")
    """
    if amount is None or pd.isna(amount):
        return "N/A"
    
    try:
        # Convert to float if it's not already
        amount = float(amount)
        
        # Handle negative values
        if amount < 0:
            return f"-${abs(amount):,.2f}"
        
        # Format positive values
        return f"${amount:,.2f}"
    
    except (ValueError, TypeError):
        return "N/A"

def safe_url_parse(url: str) -> bool:
    """
    Safely validate if a URL is properly formatted and accessible
    
    Args:
        url: URL string to validate
        
    Returns:
        Boolean indicating if URL is valid
    """
    if not url or not isinstance(url, str):
        return False
    
    # Clean up the URL
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Use validators library for comprehensive URL validation
    try:
        return validators.url(url) is True
    except Exception:
        return False

def clean_text_content(text: str) -> str:
    """
    Clean extracted text content for better processing
    
    Args:
        text: Raw text content to clean
        
    Returns:
        Cleaned text content
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might interfere with processing
    text = re.sub(r'[^\w\s\.\,\!\?\$\%\-\(\)]', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_price_from_text(text: str) -> Optional[float]:
    """
    Extract price information from text using multiple patterns
    
    Args:
        text: Text content to search for prices
        
    Returns:
        Extracted price as float or None if not found
    """
    if not text:
        return None
    
    # Multiple price extraction patterns
    price_patterns = [
        r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,000.00 or $100
        r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars?|bucks?)',  # 1000 USD
        r'(?:price|cost|fee|rate|from|starting|only)\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Price: $100
        r'\$(\d+)(?:/month|/mo|/year|/yr|/week|/day)?',  # $99/month
        r'(?:priced\s+at|costs?|worth)\s+\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # priced at $100
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                # Convert first match to float
                price_str = matches[0].replace(',', '')
                price = float(price_str)
                
                # Validate reasonable price range (between $0.01 and $1,000,000)
                if 0.01 <= price <= 1000000:
                    return price
            except (ValueError, IndexError):
                continue
    
    return None

def categorize_company(company_name: str, content: str = "") -> str:
    """
    Attempt to categorize a company based on its name and content
    
    Args:
        company_name: Name of the company
        content: Additional content to help with categorization
        
    Returns:
        Suggested category string
    """
    company_lower = company_name.lower()
    content_lower = content.lower() if content else ""
    
    # Category keywords mapping
    category_keywords = {
        'SaaS': ['saas', 'software', 'platform', 'cloud', 'app', 'service'],
        'E-commerce': ['shop', 'store', 'retail', 'marketplace', 'commerce', 'buy', 'sell'],
        'Fintech': ['finance', 'banking', 'payment', 'fintech', 'money', 'investment'],
        'Healthcare': ['health', 'medical', 'care', 'hospital', 'clinic', 'pharma'],
        'Education': ['education', 'learning', 'school', 'university', 'course', 'training'],
        'Marketing': ['marketing', 'advertising', 'campaign', 'promotion', 'brand'],
        'Analytics': ['analytics', 'data', 'insights', 'intelligence', 'reporting'],
        'Communication': ['communication', 'messaging', 'chat', 'video', 'conference'],
        'Productivity': ['productivity', 'workflow', 'management', 'organization'],
        'Security': ['security', 'protection', 'cyber', 'antivirus', 'firewall']
    }
    
    # Check both company name and content for category indicators
    combined_text = f"{company_lower} {content_lower}"
    
    category_scores = {}
    for category, keywords in category_keywords.items():
        score = sum(1 for keyword in keywords if keyword in combined_text)
        if score > 0:
            category_scores[category] = score
    
    # Return category with highest score, or 'Other' if no matches
    if category_scores:
        return max(category_scores.keys(), key=lambda k: category_scores[k])
    else:
        return 'Other'

def validate_competitor_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate competitor data structure and return list of issues
    
    Args:
        data: Competitor data dictionary
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Required fields
    required_fields = ['company', 'source_url', 'last_updated']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate URL format
    if 'source_url' in data and data['source_url']:
        if not safe_url_parse(data['source_url']):
            errors.append("Invalid URL format")
    
    # Validate price if present
    if 'price' in data and data['price'] is not None:
        try:
            price = float(data['price'])
            if price < 0:
                errors.append("Price cannot be negative")
            elif price > 1000000:
                errors.append("Price seems unreasonably high")
        except (ValueError, TypeError):
            errors.append("Invalid price format")
    
    # Validate date format
    if 'last_updated' in data and data['last_updated']:
        if not isinstance(data['last_updated'], datetime):
            errors.append("Invalid date format for last_updated")
    
    return errors

def generate_summary_stats(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive summary statistics for competitor data
    
    Args:
        data: DataFrame containing competitor data
        
    Returns:
        Dictionary with summary statistics
    """
    if data.empty:
        return {
            'total_records': 0,
            'unique_companies': 0,
            'date_range': 'No data',
            'price_stats': None,
            'category_distribution': {},
            'recent_activity': 0
        }
    
    stats = {}
    
    # Basic counts
    stats['total_records'] = len(data)
    stats['unique_companies'] = len(data['company'].unique()) if 'company' in data.columns else 0
    
    # Date range
    if 'last_updated' in data.columns and not data['last_updated'].isna().all():
        min_date = data['last_updated'].min()
        max_date = data['last_updated'].max()
        stats['date_range'] = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        
        # Recent activity (last 7 days)
        recent_cutoff = datetime.now() - timedelta(days=7)
        stats['recent_activity'] = len(data[data['last_updated'] >= recent_cutoff])
    else:
        stats['date_range'] = 'No date information'
        stats['recent_activity'] = 0
    
    # Price statistics
    if 'price' in data.columns and not data['price'].isna().all():
        price_data = data.dropna(subset=['price'])
        if not price_data.empty:
            stats['price_stats'] = {
                'count': len(price_data),
                'mean': float(price_data['price'].mean()),
                'median': float(price_data['price'].median()),
                'min': float(price_data['price'].min()),
                'max': float(price_data['price'].max()),
                'std': float(price_data['price'].std()) if len(price_data) > 1 else 0
            }
        else:
            stats['price_stats'] = None
    else:
        stats['price_stats'] = None
    
    # Category distribution
    if 'category' in data.columns:
        stats['category_distribution'] = data['category'].value_counts().to_dict()
    else:
        stats['category_distribution'] = {}
    
    return stats

def format_timeago(dt: datetime) -> str:
    """
    Format datetime as human-readable time ago string
    
    Args:
        dt: Datetime object
        
    Returns:
        Human-readable time ago string
    """
    if not isinstance(dt, datetime):
        return "Unknown"
    
    now = datetime.now()
    if dt.tzinfo is not None:
        # Handle timezone-aware datetime
        import pytz
        now = now.replace(tzinfo=pytz.UTC)
    
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def export_to_csv(data: pd.DataFrame, filename: str = None) -> str:
    """
    Export DataFrame to CSV format with proper formatting
    
    Args:
        data: DataFrame to export
        filename: Optional filename (will generate if not provided)
        
    Returns:
        CSV content as string
    """
    if data.empty:
        return ""
    
    # Create a copy for export formatting
    export_data = data.copy()
    
    # Format datetime columns
    datetime_columns = export_data.select_dtypes(include=['datetime']).columns
    for col in datetime_columns:
        export_data[col] = export_data[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Format price columns
    if 'price' in export_data.columns:
        export_data['price'] = export_data['price'].apply(
            lambda x: f"{x:.2f}" if pd.notna(x) else ""
        )
    
    # Return CSV string
    return export_data.to_csv(index=False)

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "export"
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Trim and ensure reasonable length
    filename = filename.strip('_')[:100]
    
    return filename if filename else "export"

def calculate_market_metrics(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate advanced market metrics from competitor data
    
    Args:
        data: DataFrame containing competitor data
        
    Returns:
        Dictionary with calculated market metrics
    """
    metrics = {}
    
    if data.empty:
        return metrics
    
    # Market concentration (Herfindahl-Hirschman Index approximation)
    if 'company' in data.columns:
        company_counts = data['company'].value_counts()
        total_entries = len(data)
        
        # Calculate market shares and HHI
        market_shares = (company_counts / total_entries) ** 2
        hhi = market_shares.sum() * 10000  # Scale to traditional HHI scale
        
        metrics['market_concentration'] = {
            'hhi_score': float(hhi),
            'interpretation': 'Highly Concentrated' if hhi > 2500 else 'Moderately Concentrated' if hhi > 1500 else 'Competitive'
        }
    
    # Price dispersion analysis
    if 'price' in data.columns and not data['price'].isna().all():
        price_data = data.dropna(subset=['price'])
        if len(price_data) > 1:
            cv = price_data['price'].std() / price_data['price'].mean()
            metrics['price_dispersion'] = {
                'coefficient_of_variation': float(cv),
                'interpretation': 'High Dispersion' if cv > 0.5 else 'Moderate Dispersion' if cv > 0.2 else 'Low Dispersion'
            }
    
    # Market activity trends
    if 'last_updated' in data.columns:
        # Calculate activity over time
        data_copy = data.copy()
        data_copy['date'] = data_copy['last_updated'].dt.date
        daily_activity = data_copy.groupby('date').size()
        
        if len(daily_activity) > 1:
            # Calculate trend
            x = range(len(daily_activity))
            y = daily_activity.values
            
            # Simple linear trend calculation
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi * xi for xi in x)
            
            if n * sum_x2 - sum_x * sum_x != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                
                metrics['activity_trend'] = {
                    'slope': float(slope),
                    'interpretation': 'Increasing' if slope > 0.1 else 'Decreasing' if slope < -0.1 else 'Stable'
                }
    
    return metrics

def detect_outliers(data: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
    """
    Detect outliers in a specific column using specified method
    
    Args:
        data: DataFrame containing the data
        column: Column name to analyze for outliers
        method: Method to use ('iqr' or 'zscore')
        
    Returns:
        DataFrame containing only the outlier rows
    """
    if data.empty or column not in data.columns:
        return pd.DataFrame()
    
    # Remove null values
    clean_data = data.dropna(subset=[column])
    
    if len(clean_data) < 4:  # Need minimum data for outlier detection
        return pd.DataFrame()
    
    if method == 'iqr':
        # Interquartile Range method
        Q1 = clean_data[column].quantile(0.25)
        Q3 = clean_data[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = clean_data[
            (clean_data[column] < lower_bound) | 
            (clean_data[column] > upper_bound)
        ]
        
    elif method == 'zscore':
        # Z-score method
        mean_val = clean_data[column].mean()
        std_val = clean_data[column].std()
        
        z_scores = abs((clean_data[column] - mean_val) / std_val)
        outliers = clean_data[z_scores > 2.5]  # 2.5 standard deviations
        
    else:
        outliers = pd.DataFrame()
    
    return outliers

def create_competitor_comparison_table(data: pd.DataFrame, companies: List[str]) -> pd.DataFrame:
    """
    Create a comparison table for selected companies
    
    Args:
        data: Full competitor dataset
        companies: List of company names to compare
        
    Returns:
        Formatted comparison DataFrame
    """
    if data.empty or not companies:
        return pd.DataFrame()
    
    # Filter data for selected companies
    comparison_data = data[data['company'].isin(companies)]
    
    if comparison_data.empty:
        return pd.DataFrame()
    
    # Aggregate metrics by company
    metrics = []
    
    for company in companies:
        company_data = comparison_data[comparison_data['company'] == company]
        
        if not company_data.empty:
            metric_row = {
                'Company': company,
                'Products/Services': len(company_data),
                'Categories': ', '.join(company_data['category'].unique()) if 'category' in company_data.columns else 'N/A',
                'Avg Price': company_data['price'].mean() if 'price' in company_data.columns and not company_data['price'].isna().all() else None,
                'Price Range': f"${company_data['price'].min():.2f} - ${company_data['price'].max():.2f}" if 'price' in company_data.columns and not company_data['price'].isna().all() else 'N/A',
                'Last Updated': company_data['last_updated'].max().strftime('%Y-%m-%d') if 'last_updated' in company_data.columns else 'N/A'
            }
            
            # Format average price
            if metric_row['Avg Price'] is not None:
                metric_row['Avg Price'] = f"${metric_row['Avg Price']:.2f}"
            else:
                metric_row['Avg Price'] = 'N/A'
            
            metrics.append(metric_row)
    
    return pd.DataFrame(metrics)
