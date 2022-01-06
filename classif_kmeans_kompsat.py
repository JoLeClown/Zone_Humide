# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 15:33:42 2022

@author: richa
"""

import os
import glob 
import gdal
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

wd = r"C:\Users\richa\Desktop\M2_TELENVI\Semestre1\Traitement_image\TD_ZH\DATA\Kompsat" #répertoire des données
os.chdir(wd)

# -----------------------------------------------------------------------------------------------
# Fonction 1 : ouverture et lecture de l'image en array
# -----------------------------------------------------------------------------------------------

def raster2array(img):
    """
    Parametres
    -----
        img(image raster): bande spectrale
        
    Returns
    -------
        array_refl(numpy array): image matrice en réflectance
        
    """
    raster = gdal.Open(img) #ouverture de l'image
    array = raster.ReadAsArray() #lecture de l'image en array (matrice)
    array_refl = array/10000 #conversion en réflectance
    
    return array_refl

# ================================================================================================
# PROGRAMME PRINCIPAL - MAIN
# ================================================================================================

#-------------------------------------------------------------------------------------------------
# 1. Affichage des bandes R,V,B et PIR, puis les mettre dans une liste

debut1 = time.time()

liste_images = []

for images_name in glob.glob("*.tif"):
    if images_name[8:-8]== "R" or images_name[8:-8]== "V" or images_name[8:-8]== "B" or images_name[8:-8]== "PIR":#sélection des bandes en fonction de la chaîne de caractères
        liste_images.append(wd + '\\' + images_name) #ajout de chemin et du nom de l'image dans une liste
            
print('---------------------ETAPE 1 TERMINEE---------------------')
fin1 = time.time()
print("Temps écoulé (secondes): %f"% (fin1-debut1))

#-------------------------------------------------------------------------------------------------
# 2. Ouverture des bandes en array (matrice)

debut2 = time.time()

liste_array_refl = [] #liste d'accueil des matrices
    
for image in liste_images:
    liste_array_refl.append(raster2array(image)) #stockage du résultat dans une liste
    
print('---------------------ETAPE 2 TERMINEE---------------------')
fin2 = time.time()
print("Temps écoulé (secondes): %f"% (fin2-debut2))

#-------------------------------------------------------------------------------------------------
# 3. Ajouter les arrays dans un stack

debut3 = time.time()
"""
try:
    stack = np.stack((liste_array_refl[0],liste_array_refl[1],liste_array_refl[2],liste_array_refl[3])) #empilement des matrices des bandes spectrales
except MemoryError:
    print(r"Votre mémoire est pleine, n'hésitez pas à la videz de temps en temps !" )
"""
stack = np.array([np.ravel(liste_array_refl[0]), np.ravel(liste_array_refl[1]), np.ravel(liste_array_refl[2]), np.ravel(liste_array_refl[3])])

print('---------------------ETAPE 3 TERMINEE---------------------')
fin3 = time.time()
print("Temps écoulé (secondes): %f"% (fin3-debut3))

# #-------------------------------------------------------------------------------------------------
# # 4. Conversion de la matrice stackée en DataFrame

# debut4 = time.time()

# stackDF = pd.DataFrame(stack, index = ['red', 'green', 'blue', 'pir'])
# stackDF = stackDF.T #inversement des lignes et colonnes

# print(stackDF.head())

# print('---------------------ETAPE 4 TERMINEE---------------------')
# fin4 = time.time()
# print("Temps écoulé (secondes): %f"% (fin4-debut4))

#-------------------------------------------------------------------------------------------------
# 4. Application de KMEANS au stack, avec 5 clusters
model_kmeans = KMeans(n_clusters = 5).fit(stack) #5 clusters pour les 5 seuils de hauteurs d'arbres
result_kmeans = model_kmeans.predict(stack)

#-------------------------------------------------------------------------------------------------
# 4. Reconversion de la matrice résultat (classif) en image

nb_lines = 1482
nb_col = 488

result_kmeans = np.reshape(result_kmeans, [nb_lines, nb_col])
plt.imshow(result_kmeans, cmap="Dark2")
plt.show()

