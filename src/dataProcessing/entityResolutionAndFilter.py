'''
__author__: Ellen Wu, Jiaming Shen
__description__: Map entity surface to entity id and filter entities with too small occurrences.
    Input: 1) entitylist (a list of raw entity mentions)
    Output: 1) a map between entity surface name to eid and 2) a list of eid
__latest_updates__: 08/23/2017
'''
from textblob import Word
from collections import defaultdict
import sys

def resolution(surfaceName):
    '''
    input: a surface name of entity
    output: the "normalized" entity name
    process: 1) lowercase
             2) lemmatization
    '''
    tmp = [Word(ele.lower()).lemmatize() for ele in surfaceName.split()]
    # tmp = [ele.lower() for ele in surfaceName.split()]
    return " ".join(tmp)

def main(corpusName, min_sup = -1):
    data = corpusName
    min_sup = int(min_sup)
    inputFileName = '../../data/'+data+'/intermediate/entitylist.txt'
    outputFileName = '../../data/'+data+'/intermediate/entity2id.txt'
    uniqueEntityNameFileOut = '../../data/'+data+'/intermediate/eidlist.txt'

    eid = 0
    ename2eid = {}
    normalized_ename2eid = {}
    normalized_ename2freq = defaultdict(int)
    with open(inputFileName,"r") as fin:
        for line in fin:
            segs = line.strip().split("\t")
            ename = segs[0]
            freq = int(segs[1])

            normalized_ename = resolution(ename)
            if normalized_ename in normalized_ename2eid: # already exist
                ename2eid[ename] = normalized_ename2eid[normalized_ename]
                normalized_ename2freq[normalized_ename] += freq
            else: # a new entity
                normalized_ename2eid[normalized_ename] = eid
                normalized_ename2freq[normalized_ename] += freq
                ename2eid[ename] = eid
                eid += 1

    print("Number of entities between (potential) filtering = %s" % eid)
    filtered_eid = set()
    if min_sup != -1:
        print("Filtering entities with too small occurrences")
        for ele in normalized_ename2freq.items():
            if ele[1] < min_sup:
                ## add the eid into the filtered set
                filtered_eid.add(normalized_ename2eid[ele[0]])
        print("Number of filtered entities = %s" % len(filtered_eid))

    with open(outputFileName,"w") as fout:
        for ele in sorted(ename2eid.items(), key = lambda x:x[0]):
            if ele[1] not in filtered_eid:
                fout.write(ele[0]+"\t"+str(ele[1])+"\n")

    with open(uniqueEntityNameFileOut,"w") as fout:
        for ele in sorted(normalized_ename2eid.items(), key = lambda x:x[1] ):
            if ele[1] not in filtered_eid:
                fout.write(ele[0]+"\t"+str(ele[1])+"\n")

if __name__ == '__main__':
    corpusName = sys.argv[1]
    min_sup = sys.argv[2]
    main(corpusName, min_sup)

