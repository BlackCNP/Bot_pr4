
import aiohttp
import logging


OWM_API_KEY = "837b69b2fd6f3e781972f83bd4470fbe"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

async def get_weather(city_name: str) -> str:
    """
    Асинхронно отримує погоду для вказаного міста з OpenWeatherMap.
    Повертає рядок з інформацією про погоду або повідомлення про помилку.
    """
    params = {
        'q': city_name,
        'appid': OWM_API_KEY,
        'units': 'metric',  
        'lang': 'uk'      
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    main = data['main']
                    weather_desc = data['weather'][0]['description']
                    temp = main['temp']
                    feels_like = main['feels_like']
                    city = data['name']
                    return (f"Погода в місті {city}:\n"
                            f"Температура: {temp}°C (відчувається як {feels_like}°C)\n"
                            f"Опис: {weather_desc.capitalize()}")
                elif response.status == 404:
                    return f"🤷 Місто '{city_name}' не знайдено. Спробуйте іншу назву."
                elif response.status == 401:
                    logging.error("Помилка API ключа OpenWeatherMap.")
                    return "❌ Виникла проблема з сервісом погоди (невірний ключ). Спробуйте пізніше."
                else:
                    logging.error(f"Помилка OpenWeatherMap: Статус {response.status}, Відповідь: {await response.text()}")
                    return f"❌ Виникла помилка при отриманні погоди (код: {response.status}). Спробуйте пізніше."
        except aiohttp.ClientConnectorError as e:
            logging.error(f"Помилка з'єднання з OpenWeatherMap: {e}")
            return "❌ Не вдалося підключитися до сервісу погоди. Перевірте інтернет-з'єднання."
        except Exception as e:
            logging.exception("Неочікувана помилка при отриманні погоди:")
            return "❌ Сталася неочікувана помилка при отриманні погоди."