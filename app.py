
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/search")
def search():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City is required"}), 400

    try:
        # Use OpenStreetMap Nominatim API to get city coordinates
        geo_res = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json"},
            headers={"User-Agent": "CaféFinderApp"}
        )
        geo_res.raise_for_status()
        geo_data = geo_res.json()

        if not geo_data:
            return jsonify({"error": "City not found"}), 404

        city_lat = float(geo_data[0]["lat"])
        city_lon = float(geo_data[0]["lon"])

        # For demo purposes, generate fake cafes nearby
        cafes = []
        for i in range(1, 6):
            cafes.append({
                "id": i,
                "name": f"Café {i} in {city}",
                "lat": city_lat + 0.001 * i,
                "lon": city_lon + 0.001 * i
            })

        return jsonify({"cafes": cafes, "lat": city_lat, "lon": city_lon})

    except requests.exceptions.JSONDecodeError:
        return jsonify({"error": "Invalid response from location API"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

