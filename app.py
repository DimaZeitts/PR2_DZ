from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = 'yXcUn6haV3nAcW1UlLUlbe6LEozZwVUu'

def get_weather_data(cities, api_key):
    weather_data_list = []
    for city in cities:
        location_key = fetch_location_key(city, api_key)
        if location_key:
            weather_data = fetch_weather_forecast(location_key, api_key)
            if weather_data:
                weather_data['city'] = city
                weather_data_list.append(weather_data)
    return weather_data_list

def fetch_location_key(city, api_key):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search"
    params = {'apikey': api_key, 'q': city}
    response = requests.get(url, params=params)
    if response.status_code == 200 and response.json():
        return response.json()[0]['Key']
    print(f"Ошибка: Город {city} не найден или не удалось получить данные о местоположении.")
    return None

def fetch_weather_forecast(location_key, api_key):
    forecast_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
    forecast_params = {'apikey': api_key, 'metric': 'true', 'details': 'true'}
    forecast_response = requests.get(forecast_url, params=forecast_params)
    if forecast_response.status_code == 200:
        forecast_data = forecast_response.json().get('DailyForecasts', [{}])[0]
        return {
            'temperature': forecast_data.get('Temperature', {}).get('Maximum', {}).get('Value', 0),
            'wind_speed': round(forecast_data.get('Day', {}).get('Wind', {}).get('Speed', {}).get('Value', 0) * 0.27778, 2),
            'precipitation_probability': forecast_data.get('Day', {}).get('PrecipitationProbability', 0)
        }
    print(f"Ошибка: Не удалось получить прогноз погоды для ключа {location_key}.")
    return None

def is_bad_weather(weather_data):
    conditions = []
    if weather_data['temperature'] < 0:
        conditions.append("холодно")
    elif weather_data['temperature'] > 30:
        conditions.append("жарко")
    if weather_data['wind_speed'] > 40:
        conditions.append("ветрено")
    if weather_data['precipitation_probability'] > 50:
        conditions.append("возможны осадки")
    return conditions

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_info = []
    error_message = None
    if request.method == 'POST':
        city1 = request.form.get('city1')
        city2 = request.form.get('city2')
        if city1 and city2:
            city_list = [city1.strip(), city2.strip()]
            weather_info = get_weather_data(city_list, API_KEY)
            for weather in weather_info:
                conditions = is_bad_weather(weather)
                weather['condition'] = "Плохая погода: " + ", ".join(conditions) if conditions else "Хорошая погода"
        else:
            error_message = 'Пожалуйста, введите названия обоих городов.'
    return render_template('index.html', weather_info=weather_info, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)