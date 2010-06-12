#include <vector>
#include "config.h"

#ifndef RIDDIM_H
#define RIDDIM_H

#endif
class Riddim {
  public:
        Riddim();
        void read_playlist_file();
        void print_playlist();
        void print_headers();
  private:
        int port;
        int current_line;
        std::vector<std::string> playlist;
};
