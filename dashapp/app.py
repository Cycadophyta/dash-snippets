#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 17:51:59 2020

@author: pi
"""

# Packages
import dash
import dash_html_components as html
import dash_core_components as dcc

import pandas as pd
import plotly.express as px

# Data
data = pd.read_csv('~/python/SenseHat/Environment/senselog_2020-08-15.csv', parse_dates=True)

def drop_outliers(data):
    index = data[(data['temp'] >= 50)|(data['temp'] <= 22)].index
    data.drop(index, inplace=True)

    index = data[(data['humidity'] >= 80)|(data['humidity'] <= 40)].index
    data.drop(index, inplace=True)

    index = data[(data['pressure'] >= 1500)|(data['pressure'] <= 0)].index
    data.drop(index, inplace=True)
    
drop_outliers(data)

# Dash app
app = dash.Dash(__name__)

app.layout = html.Div(children=[
        html.Div(dcc.Graph(figure=px.line(data, x='datetime', y='temp'))),
        html.Div(dcc.Graph(figure=px.line(data, x='datetime', y='humidity'))),
        html.Div(dcc.Graph(figure=px.line(data, x='datetime', y='pressure')))
])


if __name__ == '__main__':
    app.run_server(debug=False, port=8080, host='0.0.0.0')