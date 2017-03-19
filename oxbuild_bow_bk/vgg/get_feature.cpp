#include <bits/stdc++.h>
#include "leveldb/db.h"

using namespace std;

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

void loadfeatures(vector<vector<vector<float> > > &features){
    //open leveldb
    leveldb::DB *db;
    leveldb::Options option;
    option.create_if_missing = true;
    leveldb::DB::Open(option, "vgg_pca_feature_db", &db);
    leveldb::Iterator* it = db->NewIterator(leveldb::ReadOptions());
    //load features
    for(it->SeekToFirst(); it->Valid(); it->Next()){
        features.push_back(vector<vector<float> > ());
        str2feature(it->value().ToString(), features.back());
    }
}
