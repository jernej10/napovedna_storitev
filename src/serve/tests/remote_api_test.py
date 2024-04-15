import requests

def test_weather_api():
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude=46.562695&longitude=15.62935")
    assert response.status_code == 200


def test_station_api():
    response = requests.get(f"https://api.jcdecaux.com/vls/v1/stations?contract=maribor&apiKey=5e150537116dbc1786ce5bec6975a8603286526b")
    assert response.status_code == 200

