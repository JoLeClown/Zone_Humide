# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 15:21:32 2022

@author: Richard
"""

import os
import glob 
from osgeo import gdal, gdal_array, osr
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import KMeans
from sklearn.covariance import EmpiricalCovariance

img = r"C:\Users\richa\Desktop\M2_TELENVI\Semestre1\Traitement_image\TD_ZH\DATA\Kompsat\mask\Kompsat_L93_mask.tif"

# -----------------------------------------------------------------------------------------------
# Fonction 1 : ouverture et lecture d'un stack en array
# -----------------------------------------------------------------------------------------------

def stack2array(img):
    """
    Parametres
    -----
        img(image raster): stack d'image
        
    Returns
    -------
        image (image raster) : stack d'image
        stack_array(numpy array): stack matrice en réflectance
        
    """    
    image = gdal.Open(img) #ouverture de l'image (stack R,V,B,PIR)

    #creation d'une matrice vide avec les proprietes de l'image
    stack_array = np.zeros((image.RasterYSize, image.RasterXSize, image.RasterCount), #RasterYSize = nb pixel en Y, RasterXSize = nb pixel en X, RasterCount = nb de bandes
                           gdal_array.GDALTypeCodeToNumericTypeCode(image.GetRasterBand(1).DataType)) #DataType = type de valeurs, float 32

    #remplissage de la matrice vide avec les valeurs des bandes 
    for e in range(stack_array.shape[2]): #pour chaque elements allant de 0 a X, X etant le nombre de bande (4, voir stack_array[2]) 
        stack_array[:, :, e] = image.GetRasterBand(e + 1).ReadAsArray()/10000
    
    return image, stack_array

# -----------------------------------------------------------------------------------------------
# Fonction 2 : export de l'image resultat en tif
# -----------------------------------------------------------------------------------------------

def export2GTiff(chemin_export, image_matrice, image, image_rslt):
    """
    Parametres
    -----
        chemin_export (chemin) : lieu d'export de l'image
        image_matrice (numpy array) : image ouverte en matrice
        image (raster) : image ouverte avec gdal
        image_rslt (numpy array) : image en matrice a exporter (classif,...)
        
    Returns
    -------
        pas de return car pas de retour de variable necessaire
        
    """    
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(chemin_export, image_matrice.shape[1], image_matrice.shape[0], 1, gdal.GDT_Float32)
    dataset.SetGeoTransform(image.GetGeoTransform())
    dataset.SetProjection(image.GetProjection())
    dataset.GetRasterBand(1).WriteArray(image_rslt)
    dataset.FlushCache()
    dataset = None
        
# ================================================================================================
# PROGRAMME PRINCIPAL - MAIN
# ================================================================================================

image, matrice_stack = stack2array(img) #stockage de la sortie 1 (return image) et 2 (return stack_array)

#reordonner la matrice : chaque bande sur une colonne
new_shape = (matrice_stack.shape[0] * matrice_stack.shape[1], matrice_stack.shape[2])
data = matrice_stack[:, :, :np.int(matrice_stack.shape[2])].reshape(new_shape)

# APPLICATION DE LA CLASSIFICATION NON-SUPERVISEE PAR KMEANS
model_kmeans1 = MiniBatchKMeans(n_clusters=15, random_state=0, batch_size=4758, max_iter=152) #creation du modele de classification
KMeans1 = model_kmeans1.fit(data) #application du modele de classification au jeu de donnees
result_KMeans1 = KMeans1.predict(data) #stockage des resultats de la classification

model_kmeans2 = KMeans(n_clusters = 15, random_state = 0, max_iter = 150)
KMeans2 = model_kmeans2.fit(data)
result_KMeans2 = KMeans2.predict(data)

# EXPORT DE LA CLASSIFICATION EN GEOTIFF

#Reshape de la classification
Classif_KMeans1 = result_KMeans1.reshape(matrice_stack[:, :, 0].shape)
print('Reshaped back to {}'.format(Classif_KMeans1.shape))

Classif_KMeans2 = result_KMeans2.reshape(matrice_stack[:, :, 0].shape)
print('Reshaped back to {}'.format(Classif_KMeans2.shape))

#Export
chemin_export1 = r"C:\Users\richa\Desktop\M2_TELENVI\Semestre1\Traitement_image\MiniBatchKMeans_Kompsat2.tif"
export2GTiff(chemin_export1, matrice_stack, image, Classif_KMeans1)
chemin_export2 = r"C:\Users\richa\Desktop\M2_TELENVI\Semestre1\Traitement_image\KMeans_Kompsat2.tif"
export2GTiff(chemin_export2, matrice_stack, image, Classif_KMeans2)













