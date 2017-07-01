#ifndef __PARAMETERS_H__
#define __PARAMETERS_H__

#include "../utils/utils.h"

/*
Main parameters used in our model
*/
double PARAM_PATTERN_SET_SIZE_PERC = 0.7; // parameter "alpha" in paper
int PARAM_PATTERN_ENSEMBLE_TIMES = 60; // parameter "T" in paper
int PARAM_PATTERN_TOPK = 150; // parameter "Q" in paper
double PARAM_AVERAGE_RANK = 4; // parameter "r" in paper
int PARAM_EXPANDED_SIZE_K = 60; // expected size of expanded set

string corpusName = "apr";
string outputSuffix = "test"; 
string conceptSuffix = "laws";

// Input: 1) entity-context graph, 2) entity-type graph, 3) entity name map, 4) query file
string inFileName; 
string inTypeFeatureFileName;
string entityMapFileName;
string inputSeedFileName;

// Output: expansion results
string outputFileName;

/*
Other configurations used in our model
*/
int PARAM_PATTERN_DIVIERSITY_LOW = 2;
int PARAM_PATTERN_DIVIERSITY_HIGH = 30; 
int PARAM_ENTITY_TOPK = 5;
double PARAM_ENTITY_NEG_DISCOUNT = 1.0; // currently unused in our paper
double EPS = 1e-9;
double NEG_INF = -1e10;
bool FLAG_USE_TYPE = true; // Use Type information or not
bool FLAG_DEBUG = true; // Print out debugging information or not


inline void updateParameters()
{
    inFileName = "../data/"+corpusName+"/intermediate/eidSkipgram2TFIDFStrength.txt";
    inTypeFeatureFileName = "../data/"+corpusName+"/intermediate/eidCTypeStrengths.txt";
    entityMapFileName = "../data/"+corpusName+"/intermediate/entity2id.txt";
    inputSeedFileName = "../data/"+corpusName+"/source/query-"+conceptSuffix+".txt";
    outputFileName = "../result/"+corpusName+"/results-"+outputSuffix+".txt";
}

#endif
