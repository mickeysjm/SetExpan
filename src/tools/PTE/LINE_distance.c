//  Copyright 2013 Google Inc. All Rights Reserved.
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.


/* 
Change the output format by Jiaming
Add in more explanation notes for later changing
*/
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <vector>
#include <unordered_map>
// #include <malloc.h>
#include <stdlib.h>
#include <sstream>
#include <iostream>
#include <fstream>



const long long max_size = 2000;         // max length of strings
const long long N = 40;                  // number of closest words that will be shown
const long long max_w = 50;              // max length of vocabulary entries

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

inline unordered_map<string, string> readEntityMap(const string &inputFileName)
{
    unordered_map<string, string> eid2ename;
    
    ifstream inFile;

    inFile.open(inputFileName);

    if(inFile.is_open()) {
        string line;
        string eid;
        string ename;
        char delim = '\t';
        while(inFile) 
        {
            getline(inFile, line);
            if(line.size() > 0) 
            {
                vector<string> segs = splitBy(line, delim);
                ename = segs[0];
                eid = segs[1];

                eid2ename[eid] = ename;
            }
        }
        inFile.close();
    } else {
        cout << "Cannot open file: " << inputFileName << endl;
    }
    return eid2ename;
}


int main(int argc, char **argv) {
	FILE *f;
	char st1[max_size];
	char bestw[N][max_size];
	char file_name[max_size], st[100][max_size];
	float dist, len, bestd[N], vec[max_size];
	long long words, size, a, b, c, d, cn, bi[100];
	char ch;
	float *M;
	char *vocab;
	if (argc < 2) {
		printf("Usage: ./LINE_distance <FILE>\nwhere FILE contains word projections in the BINARY FORMAT\n");
		return 0;
	}
	strcpy(file_name, argv[1]);
	f = fopen(file_name, "rb");
	// f = fopen(file_name, "r");
	if (f == NULL) {
		printf("Input file not found\n");
		return -1;
	}
	fscanf(f, "%lld", &words); // Number of vocabulary size
	fscanf(f, "%lld", &size); // Dimension of embedding


	vocab = (char *)malloc((long long)words * max_w * sizeof(char));
	M = (float *)malloc((long long)words * (long long)size * sizeof(float));
	if (M == NULL) {
		printf("Cannot allocate memory: %lld MB    %lld  %lld\n", (long long)words * size * sizeof(float) / 1048576, words, size);
		return -1;
	}
	for (b = 0; b < words; b++) {
		fscanf(f, "%s%c", &vocab[b * max_w], &ch); // first read the word-string
		for (a = 0; a < size; a++) fread(&M[a + b * size], sizeof(float), 1, f); // read each dimension of embedding
		len = 0;
		for (a = 0; a < size; a++) len += M[a + b * size] * M[a + b * size];
		len = sqrt(len);
		// When read in embedding, it already normalizated
		for (a = 0; a < size; a++) M[a + b * size] /= len;
	}
	fclose(f);
	printf("Finish loading the embedding files\n");


	// Read entity map
	string entityMapFileName = "/shared/data/jiaming/MultiSetExpansion/data_new/pubmed_cvd/intermediate/entity2id.txt";
	unordered_map<string, string> eid2ename = readEntityMap(entityMapFileName);

	// Calculate kNN
	while (1) {
		for (a = 0; a < N; a++) bestd[a] = 0;
		for (a = 0; a < N; a++) bestw[a][0] = 0;
		printf("Enter word or sentence (EXIT to break): ");
		a = 0;
		while (1) {
			st1[a] = fgetc(stdin);
			if ((st1[a] == '\n') || (a >= max_size - 1)) {
				st1[a] = 0;
				break;
			}
			a++;
		}

		if (!strcmp(st1, "EXIT")) break;  // if equal, strcmp return 0, stop

		cn = 0;
		b = 0;
		c = 0;
		while (1) {
			st[cn][b] = st1[c];
			b++;
			c++;
			st[cn][b] = 0;
			if (st1[c] == 0) break;
			if (st1[c] == ' ') {
				cn++;
				b = 0;
				c++;
			}
		}
		cn++;
		printf("Number of eids in query =%lld\n",cn);

		for (a = 0; a < cn; a++) { // cn number of words
			for (b = 0; b < words; b++) if (!strcmp(&vocab[b * max_w], st[a])) break;
			if (b == words) b = -1;
			bi[a] = b;
			string a_string(st[a]);
			string entityname = eid2ename[a_string];
			printf("\nEids: %s, Entity Name: %s,  Position in vocabulary: %lld\n", st[a], entityname.c_str(), bi[a]);
			if (b == -1) {
				printf("Out of dictionary word!\n");
				break;
			}
		}

		if (b == -1) continue;
		
		printf("\n       Eid                                 Entity Name        Cosine distance\n");
		printf("-------------------------------------------------------------------------------\n");
		// obtain the embedding of input query -- vec
		for (a = 0; a < size; a++) vec[a] = 0; 
		for (b = 0; b < cn; b++) { 
			if (bi[b] == -1) continue;
			for (a = 0; a < size; a++) vec[a] += M[a + bi[b] * size];
		}

		// normalization of query embedding vector
		len = 0;
		for (a = 0; a < size; a++) len += vec[a] * vec[a];
		len = sqrt(len); 
		for (a = 0; a < size; a++) vec[a] /= len;


		for (a = 0; a < N; a++) bestd[a] = 0;
		for (a = 0; a < N; a++) bestw[a][0] = 0;

		for (c = 0; c < words; c++) {
			a = 0;
			for (b = 0; b < cn; b++) if (bi[b] == c) a = 1; // filter those words that already in the seed query
			if (a == 1) continue;

			dist = 0;
			for (a = 0; a < size; a++) dist += vec[a] * M[a + c * size];
			
			for (a = 0; a < N; a++) {
				if (dist > bestd[a]) {
					for (d = N - 1; d > a; d--) {
						bestd[d] = bestd[d - 1];
						strcpy(bestw[d], bestw[d - 1]);
					}
					bestd[a] = dist;
					strcpy(bestw[a], &vocab[c * max_w]);
					break;
				}
			}
		}
		for (a = 0; a < N; a++) {
			string besteid_string(bestw[a]);
			string best_ename = eid2ename[besteid_string];
			printf("%10s    %40s        %f\n", bestw[a], best_ename.c_str(), bestd[a]);

		}
	}
	return 0;
}
