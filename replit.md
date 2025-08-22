# Market Intelligence Platform

## Overview

The Market Intelligence Platform is a comprehensive Streamlit-based application designed for competitive market analysis and business intelligence. The platform enables users to scrape, analyze, and visualize competitor data including pricing information, product offerings, and market trends. It integrates web scraping capabilities, AI-powered content analysis through OpenAI's GPT-4o model, and interactive data visualizations to provide actionable market insights.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses **Streamlit** as the primary web framework, providing a clean, interactive dashboard interface. The frontend is organized into multiple pages using Streamlit's multi-page architecture:

- **Dashboard**: Main overview with key metrics and market summaries
- **Competitor Analysis**: Detailed competitor profiling and filtering
- **Pricing Comparison**: Price analysis and competitive positioning
- **Trend Analytics**: Time-series analysis and market trend visualization
- **Data Management**: Data input, refresh, and export functionality

The UI leverages **Plotly** for interactive visualizations, supporting pie charts, histograms, scatter plots, and time-series graphs. Session state management maintains user data and component instances across page interactions.

### Backend Architecture
The application follows a modular design pattern with specialized components:

- **DataManager**: Handles data persistence, loading, and CRUD operations using JSON file storage
- **CompetitorScraper**: Web scraping engine using Trafilatura and Requests for content extraction
- **CompetitorAnalyzer**: AI-powered content analysis using OpenAI GPT-4o for competitive intelligence
- **CompetitorVisualizer**: Chart generation and data visualization management

Data processing utilizes **Pandas** for data manipulation and analysis, with support for time-series operations and statistical calculations.

### Data Storage Solution
The platform uses **file-based JSON storage** for simplicity and portability. Data is structured as DataFrames and serialized to JSON format with datetime handling for temporal analysis. The system supports:

- Competitor profiles with metadata
- Pricing information and product catalogs
- Content summaries and analysis results
- Time-stamped data updates for trend analysis

### Authentication and Authorization
Currently implements **no authentication system** - the application runs as a single-user dashboard. All data access is unrestricted within the application scope.

### AI Integration Architecture
The platform integrates **OpenAI's GPT-4o model** for intelligent content analysis:

- Automated competitor content summarization
- Value proposition extraction
- Competitive positioning analysis
- Market trend insights generation

The AI integration uses structured prompts to ensure consistent output formatting and relevant business intelligence extraction.

## External Dependencies

### Third-Party APIs
- **OpenAI API**: GPT-4o model integration for content analysis and competitive intelligence
- **Web scraping targets**: Various competitor websites accessed through HTTP requests

### Python Libraries
- **Streamlit**: Web application framework and UI components
- **Plotly**: Interactive data visualization and charting
- **Pandas**: Data manipulation and analysis
- **Trafilatura**: Web content extraction and text processing
- **Requests**: HTTP client for web scraping operations
- **OpenAI**: Official OpenAI API client library

### Data Sources
- **Competitor websites**: Primary source for product, pricing, and content data
- **Local JSON files**: Persistent storage for historical data and analysis results

### Browser Dependencies
The scraping functionality requires standard web browser user agents and supports common HTML/CSS parsing for content extraction from competitor websites.