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

const bool EXTENDED_SURF = false;

// ----------------------------------------------------------------------------

map<int, string> dict;

void build_dict()
{
  ifstream infile;
  infile.open("images_p.txt");
  assert(infile.is_open());
  string s;
  int cnt = 0;
  while(getline(infile, s)){
    dict[cnt++] = s;
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

void changeStructure(const vector<float> &plain, vector<vector<float> > &out,
  int L)
{
  out.resize(plain.size() / L);

  unsigned int j = 0;
  for(unsigned int i = 0; i < plain.size(); i += L, ++j)
  {
    out[j].resize(L);
    std::copy(plain.begin() + i, plain.begin() + i + L, out[j].begin());
  }
}

void testDatabase()
{
  ifstream infile;
  infile.open("querys.txt");
  assert(infile.is_open());

  string path = "/home/microgroup/oxbuild_bow/query_images/";
  string s;

  cout << "Retrieving database once again..." << endl;
  Surf64Database db2("100k_db.yml.gz");
  cout << "... done! This is: " << endl << db2 << endl;
  int cnt = 0;
  float map = 0;
  
  while(getline(infile, s))
  {

    stringstream ss;
    ss << path << s << ".jpg";
    cout << "Current query: " << s << endl;
    ifstream imageFile;
    string tmp = ss.str();
    imageFile.open(tmp.c_str());
    vector<string> ranked_list;

    cv::Ptr<cv::xfeatures2d::SURF> surf = cv::xfeatures2d::SURF::create(400, 4, 2, EXTENDED_SURF);

    cout << "Extracting SURF features..." << endl;
  
    cv::Mat image = cv::imread(ss.str(), 0);
    cv::Mat mask;
    vector<cv::KeyPoint> keypoints;
    vector<float> descriptors;

    surf->detectAndCompute(image, mask, keypoints, descriptors);
    vector<vector<float> > feature;

    changeStructure(descriptors, feature, surf->descriptorSize());

    string gtq = "gt_files/" + s;
    set<string> good_set = vector_to_set( load_list(gtq + "_good.txt") );
    set<string> ok_set = vector_to_set( load_list(gtq + "_ok.txt") );
    set<string> junk_set = vector_to_set( load_list(gtq + "_junk.txt") );

    set<string> pos_set;
    pos_set.insert(good_set.begin(), good_set.end());
    pos_set.insert(ok_set.begin(), ok_set.end());

    QueryResults ret;
    db2.query(feature, ret, 10);
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
  build_dict();
  testDatabase(); 
  return 0;
}
