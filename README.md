# API pour la gestion des attractions touristiques

Cette API permet de récupérer des informations sur des attractions touristiques en fonction de divers critères : nom de la ville, coordonnées géographiques, ou encore nom et adresse de l'attraction. Elle prend en charge quatre types de requêtes pour récupérer des informations sur les lieux et leurs caractéristiques dans un rayon de 5 km autour d'un centre défini par des coordonnées géographiques ou un nom de ville.

## Description

L'API Places permet de récupérer une liste de lieux en fonction de 4 catégories prédéfinies :  
- **touristique** : Lieux touristiques
- **nature** : Lieux naturels (parcs, réserves naturelles, etc.)
- **restaurant** : Restaurants et points de restauration
- **autre** : Autres lieux d'intérêt général

L'API permet de récupérer des informations détaillées sur ces lieux, telles que :
- **Nom** : Nom du lieu
- **Adresse** : Adresse formatée
- **ID** : Identifiant unique du lieu
- **Latitude et Longitude** : Coordonnées géographiques
- **Évaluation** : Note moyenne (si disponible)
- **Nombre d'avis** : Nombre d'avis utilisateurs
- **Photos** : URLs des photos disponibles
- **Site web** : URL du site web (si disponible)
- **Google Maps URL** : Lien vers le lieu sur Google Maps
- **Numéro de téléphone** : Numéro international du lieu (si disponible)
- **Description** : Description éditoriale du lieu
- **Horaires d'ouverture** : Horaires réguliers (si disponibles)
- **Catégorie** : Catégorie du lieu (touristique, nature, restaurant, autre)

Les lieux sont filtrés dans un cercle d'un rayon de 5 km dont le centre est :
- Le **nom d'une ville** ou **lieu**, ou
- Les **coordonnées géographiques** (latitude et longitude).

L'API permet également de récupérer des informations détaillées sur un lieu précis en utilisant soit :
- Le **nom** du lieu, soit
- Les **coordonnées géographiques** du lieu.

## Routes disponibles

### 1. Récupérer des attractions par ville et catégorie
**Endpoint**: `/attractions/city={city_name}&category={category}`  
**Méthode**: `GET`

Permet de récupérer des attractions touristiques situées dans une ville donnée et appartenant à une catégorie spécifique.

#### Paramètres :
- **city_name** : Nom de la ville
- **category** : Catégorie d'attractions (ex : `touristique`, `nature`, `restaurant`, `autre`)

### 2. Récupérer des attractions par coordonnées géographiques
**Endpoint**: `/attractions_with_coordinates/coordinates={latitude}-{longitude}&attractions={attraction}`  
**Méthode**: `GET`

Permet de récupérer des attractions touristiques situées à proximité des coordonnées géographiques fournies.

#### Paramètres :
- **latitude** : Latitude des coordonnées
- **longitude** : Longitude des coordonnées
- **attraction** : Catégorie d'attraction (ex : `touristique`, `nature`, `restaurant`, `autre`)

### 3. Récupérer des informations sur une attraction à partir de son nom et adresse
**Endpoint**: `/attraction/name={place_name}&adress={address}`  
**Méthode**: `GET`

Permet de récupérer les informations détaillées d'une attraction en fournissant son nom et son adresse.

#### Paramètres :
- **place_name** : Nom de l'attraction
- **address** : Adresse de l'attraction

### 4. Récupérer des informations sur une attraction à partir des coordonnées géographiques
**Endpoint**: `/attraction_with_coordinates/{latitude}-{longitude}`  
**Méthode**: `GET`

Permet de récupérer les informations détaillées d'une attraction en fournissant ses coordonnées géographiques.

#### Paramètres :
- **latitude** : Latitude des coordonnées
- **longitude** : Longitude des coordonnées

## Instructions de déploiement

### Prérequis
- Python 3.9 ou supérieur
- Installer les dépendances avec `pip install -r requirements.txt`
- Une clé API Google Places valide pour interagir avec les services de Google Maps.

### Étapes de déploiement :
1. **Cloner le dépôt** :
   ```bash
   git clone <URL_DU_REPOSITORY>