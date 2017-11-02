'''
__author__: Ellen Wu, Jiaming Shen
__description__: Map entity surface to entity id and filter entities with too small occurrences.
    Input: 1) eidXXXCounts.txt (XXX is the feature name such as "Skipgram", "Type")
    Output: 1) eidXXX2TFIDFStrength.txt (XXX is the same feature name in input file)
__latest_updates__: 08/31/2017
'''
import sys
import time
from math import log
from collections import defaultdict

def load_eid_map(filename):
    eid2name = {}
    with open(filename, 'r') as fin:
        for line in fin:
            seg = line.strip().split('\t')
            eid2name[int(seg[1])] = seg[0]
    return eid2name

def calculate_TFIDF_strength_new(inputFileName, outputFileName):
    eid_w_feature2count = defaultdict() # mapping between (eid, feature) -> count
    feature2eidcount = defaultdict(int) # number of distinct eids that match this feature
    feature2eidcountsum = defaultdict(int) # total occurrence of eids matched this feature

    eid_set = set()
    with open(inputFileName, "r") as fin:
        print("[INFO] Read in %s" % inputFileName)
        cnt = 0
        for line in fin:
            if cnt % 1000000 == 0 and cnt != 0:
                print("Processed %s of lines" % cnt)
            cnt += 1
            seg = line.strip().split("\t")
            eid = seg[0]
            feature = seg[1]
            count = int(seg[2])

            eid_set.add(eid)
            eid_w_feature2count[(eid, feature)] = count
            feature2eidcount[feature] += 1
            feature2eidcountsum[feature] += count

    ## Please refer to eq. (1) in http://mickeystroller.github.io/resources/ECMLPKDD2017.pdf
    print("[INFO] Start calculating TF-IDF strength")
    E = len(eid_set) # vocabulary size
    with open(outputFileName, "w") as fout:
        cnt = 0
        for key in eid_w_feature2count.keys():
            cnt += 1
            if cnt % 1000000 == 0:
                print("Processed %s of (eid, feature) pairs" % cnt)
            X_e_c = eid_w_feature2count[key]
            feature = key[1]
            f_e_c_count = log(1+X_e_c) * ( log(E) - log(feature2eidcount[feature]) )
            f_e_c_strength = log(1+X_e_c) * ( log(E) - log(feature2eidcountsum[feature]) ) # the one used in SetExpan

            fout.write(key[0]+"\t"+key[1]+"\t"+str(f_e_c_count)+"\t"+str(f_e_c_strength)+"\n")

def calculate_TFIDF_strength_pair(inputFileName, outputFileName):
  eidpair_w_feature2count = defaultdict()  # mapping between (eid, feature) -> count
  feature2eidpaircount = defaultdict(int)  # number of distinct eids that match this feature
  feature2eidpaircountsum = defaultdict(int)  # total occurrence of eids matched this feature

  eidpair_set = set()
  with open(inputFileName, "r") as fin:
    print("[INFO] Read in %s" % inputFileName)
    cnt = 0
    for line in fin:
      if cnt % 1000000 == 0 and cnt != 0:
        print("Processed %s of lines" % cnt)
      cnt += 1
      seg = line.strip().split("\t")
      eid1 = seg[0]
      eid2 = seg[1]
      eidpair = "_".join([eid1,eid2])
      feature = seg[2]
      count = int(seg[3])

      eidpair_set.add(eidpair)
      eidpair_w_feature2count[(eidpair, feature)] = count
      feature2eidpaircount[feature] += 1
      feature2eidpaircountsum[feature] += count

  ## Please refer to eq. (1) in http://mickeystroller.github.io/resources/ECMLPKDD2017.pdf
  print("[INFO] Start calculating TF-IDF strength")
  E = len(eidpair_set)  # vocabulary size
  with open(outputFileName, "w") as fout:
    cnt = 0
    for key in eidpair_w_feature2count.keys():
      cnt += 1
      if cnt % 1000000 == 0:
        print("Processed %s of (eid pair, feature) pairs" % cnt)
      X_e_c = eidpair_w_feature2count[key]
      feature = key[1]
      f_e_c_count = log(1 + X_e_c) * (log(E) - log(feature2eidpaircount[feature]))
      f_e_c_strength = log(1 + X_e_c) * (log(E) - log(feature2eidpaircountsum[feature]))  # the one used in SetExpan
      eid1, eid2 = key[0].split("_")
      fout.write(eid1 + "\t" + eid2 + "\t" + key[1] + "\t" + str(f_e_c_count) + "\t" + str(f_e_c_strength) + "\n")

## [Deprecated]
def calculate_TFIDF_strength(inputFileName, outputFileName):
    word_w_skipgram2strength = defaultdict()
    skipgram2wordcount = defaultdict(int) # number of words matched this skipgram
    skipgram2wordstrength = defaultdict(int) # total occurrence of words matched this skipgram

    entity_set = set()
    with open(inputFileName, 'r') as fin:
        print("Read in %s" % inputFileName)
        ct = 0
        for line in fin:
            if ct % 1000000 == 0 and ct != 0:
                print("Procsesed %s of lines" % ct)
            ct += 1
            seg = line.strip().split("\t")
            entity_set.add(seg[0])
            word_w_skipgram2strength[(seg[0],seg[1])] = float(seg[2])
            skipgram2wordcount[seg[1]] += 1
            skipgram2wordstrength[seg[1]] += float(seg[2])

    W = len(entity_set) # vocabulary size
    with open(outputFileName,'w') as fout:
        ct = 0
        for key in word_w_skipgram2strength.keys():
            if ct % 1000000 == 0 and ct != 0:
                print(ct)
            ct += 1
            X_w_s = word_w_skipgram2strength[key]
            skipgram = key[1]
            skipgram_w_wordCount = skipgram2wordcount[skipgram]
            skipgram_w_wordStrength = skipgram2wordstrength[skipgram]

            f_w_s_count = log(1+X_w_s) * (log(W) - log(skipgram_w_wordCount))
            f_w_s_strength = log(1+X_w_s) * (log(W) - log(skipgram_w_wordStrength)) # used in EgoSet

            fout.write(key[0]+"\t"+key[1]+"\t"+str(f_w_s_count)+"\t"+str(f_w_s_strength)+"\n")

def load_TFIDF_strength(inputFileName):
    start = time.time()
    eid2skipgram_w_strength = defaultdict(list)
    skipgram2eid_w_strength = defaultdict(list)
    with open(inputFileName,"r") as fin:
        for line in fin:
            seg = line.strip().split("\t")
            eid = int(seg[0])
            skipgram = seg[1]
            strength = float(seg[3]) # used in EgoSet
            # strength = float(seg[2]) # real tf-idf meaning

            eid2skipgram_w_strength[eid].append((skipgram, strength))
            skipgram2eid_w_strength[skipgram].append((eid,strength))

    end = time.time()
    print("Finish loading files, using time %s (seconds)" % (end-start))
    return eid2skipgram_w_strength, skipgram2eid_w_strength

### TODO: The following functions seems to be unused, check it later
def TFIDF_expansion(eid2skipgram_w_strength, skipgram2eid_w_strength, eid2name, seedset):

    start = time.time()

    TOPSG = 100
    TOPEN = 100
    FL = 3
    FH = 30

    skipgram2strength = defaultdict(float)
    for eid in seedset:
        skipgram_list = eid2skipgram_w_strength[eid] # (skipgram, strength)
        for pair in skipgram_list:
            skipgram = pair[0]
            strength = pair[1]
            skipgram2strength[skipgram] += strength

    ## Filter skipgram with low and high word frequency
    skipgram2strength_filtered = {}
    for skipgram in skipgram2strength:
        size = len(skipgram2eid_w_strength[skipgram])
        if size >= FL and size <= FH:
            skipgram2strength_filtered[skipgram] = skipgram2strength[skipgram]

    ## Select TOPSG skipgrams by descending strength
    topSG_w_strength = sorted(skipgram2strength_filtered.items(), key = lambda x:-x[1])[0:min(TOPSG, len(skipgram2strength_filtered))]
    for ele in topSG_w_strength:
        print(ele[0]+"\t"+str(ele[1]))

    ## Select TOPEN expaned entities
    entity2score = defaultdict(float)
    for topSGpair in topSG_w_strength:
        skipgram = topSGpair[0]
        sg_strength = topSGpair[1]

        for pair in skipgram2eid_w_strength[skipgram]:
            eid = pair[0]
            strength = pair[1]
            entity2score[eid] += strength
    topEN_w_strength = sorted(entity2score.items(), key = lambda x:-x[1])[0:min(TOPEN, len(entity2score))]
    for ele in topEN_w_strength:
        print(eid2name[ele[0]]+"\t"+str(ele[1]))


    end = time.time()
    print("Finish set expansion, using time %s (seconds)" % (end-start))


def main():
    corpusName = sys.argv[1]
    featureName = sys.argv[2]
    folder = '../../data/'+corpusName+'/intermediate/'
    inputFileName = folder+'eid'+featureName+'Counts.txt'
    outputFileName = folder+'eid'+featureName+'2TFIDFStrength.txt'
    if featureName.startswith("Pair"):
      calculate_TFIDF_strength_pair(inputFileName, outputFileName)
    else:
      calculate_TFIDF_strength_new(inputFileName, outputFileName)

    # inputMapName = "./entity2id-wpb.txt"
    # eid2name = load_eid_map(inputMapName)

    # inputFileName = "./eidSkipgramTFIDFStrength-wpb.txt"
    # eid2skipgram_w_strength, skipgram2eid_w_strength = load_TFIDF_strength(inputFileName)
    # eids = [49362, 12286]
    # TFIDF_expansion(eid2skipgram_w_strength, skipgram2eid_w_strength, eid2name, eids)

    # inputFileName = "./eid_w_metapad2TFIDFStrength-wpb.txt"
    # eid2skipgram_w_strength, skipgram2eid_w_strength = load_TFIDF_strength(inputFileName)
    # eids = [49362, 12286]
    # TFIDF_expansion(eid2skipgram_w_strength, skipgram2eid_w_strength, eid2name, eids)



if __name__ == '__main__':
    main()
