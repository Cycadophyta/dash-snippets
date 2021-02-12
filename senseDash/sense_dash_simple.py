import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
#import pandas as pd
from sense_hat import SenseHat
from time import sleep
from datetime import datetime
from collections import deque


# Variables #

n_daily_readings = 10
update_frequency = 1  # In seconds


# SenseHat # 

sense = SenseHat()

date_time = deque(maxlen=20)
temperature = deque(maxlen=20)
humidity = deque(maxlen=20)
pressure = deque(maxlen=20)

def update_datetime():
    return datetime.now().replace(microsecond=0)

def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = int(f.read()) / 1000.0
    return temp

def update_temperature():
    t = sense.temperature
    t_cpu = get_cpu_temperature()
    t_corrected = t - ((t_cpu-t)/1.5)
    return round(t_corrected, 1)

def update_humidity():
    return round(sense.humidity, 1)

def update_pressure():
    return round(sense.pressure, 1)


# Dash # 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__) #, external_stylesheets=external_stylesheets)
#app.config.suppress_callback_exceptions = True


app.layout = html.Div([
    html.H1('SenseDash'),
    dcc.Graph(id='temperature_graph', animate=True),
    dcc.Graph(id='humidity_graph', animate=True),
    dcc.Interval(
        id = 'interval',
        interval = update_frequency * 1000  # in milliseconds
    )
])


@app.callback(Output('temperature_graph', 'figure'),
              [Input('interval', 'n_intervals')])
def temperature_graph(n):
    global date_time
    global temperature
    date_time.append(update_datetime())
    temperature.append(update_temperature())
    data = go.Scatter(
        x=list(date_time), y=list(temperature), 
        name='Temperature', mode='lines+markers'
    )
    return {
        'data': [data], 
        'layout': go.Layout(
            xaxis=dict(range=[min(date_time), max(date_time)]),
            yaxis=dict(range=[min(temperature), max(temperature)]),
            title='Temperature',
            yaxis_title='Temperature (C)'
        )
    }


@app.callback(Output('humidity_graph', 'figure'),
              [Input('interval', 'n_intervals')])
def temperature_graph(n):
    global date_time
    global humidity
    #date_time.append(update_datetime())
    humidity.append(update_humidity())
    data = go.Scatter(
        x=list(date_time), y=list(humidity), 
        name='Humidity', mode='lines+markers'
    )
    return {
        'data': [data], 
        'layout': go.Layout(
            xaxis=dict(range=[min(date_time), max(date_time)]),
            yaxis=dict(range=[min(humidity), max(humidity)]),
            title='Humidity',
            yaxis_title='Humidity (%)'
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='192.168.1.136')
