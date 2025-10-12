from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def geocode_city(city):
    params = {"q": city, "format": "json", "limit": 1}
    headers = {"User-Agent": "CafeFinder/1.0"}
    res = requests.get(NOMINATIM_URL, params=params, headers=headers)
    data = res.json()
    if not data:
        return None
    return float(data[0]["lat"]), float(data[0]["lon"])

def get_cafes(lat, lon, radius=2000):
    query = f"""
    [out:json][timeout:25];
    node["amenity"="cafe"](around:{radius},{lat},{lon});
    out;
    """
    headers = {"User-Agent": "CafeFinder/1.0"}
    res = requests.post(OVERPASS_URL, data={"data": query}, headers=headers)
    data = res.json()
    cafes = []
    for item in data["elements"]:
        cafes.append({
            "id": item["id"],
            "name": item["tags"].get("name", "Unnamed Café"),
            "lat": item["lat"],
            "lon": item["lon"],
        })
    return cafes

@app.route("/search")
def search():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City parameter is required"}), 400
    coords = geocode_city(city)
    if not coords:
        return jsonify({"error": "City not found"}), 404
    lat, lon = coords
    cafes = get_cafes(lat, lon)
    return jsonify({"city": city, "lat": lat, "lon": lon, "cafes": cafes})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port, debug=True)
