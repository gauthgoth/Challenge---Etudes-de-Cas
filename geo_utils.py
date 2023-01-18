import requests
import numpy as np
import json
from requests.structures import CaseInsensitiveDict
import pandas as pd

def filter_france_metr(df):
    mask = df['dep'].apply(lambda x : len(x)<3)
    return df[mask]

def get_com_coordinates(insee_code):
    try :
        response = requests.get('https://geo.api.gouv.fr/communes/{}?fields=centre'.format(insee_code)).json()
        return {'lon':response['centre']['coordinates'][0],'lat':response['centre']['coordinates'][1]}

    except:
        print('Warning : Could not get coordinates of commune with code {}'.format(insee_code))
        return dict()

def generate_mapping_insee_to_coords(insee_codes):
    mapping_insee_codes_coord = {insee_code:get_com_coordinates(insee_code) for insee_code in insee_codes}
    with open('communes_coordinates.json','w') as json_file:
        json.dump(mapping_insee_codes_coord,json_file)
        json_file.close()

def get_postcode_from_coord(lon,lat):
    url = "https://api.geoapify.com/v1/geocode/reverse?lat={}&lon={}&apiKey=6642b907a72940dcb7b6b3e0f9a1605a".format(lat,lon)

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    resp = requests.get(url, headers=headers)
    try :
        postcode = resp.json()['features'][0]['properties']['postcode']
    except:
        return None
    return postcode

def generate_postcodes(df_comptage):
    piv_table=df_comptage.pivot_table(index='id_compteur', values='coordinates', aggfunc='head')
    piv_table=piv_table['coordinates'].str.split(',',expand=True)
    piv_table=piv_table.applymap(float)
    postal_codes = piv_table.apply(lambda x : get_postcode_from_coord(x[1],x[0]) , axis=1)
    postal_codes=pd.DataFrame(postal_codes, columns=['postal_code'])
    localisations=df_comptage.merge(postal_codes,left_index=True, right_index=True)
    localisations=localisations[['id_compteur','nom_compteur','coordinates','postal_code']]
    return localisations

def filter_paris_postcodes(df):
    return df[df['postal_code'].astype(str).str[:2]=='75']
