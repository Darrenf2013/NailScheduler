"""
Fuel Price Finder - Proof of Concept
Fetches live fuel prices in Ireland and displays them in HTML format
"""

import json
from datetime import datetime
from typing import List, Dict
import math

# For production, you would use:
# import requests
# For this POC, we'll use sample data


class FuelStation:
    """Represents a fuel station with pricing information"""

    def __init__(self, name: str, address: str, latitude: float, longitude: float,
                 diesel_price: float, petrol_price: float, last_updated: str):
        self.name = name
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.diesel_price = diesel_price
        self.petrol_price = petrol_price
        self.last_updated = last_updated
        self.distance = None

    def calculate_distance(self, user_lat: float, user_lon: float) -> float:
        """Calculate distance using Haversine formula (in km)"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1 = math.radians(user_lat), math.radians(user_lon)
        lat2, lon2 = math.radians(self.latitude), math.radians(self.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        self.distance = R * c
        return self.distance


class FuelPriceFinder:
    """Main class for fetching and displaying fuel prices"""

    def __init__(self):
        self.stations = []

    def fetch_live_data(self):
        """
        Fetch live fuel price data from API
        For POC, using sample data based on real Irish locations

        In production, you would use:
        - GlobalPetrolPrices.com API (paid)
        - Web scraping from pumps.ie or petrolprices.ie (check terms of service)
        """

        # Sample data representing Dublin area fuel stations
        # Prices in EUR per liter (realistic for Ireland Nov 2025)
        sample_data = [
            {
                "name": "Applegreen Dublin Road",
                "address": "Dublin Road, Drogheda, Co. Louth",
                "latitude": 53.7143,
                "longitude": -6.3486,
                "diesel_price": 1.67,
                "petrol_price": 1.72,
                "last_updated": "2025-11-26 10:30"
            },
            {
                "name": "Topaz Swords",
                "address": "Main Street, Swords, Co. Dublin",
                "latitude": 53.4597,
                "longitude": -6.2181,
                "diesel_price": 1.65,
                "petrol_price": 1.70,
                "last_updated": "2025-11-26 09:15"
            },
            {
                "name": "Circle K Malahide",
                "address": "Coast Road, Malahide, Co. Dublin",
                "latitude": 53.4509,
                "longitude": -6.1543,
                "diesel_price": 1.69,
                "petrol_price": 1.74,
                "last_updated": "2025-11-26 08:45"
            },
            {
                "name": "Maxol Donabate",
                "address": "Main Street, Donabate, Co. Dublin",
                "latitude": 53.4864,
                "longitude": -6.1511,
                "diesel_price": 1.64,
                "petrol_price": 1.69,
                "last_updated": "2025-11-26 11:00"
            },
            {
                "name": "Texaco Balbriggan",
                "address": "Dublin Street, Balbriggan, Co. Dublin",
                "latitude": 53.6083,
                "longitude": -6.1819,
                "diesel_price": 1.66,
                "petrol_price": 1.71,
                "last_updated": "2025-11-26 10:00"
            },
            {
                "name": "Applegreen Lusk",
                "address": "Main Street, Lusk, Co. Dublin",
                "latitude": 53.5269,
                "longitude": -6.1664,
                "diesel_price": 1.63,
                "petrol_price": 1.68,
                "last_updated": "2025-11-26 09:30"
            }
        ]

        # Convert to FuelStation objects
        self.stations = [FuelStation(**station) for station in sample_data]

        return self.stations

    def find_nearest_cheapest(self, user_lat: float, user_lon: float,
                              fuel_type: str = 'diesel', max_distance: float = 20.0) -> List[FuelStation]:
        """
        Find nearest and cheapest fuel stations

        Args:
            user_lat: User's latitude
            user_lon: User's longitude
            fuel_type: 'diesel' or 'petrol'
            max_distance: Maximum distance in km

        Returns:
            List of fuel stations sorted by price
        """
        # Calculate distances
        for station in self.stations:
            station.calculate_distance(user_lat, user_lon)

        # Filter by distance
        nearby_stations = [s for s in self.stations if s.distance <= max_distance]

        # Sort by price
        price_attr = f"{fuel_type}_price"
        nearby_stations.sort(key=lambda x: getattr(x, price_attr))

        return nearby_stations

    def generate_html(self, stations: List[FuelStation], fuel_type: str,
                      user_location: str = "Dublin Area") -> str:
        """Generate HTML display of fuel prices"""

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fuel Price Finder - Ireland</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 30px;
            text-align: center;
        }}

        h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}

        .info-box {{
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}

        .info-box h2 {{
            color: #667eea;
            margin-bottom: 10px;
        }}

        .station-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .station-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }}

        .station-card.cheapest {{
            border: 3px solid #4CAF50;
        }}

        .cheapest-badge {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: #4CAF50;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}

        .station-name {{
            font-size: 1.5em;
            color: #333;
            margin-bottom: 10px;
            font-weight: bold;
        }}

        .station-address {{
            color: #666;
            margin-bottom: 15px;
            font-size: 1em;
        }}

        .station-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}

        .detail-item {{
            background: #f5f5f5;
            padding: 12px;
            border-radius: 8px;
        }}

        .detail-label {{
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .detail-value {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}

        .price {{
            color: #667eea;
            font-size: 1.5em;
        }}

        .distance {{
            color: #764ba2;
        }}

        .last-updated {{
            font-size: 0.85em;
            color: #999;
            margin-top: 15px;
            font-style: italic;
        }}

        .fuel-type-selector {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .fuel-type-selector span {{
            background: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            color: #667eea;
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
        }}

        .api-note {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        .api-note strong {{
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⛽ Fuel Price Finder</h1>
            <p class="subtitle">Find the cheapest fuel near you in Ireland</p>
        </header>

        <div class="api-note">
            <strong>📌 Proof of Concept:</strong> This demo uses sample data. In production, it would fetch live prices from APIs like GlobalPetrolPrices.com or scrape from pumps.ie/petrolprices.ie
        </div>

        <div class="info-box">
            <h2>Your Location: {user_location}</h2>
            <p>Showing <strong>{fuel_type.capitalize()}</strong> prices at nearby stations (within 20km)</p>
            <p>Found <strong>{len(stations)}</strong> station(s)</p>
        </div>

        <div class="fuel-type-selector">
            <span>Selected Fuel: {fuel_type.upper()}</span>
        </div>
"""

        # Add station cards
        for idx, station in enumerate(stations):
            is_cheapest = idx == 0
            cheapest_class = "cheapest" if is_cheapest else ""
            price = station.diesel_price if fuel_type == 'diesel' else station.petrol_price

            html += f"""
        <div class="station-card {cheapest_class}">
            {f'<div class="cheapest-badge">💰 Cheapest!</div>' if is_cheapest else ''}
            <div class="station-name">{station.name}</div>
            <div class="station-address">📍 {station.address}</div>

            <div class="station-details">
                <div class="detail-item">
                    <div class="detail-label">{fuel_type.capitalize()} Price</div>
                    <div class="detail-value price">€{price:.2f}/L</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Distance</div>
                    <div class="detail-value distance">{station.distance:.1f} km</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Petrol</div>
                    <div class="detail-value">€{station.petrol_price:.2f}/L</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Diesel</div>
                    <div class="detail-value">€{station.diesel_price:.2f}/L</div>
                </div>
            </div>

            <div class="last-updated">Last updated: {station.last_updated}</div>
        </div>
"""

        html += """
        <div class="footer">
            <p>💡 Tip: Prices are updated regularly. Check back often for the latest deals!</p>
            <p style="margin-top: 10px;">Data sources: GlobalPetrolPrices.com, Pumps.ie, PetrolPrices.ie</p>
        </div>
    </div>
</body>
</html>
"""
        return html


def main():
    """Main function to run the fuel price finder"""

    # Initialize finder
    finder = FuelPriceFinder()

    # Fetch live data
    print("Fetching fuel price data...")
    finder.fetch_live_data()
    print(f"Found {len(finder.stations)} stations")

    # User location (example: Dublin coordinates)
    # In production, you would get this from browser geolocation or user input
    user_lat = 53.4808  # Dublin North
    user_lon = -6.1817

    # Find cheapest diesel stations nearby
    print("\nFinding cheapest diesel stations...")
    diesel_stations = finder.find_nearest_cheapest(
        user_lat, user_lon,
        fuel_type='diesel',
        max_distance=20.0
    )

    # Generate HTML
    html_output = finder.generate_html(
        diesel_stations,
        fuel_type='diesel',
        user_location="Dublin North Area"
    )

    # Save to file
    output_file = 'fuel_prices.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"\n✅ HTML file generated: {output_file}")
    print(f"\n📊 Results Summary:")
    print(f"   Location: Dublin North Area")
    print(f"   Fuel Type: Diesel")
    print(f"   Stations Found: {len(diesel_stations)}")

    if diesel_stations:
        cheapest = diesel_stations[0]
        print(f"\n💰 Cheapest Option:")
        print(f"   {cheapest.name}")
        print(f"   Price: €{cheapest.diesel_price:.2f}/L")
        print(f"   Distance: {cheapest.distance:.1f} km")
        print(f"   Address: {cheapest.address}")

    print("\n" + "="*60)
    print("To view the results, open fuel_prices.html in your browser")
    print("="*60)


if __name__ == "__main__":
    main()
