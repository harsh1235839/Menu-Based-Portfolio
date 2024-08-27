import geocoder
from flask_cors import CORS
from flask import Flask, jsonify

app = Flask(__name__)

cors = CORS(app)


@app.route("/locateMe")
def locate():
    # Get the current location based on the IP address
    g = geocoder.ip('me')
    
    # Create a dictionary with location details
    location_data = {
        "IP Address": g.ip,
        "State": g.state,
        "Country": g.country,
        "Latitude": g.latlng[0] if g.latlng else "N/A",
        "Longitude": g.latlng[1] if g.latlng else "N/A",
        "City": g.city
    }
    
    return jsonify(location_data)

if __name__ == '__main__':
    app.run(port=80, host="0.0.0.0")
