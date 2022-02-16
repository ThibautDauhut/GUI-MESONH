#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 09:21:41 2021

@author: avrillauds
"""
import netCDF4 as nc
import datetime


def radio_sondage(day,models,params_rs,heures):
    data_rs={}
    today_str=day
    today_str=str(day.year)
    if len(str(day.month))==1:
        today_str=today_str+'0'+str(day.month)
    else :
        today_str=today_str+str(day.month)
    if len(str(day.day))==1:
        today_str=today_str+'0'+str(day.day)
    else :
        today_str=today_str+str(day.day)
    
    for model in models:
        try :
            f = nc.Dataset('/d0/MeteopoleX/models/runs/OUTPUT/MESONH/OPER/'+today_str+'00/MESONH_'+model+'_'+today_str+'00.000.nc')

            groupMEAN = '/LES_budgets/Mean/Cartesian/Not_time_averaged/Not_normalized/cart/'


            # ou bien /home/models/OUTPUT/MESONH
            if 'level' not in data_rs:
                data_rs['level']= f.variables['level'][:]
                
            if model not in data_rs :
                data_rs[model]={}
                
                for heure in heures :
                    if heure not in data_rs[model]:
                        data_rs[model][heure]={}
                        
                        for param in params_rs :
                            if param not in data_rs[model][heure]:
                                data_rs[model][heure][param]={}
                                if param == "Température" :
                                    P = f[groupMEAN].variables['MEAN_PRE'][heures[heure]['num_val'],:]
                                    D = (100000/P)**(2/7)  
                                    data_rs[model][heure][param]= (f[groupMEAN].variables['MEAN_TH'][heures[heure]['num_val'],:] / D)-273.15
                                    
                                if param == "Humidité relative":
                                    data_rs[model][heure][param]= f[groupMEAN].variables['MEAN_REHU'][heures[heure]['num_val'],:]
                                    
                                if param == "Vent":
                                    #U=f['MEAN_U___PROC1'][0,heures[heure]['num_val'],:,0,0].data[:]
                                    #V=f['MEAN_V___PROC1'][0,heures[heure]['num_val'],:,0,0].data[:]
                                    data_rs[model][heure][param]=f[groupMEAN].variables['MEANWIND'][heures[heure]['num_val'],:]
        except FileNotFoundError:
            pass
    
    return data_rs





#f = nc.Dataset('/cnrm/ktrm/stagiaire/mosai_2021/DEV/MESONH/2021011400/MESONH_Gt_2021011400.000.nc')
#day=datetime.date(2021,1,1)
#params_rs = ["Température","Humidité relative","Vent"]        
#models = ["Gt", "Rt","Tf"]
#heures = {"00h":{
#            "num_val":0},
#          "3h":{
#            "num_val":12},
#          "6h":{
#            "num_val":24},
#          "9h":{
#            "num_val":36},
#          "12h":{
#            "num_val":48},
#          "15h":{
#            "num_val":60},
#          "18h":{
#            "num_val":72},
#          "21h":{
#            "num_val":84}}
#          # on fait l'heure x 4 puisqu'il y a une valeur tous les quarts d'heure; ex: pour 9h on prend la 9x4=36ème valeur
#data_rs=radio_sondage(day,models,params_rs,heures)
#print(data_rs)
