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

import rejeu_mesonh
import rejeu_surfex

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

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True,title='MeteopoleX')
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
server=app.server
app.config.update({
                'requests_pathname_prefix': '/MeteopoleX/',
                'routes_pathname_prefix': '/'
                })

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

today=datetime.date.today()
yesterday=today-timedelta(days=1)
end_day=today-timedelta(days=1)
start_day=today-timedelta(days=1)
doy1 = datetime.datetime(int(start_day.year),int(start_day.month),int(start_day.day)).strftime('%j')
doy2 = datetime.datetime(int(end_day.year),int(end_day.month),int(end_day.day)).strftime('%j')


##############################
#
#   Comparaison Obs/Modèles
#
##############################

#Voir programme comp_obs_model.py




########################
#
#   Sondages
#
########################

#Voir programme sondages.py






#########################
#
#   Rejeu MésoNH
#
#########################

#Voir programme rejeu_mesonh.py





########################
#
#   Rejeu SURFEX
#
########################
    
#voir programme rejeu_surfex

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
