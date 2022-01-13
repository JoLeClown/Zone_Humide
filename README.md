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
    
    ReclassLidarVeg = Fonction permettant de classifier la végétation de l'espace d'étude (cf : 
    



