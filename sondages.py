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





########################
#
#   Sondages
#
########################


############### Données ###############

import radio_sondage

params_rs = ["Température","Humidité relative","Vent"]
# Les 3 paramètres que nous allons tracer

options_params_rs = {"Température":
                         {"label":"Température",
                          "unit":"°C"},
                     "Humidité relative":
                         {"label":"Humidité relative",
                          "unit":"%"},
                     "Vent":
                         {"label":"Vent",
                          "unit":"m/s"}
             }
# Ce dictionnaire permet de nommer les axes des graphiques

options_models = {"Gt":{
                    "name":"MNH-ARPEGE",
                    "line":"dot"}, 
                  "Rt":{
                    "name":"MNH-AROME",
                    "line":"longdash"},
                  "Tf":{
                    "name":"MNH-OBS",
                    "line":"solid"}}
# Ce dictionnaire attribut des types de ligne à chaque modèle tracé.

heures = {"00h":{
            "value":"00h",
            "num_val":0,
            "color":"black"},
          "3h":{
            "value":"3h",
            "num_val":12,
            "color":"brown"},
          "6h":{
            "value":"6h",
            "num_val":24,
            "color":"red"},
          "9h":{
            "value":"9h",
            "num_val":36,
            "color":"orange"},
          "12h":{
            "value":"12h",
            "num_val":48,
            "color":"green"},
          "15h":{
            "value":"15h",
            "num_val":60,
            "color":"blue"},
          "18h":{
            "value":"18h",
            "num_val":72,
            "color":"purple"},
          "21h":{
            "value":"21h",
            "num_val":84,
            "color":"fuchsia"}}

          # "num_val" est le raang de la valeur correspondant à l'heure, par exemple : puisqu'il y a une valeur tous les quarts d'heure (4 valeurs par heure), pour 9h on prend la 9x4=36ème valeur du paramètre.

day=datetime.date.today()

############### Widgets ###############

calendrier = html.Div([
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        first_day_of_week=1,
        min_date_allowed=date(2015, 1, 1),
        max_date_allowed=date(yesterday.year, yesterday.month, yesterday.day),
        date=yesterday,
        display_format = "DD/MM/YYYY",
        initial_visible_month=date(yesterday.year, yesterday.month, yesterday.day),
    ),html.Div(id='output-container-date-picker-single')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"})

    
colors=[]
for heure in heures:
    colors.append(heures[heure]["color"])
wich_heure = html.Div([
    dcc.Checklist(
        options=[{'label':x,'value': x} for x in heures],
        value=["6h"],
        id='wich_heure',
        labelStyle={'display': 'inline-block',
                    'color': colors},
        )],className="five columns",style={"text-align": "left", "justifyContent":"center"})
# C'est le widget qui permet de cocher l'heure voulue

    
labels=[]
for model in options_models :
    labels.append(options_models[model]["name"])
multi_select_line_chart_model = html.Div([
    dcc.Dropdown(
        id="multi_select_line_chart_model",
        options=[{"value":value, "label":label} for value,label in zip(options_models,labels)],
        value="MésoNH forcé par Arome",
        multi=True,
        clearable = False
    )],className="six columns",style={"text-align": "right", "justifyContent":"center"})
# C'est le widget qui permet de sélectionner les courbes que l'on veut afficher
    
    
#Premier chargement des données à la date d'aujourd'hui
data_rs = radio_sondage.radio_sondage(day,models,params_rs,heures)

# Création des figures
chart={}
for param in params_rs:
    chart[param] = go.Figure()   
    
# Tranformation en HTML  
graph={}
for param in params_rs:        
    graph[param] = dcc.Graph(
            id='graph_' + param,
            figure=chart[param]) 

############### Callbacks ###############

output_rs = []
for param in params_rs:
    output_rs.append(Output('graph_' + param,'figure')) # Graphs qui seront mis à jour
    
    
@app.callback(output_rs,[Input('wich_heure','value'),
                         Input('my-date-picker-single','date'),
                         Input('multi_select_line_chart_model','value')])

def update_rs(wich_heure,date_value,model_choisi):
    
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
    
    # Puis, mise à jour des graphes :
    for param in params_rs:
        chart[param] = go.Figure()
    
    # Extraction des données
    data_rs = radio_sondage.radio_sondage(date_object,models,params_rs,heures)
    # Mise à jour des courbes
    courbe_affichee=[]
    for selection in wich_heure :
        if selection not in courbe_affichee :
            courbe_affichee.append(selection)
            afficher_legende=True
        else :
            afficher_legende=False
        for param in params_rs :
            for model in model_choisi :
                try :
                    chart[param].add_trace(go.Scatter(x=data_rs[model][selection][param], y=data_rs['level'],line=dict(color=heures[selection]["color"],dash=options_models[model]["line"]), mode="lines",name=options_models[model]["name"]+' - '+heures[selection]["value"],showlegend=afficher_legende))
                except KeyError:
                    pass
    list_charts = []
    for param in params_rs:
        chart[param].update_layout(height=500,
                         xaxis_title=options_params_rs[param]["label"]+" ("+options_params_rs[param]["unit"]+")",
                         yaxis_title="Altitude (m agl)",
                         title=param)
        list_charts.append(chart[param])
    
    
    return list_charts

# Le code est largement inspiré de la page "Comparaison Modèles/Obs"
    
    
############### Layout ###############
    
legende=[]
for heure in heures :
    legende.append(html.Div(dcc.Textarea(value=heures[heure]['value'], style={'color':heures[heure]['color'],'width': 50, 'height': 25}),className="one columns",style={"text-align": "left", "justifyContent":"center"}))
# Ces 4 lignes permettent de créer à la chaine les zones de texte pour montrer à l'utilisateur le code couleur choisi

row1= html.Div(children=legende,className="five columns")


all_graphs = []
for param in params_rs:
    all_graphs.append(html.Div(graph[param],className="four columns"))

row2 = html.Div(children=all_graphs, className="twelve columns")


menu = html.Div([
        dcc.Link('Notice__', href='/MeteopoleX/notice'),
        dcc.Link('__Comparaisons Obs MétéoFlux/Modèles__', href='/MeteopoleX/'),
        dcc.Link('__Rejeu MésoNH__', href='/MeteopoleX/mesoNH'),
        dcc.Link('__Rejeu SURFEX', href='/MeteopoleX/surfex')
        ],className="twelve columns",style={"text-align": "right", "justifyContent":"center"})


rs_layout = html.Div([
    html.H1('Sondages'),
    menu,
    calendrier,
    html.Br(),
    html.Br(),
    html.Br(),
    wich_heure,multi_select_line_chart_model,
    html.Div(dcc.Textarea(value="Code couleur :", style={'color':"black"}),className="one columns",style={"text-align": "left", "justifyContent":"center"}),
    row1,row2,
    html.Br(),
],className="twelve columns",style={"text-align": "center", "justifyContent":"center"})


