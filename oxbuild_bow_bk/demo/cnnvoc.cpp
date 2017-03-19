/**
 * File: CNN_Demo.cpp
 * Date: November 2011
 * Author: Dorian Galvez-Lopez
 * Description: demo application of DBoW2
 * License: see the LICENSE.txt file
 */

#include <iostream>
#include <vector>
#include <fstream>
#include <ctime>

// DBoW2
#include "DBoW2.h" // defines Surf64Vocabulary and Surf64Database

#include <DUtils/DUtils.h>
#include <DVision/DVision.h>

// OpenCV
#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/xfeatures2d/nonfree.hpp>

// leveldb

#include <cassert>
#include "leveldb/db.h"


using namespace DBoW2;
using namespace DUtils;
using namespace std;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

void loadFeatures(vector<vector<vector<float> > > &features);
void testVocCreation(const vector<vector<vector<float> > > &features);

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

// number of training images
int NIMAGES = 5063; 

// ----------------------------------------------------------------------------

int main()
{
  vector<vector<vector<float> > > features;
  time_t t1, t2, t3, t4;
  time(&t1);
  loadFeatures(features);
  time(&t2);
  cout << "LOAD FEATURES:" << 1.0*(t2-t1)/3600 << "h" << endl;
  testVocCreation(features);
  time(&t3);
  cout << "BUILD VOC:" << 1.0*(t3-t2)/3600 << "h" << endl;
  return 0;
}

// ----------------------------------------------------------------------------

vector<string> split(string s, char x){
    vector<string> res;
    string str = "";
    for(int i = 0; i < s.size(); ++i){
        if(s[i] == x){
            res.push_back(str);
            str = "";
        }
        else str += s[i];
    }
    res.push_back(str);
    return res;
}

void str2feature(string str, vector<vector<float> > &res){
    vector<string> map_str = split(str, '@');
    vector<vector<string> > str_res;
    for(int i = 0; i < map_str.size(); ++i){
        str_res.push_back(split(map_str[i], '#'));
    }
    for(int i = 0; i < str_res.size(); ++i){
        vector<float> a_map;
        for(int j = 0; j < str_res[i].size(); ++j){
            float val = atof(str_res[i][j].c_str());
            a_map.push_back(val);
        }
        res.push_back(a_map);
    }
}

void loadFeatures(vector<vector<vector<float> > > &features){
    //open leveldb
    leveldb::DB *db;
    leveldb::Options option;
    option.create_if_missing = true;
    leveldb::DB::Open(option, "/home/microgroup/oxbuild_bow/vgg/vgg_pca_feature_db", &db);
    leveldb::Iterator* it = db->NewIterator(leveldb::ReadOptions());
    //load features
    for(it->SeekToFirst(); it->Valid(); it->Next()){
        cout << it->key().ToString() << endl;
        features.push_back(vector<vector<float> > ());
        str2feature(it->value().ToString(), features.back());
    }
}
// ----------------------------------------------------------------------------

void testVocCreation(const vector<vector<vector<float> > > &features)
{
  // branching factor and depth levels 
  const int k = 10;
  const int L = 5;
  const WeightingType weight = TF_IDF;
  const ScoringType score = L2_NORM;

  CNN256Vocabulary voc(k, L, weight, score);

  cout << "Creating a small " << k << "^" << L << " vocabulary..." << endl;
  voc.create(features);
  cout << "... done!" << endl;

  cout << "Vocabulary information: " << endl
  << voc << endl << endl;

  // save the vocabulary to disk
  cout << endl << "Saving vocabulary..." << endl;
  voc.save("cnn_100k_voc.yml.gz");
  cout << "Done" << endl;
}
