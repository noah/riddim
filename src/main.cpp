#include <iostream>
#include "riddim.h"

int main() 
{
  Riddim riddim;
  riddim.read_playlist_file();
  std::cout << "=============================" << std::endl;
  riddim.print_playlist();
  std::cout << "=============================" << std::endl;
  riddim.print_headers();
  /* ifstream file('mp3/Live\ In\ 
  if(file.is_open()) 
  {} */

  return 0;
}
