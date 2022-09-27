#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shortuuid
import base64
import numpy as np

import os
import time
import datetime
from datetime import timedelta, date

from dateutil.relativedelta import relativedelta

#from datetime import datetime

import matplotlib.dates as mdates

# Tous les programmes qui permettent de récupérer les données
import read_aida

# Besoin de l'utilisation de dataframes pour les calculs de différences
# entre obs/modèle (grille temporelle différente)
import pandas as pd

today = datetime.date.today()
# today=datetime.date.today()-timedelta(days=2)
yesterday = today - timedelta(days=1)
#end_day = today - timedelta(days=1)
#start_day = today - timedelta(days=7)
end_day = today
start_day = today - timedelta(days=1)
doy1 = datetime.datetime(int(start_day.year), int(
    start_day.month), int(start_day.day)).strftime('%j')
doy2 = datetime.datetime(int(end_day.year), int(end_day.month), int(end_day.day)).strftime('%j')

##############################
#
#   Comparaison Obs/Modèles
#
##############################


############### Données ###############
# Lecture des données dans AIDA
dico_params = {
    "tmp_2m": {
        "index_obs": "tpr_air_bs_c1_%60_Met_%1800",
        "index_model": "tpr_air2m",
        "title": "Température à 2m",
        "unit": "°C"
    },
    "tmp_10m": {
        "index_obs": "tpr_air_ht_c1_%60_Met_%1800",
        "index_model": "tpr_air10m",
        "title": "Température à 10m",
        "unit": "°C"
    },
    "hum_rel": {
        "index_obs": "hum_relcapa_bs_c1_%60_Met_%1800",
        "index_model": "hum_rel",
        "title": "Humidité relative",
        "unit": "%"
    },
    "vent_ff10m": {
        "index_obs": "ven_ff_10mn_c1_UV_%1800",
        "index_model": "ven_ff10m",
        "title": "Vent moyen à 10m",
        "unit": "m/s"
    },
    "flx_mvt": {
        "index_obs": "flx_mvt_Chb_%1800",
        "index_model": "flx_mvt",
        "title": "Vitesse de friction",
        "unit": "m/s"
    },
    "tke": {
        "index_obs": "trb_ect_gill_tke_%1800",
        "index_model": "",
        "title": "Energie cinétique turbulente",
        "unit": "m²/s²"
        },
    "flx_chaleur_sens": {
        "index_obs": "flx_hs_tson_Chb_%1800",
        "index_model": "flx_hs",
        "title": "Flux de chaleur sensible",
        "unit": "W/m²"
    },
    "flx_chaleur_lat": {
        "index_obs": "flx_le_Chb_%1800",
        "index_model": "flx_le",
        "title": "Flux de chaleur latente",
        "unit": "W/m²"
    },    
    "SWD": {
        "index_obs": "ray_rgd_cnr1_c2_%60_Met_%1800",
        "index_model": "ray_rgd",
        "title": "Rayonnement global descendant (SW)",
        "unit": "W/m²"
    },
    "LWU": {
        "index_obs": "ray_irm_cnr1_c2_%60_Met_%1800",
        "index_model": "ray_irm",
        "title": "Rayonnement IR montant (LW)",
        "unit": "W/m²"
    },    
    "flx_chaleur_sol": {
        "index_obs": "flx_phi0_moy_c2_%60",
        "index_model": "",
        "title": "Flux de conduction dans le sol",
        "unit": "W/m²"
    },
    "t_surface": {
        "index_obs": "tpr_solIR_c1_%60",
        "index_model": "",
        "title": "Température de surface",
        "unit": "°C"
    },
    "t-1": {
        "index_obs": "tpr_sol1cm_c4_%900_Met_%1800",
        "index_model": "",
        "title": "Température du sol à -1 cm",
        "unit": "°C"
    },
    "hu_couche1": {
        "index_obs": "hum_sol1cm_ec5_c3_%900_Met_%1800",
        "index_model": "",
        "title": "Humidité de la première couche",
        "unit": "kg/kg"
    },
    "cumul_RR": {
        "index_obs": "prp_rr_min_c2_%60_Som_%1800",
        "index_model": "",
        "title": "Cumuls de pluie (Obs: 30mn, ARO-ARP: 1h, MNH: 15mn)",
        "unit": "mm"
    },
    "altitude_CL": {
        "index_obs": "",
        "index_model": "",
        "title": "Altitude de la couche limite",
        "unit": "m"
    },
}

params = [
    "tmp_2m",
    "tmp_10m",
    "hum_rel",
    "vent_ff10m",
    "flx_mvt",
    "tke",
    "flx_chaleur_sens",
    "flx_chaleur_lat",
    "SWD",
    "LWU",    
    "flx_chaleur_sol",
    "t_surface",
    "t-1",
    "hu_couche1",
    "cumul_RR",
    "altitude_CL"]


models = ["Gt", "Rt", "Tf"]

reseaux = ["J-1:00_%3600", "J-1:12_%3600", "J0:00_%3600", "J0:12_%3600"]

def selection_donnees(start_day, end_day):

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

    doy1 = datetime.datetime(int(start_day.year), int(
        start_day.month), int(start_day.day)).strftime('%j')
    doy2 = datetime.datetime(int(end_day.year), int(end_day.month), int(end_day.day)).strftime('%j')
    data = {}

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
                        # Read AIDA : lit tous les paramètres alors que selection de données va
                        # lire uniquement un parametre specifique
                        (values, time, header) = read_aida.donnees(
                            doy1, doy2, str(start_day.year), id_aida, model)
                        data[param][model]['values'] = values
                        data[param][model]['time'] = time

                        break

                    else:

                        id_aida = dico_params[param]["index_model"] + "_" + reseau
                        (values, time, header) = read_aida.donnees(
                            doy1, doy2, str(start_day.year), id_aida, model)
                        data[param][model][reseau]['values'] = values

                        data[param][model][reseau]['time'] = time

# Correction des données ARPEGE parfois datées à H-1:59 au lieu de H:00
                        if time is not None:

                            i = 0

                            for ts in time:

                                if ts.minute == 59.:

                                    time[i] = time[i] + datetime.timedelta(minutes=1)

                                    i = i + 1

                                else:

                                    i = i + 1

                        # Les flux pour AROME et ARPEGE OPER sont agrégés entre H et H+1 : On les
                        # replace à H:30 pour davantage de réalisme
                        if param == 'flx_mvt' or param == 'flx_chaleur_sens' or param == 'flx_chaleur_lat' or param == 'SWD' or param == 'LWU':

                            if time is not None:

                                i = 0

                                for ts in time:

                                    time[i] = time[i] - datetime.timedelta(minutes=30)

                                    i = i + 1

    return data


start_day = datetime.date(2022,6,27)
end_day = datetime.date(2022,6,28)

# Première extraction des données
data = selection_donnees(start_day, end_day)
#print(data['SWD']['Rt']['J0:00_%3600'])
print(data['SWD']['Rt'])
print(data['vent_ff10m']['Rt'].keys())
print(data['vent_ff10m']['Rt']['J0:00_%3600']['values'][:24])

