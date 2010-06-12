#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include "riddim.h"

Riddim::Riddim()
{
  port = PORT;
  current_line = 0;
}

void Riddim::read_playlist_file()
{
  std::string line;
  std::ifstream pl_file(PLAYLIST);
   
  if(pl_file.is_open())
  {
    for(int i=1;getline(pl_file,line); i++)
    {
      if(i > current_line)
      {
        playlist.push_back(line);
      }
    }
    pl_file.close();
  }
}

void Riddim::print_playlist()
{
  std::vector<std::string>::const_iterator i;
  for(i=playlist.begin(); i != playlist.end(); i++)
  {
    std::cout << *i << std::endl;
  }
}

void Riddim::print_headers()
{
  std::cout << "ICY 200 OK\n"
      "icy-notice1: <BR>Riddim<BR>\n"
      "icy-notice2: riddim-server<BR>\n"
      "icy-name: riddim on $hostname\n"
      "icy-genre: eclectic rock\n"
      "icy-url: http://github.com/noah/riddim\n"
      "content-type: audio/mpeg\n"
      "icy-pub: 1\n"
      "icy-br: 128\n"
      "\n" << std::endl;
}
