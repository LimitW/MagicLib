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

void testDatabase(const vector<vector<vector<float> > > &features);

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

// number of training images
int NIMAGES = 5063; 

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


int main()
{
  vector<vector<vector<float> > > features;
  time_t t1, t2, t3;
  time(&t1);
  loadFeatures(features);
  time(&t2);
  cout << "LOAD FEATURES:" << 1.0*(t2-t1)/3600 << "h" << endl;
  testDatabase(features);
  time(&t3);
  cout << "BUILD DB:" << 1.0*(t3-t2)/3600 << "h" << endl;
  return 0;
}

void testDatabase(const vector<vector<vector<float> > > &features)
{
  cout << "Creating a small database..." << endl;

  // load the vocabulary from disk
  CNN256Vocabulary voc("cnn_100k_voc.yml.gz");
  
  CNN256Database db(voc, false, 0); // false = do not use direct index
  // (so ignore the last param)
  // The direct index is useful if we want to retrieve the features that 
  // belong to some vocabulary node.
  // db creates a copy of the vocabulary, we may get rid of "voc" now

  // add images to the database
  for(int i = 0; i < NIMAGES; i++)
  {
    db.add(features[i]);
  }

  cout << "... done!" << endl;

  cout << "Database information: " << endl << db << endl;
  // we can save the database. The created file includes the vocabulary
  // and the entries added
  cout << "Saving database..." << endl;
  db.save("cnn_100k_db.yml.gz");
  cout << "... done!" << endl;
}
