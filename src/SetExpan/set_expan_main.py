'''
__author__: Jiaming Shen, Ellen Wu
__description__: The main function for running SetExpan algorithm
__latest_update__: 10/12/2017
'''
import util
import set_expan
import time

## Setting global versions
FLAGS_USE_TYPE=True

## Loading Corpus
data = "wiki"
print('dataset:%s' % data)
folder = '../../data/'+data+'/intermediate/'
start = time.time()
print('loading eid and name maps')
eid2ename, ename2eid = util.loadEidToEntityMap(folder+'entity2id.txt') #entity2id.txt
print('loading eid and skipgram maps')
eid2patterns, pattern2eids = util.loadFeaturesAndEidMap(folder+'eidSkipgramCounts.txt') #eidSkipgramCount.txt
print('loading skipgram strength map')
eidAndPattern2strength = util.loadWeightByEidAndFeatureMap(folder+'eidSkipgram2TFIDFStrength.txt', idx=-1) #(eid, feature, weight) file
if (FLAGS_USE_TYPE):
  print('loading eid and type maps')
  eid2types, type2eids = util.loadFeaturesAndEidMap(folder+'eidTypeCounts.txt') #eidTypeCount.txt
  print('loading type strength map')
  eidAndType2strength = util.loadWeightByEidAndFeatureMap(folder+'eidType2TFIDFStrength.txt', idx=-1) #(eid, feature, weight) file
end = time.time()
print("Finish loading all dataset, using %s seconds" % (end-start))

## Start set expansion
userInput = ["United States", "China", "Japan", "germany", "England", "Russia", "India"]
seedEidsWithConfidence = [(ename2eid[ele.lower()], 0.0) for ele in userInput]

negativeSeedEids = set()
expandedEidsWithConfidence = set_expan.setExpan(
    seedEidsWithConfidence=seedEidsWithConfidence,
    negativeSeedEids=negativeSeedEids,
    eid2patterns=eid2patterns,
    pattern2eids=pattern2eids,
    eidAndPattern2strength=eidAndPattern2strength,
    eid2types=eid2types,
    type2eids=type2eids,
    eidAndType2strength=eidAndType2strength,
    eid2ename=eid2ename,
    FLAGS_VERBOSE=True,
    FLAGS_DEBUG=True
)
print("=== In test case ===")
for ele in expandedEidsWithConfidence:
  print("eid=", ele[0], "ename=", eid2ename[ele[0]])

with open("./setexpan_result.txt", "w") as fout:
  for ele in expandedEidsWithConfidence:
    fout.write("eid=" + str(ele[0]) + "\t" + "ename=" + eid2ename[ele[0]] + "\n")