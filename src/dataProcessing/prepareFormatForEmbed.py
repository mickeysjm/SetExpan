'''
__author__: Jiaming Shen, Ellen Wu
__description__: Given input corpus in JSON format, output
    1) [ew.txt] entity-context words pair with raw count
    2) [ee.txt] entity-entity sentence level co-occurrence with raw count
    3) [e.txt] a set of entity
    4) [w.txt] a set of context words
    The output files are exactly the input for LINE/PTE embedding codes
__latest_update__: 08/24/2017
'''
import sys
import json
import itertools
from collections import defaultdict

def getEid2EnameMap(inputFile):
    eid2ename = {}
    with open(inputFile,"r") as fin:
        for line in fin:
            line = line.strip()
            if line:
                segs = line.split("\t")
                eid = int(segs[1])
                ename = "_".join(segs[0].split())
                eid2ename[eid] = ename
    return eid2ename

def getContexts(tokens, start, end, winSize):
    res = []
    for t in tokens[max(0, start-winSize):start]:
        res.append(t.lower())
    for t in tokens[end+1:end+1+winSize]:
        res.append(t.lower())
    return res

# infname = sys.argv[1]
# ewfname = sys.argv[2]
# eefname = sys.argv[3]
# esetfname = sys.argv[4]
# wsetfname = sys.argv[5]
# winSize = int(sys.argv[6])

data=sys.argv[1]
infname = '../../data/'+data+'/source/sentences.json'
ewfname = '../../data/'+data+'/intermediate/ew.txt'
eefname = '../../data/'+data+'/intermediate/ee.txt'
esetfname = '../../data/'+data+'/intermediate/e.txt'
wsetfname = '../../data/'+data+'/intermediate/w.txt'
winSize = 5

eidContextCounts = defaultdict(int)
eidPair2Count = defaultdict(int)
eids = set()
contextWords = set()

inputEntityMapName = '../../data/'+data+'/intermediate/entity2id.txt'
eid2ename = getEid2EnameMap(inputEntityMapName)

with open(infname, 'r') as fin:
    line_cnt = 0
    for line in fin:
        line_cnt += 1
        if (line_cnt % 100000 == 0 and line_cnt != 0):
            print(line_cnt)

        sentInfo = json.loads(line.strip('\r\n'))
        tokens = sentInfo['tokens']
        eid_list = []
        for em in sentInfo['entityMentions']:
            eid = em['entityId']
            eid_list.append(eid)
            if eid not in eids:
                eids.add(eid)

            start = em['start']
            end = em['end']
            contexts = getContexts(tokens, start, end, winSize)
            if len(contexts) < 1:
                continue
            for c in contexts:
                if c not in contextWords:
                    contextWords.add(c)

                eidContextCounts[(eid,c)] += 1

        if len(eid_list) < 2:
            continue
        else:
            for eid_pair in itertools.combinations(eid_list,2):
                eidPair2Count[frozenset(eid_pair)] += 1

print("Finish parsing data")

with open(ewfname, "w") as fout:
    for k,v in eidContextCounts.items():
        fout.write(eid2ename[k[0]] + "\t" + k[1] + "\t" + str(v) + "\n")

with open(eefname, "w") as fout:
    for k,v in eidPair2Count.items():
        k2 = list(k)
        if len(k2) == 1: # self-co-occurrence
            continue
        fout.write(eid2ename[k2[0]] + "\t" + eid2ename[k2[1]] + "\t" + str(v) + "\n")

with open(esetfname, "w") as fout:
    for k in eids:
        fout.write(eid2ename[k] + "\n")

with open(wsetfname, "w") as fout:
    for k in contextWords:
        fout.write(str(k)+"\n")


