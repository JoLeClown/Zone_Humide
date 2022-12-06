# -*- coding: UTF-8 -*-
"""
Author : Julien Pellen

"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal, ogr, osr, gdalconst
import seaborn as sns
from math import ceil
from PIL import Image
import re


# ========================= Chemin d'accès & autres =======================

PathImgDSM ='/home/ju/Bureau/DSM_Reproj.tif'

PathImgDTM = '/home/ju/Bureau/DTM_Reproj.tif'

PathDossierCreation = '/home/ju/Bureau/Laurence_resultat/'

PathShpLimite = '/home/ju/Bureau/M2/Traitement_image_Zone_Humide/TD-ZH/3-veget_zh/ancillary_data/limites_zh.shp'

NomRasterReclassLidar = 'RECLASS_LIDAR.tif'

NomRasterLimiteZh = 'Raster_LimiteZh.tif'

PathImgLidarAlign = '/home/ju/Bureau/RECLASS2_CROP_align.tif'

PathImgMaskLimiteZH = '/home/ju/Bureau/Raster_LimiteZh_crop_align.tif'

PathFichierShp = '/home/ju/Bureau/M2/Traitement_image_Zone_Humide/TD-ZH/3-veget_zh/ancillary_data/'

zone = [366267.144, 367993.388, 6831503.872, 6837264.898]
# ======================= Fonction ================================


def LoadImgInd (PathFile):
    try:
        ds = gdal.Open(PathFile).ReadAsArray()

        #print(ds.GetGeoTransform(),'\n', ds.GetProjection())

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
    Info sup: Rien
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
        print(ds_gt)

        row1 = int((yMax - ds_gt[3]) / ds_gt[5])
        print('ROW1 :',row1)

        col1 = int((xMin - ds_gt[0]) / ds_gt[1])
        print('COL1 :',col1)

        row2 = int((yMin - ds_gt[3]) / ds_gt[5])
        print('ROW2 :',row2)

        col2 = int((xMax - ds_gt[0]) / ds_gt[1])
        print('COL2 :',col2)

        print('C\'est lopération col2-col1+1 :','\n',abs(col2 - col1 + 1))
        print('C\'est lopération row2-row1+1 :', '\n', abs(row2 - row1 + 1))

        nArray = ds.ReadAsArray(abs(col1), abs(row1), abs(col2 - col1 + 1), abs(row2 - row1 + 1))

        nArray2 = np.array(nArray).astype(np.float32)
        print(nArray2)

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

def Mask(PathImg1=None, PathImg2=None,modArray=False, matrice1=None, matrice2=None):
    """

    :param PathImg1: Chemin d'accès de l'image à masqué (type = str)
    :param PathImg2: Chemin d'accès de limage servant de masque (type = str)
    :return: Retourne une matrice masqué (type = np.array)
    """
    if modArray is False:
        try:
            ds1 = LoadImgInd(PathImg1)

            ds2 = LoadImgInd(PathImg2)

            npds2_norma = np.where(ds2==0,np.nan,1)

            mask = ds1/npds2_norma

            maskNorma = np.where(mask<0,np.nan,mask)

            return maskNorma

        except ZeroDivisionError:
            pass

        except RuntimeWarning:
            pass

        except ValueError:
            print('CHEH')
            pass
    if modArray is True:
        try:
            ds = matrice1/matrice2
            return ds

        except ZeroDivisionError:
            pass

        except RuntimeWarning :
            pass

        except ValueError :
            print('CHEH')
            pass

def InversValue(PathImg):

    ds = LoadImgInd(PathImg)

    ds_inverse = np.where(ds==255,0,1)

    return ds_inverse


if __name__ == '__main__':

    # Création du DHM

    DSM = LoadImgInd(PathImgDSM)

    DTM = LoadImgInd(PathImgDTM)

    DHM = ImgHeight(DSM, DTM)
    

    # Classification selon la hauteur de la végétation des données LiDAR

    Re = ReclassLidarVeg(DHM)

    WriteRas(Re,PathDossierCreation, NomRasterReclassLidar, PathRasRef=PathImgDSM)
    

    # Rasterisation des fichiers vecteurs

    VtoR(PathShpLimite, PathDossierCreation, NomRasterLimiteZh)

    VtoR(PathFichierShp+'cours_eau.shp', PathDossierCreation,'Cours_Eau.tif')

    VtoR(PathFichierShp+'routes.shp',PathDossierCreation,'routes.tif')

    VtoR(PathFichierShp+'plan_eau.shp', PathDossierCreation, 'Plan_Eau.tif')
    

    # Inversion des valeurs de pixel et Création du raster avec les valeurs inversées

    bati_inverse = InversValue(PathDossierCreation+'Cours_Eau_crop_align.tif')

    WriteRas(bati_inverse,PathDossierCreation,'Bati_inverse.tif',PathDossierCreation+'Bati_crop_align.tif')

    cour_eau_inverse = InversValue(PathDossierCreation+'Cours_Eau_crop_align.tif')

    WriteRas(cour_eau_inverse,PathDossierCreation,'Cour_eau_inverse.tif',PathDossierCreation+'Cours_Eau_crop_align.tif')

    plan_eau_inverse = InversValue(PathDossierCreation+'Plan_Eau_crop_align.tif')

    WriteRas(plan_eau_inverse,PathDossierCreation,'Plan_eau_inverse.tif',PathDossierCreation+'Plan_Eau_crop_align.tif')

    route_inverse = InversValue(PathDossierCreation+'routes_crop_align.tif')

    WriteRas(route_inverse,PathDossierCreation,'Route_inverse.tif',PathDossierCreation+'routes_crop_align.tif')
    

    # Masquage des Zones d'intérêts des données Lidar

    Mask_CE = Mask(PathImg1=PathDossierCreation+'RECLASS2_CROP_align.tif',PathImg2=PathDossierCreation+'Cour_eau_inverse.tif')

    WriteRas(Mask_CE,PathDossierCreation,'Mask1.tif',PathDossierCreation+'RECLASS2_CROP_align.tif')

    Mask_PE = Mask(PathImg1=PathDossierCreation+'Mask1.tif',PathImg2=PathDossierCreation+'Plan_eau_inverse.tif')

    WriteRas(Mask_PE,PathDossierCreation,'Mask2.tif',PathDossierCreation+'Plan_eau_inverse.tif')

    Mask_Road=Mask(PathImg1=PathDossierCreation+'Mask2.tif',PathImg2=PathDossierCreation+'Route_inverse.tif')

    WriteRas(Mask_Road,PathDossierCreation,'Mask3.tif',PathDossierCreation+'Route_inverse.tif')

    Mask_bati=Mask(PathImg1=PathDossierCreation+'Mask3.tif',PathImg2=PathDossierCreation+'Bati_inverse.tif')

    WriteRas(Mask_bati,PathDossierCreation,'Mask4.tif',PathDossierCreation+'Bati_inverse.tif')

    MaskZh = Mask(PathImg1=PathDossierCreation+'Mask4.tif',PathImg2=PathDossierCreation+'Raster_LimiteZh_crop_align.tif')

    WriteRas(MaskZh,PathDossierCreation,'MaskFinal.tif',PathDossierCreation+'Raster_LimiteZh_crop_align.tif')
    
    ImgMaskOptique = LoadImgInd(PathDossierCreation+'MaskFinal.tif')

    maskTotal = np.where(ImgMaskOptique>0,1,0)

    WriteRas(maskTotal,PathDossierCreation,'MaskOptique.tif',PathDossierCreation+'MaskFinal.tif')
    

    # Changement de la Reclass Lidar pour classification

    Lidar=LoadImgInd(PathDossierCreation+'MaskFinal.tif')
    
    Lidar_sans_nan = np.where(np.isnan(Lidar), 0,Lidar)
    
    WriteRas(Lidar_sans_nan,PathDossierCreation,'Lidar_reclass.tif',PathDossierCreation+'MaskFinal.tif')
    

    # Vérification de changement entre les deux classifications Kmeans

    Fusion = LoadImgInd(PathDossierCreation+'MiniBatchKMeans_Kompsat2multipli_15classes.tif')

    SansFusion = LoadImgInd(PathDossierCreation+'MiniBatchKMeans_Kompsat2_15classes.tif')

    chang = Fusion-SansFusion

    print(np.count_nonzero(chang))

    print('Nos classifications sont différence de  ', (np.count_nonzero(chang)/(chang.shape[0]*chang.shape[1]))*100,'%')



