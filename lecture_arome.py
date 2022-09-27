#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 

@author:canut
"""

import netCDF4 as nc
import datetime
from datetime import timedelta


import numpy as np

# Les 2 fonctions ci-dessous sont assez similaires, seulement elles ne
# vont pas chercher les mêmes données aux mêmes endroits (possibilité de
# les regrouper en une seule fonction)


data_arome_filepath= '/cnrm/ktrm/manip/METEOPOLEX/AROME/Toulouse/
#202205/netcdf_tlse.tar.arome_20220501.netcdf'
start_day = datetime.datetime(2022,5,1)
end_day = datetime.datetime(2022,5,2)


def lect_arome(start_day, end_day, models, params,filepath):
    nb_jour = (end_day - start_day).days
    data_arome = {}
    for i in range(nb_jour + 1):
        date_run = start_day + datetime.timedelta(days=i)
        month_str = date_run.strftime('%Y%m')
        today_str = date_run.strftime('%Y%m%d')
        if today_str not in data_arome:
            data_arome[today_str] = {}
            for model in models:
                try:
                    f = nc.Dataset(filepath + month_str + 'netcdf_tlse.tar.arome_'+today_str() +'.nc'
                    if 'time' not in data_mnh[today_str]:
                        data_mnh[today_str]['time'] = {}

                        time_since_reseau = f.variables['time_les'][:]

                        hhmmss_reseau = datetime.time(0, 15, 0)
                        time_reseau = datetime.datetime.combine(date_run, hhmmss_reseau)

                        time = [time_reseau]
                        swich = []

                        for t in time_since_reseau:
                            if time[-1] == time_reseau + timedelta(hours=23, minutes=45):
                                swich.append(1)
                            if len(swich) == 0:
                                time.append(time_reseau + timedelta(seconds=t))
                        data_arome[today_str]['time'] = time
                    if model not in data_arome[today_str]:
                        data_arome[today_str][model] = {}
                        for param in params:
                            if param not in data_arome[today_str][model]:
                                data_arome[today_str][model][param] = {}
                                if param == "tmp_2m":
                                    P = f[groupMEAN].variables['MEAN_PRE'][:, 1]
                                    D = (100000 / P)**(2 / 7)
                                    data_arome[today_str][model][param] = (
                                        f[groupMEAN].variables['MEAN_TH'][:, 1] / D) - 273.15

                                if param == "tmp_10m":
                                    P = f[groupMEAN].variables['MEAN_PRE'][:, 3]
                                    D = (100000 / P)**(2 / 7)
                                    data_arome[today_str][model][param] = (
                                        f[groupMEAN].variables['MEAN_TH'][:, 3] / D) - 273.15
                                if param == "hum_rel":
                                    data_arome[today_str][model][param] = f[groupMEAN].variables['MEAN_REHU'][:, 1]

                                if param == "vent_ff10m":
                                    data_arome[today_str][model][param] = f[groupMEAN].variables['MEANWIND'][:, 3]
                                if param == "flx_mvt":
                                    data_arome[today_str][model][param] = f[groupSURF].variables['Ustar'][:]
                                if param == "flx_chaleur_sens":
                                    data_arome[today_str][model][param] = f[groupSURF].variables['Q0'][:] * \
                                        f.variables['RHODREF'][1] * 1004
                                if param == "flx_chaleur_lat":
                                    data_arome[today_str][model][param] = f[groupSURF].variables['E0'][:] * \
                                        f.variables['RHODREF'][1] * \
                                        2400000  # TODO facteur a corriger
                                if param == "LWU":
                                    data_arome[today_str][model][param] = (f[groupRAD].variables['LWU'][:, 1]+f[groupRAD].variables['LWU'][:, 2])/2
                                if param == "SWD":
                                    data_arome[today_str][model][param] = (f[groupRAD].variables['SWD'][:, 1]+f[groupRAD].variables['SWD'][:, 2])/2
                                if param == "tke":
                                    data_arome[today_str][model][param] = (f[groupSBG].variables['SBG_TKE'][:, 1]+f[groupSBG].variables['SBG_TKE'][:, 2])/2

                except FileNotFoundError:
                    pass
    return data_arome


def mesoNH_user(start_day, end_day, id_user, params):

    nb_jour = (end_day - start_day).days
    data_user = {}
    for i in range(nb_jour + 1):
        date_run = start_day + datetime.timedelta(days=i)
        today_str = date_run.strftime('%Y%m%d')
        if today_str not in data_user:
            data_user[today_str] = {}
            try:
                f = nc.Dataset(
                    '/home/manip/MeteopoleX/models/runs/OUTPUT/MESONH/USER/' +
                    today_str +
                    '00/MESONH_Rt_' +
                    today_str +
                    '00_' +
                    id_user +
                    '.000.nc')
                f2 = nc.Dataset(
                    '/home/manip/MeteopoleX/models/runs/OUTPUT/MESONH/USER/' +
                    today_str +
                    '00/MESONH_Rt_' +
                    today_str +
                    '00_' +
                    id_user +
                    '.nc')

                groupMEAN = '/LES_budgets/Mean/Cartesian/Not_time_averaged/Not_normalized/cart/'
                groupSBG  = '/LES_budgets/Subgrid/Cartesian/Not_time_averaged/Not_normalized/cart/'
                groupSURF = '/LES_budgets/Surface/Cartesian/Not_time_averaged/Not_normalized/cart/'
                groupRAD = '/LES_budgets/Radiation/Cartesian/Not_time_averaged/Not_normalized/cart/'

                if 'time' not in data_user[today_str]:

                    data_user[today_str]['time'] = {}

                    time_since_reseau = f.variables['time_les'][:]

                    hhmmss_reseau = datetime.time(0, 15, 0)
                    time_reseau = datetime.datetime.combine(date_run, hhmmss_reseau)

                    time = [time_reseau]
                    swich = []

                    for t in time_since_reseau:
                        if time[-1] == time_reseau + timedelta(hours=23, minutes=45):
                            swich.append(1)
                        if len(swich) == 0:
                            time.append(time_reseau + timedelta(seconds=t))
                    data_user[today_str]['time'] = time

                for param in params:

                    if param not in data_user[today_str]:
                        data_user[today_str][param] = {}

                        if param == "tmp_2m":
                            P = f[groupMEAN].variables['MEAN_PRE'][:, 1]
                            D = (100000 / P)**(2 / 7)
                            data_user[today_str][param] = (
                                f[groupMEAN].variables['MEAN_TH'][:, 1] / D) - 273.15

                        if param == "tmp_10m":
                            P = f[groupMEAN].variables['MEAN_PRE'][:, 3]
                            D = (100000 / P)**(2 / 7)
                            data_user[today_str][param] = (
                                f[groupMEAN].variables['MEAN_TH'][:, 3] / D) - 273.15

                        if param == "hum_rel":
                            data_user[today_str][param] = f[groupMEAN].variables['MEAN_REHU'][:, 3]

                        if param == "vent_ff10m":
                            data_user[today_str][param] = f[groupMEAN].variables['MEANWIND'][:, 3]

                        if param == "flx_mvt":
                            data_user[today_str][param] = f[groupSURF].variables['Ustar'][:]
                        if param == "flx_chaleur_sens":
                            data_user[today_str][param] = f[groupSURF].variables['Q0'][:] * \
                                f.variables['RHODREF'][1] * 1004
                        if param == "flx_chaleur_lat":
                            data_user[today_str][param] = f[groupSURF].variables['E0'][:] * \
                                f.variables['RHODREF'][1] * 2400000  # TODO facteur a corriger
                        if param == "LWU":
                            data_user[today_str][param] = (f[groupRAD].variables['LWU'][:, 1]+f[groupRAD].variables['LWU'][:, 2])/2
                        if param == "SWD":
                            data_user[today_str][param] = (f[groupRAD].variables['SWD'][:, 1]+f[groupRAD].variables['SWD'][:, 2])/2
                        if param == "tke":
                            data_user[today_str][param] = (f[groupSBG].variables['SBG_TKE'][:, 1]+f[groupSBG].variables['SBG_TKE'][:, 2])/2
            except FileNotFoundError:
                pass
            except TypeError:
                pass
    return data_user
