#include <iostream>
#include <vector>
#include <fstream>
#include <ctime>
#include <set>
#include <string>

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

vector<string> q;

void loadFeatures(vector<vector<vector<float> > > &features){
    //open leveldb
    leveldb::DB *db;
    leveldb::Options option;
    option.create_if_missing = true;
    leveldb::DB::Open(option, "/home/microgroup/oxbuild_bow/vgg/query_feature_db", &db);
    leveldb::Iterator* it = db->NewIterator(leveldb::ReadOptions());
    //load features
    int cnt = 0;
    for(it->SeekToFirst(); it->Valid(); it->Next()){
        cout << it->key().ToString() << endl;
        vector<string> key_dim = split(it->key().ToString(), '@');
        q.push_back(key_dim[0]);
        features.push_back(vector<vector<float> > ());
        str2feature(it->value().ToString(), features.back());
    }
}

map<int, string> dict;

void build_dict()
{
  ifstream infile;
  infile.open("cnn_images.txt");
  assert(infile.is_open());
  string s;
  int cnt = 0;
  while(getline(infile, s)){
    vector<string> key_dim = split(s, '@');
    dict[cnt++] = key_dim[0];
  }
}

vector<string>
load_list(const string& fname)
{
  vector<string> ret;
  ifstream fobj(fname.c_str());
  if (!fobj.good()) { cerr << "File " << fname << " not found!\n"; exit(-1); }
  string line;
  while (getline(fobj, line)) {
    ret.push_back(line);
  }
  return ret;
}

template<class T>
set<T> vector_to_set(const vector<T>& vec)
{ return set<T>(vec.begin(), vec.end()); }

float
compute_ap(const set<string>& pos, const set<string>& amb, const vector<string>& ranked_list)
{
  float old_recall = 0.0;
  float old_precision = 1.0;
  float ap = 0.0;
  
  size_t intersect_size = 0;
  size_t i = 0;
  size_t j = 0;
  for ( ; i<ranked_list.size(); ++i) {
    if (amb.count(ranked_list[i])) continue;
    if (pos.count(ranked_list[i])) intersect_size++;

    float recall = intersect_size / (float)pos.size();
    float precision = intersect_size / (j + 1.0);

    ap += (recall - old_recall)*((old_precision + precision)/2.0);

    old_recall = recall;
    old_precision = precision;
    j++;
  }
  return ap;
}

void testDatabase(vector<vector<vector<float> > > &features)
{
  cout << "Retrieving database..." << endl;
  CNN256Database db2("cnn_10k_db.yml.gz");
  cout << "... done! This is: " << endl << db2 << endl;
  int cnt = 0;
  float map = 0;
 
  for(int i = 0; i < q.size(); ++i){ 
    cout << "Current query: " << q[i] << endl;
    vector<string> ranked_list;

    cout << "get CNN features..." << endl;
  
    string gtq = "gt_files/" + q[i];
    set<string> good_set = vector_to_set( load_list(gtq + "_good.txt") );
    set<string> ok_set = vector_to_set( load_list(gtq + "_ok.txt") );
    set<string> junk_set = vector_to_set( load_list(gtq + "_junk.txt") );

    set<string> pos_set;
    pos_set.insert(good_set.begin(), good_set.end());
    pos_set.insert(ok_set.begin(), ok_set.end());

    QueryResults ret;
    db2.query(features[i], ret, 5063);
    QueryResults::const_iterator qit;
    for(qit = ret.begin(); qit != ret.end(); ++qit){
        ranked_list.push_back(dict[qit->Id]);
        cout << "GET " << qit->Id << " " << dict[qit->Id] << endl;
    }
    float ap = compute_ap(pos_set, junk_set, ranked_list);
    cout << "AP: " << ap << endl;
    cnt++;
    map += ap;
  }
  map /= cnt;
  cout << "mAP: " << map << endl;
}

int main(){
  vector<vector<vector<float> > > features;
  build_dict();
  loadFeatures(features);
  testDatabase(features); 
  return 0;
}
