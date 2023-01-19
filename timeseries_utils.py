import numpy as np
from sklearn.preprocessing import MinMaxScaler
import keras
import pandas as pd
from copy import deepcopy
from keras.utils import timeseries_dataset_from_array
from keras.callbacks import ModelCheckpoint
from keras.models import Sequential, load_model
from keras.layers import Masking , TimeDistributed, Bidirectional, Dense , LSTM, Dropout , Conv1D , MaxPooling1D , Reshape , Activation
from keras.optimizers import Nadam

def reshape_timeseries(series , target_ids, win_size , take_curr = True , scale = True):
    
    X = series.values
    Y = series.iloc[ : , target_ids].values
    
    # Scaling des données 
    if scale:
        maxs = Y.max(axis = 0)
        Y = np.divide( Y , maxs)
        X = MinMaxScaler().fit_transform(X)
    
    ts = timeseries_dataset_from_array(X[:-1] , np.roll(Y,-win_size)[:-1] , win_size , batch_size = X.shape[0])
    X , Y = list(ts.as_numpy_iterator())[0]

    X = X.copy()
    Y = Y.copy()
    
    # Masking
    if take_curr:
        for step in X[: , win_size - 1]:
            step[target_ids] = [-2 for i in target_ids]
    else:
        X = X[: , :-1]
        
    if scale:
        return X , Y , maxs

    return X,Y

def lstm_model(X , Y , lr = 0.001,
          lstm_layers = [] , lstm_dropout = [],
          dense_layers = [] , dense_dropout = [] ,
          ntest_day = 365 , epochs = 10 , batch_size = 32):
        
        
    # training et test sets :
    length , timesteps , features = X.shape[0] , X.shape[1] , X.shape[2]
    target_shape = Y.shape[1]
    
    # Validation rate à passer au modèle séquentiel :
    validation_rate = ntest_day/length
    
    
    ############################################ Model :
    
    checkpoint = ModelCheckpoint('model' , save_best_only=True)

    model = Sequential()
    
    # couche de masking 
    model.add(Masking(mask_value = -2 , input_shape=(X.shape[1],  X.shape[2])    ))
    
    
    # couches BI-LSTM.
    for i in range(len(lstm_layers)):
        return_sequences  = not (i == (len(lstm_layers) - 1))
        model.add(Bidirectional( LSTM(lstm_layers[i] , return_sequences = return_sequences) ,input_shape=(X.shape[1], X.shape[2]) ) )
        model.add(Dropout(lstm_dropout[i]))

    # couches denses.
    for i in range(len(dense_layers)): 
        model.add(Dense(dense_layers[i]) )
        model.add(Dropout(dense_dropout[i]))
        model.add(Activation('relu'))
        
    
    model.add(Dense(target_shape))
    opt = Nadam(lr = lr , beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    model.compile(loss='mean_squared_error', optimizer=opt)
    
    print('Résumé du modèle:')
    print(model.summary())
    
    # fitting the data
    print('\n\n Entraînement du modèle :')
    model.fit(X, Y, epochs= epochs, batch_size=batch_size, validation_split = validation_rate, callbacks = [checkpoint])

    # loading best_model
    model = load_model('model')
    
    return model

def long_term_prediction(model , X , nb_targets):   
    preds = []
    new_line = X[0].reshape(1 , *X.shape[1:])
    pred = model.predict(new_line)
    preds.append(pred)
    
    for line in X[1:]:
        old_line = deepcopy(line)
        old_line[-2 , :nb_targets] = pred
        pred= model.predict(old_line.reshape(1 , *X.shape[1:]))
        preds.append(pred)
        
    return np.array(preds).reshape(-1 , nb_targets )

def get_prediction_dates(last_date,num_prediction):
    prediction_dates = pd.date_range(last_date, periods=num_prediction+1).tolist()
    return prediction_dates
    
    

    