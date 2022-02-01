import plotly.graph_objects as go
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import os
import time
import datetime
from datetime import timedelta,date

import flask

# Tous les programmes qui permettent de récupérer les données
import read_aida
import lecture_mesoNH
import lecture_surfex

import comp_obs_model
import sondages


#########################
#
#   Rejeu MésoNH
#
#########################


############### Données ###############
dico_vars_mesonh = {
        "CTURB" : {
                "name" : "Turbulence scheme",
                "values" : ["NONE", "TKEL"]
        },
        "CCLOUD" : {
                "name" : "Microphysical scheme",
                "values" : ["NONE", "REVE", "KESS", "C2R2", "KHKO", "ICE3", "ICE4", "LIMA"]
        },
        "CRAD" : {
                "name" : "Radiative transfer scheme",
                "values" : ["NONE", "TOPA", "FIXE", "ECMW", "ECRA"]
        }}


############### Widgets ###############
        
calendrier = html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',
        first_day_of_week=1,
        min_date_allowed=date(2015, 1, 1),
        max_date_allowed=date(tomorow.year, tomorow.month, tomorow.day),
        start_date=yesterday,
        display_format = "DD/MM/YYYY",
        initial_visible_month=date(today.year, today.month, today.day),
        end_date=yesterday,
        minimum_nights=0,
    ),html.Div(id='output-container-date-picker-range')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"})

    
all_params_id = []
all_params_html = []
inputs =[]
for var in dico_vars_mesonh :
    
    title = html.Div(dico_vars_mesonh[var]["name"]+' :',className="four columns",style={"text-align": "right", "justifyContent":"center"})    
    multi_select_line = html.Div([
        dcc.Dropdown(
            id="multi_select_line_"+var,
            options=[{"value":label, "label":label} for label in dico_vars_mesonh[var]["values"]],
            multi=False,
            clearable = False
        )],className="six columns",style={"text-align": "center", "justifyContent":"center"})
    all_params_html.append(title)
    all_params_html.append(multi_select_line)
    inputs.append(State("multi_select_line_"+var,'value'))
    all_params_id.append("multi_select_line_"+var)

############### Callbacks ###############
import mesonh
import shortuuid

user_params={}

@app.callback(Output('my-output','children'),Input('button','n_clicks'),)

def simu(n_clicks):
    global user_params
    if n_clicks is not None and n_clicks == 1:
        user_params["id"]=shortuuid.uuid()[:4]
        content=[html.H5([html.Span('Simulation en cours ! Vous pouvez fermer la page, votre simulation sera accessible avec l\'identifiant : '),html.Span(user_params["id"],style={"font-weight":"bold"}),
                 html.Br(),html.Span('Gardez-le précieusement ! La simulation dure environ 5-10 min')])]
        return content
    else:
        return None
    
@app.callback(Output('loading-1','children'),[Input('button','n_clicks'),
                                                Input('my-date-picker-range','start_date'),
                                                Input('my-date-picker-range','end_date')],inputs)

def loader_func(n_clicks,start_date,end_date,*arg):
    
    time.sleep(1)
    start_date=date.fromisoformat(start_date)
    end_date=date.fromisoformat(end_date)
    for i,var in enumerate(dico_vars_mesonh):
        user_params[var]=arg[i]
        
    if n_clicks is not None and n_clicks == 1:
        nb_jour = (end_date-start_date).days
        for i in range(nb_jour+1):
            date_run=start_date+timedelta(days=i)
            today_str=date_run.strftime('%Y-%m-%dT00:00:00')
            print(start_date)
            mesonh.MesoNH(date_run=today_str, model_couplage="AROME", type_forcage="MODEL", user_params=user_params)
                
        return html.H2('Simulation terminée !')
    else:
        return None

############### Layout ###############

row1=html.Div(children=all_params_html, className="twelve columns")

menu = html.Div([
        dcc.Link('Notice__', href='/MeteopoleX/notice'),
        dcc.Link('__Comparaisons Obs MétéoFlux/Modèles__', href='/MeteopoleX/'),
        dcc.Link('__Sondages__', href='/MeteopoleX/rs'),
        dcc.Link('__Rejeu SURFEX', href='/MeteopoleX/surfex')
        ],className="twelve columns",style={"text-align": "right", "justifyContent":"center"})

mesoNH_layout = html.Div([
    html.H1('Rejeu de MésoNH'),
    menu,
    html.Br(),
    calendrier,
    html.Br(),
    row1,
    html.Br(),
    html.Br(),
    html.Div(html.Button('Lancer la simulation MésoNH', id='button'), style={"margin-top": "100px"}),
    html.Br(),
    html.Br(),
    html.Div(id='my-output'),
    html.Br(),
    html.Br(),
    html.Br(),
    dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1")
        )
],className="twelve columns",style={"text-align": "center", "justifyContent":"center"})


