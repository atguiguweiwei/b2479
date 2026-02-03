# backend/item_prices.py
import requests
import json
import os
import sys
from typing import Dict, Any, Optional

# Create directories if they don't exist
os.makedirs('backend/item_prices', exist_ok=True)
os.makedirs('backend/item_trends', exist_ok=True)

def get_item_price(item_id: int) -> Optional[Dict[str, Any]]:
    """Fetch item price data from OSRS API"""
    url = f"https://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item={item_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for item {item_id}: {e}")
        return None

def save_item_price(data: Dict[str, Any]):
    """Save item price data to JSON file"""
    item_id = data['item']['id']
    item_name = data['item']['name'].replace(' ', '_').replace('/', '_').replace('\\', '_')
    
    # Save to JSON file
    price_file_path = f'backend/item_prices/{item_id}_{item_name}.json'
    with open(price_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"Item price data saved to {price_file_path}")
    return price_file_path

def get_item_prices(item_ids: list):
    """Main function to get prices for multiple items"""
    for item_id in item_ids:
        print(f"Fetching price data for item ID: {item_id}")
        
        item_data = get_item_price(item_id)
        
        if item_data is None:
            print(f"Failed to fetch data for item {item_id}")
            continue
        
        # Save to JSON
        save_item_price(item_data)
        
        print(f"Successfully processed data for item {item_id}: {item_data['item']['name']}")
        print(f"Current price: {item_data['item']['current']['price']}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python item_prices.py get_item_prices <item_id1> <item_id2> ...")
        sys.exit(1)
    
    # Convert arguments to integers
    item_ids = [int(id) for id in sys.argv[2:]]
    globals()[sys.argv[1]](item_ids)