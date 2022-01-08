# -*- coding: UTF-8 -*-
"""
Author : Julien Pellen

"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal, ogr, osr
import seaborn as sns
from math import ceil
from PIL import Image
import re


# ======================= Fonction ================================


def LoadImgInd (PathFile):
    try:
        ds = gdal.Open(PathFile)
        #print(ds.GetGeoTransform(),'\n', ds.GetProjection())
        ds = ds.ReadAsArray()
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

        
def VtoR (PathShp, Output, Newkey, TypeImg = 'GTiff', CRS = 2154, Resolution = 0.5):
    """
    :param PathShp: Chemin d'accès absolue du fichier vecteur à convertir en raster (type = str)
    :param Output: Chemin d'accès d'enregistrement du fichier raster (type = str)
    :param Newkey: Nom du fichier qui doit créer (type = str)
    :param TypeImg: Format d'image en sorti, sert à choisir le driver pour construire le raster (type = str)
    :param CRS: Le système de projection voulu (type = int)
    :param Resolution: La résolution spatiale attendue du raster en sorti (type = float)
    :return:
    """
    try:
        # Chargement de l'objet vecteur
        Input_Shp = ogr.Open(PathShp)
        InputShp = Input_Shp.GetLayer()
        # Chargement de la resolution voulu, par défaut 50cm
        pixel_size = Resolution
        # Obtenir l'emprise spatiale de la couche vecteur
        x_min, x_max, y_min, y_max = InputShp.GetExtent()
        # Calcule de la dimension du raster
        x_res = int((x_max - x_min) / pixel_size)
        y_res = int((y_max - y_min) / pixel_size)
        # Chargement du driver pour créer le fichier raster
        driver = gdal.GetDriverByName(TypeImg)
        # Création du Raster, et paramétrage des attributs du raster
        new_raster = driver.Create(Output+Newkey, x_res, y_res, 1, gdal.GDT_Byte)
        new_raster.SetGeoTransform((x_min, pixel_size, 0, y_min, 0, pixel_size))
        band = new_raster.GetRasterBand(1)
        # Gestion des Nodatas
        no_data_value = -9999
        band.SetNoDataValue(no_data_value)
        band.FlushCache()
        # On 'remplit' le raster vide créer précédémment avec les données shp, qui cooresponde à une emprise spatiale
        gdal.RasterizeLayer(new_raster, [1], InputShp, burn_values=[255])
        # Gestion du système de projection du raster
        new_rasterSRS = osr.SpatialReference()
        new_rasterSRS.ImportFromEPSG(CRS)
        new_raster.SetProjection(new_rasterSRS.ExportToWkt())

    except ValueError:
        print('CHEH')
        sys.exit(1)

        
def WriteRas (Matrice,OUTPUT, Newkey, PathRasRef ):
    try:
        ds = gdal.Open(PathRasRef)
        driver = gdal.GetDriverByName('GTiff')
        p = driver.Create(OUTPUT + Newkey, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32)
        p.SetGeoTransform(ds.GetGeoTransform())
        p.SetProjection(ds.GetProjection())
        p.GetRasterBand(1).WriteArray(Matrice)
        p.FlushCache()
    except ValueError:
        print("Problème de projection")

        
def Reproj (NameFile,ProjVoulu):
    try:
        ds =gdal.Open(NameFile)
        option = gdal.WarpOptions(dstSRS=ProjVoulu)
        ds_reproj = gdal.Warp(NameFile[:-4]+"_Reproj.tif", ds, options=option)
    except ValueError:
        print("CHEH")
        pass

    
def Crop(PathImg, Zone, ReturnArray= True):
    try:

        xMin, xMax, yMin, yMax = Zone
        ds = gdal.Open(PathImg)
        ds_gt = ds.GetGeoTransform()

        row1 = int((yMax - ds_gt[3]) / ds_gt[5])
 
        col1 = int((xMin - ds_gt[0]) / ds_gt[1])

        row2 = int((yMin - ds_gt[3]) / ds_gt[5])

        col2 = int((xMax - ds_gt[0]) / ds_gt[1])
        nArray = ds.ReadAsArray(abs(col1), abs(row1), abs(col2 - col1 + 1), abs(row2 - row1 + 1))
        nArray2 = np.array(nArray).astype(np.float32)


        if ReturnArray is True:
            return nArray2

        else:
            driver = gdal.GetDriverByName('GTiff')
            Output = str(input('Mettre le chemin d\'accès vers le dossier d\'enregistrement : '))
            Namefile = str(input('Rentrer le nom du fichier : '))
            p = driver.Create(Output + Namefile, nArray2.shape[1],nArray2.shape[0], 1,gdal.GDT_Float32)
            p.SetGeoTransform([xMin, ds_gt[1], ds_gt[2], yMax, ds_gt[4], ds_gt[5]])
            p.SetProjection(ds.GetProjection())
            p.GetRasterBand(1).WriteArray(nArray)
            p.FlushCache()

    except KeyError:
        print('Don\'t Panic')
        pass

def CROPMASK(PathImg, Zone, ReturnArray=True): # Ne Marche Pas

    try :

        xMin, xMax, yMin, yMax = Zone
        ds = gdal.Open(PathImg)
        ds_gt = ds.GetGeoTransform()
        print(ds_gt)
        row1 = int((yMax - ds_gt[3]) / ds_gt[5])
        print('ROW1 :', row1)
        col1 = int((xMin - ds_gt[0]) / ds_gt[1])
        print('COL1 :', col1)
        row2 = int((yMin - ds_gt[3]) / ds_gt[5])
        print('ROW2 :', row2)
        col2 = int((xMax - ds_gt[0]) / ds_gt[1])
        print('COL2 :', col2)
        print('C\'est lopération col2-col1+1 :', '\n', abs(col2 - col1 + 1))
        print('C\'est lopération row2-row1+1 :', '\n', abs(row2 - row1 + 1))
        nArray = ds.ReadAsArray(col2, row2, abs(col1-col2+1), abs(row1-row2+1))
        nArray2 = np.array(nArray).astype(np.float32)
        print(nArray2)

        if ReturnArray is True :
            return nArray2

        else :
            driver = gdal.GetDriverByName('GTiff')
            Output = str(input('Mettre le chemin d\'accès vers le dossier d\'enregistrement : '))
            Namefile = str(input('Rentrer le nom du fichier : '))
            p = driver.Create(Output + Namefile, nArray2.shape[1], nArray2.shape[0], 1, gdal.GDT_Float32)
            p.SetGeoTransform([xMin, ds_gt[1], ds_gt[2], yMax, ds_gt[4], ds_gt[5]])
            p.SetProjection(ds.GetProjection())
            p.GetRasterBand(1).WriteArray(nArray)
            p.FlushCache()

    except KeyError :
        print('Don\'t Panic')
        pass #

def Mask(PathImg1, PathImg2):
    """

    :param PathImg1: Chemin d'accès de l'image à masqué (type = str)
    :param PathImg2: Chemin d'accès de limage servant de masque (type = str)
    :return: Retourne une matrice masqué (type = np.array)
    """
    try:
        ds1 = gdal.Open(PathImg1).ReadAsArray()
        npds1 = np.array(ds1)
        ds2 = gdal.Open(PathImg2).ReadAsArray()
        npds2 = np.array(ds2)
        mask = npds1/npds2
        return mask

    except ZeroDivisionError:
        pass
    
    except ValueError:
        print('CHEH')
        pass

if __name__ == '__main__':

    # Création du DHM
    #DSM = LoadImgInd('/home/ju/Bureau/DSM_Reproj.tif')

    #Kompat2Blue  = LoadImgInd('/home/ju/Bureau/M2/Traitement_image_Zone_Humide/TD-ZH/SatelliteIdrisi/kompsat_b1.rst')
    #DTM = LoadImgInd('/home/ju/Bureau/DTM_Reproj.tif')
    #DHM = ImgHeight(DSM, DTM)
    # Classification selon la hauteur de la végétation des données LiDAR
    #Re = ReclassLidarVeg(DHM)
    #WriteRas(Re,'/home/ju/Bureau/','RECLASS_LIDAR.tif', PathRasRef='/home/ju/Bureau/DSM_Reproj.tif')
    #VtoR('/home/ju/Bureau/M2/Traitement_image_Zone_Humide/TD-ZH/3-veget_zh/ancillary_data/limites_zh.shp', '/home/ju/Bureau/', 'Raster_LimiteZh.tif')
    #zone = [366267.144,367993.388, 6831503.872, 6837264.898]
    #DHM_crop= Crop('/home/ju/Bureau/RECLASS_LIDAR.tif', zone, ReturnArray=False)
    #Mask_LimiteZH = CROPMASK('/home/ju/Bureau/Raster_LimiteZh.tif', zone)

    # PARTIE SUR LE RASTER MASK (COUCHE VECTEUR => RASTER) TENTATIVE DE CROP
    Lidar = gdal.Open('/home/ju/Bureau/RECLASS2_CROP.tif').ReadAsArray()
    npLidar= np.array(Lidar[:,:-1])
    Limite = gdal.Open('/home/ju/Bureau/Raster_LimiteZh_crop.tif').ReadAsArray()
    npLimite = np.array(Limite[:-1,:])
    Mask = npLidar/npLimite
    plt.imshow(Mask)
    plt.show()

    """
    #Coordonées de Crop
    P1 = 366267.144, 6837264.898
    P1_correcte = 366285.65,6837251.21
    P2 = 367993.388,6831503.872
    P2_correct = 367993.249,6831504.041
    
    Point_origine_raster = 366267.288,6831503.917
    
    #Coordonnées TEST MASK
    
    P1 = 367102.1,6833203.0
    P2 = 369207.7,6830724.6
    
    #Divers
    P3 = 366286.241,6837250.620    
    """











