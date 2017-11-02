'''
__author__: Jiaming Shen
__description__: Extract relational skipgrams from coropus
    Input: 1) sentences.json
    Output: 1) eidPairRelationSkipgramCounts.txt
__latest_update__: 08/31/2017
'''
import sys
import json
from collections import defaultdict

def getRelationalSkipgrams(tokens, start1, end1, start2, end2, window=5):
  # with assumption, there is no overlap between entity mentions
  # if the number of tokens between two entity mentions is less than the window size
  # we extract the relational skipgram for this tuple
  if (start1 - end2 > window) or (start2 - end1 > window):
    return []
  positions = [(-1, 1), (-2, 1), (-3, 1), (-1, 3), (-2, 2), (-1, 2)]
  relational_skipgrams = []
  max_len = len(tokens)
  for pos in positions:
    if start1 < start2:
      relational_skipgrams.append(' '.join(tokens[max(start1+pos[0],0):start1])+' __ '+' '.join(tokens[end1+1:start2])+' __ '+' '.join(tokens[end2+1:min(end2+1+pos[1], max_len)]))
  else:
    relational_skipgrams.append(' '.join(tokens[max(start2+pos[0],0):start2])+' __ '+' '.join(tokens[end2+1:start1])+' __ '+' '.join(tokens[end1+1:min(end1+1+pos[1], max_len)]))
  return relational_skipgrams

def extractRelationalSkipgrams(inputFileName):
  eidPairRelationalSkipgrams2Counts = defaultdict(int)
  cnt = 0
  with open(inputFileName, "r") as fin:
    for line in fin:
      cnt += 1
      if (cnt % 100000 == 0):
        print("Processed %s lines" % cnt)
      line = line.strip()
      sentInfo = json.loads(line)
      tokens = sentInfo['tokens']
      eid2positions = defaultdict(list)
      for em in sentInfo['entityMentions']:
        eid2positions[em['entityId']].append((em['start'],em['end']))
      for eid1 in eid2positions.keys():
        for eid2 in eid2positions.keys():
          if eid2 == eid1:
            continue
          for idx1 in eid2positions[eid1]:
            for idx2 in eid2positions[eid2]:
              relational_sgs = getRelationalSkipgrams(tokens, idx1[0], idx1[1], idx2[0], idx2[1])
              for relational_sg in relational_sgs:
                key = (eid1, eid2, relational_sg)
                eidPairRelationalSkipgrams2Counts[key] += 1
  return eidPairRelationalSkipgrams2Counts

def saveEidPairRelationalSkipgrams(res, outputFileName):
  with open(outputFileName, "w") as fout:
    for ele in res:
      fout.write(str(ele[0])+"\t"+str(ele[1])+"\t"+ele[2]+"\t"+str(res[ele])+"\n")


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print('Usage: extractRelationalSkipgrams.py -data')
    exit(1)
  corpusName = sys.argv[1]
  inputFileName = "../../data/"+corpusName+"/source/sentences.json"
  outputFileName = "../../data/"+corpusName+"/intermediate/eidPairRelationalSkipgramsCounts.txt"
  res = extractRelationalSkipgrams(inputFileName)
  saveEidPairRelationalSkipgrams(res, outputFileName)
