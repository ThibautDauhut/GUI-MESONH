#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 09:21:41 2021

@author: avrillauds
"""
import netCDF4 as nc
import datetime

from datetime import timedelta,date

import numpy as np

import matplotlib.pyplot as plt

from scipy import interpolate

#Lecture obs AMDAR
import read_aida

import pandas as pd



def radio_sondage(day,models,params_rs,heures,heures_aroarp):
    data_rs={}
    today=day
    today_str=str(day.year)
    if len(str(day.month))==1:
        today_str=today_str+'0'+str(day.month)
    else :
        today_str=today_str+str(day.month)

    yyyymm = today_str

    if len(str(day.day))==1:
        today_str=today_str+'0'+str(day.day)
    else :
        today_str=today_str+str(day.day)
    
    for model in models:
        try :
            f = nc.Dataset('/d0/MeteopoleX/models/runs/OUTPUT/MESONH/OPER/'+today_str+'00/MESONH_'+model+'_'+today_str+'00.000.nc')

            groupMEAN = '/LES_budgets/Mean/Cartesian/Not_time_averaged/Not_normalized/cart/'


            # ou bien /home/models/OUTPUT/MESONH

            if model not in data_rs :
                data_rs[model]={}

                #print("CLEFS DICO MODELS : ", data_rs.keys())

            if 'level' not in data_rs[model]:
                data_rs[model]['level']= f.variables['level'][:]
                
                
                for heure in heures :
                    if heure not in data_rs[model]:
                        data_rs[model][heure]={}
                        
                        for param in params_rs :
                            if param not in data_rs[model][heure]:
                                data_rs[model][heure][param]={}
                                if param == "Température" :
                                    P = f[groupMEAN].variables['MEAN_PRE'][heures[heure]['num_val'],:]
                                    D = (100000/P)**(2/7)  
                                    data_rs[model][heure][param]= (f[groupMEAN].variables['MEAN_TH'][heures[heure]['num_val'],:] / D) - 273.15
                                    
                                if param == "Humidité relative":
                                    data_rs[model][heure][param]= f[groupMEAN].variables['MEAN_REHU'][heures[heure]['num_val'],:]
                                    
                                if param == "Vent":
                                    #U=f['MEAN_U___PROC1'][0,heures[heure]['num_val'],:,0,0].data[:]
                                    #V=f['MEAN_V___PROC1'][0,heures[heure]['num_val'],:,0,0].data[:]
                                    data_rs[model][heure][param]=f[groupMEAN].variables['MEANWIND'][heures[heure]['num_val'],:]
        except FileNotFoundError:
            pass



    for model in ['ARP', 'ARO']:
        try :
            if model == 'ARP' :

               f = nc.Dataset('/cnrm/proc/bazile/NetCdf/Toulouse/'+yyyymm+'/Arpege-oper-L105_Toulouse_'+today_str+'00.nc')

            elif model == 'ARO' : 

               f = nc.Dataset('/cnrm/ktrm/manip/METEOPOLEX/AROME/Toulouse/'+yyyymm+'/netcdf_tlse.tar.arome_'+today_str+'.netcdf')
                                    

                
            if model not in data_rs :
               data_rs[model]={}

            if 'level' not in data_rs[model]:

                if model == 'ARP' :

                   data_rs[model]['level']= f['height_h'][1,::-1]

                if model == 'ARO' :
               
                   """
                   lvl_aro = [5.00148256575414, 16.7609146275979, 31.9999856716034, 50.6506387418972, 72.6448134875948, 97.914455630736, 126.391508411840, 158.007915671418, 192.695621996127, 
230.386571302649, 271.012706897240, 314.505973414367, 360.798314810016, 409.821674828922, 461.507997847950, 515.890042408161, 573.093937517738, 633.231198491812, 
696.398736766220, 762.678848044096, 832.139215500780, 904.832909766711, 980.798389785428, 1060.05950095623, 1142.62547636213, 1228.49093654830, 1317.63588971212, 
1410.02573054417, 1505.73432230725, 1604.93984760156, 1707.79812299161, 1814.44258334521, 1924.98428740911, 2039.51193175523, 2158.09183540232, 2280.76794378598, 
2407.56182949566, 2538.47269089309, 2673.47735336959, 2812.53026865253, 2955.56351459630, 3102.48360541930, 3253.19498943504, 3407.62661862652, 3565.73195622143, 
3727.48898443499, 3892.90019410005, 4061.99258757885, 4234.81767907587, 4411.45149612596, 4591.99457746971, 4776.57197432233, 4965.33325159684, 5158.45249292134, 
5356.12828712931, 5558.65852457596, 5766.45816179863, 5980.00284181189, 6199.82890110527, 6426.53336977965, 6660.77397670184, 6903.26915353359, 7154.79804227343, 
7416.20049682756, 7688.37709125546, 7972.28912861375, 8268.07660797884, 8575.22917035383, 8893.62412699775, 9223.52646472597, 9565.58886389478, 9920.85173976858, 
10290.7432801852, 10677.0795176319, 11082.0546910758, 11510.3223903101, 11966.1795634141, 12454.7528314299, 12982.0128918015, 13554.6557230282, 14180.1025765563, 
14866.4999945363, 15627.4731252487, 16485.0471290191, 17467.8152385289, 18610.9387773901, 19955.6070022098, 21550.0160473017, 23450.1477297912, 34461.1214067193]
                   """
  
                   data_rs[model]['level']= f['height_h'][1,::-1]

                for heure in heures_aroarp :

                    if heure not in data_rs[model]:
                       data_rs[model][heure]={}
     
                    for param in params_rs :

                        if param not in data_rs[model][heure]:
                           data_rs[model][heure][param]={}

                        if param == "Température" : 

                           data_rs[model][heure][param]= (f['t'][heures_aroarp[heure]['num_val'],::-1] - 273.15)

                        if param == "Humidité relative":
                           data_rs[model][heure][param]= (f['hr'][heures_aroarp[heure]['num_val'],::-1]*100)
                                    
                        if param == "Vent":
                           data_rs[model][heure][param]=f['Vamp'][heures_aroarp[heure]['num_val'],::-1]
         
        except FileNotFoundError:
            pass




#Observations AMDAR

    model = 'Ab'

    yesterday = today-timedelta(days=1)

    doy = datetime.datetime(int(yesterday.year),int(yesterday.month),int(yesterday.day)).strftime('%j')

    print("DAY : ", yesterday)
    print("DOY : ", doy)

    if model not in data_rs :

     data_rs[model] = {}
 
     #Extraction des données sous AIDA
     (z_val, time, header)=read_aida.donnees(doy,doy,str(today.year),'alt_pre_amdar_cal_%60',model)
     (t_val, time, header)=read_aida.donnees(doy,doy,str(today.year),'tpr_air_amdar_cal_%60',model)
     (ff_val, time, header)=read_aida.donnees(doy,doy,str(today.year),'ven_ffmoy_amdar_cal_%60',model)
      
     #Construction du dataframe regrouypant Z, T et FF
     df_z  = pd.DataFrame(list(z_val), index=(time))
     df_t  = pd.DataFrame(list(t_val), index=(time))
     df_ff = pd.DataFrame(list(ff_val), index=(time))

     df_amdar=pd.concat([df_z, df_t], axis=1)
     df_amdar=pd.concat([df_amdar, df_ff], axis=1)


     #Nomination des colonnes
     df_amdar.columns = ['altitude', 'temperature', 'vent']

     #Conversion K -> degC
     df_amdar['temperature'] = df_amdar['temperature']-273.15



     ih=0  
     
     for heure in heures_aroarp :  

           ih=ih+1
  
           if heure not in data_rs[model]:
              data_rs[model][heure]={}

           #Construction d'une plage horaire dont on va prendre les données
           if  ih < 5 :

              date_profil = yesterday.strftime('%Y-%m-%d 0'+heure[0:1]+':%M:%S')

              if ih == 1 : 

                 date_start = datetime.datetime.strptime(date_profil, "%Y-%m-%d %H:%M:%S")
                 date_end   = datetime.datetime.strptime(date_profil, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)

              else :

                 date_start = datetime.datetime.strptime(date_profil, "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)
                 date_end   = datetime.datetime.strptime(date_profil, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)

           else :

              date_profil = yesterday.strftime('%Y-%m-%d '+heure[0:2]+':%M:%S')  
 
              date_start = datetime.datetime.strptime(date_profil, "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)
              date_end   = datetime.datetime.strptime(date_profil, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)

           #Sélection de la plage horaire dans le dataframe 
           mask = (df_amdar.index > date_start) & (df_amdar.index < date_end)


           if 'level' not in data_rs[model][heure]:

              data_rs[model][heure]['level'] = list(df_amdar['altitude'].loc[mask])
               
              print("Z : ", df_amdar['altitude'].loc[mask])

           for param in params_rs :

               if param not in data_rs[model][heure]:
                  data_rs[model][heure][param]={}

               if param == "Température" :  
                
                  data_rs[model][heure][param] = list(df_amdar['temperature'].loc[mask])

               if param == "Vent":

                  data_rs[model][heure][param] = list(df_amdar['vent'].loc[mask])
  
    return data_rs


