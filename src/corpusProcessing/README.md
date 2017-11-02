This folder contains scripts to generate input files for subsequent dataProcessing pipeline.

To run, simply change the corpus (data) name in corpusProcess.sh and run ./corpusProcess.sh

You need to start the stanford coreNLP server on localhost:9002 by following the [official guide](https://stanfordnlp.github.io/CoreNLP/corenlp-server.html#getting-started) and downloading its python wrapper library [pycorenlp](https://github.com/smilli/py-corenlp). 

You need to provide a raw txt source file: "../../data/{corpus name}/source/corpus.txt".