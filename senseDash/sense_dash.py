
## Packages ##

import dash
import dash_html_components as html
import dash_core_components as dcc

import pandas as pd
import plotly.express as px

from sense_hat import SenseHat
from time import sleep
from datetime import datetime


## Settings ##

daily_time = 60
weekly_time = 60 * 60
monthly_time = 


## SenseHat ##

sense = SenseHat()

# Variables

measurements = {
	'datetime': [],
	'temp': [],
	'humidity': [],
	'pressure': []
}

# Measurements

while True:
	datetime_now = datetime()
	temp_now = round(sense.temp, 1)
	humidity_now = round(sense.humidity, 1)
	pressure_now = round(sense.pressure)
	sleep(daily_time)


## Screen ##

# Variables

sense.low_light = True

green = (0, 100, 0)
red = (100, 0, 0)
blue = (0, 0, 100)
white = (100, 100, 100)

index = 0
sensors = ['time', 'temp', 'humidity', 'pressure']
selection = False


# Functions

def selection_screen(mode):
    if mode == "temp":
        show_t()
    elif mode == "pressure":
        show_p()
    elif mode == "humidity":
        show_h()

def sensor_screen(mode):
    if mode == 'time':
        time = datetime.now().strftime('%H:%M')
        sense.show_message(str(time), text_colour=white)
    elif mode == 'temp':
        temp = round(sense.temp, 1)
        sense.show_message(str(temp) + '\'C', text_colour=white)
    elif mode == 'humidity':
        humidity = round(sense.humidity, 1)
        sense.show_message(str(humidity) + '%', text_colour=white)
    elif mode == 'pressure':
        pressure = round(sense.pressure)
        sense.show_message(str(pressure) + ' mB', text_colour=white)


# Main loop

try:
    while True:
        for event in sense.stick.get_events():
            if event.action == 'pressed':
                if event.direction == 'middle':
                    selection = True
                elif event.direction == "left":
                    index -= 1
                    selection = True
                elif event.direction == "right":
                    index += 1
                    selection = True
                if selection:
                    current_mode = sensors[index % 3]
                    sensor_screen(current_mode)
                    selection = False
        if not selection:
            sense.clear()
except KeyboardInterrupt:
    sense.clear()


## Dash ##

app = dash.Dash(__name__)

app.layout = html.Div(children=[
        html.Div(dcc.Graph(figure=px.line(data, x='datetime', y='temp'))),
        html.Div(dcc.Graph(figure=px.line(data, x='datetime', y='humidity'))),
        html.Div(dcc.Graph(figure=px.line(data, x='datetime', y='pressure')))
])

if __name__ == '__main__':
    app.run_server(debug=False, port=8080, host='12.12.12.12')
