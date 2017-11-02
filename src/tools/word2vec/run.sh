#!/bin/bash

TEXT_DATA=../../../data/$1/intermediate/raw_text.txt
VECTOR_DATA=../../../data/$1/intermediate/entity_name_word2vec.emb

time ./bin/word2vec -train $TEXT_DATA -output $VECTOR_DATA -cbow 0 -size 100 -window 5 -negative 10 -hs 0 -sample 1e-3 -threads 20 -binary 0
