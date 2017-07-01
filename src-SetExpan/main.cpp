#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unordered_map>
#include <unordered_set>

#include "utils/utils.h"
#include "utils/parameters.h"
#include "utils/commandline_flags.h"
#include "singleSE.h"

int main(int argc, char* argv[])
{

    /*
    1) Usage command :
    ./main -corpus apr -concept laws -suffix test -K 60 -T 30 -alpha 0.7 -Q 150 -r 4
    2) more parameters settings can be found in utils/parameters.h
    */
    parseCommandFlags(argc, argv);
    updateParameters();


    /*
    Loading corpus files
    */
    // read in eid2ename files
    unordered_map<int, string> eid2ename;
    unordered_map<string, int> ename2eid;
    eid2ename = readEntityMap(entityMapFileName);
    ename2eid = readEntityMap2(entityMapFileName);

    // read in entity-pattern strength files
    unordered_map<int, unordered_set<string> > eid2patterns;
    unordered_map<string, unordered_set<int> > pattern2eids;
    unordered_map<int, unordered_map<string, double> > eid2Pattern2Strength;

    time_t Start, End; 
    double dif;
    time (& Start);
    printf("Loading files\n");
    readEntityFeatureFile(inFileName, eid2patterns, pattern2eids, eid2Pattern2Strength);
    
    // read in entity-type strength files
    unordered_map<int, unordered_set<string> > eid2types;
    unordered_map<string, unordered_set<int> > type2eids;
    unordered_map<int, unordered_map<string, double> > eid2Type2Strength;
    if(FLAG_USE_TYPE) {
        readEntityTypeFeature(inTypeFeatureFileName, eid2types, type2eids, eid2Type2Strength);
    }
    time (& End);
    dif = difftime (End, Start);
    cout << "!!!Completed loading file in " << dif << " second(s)." << endl;

    // read in input queries
    vector<vector<int> > queries = readInQueries(inputSeedFileName);
    
    /*
    Start set expansion for each query
    */
    cout << "!!!Start query expansion" << endl;
    unordered_set<int> userInputSeeds;
    vector<int> seedEids;
    vector<vector<int> > expandedEntitiesMultiRound;
    vector<unordered_set<int> > userInputEntitiesMultiRound;


    int PARAM_NUMBER_OF_QUERY = queries.size();

    for(int i = 0; i < PARAM_NUMBER_OF_QUERY; i++)
    {
        userInputSeeds.insert(queries[i].begin(), queries[i].end());
        userInputEntitiesMultiRound.push_back(userInputSeeds);
        
        printf("Expanding query %d. Seeds = ", i+1);
        for(auto eid:userInputSeeds) {
            printf("(%d,%s) ", eid, eid2ename[eid].c_str());
        }
        printf("\n");

        expandSet(userInputSeeds, seedEids,
            eid2patterns, pattern2eids, eid2Pattern2Strength,
            eid2types, type2eids, eid2Type2Strength,
            FLAG_DEBUG, FLAG_USE_TYPE, eid2ename);

        expandedEntitiesMultiRound.push_back(seedEids);

        userInputSeeds.clear();
        seedEids.clear();
    }

    saveSEResultMulti(outputFileName, userInputEntitiesMultiRound,
        expandedEntitiesMultiRound, eid2ename);

    return 0;
}
