import sys
sys.path.append('./src')
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from NS_attention import *
from data_generator import DataGenerator, SimpleGenerator
from Dataset import Dataset
from sklearn.utils import shuffle
import argparse
import h5py
import plot
from tensorflow import keras
from tensorflow.keras import mixed_precision

#mixed_precision.set_global_policy('mixed_float16')
config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.compat.v1.Session(config=config)

keras.backend.set_floatx('float32')
parser = argparse.ArgumentParser()
parser.add_argument('-st', '--strides', type=int, default=1,\
                    help='height of the single image')
parser.add_argument('-a', '--architecture', type=str, default="deep",\
                    help='height of the single image')
parser.add_argument('-ke', '--kernelsize', type=int, default=5,\
                    help='height of the single image')
parser.add_argument('-he', '--height', type=int, default=64,\
                    help='height of the single image')
parser.add_argument('-w', '--width', type=int, default=256,\
                    help='width of the single image')
parser.add_argument('-lr', '--learningrate', type=float, default=1e-4,\
                    help='learning rate')
parser.add_argument('-lcont', '--lambdacont', type=float, default=1.0,\
                    help='constant for the pde loss')
parser.add_argument('-lmomx', '--lambdamomx', type=float, default=1.0,\
                    help='constant for the pde loss')
parser.add_argument('-lmomz', '--lambdamomz', type=float, default=1.0,\
                    help='constant for the pde loss')
parser.add_argument('-e', '--epochs', type=int, default=10,\
                    help='number of epochs to train for')
parser.add_argument('-bs', '--batchsize', type=int, default=64, \
                    help='global batch size')
parser.add_argument('-rlr', '--reducelr', type=int, default=0, \
                    help='include RLRoP callback')
parser.add_argument('-pa', '--patience', type=int, default=10, \
                    help='number of patience epochs for RLRoP')
parser.add_argument('-m', '--masking', type=int, default=1, \
                    help='mask some patches')
parser.add_argument('-hp', '--patchheight', type=int, default=32, \
                    help='mask some patches')
parser.add_argument('-wp', '--patchwidth', type=int, default=128, \
                    help='mask some patches')
parser.add_argument('-ah', '--attention', type=int, default=12, \
                    help='number of attention heads')
parser.add_argument('-pr', '--projection', type=int, default=64, \
                    help='number of projection dimentions for the patch encoder')
parser.add_argument('-t', '--transformers', type=int, default=12, \
                    help='number of projection dimentions for the patch encoder')
parser.add_argument('-mn', '--modelname', type=str, default="amr", \
                    help='number of projection dimentions for the patch encoder')

args = parser.parse_args()
mirrored_strategy = tf.distribute.MirroredStrategy()

image_size = [args.height,args.width]
patch_size =[args.patchheight,args.patchwidth]

X_train = np.load('./channelflow_LR.npy')
Y_train = np.load('./Y_channelflow.npy',allow_pickle=True)[0:3]
print(Y_train.shape)


name = "epochs_"+str(args.epochs)+\
       "_lr_"+str(args.learningrate)+\
       "_bs_"+str(args.batchsize)+\
       "_reg_"+str(args.lambdacont)+\
       "_RLR_"+str(args.reducelr)+\
       "_arch_"+str(args.architecture)+\
       args.modelname

if args.architecture == "deep":
 filters=[4,8,16]
if args.architecture == "shallow":
 filters = [4,8]

nsNet =  NSSelfAttention(
               patch_size = [4,16],
               filters=[16,32],
               kernel_size = 5,
               num_attention = 1,
               num_heads=2,
               proj_dimension=64
               )

#nsNet.build(input_shape=[(None,32,128,4),(None,32,128,2)])
optimizer = keras.optimizers.Adam(learning_rate=args.learningrate)
nsNet.compile(optimizer=optimizer,
	      run_eagerly=False)

#nsCB=[]
#
#
#if (args.reducelr):
# nsCB=[    keras.callbacks.ReduceLROnPlateau(monitor='loss',\
#						 factor=0.8,\
#						 min_delta=1e-3,\
#      						 patience=args.patience,
#						 min_lr=1e-7)
#      ]
#
#
#nsCB = [keras.callbacks.EarlyStopping(monitor="val_loss",\
#					min_delta=1e-5,\
#					patience = args.patience,\
#					    verbose=1,\
#					    mode="auto",\
#					    baseline=None,\
#					    restore_best_weights=False,
#)]
#
#
nsCB = []
history = nsNet.fit(x=X_train,
                    y=Y_train,
                    steps_per_epoch = 3,
                    validation_data=(X_train,Y_train),\
                    validation_steps = 1,
                    initial_epoch=0, 
                    epochs=args.epochs,\
                    verbose=1, 
               	    callbacks=nsCB,
              	    shuffle=True)

plot.history(history,name=name)
nsNet.save('./models/'+name)
