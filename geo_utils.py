import requests
import numpy as np
import json

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
