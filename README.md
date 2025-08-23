# CRM Market Intelligence Platform

A comprehensive web application that automates competitive market analysis for CRM platforms, providing real-time pricing comparisons and feature analytics to support strategic business decisions.

## 🚀 Features

### Core Functionality
- **Automated Data Extraction**: Real-time web scraping of CRM vendor websites
- **AI-Powered Analysis**: Intelligent content analysis using OpenAI GPT-4o
- **Interactive Comparison Table**: Sortable and filterable CRM comparison with key metrics
- **Dynamic Pricing Analysis**: Automated extraction and visualization of pricing data
- **Export Capabilities**: CSV and summary report generation

### Key Comparison Metrics
- **CRM Platform**: Vendor name and branding
- **Entry Price**: Lowest advertised plan per user/month
- **Notable Features**: Key functionality and differentiators
- **AI/Automation**: Advanced automation and AI capabilities
- **Target Market**: Primary customer segments

## 🛠 Technical Stack

- **Backend**: Python, Pandas, JSON storage
- **Frontend**: Streamlit web framework
- **AI Integration**: OpenAI GPT-4o API
- **Data Visualization**: Plotly interactive charts
- **Web Scraping**: Trafilatura, Requests, BeautifulSoup
- **Data Processing**: Regex pattern matching, automated fallbacks

## 📋 Installation & Setup

### Prerequisites
- Python 3.11+
- OpenAI API key

### Dependencies
```bash
pip install streamlit pandas plotly openai requests beautifulsoup4 trafilatura validators
```

### Environment Setup
1. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Run the application:
   ```bash
   streamlit run app.py --server.port 5000
   ```

## 🎯 Usage

1. **Enter CRM Company**: Input any major CRM vendor name (e.g., Salesforce, HubSpot, Pipedrive)
2. **Click "Analyze CRM Market"**: The platform automatically finds and analyzes competitors
3. **Review Comparison Table**: Sort by price, filter by target market, explore features
4. **Export Results**: Download CSV reports or summary insights for further analysis

## 🏗 Project Structure

```
├── app.py                 # Main Streamlit application
├── modules/
│   ├── scraper.py        # Web scraping functionality
│   ├── analyzer.py       # AI-powered content analysis
│   ├── visualizer.py     # Chart and visualization generation
│   └── data_manager.py   # Data persistence and management
├── utils/
│   └── helpers.py        # Utility functions
└── .streamlit/
    └── config.toml       # Streamlit configuration
```

## 🔧 Key Components

### Data Extraction Engine
- **Web Scraping**: Automated extraction from 10+ major CRM platforms
- **Pricing Intelligence**: Regex-based pricing extraction with fallback systems
- **Feature Analysis**: AI-powered categorization of platform capabilities

### Visualization Dashboard
- **Comparison Table**: Interactive sorting and filtering
- **Pricing Charts**: Bar charts showing competitive pricing landscape
- **Market Distribution**: Pie charts displaying target market segments
- **Export Tools**: CSV and summary report generation

### AI Analysis System
- **Content Processing**: GPT-4o integration for intelligent feature extraction
- **Market Categorization**: Automated target market identification
- **Competitive Insights**: AI-generated strategic recommendations

## 📊 Supported CRM Platforms

- Salesforce
- HubSpot
- Pipedrive
- Zoho CRM
- Microsoft Dynamics 365
- Freshsales
- Copper
- Close
- Insightly
- Monday.com

## 🎨 User Interface

### Interactive Features
- **Mobile-Responsive Design**: Optimized for all screen sizes
- **Real-Time Sorting**: Sort by platform, price, or target market
- **Advanced Filtering**: Filter results by market segment
- **Dynamic Charts**: Interactive Plotly visualizations
- **Export Options**: One-click CSV and summary downloads

### User Experience
- **Simple Input**: Single text field for company analysis
- **Progress Tracking**: Real-time scraping progress indicators
- **Error Handling**: Graceful fallbacks for failed data extraction
- **Professional Styling**: Clean, business-focused interface

## 🚀 Business Applications

### Sales & Marketing Teams
- **Competitive Positioning**: Understand market landscape and pricing strategies
- **Feature Comparison**: Identify competitive advantages and gaps
- **Market Research**: Quick analysis of new market entrants

### Product Management
- **Feature Benchmarking**: Compare product capabilities across vendors
- **Pricing Strategy**: Analyze competitive pricing models
- **Target Market Analysis**: Understand customer segmentation strategies

### Strategic Planning
- **Market Intelligence**: Comprehensive competitor analysis
- **Investment Decisions**: Data-driven vendor evaluation
- **Partnership Opportunities**: Identify potential collaboration targets

## 🔒 Data Handling

- **Privacy-First**: No storage of scraped vendor data
- **Real-Time Processing**: Fresh data extraction for each analysis
- **Fallback Systems**: Reliable operation even with scraping failures
- **Export Security**: User-controlled data export and retention

## 🤝 Contributing

This project was built as a market intelligence tool for CRM competitive analysis. The modular architecture allows for easy extension to other market segments.

## 📄 License

This project is designed for educational and business intelligence purposes.

---

**Built with Python & Streamlit** | **Powered by OpenAI GPT-4o**