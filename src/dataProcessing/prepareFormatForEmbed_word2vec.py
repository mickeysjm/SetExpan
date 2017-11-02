'''
__author__: Jiaming Shen
__description__: Given input corpus in JSON format, output
    1)
    The output files are exactly the input for word2vec embedding codes
__latest_update__: 09/06/2017
'''
import json
import sys
import re

def processOneLine(sentInfo):
  tokens = sentInfo["tokens"]
  for entityMention in sentInfo["entityMentions"]:
    eid = entityMention["entityId"]
    start = entityMention["start"]
    end = entityMention["end"]
    for i in range(start, end + 1):
      tokens[i] = "ENTITY" + str(eid)
  sentence = " ".join(tokens)

  ## Replace continuous entity tokens with a single one
  sentence = re.sub(r"(ENTITY(\d+)\s*){2,}", r"\1", sentence)
  return sentence

if __name__ == "__main__":
  corpusName = sys.argv[1]
  inputFilePath = '../../data/' + corpusName + '/source/sentences.json'
  outputFilePath = "../../data/" + corpusName + "/intermediate/raw_text.txt"
  with open(inputFilePath, "r") as fin, open(outputFilePath, "w") as fout:
    cnt = 0
    for line in fin:
      cnt += 1
      if cnt % 100000 == 0:
        print("[INFO] Processed %s lines" % cnt)
      sentInfo = json.loads(line.strip())
      sentence = processOneLine(sentInfo)
      fout.write(sentence)
      fout.write("\n")