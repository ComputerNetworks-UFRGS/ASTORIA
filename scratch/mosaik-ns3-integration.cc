#include "ns3/ns3-simulation.h"
 
using namespace ns3;
 
 
int main (int argc, char *argv[]){
 
    Ns3Simulation *simulation;
    simulation = new Ns3Simulation();
     
    while(!simulation->finished);
    return 0;
}
