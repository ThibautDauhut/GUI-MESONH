#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import plotly.graph_objects as go
import numpy as np

import dash
#import dash_core_components as dcc
from dash import dcc

#import dash_html_components as html
from dash import html 

from dash.dependencies import Input, Output, State

import os
import time
import datetime
from datetime import timedelta,date

from dateutil.relativedelta import relativedelta

#from datetime import datetime

import matplotlib.dates as mdates

import flask

# Tous les programmes qui permettent de récupérer les données
import read_aida
import lecture_mesoNH
import lecture_surfex

# Besoin de l'utilisation de dataframes pour les calculs de différences entre obs/modèle (grille temporelle différente)
import pandas as pd



#####################################################################

# Petit préambule sur l'organisation de ce code :
# Toutes les pages du site se touvent ici, elles sont délimités par leur titre de type :


						##############################
						#
						#   Comparaison Obs/Modèles
						#
						##############################

# Chaque page contient 4 parties dans cet ordre :

					############### Données ###############
					############### Widgets ###############
					############### Callbacks ###############
					############### Layout ###############

# Les données contiennent les fonctions nécessaires à la récupérations des valeurs de tous les modèles.
# Les widgets sont les objets qui permettent de choisir quoi afficher (quelles courbes à quelle date/heure/période)
# Les callbacks actualisent la page.
# Le layout est la mise en page.


# La dernière partie du code est :
				##########################################################################################
				#
				#   				Gestion des pages
				#
				##########################################################################################

# qui est, comme son nom l'indique, destinée à la gestion des pages lors de la navigation sur le site.

#####################################################################






#################### Creating App Object ############################               
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] #ou bien https://intra.cnrm.meteo.fr/MeteopoleX/css.css
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css']
# C'est la css qui va permettre la mise en page

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True,title='MeteopoleX',
                requests_pathname_prefix='/MeteopoleX/',
                routes_pathname_prefix='/')
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
server=app.server

#app.config.update({
#                'requests_pathname_prefix': '/MeteopoleX/',
#                'routes_pathname_prefix': '/'
#                })

#app = dash.Dash(
#    requests_pathname_prefix='/MeteopoleX/',
#    routes_pathname_prefix='/')

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

today=datetime.date.today()
#today=datetime.date.today()-timedelta(days=2)
yesterday=today-timedelta(days=1)
end_day=today-timedelta(days=1)
start_day=today-timedelta(days=7)
doy1 = datetime.datetime(int(start_day.year),int(start_day.month),int(start_day.day)).strftime('%j')
doy2 = datetime.datetime(int(end_day.year),int(end_day.month),int(end_day.day)).strftime('%j')


##############################
#
#   Comparaison Obs/Modèles
#
##############################



############### Données ###############
#Lecture des données dans AIDA
dico_params = {
        "tmp_2m": {
                "index_obs" : "tpr_air_bs_c1_%60_Met_%1800",
                "index_model" : "tpr_air2m",
                "title": "Température à 2m",
                "unit" : "°C"
                },
        "tmp_10m": {
                "index_obs" : "tpr_air_ht_c1_%60_Met_%1800",
                "index_model" : "tpr_air10m",
                "title": "Température à 10m",
                "unit" : "°C"
                },
        "hum_rel": {
                "index_obs" : "hum_relcapa_bs_c1_%60_Met_%1800",
                "index_model" : "hum_rel",
                "title": "Humidité relative",
                "unit" : "%"
                },
        "vent_ff10m": {
                "index_obs" : "ven_ff_10mn_c1_UV_%1800",
                "index_model" : "ven_ff10m",
                "title": "Vent moyen à 10m",
                "unit" : "m/s"
                },
        "flx_mvt": {
                "index_obs" : "flx_mvt_Chb_%1800",
                "index_model" : "flx_mvt",
                "title": "Vitesse de friction",
                "unit" : "m/s"
                },
        "flx_chaleur_sens": {
                "index_obs" : "flx_hs_tson_Chb_%1800",
                "index_model" : "flx_hs",
                "title": "Flux de chaleur sensible",
                "unit" : "W/m²"
                },
        "flx_chaleur_lat": {
                "index_obs" : "flx_le_Chb_%1800",
                "index_model" : "flx_le",
                "title": "Flux de chaleur latente",
                "unit" : "W/m²"
                },
        "SWD": {
                "index_obs" : "ray_rgd_cnr1_c2_%60_Met_%1800",
                "index_model" : "ray_rgd",
                "title": "Rayonnement global descendant (SW)",
                "unit" : "W/m²"
                },
        "LWU": {
                "index_obs" : "ray_irm_cnr1_c2_%60_Met_%1800",
                "index_model" : "ray_irm",
                "title": "Rayonnement IR montant (LW)",
                "unit" : "W/m²"
                },
        "t_surface": {
                "index_obs" : "tpr_solIR_c1_%60",
                "index_model" : "",
                "title": "Température de surface",
                "unit" : "°C"
                },
        "t-1": {
                "index_obs" : "tpr_sol1cm_c4_%900_Met_%1800",
                "index_model" : "",
                "title": "Température du sol à -1 cm",
                "unit" : "°C"
                },
        "hu_couche1": {
                "index_obs" : "hum_sol1cm_ec5_c3_%900_Met_%1800",
                "index_model" : "",
                "title": "Humidité de la première couche",
                "unit" : "kg/kg"
                },
        "cumul_RR": {
                "index_obs" : "prp_rr_min_c2_%60_Som_%1800",
                "index_model" : "",
                "title": "Cumuls du pluie sur 30 min",
                "unit" : "mm"
                },
        "altitude_CL": {
                "index_obs" : "",
                "index_model" : "",
                "title": "Altitude de la couche limite",
                "unit" : "m"
                },
        }

# Ce dictionnaire rassemble les spécificités de chaque paramètres tracés. Les 2 'index' sont les noms donnés sur AIDA au paramètre en question, dans les observations et dans les modèles. 
#Le 'title' est le titre du graph qui sera affiché, donc c'est l'utilisateur qui choisi, idem pour le unit, c'est à l'utilisateur de rentrer les bonnes unités.

# DRIVER LECTURE DES SIMULATIONS MESONH ET SURFEX : AJOUT DE NOUVEAU RUN ICI
dico_model={"MésoNH_Arp":
                {'name':'Gt',
                 'color':'purple'},
            "MésoNH_Aro":
                {'name':'Rt',
                 'color':"limegreen"},
            "MésoNH_Obs":
                {'name':'Tf',
                 'color':'orange'},
            "SURFEX_Arp":
                {'name':'Gt',
                 'color':'darkgreen'},
            "SURFEX_Aro":
                {'name':'Rt',
                 'color':'pink'},
            "SURFEX_Obs":
                {'name':'Tf',
                 'color':'gold'}}

params = ["tmp_2m", "tmp_10m","hum_rel","vent_ff10m","flx_mvt","flx_chaleur_sens","flx_chaleur_lat","SWD","LWU","t_surface","t-1","hu_couche1","cumul_RR","altitude_CL"]


# C'est la liste de tous les paramètres qui vont être tracés. Pour toute modification de cette liste, penser à modifier le dico_params en conséquence.
        
models = ["Gt", "Rt","Tf"]

reseaux = ["J-1:00_%3600", "J-1:12_%3600", "J0:00_%3600", "J0:12_%3600"]



def selection_donnees (start_day,end_day):
    
# Cette fonction permet de récupérer les données disponibles sur AIDA, c'est à dire les données des Obs de Météopole Flux, d'Arome et d'Arpège.
# Structure du dictionnaire data qui stocke toutes les données :
#   data={'param '(une valeur de params):
#               {'Tf':
#                       {'values':valeurs numériques prises par le paramètre (param) des obs pendant la période (end_day-start_day),
#                        'time':datetime.date de touts les temps où il y a eu une mesure},
#               'Rt' (ou 'Gt', même structure):
#                       {'reseau' (une valeur de reseaux):
#                           {'value': les valeurs du modèle (Rt ou Gt) pour le paramètre (param) correspondant et un réseau (reseau),
#                            'time': datetime.date de tous les temps où il y a une valeur}
#                       }
#               }
#          } 

    
    doy1 = datetime.datetime(int(start_day.year),int(start_day.month),int(start_day.day)).strftime('%j')
    doy2 = datetime.datetime(int(end_day.year),int(end_day.month),int(end_day.day)).strftime('%j')
    data = {}
    chart = {}
    graph = {}



    for param in params:
        if param not in data:
            data[param] = {}
        for model in models:
            if model not in data[param]:
                data[param][model] = {}
                for reseau in reseaux:
                    if reseau not in data[param][model]:
                        data[param][model][reseau] = {}

                    if model == "Tf":
                        id_aida = dico_params[param]["index_obs"] 
                        (values, time, header)=read_aida.donnees(doy1,doy2,str(start_day.year),id_aida,model) #Read AIDA : lit tous les paramètres alors que selection de données va lire uniquement un parametre specifique
                        data[param][model]['values'] = values
                        data[param][model]['time'] = time 

                        break

                    else:

                        id_aida = dico_params[param]["index_model"] + "_" + reseau 
                        (values, time, header)=read_aida.donnees(doy1,doy2,str(start_day.year),id_aida,model)
                        data[param][model][reseau]['values'] = values

                        data[param][model][reseau]['time'] = time

#Correction des données ARPEGE parfois datées à H-1:59 au lieu de H:00
                        if time is not None:                       
                       
                           i=0
                     
                           for ts in time:

                               if ts.minute == 59. :
 
                                  time[i]  = time[i] + datetime.timedelta(minutes=1)

                                  i=i+1

                               else:

                                  i=i+1  
                                  
                        #Les flux pour AROME et ARPEGE OPER sont agrégés entre H et H+1 : On les replace à H:30 pour davantage de réalisme
                        if param == 'flx_mvt' or param == 'flx_chaleur_sens' or param == 'flx_chaleur_lat' or param == 'SWD' or param == 'LWU' :

                           if time is not None:                       
                       
                              i=0
                     
                              for ts in time:
                      
                                  time[i]  = time[i] - datetime.timedelta(minutes=30)

                                  i=i+1
              


                      
        chart[param] = go.Figure()
        # Tracé des figures
               
        graph[param] = dcc.Graph(
                id='graph_' + param,
                figure=chart[param]
            ) 
         #Tranformation en HTML
         
         # Ces 2 dernières étapes sont essentielles : d'abord on effectue le tracé, puis on le transforme en objet html pour pouvoir l'afficher

    return data, chart, graph



today=datetime.date.today()
#today=datetime.date.today()-timedelta(days=2)
tomorow=today+timedelta(days=1)
yesterday=today-timedelta(days=1)
end_day=today
#start_day=yesterday # Période par défaut : hier et aujourd'hui
start_day=today-timedelta(days=7)

# Première extraction des données
data, chart, graph = selection_donnees(start_day,end_day)
data_mnh=lecture_mesoNH.mesoNH(start_day,end_day,models,params) #Pour ajouter un nouveau run de MesoNH, changer la liste models : en créer une autre
data_surfex=lecture_surfex.surfex(start_day,end_day,models,params)

############### Widgets ###############

calendrier = html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',
        first_day_of_week=1,
        min_date_allowed=date(2015, 1, 1),
        max_date_allowed=date(tomorow.year, tomorow.month, tomorow.day), # Il faut mettre demain pour que la date max soit aujourd'hui
        display_format = "DD/MM/YYYY",
        initial_visible_month=date(today.year, today.month, today.day),
        start_date=yesterday,
        end_date=today,
        minimum_nights=0 # Durée minimum sélectionnable : si =0, durée min = 1 jour c-à-d start_date=end_date
    ),html.Div(id='output-container-date-picker-range')])


multi_select_line_chart_obs = dcc.Dropdown(
        id="multi_select_line_chart_obs",
        options=[{"value":label, "label":label} for label in ["Obs"]],
        value=["Obs"], # Valeur qui s'affiche par défaut (si pas dans la liste des options alors rien n'est affiché)
        multi=True, # Possibilité d'en choisir plusieur
        clearable = False
    )
# Le dcc.Dropdown est un objet dash qui permet l'affichage des options sélectionnables quand on clique dessus, puis la sélection d'une ou plusieurs options.

multi_select_line_chart_ARP = dcc.Dropdown(
        id="multi_select_line_chart_ARP",
        options=[{"value":label, "label":label} for label in ["Arp_J-1_00h","Arp_J-1_12h","Arp_J0_00h","Arp_J0_12h",]],
        value=["Arp_J0_00h","Arp_J-1_12h"],
        multi=True,
        clearable = False
    )

multi_select_line_chart_ARO = dcc.Dropdown(
        id="multi_select_line_chart_ARO",
        options=[{"value":label, "label":label} for label in ["Aro_J-1_00h","Aro_J-1_12h","Aro_J0_00h","Aro_J0_12h"]],
        value=["Aro_J0_00h","Aro_J-1_12h"],
        multi=True,
        clearable = False
    )

multi_select_line_chart_MNH = dcc.Dropdown(
        id="multi_select_line_chart_MNH",
        options=[{"value":label, "label":label} for label in ["MésoNH_Arp","MésoNH_Aro","MésoNH_Obs"]],
        value=["MésoNH_Arp","MésoNH_Aro"],
        multi=True,
        clearable = False
    )

multi_select_line_chart_SURFEX = dcc.Dropdown(
        id="multi_select_line_chart_SURFEX",
        options=[{"value":label, "label":label} for label in ["SURFEX_Arp","SURFEX_Aro","SURFEX_Obs"]],
        value=["SURFEX_Arp"],
        multi=True,
        clearable = False
    )
     
id_user = html.Div([
        dcc.Input(id = 'id_user1',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user2',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user3',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user4',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user5',type = 'text',placeholder = 'id de la simulation à rajouter')]) # Attention : dcc.Input != Input (voir plus bas)
# Les dcc.Input sont des carrés où l'utilisateur peut rentrer des info : ici type = 'text' donc du texte, 




############### Callbacks ###############

# Les callbacks ont obligatoirement besoin d'une liste d'Output et d'une liste d'Input pour fonctionner.
# Ils contiennent la/les fonction(s) qui vont actualiser l'/les Output(s) à chaque fois qu'un/que des Input(s) est/sont modifié(s)




output_graphs = []

for param in params:
    output_graphs.append(Output('graph_' + param,'figure')) # Définition des Outputs c-à-d des graphs qui seront mis à jour


@app.callback(output_graphs, 
               [Input('multi_select_line_chart_obs', 'value'),
                Input('multi_select_line_chart_ARP', 'value'),
                Input('multi_select_line_chart_ARO', 'value'),
                Input('multi_select_line_chart_MNH', 'value'),
                Input('multi_select_line_chart_SURFEX', 'value'),
                Input('my-date-picker-range', 'start_date'),
                Input('my-date-picker-range', 'end_date'),
                Input('id_user1','value'),Input('id_user2','value'),Input('id_user3','value'),Input('id_user4','value'),Input('id_user5','value')
                ])
		# Chaque Input prend en argument l'id d'une dcc.Input et la valeur qu'elle récupère


def update_line(reseau1,reseau2,reseau3,reseau4,reseau5,start_day,end_day,id_user1,id_user2,id_user3,id_user4,id_user5):
# On donne ici le nom que l'on veut aux arguments, seul l'ordre (et le nombre) est important et correspond à l'ordre (et au nombre) d'Inputs du callback. 
    
    
    if start_day is not None:
        start_day = date.fromisoformat(start_day)
    if end_day is not None:
        end_day = date.fromisoformat(end_day)   
    # transformation des dates de type str que l'on récupère du "calendrier" en datetime.date
    
    # UPDATE DES DATES APRES LE CALLBACK
    data, chart, graph = selection_donnees(start_day,end_day)
    data_mnh=lecture_mesoNH.mesoNH(start_day,end_day,models,params)
    data_surfex=lecture_surfex.surfex(start_day,end_day,models,params)
    # Extraction des données correspondants à la période choisie

    # Puis, mise à jour des graphes :

    for param in params:
        chart[param] = go.Figure()
	# Création des objets plotly


## Pour les 5 rejeux possibles de MésoNH, correspondants aux différents id_user :
        
    types=['solid', 'dot','dash','longdash','dashdot']   # différentes valeurs pour l'attribut "dash" du paramètre "line" qui donnent le type de tracé (trait plein/pointillés/tirets/longs tirets/alternance tirets-points)
    for j,id_user in enumerate([id_user1,id_user2,id_user3,id_user4,id_user5]):
        data_user=lecture_mesoNH.mesoNH_user(start_day,end_day,id_user,params)
        nb_jour = (end_day-start_day).days
        for i in range(nb_jour+1):
            date_run=start_day+datetime.timedelta(days=i)
            today_str=date_run.strftime('%Y%m%d')
            for param in params:
                try :
                    if isinstance(data_user[today_str][param],(list,np.ndarray)):  # On vérifie qu'il y a des données
                        chart[param].add_trace(go.Scatter(x=data_user[today_str]['time'], y=data_user[today_str][param], line=dict(color='black',dash=types[j]),name='MésoNH modifié (id : '+str(id_user)+' )'))
                        #print(data_user)
                except KeyError :
                    pass
		# Ici le try/except permet de ne rien afficher lorsque les données ne sont pas disponibles


## Pour les Obs de Météopole Flux, affichées par défaut car une seule option dans le widget :

    for selection in reseau1:
        if selection == "Obs" :
            for param in params:
                if isinstance(data[param]['Tf']['values'],(list,np.ndarray)):
                    chart[param].add_trace(go.Scatter(x=data[param]['Tf']['time'], y=data[param]['Tf']['values'].data,marker={"color":"red"},mode="lines",name=selection))
		    # Ici plus besoin de try/except, c'est AIDA qui s'en charge

## Pour les différents réseaux d'Arpège :
    for selection in reseau2:
        if selection == "Arp_J-1_00h" :
            reseau = reseaux[0]
            line_param = dict(color='navy',dash='dot')
        if selection == "Arp_J-1_12h" :
            reseau = reseaux[1]
            line_param = dict(color='mediumslateblue',dash='dot')
        if selection == "Arp_J0_00h" :
            reseau = reseaux[2]
            line_param = dict(color='navy')
        if selection == "Arp_J0_12h" :
            reseau = reseaux[3]
            line_param = dict(color='mediumslateblue')
            
        for param in params:
            if isinstance(data[param]['Gt'][reseau]['values'],(list,np.ndarray)):
                chart[param].add_trace(go.Scatter(x=data[param]['Gt'][reseau]['time'], y=data[param]['Gt'][reseau]['values'].data,line=line_param,name=selection))


## Pour les différents réseaux d'Arome :    
    for selection in reseau3:
        if selection == "Aro_J-1_00h" :
            reseau = reseaux[0]
            line_param = dict(color='green',dash='dot')
        if selection == "Aro_J-1_12h" :
            reseau = reseaux[1]
            line_param = dict(color='olive',dash='dot')
        if selection == "Aro_J0_00h" :
            reseau = reseaux[2]
            line_param = dict(color='green')
        if selection == "Aro_J0_12h" :
            reseau = reseaux[3]
            line_param = dict(color='olive')
            
        for param in params:
            if isinstance(data[param]['Rt'][reseau]['values'],(list,np.ndarray)):
                chart[param].add_trace(go.Scatter(x=data[param]['Rt'][reseau]['time'], y=data[param]['Rt'][reseau]['values'].data,line=line_param,name=selection))
    

## Pour les courbes de MésoNH : 
# A la différence des 3 réseaux précédents où l'on récupère les données sur la période choisie à chaque nouvelle période grâce à AIDA, MésoNH et SURFEX sont stockés par dossier nommé à la date de run.
# Il faut donc parcourir tous les jours entre le start_day et le end_day et stocker les informations lues.
    courbe_affichee=[]    
    for selection in reseau4 :
        nb_jour = (end_day-start_day).days
        for i in range(nb_jour+1):
            day=start_day+timedelta(days=i)
            today_str=day.strftime('%Y%m%d')

            #Gestion du nombre de légende affichée : La légende est affichée si elle absente avant cad si courbe_affichee est vide (courbe affichee est remplie au 1er jour affiche)
            if selection not in courbe_affichee and dico_model[selection]['name'] in data_mnh[today_str] and isinstance(data_mnh[today_str][dico_model[selection]['name']]['tmp_2m'],(list,np.ndarray)):
                courbe_affichee.append(selection)
                afficher_legende=True
            else:
                afficher_legende=False
		# Ce montage un peu douteux de if/else permet de n'afficher qu'une seule fois la légende de la courbe MésoNH choisie. Sans ça, le programme affichait autant de fois la légende
		# qu'il y avait de jours entre le start_day et le end_day.
            for param in params:
                try :
                    if isinstance(data_mnh[today_str][dico_model[selection]['name']][param],(list,np.ndarray)):
                        chart[param].add_trace(go.Scatter(x=data_mnh[today_str]['time'], y=data_mnh[today_str][dico_model[selection]['name']][param], marker={"color":dico_model[selection]['color']}, mode="lines",name=selection,showlegend=afficher_legende))
                except KeyError :
                    pass
		# Le retour du try/except pour éviter que le script ne se bloque.

#    print("--------------------------------------   PRINT MNH  ----------------------------------------- ", data_mnh[today_str]['Rt']['tmp_2m'])

## Pour les courbes de Surfex : 
    courbe_affichee_surfex=[]    
    for selection in reseau5 :
        nb_jour = (end_day-start_day).days
        for i in range(nb_jour+1):
            day=start_day+timedelta(days=i)
            today_str=day.strftime('%Y%m%d')
                
            if selection not in courbe_affichee_surfex and dico_model[selection]['name'] in data_surfex[today_str] and isinstance(data_surfex[today_str][dico_model[selection]['name']]['tmp_2m'],(list,np.ndarray)):
                courbe_affichee_surfex.append(selection)
                afficher_legende_surfex=True
            else:
                afficher_legende_surfex=False
            for param in params:
                try :
                    if isinstance(data_surfex[today_str][dico_model[selection]['name']][param],(list,np.ndarray)):
                        chart[param].add_trace(go.Scatter(x=data_surfex[today_str]['time'], y=data_surfex[today_str][dico_model[selection]['name']][param],line=dict(color=dico_model[selection]['color'],dash='dashdot'),name=selection,showlegend=afficher_legende_surfex))
                except KeyError :
                    pass
        

## Mise à jour des graphiques après tous les changements        
    list_charts = []
    for param in params:
        chart[param].update_layout(height=500, width=1000,
                         xaxis_title="Date et heure",
                         yaxis_title=str(dico_params[param]['unit']),
                         title=dico_params[param]['title'])
        list_charts.append(chart[param])
    
    
    return list_charts #Le callback attend des Outputs qui sont contenus dans chart[param]
 

                                             
############### Layout ###############



all_graphs=[]

for param in params:
   
    all_graphs.append(html.Div(graph[param],className="six columns", style={'display': 'inline-block'}))

row = html.Div(children=all_graphs, className="six columns")



#print("SHAPE OF ROW2 = ", row2)

# Puisqu'on n'a pas la main sur la css (pour l'instant)(cf external_stylesheets au début du code), on joue sur les html.Div.
# Ici par exemple, chaque graph est d'abord mis dans une Div dont on réduit la taille ("className="five columns"),
# puis on met toutes ces Div dans une seule qui elle prend toute la page ("className="twelve columns")


menu = html.Div([
        dcc.Link('Notice__', href='/MeteopoleX/notice'),
        dcc.Link('__Biais Obs/Modèles__', href='/MeteopoleX/biais'),
        dcc.Link('__Biais Moyens__', href='/MeteopoleX/biaisM'),
        dcc.Link('__Sondages__', href='/MeteopoleX/rs'),
        dcc.Link('__Rejeu MésoNH__', href='/MeteopoleX/mesoNH'),
        dcc.Link('__Rejeu SURFEX', href='/MeteopoleX/surfex')
        ],className="twelve columns",style={"text-align": "right", "justifyContent":"center"})

# le menu diffère de chaque page, il contient une liste de lien (dcc.Link) dont les arguments sont le nom souhaité et son url


obs_modeles_layout = html.Div([
    html.H1('MeteopoleX'),
    menu,
    calendrier,
    dcc.Dropdown(),
    html.Div([multi_select_line_chart_obs,multi_select_line_chart_ARP,multi_select_line_chart_ARO,
    multi_select_line_chart_MNH,multi_select_line_chart_SURFEX],className="six columns",style={"text-align": "center", "justifyContent":"center"}),
    id_user,
#    row_left,
#    row_right,
    row,
],className="row",style={"text-align": "center", "justifyContent":"center"})

# Ces dernières lignes sont la mise en forme finale de la page
    
    
###################
#
#   Notice
#
###################
    
menu = html.Div([
        dcc.Link('Comparaisons Obs MétéoFlux/Modèles__', href='/MeteopoleX/'),
        dcc.Link('__Biais Obs/Modèles__', href='/MeteopoleX/biais'),
        dcc.Link('__Biais Moyens__', href='/MeteopoleX/biaisM'),
        dcc.Link('__Sondages__', href='/MeteopoleX/rs'),
        dcc.Link('__Rejeu MésoNH', href='/MeteopoleX/mesoNH'),
        dcc.Link('__Rejeu SURFEX', href='/MeteopoleX/surfex')
        ],className="twelve columns",style={"text-align": "right", "justifyContent":"center"})
    
import base64
test_png = 'fig1.png'
test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')
# Ces 3 lignes mettent en forme l'image 'fig1.png'
    
content = html.Div([
    html.H3('Abréviations pour les tracés'),
    html.Br(),


    html.Span('Les différentes courbes de la page "Comparaison Obs/Modèles" sont nommées de la manière suivante :'),
    html.Div([html.Span('"Nom-du-modèle_date-de-run"',style={"font-weight":"bold"})],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Br(),
    html.Span('Par exemple, on se place le 15 avril : la courbe affichée ce jour là nommée "Aro_J-1_12h" est le run d\'Arome qui a tourné le 14 avril, la veille (J-1), à 12h.'),
    html.Span([html.Span(' Quant aux 2 dernières cases de sélection, leur nomenclature est pensée sous la forme '),html.Span('"Modèle_Forçages"',style={"font-weight":"bold"}),
    html.Span('. Ainsi, "MésoNH_Arp" désigne le tracé de MésoNH forcé par Arpège (voir les rubriques "Visualisation des runs automatiques de MesoNH" et "Visualisation des runs automatiques de SURFEX" pour plus de précisions).')]),
    html.Br(),
    html.Br(),
    html.Br(),




    html.H3('Pourquoi y-a-t-il des tracés en pointillés et pas en trait plein à la date d\'aujourd\'hui ?'),
    html.Br(),
    html.Span('Chaque run considéré donne des valeurs à au moins 48h d\'échéance. Ainsi, à une date donnée, les tracés à J0 sont les 24 premières heures des runs du jour,'
            ' et ceux à J-1 vont de la 25ème à la 48ème heure des runs du jour d\'avant. C\'est pour ça que les traits pleins et en pointillés se superposent : les pontillés représentent le'
            ' paramètre tel qu\'il était prévu la veille à 00h et 12h, et les traits pleins tel qu\'il est prévu le jour J à 00h et 12h.'),
    html.Br(),
    html.Br(),
    html.Span(' Pour la date actuelle (aujourd\'hui), c\'est légèrement différent : Puisque le rapatriement des données vers AIDA (entité que l\'on utilise pour lire les données d\'Arome,'
            ' Arpège et des Obs) ne se fait qu\'à 6h du matin chaque jour, les données les plus récentes que nous avons sont celles produites par les runs d\'hier.'
            ' Ne sont donc disponible pour la date d\'aujourd\'hui que les valeurs prédites 1 jour avant par les modèles, soient les runs de J-1, tracés en pointillés.'),
    html.Div([html.Img(src='data:image/png;base64,{}'.format(test_base64),style={'height':'50%', 'width':'50%'})],className="twelve columns",style={"text-align": "center"}), 
    # La balise html.Img permet d'afficher l'image 'fig1.png'
    html.Br(),
    html.Br(),
    html.Br(),





    html.H3('Visualisation des runs automatiques de MesoNH'),
    html.Span('Chaque jour vers 10h, 3 runs de MesoNH sont lancés :'),
    html.Div([html.Span('MesoNH-Aro',style={"font-weight":"bold"}),html.Span(' est forcé par Arome 0h du jour.')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Div([html.Span('MesoNH-Arp',style={"font-weight":"bold"}),html.Span(' est forcé par Arpège 0h du jour.')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Div([html.Span('MesoNH-Obs',style={"font-weight":"bold"}),html.Span(' est forcé par Arome 0h de l’avant-veille en altitude + les observations du site MeteopoleX au sol, sur les 2 journées précédentes.')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Div([html.Span('Ces 3 runs proposent des prévisions à 36h. Ainsi, si nous sommes le 7 avril après 10h, en supposant que les simulations du jour soient terminées, les données les plus récentes dont nous disposons sont :')]),
    html.Div([html.Span('MesoNH-Aro pour la période du 7 avril à 00h au 8 avril à 12h')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Div([html.Span('MesoNH-Arp pour la période du 7 avril à 00h au 8 avril à 12h')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Div([html.Span('MesoNH-Obs pour la période du 5 avril à 00h au 6 avril à 12h.')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Span('En revanche, le jour le plus récent qui peut être affiché est J0 (et pas J+1), les 12 dernières heures sont donc inutilisées.'), 
    html.Span(' Cependant, la disponibilité des données n’est pas toujours garantie : les runs d’Arome et d’Arpege'
              ' utilisés pour le forçage de MesoNH ne sont souvent pas disponibles à temps. La simulation sera alors durant dans les jours qui suivent. Dans tous les cas, si des données issues de MesoNH sont visibles, elles sont nécessairement issues du run de minuit précédant la date affichée.'),
    html.Br(),
    html.Br(),
    html.Br(),




    html.H3('Visualisation des runs automatiques de SURFEX'),
    html.Span('Les 3 runs de SURFEX s’exécutent quotidiennement à 10h :'),
    html.Div([html.Span('SURFEX_Aro',style={"font-weight":"bold"}),html.Span(' est forcé par Arome 00h du jour.')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Div([html.Span('SURFEX_Arp',style={"font-weight":"bold"}),html.Span(' est forcé par Arpège 00h du jour.')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Div([html.Span('SURFEX_Obs',style={"font-weight":"bold"}),html.Span(' est forcé par les Observations de Météopole Flux.')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}), 
    html.Span('Pour les 2 premiers, l’initialisation des paramètres de surface se fait avec les données de SURFEX issues des fichiers en extension .fa des runs d\'Arome et d\'Arpège. Pour les runs de SURFEX forcés par les obeservations, on utilise pour l’instant les mêmes fichiers en .fa, en attendant un couplage fonctionnel avec les Obs de Météopole Flux.'),
    html.Br(),
    html.Span('Les runs se déroulent sur 60h de j-1 à j+1 : Les 24h premières heures sont celles de j-1 et elles ne servent qu’au calage, ainsi, seules les 36 dernières heures qui vont de j à j+1 à 12h sont pertinentes.'),
    html.Br(),
    html.Span('Par exemple, considerons que nous sommes le 10 Mars après 10h. Si les simulations du jour ont bien tournés, les sorties les plus récentes dont nous disposons sont :'),
    html.Div([html.Span('SURFEX_Aro pour la période du 10 Mars à 00h au 11 Mars à 12h,')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Div([html.Span('SURFEX_Arp pour la période du 10 Mars à 00h au 11 Mars à 12h.')],className="twelve columns",style={"text-align": "center", "justifyContent":"center"}),
    html.Span('Par contre, comme pour les précédents tracés, le jour le plus récent qui peut être affiché reste toujours J0 (soit ici le 10 Mars).'),
    html.Br(),
    html.Br(),
    html.Br(),   






    html.H3('Rejeu de MésoNH'),
    html.Span('Il est possible pour un utilisateur de lancer un run de MesoNH avec les paramètres qu’il souhaite. Ce run sera nécessairement forcé par Arome '
            '(choix Arome/Arpege sans doute dans une prochaine version du site). Sur la page web, un certain nombre de paramètres sont disponibles. '),
    html.Br(),
    html.Br(),
    html.Span('L’utilisateur commence par choisir une date de run. Le run sera initialisé à minuit de la date choisie.'),
    html.Br(),
    html.Span('Ex: l’utilisateur a choisi la date du 15 août 2019. La run sera donc initialisé avec les données du run du 15 août 2019 0Z d’Arome. Ce run de MesoNH a une '
            'échéance maximale de 36h, des données seront donc disponibles entre le 15 août 0h et le 16 août 12h.'),
    html.Span(' L’utilisateur dispose de listes déroulantes pour choisir les schémas physiques qui l’intéressent.'),
    html.Br(),
    html.Span(' Sans sélection de la part de l’utilisateur, un paramètre prendra sa valeur par défaut (cf '),
    html.A("la documentation utilisateur de MésoNH",href='http://mesonh.aero.obs-mip.fr/mesonh54/BooksAndGuides?action=AttachFile&do=get&target=users_guide_m544.pdf#subsection.9.2.44)'),
    html.Span(').'),
    html.Br(),
    html.Span('Pour l’instant, seuls les paramètres CTURB, CRAD et CCLOUD sont modifiables, sans doute bien plus à l’avenir. Après avoir choisi une date de rejeu et les '
            'paramètres qu’il souhaite, l’utilisateur est invité à cliquer sur le bouton en bas de page pour lancer la simulation.'),
    html.Br(),
    html.Span('Un identifiant est délivré pour chaque simulation. C’est cet identifiant qui permettra ensuite d’afficher la simulation parmi les autres sur la plateforme '
            'de visualisation du site web. L’utilisateur peut choisir de patienter pour savoir exactement quand la simulation est terminé, ou de fermer la page web : la simulation continuera sur le serveur et, quelques minutes plus tard, sera disponible à la visualisation.'),
    html.Br(),
    html.Span('Dans tous les cas, il est important de bien conserver l’identifiant pour pouvoir afficher la simulation personnalisée.'),
    ],className="twelve columns",style={"text-align": "left", "justifyContent":"center"})





 



   
notice_layout = html.Div([
    html.Br(),
    html.H1('Précisions relatives aux abrévations et aux modèles utilisés'),
    menu,
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    content,
],className="twelve columns",style={"text-align": "center", "justifyContent":"center"})

# Mise en page finale








#print("DATA MNH ", data_mnh)


##############################
#
#   Biais Obs/Modèles
#
##############################



############### Calcul des biais #########

def calcul_biais(start_day,end_day):

    doy1 = datetime.datetime(int(start_day.year),int(start_day.month),int(start_day.day)).strftime('%j')
    doy2 = datetime.datetime(int(end_day.year),int(end_day.month),int(end_day.day)).strftime('%j')

    chartB = {}
    graphB = {}

    biais = {}
    #biais_mnh = {}


    #création d'un dataframe vide avec les valeurs des dates de la période (start_day,end_day), toutes les heures car modele OPER = sorties horaires.
    dt=mdates.num2date(mdates.drange(datetime.datetime(int(start_day.year),int(start_day.month),int(start_day.day)),datetime.datetime(int(end_day.year),int(end_day.month),int(end_day.day)),datetime.timedelta(minutes=30)))

    dataallyear = [i.replace(tzinfo=None) for i in dt]
    dataframe_sanstrou = pd.DataFrame(index=dataallyear)   


    #Données des simulations MésoNH OPER
    data_mnh = lecture_mesoNH.mesoNH(start_day,end_day,models,params)




    for param in params:

        if param not in biais:
            biais[param] = {}

        for model in models:

            id_aida_obs = dico_params[param]["index_obs"] 
            (values_obs, time_obs, header_obs)=read_aida.donnees(doy1,doy2,str(start_day.year),id_aida_obs,"Tf")
  
            if model not in biais[param]:
                biais[param][model] = {}            
 
            for reseau in reseaux:

                if reseau not in biais[param][model]:

                   biais[param][model][reseau] = {}

                id_aida_mod = dico_params[param]["index_model"] + "_" + reseau 
                (values_mod, time_mod, header_mod)=read_aida.donnees(doy1,doy2,str(start_day.year),id_aida_mod,model)

                      
                #Correction des données ARPEGE parfois datées à H-1:59 au lieu de H:00
                if time_mod is not None:                       
                       
                      i=0
                     
                      for ts in time_mod:

                          if ts.minute == 59. :
 
                             time_mod[i]  = time_mod[i] + datetime.timedelta(minutes=1)

                             i=i+1

                          else:

                             i=i+1   

                #Les flux pour AROME et ARPEGE OPER sont agrégés entre H et H+1 : On les replace à H:30 pour davantage de réalisme
                if param == 'flx_mvt' or param == 'flx_chaleur_sens' or param == 'flx_chaleur_lat' or param == 'SWD' or param == 'LWU' :

                   if time_mod is not None:                       
                       
                      i=0
                     
                      for ts in time_mod:
                      
                          time_mod[i]  = time_mod[i] - datetime.timedelta(minutes=30)

                          i=i+1


                if values_mod is None or values_obs is None :

                        biais[param][model][reseau]['values'] = np.nan

                         
                else:   
             
                          
                        #Création de dataframes des valeurs obs et modèles
                        df_obs = pd.DataFrame(list(values_obs), index=(time_obs))
                        df_mod = pd.DataFrame(list(values_mod), index=(time_mod))

                        #concordance des dates sur le dataframe défini au début 
                        df_obs= dataframe_sanstrou.join(df_obs)
                        df_mod= dataframe_sanstrou.join(df_mod)

                        #Calcul du biais
                        df_biais = df_mod - df_obs

                        #df_biais = dataframe_sanstrou.join(df_biais)
                        #df_biais = df_biais.fillna(0)
                        df_biais = df_biais.dropna()
                        df_biais.index = pd.to_datetime(df_biais.index)

                        date_list = df_biais.index.strftime("%Y-%m-%d %H:%M:%S").tolist()

                        #Passage du dataframes "biais" en listes pour intégrations dans les dictionnaires biais
                        biais[param][model][reseau]['values']  = list(df_biais[0])
                        biais[param][model][reseau]['time']    = list(df_biais.index)


                        
            nb_jour = (end_day-start_day).days

            for i in range(nb_jour+1):


               day=start_day+timedelta(days=i)
               today_str=day.strftime('%Y%m%d')

               day_after=start_day+timedelta(days=i+1)
               after_str=day_after.strftime('%Y%m%d')  
                 
               day_1 = datetime.datetime(int(day.year),int(day.month),int(day.day)).strftime('%j')  
               day_2 = datetime.datetime(int(day_after.year),int(day_after.month),int(day_after.day)).strftime('%j')


               id_aida_obs = dico_params[param]["index_obs"] 
               (values_obs, time_obs, header_obs)=read_aida.donnees(day_1,day_2,str(start_day.year),id_aida_obs,"Tf") 



               dt_mnh=mdates.num2date(mdates.drange(datetime.datetime(int(day.year),int(day.month),int(day.day)),datetime.datetime(int(day_after.year),int(day_after.month),int(day_after.day)),datetime.timedelta(minutes=30)))
  
               dataallyear_mnh = [i.replace(tzinfo=None) for i in dt_mnh]
               dataframe_sanstrou_mnh = pd.DataFrame(index=dataallyear_mnh)   


               if today_str not in biais[param][model]:

                  biais[param][model][today_str] = {}

               if model != 'Tf' :

                  if values_obs is not None : 

                        try:
 
                           values_mnh = data_mnh[today_str][model][param]
                           time_mnh   = data_mnh[today_str]['time']

                           if len(values_mnh) != 0 :   
                                                 
                             #Création de dataframes des valeurs obs et modèles
                             df_obs = pd.DataFrame(list(values_obs), index=(time_obs))
                             df_mnh = pd.DataFrame(list(values_mnh[0:96]), index=(time_mnh))

                             #concordance des dates sur le dataframe défini au début 
                             df_obs= dataframe_sanstrou_mnh.join(df_obs)
                             df_mnh= dataframe_sanstrou_mnh.join(df_mnh)

                             #Calcul du biais
                             df_biais_mnh = df_mnh - df_obs

                             #df_biais = dataframe_sanstrou.join(df_biais)
                             df_biais_mnh = df_biais_mnh.fillna(0)
                             df_biais_mnh.index = pd.to_datetime(df_biais_mnh.index) 
                           
                             biais[param][model][today_str]['values']  = list(df_biais_mnh[0])
                             biais[param][model][today_str]['time']    = list(df_biais_mnh.index)

                        except KeyError :
                               pass

        chartB[param] = go.Figure()
        # Tracé des figures
               
        graphB[param] = dcc.Graph(
                id='graphB_' + param,
                figure=chartB[param],
            ) 
         #Tranformation en HTML
         
         # Ces 2 dernières étapes sont essentielles : d'abord on effectue le tracé, puis on le transforme en objet html pour pouvoir l'afficher

    return biais, chartB, graphB

biais, chartB, graphB = calcul_biais(start_day,end_day)






############### Widgets ###############

calendrier = html.Div([
    dcc.DatePickerRange(
        id = 'my-date-picker-range',
        first_day_of_week = 1,
        min_date_allowed = date(2015, 1, 1),
        max_date_allowed = date(tomorow.year, tomorow.month, tomorow.day), # Il faut mettre demain pour que la date max soit aujourd'hui
        display_format = "DD/MM/YYYY",
        initial_visible_month = date(today.year, today.month, today.day),
        start_date = yesterday,
        end_date = today,
        minimum_nights = 0 # Durée minimum sélectionnable : si =0, durée min = 1 jour c-à-d start_date=end_date
    ),html.Div(id = 'output-container-date-picker-range')])


#multi_select_line_chartB_obs = dcc.Dropdown(
#        id="multi_select_line_chartB_obs",
#        options=[{"value":label, "label":label} for label in ["Obs"]],
#        value=["Obs"], # Valeur qui s'affiche par défaut (si pas dans la liste des options alors rien n'est affiché)
#        multi=True, # Possibilité d'en choisir plusieur
#        clearable = False
#    )
# Le dcc.Dropdown est un objet dash qui permet l'affichage des options sélectionnables quand on clique dessus, puis la sélection d'une ou plusieurs options.


multi_select_line_chartB_ARP = dcc.Dropdown(
        id = "multi_select_line_chartB_ARP",
        options = [{"value":label, "label":label} for label in ["Arp_J-1_00h","Arp_J-1_12h","Arp_J0_00h","Arp_J0_12h",]],
        value = ["Arp_J0_00h","Arp_J-1_12h"],
        multi = True,
        clearable = False
    )

multi_select_line_chartB_ARO = dcc.Dropdown(
        id = "multi_select_line_chartB_ARO",
        options = [{"value":label, "label":label} for label in ["Aro_J-1_00h","Aro_J-1_12h","Aro_J0_00h","Aro_J0_12h"]],
        value = ["Aro_J0_00h","Aro_J-1_12h"],
        multi = True,
        clearable = False
    )

multi_select_line_chartB_MNH = dcc.Dropdown(
        id = "multi_select_line_chartB_MNH",
        options = [{"value":label, "label":label} for label in ["MésoNH_Arp","MésoNH_Aro","MésoNH_Obs"]],
        value = ["MésoNH_Arp","MésoNH_Aro"],
        multi = True,
        clearable = False
    )

multi_select_line_chartB_SURFEX = dcc.Dropdown(
        id = "multi_select_line_chartB_SURFEX",
        options = [{"value":label, "label":label} for label in ["SURFEX_Arp","SURFEX_Aro","SURFEX_Obs"]],
        value = ["SURFEX_Arp"],
        multi = True,
        clearable = False
    )
     
id_user = html.Div([
        dcc.Input(id = 'id_user1',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user2',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user3',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user4',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user5',type = 'text',placeholder = 'id de la simulation à rajouter')]) # Attention : dcc.Input != Input (voir plus bas)
# Les dcc.Input sont des carrés où l'utilisateur peut rentrer des info : ici type = 'text' donc du texte, 




############### Callbacks ###############

# Les callbacks ont obligatoirement besoin d'une liste d'Output et d'une liste d'Input pour fonctionner.
# Ils contiennent la/les fonction(s) qui vont actualiser l'/les Output(s) à chaque fois qu'un/que des Input(s) est/sont modifié(s)


output_graphsB = []

for param in params:
    output_graphsB.append(Output('graphB_' + param, 'figure')) # Définition des Outputs c-à-d des graphs qui seront mis à jour


##### BIAIS MNH
#for param in params:
#    output_graphsB.append(Output('graphB_mnh_' + param, 'figure'))


@app.callback(output_graphsB, 
#               [Input('multi_select_line_chartB_obs', 'value'),
                [Input('multi_select_line_chartB_ARP', 'value'),
                Input('multi_select_line_chartB_ARO', 'value'),
                Input('multi_select_line_chartB_MNH', 'value'),
                Input('multi_select_line_chartB_SURFEX', 'value'),
                Input('my-date-picker-range', 'start_date'),
                Input('my-date-picker-range', 'end_date'),
                Input('id_user1','value'),Input('id_user2','value'),Input('id_user3','value'),Input('id_user4','value'),Input('id_user5','value')
                ])
		# Chaque Input prend en argument l'id d'une dcc.Input et la valeur qu'elle récupère



def update_lineB(reseau2,reseau3,reseau4,reseau5,start_day,end_day,id_user1,id_user2,id_user3,id_user4,id_user5):
# On donne ici le nom que l'on veut aux arguments, seul l'ordre (et le nombre) est important et correspond à l'ordre (et au nombre) d'Inputs du callback. 
        
    if start_day is not None:
        start_day = date.fromisoformat(start_day)
    if end_day is not None:
        end_day = date.fromisoformat(end_day)   
    # transformation des dates de type str que l'on récupère du "calendrier" en datetime.date
    
    # UPDATE DES DATES APRES LE CALLBACK


    data_mnh    = lecture_mesoNH.mesoNH(start_day,end_day,models,params)
    data_surfex = lecture_surfex.surfex(start_day,end_day,models,params)




    # CALCUL DES BIAIS correspondants à la période choisie

    biais, chartB, graphB = calcul_biais(start_day,end_day)

    # Puis, mise à jour des graphes :

    for param in params:
        chartB[param] = go.Figure()


## Pour les 5 rejeux possibles de MésoNH, correspondants aux différents id_user :
        
    types=['solid', 'dot','dash','longdash','dashdot']   # différentes valeurs pour l'attribut "dash" du paramètre "line" qui donnent le type de tracé (trait plein/pointillés/tirets/longs tirets/alternance tirets-points)
    for j,id_user in enumerate([id_user1,id_user2,id_user3,id_user4,id_user5]):
        data_user=lecture_mesoNH.mesoNH_user(start_day,end_day,id_user,params)
        nb_jour = (end_day-start_day).days
        for i in range(nb_jour+1):
            date_run=start_day+datetime.timedelta(days=i)
            today_str=date_run.strftime('%Y%m%d')
            for param in params:
                try :
                    if isinstance(data_user[today_str][param],(list,np.ndarray)):  # On vérifie qu'il y a des données

                        chartB[param].add_trace(go.Scatter(x=data_user[today_str]['time'], y=data_user[today_str][param], line=dict(color='black',dash=types[j]),name='MésoNH modifié (id : '+str(id_user)+' )'))

                except KeyError :
                    pass
		# Ici le try/except permet de ne rien afficher lorsque les données ne sont pas disponibles


## BIAIS -> le calcul sur les obs permet d'avoir le zéro en affichage (obs - obs = 0)

#    for selection in reseau1:
#        if selection == "Obs" :
#            for param in params:
#                if isinstance(biais[param]['Tf']['values'],(list,np.ndarray)):
#                    chartB[param].add_trace(go.Scatter(x=biais[param]['Tf']['time'], y=biais[param]['Tf']['values'],marker={"color":"red"},mode="lines",name=selection))

		    # Ici plus besoin de try/except, c'est AIDA qui s'en charge


## Pour les différents réseaux d'Arpège :
    for selection in reseau2:
        if selection == "Arp_J-1_00h" :
            reseau = reseaux[0]
            line_param = dict(color='navy',dash='dot')
        if selection == "Arp_J-1_12h" :
            reseau = reseaux[1]
            line_param = dict(color='mediumslateblue',dash='dot')
        if selection == "Arp_J0_00h" :
            reseau = reseaux[2]
            line_param = dict(color='navy')
        if selection == "Arp_J0_12h" :
            reseau = reseaux[3]
            line_param = dict(color='mediumslateblue')
            
        for param in params:
            if isinstance(biais[param]['Gt'][reseau]['values'],(list,np.ndarray)):
                chartB[param].add_trace(go.Scatter(x=biais[param]['Gt'][reseau]['time'], y=biais[param]['Gt'][reseau]['values'], line=line_param,name=selection))


## Pour les différents réseaux d'Arome :    
    for selection in reseau3:
        if selection == "Aro_J-1_00h" :
            reseau = reseaux[0]
            line_param = dict(color='green',dash='dot')
        if selection == "Aro_J-1_12h" :
            reseau = reseaux[1]
            line_param = dict(color='olive',dash='dot')
        if selection == "Aro_J0_00h" :
            reseau = reseaux[2]
            line_param = dict(color='green')
        if selection == "Aro_J0_12h" :
            reseau = reseaux[3]
            line_param = dict(color='olive')
            
        for param in params:
            if isinstance(biais[param]['Rt'][reseau]['values'],(list,np.ndarray)):
                chartB[param].add_trace(go.Scatter(x=biais[param]['Rt'][reseau]['time'], y=biais[param]['Rt'][reseau]['values'], line=line_param,name=selection))    


#!!!!!! A COMPLETER POUR MESO-NH ET SURFEX !!!!!!!!!!!!

## Pour les courbes de MésoNH : 
# A la différence des 3 réseaux précédents où l'on récupère les données sur la période choisie à chaque nouvelle période grâce à AIDA, MésoNH et SURFEX sont stockés par dossier nommé à la date de run.
# Il faut donc parcourir tous les jours entre le start_day et le end_day et stocker les informations lues.

    courbe_affichee=[]    
    for selection in reseau4 :

        nb_jour = (end_day-start_day).days

        for i in range(nb_jour+1):

            day=start_day+timedelta(days=i)
            today_str=day.strftime('%Y%m%d')

            #Gestion du nombre de légende affichée : La légende est affichée si elle absente avant cad si courbe_affichee est vide (courbe affichee est remplie au 1er jour affiche)
            #if selection not in courbe_affichee and dico_model[selection]['name'] in biais['tmp_2m'] and isinstance(biais['tmp_2m'][dico_model[selection]['name']][today_str],(list,np.ndarray)):
            if selection not in courbe_affichee and dico_model[selection]['name'] in biais['tmp_2m']:    


                courbe_affichee.append(selection)
                afficher_legende=True

            else:

                afficher_legende=False

		# Ce montage un peu douteux de if/else permet de n'afficher qu'une seule fois la légende de la courbe MésoNH choisie. Sans ça, le programme affichait autant de fois la légende
		# qu'il y avait de jours entre le start_day et le end_day.

            for param in params:

                try :

                   if isinstance(biais[param][dico_model[selection]['name']][str(today_str)]['values'],(list,np.ndarray)):

                      chartB[param].add_trace(go.Scatter(x=biais[param][dico_model[selection]['name']][str(today_str)]['time'], y=biais[param][dico_model[selection]['name']][str(today_str)]['values'], marker={"color":dico_model[selection]['color']}, mode="lines",name=selection,showlegend=afficher_legende))

                except KeyError :
                    pass
		# Le retour du try/except pour éviter que le script ne se bloque.



## Pour les courbes de Surfex : 
    courbe_affichee_surfex=[]    
    for selection in reseau5 :
        nb_jour = (end_day-start_day).days
        for i in range(nb_jour+1):
            day=start_day+timedelta(days=i)
            today_str=day.strftime('%Y%m%d')
                
            if selection not in courbe_affichee_surfex and dico_model[selection]['name'] in data_surfex[today_str] and isinstance(data_surfex[today_str][dico_model[selection]['name']]['tmp_2m'],(list,np.ndarray)):
                courbe_affichee_surfex.append(selection)
                afficher_legende_surfex=True
            else:
                afficher_legende_surfex=False
            for param in params:
                try :
                    if isinstance(data_surfex[today_str][dico_model[selection]['name']][param],(list,np.ndarray)):
                        chartB[param].add_trace(go.Scatter(x=data_surfex[today_str]['time'], y=data_surfex[today_str][dico_model[selection]['name']][param],line=dict(color=dico_model[selection]['color'],dash='dashdot'),name=selection,showlegend=afficher_legende_surfex))
                except KeyError :
                    pass
        


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        



## Mise à jour des graphiques après tous les changements  
      
    list_chartsB = []

    for param in params:

        chartB[param].update_layout(height=500, width=1000,
                         xaxis_title="Date et heure",
                         yaxis_title=str(dico_params[param]['unit']),
                         title=dico_params[param]['title'])

        list_chartsB.append(chartB[param])
    
    return list_chartsB #Le callback attend des Outputs qui sont contenus dans chartB[param]
 





############### Layout ###############


#!!!!!!!!!!!!!!! Tracé des graphes sur la page correspondantes: à modifier avec les graphes affichant les biais (calculés plus haut)


all_graphsB = []

for param in params:
    all_graphsB.append(html.Div(graphB[param],className="six columns", style={'display': 'inline-block'}))

row2 = html.Div(children=all_graphsB, className="twelve columns")

# Puisqu'on n'a pas la main sur la css (pour l'instant)(cf external_stylesheets au début du code), on joue sur les html.Div.
# Ici par exemple, chaque graph est d'abord mis dans une Div dont on réduit la taille ("className="five columns"),
# puis on met toutes ces Div dans une seule qui elle prend toute la page ("className="twelve columns")


menu = html.Div([
        dcc.Link('Notice__', href='/MeteopoleX/notice'),
        dcc.Link('__Comparaisons Obs MétéoFlux/Modèles__', href='/MeteopoleX/'),
        dcc.Link('__Biais Moyens__', href='/MeteopoleX/biaisM'),
        dcc.Link('__Sondages__', href='/MeteopoleX/rs'),
        dcc.Link('__Rejeu MésoNH__', href='/MeteopoleX/mesoNH'),
        dcc.Link('__Rejeu SURFEX', href='/MeteopoleX/surfex')
        ],className="twelve columns",style={"text-align": "right", "justifyContent":"center"})

# le menu diffère de chaque page, il contient une liste de lien (dcc.Link) dont les arguments sont le nom souhaité et son url


biais_layout = html.Div([
    html.H1('Biais entre Observations Météopôle-Flux et Modèles'),
    menu,
    calendrier,
    html.Div([multi_select_line_chartB_ARP,multi_select_line_chartB_ARO,
    multi_select_line_chartB_MNH,multi_select_line_chartB_SURFEX],className="eight columns",style={"text-align": "center", "justifyContent":"center"}),
    id_user,
    row2,
],className="twelve columns",style={"text-align": "center", "justifyContent":"center"})

















##############################
#
#   Biais Obs/Modèles - CYCLE DIURNE MOYEN
#
##############################



############### Calcul des biais moyens #########


def biais_moyen(start_day,end_day):


    print("START_DAY", str(start_day))
    print("END_DAY", str(end_day))
        
    #Initialisation du DataFrame final vide
    DF=[]

    #Axe des temps: on prend la résolution des obs
    DF= pd.DataFrame(DF, index=list(data['tmp_2m']['Tf']['time']))

    for param in params:

        for model in models:

            if model != 'Tf' :

               #Ajout des données ARO/ARP OPER
               for reseau in reseaux:

                   #if len(biais[param][model][reseau]) > 1 :

                   dico_loc= {}
                   df_loc  = []
                   
                   #Nom des colonnes du DF
                   colname = str(param+'_'+model+'_'+reseau)
                   #print(colname)
                   
                   try:
                      dico_loc = {colname:list(biais[param][model][reseau]['values'])}
                      df_loc = pd.DataFrame(data=dico_loc, index=list(biais[param][model][reseau]['time']))

                      DF = pd.concat([DF, df_loc], axis=1)
                      
                      #print("OK POUR BIAIS MOY OPER")
                   except:
                      pass

             
            #Ajout des données MNH-OPER            
            nb_jour = (end_day-start_day).days

            df_mnh=[]
            df_mnh = pd.DataFrame(df_mnh)

            for i in range(nb_jour):

                day=start_day+timedelta(days=i)
                today_str=day.strftime('%Y%m%d')
               #if len(biais[param][model][str(today_str)]) > 1 :
                  
                  
                    
               
                df_loc = []
                colname = str(param+'_MesoNH_'+model)
                     #dummyarray = np.full(len(biais[param][model][str(today_str)]['time']), np.nan)
                   
                     #df_nan = pd.DataFrame(data={colname:list(dummyarray)}, index=list(biais[param][model][str(today_str)]['time']))
                   
                print(biais.keys())
                     #df_loc = pd.DataFrame(df_loc, index=list(biais[param][model][str(today_str)]['time']))
                      
                try:
                   
                  print("ESSAI DE CREER DF BIAIS SUR LE JOUR : ", str(today_str))
                  df_loc = pd.DataFrame(df_loc, index=list(biais[param][model][str(today_str)]['time']))
                  print("OK POUR CREATION DF BIAIS SUR LE JOUR : ", str(today_str))
                      
                  data_loc={colname:list(biais[param][model][str(today_str)]['values'])} 
                  print("NOM DE LA COLONNE : ", colname)
                      
                      
                  #df_loc = pd.DataFrame(data=data_loc, index=list(biais[param][model][str(today_str)]['time'])) 
                  #print("CREATION DF LOCAL POUR LE JOUR : ", str(today_str))
             
                  df_mnh = pd.concat([df_mnh, df_loc], axis=0)
                      
                  print("OK POUR BIAIS MOY MNH")
               
                except:
                      
                  #df_mnh = pd.concat([df_mnh, df_nan], axis=0)
                         
                  pass
          
            DF = pd.concat([DF, df_mnh], axis=1)




   #Conversion colonnes type 'object' en type 'numeric'
   #Sinon le 'groupby' enlève les colonnes 'object'

    cols =DF.columns[DF.dtypes.eq('object')]
    DF[cols] = DF[cols].astype('float')
    
    print(DF.index)

    #Dataframe regroupé par heures
    DF_CyDi = DF.groupby(DF.index.hour).mean()

    

    #Création du dictionnaire associé aux biais moyens + graphes html
    chartM = {}
    graphM = {}

    biais_moy = {}
    
    #Intégration des données du DataFrame DF_CyDi dans le dictionnaire biais_moy
    for param in params:
        
        if param not in biais_moy:
            biais_moy[param] = {}

        for model in models:
        
            if model not in biais_moy[param]:
               biais_moy[param][model] = {}
    
            if model != 'Tf' :

               #Ajout des données ARO/ARP OPER
               for reseau in reseaux:
               
                   if reseau not in biais_moy[param][model]:
                      biais_moy[param][model][reseau] = {}
    
                   colname = str(param+'_'+model+'_'+reseau)
                   
                   try:
                      biais_moy[param][model][reseau]['values']  = list(DF_CyDi[colname])
                      biais_moy[param][model][reseau]['time']    = list(DF_CyDi.index)
                   except:
                      biais_moy[param][model][reseau]['values']  = 0.
                      biais_moy[param][model][reseau]['time']    = list(DF_CyDi.index)
                      pass
                   
            if 'MNH' not in biais_moy[param][model]:
           
               biais_moy[param][model]['MNH'] = {}
            
            colname = str(param+'_MesoNH_'+model) 
            
            try:  
               biais_moy[param][model]['MNH']['values']  = list(DF_CyDi[colname])
               biais_moy[param][model]['MNH']['time']    = list(DF_CyDi.index)
            except:
               biais_moy[param][model]['MNH']['values']  = 0.
               biais_moy[param][model]['MNH']['time']    = list(DF_CyDi.index)
               pass   
               
    
    

        chartM[param] = go.Figure()
        # Tracé des figures
               
        graphM[param] = dcc.Graph(
                id='graphM_' + param,
                figure=chartM[param],
            ) 
         #Tranformation en HTML
         
         # Ces 2 dernières étapes sont essentielles : d'abord on effectue le tracé, puis on le transforme en objet html pour pouvoir l'afficher

    return biais_moy, chartM, graphM




biais_moy, chartM, graphM = biais_moyen(start_day,end_day)






############### Widgets ###############

calendrier = html.Div([
    dcc.DatePickerRange(
        id = 'my-date-picker-range',
        first_day_of_week = 1,
        min_date_allowed = date(2015, 1, 1),
        max_date_allowed = date(tomorow.year, tomorow.month, tomorow.day), # Il faut mettre demain pour que la date max soit aujourd'hui
        display_format = "DD/MM/YYYY",
        initial_visible_month = date(today.year, today.month, today.day),
        start_date = yesterday,
        end_date = today,
        minimum_nights = 0 # Durée minimum sélectionnable : si =0, durée min = 1 jour c-à-d start_date=end_date
    ),html.Div(id = 'output-container-date-picker-range')])


#multi_select_line_chartB_obs = dcc.Dropdown(
#        id="multi_select_line_chartB_obs",
#        options=[{"value":label, "label":label} for label in ["Obs"]],
#        value=["Obs"], # Valeur qui s'affiche par défaut (si pas dans la liste des options alors rien n'est affiché)
#        multi=True, # Possibilité d'en choisir plusieur
#        clearable = False
#    )
# Le dcc.Dropdown est un objet dash qui permet l'affichage des options sélectionnables quand on clique dessus, puis la sélection d'une ou plusieurs options.


multi_select_line_chartM_ARP = dcc.Dropdown(
        id = "multi_select_line_chartM_ARP",
        options = [{"value":label, "label":label} for label in ["Arp_J-1_00h","Arp_J-1_12h","Arp_J0_00h","Arp_J0_12h",]],
        value = ["Arp_J0_00h","Arp_J-1_12h"],
        multi = True,
        clearable = False
    )

multi_select_line_chartM_ARO = dcc.Dropdown(
        id = "multi_select_line_chartM_ARO",
        options = [{"value":label, "label":label} for label in ["Aro_J-1_00h","Aro_J-1_12h","Aro_J0_00h","Aro_J0_12h"]],
        value = ["Aro_J0_00h","Aro_J-1_12h"],
        multi = True,
        clearable = False
    )

multi_select_line_chartM_MNH = dcc.Dropdown(
        id = "multi_select_line_chartM_MNH",
        options = [{"value":label, "label":label} for label in ["MésoNH_Arp","MésoNH_Aro","MésoNH_Obs"]],
        value = ["MésoNH_Arp","MésoNH_Aro"],
        multi = True,
        clearable = False
    )

multi_select_line_chartM_SURFEX = dcc.Dropdown(
        id = "multi_select_line_chartM_SURFEX",
        options = [{"value":label, "label":label} for label in ["SURFEX_Arp","SURFEX_Aro","SURFEX_Obs"]],
        value = ["SURFEX_Arp"],
        multi = True,
        clearable = False
    )
     
id_user = html.Div([
        dcc.Input(id = 'id_user1',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user2',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user3',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user4',type = 'text',placeholder = 'id de la simulation à rajouter'),
        dcc.Input(id = 'id_user5',type = 'text',placeholder = 'id de la simulation à rajouter')]) # Attention : dcc.Input != Input (voir plus bas)
# Les dcc.Input sont des carrés où l'utilisateur peut rentrer des info : ici type = 'text' donc du texte, 




############### Callbacks ###############

# Les callbacks ont obligatoirement besoin d'une liste d'Output et d'une liste d'Input pour fonctionner.
# Ils contiennent la/les fonction(s) qui vont actualiser l'/les Output(s) à chaque fois qu'un/que des Input(s) est/sont modifié(s)


output_graphsM = []

for param in params:
    output_graphsM.append(Output('graphM_' + param, 'figure')) # Définition des Outputs c-à-d des graphs qui seront mis à jour


##### BIAIS MNH
#for param in params:
#    output_graphsB.append(Output('graphB_mnh_' + param, 'figure'))


@app.callback(output_graphsM, 
#               [Input('multi_select_line_chartB_obs', 'value'),
                [Input('multi_select_line_chartM_ARP', 'value'),
                Input('multi_select_line_chartM_ARO', 'value'),
                Input('multi_select_line_chartM_MNH', 'value'),
                Input('multi_select_line_chartM_SURFEX', 'value'),
                Input('my-date-picker-range', 'start_date'),
                Input('my-date-picker-range', 'end_date'),
                Input('id_user1','value'),Input('id_user2','value'),Input('id_user3','value'),Input('id_user4','value'),Input('id_user5','value')
                ])
		# Chaque Input prend en argument l'id d'une dcc.Input et la valeur qu'elle récupère



def update_lineM(reseau2,reseau3,reseau4,reseau5,start_day,end_day,id_user1,id_user2,id_user3,id_user4,id_user5):
# On donne ici le nom que l'on veut aux arguments, seul l'ordre (et le nombre) est important et correspond à l'ordre (et au nombre) d'Inputs du callback. 
        
    if start_day is not None:
        start_day = date.fromisoformat(start_day)
    if end_day is not None:
        end_day = date.fromisoformat(end_day)   
    # transformation des dates de type str que l'on récupère du "calendrier" en datetime.date
    
    # UPDATE DES DATES APRES LE CALLBACK


    data_mnh    = lecture_mesoNH.mesoNH(start_day,end_day,models,params)
    data_surfex = lecture_surfex.surfex(start_day,end_day,models,params)




    # CALCUL DES BIAIS moyens sur la période choisie - Cycle Diurne:

    biais_moy, chartM, graphM = biais_moyen(start_day,end_day)

    # Puis, mise à jour des graphes :

    for param in params:
        chartM[param] = go.Figure()


## Pour les 5 rejeux possibles de MésoNH, correspondants aux différents id_user :
        
    types=['solid', 'dot','dash','longdash','dashdot']   # différentes valeurs pour l'attribut "dash" du paramètre "line" qui donnent le type de tracé (trait plein/pointillés/tirets/longs tirets/alternance tirets-points)
    for j,id_user in enumerate([id_user1,id_user2,id_user3,id_user4,id_user5]):
        data_user=lecture_mesoNH.mesoNH_user(start_day,end_day,id_user,params)
        nb_jour = (end_day-start_day).days
        for i in range(nb_jour+1):
            date_run=start_day+datetime.timedelta(days=i)
            today_str=date_run.strftime('%Y%m%d')
            for param in params:
                try :
                    if isinstance(data_user[today_str][param],(list,np.ndarray)):  # On vérifie qu'il y a des données

                        chartM[param].add_trace(go.Scatter(x=data_user[today_str]['time'], y=data_user[today_str][param], line=dict(color='black',dash=types[j]),name='MésoNH modifié (id : '+str(id_user)+' )'))

                except KeyError :
                    pass
		# Ici le try/except permet de ne rien afficher lorsque les données ne sont pas disponibles


## BIAIS -> le calcul sur les obs permet d'avoir le zéro en affichage (obs - obs = 0)

#    for selection in reseau1:
#        if selection == "Obs" :
#            for param in params:
#                if isinstance(biais[param]['Tf']['values'],(list,np.ndarray)):
#                    chartB[param].add_trace(go.Scatter(x=biais[param]['Tf']['time'], y=biais[param]['Tf']['values'],marker={"color":"red"},mode="lines",name=selection))

		    # Ici plus besoin de try/except, c'est AIDA qui s'en charge


## Pour les différents réseaux d'Arpège :
    for selection in reseau2:
        if selection == "Arp_J-1_00h" :
            reseau = reseaux[0]
            line_param = dict(color='navy',dash='dot')
        if selection == "Arp_J-1_12h" :
            reseau = reseaux[1]
            line_param = dict(color='mediumslateblue',dash='dot')
        if selection == "Arp_J0_00h" :
            reseau = reseaux[2]
            line_param = dict(color='navy')
        if selection == "Arp_J0_12h" :
            reseau = reseaux[3]
            line_param = dict(color='mediumslateblue')
            
        for param in params:
            if isinstance(biais[param]['Gt'][reseau]['values'],(list,np.ndarray)):
                chartM[param].add_trace(go.Scatter(x=biais_moy[param]['Gt'][reseau]['time'], y=biais_moy[param]['Gt'][reseau]['values'], line=line_param,name=selection))


## Pour les différents réseaux d'Arome :    
    for selection in reseau3:
        if selection == "Aro_J-1_00h" :
            reseau = reseaux[0]
            line_param = dict(color='green',dash='dot')
        if selection == "Aro_J-1_12h" :
            reseau = reseaux[1]
            line_param = dict(color='olive',dash='dot')
        if selection == "Aro_J0_00h" :
            reseau = reseaux[2]
            line_param = dict(color='green')
        if selection == "Aro_J0_12h" :
            reseau = reseaux[3]
            line_param = dict(color='olive')
            
        for param in params:
            if isinstance(biais[param]['Rt'][reseau]['values'],(list,np.ndarray)):
                chartM[param].add_trace(go.Scatter(x=biais_moy[param]['Rt'][reseau]['time'], y=biais_moy[param]['Rt'][reseau]['values'], line=line_param,name=selection))    


#!!!!!! A COMPLETER POUR MESO-NH ET SURFEX !!!!!!!!!!!!

## Pour les courbes de MésoNH : 
# A la différence des 3 réseaux précédents où l'on récupère les données sur la période choisie à chaque nouvelle période grâce à AIDA, MésoNH et SURFEX sont stockés par dossier nommé à la date de run.
# Il faut donc parcourir tous les jours entre le start_day et le end_day et stocker les informations lues.

    courbe_affichee=[]    
    for selection in reseau4 :

        nb_jour = (end_day-start_day).days

        for i in range(nb_jour+1):

            day=start_day+timedelta(days=i)
            today_str=day.strftime('%Y%m%d')

            #Gestion du nombre de légende affichée : La légende est affichée si elle absente avant cad si courbe_affichee est vide (courbe affichee est remplie au 1er jour affiche)
            #if selection not in courbe_affichee and dico_model[selection]['name'] in biais['tmp_2m'] and isinstance(biais['tmp_2m'][dico_model[selection]['name']][today_str],(list,np.ndarray)):
            if selection not in courbe_affichee and dico_model[selection]['name'] in biais['tmp_2m']:    


                courbe_affichee.append(selection)
                afficher_legende=True

            else:

                afficher_legende=False

		# Ce montage un peu douteux de if/else permet de n'afficher qu'une seule fois la légende de la courbe MésoNH choisie. Sans ça, le programme affichait autant de fois la légende
		# qu'il y avait de jours entre le start_day et le end_day.

            for param in params:

                try :

                   if isinstance(biais_moy[param][dico_model[selection]['name']]['MNH']['values'],(list,np.ndarray)):

                      chartM[param].add_trace(go.Scatter(x=biais_moy[param][dico_model[selection]['name']]['MNH']['time'], y=biais_moy[param][dico_model[selection]['name']]['MNH']['values'], marker={"color":dico_model[selection]['color']}, mode="lines",name=selection,showlegend=afficher_legende))

                except KeyError :
                    pass
		# Le retour du try/except pour éviter que le script ne se bloque.



## Pour les courbes de Surfex : 
    courbe_affichee_surfex=[]    
    for selection in reseau5 :
        nb_jour = (end_day-start_day).days
        for i in range(nb_jour+1):
            day=start_day+timedelta(days=i)
            today_str=day.strftime('%Y%m%d')
                
            if selection not in courbe_affichee_surfex and dico_model[selection]['name'] in data_surfex[today_str] and isinstance(data_surfex[today_str][dico_model[selection]['name']]['tmp_2m'],(list,np.ndarray)):
                courbe_affichee_surfex.append(selection)
                afficher_legende_surfex=True
            else:
                afficher_legende_surfex=False
            for param in params:
                try :
                    if isinstance(data_surfex[today_str][dico_model[selection]['name']][param],(list,np.ndarray)):
                        chartM[param].add_trace(go.Scatter(x=data_surfex[today_str]['time'], y=data_surfex[today_str][dico_model[selection]['name']][param],line=dict(color=dico_model[selection]['color'],dash='dashdot'),name=selection,showlegend=afficher_legende_surfex))
                except KeyError :
                    pass
        


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        



## Mise à jour des graphiques après tous les changements  
      
    list_chartsM = []

    for param in params:

        chartM[param].update_layout(height=500, width=1000,
                         xaxis_title="Heure de la journéee",
                         yaxis_title=str(dico_params[param]['unit']),
                         title=dico_params[param]['title'])

        list_chartsM.append(chartM[param])
    
    return list_chartsM #Le callback attend des Outputs qui sont contenus dans chartB[param]
 





############### Layout ###############


#!!!!!!!!!!!!!!! Tracé des graphes sur la page correspondantes: à modifier avec les graphes affichant les biais (calculés plus haut)


all_graphsM = []

for param in params:
    all_graphsM.append(html.Div(graphM[param],className="six columns", style={'display': 'inline-block'}))

row3 = html.Div(children=all_graphsM, className="twelve columns")

# Puisqu'on n'a pas la main sur la css (pour l'instant)(cf external_stylesheets au début du code), on joue sur les html.Div.
# Ici par exemple, chaque graph est d'abord mis dans une Div dont on réduit la taille ("className="five columns"),
# puis on met toutes ces Div dans une seule qui elle prend toute la page ("className="twelve columns")


menu = html.Div([
        dcc.Link('Notice__', href='/MeteopoleX/notice'),
        dcc.Link('__Comparaisons Obs MétéoFlux/Modèles__', href='/MeteopoleX/'),
        dcc.Link('__Biais Obs/Modèles__', href='/MeteopoleX/biais'),
        dcc.Link('__Sondages__', href='/MeteopoleX/rs'),
        dcc.Link('__Rejeu MésoNH__', href='/MeteopoleX/mesoNH'),
        dcc.Link('__Rejeu SURFEX', href='/MeteopoleX/surfex')
        ],className="twelve columns",style={"text-align": "right", "justifyContent":"center"})

# le menu diffère de chaque page, il contient une liste de lien (dcc.Link) dont les arguments sont le nom souhaité et son url


biaisM_layout = html.Div([
    html.H1('Biais Moyens'),
    menu,
    calendrier,
    html.Div([multi_select_line_chartM_ARP,multi_select_line_chartM_ARO,
    multi_select_line_chartM_MNH,multi_select_line_chartM_SURFEX],className="eight columns",style={"text-align": "center", "justifyContent":"center"}),
#    html.Div([multi_select_line_chartB_ARP,multi_select_line_chartB_ARO,
#    multi_select_line_chartB_MNH,multi_select_line_chartB_SURFEX],className="eight columns",style={"text-align": "center", "justifyContent":"center"}),
    id_user,
    row3,
],className="twelve columns",style={"text-align": "center", "justifyContent":"center"})

























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
                          "unit":"%"}, #HR n'existe pas dans les obs AMDAR
                     "Vent":
                         {"label":"Vent",
                          "unit":"m/s"}
             }
# Ce dictionnaire permet de nommer les axes des graphiques

options_models = {"Gt":{
                    "name":"MNH-ARPEGE",
                    "line":"dash"}, 
                  "Rt":{
                    "name":"MNH-AROME",
                    "line":"longdash"},
                  "Tf":{
                    "name":"MNH-OBS",
                    "line":"solid"},
                  "ARP":{
                    "name":"ARP-OPER",
                    "line":"dashdot"},
                  "ARO":{
                    "name":"ARO-OPER",
                    "line":"dot"},
                  "Ab":{
                    "name":"OBS-AMDAR",
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


heures_aroarp = {"00h":{
            "value":"00h",
            "num_val":0,
            "color":"black"},
          "3h":{
            "value":"3h",
            "num_val":3,
            "color":"brown"},
          "6h":{
            "value":"6h",
            "num_val":6,
            "color":"red"},
          "9h":{
            "value":"9h",
            "num_val":9,
            "color":"orange"},
          "12h":{
            "value":"12h",
            "num_val":12,
            "color":"green"},
          "15h":{
            "value":"15h",
            "num_val":15,
            "color":"blue"},
          "18h":{
            "value":"18h",
            "num_val":18,
            "color":"purple"},
          "21h":{
            "value":"21h",
            "num_val":21,
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
    


#multi_select_line_chart_obs = dcc.Dropdown(
#        id="multi_select_line_chartB_obs",
#        options=[{"value":label, "label":label} for label in ["Obs"]],
#        value=["Obs"], # Valeur qui s'affiche par défaut (si pas dans la liste des options alors rien n'est affiché)
#        multi=True, # Possibilité d'en choisir plusieur
#        clearable = False
#    )
# Le dcc.Dropdown est un objet dash qui permet l'affichage des options sélectionnables quand on clique dessus, puis la sélection d'une ou plusieurs options.


#multi_select_line_chart_ARP = dcc.Dropdown(
#        id="multi_select_line_chartB_ARP",
#        options=[{"value":label, "label":label} for label in ["Arp_J0_00h",]],
#        value=["Arp_J0_00h"],
#        multi=True,
#        clearable = False
#    )

#multi_select_line_chart_ARO = dcc.Dropdown(
#        id="multi_select_line_chartB_ARO",
#        options=[{"value":label, "label":label} for label in ["Aro_J0_00h"]],
#        value=["Aro_J0_00h"],
#        multi=True,
#        clearable = False
#    )

#multi_select_line_chart_MNH = dcc.Dropdown(
#        id="multi_select_line_chartB_MNH",
#        options=[{"value":label, "label":label} for label in ["MésoNH_Arp","MésoNH_Aro","MésoNH_Obs"]],
#        value=["MésoNH_Arp","MésoNH_Aro"],
#        multi=True,
#        clearable = False
#    )

#multi_select_line_chartB_SURFEX = dcc.Dropdown(
#        id="multi_select_line_chartB_SURFEX",
#        options=[{"value":label, "label":label} for label in ["SURFEX_Arp","SURFEX_Aro","SURFEX_Obs"]],
#        value=["SURFEX_Arp"],
#        multi=True,
#        clearable = False
#    )
     
#id_user = html.Div([
#        dcc.Input(id = 'id_user1',type = 'text',placeholder = 'id de la simulation à rajouter'),
#        dcc.Input(id = 'id_user2',type = 'text',placeholder = 'id de la simulation à rajouter'),
#        dcc.Input(id = 'id_user3',type = 'text',placeholder = 'id de la simulation à rajouter'),
#        dcc.Input(id = 'id_user4',type = 'text',placeholder = 'id de la simulation à rajouter'),
#        dcc.Input(id = 'id_user5',type = 'text',placeholder = 'id de la simulation à rajouter')]) # Attention : dcc.Input != Input (voir plus bas)
# Les dcc.Input sont des carrés où l'utilisateur peut rentrer des info : ici type = 'text' donc du texte, 

    
#Premier chargement des données à la date d'aujourd'hui
data_rs = radio_sondage.radio_sondage(day,models,params_rs,heures,heures_aroarp)

#aroarp_rs = radio_sondage.pv_aroarp(day,models,params_rs,heures)

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

#@app.callback(output_rs, 
#               [Input('multi_select_line_chart_obs', 'value'),
#                [Input('multi_select_line_chart_ARP', 'value'),
#                Input('multi_select_line_chart_ARO', 'value'),
#                Input('multi_select_line_chart_MNH', 'value'),
#                Input('multi_select_line_chart_SURFEX', 'value'),
#                Input('my-date-picker-range', 'start_date'),
#                Input('my-date-picker-range', 'end_date'),
#                Input('id_user1','value'),Input('id_user2','value'),Input('id_user3','value'),Input('id_user4','value'),Input('id_user5','value')
#                ])

def update_rs(wich_heure,date_value,model_choisi):
    
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
    
    # Puis, mise à jour des graphes :
    for param in params_rs:
        chart[param] = go.Figure()
    
    # Extraction des données
    data_rs = radio_sondage.radio_sondage(date_object,models,params_rs,heures,heures_aroarp)
    #aroarp_rs = radio_sondage.pv_aroarp(date_object,models,params_rs,heures)

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

                if model == 'Ab' and len(data_rs[model][selection][param]) > 1 :
                   try:

                      chart[param].add_trace(go.Scatter(x=data_rs[model][selection][param], y=data_rs[model][selection]['level'],line=dict(color=heures[selection]["color"], width=8, dash=options_models[model]["line"]), mode="markers",name=options_models[model]["name"]+' - '+heures[selection]["value"],showlegend=afficher_legende))
                   except KeyError:
                       pass

                else:

                   try :
                          chart[param].add_trace(go.Scatter(x=data_rs[model][selection][param], y=data_rs[model]['level'],line=dict(color=heures[selection]["color"], width=4, dash=options_models[model]["line"]), mode="lines",name=options_models[model]["name"]+' - '+heures[selection]["value"],showlegend=afficher_legende))

                

                   except KeyError:
                       pass
    list_charts = []
    for param in params_rs:
        chart[param].update_layout(height=1300, width=600,
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

row1= html.Div(children=legende,className="six columns")


all_graphs = []
for param in params_rs:
    all_graphs.append(html.Div(graph[param],className="six columns", style={'display': 'inline-block'}))

row2 = html.Div(children=all_graphs, className="six columns")


menu = html.Div([
        dcc.Link('Notice__', href='/MeteopoleX/notice'),
        dcc.Link('__Comparaisons Obs MétéoFlux/Modèles__', href='/MeteopoleX/'),
        dcc.Link('__Biais Obs/Modèles__', href='/MeteopoleX/biais'),
        dcc.Link('__Biais Moyens__', href='/MeteopoleX/biaisM'),
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
    wich_heure,
    multi_select_line_chart_model,
    html.Div(dcc.Textarea(value="Code couleur :", style={'color':"black"}),className="two columns",style={"text-align": "left", "justifyContent":"center"}),
#    html.Div([multi_select_line_chart_ARP,multi_select_line_chart_ARO,
#    multi_select_line_chart_MNH,multi_select_line_chart_SURFEX],className="eight columns",style={"text-align": "center", "justifyContent":"center"}),
#    id_user,
    row1,row2,
    html.Br(),
],className="twelve columns",style={"text-align": "center", "justifyContent":"center"})



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
            #print(start_date)
            mesonh.MesoNH(date_run=today_str, model_couplage="AROME", type_forcage="MODEL", user_params=user_params)
                
        return html.H2('Simulation terminée !')
    else:
        return None

############### Layout ###############

row1=html.Div(children=all_params_html, className="twelve columns")

menu = html.Div([
        dcc.Link('Notice__', href='/MeteopoleX/notice'),
        dcc.Link('__Comparaisons Obs MétéoFlux/Modèles__', href='/MeteopoleX/'),
        dcc.Link('__Biais Obs/Modèles__', href='/MeteopoleX/biais'),
        dcc.Link('__Biais Moyens__', href='/MeteopoleX/biaisM'),
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


########################
#
#   Rejeu SURFEX
#
########################
    
menu = html.Div([
        dcc.Link('Notice__', href='/MeteopoleX/notice'),
        dcc.Link('__Comparaisons Obs MétéoFlux/Modèles__', href='/MeteopoleX/'),
        dcc.Link('__Biais Obs/Modèles__', href='/MeteopoleX/biais'),
        dcc.Link('__Biais Moyens__', href='/MeteopoleX/biaisM'),
        dcc.Link('__Sondages__', href='/MeteopoleX/rs'),
        dcc.Link('__Rejeu MésoNH', href='/MeteopoleX/mesoNH'),
        ],className="twelve columns",style={"text-align": "right", "justifyContent":"center"})

surfex_layout = html.Div([
    html.H1('Rejeu de SURFEX'),
    menu
],className="twelve columns",style={"text-align": "center", "justifyContent":"center"})
    
    


##########################################################################################
#
#   				Gestion des pages
#
##########################################################################################


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/MeteopoleX/':
        return obs_modeles_layout
    elif pathname == '/MeteopoleX/biais':
        return biais_layout
    elif pathname == '/MeteopoleX/biaisM':
        return biaisM_layout
    elif pathname == '/MeteopoleX/mesoNH':
        return mesoNH_layout
    elif pathname == '/MeteopoleX/surfex':
        return surfex_layout
    elif pathname == '/MeteopoleX/rs' :
        return rs_layout
    elif pathname == '/MeteopoleX/notice' :
        return notice_layout
    # You could also return a 404 "URL not found" page here


if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0",port=8010)

#print(data)
