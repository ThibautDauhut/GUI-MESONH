#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 14:03:21 2021

@author: avrillauds
"""


import os
import sys

#AH = os.getenv('AIDA_HOME', '/d0/AIDA/aida')
AH = os.getenv('AIDA_HOME', '/home/common/aida')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))
import AIDA
# definition acquid acquid=identifiant de la journee pou lecture donnée sous forme vecteur


def donnees(doy1, doy2, annee, parametre, plateforme):

    if len(doy2) == 3:
        acqid_fin = annee[-2:] + '0' + doy2
    elif len(doy2) == 2:
        acqid_fin = annee[-2:] + '00' + doy2
    else:
        acqid_fin = annee[-2:] + '000' + doy2
    if len(doy1) == 3:
        acqid_debut = annee[-2:] + '0' + doy1
    elif len(doy1) == 2:
        acqid_debut = annee[-2:] + '00' + doy1
    else:
        acqid_debut = annee[-2:] + '000' + doy1

    # AIDA.read_datas fonction de lecture du module AIDA pour lire les données

    values, time, header = AIDA.read_datas(
        plateforme + acqid_debut, parametre, plateforme + acqid_fin)
    return [values, time, header]
