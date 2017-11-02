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