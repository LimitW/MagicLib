/**
 * File: FCNN256.cpp
 * Date: November 2011
 * Author: Dorian Galvez-Lopez
 * Description: functions for Surf64 descriptors
 * License: see the LICENSE.txt file
 *
 */
 
#include <vector>
#include <string>
#include <sstream>

#include "FClass.h"
#include "FCNN256.h"

using namespace std;

namespace DBoW2 {

// --------------------------------------------------------------------------

void FCNN256::meanValue(const std::vector<FCNN256::pDescriptor> &descriptors, 
  FCNN256::TDescriptor &mean)
{
  mean.resize(0);
  mean.resize(FCNN256::L, 0);
  
  float s = descriptors.size();
  
  vector<FCNN256::pDescriptor>::const_iterator it;
  for(it = descriptors.begin(); it != descriptors.end(); ++it)
  {
    const FCNN256::TDescriptor &desc = **it;
    for(int i = 0; i < FCNN256::L; i += 4)
    {
      mean[i  ] += desc[i  ] / s;
      mean[i+1] += desc[i+1] / s;
      mean[i+2] += desc[i+2] / s;
      mean[i+3] += desc[i+3] / s;
    }
  }
}

// --------------------------------------------------------------------------
  
double FCNN256::distance(const FCNN256::TDescriptor &a, const FCNN256::TDescriptor &b)
{
  double sqd = 0.;
  for(int i = 0; i < FCNN256::L; i += 4)
  {
    sqd += (a[i  ] - b[i  ])*(a[i  ] - b[i  ]);
    sqd += (a[i+1] - b[i+1])*(a[i+1] - b[i+1]);
    sqd += (a[i+2] - b[i+2])*(a[i+2] - b[i+2]);
    sqd += (a[i+3] - b[i+3])*(a[i+3] - b[i+3]);
  }
  return sqd;
}

// --------------------------------------------------------------------------

std::string FCNN256::toString(const FCNN256::TDescriptor &a)
{
  stringstream ss;
  for(int i = 0; i < FCNN256::L; ++i)
  {
    ss << a[i] << " ";
  }
  return ss.str();
}

// --------------------------------------------------------------------------
  
void FCNN256::fromString(FCNN256::TDescriptor &a, const std::string &s)
{
  a.resize(FCNN256::L);
  
  stringstream ss(s);
  for(int i = 0; i < FCNN256::L; ++i)
  {
    ss >> a[i];
  }
}

// --------------------------------------------------------------------------

void FCNN256::toMat32F(const std::vector<TDescriptor> &descriptors, 
    cv::Mat &mat)
{
  if(descriptors.empty())
  {
    mat.release();
    return;
  }
  
  const int N = descriptors.size();
  const int L = FCNN256::L;
  
  mat.create(N, L, CV_32F);
  
  for(int i = 0; i < N; ++i)
  {
    const TDescriptor& desc = descriptors[i];
    float *p = mat.ptr<float>(i);
    for(int j = 0; j < L; ++j, ++p)
    {
      *p = desc[j];
    }
  } 
}

// --------------------------------------------------------------------------

} // namespace DBoW2

