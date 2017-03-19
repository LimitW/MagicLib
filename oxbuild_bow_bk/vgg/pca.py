import leveldb
import pickle
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize
import numpy as np
import sys

db = leveldb.LevelDB('vgg_feature_db')

def load_features():
    ks = []
    vs = []
    for k, v in db.RangeIter():
        ks.append(k)
        vv = np.fromstring(v, dtype='float32').reshape(336,512)
        print vv.shape
        sys.stdout.flush()
        vs.extend(vv)
    return ks, vs

import os

pca_model_name = 'ox_cnn_pca_model.pkl'

pca_model = None

if os.path.isfile(pca_model_name):
    pca_model = pickle.load(open(pca_model_name, 'rb'))

keys, features = load_features()

features = np.array(features)

print features.shape

features = normalize(features)

if pca_model == None:
    pca_model = PCA(n_components=256, whiten=True)
    features = pca_model.fit_transform(features)
    print 'saving model...'
    pickle.dump(pca_model, open(pca_model_name, 'wb'))
else:
    features = pca_model.transform(features)

print 'Features l2 normalization'

features = normalize(features)

def tostr(v):
    return '@'.join(['#'.join(map(str, row)) for row in v])

db = leveldb.LevelDB('ox_cnn_feature_db')

sz = 336

feats_split = [features[i:i+sz] for i in range(0, len(features), sz)]

print len(feats_split)

for k, v in zip(keys, feats_split):
    db.Put(k, tostr(v))

