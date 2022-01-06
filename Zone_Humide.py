# -*- coding: UTF-8 -*-
"""
Author : Julien Pellen

"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal
import seaborn as sns
from math import ceil
from PIL import Image
import re



# ======================= Fonction ================================


def LoadImgInd (PathFile):
    try:
        ds = gdal.Open(PathFile).ReadAsArray()
        npa = np.array(ds)
        return npa
    except FileNotFoundError:
        print('Problème dans le chemin d\'accès')
        sys.exit(1)

def ImgHeight(DSM, DTM):
    try:
        p = DSM-DTM
        return p
    except ValueError:
        print('Problème de dimension du raster')
        sys.exit(1)

def ReclassLidarVeg(matrice):
    """
    Premier palier = Lowherbaceous stratum : <0.30m
    Deuxième palier = Medium herbaceous stratum : >0.30m et < 0.9m
    Troisième palier = High herbaceous stratum : > 0.9 et < 1.8 m
    Quatrième palier = Bush stratum : > 1.8m et <6m
    Cinquième palier = Tree stratum : > 6m

    :param matrice: 
    :return: Une classification selon les différents paliers
    """
    try:
        LH = np.where(matrice < 0.30, 1, 0)
        MH = np.where(matrice < 0.9, 2, 0)
        BonMH =MH - LH
        HH = np.where(matrice < 1.8, 3, 0)
        BonHH = HH - BonMH
        BS = np.where(matrice < 6, 4, 0)
        BonBS = BS - BonHH
        TS = np.where(matrice > 6, 5, 0)
        BonTS = (BonBS - TS)
        BonTS = np.where(BonTS==(-5), 5, BonTS)

        return BonTS

    except FileNotFoundError:
        print('Problème dans le chemin d\'accès de la matrice')
        sys.exit(1)

    except ValueError:
        print('Problème dans l\'attribution de Valeurs')
        sys.exit(1)

def MaskShapeFile(PathRaster, PathShapelfile):
    try:
        ds = gdal.Open(PathRaster).ReadAsArray()
        nds = np.array(ds)
            

        print('En cours de dvlp')
    except ValueError:
        print('CHEH')
        pass

def Resample(NameFile, Xres, Yres , algo):
    """

    :param NameFile: Le chemin d'accès vers l'image à rééchantillonné
    :param Xres: La largeur voulu qui sera donné à un pixel
    :param Yres: La longueur  voulu qui sera donné à un pixel
    :param algo: Le type de rééchenatillonage
    par défaut sur le plus proche voisin
    :return:
    """
    try:
        ds = gdal.Open(NameFile)
        option = gdal.WarpOptions(xRes=Xres, yRes=Yres, resampleAlg=algo)
        ds_resample = gdal.Warp(NameFile[:-4]+"_Resample.tif", ds, options=option)

    except NotADirectoryError:
        print("Le chemin d'accès vers l'image n'est pas conforme, \n par exemple sous Linux : '/home/user/Bureau/Image.tif'")
        sys.exit(1)



if __name__ == '__main__':

    # Création du DHM
    DSM = LoadImgInd('/home/ju/Bureau/M2/Traitement_image_Zone_Humide/TD-ZH/LiDARidrisi/LiDAR_dsm.rst')
    DTM = LoadImgInd('/home/ju/Bureau/M2/Traitement_image_Zone_Humide/TD-ZH/LiDARidrisi/LiDAR_dtm.rst')
    DHM = ImgHeight(DSM, DTM)
    # Classification selon la hauteur de la végétation des données LiDAR
    Re = ReclassLidarVeg(DHM)










