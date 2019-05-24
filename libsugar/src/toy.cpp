#include <iostream>


int stateVariable;

extern "C" void initialize()
{
    stateVariable = 0;
}

extern "C" int getState()
{
    return stateVariable;
}

extern "C" void incrementState()
{
    stateVariable++;
}