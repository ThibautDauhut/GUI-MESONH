#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 11:59:53 2021

@author: Axel Bouchet
Contact: axel.bouchet@meteo.fr

"""

import numpy as np
from datetime import datetime, timedelta
from subprocess import call
import os
import netCDF4 as nc
import shortuuid
import read_aida
import glob

path = '/d0/MeteopoleX/models/MNH-V5-5-0/MY_RUN/OPER/'  # '/cnrm/ktrm/stagiaire/mosai_2021/DEV/web_20210402/'
path_output = '/d0/MeteopoleX/models/runs/OUTPUT/MESONH/'  # '/cnrm/ktrm/stagiaire/mosai_2021/DEV/MESONH/'


class MesoNH:
    """
    Classe MesoNH
    
    Entrée :
        - (optionnel) str date_run : 
            date du run du modèle de couplage, correspondra aussi à la date du run 
            de MESO-NH | isoformat(par ex : YYYY-mm-ddTHH:ii:ss) ou *latest*
        
        - (optionnel) str model_couplage : nom du modèle de couplage € {*AROME*, 
        ARPEGE}
        
        - (optionnel) str type_forcage : type de forçage au sol € {*MODEL*, 
        OBS}^
        
    NB: Entre astérisques (*) les valeurs prises par défaut.
        
        
    Sortie :
        - None
        
    Exemple avec 3 simulations:
    1. MesoNH()
    2. MesoNH(model_couplage='ARPEGE', user_params={"id": "AxD4f5", "CCLOUD": "LIMA", "CTURB": "TKEL"})
    3. MesoNH(date_run="2021-01-23T00:00:00", type_forcage='OBS')
    """
    
    def __init__(self, date_run = 'latest', model_couplage = 'AROME', type_forcage = 'MODEL', user_params = {}):
        """
        Constructeur de MesoNH
        
        Le constructeur lance à lui seul toutes les étapes nécessaires au bon
        fonctionnement du modèle. En commentant telle ou telle étape, il est
        relativement aisé de débugger le code. 
        
        Le constructeur est divisé en deux parties : dans la première sont
        définies les propriété d'un objet MesoNH, dans la seconde sont lancées
        une à une les étapes de modélisations.
        """
        
        ##############################
        # DECLARATION DES PROPRIETES #
        ##############################
        
        self.path = path
        self.path_output = path_output
        self.li_models_couplage = ['AROME', 'ARPEGE']
        self.rho = 1
        
        # On vérifie que user_params et bien un dictionnaire, on détecte s'il s'agit d'un rejeu ou non
        self.rejeu, self.user_params = self.check_user_params(user_params)
        
        # On vérifie que le type de forçage est soit MODEL soit OBS :
        self.type_forcage = self.check_type_forcage(type_forcage)
        
        # On vérifie que le modèle de couplage est bien dans la liste des
        # modèle acceptés li_models_couplage :
        self.model_couplage = self.check_model_couplage(model_couplage)
        
        # Cette variable contiendra l'index AIDA du modèle de couplage si le 
        # forçage se fait par les modèles, l'idex AIDA des obs "Tf" sinon
        self.model_couplage_aida = self.create_model_couplage_aida()
        
        # On vérifie/détermine la date du run qui va tourner
        self.date_run = self.create_datetime_run(date_run)
        
        # Petite vérification que le modèle n'ait pas déjà tourné sur ce run
        self.check_run_already_exists()
        
        # On récupère le fichier de couplage puis on stocke son contenu
        # dans un dataset (netCDF)
        file = self.get_initialize_file(model_couplage, self.date_run)
        self.coupl_data = nc.Dataset(file)
        
        ##########################
        # ETAPES DE MODELISATION #
        ##########################
        
        # 1) Paramétrisation des namelists
        self._parametrize()
        
        # 2) Couplage avec le modèle
        self._couplage()
        
        # 3) Intégration
        self._run()
        
        # 4) Diagnostique
        self._diag()
        
        # 5) Transformation puis transmission des fichiers vers path_output
        self._concat_rename()
        
        # 6) Suppression des fichiers indésirables, nettoyage du dossier path
        self._clean()
        
        
    def _parametrize(self):
        """
        Entrée: 
            - self
        Sortie:
            - None 
            
        Paramétrisation de MESO-NH, après cette étape les namelist se trouvent 
        à la racine et non plus dans le dossier bases_nam. Les paramètres 
        variables ont été modifiées en fonction de la date, des paramètres 
        choisis par l'utilisateur, etc...
        
        Le forçage par les données d'observation se fait aussi ici.
        """
        
        # Paramétrisation de la namelist PRE_IDEA1
        with open(path + 'bases_nam/PRE_IDEA1.nam', 'r') as f:
            namelist = f.read()
        
        try:
            import epygram
            epygram.init_env()
            date_epygram = self.date_run.strftime('%Y%m%d')
            yyyymm_epy = self.date_run.strftime('%Y%m')
            f = epygram.formats.resource('/cnrm/ktrm/manip/METEOPOLEX/AROME/Toulouse/' + yyyymm_epy + '/historic.surfex.tlse-1300m000+0000:00_'+date_epygram+'.fa', 'r')
#            f = epygram.formats.resource('/cnrm/phynh/data1/rodierq/LEO/' + yyyymm_epy + '/historic.surfex.tlse-1300m000+0000:00_'+date_epygram+'.fa', 'r')
            variables = ['X001WG1', 'X001WG2', 'X001WG3', 'X001WGI1', 'X001WGI2']
            Dvar={}
            for var in variables:
                Dvar[var] = f.readfield(var).getvalue_ll(1.3744755, 43.5728090)
            WG1 = Dvar['X001WG1']
            WG2 = Dvar['X001WG2']
            WG3 = Dvar['X001WG3']
            f.close() 
            print('Les paramètres du sol issus du modèle ont pu être utilisés, chouette !')
        except:
            print('Utilisation des paramètres du sol par défaut')
            WG1 = self.trunc(self.coupl_data['q'][0][-1])
            WG2 = 2.5562e-01
            WG3 = WG2
            
        if self.type_forcage == 'OBS':
            CSEA = "'FLUX'"
            CNATURE = "'NONE'"
            XUNIF_COVERS = "XUNIF_COVER(1)=1"
            XUNIF_SEA = 1.
            XUNIF_NATURE = 0.
        else:
            CNATURE = "'ISBA'"
            CSEA = "'NONE'"
            XUNIF_COVERS = "XUNIF_COVER(361)=0.5, XUNIF_COVER(456)=0.5"
            XUNIF_SEA = 0.
            XUNIF_NATURE = 1.
            
        li_params_pre_idea1 = {
                "CSEA" : CSEA,
                "CNATURE" : CNATURE,
                "XUNIF_COVERS" : XUNIF_COVERS,
                "XUNIF_SEA": XUNIF_SEA,
                "XUNIF_NATURE": XUNIF_NATURE,
                "NYEAR" : self.date_run.strftime("%Y"),
                "NMONTH" : self.date_run.strftime("%m"),
                "NDAY" : self.date_run.strftime("%d"),
                "XTIME" : float(self.date_run.strftime("%H")) * 3600.,
                "XHUG_SURF" : WG1,
                "XHUG_ROOT" : WG2,
                "XHUG_DEEP": WG3,
                "XTG_SURF" : self.trunc(self.coupl_data['t'][0][-1]),
                "XTG_ROOT" : self.trunc(self.coupl_data['t_soil'][0][0]),
                "XTG_DEEP": self.trunc(self.coupl_data['t_soil'][0][0]),
                "NYEAR2" : self.date_run.strftime("%Y"),
                "NMONTH2" : self.date_run.strftime("%m"),
                "NDAY2" : self.date_run.strftime("%d"),
                "XTIME2" : float(self.date_run.strftime("%H")) * 3600.
                }
        
        for param in li_params_pre_idea1:
            namelist = namelist.replace("{" + param + "}", str(li_params_pre_idea1[param]))
                
        with open(self.path + 'PRE_IDEA1.nam', 'w') as f:
            f.write(namelist)
        
        # Paramétrisation de la namelist EXSEG1
        namelist = ""
        
        if self.rejeu:
            exsegfile = "USER"
        else:
            exsegfile = "OPER"
        
        with open(path + 'bases_nam/EXSEG1_' + exsegfile + '.nam', 'r') as f:
            namelist += f.read()
         
        NAM_PARAMn = ""
        for param in self.user_params:
            if param != 'id' and self.user_params[param] != None:
                NAM_PARAMn += param + "=" + self.format2namelist(self.user_params[param]) + ", "
                
        NAM_PARAMn = NAM_PARAMn[:-2]
        namelist = namelist.replace("{NAM_PARAMn}", NAM_PARAMn)
        
        if self.type_forcage == "OBS":
            namelist += self.create_NAM_IDEAL_FLUX()
            namelist += "\n"
            
        with open(self.path + 'EXSEG1.nam', 'w') as f:
            f.write(namelist)
    
    
    def _couplage(self):
        """
        Entrée: 
            - self
        Sortie:
            - None 
            
        Couplage de MesoNH avec les données d'un modèle atmosphérique (AROME ou 
        ARPEGE) dans PRE_IDEA1.
        """
        
        data = self.coupl_data
        
        RSOU_part = self.create_RSOU(data)
        ZFRC_part = self.create_ZFRC(data)
        
        namelist = ""
        with open(self.path + 'PRE_IDEA1.nam', 'r') as f:
            namelist += f.read()

        namelist += RSOU_part
        namelist += ZFRC_part
        namelist += "\n"
        
        print(namelist)
        
        with open(self.path + 'PRE_IDEA1.nam', 'w') as f:
            f.write(namelist)
        
        
    def _run(self):
        """
        Entrée: 
            - self
        Sortie:
            - None 
            
        Intégration du modèle, appel d'un bash dédié.
        """
        
        call('cp ' + path + 'run ' + self.path + 'run', shell='True')
        call('cd ' + self.path + ' ; run', shell='True')
        
    def _diag(self):
        """
        Entrée: 
            - self
        Sortie:
            - None 
            
        Etape de diagnostique puis concaténation dans le fichier de backup pour
        chaque échéance.
        """
        call('cp ' + path + 'diag ' + self.path + 'diag', shell='True')
        
        for YINIFILE in glob.glob(self.path + 'REF*.nc'):
            if '000.nc' not in YINIFILE:
                namelist = ''
                with open(path + 'bases_nam/DIAG1.nam', 'r') as f:
                    namelist += f.read()
                 
                namelist = namelist.replace("{YINIFILE}", '"' + os.path.basename(YINIFILE)[:-3] + '"')
                    
                with open(self.path + 'DIAG1.nam', 'w') as f:
                    f.write(namelist)
                    
                call('cd ' + self.path + ' ; diag', shell='True')
                call('ncks -A -v HBLTOP ' + YINIFILE[:-3] + '_DIAG.nc ' + YINIFILE, shell='True')

        
        
        
    def _concat_rename(self):
        """
        Entrée: 
            - self
        Sortie:
            - None 
            
       Vérification de la simulation, déplacement/concaténation des fichiers
       d'intérêt dans le dossier de sortie.
       """
        
        f = nc.Dataset(self.path + 'REF01.1.SEG01.000.nc')
        if f.getncattr('MNH_cleanly_closed') == 'yes':
            if 'id' in self.user_params:
                id_run = '_' + self.user_params['id']
            else:
                id_run = ''
            output_file = self.path_output + 'MESONH_' + self.model_couplage_aida + '_' + self.date_run.strftime('%Y%m%d%H') + id_run
            call('ncrcat -O ' + self.path + 'REF01.1.SEG01.*[1-9].nc ' + output_file + '.nc', shell='True')
            call('mv ' + self.path + 'REF01.1.SEG01.000.nc ' + output_file + '.000.nc', shell='True')
            call('cp ' + self.path + 'PRE_IDEA1.nam ' + output_file + '_PRE_IDEA1.nam', shell='True')
            call('cp ' + self.path + 'EXSEG1.nam ' + output_file + '_EXSEG1.nam', shell='True')
            call('cp ' + self.path + 'OUTPUT_LISTING1 ' + output_file + '_OUTPUT_LISTING1', shell='True')
        else:
            raise SystemError('La simulation a planté, les fichiers ne seront pas transmis')
    
    
    def _clean(self):
        """
        Entrée: 
            - self
        Sortie:
            - None 
            
           Suppression du dossier de simulation
        """
        
#        call('rm -rf ' + self.path, shell='True')
    
    
    def get_initialize_file(self, model_couplage, date_run):
        """
        Entrée: 
            - self
            - str model_couplage : le modèle de couplage utilisé
            - str date_run : la date du run pour cette simulation
        Sortie:
            - str file : le chemin absolu vers le fichier .nc contenant le résultat
            de la simulation du modèle de couplage
            
           Cette fonction permet de déterminer le chemin absolu vers le fichier
           du modèle de couplage.
        """
        
        if model_couplage == "AROME":
            date_run_arome = date_run.strftime('%Y%m%d')
            print("RUN AROME COUPLAGE : ", date_run_arome)
            yyyymm_aro = date_run.strftime('%Y%m')
            file = '/cnrm/ktrm/manip/METEOPOLEX/AROME/Toulouse/' + yyyymm_aro + '/netcdf_tlse.tar.arome_'+date_run_arome+'.netcdf'
#            file = '/cnrm/phynh/data1/rodierq/LEO/' + yyyymm_aro + '/netcdf_tlse.tar.arome_'+date_run_arome+'.netcdf'
        elif model_couplage == "ARPEGE":
            yearmonth = date_run.strftime('%Y%m')
            date_run_arpege = date_run.strftime('%Y%m%d%H')
            file = '/cnrm/proc/bazile/NetCdf/Toulouse/' + yearmonth + '/Arpege-oper-L105_Toulouse_' + date_run_arpege + '.nc'
        
        return file
        
    
    def create_datetime_run(self, date_run):
        """
        Entrée: 
            - self
            - str date_run : la date du run pour cette simulation, entrée par 
            l'utilisateur. Cette date peut prendre la valeur 'latest' ou un
            isoformat.
        Sortie:
            - datetime date : la date du run, au format datetime, pour cette simulation.
            
           Cette fonction permet de déterminer/formater la date passée en
           argument par l'utilisateur. Après cette étape, il s'agit d'utiliser
           non plus la variable date_run mais la variable self.date_run, bien
           formatée, à la place.
        """
        
        if(date_run == 'latest'):
            now = datetime.now()
            if self.type_forcage == "OBS":
                now = now - timedelta(days=2)
            new_date = now.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
            while(not os.path.exists(self.get_initialize_file(self.model_couplage, new_date))):
                new_date = new_date - timedelta(days = 1)
            print('Date de run utilisée : ' + str(new_date))
            date = new_date
        else:
            date = datetime.fromisoformat(date_run)
        return date
    
    
    def check_model_couplage(self, model_couplage):
        """
        Entrée: 
            - self
            - str model_couplage : le modèle de couplage utilisé
        Sortie:
            - str model_couplage : le modèle de couplage utilisé, après 
            vérification
            
           Petite fonction de sécurité, permettant de savoir si l'utilisateur 
           a choisi un modèle de couplage qui existe. Après cette étape, il 
           convient de ne plus utiliser la variable model_couplage, mais 
           self.model_couplage à la place.
        """
        
        if model_couplage not in self.li_models_couplage:
            raise ValueError('Le modèle de couplage choisi n\'est pas pris en charge')
        else:
            return model_couplage
        
    def check_type_forcage(self, type_forcage):
        """
        Entrée: 
            - self
            - str type_forcage : le type de forçage utilisé
        Sortie:
            - str type_forcage : le type de forçage utilisé, après 
            vérification
            
           Fonction de sécurité à nouveau, permettant de savoir si l'utilisateur 
           a choisi un type de forçage qui existe. Après cette étape, il 
           convient de ne plus utiliser la variable type_forcage, mais 
           self.type_forcage à la place.
        """
        
        if type_forcage != 'MODEL' and type_forcage != 'OBS':
            raise ValueError('Le type de forçage choisi n\'est pas pris en charge')
        else:
            return type_forcage
        
    def check_user_params(self, user_params):
        """
        Entrée: 
            - self
            - dict user_params : les paramètres entrés par l'utilisateur
        Sortie:
            - bool rejeu : indique s'il s'agit d'un rejeu ou non
            - dict user_params : les paramètres entrés par l'utilisateur, après 
            vérification
            
           Fonction permettant de vérifier si les paramètres entrés par 
           l'utilisateur sont au bon format s'il y en a, de déterminer s'il 
           s'agit d'un run de rejeu ou non et de modifier les chemins en 
           conséquence : création notamment d'un dossier de travail spécifique 
           à la simulation dans tous les cas.
        """
        
        if isinstance(user_params, dict):
            self.path += "simulation_"
            if 'id' in user_params:
                rejeu = True
                dos = 'USER/'
                self.path += user_params['id'] + '/'
            else:
                rejeu = False
                dos = 'OPER/'
                self.path += shortuuid.uuid()[:8] + '/'
            os.mkdir(self.path)
            self.path_output += dos
            return rejeu, user_params
        else:
            raise ValueError('Les paramètres doivent être fournis sous forme d\'un dictionnaire {clé: valeur}')
        
        
    def create_model_couplage_aida(self):
        """
        Entrée: 
            - self
        Sortie:
            - str name_aida : identifiant AIDA relatif au modèle utilisé.
            
           Petite fonction pour simplifier la vie du développeur front-end, qui
           travaille principalement avec l'outil AIDA. Ces identifiants seront 
           utilisés pour nommer les fichiers de sortie et ainsi facilement
           s'y retrouver entre les différents fichiers.
        """
        
        if self.type_forcage == 'OBS':
            name_aida = "Tf"
        elif self.model_couplage == "AROME":
            name_aida = "Rt"
        elif self.model_couplage == "ARPEGE":
            name_aida = "Gt"
        return name_aida
        
    
    def check_run_already_exists(self):
        """
        Entrée: 
            - self
        Sortie:
            - None
            
           Cette fonction lève une erreur si le modèle a déjà tourné dans la 
           même configuration pour cette échéance. Si aucun modèle n'a tourné 
           pour l'échéance, on crée le dossier relatif à la date du run.
        """
        
        date_format_dos = self.date_run.strftime('%Y%m%d%H')
        self.path_output += date_format_dos + '/'
        output_file = self.path_output + 'MESONH_' + self.model_couplage_aida + '_' + date_format_dos + '.nc'
        if os.path.exists(output_file):
            raise FileExistsError('Le modèle a déjà tourné pour cette échéance')
        else : 
            if not os.path.exists(self.path_output):
                os.mkdir(self.path_output)
        
        
    def create_RSOU(self, data):
        """
        Entrée: 
            - self
            - netCDF4._netCDF4.Dataset data : correspond exactement à 
            self.coupl_data. Variable renommée ainsi car fréquemment utilisée 
            dans cette fonction, un nom de variable plus court est donc 
            confortable. Contient donc les données issues du modèle de couplage.
        Sortie:
            - str txt : contenu de la partie nommée "Radiosounding case", qui 
            sera inséré à la fin (free-format part) de la namelist 
            PRE_IDEA1.nam .
            
           Cette fonction formate les données d'initialisation (à t=0) du 
           modèle de couplage pour qu'elles soient lisibles par MESONH au 
           travers de la namelist PRE_IDEA1.nam .
        """
        
        #__ Type de condition initiale: RSOU __#
        txt = "RSOU\n"
        
        #__ Date du RSOU__#
        year = self.date_run.strftime('%Y')
        month = str(int(self.date_run.strftime('%m')))
        day = self.date_run.strftime('%d')
        hour_in_seconds = str(float(self.date_run.strftime('%H')) * 3600)
        txt += year + " " + month + " " + day + " " + hour_in_seconds + '\n'
        
        #__ Type de RSOU __#
        txt += "\'ZUVTHVMR\'\n"
        
        #__ Extraction des valeurs au sol ([-1]) __#
        txt += "0. \n" # Height of ground level
        txt += str(data['pressure_f'][0][-1]) + "\n" # Pressure at ground level
        txt += str(data['thv'][0][-1]) + "\n" # Virtual potential temperature at ground level
        txt += str(data['qv'][0][-1]) + "\n" # Vapor mixing ratio at ground level
        
        #__ Extraction des variables vent __#
        nb_wind_levels = data['nlev'].size
        txt += str(nb_wind_levels - 1) + "\n" # Number of wind levels
        for i in range(2, nb_wind_levels + 1):
            txt += self.trunc(data['height_h'][0][-i]) + " "
            txt += self.trunc(data['u'][0][-i]) + " "
            txt += self.trunc(data['v'][0][-i]) + "\n"
         
        #__ Extraction des variables mass __#
        nb_mass_levels = data['nlevp1'].size
        txt += str(nb_mass_levels - 1) + "\n" # Number of mass levels
        for i in range(2, nb_mass_levels):
            txt += self.trunc(data['height_h'][0][-i]) + " "
            txt += self.trunc(data['thv'][0][-i]) + " "
            txt += self.trunc(data['qv'][0][-i]) + "\n"
        
        return txt
    
    def create_ZFRC(self, data):
        """
        Entrée: 
            - self
            - netCDF4._netCDF4.Dataset data : correspond exactement à 
            self.coupl_data. Variable renommée ainsi car fréquemment utilisée 
            dans cette fonction, un nom de variable plus court est donc 
            confortable. Contient donc les données issues du modèle de couplage.
        Sortie:
            - str txt : contenu de la partie nommée "The forced version", qui 
            sera inséré à la fin (free-format part) de la namelist 
            PRE_IDEA1.nam .
            
           Cette fonction formate les données de forcage/advection du 
           modèle de couplage pour qu'elles soient lisibles par MESONH au 
           travers de la namelist PRE_IDEA1.nam .
        """
        
        #__ Type de forçage: ZFRC __#
        txt = "ZFRC\n"
        
        #__ Echeance max dépendante au forcing __#
        nb_echeances = data['time'].size
        txt += str(nb_echeances - 1) + "\n"
        
        #__ Nombre de niveau (hors boucle pour éviter trop appels) __#
        nb_levels = data['nlev'].size
        
        #__ Extraction, pour chaque échéance, du forçage __#
        for e in range(nb_echeances):
            #__ Echeance du forçage__#
            datetime_forcage = self.date_run + timedelta(seconds=int(data['time'][e]))
            year = datetime_forcage.strftime('%Y')
            month = str(int(datetime_forcage.strftime('%m')))
            day = datetime_forcage.strftime('%d')
            hour_in_seconds = str(float(datetime_forcage.strftime('%H')) * 3600)
            txt += year + " " + month + " " + day + " " + hour_in_seconds + '\n'
            
            #__ Extraction des valeurs au sol ([-1]) __#
            txt += "0. \n" # Height of ground level
            txt += str(data['pressure_f'][e][-1]) + "\n" # Pressure at ground level
            txt += str(data['thv'][e][-1]) + "\n" # Virtual potential temperature at ground level
            txt += str(data['qv'][e][-1]) + "\n" # Vapor mixing ratio at ground level
            
            #__ Nombre de niveaux à afficher __#
            txt += str(nb_levels - 1) + "\n"
            
            #__ Extraction des variables de forçage pour l'échéance e __#
            for i in range(2, nb_levels + 1):
                txt += self.trunc(data['height_h'][e][-i]) + " "
                txt += self.trunc(data['u'][e][-i]) + " "
                txt += self.trunc(data['v'][e][-i]) + " "
                txt += self.trunc(data['thv'][e][-i]) + " " 
                txt += self.trunc(data['qv'][e][-i]) + " "
                txt += self.trunc(self.toPres(data['omega'][e][-i], e, i)) + " "
                txt += self.trunc(data['tadv'][e][-i]) + " "
                txt += self.trunc(data['qadv'][e][-i]) + " "
                txt += self.trunc(data['uadv'][e][-i]) + " "
                txt += self.trunc(data['vadv'][e][-i]) + " "
                txt += "\n"
        
        
        return txt
    
    def create_NAM_IDEAL_FLUX(self):
        """
        Entrée: 
            - self
        Sortie:
            - str txt : contenu de la namelist nommée "NAM_IDEAL_FLUX", qui 
            sera inséré à la fin du fichier EXSEG1.nam .
            
           Cette fonction formate les données de forçage au sol issues des 
           observations receuillies avec l'outil AIDA, pour qu'elles soient 
           lisibles par MESONH au travers de la namelist EXSEG1.nam .
        """
        
        ech_max = 96
        txt = "&NAM_IDEAL_FLUX NFORCF=" + str(ech_max) + ",\n"
        
        doy1 = (self.date_run + timedelta(days=0)).strftime('%j')
        doy2 = (self.date_run + timedelta(days=1)).strftime('%j')
        year = self.date_run.strftime('%Y')
        
        dico_ids_aida = {
                "flx_hs_tson_Chb_%1800" : "SFTH",
                "LE" : "SFTQ",
                "CO2" : "SFCO2",
                "USTAR" : "USTAR"
                }
        
        
        values, times, header = read_aida.donnees(doy1, doy2, year, "flx_hs_tson_Chb_%1800", "Tf")
    
            
        for i, time in enumerate(times[:ech_max]):
            time = float((time - self.date_run).days) * 86400 + float((time - self.date_run).seconds) - 1800
            txt += "XTIMEF(" + str(i+1) + ")=" + str(time) + ",\n"
            
        for id_aida in dico_ids_aida:
            if id_aida == "CO2" :
                values = np.zeros(ech_max)
            elif id_aida == "USTAR" :
                values, times, header = read_aida.donnees(doy1, doy2, year, "flx_mvt_Chb_%1800", "Tf")
                values = np.sqrt(values/self.rho)
            elif id_aida == "LE":
                vec_le, times, header = read_aida.donnees(doy1, doy2, year, "flx_le_Chb_%1800", "Tf")
                vec_hs, times, header = read_aida.donnees(doy1, doy2, year, "flx_le_Chb_%1800", "Tf")
                
                print(vec_le)
                
                nb_val_manquantes = len(vec_le.mask.nonzero()[0])
                pourc_manquant = nb_val_manquantes/len(vec_le) * 100
                
                if pourc_manquant > 25 or self.following_miss_val(vec_le):
                    raise ValueError('Trop d\'obs manquantes, le run ne sera pas lancé')
                
                values = self.interp_vec_le(vec_le, vec_hs, times)
            else :
                values, times, header = read_aida.donnees(doy1, doy2, year, id_aida, "Tf")
                
            for i, value in enumerate(values[:ech_max]):
                txt += "X" + dico_ids_aida[id_aida] + "(" + str(i+1) + ")=" + str(value) + ",\n"
                
        txt += "CSFTQ='W/m2',\n"
        txt += "CUSTARTYPE='USTAR'\n"
        txt += "/"
        
        
        return txt
    
    #####################
    #   FONCTIONS TIERS #
    #####################
    
    def trunc(self, char):
        """
        Entrée: 
            - self
            - type(char) char : un caractère à formater.
        Sortie:
            - str char : le caractère formaté.
            
           Cette fonction était initialement utilisée pour formater la taille
           des données renvoyées dans les namelists. La taille important 
           finalement peu, l'utilité de cette fonction parait discutable...
        """
        
        return str(char)
    
    
    def format2namelist(self, param):
        """
        Entrée: 
            - self
            - type(param) param : un paramètre de namelist à formater.
        Sortie:
            - type(param) param : le paramètre formaté.
            
           Fonction de formatage des données avant envoi dans la namelist. Par
           exemple, si le paramètre CCLOUD a la valeur ICE3, cette fonction 
           ajoutera des guillements simple ( 'ICE3' ) pour que la donnée écrite
           en namelist soit finalement : 
           ...
               "CCLOUD" : 'ICE3',
           ...
           On s'affranchit en quelque sorte des problèmes de guillemets.
           Il serait sans doute intéressant de combiner les fonction trunc et
           format2namelist pour en avoir une seule "qui fait tout".
        """
        
        if isinstance(param, str) and param[0] != "'":
            param = "'" + param + "'"
        return param
            
    
    def toPres(self, omega, e, i):
        """
        Entrée: 
            - self
            - flat omega : vitesse en Pa/s
            - int e : indice de l'échéance
            - int i : indice du niveau vertical.
        Sortie:
            - float omega : vitesse en m/s.
            
           Convertit la vitesse verticale de Pa/s vers m/s.
        """
        rho = self.coupl_data['pressure_f'][e][-i]/ (288 * self.coupl_data['t'][e][-i])
        return omega / (-9.81 * rho)
    
    def interp_vec_le(self, vec_le, vec_hs, time):
        """
        Entrée: 
            - self
            - array vec_le : tableau contenant les valeurs de flux de LE
            - array vec_hs : tableau contenant les valeurs de flux de H
            - array time : tableau contenant les dates associées aux tableaux
            précédents.
        Sortie:
            - array vec_le : tableau contenant les valeurs de flux de LE 
            interpolées.
            
           Fonction d'interpolation du vecteur contenant les flux de chaleur 
           latente.
        """
        if len(vec_le.mask.nonzero()[0]) > 0:
            for i in range(len(vec_le)):         
                if not 6 < int(time[i].strftime('%H')) < 22:
                    if type(vec_le[-i]) is not np.float32:
                        vec_le[-i] = 0
                    
                if vec_hs[i] <= 0 and type(vec_le[i]) is not np.float32:
                    vec_le[i] = 0
            
            x = vec_le.mask.nonzero()[0]
            xp = (~vec_le.mask).nonzero()[0]
            fp = vec_le[~np.isnan(vec_le)].data
            
            vec_le[np.isnan(vec_le)] = np.interp(x, xp, fp)
        return vec_le
    
    def following_miss_val(self, vec):
        """
        Entrée: 
            - self
            - array vec: un tableau 1D.
        Sortie:
            - bool following_miss_val: un booleen valant True si il y a plus
            de 6 valeurs manquantes dans le vecteur vec.
            
           Fonction permettant de déterminer s'il y a plus de 6 valeurs 
           manquantes dans le vecteur vec. Elle est utilisée pour checker si 
           le vecteur contenant les valeurs de flux de chaleur latente est
           utilisable ou non.
        """
        i=0
        for val in vec:
            if type(val) is not np.float32:
                i += 1
            else:
                i = 0
                
            if i > 6:
                return True
        return False
    
#######################
# LANCEMENT MULTI RUN #
#######################
        
def three_months():
#DATE DE DEPART DU RUN
    date_depart = datetime.fromisoformat('2022-02-01T00:00:00')

#NOMBRE DE JOURS A PARTIR DE LA DATE DE DEPART ????
    for i in range(15):

        date_run = date_depart + timedelta(days=i)
#        for model in ['AROME', 'ARPEGE']:
        for model in ['AROME']:
            try:
                MesoNH(date_run=str(date_run), model_couplage=model)
            except:
                print('Le modèle du ' + str(date_run) + ' ' + model + ' n\' a pas pu être lancé')
        try:
            MesoNH(date_run=str(date_run), type_forcage='OBS')
        except:
            print('Le modèle du ' + str(date_run) + ' OBS n\' a pas pu être lancé')
        
"""
    Sécurité/Améliorations à apporter:
        - 
        -
"""
