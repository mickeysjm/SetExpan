# SetExpan: Corpus-based Set Expansion Framework


## Introduction

This is the source code for SetExpan framework developed for corpus-based set expansion (i.e., finding the "complete" set of entites belonging to the same semantic class based on a given corpus and a tiny set of seeds). 


## Usage

We provide the Linux version of SetExpan. Only a compiler supporting C++11 is needed to compile and run the code. 

## Corpus Input 

The input corpus of SetExpan framework should be put under folder "./data/<CorpusName>/". For each corpus, we require three files: 

* eidSkipgram2TFIDFStrength.txt: each line represents a tuple of (eid, skipgram, weight), seperated by tab. 
* eidCTypeStrengths.txt: each line represents a tuple of (eid, coarse-grained type, weight), seperated by tab. 
* entity2id.txt: each line represents a pair of (entityName, entityID), seperated by tab. 

NOTE: We calculate multiple (eid, context-feature) strengths in the raw input, the **last column** is the TF-IDF weight scaling reported in the paper. 

Some sample corpus are put on [Google Drive](https://drive.google.com/open?id=0B--ZKWD8ahE4TmhuMndURVlVaG8).

## Query Input

The input query of SetExpan framework can be put either under folder "./data/<CorpusName>/" or some other user specified path. If it's the later case, you need to explicitly give the query input path when running SetExpan. For each query, it can contain **MULTIPLE** queries for **ONE** target corpus. Each line of query input file represents one query. Each seed entity is given by its corresponding entity id, and for multi-seed queries, they are seperated by blank space. The last line of query input file is "EXIT". Here is an query input example:

```
53862 114149 99092
93219 53863 24981
53914 42708 114008
81511 121241 25297
108659 53805 45820
EXIT
```

Some sample queries are put on [Google Drive](https://drive.google.com/open?id=0B--ZKWD8ahE4TmhuMndURVlVaG8).


## Run

```
./main -corpus apr -concept laws -suffix test -K 60 -T 30 -alpha 0.7 -Q 150 -r 4
```

* -corpus, the name of corpus;
* -concept, the name of query;
* -suffix, the suffix used in outputfile name;
* -K, the expected size of output expanded set;
* -T, the number of ensemble batches used in entity selection;
* -alpha, the percentage of features to be sampled. alpha should fall in range (0,1);
* -Q, the number of selected context features in each iteration;
* -r, the threshold of a candidate entity's average rank. 

## Files in the folder

* /data/, the input folder of SetExpan, including both corpus input and query input;
* /result/, the output folder of SetExpan;
* /src-SetExpan/main.cpp, the main entrance of SetExpan;
* /src-SetExpan/singleSE.h, the source code of SetExpan;
* /src-SetExpan/utils/parameters.h, model parameters and input/output pathes for SetExpan. NOTE: You can explicitly change the input path of corpus here, if it's necessary. 


