from fastapi.testclient import TestClient
#from ..routers.health import router
from ..routers.prediction import router

client = TestClient(router)

'''
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "Api is up and running!"}
'''

def test_predict():
    response = client.post(
        "/mbajk/predict",
        json=[
        {
        "available_bike_stands": 15,
        "bike_stands": 20,
        "temperature": 16.5,
        "relative_humidity": 60.0,
        "dew_point": 10.0,
        "apparent_temperature": 15.5,
        "precipitation": 0.0,
        "wind_speed": 8.0,
        "surface_pressure": 985.0
        },
        {
        "available_bike_stands": 12,
        "bike_stands": 20,
        "temperature": 17.0,
        "relative_humidity": 62.0,
        "dew_point": 10.5,
        "apparent_temperature": 16.0,
        "precipitation": 0.0,
        "wind_speed": 7.0,
        "surface_pressure": 986.0
        }
    ],
    )
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert isinstance(response.json()["prediction"], int)
    assert response.json()["prediction"] >= 0
    assert response.json()["prediction"] <= 100

''' 
def test_predict_fail():
    response = client.post(
        "/mbajk/predict",
        json=[
        {
        "available_bike_stands": 15,
        "bike_stands": 20,
        "temperature": 16.5,
        "relative_humidity": 60.0,
        "dew_point": 10.0,
        "apparent_temperature": 15.5,
        "precipitation": 0.0,
        "wind_speed": 8.0,
        "surface_pressure": 985.0
        }
    ]
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Data must contain 2 items"
'''