import sys
sys.path.append('./src')
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from NS_transformer import *
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
masking=args.masking

#X_train = np.load('./train_input_large.npy')
#print(X_train.shape)


name = "epochs_"+str(args.epochs)+\
       "_lr_"+str(args.learningrate)+\
       "_bs_"+str(args.batchsize)+\
       "_reg_"+str(args.lambdacont)+\
       "_RLR_"+str(args.reducelr)+\
       "_arch_"+str(args.architecture)+\
       args.modelname

factor = 16
f = int(np.sqrt(factor))

if args.architecture == "deep":
 filters=[4,8,16]
if args.architecture == "shallow":
 filters = [4,8]

if args.modelname =="transformer":
  nsNet =  NSTransformer(image_size = [args.height,args.width,6],
                       factor = f,
		       filters=filters,
		       strides=args.strides,
	               kernel_size = args.kernelsize,
                       num_attention=1,
                       projection_dim = 16,
                       num_heads = 2,
                       patch_size = [4,4],
		       beta=[args.lambdacont,args.lambdamomx,args.lambdamomz])


  nsNet.build(input_shape=[(None,16,64,4),(None,64,256,2)])
  nsNet.summary()
  optimizer = keras.optimizers.Adam(learning_rate=args.learningrate)
  nsNet.compile(optimizer=optimizer,
	      run_eagerly=True)
#else: 
# nsNet = 1
#
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
nsCB = [keras.callbacks.EarlyStopping(monitor="val_loss",\
					min_delta=1e-5,\
					patience = args.patience,\
					    verbose=1,\
					    mode="auto",\
					    baseline=None,\
					    restore_best_weights=False,
)]

X_val = np.load('./ellipse03.npy')
Y_val = X_val

history = nsNet.fit(x=X_train,
                    y=X_train,
	            batch_size=args.batchsize,
                    validation_data=(X_val,Y_val),\
                    initial_epoch=0, 
                    epochs=args.epochs,\
                    verbose=1, 
               	    callbacks=nsCB,
              	    shuffle=True)

plot.history(history,name=name)
nsNet.save('./models/'+name)
