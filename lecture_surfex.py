#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 15:25:41 2021

@author: avrillauds
"""
import netCDF4 as nc
import datetime
from datetime import timedelta

# extraction des variables


def surfex(start_day, end_day, models, params):
    nb_jour = (end_day - start_day).days
    data_surfex = {}
    for i in range(nb_jour + 1):
        today = start_day + datetime.timedelta(days=i)
        today_str = str(today.year)
        if len(str(today.month)) == 1:
            today_str = today_str + '0' + str(today.month)
        else:
            today_str = today_str + str(today.month)
        if len(str(today.day)) == 1:
            today_str = today_str + '0' + str(today.day)
        else:
            today_str = today_str + str(today.day)
        if today_str not in data_surfex:
            data_surfex[today_str] = {}
            for model in models:
                try:
                    f = nc.Dataset('/cnrm/ktrm/stagiaire/mosai_2021/DEV/SURFEX/' +
                                   today_str + '/SURFEX_' + today_str + '_' + model + '.nc')
                # ou bien /home/manip/METEOPOLEX/OUTPUT/SURFEX
                    if 'time' not in data_surfex[today_str]:
                        data_surfex[today_str]['time'] = {}
                        time_reseau = datetime.datetime(int(today_str[:4]), int(
                            today_str[4:6]), int(today_str[6:8]), 0, 0, 0)
                        time = [time_reseau]
                        for i in range(1, 24):
                            time.append(time_reseau + timedelta(hours=i))
                        data_surfex[today_str]['time'] = time
                    if model not in data_surfex[today_str]:
                        data_surfex[today_str][model] = {}
                        for param in params:
                            if param not in data_surfex[today_str][model]:
                                data_surfex[today_str][model][param] = {}
                                if param == "tmp_2m":
                                    data_surfex[today_str][model][param] = f['T2M'][:,
                                                                                    0, 0][:24] - 273.15
                                if param == "tmp_10m":
                                    data_surfex[today_str][model][param] = []
                                if param == "vent_ff10m":
                                    data_surfex[today_str][model][param] = []
                                if param == "hum_rel":
                                    data_surfex[today_str][model][param] = f['HU2M'][:,
                                                                                     0, 0][:24] * 10000  # TODO conversion HU
#                                if param == "flx_mvt":
#                                    data_surfex[today_str][model][param] = []
                                if param == "flx_chaleur_sens":
                                    data_surfex[today_str][model][param] = f['H'][:, 0, 0][:24]
                                if param == "flx_chaleur_lat":
                                    data_surfex[today_str][model][param] = f['LE'][:, 0, 0][:24]
                                if param == "LWU":
                                    data_surfex[today_str][model][param] = f['LWU'][:,
                                                                                    0, 0].data[:24]
                                if param == "SWD":
                                    data_surfex[today_str][model][param] = f['SWD'][:,
                                                                                    0, 0].data[:24]
                                if param == "t_surface":
                                    data_surfex[today_str][model][param] = f['TSRAD_ISBA'][:,
                                                                                           0, 0].data[:24] - 273.15
                                if param == "t-1":
                                    data_surfex[today_str][model][param] = f['TG1_ISBA'][:,
                                                                                         0, 0].data[:24] - 273.15
                                if param == "hu_couche1":
                                    data_surfex[today_str][model][param] = f['WG1_ISBA'][:,
                                                                                         0, 0].data[:24]
                except FileNotFoundError:
                    pass
    return data_surfex
