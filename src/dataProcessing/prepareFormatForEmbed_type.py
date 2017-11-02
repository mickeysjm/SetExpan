'''
__author__: Jiaming Shen
__description__: Given input corpus in JSON format, output
    1) [et.txt] entity-type pair with raw count
    2) [t.txt] a set of types
    The output files are exactly the input for LINE/PTE embedding codes
'''
import sys
import json
import itertools
from collections import Counter
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

data=sys.argv[1]
#infname = '/shared/data/zeqiuwu1/fts-summer/data/'+data+'/source/sentences.json'
infname = '../../data/'+data+'/intermediate/eidTypeCounts.txt'
etfname = '../../data/'+data+'/intermediate/ef.txt'
tsetfname = '../../data/'+data+'/intermediate/f.txt'

eidTypeCounts = defaultdict(float)
typeSet = set()

inputEntityMapName = '../../data/'+data+'/intermediate/entity2id.txt'
eid2ename = getEid2EnameMap(inputEntityMapName)

with open(infname, 'r') as fin:
    line_cnt = 0
    for line in fin:
        seg = line.strip('\r\n').split('\t')
        eid = int(seg[0])
        t = seg[1]
        if t not in typeSet:
            typeSet.add(t)
        eidTypeCounts[(eid,t)] += float(seg[2])
    '''
    for line in fin:
        line_cnt += 1
        if (line_cnt % 100000 == 0 and line_cnt != 0):
            print(line_cnt)

        sentInfo = json.loads(line.strip('\r\n'))
        tokens = sentInfo['tokens']
        for em in sentInfo['entityMentions']:
            eid = em['entityId']
            types = em['type'].split(',')
            if len(types) < 1:
                continue
            for t in types:
                if t not in typeSet:
                    typeSet.add(t)

                eidTypeCounts[(eid,t)] += 1
    '''
print("Finish parsing data")

with open(etfname, "w") as fout:
    for k,v in eidTypeCounts.items():
        fout.write(eid2ename[k[0]] + "\t" + k[1] + "\t" + str(v) + "\n")

with open(tsetfname, "w") as fout:
    for k in typeSet:
        fout.write(str(k)+"\n")


