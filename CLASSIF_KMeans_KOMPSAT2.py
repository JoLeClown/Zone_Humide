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

chemin_stack = r"C:\Users\richa\Desktop\M2_TELENVI\Semestre1\Traitement_image\TD_ZH\DATA\Kompsat\kompsat_L93.tif"

# tell GDAL to throw Python exceptions, and register all drivers
gdal.UseExceptions()
gdal.AllRegister()

# -----------------------------------------------------------------------------------------------
# Fonction 1 : ouverture et lecture d'un stack en array
# -----------------------------------------------------------------------------------------------

def stack2array(chemin_stack):
    """
    Parametres
    -----
        img(image raster): stack d'image
        
    Returns
    -------
        image (image raster) : stack d'image
        stack_array(numpy array): stack matrice en réflectance
        
    """    
    image = gdal.Open(chemin_stack) #ouverture de l'image (stack R,V,B,PIR)

    #creation d'une matrice vide avec les proprietes de l'image
    stack_array = np.zeros((image.RasterYSize, image.RasterXSize, image.RasterCount), #RasterYSize = nb pixel en Y, RasterXSize = nb pixel en X, RasterCount = nb de bandes
                           gdal_array.GDALTypeCodeToNumericTypeCode(image.GetRasterBand(1).DataType)) #DataType = type de valeurs, float 32

    #remplissage de la matrice vide avec les valeurs des bandes 
    for e in range(stack_array.shape[2]): #pour chaque elements allant de 0 a X, X etant le nombre de bande (4, voir stack_array[2]) 
        stack_array[:, :, e] = image.GetRasterBand(e + 1).ReadAsArray()/10000
    
    return image, stack_array

# ================================================================================================
# PROGRAMME PRINCIPAL - MAIN
# ================================================================================================

image, matrice_stack = stack2array(chemin_stack)

#reordonner la matrice : chaque bande sur une colonne
new_shape = (matrice_stack.shape[0] * matrice_stack.shape[1], matrice_stack.shape[2])
data = matrice_stack[:, :, :np.int(matrice_stack.shape[2])].reshape(new_shape)

# APPLICATION DE LA CLASSIFICATION NON-SUPERVISEE PAR KMEANS
model_kmeans = MiniBatchKMeans(n_clusters=16, random_state=0, batch_size=6, max_iter=150) #creation du modele de classification
KMeans = model_kmeans.fit(data) #application du modele de classification au jeu de donnees
result_KMeans = KMeans.predict(data) #stockage des resultats de la classification

#visualition de la classification
Classif_KMeans = result_KMeans.reshape(matrice_stack[:, :, 0].shape)
print('Reshaped back to {}'.format(Classif_KMeans.shape))

fig, ax = plt.subplots(figsize=(50, 30))

kmeans_plot = ax.imshow(Classif_KMeans)
plt.show()

# EXPORT DE LA CLASSIFICATION EN GEOTIFF

chemin_export = r"C:\Users\richa\Desktop\M2_TELENVI\Semestre1\Traitement_image\TD_ZH\KMeans_Kompsat2.tif"

driver = gdal.GetDriverByName('GTiff')
dataset = driver.Create(chemin_export, matrice_stack.shape[1], matrice_stack.shape[0], 1, gdal.GDT_Float32)
dataset.SetGeoTransform(image.GetGeoTransform())
dataset.SetProjection(image.GetProjection())
dataset.GetRasterBand(1).WriteArray(Classif_KMeans)
dataset.FlushCache()
















