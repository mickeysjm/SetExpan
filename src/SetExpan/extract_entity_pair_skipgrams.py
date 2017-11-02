'''
__author__: Ellen Wu (modified by Jiaming Shen)
__description__: Extract relational skipgram
__latest_update__: 08/31/2017
'''
import json

def getRelationalSkipgrams(tokens, start1, end1, start2, end2, window=5):
  # with assumption, there is no overlap between entity mentions
  # if the number of tokens between two entity mentions is less than the window size
  # we extract the relational skipgram for this tuple
  # if ( (start1 > end2 and (start1 - end2 > window) ) or (start2 > end1 and (start2 - end1 > window) ) ):
  if (start1 - end2 > window) or (start2 - end1 > window):
    return []
  positions = [(-1, 1), (-2, 1), (-3, 1), (-1, 3), (-2, 2), (-1, 2)]
  relational_skipgrams = []
  max_len = len(tokens)
  for pos in positions:
    if start1 < start2:
      relational_skipgrams.append(' '.join(tokens[max(start1+pos[0],0):start1])+' __ '+' '.join(tokens[end1+1:start2])+' __ '+' '.join(tokens[end2+1:min(end2+1+pos[1], max_len-1)]))
  else:
    relational_skipgrams.append(' '.join(tokens[max(start2+pos[0],0):start2])+' __ '+' '.join(tokens[end2+1:start1])+' __ '+' '.join(tokens[end1+1:min(end1+1+pos[1], max_len-1)]))
  return relational_skipgrams

def processSentence(sent, testEids):
  sentInfo = json.loads(sent)
  testSkipgrams = {}
  eids = {}
  tokens = sentInfo['tokens']
  for em in sentInfo['entityMentions']:
    eid = em['entityId']
    start = em['start']
    end = em['end']
    if eid in eids:
      eids[eid].append((start, end))
    else:
      eids[eid] = [(start, end)]
  for testEid in testEids:
    if testEid in eids.keys():
      for em2 in eids.keys():
        if em2 != testEid:
          ## process one pair
          for idx1 in eids[testEid]:
            for idx2 in eids[em2]:
              ## obtain the skipgrams for this pair
              sgs = getRelationalSkipgrams(tokens, idx1[0], idx1[1], idx2[0], idx2[1])
              for sg in sgs:
                key = (testEid, em2, sg)
                if key in testSkipgrams:
                  testSkipgrams[key] +=1
                else:
                  testSkipgrams[key] = 1
  return testSkipgrams

def updateMapFromMap(fromMap, toMap):
  for key in fromMap:
    if key in toMap:
      toMap[key] += fromMap[key]
    else:
      toMap[key] = fromMap[key]
  return toMap

def getSeedEidPairs(filename):
  with open(filename, 'r') as fin:
    res = []
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      res.append((int(seg[0]), int(seg[1])))
  return res


# extract skipgrams for entity pairs and write to "eidPairSkipgramCounts.txt", in the same format as "eidSkipgramCounts.txt"
def extractEidPairSkipgrams(data, testEids):
  folderPath = '../../data/'+data+'/'
  infname = folderPath+'source/sentences.json'
  outfname = folderPath+'intermediate/eidPairSkipgramCounts.txt'
  allSkipgramCounts = {}
  with open(infname, 'r') as fin, open(outfname, 'w') as fout:
    for line in fin:
      allSkipgrams = processSentence(line.strip('\r\n'), testEids)
      allSkipgramCounts = updateMapFromMap(allSkipgrams, allSkipgramCounts)
    for key in allSkipgramCounts:
      fout.write(str(key[0])+'\t'+str(key[1])+'\t'+str(key[2])+'\t'+str(allSkipgramCounts[key])+'\n')
    print('Complete extracting skipgram features...')

if __name__ == '__main__':
  tokens = ["The", "band", "also", "shared", "membership", "with", "the", "similar", ",", "defunct", "group", "Out", "Hud", "(", "including", "Tyler", "Pope", ",", "who", "has", "played", "with", "LCD", "Soundsystem", "and", "written", "music", "for", "Cake", ")", "."]
  start1 = 22
  end1 = 23
  start2 = 28
  end2 = 28
  res = getRelationalSkipgrams(tokens, start1, end1, start2, end2)
  for ele in res:
    print(ele)