>>> PROJET Zone_humide <<<
Préparation de données et classification des zones humides selon la végétation

-------
AUTEURS
-------
R.Sourbes, L.Orgambide, J.Pellen
Université Rennes 2
Janvier 2022

--------------------
Librairies utilisées
--------------------
Gdal, Gdalconstant, Numpy, Matplotlib, Seaborn, Sklearn

---------------------
Présentation générale
---------------------

Ce projet se distingue en deux programmes différents:

1- Un programme permettant de préparer les données Lidar et Optique (Zone_Humide.py)

2- Un programme de Classification Kmeans (CLASSIF_KMeans_KOMPSAT2.py)

-------------------------------------
MODE D'EMPLOI : Programme Zone_Humide
-------------------------------------

Les fonctions proposées:

    LoadImg = Fonction permettant de charger une image en table numpy
    
    ImgHeight = Fonction permettant de calculer le modèle numérique d' à partir d'un modèle numérique de surface et un modèle numérique de terrain
    
    ReclassLidarVeg = Fonction permettant de classifier la végétation de l'espace d'étude (cf : Presentation_Git_Reclass.png)
    
    Resample = Fonction permettant de changer la résolution spatiale d'une image géoréférencé
    
    VtoR = Fonction permettant de 'Rasteriser' des couches .shp, et obtenir une images binaire
    
    WriteRas = Fonction permettant de créer une image géoreférencer 
    
    Reproj = Fonciton permettant de changer le système de projection d'une image géoréférencée
    
    Crop = Fonction permettant de sélectionner un espace particulier au sein d'une image
    
    Mask = Fonction permettant de masquer de suprimer des valeurs de pixels entre deux images 
    
    InversValue = Fonction permettant d'inverser les valeurs d'une  image binaire (un pixel ayant une valeur de 0 passe à 1) 
    



