'''
__author__: Ellen Wu, Jiaming Shen
__description__: Map the embedding for entity surface name to entity eid
    If use PTE method learning embedding:
      Input: 1) entity_name.emb, 2) entity2id.txt
      Output: 1) entity.emb

    If use word2vec method learning embedding:
      Input: 1) entity_name_word2vec.emb
      Output: 1) entity_word2vec.emb

__latest_update__: 09/06/2017
'''
import sys
import re

def loadEidToEntityMap(filename):
    ename2eid = {}
    with open(filename, 'r') as fin:
        for line in fin:
            seg = line.strip('\r\n').split('\t')
            ename2eid[seg[0]] = int(seg[1])
    return ename2eid

corpusName=sys.argv[1]
embedMethodName=sys.argv[2]
if embedMethodName == "type":
    fname = '../../data/'+corpusName+'/intermediate/entity_name_type.emb'
    fname_out = '../../data/'+corpusName+'/intermediate/entity_type.emb'
elif embedMethodName == "PTE":
    fname = '../../data/'+corpusName+'/intermediate/entity_name.emb'
    fname_out = '../../data/' + corpusName + '/intermediate/entity.emb'
elif embedMethodName == "word2vec":
    fname = '../../data/' + corpusName + '/intermediate/entity_name_word2vec.emb'
    fname_out = '../../data/' + corpusName + '/intermediate/entity_word2vec.emb'
else:
    print("[ERROR] Unsupported embedding method")


mapFile = '../../data/'+corpusName+'/intermediate/entity2id.txt'
with open(fname, 'r') as fin, open(fname_out, 'w') as fout:
    ct = -1
    ename2eid = loadEidToEntityMap(mapFile)
    for line in fin:
        if ct == -1:
            ct += 1
            continue
        seg = line.strip('\r\n').split(' ')

        if embedMethodName == "PTE":
            if seg[0] in ename2eid:
                fout.write(' '.join([str(ename2eid[seg[0]])]+seg[1:])+'\n')
            elif seg[0].replace('_', ' ') in ename2eid:
                fout.write(' '.join([str(ename2eid[seg[0].replace('_', ' ')])]+seg[1:])+'\n')
            else:
                ct += 1
        elif embedMethodName == "word2vec":
            if re.match(r"^ENTITY(\d)+", seg[0]):
                fout.write(" ".join([seg[0][6:]]+seg[1:]) + "\n")
            else:
                ct += 1
    print(ct)
