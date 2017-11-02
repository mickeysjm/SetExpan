'''
__author__: Jiaming Shen, Ellen Wu
__description__: Python Implementation of SetExpan algorithm
__latest_update__: 08/28/2017
'''
import random
import math
import time
# SAMPLE_RATE is the number of context feature sample rate. 0.8 means 80% of core skipgram features
# will be selected in each ranking pass.
SAMPLE_RATE = 0.6
# TOP_K_SG is the maximum number of skipgrams that wil be selected to calculate the entity-entity
# distributional similarity.
TOP_K_SG = 200
# TOP_K_EID is the number of candidate entities that we considered to calculate mrr score during
# each ranking pass.
TOP_K_EID = 30
# MAX_ITER_SET is the maximum number of expansion iterations
MAX_ITER_SET = 10
# SAMPLES is the ensemble number
SAMPLES = 30
# THRES_MRR is the threshold that determines whether a new entity will be included in the set or not
THRES_MRR = SAMPLES * (1.0 / 5.0)
# Skipgrams with score >= (THRESHOLD * nOfSeedEids) will be retained
THRESHOLD = 0.0
# Skipgrams that can cover [FLAGS_SG_POPULARITY_LOWER, FLAGS_SG_POPULARITY_UPPER] numbers of entities will be
# retained
FLAGS_SG_POPULARITY_LOWER = 3
FLAGS_SG_POPULARITY_UPPER = 30
# FLAGS_TYPE_FLITER determines whether we filter candidate entities if their coreType is different from the
# coreType of the seedEids' set
FLAGS_TYPE_FLITER = False

def getSampledCoreSkipgrams(coreSkipgrams):
  sampledCoreSkipgrams = []
  for sg in coreSkipgrams:
    if random.random() <= SAMPLE_RATE:
      sampledCoreSkipgrams.append(sg)
  return sampledCoreSkipgrams

def getDominantType(eid, eid2types, eidAndType2strength):
  dominantType = None
  strength = -999
  for t in eid2types[eid]:
    if eidAndType2strength[(eid, t)] > strength:
      dominantType = t
      strength = eidAndType2strength[(eid, t)]

  if not dominantType:
    raise Exception("[WARNING] Unable to obtain dominantType for entity with id %s" % eid)
  return dominantType

def getCombinedWeightByFeatureMap(seedEids, featuresByEidMap, weightByEidAndFeatureMap):
  combinedWeightByFeatureMap = {}
  for seed in seedEids:
    featuresOfSeed = featuresByEidMap[seed]
    for sg in featuresOfSeed:
      if sg in combinedWeightByFeatureMap:
        combinedWeightByFeatureMap[sg] += weightByEidAndFeatureMap[(seed, sg)]
      else:
        combinedWeightByFeatureMap[sg] = weightByEidAndFeatureMap[(seed, sg)]

  return combinedWeightByFeatureMap

def getFeatureSim(eid, seed, weightByEidAndFeatureMap, features):
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
    # Weighted Jaccard similarity
    simWithSeed[0] += min(weight_eid, weight_seed)
    simWithSeed[1] += max(weight_eid, weight_seed)
  if simWithSeed[1] == 0:
    res = 0.0
  else:
    res = simWithSeed[0]*1.0/simWithSeed[1]
  return res

# expand the set of seedEntities and return eids by order, excluding seedEntities (original children)
def setExpan(seedEidsWithConfidence, negativeSeedEids, eid2patterns, pattern2eids, eidAndPattern2strength,
             eid2types, type2eids, eidAndType2strength, eid2ename, FLAGS_VERBOSE=False, FLAGS_DEBUG=False):
  ''' Note: currently the confidence score of each entity id is actually not used, just ignore it.

  :param seedEidsWithConfidence: a list of [eid (int), confidence_score (float)]
  :param negativeSeedEids: a set of eids (int) that should not be included
  :param eid2patterns:
  :param pattern2eids:
  :param eidAndPattern2strength:
  :param eid2types:
  :param type2eids:
  :param eidAndType2strength:
  :param eid2ename:

  :return: a list of expanded [eid (excluding the original input eids in seedEids), confidence_score]
  '''

  seedEids = [ele[0] for ele in seedEidsWithConfidence]
  eid2confidence = {ele[0]: ele[1] for ele in seedEidsWithConfidence}

  ## Cache the seedEids for later use
  cached_seedEids = set([ele for ele in seedEids])
  if FLAGS_VERBOSE:
    print('Seed set:')
    for eid in seedEids:
      print(eid, eid2ename[eid])
    print("[INFO] Start SetExpan")

  iters = 0
  while iters < MAX_ITER_SET:
    iters += 1
    prev_seeds = set(seedEids)
    start = time.time()
    # generate combined weight maps
    combinedWeightBySkipgramMap = getCombinedWeightByFeatureMap(seedEids, eid2patterns, eidAndPattern2strength)

    combinedWeightByTypeMap = getCombinedWeightByFeatureMap(seedEids, eid2types, eidAndType2strength)

    nOfSeedEids = len(seedEids)

    # pruning skipgrams which can match too few or too many eids
    redundantSkipgrams = set()
    for i in combinedWeightBySkipgramMap:
      size = len(pattern2eids[i])
      if size < FLAGS_SG_POPULARITY_LOWER or size > FLAGS_SG_POPULARITY_UPPER:
        redundantSkipgrams.add(i)

    for sg in redundantSkipgrams:
      del combinedWeightBySkipgramMap[sg]

    # get final core pattern features
    coreSkipgrams = []
    count = 0
    for sg in sorted(combinedWeightBySkipgramMap, key=combinedWeightBySkipgramMap.__getitem__, reverse=True):
      if count >= TOP_K_SG:
        break
      count += 1
      if combinedWeightBySkipgramMap[sg]*1.0/nOfSeedEids > THRESHOLD:
        coreSkipgrams.append(sg)

    # use type information select one type to filter candidates
    coreType = sorted(combinedWeightByTypeMap, key=combinedWeightByTypeMap.__getitem__, reverse=True)[0]
    end = time.time()
    print("[INFO] Finish context feature selection using time %s seconds" % (end - start))

    # terminate condition
    if len(coreSkipgrams) == 0:
      print("[INFO] Terminated due to no additional quality skipgrams at iteration %s" % iters)
      break

    # rank ensemble
    all_start = time.time()
    eid2mrr = {}
    if FLAGS_DEBUG:
      print("Start ranking ensemble at iteration %s:" % iters, end=" ")
    for i in range(SAMPLES):
      sampledCoreSkipgrams = getSampledCoreSkipgrams(coreSkipgrams)
      combinedSgSimByCandidateEid = {}
      candidates = set()

      for sg in sampledCoreSkipgrams:
        candidates = candidates.union(pattern2eids[sg])

      for eid in candidates:
        ## Directly filter entities with wrong type
        if FLAGS_TYPE_FLITER:
          if coreType != getDominantType(eid, eid2types, eidAndType2strength):
            continue
        combinedSgSimByCandidateEid[eid] = 0.0
        for seed in seedEids:
          combinedSgSimByCandidateEid[eid] += getFeatureSim(eid, seed, eidAndPattern2strength, sampledCoreSkipgrams)

      #get top k candidates
      count = 0
      for eid in sorted(combinedSgSimByCandidateEid, key=combinedSgSimByCandidateEid.__getitem__, reverse=True):
        if count >= TOP_K_EID:
          break

        if eid not in seedEids:
          count += 1
          if eid in eid2mrr:
            eid2mrr[eid] += 1.0 / count
          else:
            eid2mrr[eid] = 1.0 / count
    all_end = time.time()

    if FLAGS_DEBUG:
      print("End ranking ensemble at iteration %s" % iters)
      print("Totally using time %s seconds" % (all_end - all_start))

    # Select entities to be added into the set
    eid_incremental = []
    max_mrr = max(eid2mrr.values())
    for ele in sorted(eid2mrr.items(), key=lambda x:-x[1]):
      eid = ele[0]
      mrr_score = ele[1]
      if mrr_score < THRES_MRR:
        break
      if FLAGS_DEBUG:
        print("Add entity %s with normalized mrr score %s" % (eid2ename[eid], mrr_score / max_mrr))

      ## exclude negative seed eids, and calculate confidence score (currently not used)
      if eid not in negativeSeedEids:
        confidence_score = 0.0
        eid_incremental.append(eid)
        eid2confidence[eid] = confidence_score

    seedEids.extend(eid_incremental)

    # if nothing been added, stop
    if len(set(seedEids).difference(prev_seeds)) == 0 and len(prev_seeds.difference(set(seedEids))) == 0:
      print("[INFO] Terminated due to no additional quality entities at iteration %s" % iters)
      break

  if FLAGS_VERBOSE:
    print('[INFO] Finish SetExpan for one set')
    print('Expanded set:')

  expanded = []
  for eid in seedEids:
    if FLAGS_VERBOSE:
      print(eid, eid2ename[eid])
    if eid not in cached_seedEids:
      expanded.append([eid, eid2confidence[eid]])

  return expanded