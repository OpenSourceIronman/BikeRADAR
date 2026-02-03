from nicegui import ui
import requests

if __name__ == "__main__":
    response = requests.get('https://on-air.nicegui.io/status/')
    print(response.text)
    ui.label('NiceGUI On Air')


if __name__ == "__mp_main__":
    ui.label('NiceGUI On Air')
    ui.run(native=False, on_air='VBGvymM2zVnRX0vr', port=0)

"""
from nicegui import ui
import os
from dotenv import load_dotenv

if __name__ in {"__main__", "__mp_main__"}:
    load_dotenv()
    onAirKey = os.getenv("ON_AIR_TOKEN")
    print(f"API Key: {onAirKey}")
    ui.label(f"Testing with {onAirKey}")
    ui.label("Hello World!")
    ui.run(native=False, dark=True, window_size=(330, 330), title='Testing On-Air', on_air=onAirKey)
"""
