import sys
import os
import re
import time
from math import log
from collections import defaultdict
from collections import Counter


def load_eid_map(filename):
  eid2name = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip().split('\t')
      eid2name[int(seg[1])] = seg[0]
  return eid2name

def calculate_TFIDF_strength(inputFileName, outputFileName):
  word_w_skipgram2strength = defaultdict()
  skipgram2wordcount = defaultdict(int) # number of words matched this skipgram
  skipgram2wordstrength = defaultdict(int) # total occurrence of words matched this skipgram

  entity_set = set()
  with open(inputFileName, 'r') as fin:
    for line in fin:
      seg = line.strip().split("\t")
      entity_set.add((seg[0], seg[1]))
      if ((seg[0],seg[1]),seg[2]) in word_w_skipgram2strength:
        print((seg[0],seg[1]),seg[2])
      word_w_skipgram2strength[((seg[0],seg[1]),seg[2])] = int(seg[3])
      skipgram2wordcount[seg[2]] += 1
      skipgram2wordstrength[seg[2]] += int(seg[3])

  W = len(entity_set) # vocabulary size
  with open(outputFileName,'w') as fout:
    for key in word_w_skipgram2strength.keys():
      X_w_s = word_w_skipgram2strength[key]
      skipgram = key[1]
      skipgram_w_wordCount = skipgram2wordcount[skipgram]
      skipgram_w_wordStrength = skipgram2wordstrength[skipgram]
      f_w_s_count = log(1+X_w_s) * (log(W) - log(skipgram_w_wordCount))
      f_w_s_strength = log(1+X_w_s) * (log(W) - log(skipgram_w_wordStrength)) # used in EgoSet
      fout.write(key[0][0]+"\t"+key[0][1]+"\t"+key[1]+"\t"+str(f_w_s_count)+"\t"+str(f_w_s_strength)+"\n")
  print('Completing calculating TFIDF....')

def calculateEidPairTFIDFs(data):
  folderPath = '../../data/'+data+'/'
  inputFileName = folderPath+'intermediate/eidPairSkipgramCounts.txt'
  outputFileName = folderPath+"intermediate/eidPairSkipgram2TFIDFStrength.txt"
  calculate_TFIDF_strength(inputFileName, outputFileName)

if __name__ == '__main__':
  calculateEidPairTFIDFs(sys.argv[1])
