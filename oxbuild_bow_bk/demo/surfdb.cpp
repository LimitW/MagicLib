/**
 * File: Demo.cpp
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
void changeStructure(const vector<float> &plain, vector<vector<float> > &out,
  int L);
void testVocCreation(const vector<vector<vector<float> > > &features);
void testDatabase(const vector<vector<vector<float> > > &features);

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

// number of training images
int NIMAGES = 0; 
// extended surf gives 128-dimensional vectors
const bool EXTENDED_SURF = false;

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
  testDatabase(features);
  time(&t4);
  cout << "BUILD DB:" << 1.0*(t4-t3)/3600 << "h" << endl;
  return 0;
}

void loadFeatures(vector<vector<vector<float> > > &features)
{
  features.clear();
  features.reserve(NIMAGES);

  cv::Ptr<cv::xfeatures2d::SURF> surf = cv::xfeatures2d::SURF::create(400, 4, 2, EXTENDED_SURF);

  cout << "Extracting SURF features..." << endl;
  
  ifstream infile;
  infile.open("images.txt");
  assert(infile.is_open());

  string path = "/home/microgroup/oxbuild_bow/oxbuild_images/";
  string s;
  int cnt = 0;
  
  while(getline(infile, s))
  {
    stringstream ss;
    ss << path << s;
    cout << "Current file: " << s << endl;
 
    ifstream imageFile;
    imageFile.open((path + s).c_str());
   
    clock_t stime, etime;

    stime = clock();

    cv::Mat image = cv::imread(ss.str(), 0);
    cv::Mat mask;
    vector<cv::KeyPoint> keypoints;
    vector<float> descriptors;

    surf->detectAndCompute(image, mask, keypoints, descriptors);

    features.push_back(vector<vector<float> >());
    changeStructure(descriptors, features.back(), surf->descriptorSize());
    
    etime = clock();
    cout << "Get SURF features: " << features.back().size() << endl;
    cout << "Time costs: " << (double) (etime - stime) / 1000.0 << "ms" << endl;
    NIMAGES++;
    //write to leveldb
   // db->Put(leveldb::WriteOptions(), s, feature2String(features.back()));
  }
}

// ---------------------------------------------------------------------------- 
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

// ----------------------------------------------------------------------------

void testVocCreation(const vector<vector<vector<float> > > &features)
{
  // branching factor and depth levels 
  const int k = 100;
  const int L = 3;
  const WeightingType weight = TF_IDF;
  const ScoringType score = L1_NORM;

  Surf64Vocabulary voc(k, L, weight, score);

  cout << "Creating a small " << k << "^" << L << " vocabulary..." << endl;
  voc.create(features);
  cout << "... done!" << endl;

  cout << "Vocabulary information: " << endl
  << voc << endl << endl;

/*
  // lets do something with this vocabulary
  cout << "matching images against themselves (0 low, 1 high): " << endl;
  bowvector v1, v2;
  for(int i = 0; i < nimages; i++)
  {
    voc.transform(features[i], v1);
    for(int j = 0; j < nimages; j++)
    {
      voc.transform(features[j], v2);
      double score = voc.score(v1, v2);
      cout << "image " << i << " vs image " << j << ": " << score << endl;
    }
  }

*/
  // save the vocabulary to disk
  cout << endl << "Saving vocabulary..." << endl;
  voc.save("100_100k_voc.yml.gz");
  cout << "Done" << endl;
}

// ----------------------------------------------------------------------------

void testDatabase(const vector<vector<vector<float> > > &features)
{
  cout << "Creating a small database..." << endl;

  // load the vocabulary from disk
  Surf64Vocabulary voc("100_100k_voc.yml.gz");
  
  Surf64Database db(voc, false, 0); // false = do not use direct index
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
  /*

  // and query the database
  cout << "Querying the database: " << endl;

  QueryResults ret;
  for(int i = 0; i < NIMAGES; i++)
  {
    db.query(features[i], ret, 10);

    // ret[0] is always the same image in this case, because we added it to the 
    // database. ret[1] is the second best match.

    cout << "Searching for Image " << i << ". " << ret << endl;
  }

  cout << endl;
  */

  // we can save the database. The created file includes the vocabulary
  // and the entries added
  cout << "Saving database..." << endl;
  db.save("100_100k_db.yml.gz");
  cout << "... done!" << endl;
 /*
  
  // once saved, we can load it again  
  cout << "Retrieving database once again..." << endl;
  Surf64Database db2("small_db.yml.gz");
  cout << "... done! This is: " << endl << db2 << endl;
 */
}

// ----------------------------------------------------------------------------
