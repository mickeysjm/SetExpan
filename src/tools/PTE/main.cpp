//  Copyright 2013 Google Inc. All Rights Reserved.
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
#include <gsl/gsl_rng.h>
#include "linelib.h"
#include "ransampl.h"

#define MAX_PATH_LENGTH 300

char node_file[MAX_STRING], label_file[MAX_STRING], link_file[MAX_STRING], output_file[MAX_STRING];
char data[MAX_STRING];
char file_path[MAX_STRING];
int binary = 0, num_threads = 1, vector_size = 100, negative = 5;
long long samples = 1, edge_count_actual;
real alpha = 0.025, starting_alpha;

const gsl_rng_type * gsl_T;
gsl_rng * gsl_r;

line_node node_w, node_c, node_e;//, node_t;
line_hin hin_ec, hin_ew;//, hin_et;
//line_adjacency adj;
line_trainer_line trainer_ec, trainer_ew;
//line_trainer_l1 trainer_et;

double func_rand_num()
{
    return gsl_rng_uniform(gsl_r);
}

void *training_thread(void *id)
{
    long long edge_count = 0, last_edge_count = 0;
    unsigned long long next_random = (long long)id;
    real *error_vec = (real *)calloc(vector_size, sizeof(real));
    
    while (1)
    {
        //judge for exit
        if (edge_count > samples / num_threads + 2) break;
        
        if (edge_count - last_edge_count > 1000)
        {
            edge_count_actual += edge_count - last_edge_count;
            last_edge_count = edge_count;
            printf("%cAlpha: %f Progress: %.3lf%%", 13, alpha, (real)edge_count_actual / (real)(samples + 1) * 100);
            fflush(stdout);
            alpha = starting_alpha * (1 - edge_count_actual / (real)(samples + 1));
            if (alpha < starting_alpha * 0.0001) alpha = starting_alpha * 0.0001;
        }
        
        trainer_ec.train_sample(alpha, negative, error_vec, func_rand_num, next_random);
        trainer_ew.train_sample(alpha, negative, error_vec, func_rand_num, next_random);
        trainer_ew.train_sample(alpha, negative, error_vec, func_rand_num, next_random);
        trainer_ew.train_sample(alpha, negative, error_vec, func_rand_num, next_random);
        trainer_ew.train_sample(alpha, negative, error_vec, func_rand_num, next_random);
        trainer_ew.train_sample(alpha, negative, error_vec, func_rand_num, next_random);

        edge_count += 6;
    }
    free(error_vec);
    pthread_exit(NULL);
}

void TrainModel() {
    long a;
    pthread_t *pt = (pthread_t *)malloc(num_threads * sizeof(pthread_t));
    starting_alpha = alpha;
    char file_name[MAX_STRING];
    
    gsl_rng_env_setup();
    gsl_T = gsl_rng_rand48;
    gsl_r = gsl_rng_alloc(gsl_T);
    gsl_rng_set(gsl_r, 314159265);
    sprintf(file_name, "%sw.txt", file_path);
    printf("start reading file: %s\n", file_name);
    node_w.init(file_name, vector_size);
    sprintf(file_name, "%se.txt", file_path);
    printf("start reading file: %s\n", file_name);
    node_c.init(file_name, vector_size);
    node_e.init(file_name, vector_size);

    
    sprintf(file_name, "%see.txt", file_path);
    hin_ec.init(file_name, &node_e, &node_c, 0);
    sprintf(file_name, "%sew.txt", file_path);
    hin_ew.init(file_name, &node_e, &node_w, 0);

    trainer_ew.init(&hin_ew, 0);
    trainer_ec.init(&hin_ec, 0);

    clock_t start = clock();
    printf("Training:");
    for (a = 0; a < num_threads; a++) pthread_create(&pt[a], NULL, training_thread, (void *)a);
    for (a = 0; a < num_threads; a++) pthread_join(pt[a], NULL);
    printf("\n");
    clock_t finish = clock();
    printf("Total time: %lf\n", (double)(finish - start) / CLOCKS_PER_SEC);
    
    sprintf(file_name, "%sfeature_name.emb", file_path);
    node_w.output(file_name, binary);
    sprintf(file_name, "%sentity_name.emb", file_path);
    node_e.output(file_name, binary);
}

int ArgPos(char *str, int argc, char **argv) {
    int a;
    for (a = 1; a < argc; a++) if (!strcmp(str, argv[a])) {
        if (a == argc - 1) {
            printf("Argument missing for %s\n", str);
            exit(1);
        }
        return a;
    }
    return -1;
}

int main(int argc, char **argv) {
    int i;
    if (argc == 1) {
        printf("HIN2VEC\n\n");
        printf("Options:\n");
        printf("Parameters for training:\n");
        printf("\t-node <file>\n");
        printf("\t\tA dictionary of all nodes\n");
        printf("\t-link <file>\n");
        printf("\t\tAll links between nodes. Links are directed.\n");
        printf("\t-path <int>\n");
        printf("\t\tAll meta-paths. One path per line.\n");
        printf("\t-output <int>\n");
        printf("\t\tThe output file.\n");
        printf("\t-binary <int>\n");
        printf("\t\tSave the resulting vectors in binary moded; default is 0 (off)\n");
        printf("\t-size <int>\n");
        printf("\t\tSet size of word vectors; default is 100\n");
        printf("\t-negative <int>\n");
        printf("\t\tNumber of negative examples; default is 5, common values are 5 - 10 (0 = not used)\n");
        printf("\t-samples <int>\n");
        printf("\t\tSet the number of training samples as <int>Million\n");
        printf("\t-iters <int>\n");
        printf("\t\tSet the number of interations.\n");
        printf("\t-threads <int>\n");
        printf("\t\tUse <int> threads (default 1)\n");
        printf("\t-alpha <float>\n");
        printf("\t\tSet the starting learning rate; default is 0.025\n");
        printf("\nExamples:\n");
        printf("./hin2vec -node node.txt -link link.txt -path path.txt -output vec.emb -binary 1 -size 100 -negative 5 -samples 5 -iters 20 -threads 12\n\n");
        return 0;
    }
    output_file[0] = 0;
    if ((i = ArgPos((char *)"-output", argc, argv)) > 0) strcpy(output_file, argv[i + 1]);
    if ((i = ArgPos((char *)"-binary", argc, argv)) > 0) binary = atoi(argv[i + 1]);
    if ((i = ArgPos((char *)"-size", argc, argv)) > 0) vector_size = atoi(argv[i + 1]);
    if ((i = ArgPos((char *)"-negative", argc, argv)) > 0) negative = atoi(argv[i + 1]);
    if ((i = ArgPos((char *)"-samples", argc, argv)) > 0) samples = (long long)(atof(argv[i + 1])*1000000);
    if ((i = ArgPos((char *)"-alpha", argc, argv)) > 0) alpha = atof(argv[i + 1]);
    if ((i = ArgPos((char *)"-threads", argc, argv)) > 0) num_threads = atoi(argv[i + 1]);
    if ((i = ArgPos((char *)"-data", argc, argv)) > 0) strcpy(data, argv[i + 1]);
    sprintf(file_path, "../../../data/%s/intermediate/", data);
    printf(file_path);
    TrainModel();
    return 0;
}
