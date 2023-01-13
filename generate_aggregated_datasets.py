import pandas as pd


def load_accidents_caracteristics_df():
    kwargs = {"2009":{"delimiter":";"},"2019":{"delimiter":";"},"2020":{"delimiter":";"},"2021":{"delimiter":";"}}
    cols_to_keep = ['Num_Acc', 'jour', 'mois', 'an', 'hrmn', 'lum', 'dep', 'com', 'agg',
       'int', 'atm', 'col', 'adr', 'lat', 'long']
    df_list = []
    for year in range(2005,2022):
        sep = '_'
        if year > 2016 :
            sep = '-'
        file_path = './data/{}{}{}.csv'.format('caracteristiques',sep,year)
        print(file_path)
        if kwargs.get(str(year)):
            df = pd.read_csv(file_path,**kwargs.get(str(year)))
        else : 
            df = pd.read_csv(file_path,encoding='latin-1')
        df_list.append(df[cols_to_keep])
    return pd.concat(df_list)

def format_columns_caracteristics(df_car):
    #split the df with dates before and after 2019 to homogeneize the data formats

    #before 2019, the field 'an' only contains the two last digits of the year
    df_before_2019 = df_car[df_car['an']<=18]
    df_before_2019['an'] = df_before_2019['an']+2000
    #since 2019, it contains the whole year
    df_2019_and_after = df_car[df_car['an']>=2019]

    #before 2019 hrmn is a four digit number with the hours and minutes
    df_before_2019['hrmn'] = df_before_2019['hrmn'].apply(lambda x : str(x).zfill(4)[:2]+':'+str(x).zfill(4)[2:])
    #since 2019 it is a string with the format HH:mm]

    #before 2019, the field 'dep' is an integer equal to the code of the department
    #followed by a 0.
    df_before_2019['dep'] = df_before_2019['dep'].apply(lambda x : x//10 if x%10==0 else x).astype(str)
    #after 2019, it is a string with the department code
    df_2019_and_after['dep'].astype(str)

    #before 2019, the field 'com' is an integer which gives the insee code of
    #a commune when concatenated with the department code
    df_before_2019['com'] = df_before_2019['com'].astype(str).apply(lambda x : x.zfill(3) if len(x)<3 else x)
    #after 2019, it is the whole insee code of the commune
    #so let's create a new column code_insee in both dataframes
    df_2019_and_after['code_insee'] = df_2019_and_after['com']
    df_before_2019['code_insee'] = df_before_2019['dep']+df_before_2019['com']

    #finally, let's convert the gps cordinates to floats 
    df_before_2019['long'] = df_before_2019['long'].replace('-',0).astype(float)/10**5
    df_before_2019['lat'] = df_before_2019['lat'].replace('-',0).astype(float)/10**5

    df_2019_and_after['long'] = df_2019_and_after['long'].str.replace(',','.').astype(float)
    df_2019_and_after['lat'] = df_2019_and_after['lat'].str.replace(',','.').astype(float)

    print(df_before_2019['hrmn'].dtype)
    print(df_2019_and_after['hrmn'].dtype)

    return pd.concat([df_before_2019,df_2019_and_after])



    


    
