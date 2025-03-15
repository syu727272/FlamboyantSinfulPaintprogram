# Tokyo Event Information App

This Streamlit application displays event information in Tokyo using the GROK API from X.AI.

## Features

- Search for events in Tokyo within a specified date range
- Configurable date range (up to 6 months)
- Filter events by type
- View event details including name, date, location, description, and URL
- Multiple view modes (card view and table view)

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set your X.AI API key:
   - Option 1: Create a `.env` file with `XAI_API_KEY=your_api_key`
   - Option 2: Set environment variable: `export XAI_API_KEY=your_api_key`
   - Option 3: Enter your API key directly in the app's sidebar

## Running the App

```
streamlit run tokyo_events_app.py
```

## Notes

- The app limits event searches to a maximum of 6 months to prevent excessive API usage
- The default view shows up to 30 events, but this can be adjusted in the interface
