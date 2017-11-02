'''
__author__: Ellen Wu, Jiaming Shen
__description__: generate entity count information
    Input: 1) the sentence.json.raw, 2) a map from unnormalized entity surface name to eid
    Output: 1) the a map file from entity surface name to its occurrence counts in corpus
__latest_updates__: 08/23/2017
'''
import sys
import json

data=sys.argv[1]
jsonfname = '../../data/'+data+'/source/sentences.json'
mapfname = '../../data/'+data+'/intermediate/entity2id.txt'
countfname = '../../data/'+data+'/intermediate/entityCount.txt'
with open(jsonfname, 'r') as jsonf, open(mapfname, 'r') as mapf, open(countfname, 'w') as countf:
    map = {}
    countMap = {}
    for line in mapf:
        seg = line.strip('\r\n').split('\t')
        map[int(seg[1])] = seg[0]
    for line in jsonf:
        sentinfo = json.loads(line)
        for em in sentinfo['entityMentions']:
            key = map[em['entityId']]
            if key in countMap:
                countMap[key] += 1
            else:
                countMap[key] = 1
    for k in sorted(countMap, key=countMap.__getitem__, reverse=True):
        countf.write(k+'\t'+str(countMap[k])+'\n')
