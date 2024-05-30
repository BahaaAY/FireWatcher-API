import os
import httpx

async def fetch_weather_data(lat: float, lon: float) -> dict:
    """
    Fetches weather data from the WeatherAPI using provided latitude and longitude.
    Returns the response as a JSON dictionary.
    """
    # Retrieve the API key from environment variables
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise ValueError("API key is not configured")

    # Build the API URL
    url = f"https://api.weatherapi.com/v1/current.json?q={lat},{lon}&lang=en&key={api_key}"

    # Make an asynchronous HTTP GET request
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch weather data, status code {response.status_code}")

    # Return the JSON response
    return response.json()