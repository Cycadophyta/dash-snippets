import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
#import pandas as pd
from sense_hat import SenseHat
from time import sleep
from datetime import datetime
from collections import deque
import paho.mqtt.client as mqtt
import json
from dateutil import parser


# Variables #

n_daily_readings = 10
update_frequency = 1  # In seconds
enviro_readings = 4 * 24


# mqtt #

mqtt_server = "localhost"
mqtt_channels = ['enviro']

connection_status = 'Disconnected'

enviro_data = {}

enviro_datetime = deque(maxlen=enviro_readings)
enviro_cpu_temp = deque(maxlen=1)
enviro_temperature = deque(maxlen=enviro_readings)
enviro_humidity = deque(maxlen=enviro_readings)
enviro_pressure = deque(maxlen=enviro_readings)
enviro_oxidising = deque(maxlen=enviro_readings)
enviro_reducing = deque(maxlen=enviro_readings)
enviro_nh3 = deque(maxlen=enviro_readings)


def on_connect(client, userdata, flags, rc):
    ''' The callback for when the client connects to the server.'''
    if rc == 0:
        print("Connected OK")
        connection_status = 'Connected'
    else:
        print("Bad connection Returned code=", rc)
        connection_status = 'Disconnected'
    #connect_to_channels(mqtt_channels)  # Renews subscriptions if connection lost.


def on_message(client, userdata, msg):
    '''The callback for when a PUBLISH message is received from the server.'''
    enviro_data = json.loads(str(msg.payload.decode('utf-8', 'ignore')))
    
    #global enviro_cpu_temp
    enviro_datetime.append(parser.parse(enviro_data['strtime']))
    enviro_cpu_temp.append(enviro_data['cpu_temp'])
    enviro_temperature.append(enviro_data['temperature'])
    enviro_humidity.append(enviro_data['humidity'])
    enviro_pressure.append(enviro_data['pressure'])
    enviro_oxidising.append(enviro_data['oxidised'])
    enviro_reducing.append(enviro_data['reduced'])
    enviro_nh3.append(enviro_data['nh3'])
    

def connect_to_channels(channels):
    for channel in channels:
        client.subscribe(channel)
        print(f'Connected to: {channel}')


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(mqtt_server, 1883, 60)

connect_to_channels(mqtt_channels)
 
client.loop_start()



# SenseHat # 

sense = SenseHat()

sense_datetime = deque(maxlen=20)
sense_temperature = deque(maxlen=20)
sense_humidity = deque(maxlen=20)
sense_pressure = deque(maxlen=20)

def update_datetime():
    return datetime.now().replace(microsecond=0)

def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = int(f.read()) / 1000.0
    return round(temp, 1)

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

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
#app.config.suppress_callback_exceptions = True

def create_card(card_id, title): #, description):
    return dbc.Card(
        dbc.CardBody([
            html.H4(title, id=f"{card_id}-title"),
            html.H2("100", id=f"{card_id}-value"),
            #html.P(description, id=f"{card_id}-description")
        ])
    )

app.layout = html.Div([
    html.H1('Enviroplus'),
    dbc.Row([
        dbc.Col(create_card('enviro_cpu_temp', 'Enviro CPU Temp')),
        dbc.Col(create_card('sense_cpu_temp', 'SenseHat CPU Temp'))
    ]),
    dcc.Graph(id='sense_temp_graph', animate=True),
    dcc.Graph(id='sense_humidity_graph', animate=True),
    #html.H2(id='enviro_cpu_temp'),
    #html.H2(id='sense_cpu_temp'),
    #dcc.Graph(id='oxidising_graph', animate=True),
    #dcc.Graph(id='reducing_graph', animate=True),
    #dcc.Graph(id='nh3_graph', animate=True),
    dcc.Interval(
        id = 'interval',
        interval = update_frequency * 1000  # in milliseconds
    )
])


@app.callback([
    Output('enviro_cpu_temp-value', 'children'),
    Output('sense_cpu_temp-value', 'children')
], [Input('interval', 'n_intervals')])
def cpu_temps(n):
    return(
        f'{next(iter(enviro_cpu_temp), None)} C', 
        f'{get_cpu_temperature()} C'
    )


@app.callback(Output('sense_temp_graph', 'figure'),
              [Input('interval', 'n_intervals')])
def temperature_graph(n):
    global sense_datetime
    global sense_temperature
    sense_datetime.append(update_datetime())
    sense_temperature.append(update_temperature())
    data = go.Scatter(
        x=list(sense_datetime), y=list(sense_temperature), 
        name='Temperature', mode='lines+markers'
    )
    return {
        'data': [data], 
        'layout': go.Layout(
            xaxis=dict(range=[min(sense_datetime), max(sense_datetime)]),
            yaxis=dict(range=[0, 50]),
            title='Temperature',
            yaxis_title='Temperature (C)',
            template='plotly_dark'
        )
    }


@app.callback(Output('sense_humidity_graph', 'figure'),
              [Input('interval', 'n_intervals')])
def humidity_graph(n):
    global sense_datetime
    global sense_humidity
    #date_time.append(update_datetime())
    sense_humidity.append(update_humidity())
    data = go.Scatter(
        x=list(sense_datetime), y=list(sense_humidity), 
        name='Humidity', mode='lines+markers'
    )
    return {
        'data': [data], 
        'layout': go.Layout(
            xaxis=dict(range=[min(sense_datetime), max(sense_datetime)]),
            yaxis=dict(range=[0, 100]),
            title='Humidity',
            yaxis_title='Humidity (%)',
            template='plotly_dark'
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='192.168.1.136')

