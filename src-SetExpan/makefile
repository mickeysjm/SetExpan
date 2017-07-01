CC = g++
# CC = /usr/local/bin/g++-6
CFLAGS = -std=c++11 -Wall -O3 -msse2

main : main.o
	$(CC) $(CFLAGS) -o main main.o

main.o: main.cpp ./utils/utils.h ./utils/parameters.h ./utils/commandline_flags.h ./singleSE.h
	$(CC) $(CFLAGS) -c main.cpp

clean:
	rm -rf *.o main





