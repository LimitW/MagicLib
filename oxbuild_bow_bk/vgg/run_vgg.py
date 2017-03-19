#coding=utf-8
import numpy as np
#import matplotlib.pyplot as plt

caffe_root = '/home/microgroup/test_caffe/'
pwd_root = '/home/microgroup/oxbuild_bow/vgg/'

import sys
sys.path.insert(0, caffe_root + 'python')

import caffe
import os

caffe.set_mode_gpu()
model_def = pwd_root + 'vgg16_pool5.prototxt'
model_weights = pwd_root + 'vgg16.caffemodel'

net = caffe.Net(model_def, model_weights, caffe.TEST)

mu = np.load(pwd_root + 'mean.npy')
mu = mu.mean(1).mean(1)

transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))  # move image channels to outermost dimension
transformer.set_mean('data', mu)            # subtract the dataset-mean value in each channel
transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
transformer.set_channel_swap('data', (2,1,0))  # swap channels from RGB to BGR

net.blobs['data'].reshape(1, 3, 336, 256)

import leveldb

db = leveldb.LevelDB('vgg_feature_db')

for fl in os.listdir(pwd_root + '../oxbuild_images/'):
    print 'current file: ' + fl
    pa = pwd_root + '../oxbuild_images/' + fl
    if os.path.isfile(pa) != True:
        print 'no this file'
        continue
    image = caffe.io.load_image(pa)
    net.blobs['data'].data[...] = transformer.preprocess('data', image)
    output = net.forward()
    layers = [(k, v.data.shape) for k, v in net.blobs.items()]
    feats = net.blobs['conv5_1'].data.copy().astype(np.float32).squeeze()
    dim = feats.shape
    feats = feats.swapaxes(0, 1).swapaxes(1, 2)
    feats = feats.reshape(dim[2] * dim[1], dim[0])
    key = '@'.join([fl.split('.')[0], str(dim[2]*dim[1]), str(dim[0])])
    val = feats.tostring()
    print key, feats.shape
    db.Put(key, val)
