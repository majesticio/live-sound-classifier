# -*- coding: utf-8 -*-
"""live-sound-classifier-only.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1R7xs077Cv8Luc3cx43Ro1bB7wBeEWoZO
"""

#import IPython.display as ipd
#import matplotlib.pyplot as plt
#import tensorflow as tf
import pandas as pd 
import wave
import struct
from sklearn.preprocessing import LabelEncoder 
from sklearn.model_selection import train_test_split 
from tensorflow.keras.utils import to_categorical
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, Conv2D, MaxPooling2D, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from keras.utils import np_utils
from sklearn import metrics
from keras.callbacks import ModelCheckpoint 
from datetime import datetime 
from playsound import playsound
import os
import librosa
import librosa.display
from pydub import AudioSegment
import numpy as np
import soundfile as sfile
import math
import matplotlib.pyplot as plt
from scipy.io import wavfile
import subprocess
# import audioop
import os
import datetime
import pickle

#Declare path for pickled variables X, y
pickledX = '/home/samus/models/variables/pickledX.x'
pickledY = '/home/samus/models/variables/pickledY.y'

#Assign X and y to thier respective pickles
X = pickle.load(open(pickledX, 'rb'))
y = pickle.load(open(pickledY, 'rb'))

#All of the metadata is defined from X and y(!)
# Encode the classification labels
le = LabelEncoder()
yy = to_categorical(le.fit_transform(y)) 

# split the dataset 

x_train, x_test, y_train, y_test = train_test_split(X, yy, test_size=0.2, random_state = 42)

#Question for Nevin: do I need checkpointer, model.fit? Do I need to compile?
# num_epochs = 128
# num_batch_size = 64
# checkpointer = ModelCheckpoint(filepath='saved_models/weights.best.basic_mlp.hdf5', 
#                                verbose=1, save_best_only=True)

# %store

"""Load a pickeled model."""

# load the model from pickled model path
pickledModelPath = '/home/samus/models/pickeled_model.sav'
model = pickle.load(open(pickledModelPath, 'rb'))

"""Load a pre-trained model.

Very Important
"""

#Must Declare
num_rows = 40
num_columns = 174
num_channels = 1

"""Compile the model."""

#Do I need to compile?
model.summary()

#Define a function that will create a spectrogram for each audio sample. 
#This function uses librosa to standardize the data.

max_pad_len = 174 #original
# max_pad_len = 255

def extract_features(file_name):
   
    try:
        audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast') 
        # print(sample_rate)
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        # print(mfccs)
        pad_width = max_pad_len - mfccs.shape[1]
        # print(mfccs.shape[1])
        mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)),
                       mode='constant')
        
    except Exception as e:
        print("Error encountered while parsing file: ", file_name)
        return None 
     
    return mfccs

def print_prediction(file_name):
    prediction_feature = extract_features(file_name)
    # print("Printing Type: ")
    # type(prediction_feature)
    # print("Printing Feature")
    # print(prediction_feature)
    prediction_feature = prediction_feature.reshape(1, num_rows, num_columns, num_channels)#very important 

    predicted_vector = model.predict(prediction_feature) 
    # np.argmax(model.predict(x), axis=-1)
    
    predicted_class = np.argmax(predicted_vector,axis=1)
    labels = ["air_conditioner", "car_horn", "children_playing", "dog_bark", "drilling", "engine_idling",
              "glass_breaking", "gun_shot", "jackhammer", "siren", "street_music"]
    print("The predicted class is:", labels[predicted_class[0]], '\n') 

    predicted_proba_vector = model.predict(prediction_feature) 
    predicted_proba = predicted_proba_vector[0]
    for i in range(len(predicted_proba)): 
        category = le.inverse_transform(np.array([i]))
        print(category[0], "\t\t : ", format(predicted_proba[i], '.32f') )

def checkVolumePredict(filename, sensitivity):
# sensitivity = -40
  audio=AudioSegment.from_mp3(filename)
  signal, sr = sfile.read(filename)
  samples=audio.get_array_of_samples()
  samples_sf=0
  try:
      samples_sf = signal[:, 0]  # use the first channel for dual
  except:
      samples_sf=signal  # for mono


  def convert_to_decibel(arr):

    ref = 1
    if arr !=0:
      return 20 * np.log10(abs(arr) / ref)
          
    else:
      return -60
  data=[convert_to_decibel(i) for i in samples_sf]
  highest = max(data)
  print ("highest reading:",
        highest)
  if highest > sensitivity:
    print_prediction(filename)
    print(highest)
    os.system("rm " + filename)

  else:
    os.system("rm " + filename)
    # subprocess.run(["rm" , filename])
    print('too quiet', highest)

###SYSTEM TEST
#Class: glass breaking
#filename = '/home/samus/DataCollection/fucked/legit.wav'
#print_prediction(filename)


###MAIN LOOP
##Check for files
##Analyze files
##Remove files

path_to_watch = '/home/samus/Music/buffer/'
print('Your folder path is"',path_to_watch,'"')

print(old)

while True:
    new = os.listdir(path_to_watch)
    if len(new) > 1:
        #newfile = list(set(new))
        print(new[0])
        checkVolumePredict(new[0], -40); #Determines decibel threshold

        #old = new
        #os.system("rm " + new[0])

    else:
        continue
