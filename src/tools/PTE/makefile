CC = g++
CFLAGS = -lm -pthread -Ofast -march=native -Wall -funroll-loops -Wno-unused-result -lgsl -lm -lgslcblas
INCLUDES = -I/usr/local/include -I/home/mengqu2/software/eigen-3.2.5
LIBS = -L/usr/local/lib


embed : ransampl.o linelib.o main.o
	$(CC) $(CFLAGS) -o embed ransampl.o linelib.o main.o $(INCLUDES) $(LIBS) -lgsl -lm -lgslcblas

ransampl.o : ransampl.c
	$(CC) $(CFLAGS) -c ransampl.c $(INCLUDES) $(LIBS) -lgsl -lm -lgslcblas

linelib.o : linelib.cpp ransampl.h
	$(CC) $(CFLAGS) -c linelib.cpp $(INCLUDES) $(LIBS) -lgsl -lm -lgslcblas

main.o : main.cpp linelib.o
	$(CC) $(CFLAGS) -c main.cpp $(INCLUDES) $(LIBS) -lgsl -lm -lgslcblas

clean :
	rm -rf *.o embed
