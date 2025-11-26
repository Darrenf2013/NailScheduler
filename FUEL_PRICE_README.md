# Fuel Price Finder - Ireland 🇮🇪 ⛽

A proof-of-concept Python script that fetches fuel prices in Ireland and displays them in a beautiful HTML interface.

## Features

✅ **Live Fuel Price Data** - Fetch current diesel and petrol prices
✅ **Location-Based Search** - Find cheapest stations near you
✅ **Distance Calculation** - Shows how far each station is
✅ **Beautiful HTML UI** - Modern, responsive design
✅ **Price Comparison** - Easily compare prices across stations
✅ **Highlights Cheapest** - Best deal highlighted automatically

## Quick Start

### Run the Script

```bash
python fuel_prices.py
```

This will:
1. Fetch fuel price data (currently using sample data)
2. Calculate distances from your location
3. Sort stations by price
4. Generate `fuel_prices.html`

### View Results

Open the generated HTML file in any browser:

```bash
# Linux/Mac
open fuel_prices.html

# Or just double-click the file
```

## Current Implementation (POC)

The current version uses **sample data** to demonstrate the concept. It includes:

- 6 sample fuel stations in the Dublin area
- Realistic prices based on November 2025 rates
- Real coordinates for distance calculation
- Haversine formula for accurate distance calculation

## Integrating Live Data

To use real live data, you have several options:

### Option 1: GlobalPetrolPrices.com API (Recommended)

```python
import requests

def fetch_live_data_globalpetrolprices(api_key):
    """Fetch from GlobalPetrolPrices.com API"""
    url = "https://api.globalpetrolprices.com/latest"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"country": "Ireland"}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    # Parse and return stations
    return parse_api_data(data)
```

**Pros:**
- Official API with documentation
- Reliable and updated regularly
- Includes historical data

**Cons:**
- Paid service (free trial available)
- May not have individual station data

### Option 2: Web Scraping Pumps.ie or PetrolPrices.ie

```python
import requests
from bs4 import BeautifulSoup

def scrape_pumps_ie():
    """Scrape fuel prices from pumps.ie"""
    url = "https://pumps.ie/"

    # IMPORTANT: Check terms of service first!
    # Add appropriate headers and respect robots.txt

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Parse the HTML to extract station data
    # (Implementation depends on website structure)

    return stations
```

**Pros:**
- Free to use
- Includes individual station prices
- Community-updated

**Cons:**
- Must respect terms of service
- Website structure may change
- Rate limiting required

### Option 3: Government Data Sources

The EU publishes weekly fuel price bulletins. You can access this data at:

```python
def fetch_eu_oil_bulletin():
    """Fetch from EU Weekly Oil Bulletin"""
    url = "https://energy.ec.europa.eu/oil-bulletin_en"

    # Download and parse CSV/XML data
    # Note: This gives national averages, not individual stations

    return data
```

## Adding Geolocation

To get the user's real location, you can:

### Command Line Input

```python
def get_user_location():
    """Get user location from input"""
    print("Enter your location:")
    location = input("Town/City: ")

    # Use geocoding to convert to coordinates
    # e.g., using geopy library
    from geopy.geocoders import Nominatim

    geolocator = Nominatim(user_agent="fuel_finder")
    location = geolocator.geocode(f"{location}, Ireland")

    return location.latitude, location.longitude
```

### Browser Geolocation (For Web Version)

If you convert this to a web app:

```javascript
// Add to HTML
navigator.geolocation.getCurrentPosition(function(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    // Send to backend
    fetch('/find-fuel', {
        method: 'POST',
        body: JSON.stringify({lat, lon}),
        headers: {'Content-Type': 'application/json'}
    });
});
```

## Customization

### Change Fuel Type

```python
# In main() function, change:
diesel_stations = finder.find_nearest_cheapest(
    user_lat, user_lon,
    fuel_type='petrol',  # Changed from 'diesel'
    max_distance=20.0
)
```

### Adjust Search Radius

```python
# Change max_distance parameter (in kilometers)
diesel_stations = finder.find_nearest_cheapest(
    user_lat, user_lon,
    fuel_type='diesel',
    max_distance=50.0  # Search within 50km
)
```

### Modify User Location

```python
# Change coordinates in main()
user_lat = 53.3498  # Dublin City Center
user_lon = -6.2603
```

## Dependencies

For production use, install these packages:

```bash
pip install requests beautifulsoup4 geopy
```

Current POC requires only Python standard library.

## Converting to Web Application

To integrate this into a Flask app (like your NailScheduler app):

1. **Add a new route** in `routes.py`:

```python
@app.route('/fuel-prices')
def fuel_prices():
    from fuel_prices import FuelPriceFinder

    finder = FuelPriceFinder()
    finder.fetch_live_data()

    # Get user location (from request or session)
    user_lat = request.args.get('lat', 53.4808)
    user_lon = request.args.get('lon', -6.1817)

    stations = finder.find_nearest_cheapest(
        float(user_lat),
        float(user_lon),
        fuel_type=request.args.get('fuel_type', 'diesel')
    )

    return render_template('fuel_prices.html', stations=stations)
```

2. **Create a template** in `templates/fuel_prices.html`

3. **Add to navigation** in your existing app

## Data Sources

This POC demonstrates integration with:

- **GlobalPetrolPrices.com** - API for fuel prices in 135 countries
- **Pumps.ie** - Ireland's fuel price website
- **PetrolPrices.ie** - Find cheapest petrol & diesel prices
- **AA Ireland** - Regular fuel price updates
- **EU Oil Bulletin** - Official weekly fuel price data

## Roadmap

Future enhancements could include:

- [ ] Real-time API integration
- [ ] User authentication and saved locations
- [ ] Price alerts (notify when prices drop)
- [ ] Historical price charts
- [ ] Mobile app version
- [ ] Route optimization (cheapest along your route)
- [ ] Price predictions using ML

## Legal Considerations

⚠️ **Important:** Before deploying to production:

1. Check API terms of service
2. Respect rate limits
3. Don't scrape without permission
4. Include proper attribution
5. Consider data privacy regulations

## License

This is a proof of concept for demonstration purposes.

## Support

For issues or questions about this fuel price finder:
- Check the code comments in `fuel_prices.py`
- Review API documentation for your chosen data source
- Ensure all dependencies are installed

---

**Created:** November 2025
**Status:** Proof of Concept
**Next Step:** Integrate real API for production use
