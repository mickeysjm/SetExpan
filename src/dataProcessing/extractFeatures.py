'''
__author__: Ellen Wu, Jiaming Shen
__description__: extract occurrence features for candidate entities
    Input: 1) the sentence.json
    Output: 1) eidSkipgramCounts.txt, 2) eidTypeCounts.txt, and 3) eidPairCounts.txt
__latest_updates__: 08/24/2017
'''
import sys
import json
import itertools

def getSkipgrams(tokens, start, end):
  positions = [(-1, 1), (-2, 1), (-3, 1), (-1, 3), (-2, 2), (-1, 2)]
  skipgrams = []
  for pos in positions:
    skipgrams.append(' '.join(tokens[start+pos[0]:start])+' __ '+' '.join(tokens[end+1:end+1+pos[1]]))
  return skipgrams


def processSentence(sent):
  sentInfo = json.loads(sent)
  eidSkipgrams = {}
  eidTypes = {}
  eidPairs = []
  tokens = sentInfo['tokens']
  eids = set()
  for em in sentInfo['entityMentions']:
    eid = em['entityId']

    typeList = em['type'].split(",")
    start = em['start']
    end = em['end']
    eids.add(eid)

    for type in typeList:
      key = (eid, type)
      if key in eidTypes:
        eidTypes[key] += 1
      else:
        eidTypes[key] = 1

    for skipgram in getSkipgrams(tokens, start, end):
      key = (eid, skipgram)
      if key in eidSkipgrams:
        eidSkipgrams[key] += 1
      else:
        eidSkipgrams[key] = 1

  for pair in itertools.combinations(eids, 2):
    eidPairs.append(frozenset(pair))
  return eidSkipgrams, eidTypes, eidPairs


def writeMapToFile(map, outFilename):
  with open(outFilename, 'w') as fout:
    for key in map:
      lkey = list(key)
      fout.write(str(lkey[0])+'\t'+str(lkey[1])+'\t'+str(map[key])+'\n')


def updateMapFromMap(fromMap, toMap):
  for key in fromMap:
    if key in toMap:
      toMap[key] += fromMap[key]
    else:
      toMap[key] = fromMap[key]
  return toMap


def updateMapFromList(fromList, toMap):
  for ele in fromList:
    if ele in toMap:
      toMap[ele] += 1
    else:
      toMap[ele] = 1
  return toMap


def extractFeatures(dataname):
  outputFolder = '../../data/'+dataname+'/intermediate/'
  infilename = '../../data/'+dataname+'/source/sentences.json'
  eidSkipgramCounts = {}
  eidTypeCounts = {}
  eidPairCounts = {}
  with open(infilename, 'r') as fin:
    ct = 0
    for line in fin:
      eidSkipgrams, eidTypes, eidPairs = processSentence(line)
      updateMapFromMap(eidSkipgrams, eidSkipgramCounts)
      updateMapFromMap(eidTypes, eidTypeCounts)
      updateMapFromList(eidPairs, eidPairCounts)
      ct += 1
      if ct % 100000 == 0 and ct != 0:
          print('processed ' + str(ct) + ' lines')

  writeMapToFile(eidSkipgramCounts, outputFolder+'eidSkipgramCounts.txt')
  writeMapToFile(eidTypeCounts, outputFolder+'eidTypeCounts.txt')
  writeMapToFile(eidPairCounts, outputFolder+'eidPairCounts.txt')

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print('Usage: extractFeatures.py -data')
    exit(1)
  corpusName = sys.argv[1]
  extractFeatures(corpusName)
