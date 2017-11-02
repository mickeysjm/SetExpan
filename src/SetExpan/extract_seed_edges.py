import sys

def loadEidToEntityMap(filename):
  map = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      map[int(seg[1])] = seg[0]
  return map

def loadFeaturesAndEidPairMap(filename):
  featuresetByEidPair = {}
  eidPairsByFeature = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      eidPair = (int(seg[0]), int(seg[1]))
      feature = seg[2]
      if eidPair not in featuresetByEidPair:
        featuresetByEidPair[eidPair] = set([feature])
      else:
        featureset = featuresetByEidPair[eidPair]
        featureset.add(feature)
        featuresetByEidPair[eidPair] = featureset
      if feature not in eidPairsByFeature:
        eidPairsByFeature[feature] = set([eidPair])
      else:
        eidPairSet = eidPairsByFeature[feature]
        eidPairSet.add(eidPair)
        eidPairsByFeature[feature] = eidPairSet
  return featuresetByEidPair, eidPairsByFeature

def loadWeightByEidPairAndFeatureMap(filename):
  weightByEidPairAndFeatureMap = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      eidPair = (int(seg[0]), int(seg[1]))
      feature = seg[2]
      weight = float(seg[4])
      weightByEidPairAndFeatureMap[(eidPair, feature)] = weight
  return weightByEidPairAndFeatureMap

def getCombinedWeightByFeatureMap(seedEidPairs, featuresByEidPairMap, weightByEidPairAndFeatureMap):
  combinedWeightByFeatureMap = {}
  for seedPair in seedEidPairs:
    if seedPair not in featuresByEidPairMap:
      continue
    featuresOfSeedPair = featuresByEidPairMap[seedPair]
    for sg in featuresOfSeedPair:
      increment = 0
      if (seedPair, sg) in weightByEidPairAndFeatureMap:
        increment = weightByEidPairAndFeatureMap[(seedPair, sg)]
      if sg in combinedWeightByFeatureMap:
        combinedWeightByFeatureMap[sg] += increment
      else:
        combinedWeightByFeatureMap[sg] = increment

  return combinedWeightByFeatureMap

def getFeatureSim(eidPair, seed, weightByEidPairAndFeatureMap, features, dpMap=None):
  key = frozenset([eidPair, seed])
  if dpMap is not None:
    if key in dpMap:
      return dpMap[key], dpMap
  simWithSeed = [0.0, 0.0]
  for f in features:
    if (eidPair, f) in weightByEidPairAndFeatureMap:
      weight_eidPair = weightByEidPairAndFeatureMap[(eidPair, f)]
    else:
      weight_eidPair = 0.0
    if (seed, f) in weightByEidPairAndFeatureMap:
      weight_seed = weightByEidPairAndFeatureMap[(seed, f)]
    else:
      weight_seed = 0.0
    # Jaccard similarity
    simWithSeed[0] += min(weight_eidPair, weight_seed)
    simWithSeed[1] += max(weight_eidPair, weight_seed)
  res = simWithSeed[0]*1.0/simWithSeed[1]
  if dpMap is not None:
    dpMap[key] = res
    return res, dpMap
  else:
    return res


def loadFeaturesAndEidMap(filename):
  featuresetByEid = {}
  eidsByFeature = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      eid = int(seg[0])
      feature = seg[1]
      if eid not in featuresetByEid:
        featuresetByEid[eid] = set([feature])
      else:
        featureset = featuresetByEid[eid]
        featureset.add(feature)
        featuresetByEid[eid] = featureset
      if feature not in eidsByFeature:
        eidsByFeature[feature] = set([eid])
      else:
        eidSet = eidsByFeature[feature]
        eidSet.add(eid)
        eidsByFeature[feature] = eidSet
  return featuresetByEid, eidsByFeature

def loadWeightByEidAndFeatureMap(filename):
  weightByEidAndFeatureMap = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      eid = int(seg[0])
      feature = seg[1]
      weight = float(seg[3])
      weightByEidAndFeatureMap[(eid, feature)] = weight
  return weightByEidAndFeatureMap

def getCombinedWeightByFeatureMap_eid(seedEids, featuresByEidMap, weightByEidAndFeatureMap):
  combinedWeightByFeatureMap = {}
  for seed in seedEids:
    featuresOfSeed = featuresByEidMap[seed]
    for sg in featuresOfSeed:
      if sg in combinedWeightByFeatureMap:
        combinedWeightByFeatureMap[sg] += weightByEidAndFeatureMap[(seed, sg)]
      else:
        combinedWeightByFeatureMap[sg] = weightByEidAndFeatureMap[(seed, sg)]
  return combinedWeightByFeatureMap

def getFeatureSim_eid(eid, seed, weightByEidAndFeatureMap, features, dpMap=None):
  key = frozenset([eid, seed])
  if dpMap is not None:
    if key in dpMap:
      return dpMap[key], dpMap
  simWithSeed = [0.0, 0.0]
  for f in features:
    if (eid, f) in weightByEidAndFeatureMap:
      weight_eid = weightByEidAndFeatureMap[(eid, f)]
    else:
      weight_eid = 0.0
    if (seed, f) in weightByEidAndFeatureMap:
      weight_seed = weightByEidAndFeatureMap[(seed, f)]
    else:
      weight_seed = 0.0
    # Jaccard similarity
    simWithSeed[0] += min(weight_eid, weight_seed)
    simWithSeed[1] += max(weight_eid, weight_seed)
  if simWithSeed[1] == 0:
    res = 0
  else:
    res = simWithSeed[0]*1.0/simWithSeed[1]
  if dpMap is not None:
    dpMap[key] = res
    return res, dpMap
  else:
    return res

#initialize

def loadAllEidPairMaps(data):
  folderPath = '../../data/'+data+'/intermediate/'

  print('loading eidToEntityMap...')
  eidToEntityMap = loadEidToEntityMap(folderPath+'entity2id.txt') #entity2id.txt

  print('loading skipgramsByEidMap, eidsBySkipgramMap...')
  skipgramsByEidPairMap, eidPairsBySkipgramMap = loadFeaturesAndEidPairMap(folderPath+'eidPairSkipgramCounts.txt') #eidPairSkipgramCount.txt
  print('loading weightByEidAndSkipgramMap...')
  weightByEidPairAndSkipgramMap = loadWeightByEidPairAndFeatureMap(folderPath+'eidPairSkipgram2TFIDFStrength.txt') #(eid1, eid2, feature, weight) file

  print('loading typesByEidMap, eidsByTypeMap...')
  typesByEidMap, eidsByTypeMap = loadFeaturesAndEidMap(folderPath+'eidTypeCounts.txt') #eidTypeCount.txt
  print('loading weightByEidAndTypeMap...')
  weightByEidAndTypeMap = loadWeightByEidAndFeatureMap(folderPath+'eidType2TFIDFStrength.txt') #(eid, feature, weight) file

  return eidToEntityMap, skipgramsByEidPairMap, eidPairsBySkipgramMap, weightByEidPairAndSkipgramMap, typesByEidMap, eidsByTypeMap, weightByEidAndTypeMap



def extractSeedEdges(data, targetEid, seedEidPairs, eidToEntityMap, skipgramsByEidPairMap, eidPairsBySkipgramMap, weightByEidPairAndSkipgramMap, typesByEidMap, eidsByTypeMap, weightByEidAndTypeMap):
  print('targetEid: ', targetEid)
  folderPath = '../../data/'+data+'/intermediate/'
  threshold = 2 #tunable
  combinedWeightBySkipgramMap = getCombinedWeightByFeatureMap(seedEidPairs, skipgramsByEidPairMap, weightByEidPairAndSkipgramMap)
  eids = [eidPair[1] for eidPair in seedEidPairs]
  print(eids)
  combinedWeightByTypeMap = getCombinedWeightByFeatureMap_eid(eids, typesByEidMap, weightByEidAndTypeMap)
  #pruning pattern features
  redundantSkipgrams = set()
  for i in combinedWeightBySkipgramMap:
    size = len(eidPairsBySkipgramMap[i])
    if size < 3 or size > 100:
      redundantSkipgrams.add(i)
  for sg in redundantSkipgrams:
    del combinedWeightBySkipgramMap[sg]
  #get final pattern features
  coreSkipgrams = []
  print(len(combinedWeightBySkipgramMap))
  k = 100
  count = 0
  nOfSeedEidPairs = len(seedEidPairs)
  for sg in sorted(combinedWeightBySkipgramMap, key=combinedWeightBySkipgramMap.__getitem__, reverse=True):
    if count >= k:
      break
    count += 1
    if combinedWeightBySkipgramMap[sg]*1.0/nOfSeedEidPairs > threshold:
      coreSkipgrams.append(sg)
  print(len(coreSkipgrams))

  coreTypes = []
  k = 10
  count = 0
  for ty in sorted(combinedWeightByTypeMap, key=combinedWeightByTypeMap.__getitem__, reverse=True):
    if count >= k:
      break
    count += 1
    if combinedWeightByTypeMap[ty]*1.0/nOfSeedEidPairs > 0:
      coreTypes.append(ty)

  combinedSgSimByCandidateEidPair = {}
  combinedTySimByCandidateEidPair = {}
  combinedSimByCandidateEidPair = {}
  candidates = set()
  for sg in coreSkipgrams:
    candidates = candidates.union(eidPairsBySkipgramMap[sg])
  print("num of candidates: ", len(candidates))
  for eidPair in candidates:
    combinedSgSimByCandidateEidPair[eidPair] = 0.0
    combinedTySimByCandidateEidPair[eidPair] = 0.0
    for seed in seedEidPairs:
      #print(seed)
      combinedSgSimByCandidateEidPair[eidPair] += getFeatureSim(eidPair, seed, weightByEidPairAndSkipgramMap, coreSkipgrams)
      combinedTySimByCandidateEidPair[eidPair] += getFeatureSim_eid(eidPair[1], seed[1], weightByEidAndTypeMap, coreTypes)
    combinedSimByCandidateEidPair[eidPair] = combinedSgSimByCandidateEidPair[eidPair]+combinedTySimByCandidateEidPair[eidPair]*1.0

  #get top k candidates for seed set of next iteration
  k = 3
  count = 0
  returnList = []
  for pair in sorted(combinedSimByCandidateEidPair, key=combinedSimByCandidateEidPair.__getitem__, reverse=True):
    if count >= k:
      break
    else:
      if pair[0] != targetEid:
        continue
      returnList.append(str(pair[1]))
      count += 1
  return returnList


