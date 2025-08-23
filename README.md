# CRM Market Intelligence Platform

Hi there :')
This is a web application that analyzes and compares CRM platforms by automatically extracting pricing and feature data from vendor websites.

## Overview

This project scrapes CRM vendor websites to create comparative analysis tables showing pricing, features, AI capabilities, and target markets. Built as a learning project to practice web scraping, API integration, and data visualization.

## Features

- Web scraping of major CRM platforms (Salesforce, HubSpot, Pipedrive, etc.)
- AI-powered content analysis using OpenAI API
- Interactive comparison table with sorting and filtering
- Pricing visualization charts
- CSV export functionality

## Tech Stack

- **Python** - Core programming language
- **Streamlit** - Web framework for the dashboard
- **OpenAI API** - Content analysis and feature extraction
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive charts and visualizations
- **BeautifulSoup/Trafilatura** - Web scraping libraries

## Installation

1. Install dependencies:
```bash
pip install streamlit pandas plotly openai requests beautifulsoup4 trafilatura validators
```

2. Set up OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

3. Run the application:
```bash
streamlit run app.py --server.port 5000
```

## Usage

1. Enter a CRM company name (like "Salesforce")
2. Click "Analyze CRM Market" 
3. View the comparison table with pricing and features
4. Sort by price or filter by target market
5. Export results as CSV if needed

## Project Structure

```
├── app.py              # Main application
├── modules/
│   ├── scraper.py     # Web scraping logic
│   ├── analyzer.py    # AI content analysis
│   └── visualizer.py  # Chart generation
└── utils/
    └── helpers.py     # Utility functions
```

## Key Learning Outcomes

- Web scraping techniques and challenges
- API integration with OpenAI
- Data visualization with Python
- Building responsive web apps with Streamlit
- Handling real-world data extraction problems

## Supported Platforms

Salesforce, HubSpot, Pipedrive, Zoho CRM, Microsoft Dynamics 365, Freshsales, Copper, Close, Insightly, Monday.com
