# backend/item_trends_graphs.py
import requests
import json
import os
import sys
from typing import Dict, Any, Optional, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Create directories if they don't exist
os.makedirs('backend/item_trends', exist_ok=True)
os.makedirs('backend/item_prices', exist_ok=True)

def get_item_price_history(item_id: int, time_period: str = '180') -> Optional[Dict[str, Any]]:
    """Fetch item price history data from OSRS API"""
    # Time periods: 1 (24h), 7 (1 week), 30 (1 month), 90 (3 months), 180 (6 months), 365 (1 year)
    url = f"https://services.runescape.com/m=itemdb_oldschool/api/graph/{item_id}.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching history data for item {item_id}: {e}")
        return None

def get_item_name(item_id: int) -> Optional[str]:
    """Get item name from OSRS API"""
    url = f"https://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item={item_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            return data['item']['name']
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching item name for {item_id}: {e}")
        return None

def create_price_trend_graph(item_id: int, time_period: str = '180'):
    """Create and save price trend graph using Plotly"""
    # Get item name
    item_name = get_item_name(item_id)
    if not item_name:
        print(f"Failed to get item name for ID: {item_id}")
        return
    
    print(f"Creating price trend graph for: {item_name} (ID: {item_id})")
    
    # Get price history
    history_data = get_item_price_history(item_id, time_period)
    if not history_data:
        print(f"Failed to fetch price history for item {item_id}")
        return
    
    # Extract data
    daily = history_data.get('daily', {})
    average = history_data.get('average', {})
    
    # Convert timestamps to readable dates
    dates = []
    daily_prices = []
    avg_prices = []
    
    for timestamp, price in daily.items():
        dates.append(timestamp)
        daily_prices.append(price)
        avg_prices.append(average.get(timestamp, 0))
    
    # Create subplots
    fig = make_subplots(rows=1, cols=1, subplot_titles=[f'Price Trend for {item_name}'])
    
    # Add traces
    fig.add_trace(go.Scatter(x=dates, y=daily_prices, name='Daily Price', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=avg_prices, name='Average Price', line=dict(color='red', dash='dash')), row=1, col=1)
    
    # Update layout
    fig.update_layout(
        title=f'Price Trend for {item_name} (ID: {item_id})',
        xaxis_title='Date',
        yaxis_title='Price (GP)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # Save graph
    item_name_safe = item_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    graph_path = f'backend/item_trends/{item_id}_{item_name_safe}_trend.png'
    fig.write_image(graph_path)
    
    print(f"Price trend graph saved to: {graph_path}")
    
    # Also save the history data to JSON for reference
    history_file_path = f'backend/item_prices/{item_id}_{item_name_safe}_history.json'
    with open(history_file_path, 'w') as json_file:
        json.dump(history_data, json_file, indent=4)
    
    print(f"Price history data saved to: {history_file_path}")

def generate_item_trends(item_ids: List[int]):
    """Main function to generate trends for multiple items"""
    for item_id in item_ids:
        create_price_trend_graph(item_id)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python item_trends_graphs.py generate_item_trends <item_id1> <item_id2> ...")
        sys.exit(1)
    
    # Convert arguments to integers
    item_ids = [int(id) for id in sys.argv[2:]]
    globals()[sys.argv[1]](item_ids)