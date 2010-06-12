SRC_DIR=./src
BIN_DIR=./bin
OBJ_DIR=./obj
INC_DIR=./inc
LIB_DIR=./lib

INCLUDE = -I$(INC_DIR)

LIB = -L$(LIB_DIR)\
      -L/usr/lib

VPATH=$(INC_DIR):$(OBJ_DIR):$(SRC_DIR):$(LIB_DIR)
CXXFLAGS=$(INCLUDE) $(LIB) -pipe -fPIC -O2 -Wall

all: 		riddim main

riddim:		
		$(CXX) -c $(CXXFLAGS) $(SRC_DIR)/riddim.cpp -o $(OBJ_DIR)/riddim.o

main:		riddim
		$(CXX) $(CXXFLAGS) $(SRC_DIR)/main.cpp -o $(BIN_DIR)/riddim $(OBJ_DIR)/riddim.o
clean:
		rm $(OBJ_DIR)/*
		rm $(BIN_DIR)/*
