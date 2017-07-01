#ifndef __UTILS_H__
#define __UTILS_H__

#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <stdlib.h>
#include <cctype>
#include <cmath>
#include <ctime>
#include <cassert>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <string>
#include <vector>
#include <sstream>
#include <map>
#include <set>
#include <queue>
#include <unordered_map>
#include <unordered_set>

using namespace std;


inline vector<string> splitBy(const string &s, char delim) 
{
    vector<string> result;
    stringstream ss;
    ss.str(s);
    string item;
    while (getline(ss, item, delim)) {
        result.push_back(item);
    }
    return result;
}

template<class T>
inline bool compBySecondElementDesc(const pair<T, double> &a, const pair<T, double> &b ) 
{
    return a.second > b.second;
}

template<class T>
inline vector<pair<T, double> > sortMapByKey(const unordered_map<T, double> &a )
{
    vector<pair<T, double> > result(a.begin(), a.end());
    sort(result.begin(), result.end(), compBySecondElementDesc<T>);
    return result;
}

template<class T>
inline vector<pair<T, double> > selectTopKByKey(const unordered_map<T, double> &a, const int topK)
{
    vector<pair<T, double> > tmp(a.begin(), a.end());
    partial_sort(tmp.begin(), tmp.begin()+topK, tmp.end(), compBySecondElementDesc<T>);
    vector<pair<T, double> > result(tmp.begin(), tmp.begin()+topK);
    return result;
}

inline int randomSelectOneInt(const unordered_set<int> &s)
{
    return 0;
    // int r = rand() % s.size();
    // unordered_set<int>::iterator it(s.begin());
    // advance(it, r);
    // return *it;
}

inline pair<double, double> calculateMeanAndStddev(const vector<double> &v) {
    double sum = 0;
    for(auto ele:v) {sum += ele; }
    double m = sum / v.size();

    double accum = 0;
    for_each (v.begin(), v.end(), [&](const double d) {
        accum += ( d - m ) * ( d - m );
    });

    double stddev = sqrt(accum / v.size() );

    pair<double, double> result(m, stddev);
    return result;
};

inline vector<vector<int> > readInQueries(const string &inputFileName)
{
    vector<vector<int> > queries;
    ifstream inFile;

    inFile.open(inputFileName);

    if(inFile.is_open()) {
        string line;
        char delim = ' ';
        while(inFile)
        {
            getline(inFile, line);
            if(line.size() > 0 and line != "EXIT") 
            {
                vector<string> segs = splitBy(line, delim);
                vector<int> query;
                for(auto ele:segs) {
                    // printf("%s\n", ele.c_str());
                    query.push_back(stoi(ele));
                }
                queries.push_back(query);
            }
            else {
                break;
            }
        }
        inFile.close();
    } else {
        cout << "Cannot open file: " << inputFileName << endl;
    }
    return queries;
}

inline vector<int> readSeedPool(const string &inputFileName)
{
    vector<int> seedPool;

    ifstream inFile;

    inFile.open(inputFileName);

    if(inFile.is_open()) {
        string line;
        int eid;
        string ename;
        char delim = '\t';
        while(inFile) 
        {
            getline(inFile, line);
            if(line.size() > 0) 
            {
                vector<string> segs = splitBy(line, delim);
                eid = stoi(segs[0]);
                seedPool.push_back(eid);
            }
        }
        inFile.close();
    } else {
        cout << "Cannot open file: " << inputFileName << endl;
    }
    return seedPool;
}

inline vector<int> readSeedPool2(const string &inputFileName, unordered_map<string, int> &ename2eid)
{
    vector<int> seedPool;

    ifstream inFile;

    inFile.open(inputFileName);

    if(inFile.is_open()) {
        string line;
        string prev_line = "";
        int eid;
        string ename;
        // char delim = '\t';
        while(inFile) 
        {
            getline(inFile, line);
            if (line == prev_line) {break;}
            if(line.size() > 0) 
            {
                // cout << line << endl;
                ename = line;
                if(ename2eid.count(ename) > 0 ) {
                    eid = ename2eid[ename];
                } else {
                    cout << "Unable to find entity " << ename << endl;
                }
                seedPool.push_back(eid);
                prev_line = line;
            }
        }
        inFile.close();
    } else {
        cout << "Cannot open file: " << inputFileName << endl;
    }
    return seedPool;
}


inline unordered_map<int, string> readEntityMap(const string &inputFileName)
{
    unordered_map<int, string> eid2ename;
    
    ifstream inFile;

    inFile.open(inputFileName);

    if(inFile.is_open()) {
        string line;
        int eid;
        string ename;
        char delim = '\t';
        while(inFile) 
        {
            getline(inFile, line);
            if(line.size() > 0) 
            {
                vector<string> segs = splitBy(line, delim);
                ename = segs[0];
                eid = stoi(segs[1]);

                eid2ename[eid] = ename;
            }
        }
        inFile.close();
    } else {
        cout << "Cannot open file: " << inputFileName << endl;
    }
    return eid2ename;
}

inline unordered_map<string, int> readEntityMap2(const string &inputFileName)
{
    unordered_map<string, int> ename2eid;

    ifstream inFile;

    inFile.open(inputFileName);

    if(inFile.is_open()) {
        string line;
        int eid;
        string ename;
        char delim = '\t';
        while(inFile) 
        {
            getline(inFile, line);
            if(line.size() > 0) 
            {
                vector<string> segs = splitBy(line, delim);
                ename = segs[0];
                eid = stoi(segs[1]);

                ename2eid[ename] = eid;
            }
        }
        inFile.close();
    } else {
        cout << "Cannot open file: " << inputFileName << endl;
    }
    return ename2eid;
}

inline void saveResult(const string &outputFileName, vector<unordered_set<int> > &seed_entities, 
    const vector<vector<int> > &meb_entities, unordered_map<int, string> &eid2ename)
{
    ofstream outFile;
    outFile.open(outputFileName);

    if(outFile.is_open()) {
        // Writing seed first
        for(int i = 0; i < seed_entities.size(); i++) 
        {
            outFile << "Class " << i << " seeds: ";
            for(auto entity_id:seed_entities[i]) 
            {
                string entity_name = eid2ename[entity_id];
                outFile << "(" << entity_id << "," << entity_name << ") "; 
            }
            outFile << "\n";
        }

        outFile << "========================================\n";
        
        // Writing expanded entities in order
        for(int i = 0; i < meb_entities.size(); i++) 
        {
            outFile << "Class " << i << " entities: " << "\n";
            for(int j = 0; j < meb_entities[i].size(); j++) 
            {
                int entity_id = meb_entities[i][j];
                string entity_name = eid2ename[entity_id];
                outFile << entity_id << "\t" << entity_name << "\n"; 
            }
            outFile << "----------------------------------------\n";
        }
        outFile.close();

    } else {
        cout << "Could not write into file: " << outputFileName << endl;
    }

    cout << "Finish writing results to files!!!" << endl;
}

#endif
