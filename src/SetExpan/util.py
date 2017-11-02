'''
__author__: Ellen Wu (modified by Jiaming Shen)
__description__: A bunch of utility functions
__latest_update__: 08/31/2017
'''
from collections import defaultdict
import set_expan
import eid_pair_TFIDF_selection
import extract_seed_edges
import extract_entity_pair_skipgrams

def loadEidToEntityMap(filename):
  eid2ename = {}
  ename2eid = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      eid2ename[int(seg[1])] = seg[0]
      ename2eid[seg[0].lower()] = int(seg[1])
  return eid2ename, ename2eid

def loadFeaturesAndEidMap(filename):
  featuresetByEid = defaultdict(set)
  eidsByFeature = defaultdict(set)
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      eid = int(seg[0])
      feature = seg[1]
      featuresetByEid[eid].add(feature)
      eidsByFeature[feature].add(eid)
  return featuresetByEid, eidsByFeature

def loadFeaturesAndEidPairMap(filename):
  featuresetByEidPair = defaultdict(set)
  eidPairsByFeature = defaultdict(set)
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      eidPair = (int(seg[0]), int(seg[1]))
      feature = seg[2]
      featuresetByEidPair[eidPair].add(feature)
      eidPairsByFeature[feature].add(eidPair)
  return featuresetByEidPair, eidPairsByFeature

def loadWeightByEidAndFeatureMap(filename, idx = -1):
  ''' Load the (eid, feature) -> strength

  :param filename:
  :param idx: The index column of weight, default is the last column
  :return:
  '''
  weightByEidAndFeatureMap = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      eid = int(seg[0])
      feature = seg[1]
      weight = float(seg[idx])
      weightByEidAndFeatureMap[(eid, feature)] = weight
  return weightByEidAndFeatureMap

def loadWeightByEidPairAndFeatureMap(filename, idx = -1):
  ''' Load the ((eid1, eid2), feature) -> strength

  :param filename:
  :param idx: The index column of weight, default is the last column
  :return:
  '''
  weightByEidPairAndFeatureMap = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      eidPair = (int(seg[0]), int(seg[1]))
      feature = seg[2]
      weight = float(seg[idx])
      weightByEidPairAndFeatureMap[(eidPair, feature)] = weight
  return weightByEidPairAndFeatureMap

def loadGroundTruthRelations(filename, header=False):
  '''

  :param filename: assume the input file contains 4 column, the first/third columns are entity string name
   the second/fourth columns are entity id
  :param header: if header = True, the first line is header
  :return: a set of tuple
  '''
  gt_relations = set()
  with open(filename, "r") as fin:
    for line in fin:
      line = line.strip()
      if header:
        header = False
        continue
      else:
        segs = line.split("\t")
        gt_relations.add((int(segs[1]), int(segs[3])))
  return gt_relations


def hasCausalRelationship(pathx, pathy):
  if len(pathx) > len(pathy):
    return False
  else:
    for i in range(len(pathx)-1):
      if pathx[i] != pathy[i]:
        return False
    if pathx[len(pathx)-1] > pathy[len(pathx)-1]:
      return False
    else:
      return True

def getCorelationToSet(node, eid2patterns, eidAndPattern2strength):
  nodeSet = set(node.parent.children)
  totalSim = 0.0
  for sibling in nodeSet:
    features = set(eid2patterns[node.eid]).union(set(eid2patterns[sibling.eid]))
    totalSim += set_expan.getFeatureSim(node.eid, sibling.eid, eidAndPattern2strength, features)
  return totalSim / len(nodeSet)

def getMostProbableNodeIdx(nodes, eid2patterns, eidAndPattern2strength):
  '''
  :param nodes: a list of TreeNode objects
  :param eid2patterns:
  :param eidAndPattern2strength:
  :return:
  '''
  ## Sanity checking
  assert len(nodes) > 0
  eid = nodes[0].eid
  for i in range(1, len(nodes)):
    assert nodes[i].eid == eid

  ## Rule 1: User is the big boss
  for i in range(len(nodes)):
    if nodes[i].isUserProvided:
      return i

  candidates = set(range(len(nodes)))
  treePaths = []
  for i in range(len(nodes)):
    node = nodes[i]
    path = []
    while node.parent != None:
      ## TODO: TreeNode object has default comparsion method?
      # path.append(node.parent.children.index(node))
      index = len(node.parent.children)
      for i in range(len(node.parent.children)):
        if node.parent.children[i].eid == node.eid:
          index = i
          break
      path.append(index)
      node = node.parent
    treePaths.append(list(reversed(path)))

  for i in range(len(nodes)):
    for j in range(len(nodes)):
      if i == j:
        continue
      ## TODO: double check such ordered examination way is reasonable. It seems that the node with smaller index
      ## is more preferred.
      if hasCausalRelationship(treePaths[i], treePaths[j]):
        candidates.discard(j)

  if len(candidates) == 0:
    raise Exception("[ERROR] No left candidate node after CasualRelationship filtering")
  else:
    max_cor = -100000000000
    max_cor_index = -1
    for c in candidates:
      # cor = getCorelationToSet(nodes[c], eid2patterns, eidAndPattern2strength)
      cor = nodes[c].confidence_score
      if cor > max_cor:
        max_cor_index = c
        max_cor = cor

    if max_cor_index == -1:
      raise Exception("[ERROR] Unable to find the node with maximal correlation score")
    else:
      return max_cor_index

def getSeedEntities(data, targetNode, sourceNode):
  parentSet = set(targetNode.parent.children)
  extract_entity_pair_skipgrams.extractEidPairSkipgrams(data, parentSet)
  eid_pair_TFIDF_selection.calculateEidPairTFIDFs(data)
  eid2ename, eidPair2patterns, patterns2eidPairs, eidAndPattern2strength, eid2types, type2eids, eidAndType2strength\
      = extract_seed_edges.loadAllEidPairMaps(data)
  seedEidPairs = [(sourceNode.eid, child.eid) for child in sourceNode.children[:10]]
  return extract_seed_edges.extractSeedEdges(data, targetNode.eid, seedEidPairs, eid2ename, eidPair2patterns, patterns2eidPairs, eidAndPattern2strength, eid2types, type2eids, eidAndType2strength)

