#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 15:39:56 2021

@author: avrillauds
"""

import netCDF4 as nc
import datetime
from datetime import timedelta

# Les 2 fonctions ci-dessous sont assez similaires, seulement elles ne vont pas chercher les mêmes données aux mêmes endroits (possibilité de les regrouper en une seule fonction)

def mesoNH (start_day,end_day,models,params):
    nb_jour = (end_day-start_day).days
    data_mnh = {} 
    for i in range(nb_jour+1):
        date_run=start_day+datetime.timedelta(days=i)
        today_str=date_run.strftime('%Y%m%d')
        if today_str not in data_mnh :
            data_mnh[today_str]={}
            for model in models:
                try :
                    f = nc.Dataset('/d0/MeteopoleX/manip/METEOPOLEX/OUTPUT/MESONH/OPER/'+today_str+'00/MESONH_'+model+'_'+today_str+'00.000.nc')
                            #TODO try 2 lecture fichier HBLTOP
                #ou bien /home/manip/METEOPOLEX/OUTPUT/MESONH
                    if 'time' not in data_mnh[today_str] :
                        data_mnh[today_str]['time'] = {}
                        time_since_reseau=f['MEAN_U___DATIM'][:,15].data
                        time_reseau = datetime.datetime(f['MEAN_U___DATIM'][0,0],f['MEAN_U___DATIM'][0,1],f['MEAN_U___DATIM'][0,2])
                        time = [time_reseau]
                        swich=[]
                        for t in time_since_reseau :
                            if time[-1]==time_reseau+timedelta(hours=23,minutes=45):
                                swich.append(1)
                            if len(swich)==0:
                                time.append(time_reseau+timedelta(seconds=t))
                        data_mnh[today_str]['time']=time
                    if model not in data_mnh[today_str]:
                        data_mnh[today_str][model] = {}
                        for param in params:
                            if param not in data_mnh[today_str][model]:
                                data_mnh[today_str][model][param] = {}
                                if param == "tmp_2m":
                                    P = f['MEAN_PRE___PROC1'][0, :, 2, 0, 0].data[:96]
                                    D = (100000/P)**(2/7)  
                                    data_mnh[today_str][model][param]= (f['MEAN_TH___PROC1'][0, :, 2, 0, 0].data[:96] / D)-273.15
                                if param == "tmp_10m":
                                    P = f['MEAN_PRE___PROC1'][0, :, 5, 0, 0].data[:96]
                                    D = (100000/P)**(2/7)  
                                    data_mnh[today_str][model][param] = (f['MEAN_TH___PROC1'][0, :, 5, 0, 0].data [:96]/ D)-273.15
                                if param == "hum_rel":
                                    data_mnh[today_str][model][param] = f['MEAN_REHU___PROC1'][0,:,2,0,0].data[:96]
                                if param == "vent_ff10m":
                                    U=f['MEAN_U___PROC1'][0,:,5,0,0].data[:96]
                                    V=f['MEAN_V___PROC1'][0,:,5,0,0].data[:96]
                                    data_mnh[today_str][model][param]=(U**2+V**2)**(1/2)
                                if param == "flx_mvt":
                                    U=f['SBG_WU___PROC1'][0, :, 2, 0, 0].data[:96]
                                    V=f['SBG_WV___PROC1'][0, :, 2, 0, 0].data[:96]
                                    data_mnh[today_str][model][param] = (U**2+V**2)**(1/2)
                                if param == "flx_chaleur_sens":
                                    data_mnh[today_str][model][param] = f['Q0___PROC1'][0,:,0,0,0].data[:96]*f['RHODREF'][2,0,0]*1004
                                if param == "flx_chaleur_lat":
                                    data_mnh[today_str][model][param] = f['E0___PROC1'][0,:,0,0,0].data[:96]*f['RHODREF'][2,0,0]*2.501*10e3 #TODO facteur a corriger
                                if param == "LWU":
                                    data_mnh[today_str][model][param] = f['LWU___PROC1'][0,:,2,0,0].data[:96]
                                if param == "SWD":
                                    data_mnh[today_str][model][param] = f['SWD___PROC1'][0,:,2,0,0].data[:96]
#TODO paramètres inconnus dans les fichiers 00.000.nc
#                                if param == "t_surface":
#                                    f = nc.Dataset('/cnrm/ktrm/stagiaire/mosai_2021/DEV/MESONH/2021010400/MESONH_Gt_2021010400.nc')
#                                    data_mnh[today_str][model][param] = f['TSRAD_NAT'][1,1].data[:96]
#                                if param == "t-1":
#                                    f = nc.Dataset('/cnrm/ktrm/stagiaire/mosai_2021/DEV/MESONH/2021010400/MESONH_Gt_2021010400.nc')
#                                    data_mnh[today_str][model][param] = f['TG1P1'][1,1].data[:96]
                                if param == "altitude_CL" :
                                    data_mnh[today_str][model][param] = f['HBLTOP'].data[:96]



                                    
                except FileNotFoundError:
                    pass
    return data_mnh



def mesoNH_user(start_day,end_day,id_user,params):
    
    nb_jour = (end_day-start_day).days
    data_user = {} 
    for i in range(nb_jour+1):
        date_run=start_day+datetime.timedelta(days=i)
        today_str=date_run.strftime('%Y%m%d')
        if today_str not in data_user :
            data_user[today_str]={}
            try :
                f = nc.Dataset('/d0/MeteopoleX/manip/METEOPOLEX/OUTPUT/MESONH/USER/'+today_str+'00/MESONH_Rt_'+today_str+'00_'+id_user+'.000.nc')
                if 'time' not in data_user[today_str] :
                        data_user[today_str]['time'] = {}
                        time_since_reseau=f['MEAN_U___DATIM'][:,15].data
                        time_reseau = datetime.datetime(f['MEAN_U___DATIM'][0,0],f['MEAN_U___DATIM'][0,1],f['MEAN_U___DATIM'][0,2])
                        time = [time_reseau]
                        swich=[]
                        for t in time_since_reseau :
                            if time[-1]==time_reseau+timedelta(hours=23,minutes=45):
                                swich.append(1)
                            if len(swich)==0:
                                time.append(time_reseau+timedelta(seconds=t))
                        data_user[today_str]['time']=time
                for param in params:
                    if param not in data_user[today_str]:
                        data_user[today_str][param] = {}
                        if param == "tmp_2m":
                            P = f['MEAN_PRE___PROC1'][0, :, 2, 0, 0].data[:96]
                            D = (100000/P)**(2/7)  
                            data_user[today_str][param]= (f['MEAN_TH___PROC1'][0, :, 2, 0, 0].data[:96] / D)-273.15
                        if param == "tmp_10m":
                            P = f['MEAN_PRE___PROC1'][0, :, 5, 0, 0].data[:96]
                            D = (100000/P)**(2/7)  
                            data_user[today_str][param] = (f['MEAN_TH___PROC1'][0, :, 5, 0, 0].data [:96]/ D)-273.15
                        if param == "hum_rel":
                            data_user[today_str][param] = f['MEAN_REHU___PROC1'][0,:,2,0,0].data[:96]
                        if param == "vent_ff10m":
                            U=f['MEAN_U___PROC1'][0,:,5,0,0].data[:96]
                            V=f['MEAN_V___PROC1'][0,:,5,0,0].data[:96]
                            data_user[today_str][param]=(U**2+V**2)**(1/2)
                        if param == "flx_mvt":
                            U=f['SBG_WU___PROC1'][0, :, 2, 0, 0].data[:96]
                            V=f['SBG_WV___PROC1'][0, :, 2, 0, 0].data[:96]
                            data_user[today_str][param] = (U**2+V**2)**(1/2)
                        if param == "flx_chaleur_sens":
                            data_user[today_str][param] = f['Q0___PROC1'][0,:,0,0,0].data[:96]*f['RHODREF'][2,0,0]*1004
#TODO partie qui bug pour l'affichage des rejeux
#                        if param == "flx_chaleur_lat":
#                            data_user[today_str][param] = f['E0___PROC1'][0,:,0,0,0].data[:96]*f['RHODREF'][2,0,0]*2.501*10e6
#                        if param == "LWU":
#                            data_user[today_str][param] = f['LWU___PROC1'][0,:,2,0,0].data[:96]
#                        if param == "SWD":
#                            data_user[today_str][param] = f['SWD___PROC1'][0,:,2,0,0].data[:96]
                        
            except FileNotFoundError:
                pass
            except TypeError:
                pass
    return data_user
    
    
