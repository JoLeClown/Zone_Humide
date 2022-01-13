>>> PROJET Zone_humide <<<
-----------------------------
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
 
Après l'espace dédié au chargement des librairies, 
un espace de chargement des liens vers les différentes données est proposé 
afin de lancer plus facilement le programme principale dans son intégralité.

Le programme principale ( à partir de if __name__=='__main__'), n'est pas complet dans les traitements à effectuer pour pouvoir sortir les images pré-traitées.
Mais le développement d'autres fonctions permettant d'automatiser les traitements est à venir.

Nous vous engagons à utiliser les fonctions mais pas forcément le programme principale car il répond à des besoins de standardisations de données particulier.
 
------------------------------------------------
MODE D'EMPLOI : Programme Classification Kmeans
------------------------------------------------

Les fonction proposées :






---------
A SAVOIR
---------

Nous essayerons de regrouper les deux programmes de ce répertoire pour alléger la complexité de ces programmes.

Les seuils utilisés pour le reclassement des données Lidar sont fixes. Pour les changer il faut changer les valeurs exprimées dans les conditions np.where()
c'est le premier argument du np.where.

Une fonction dédiée aux classifieurs sera disponible prochainement.

Une fonction d'alignement des rasters (correction géométrique), sera développée prochainement.

Ces programmes sont le résultat d'un dossier d'étude demandé dans le cadre de nos études (Master TELENVI Université Rennes 2),
soyez indulgent dans vos retours, nous ne sommes pas professionnel (pour l'instant).  

Les données standardisées = la même résolution spatiale, le même nombre de lignes/colonnes, le même système de projection
avant d'être classifiées. 

La fonction crop peut être difficile à utiliser, nous cherchons activement le moyen de rendre plus stable cette fonction.

Et n'hésitez pas à faire vos retours!





