#ifndef _STKTOY_
#define _STKTOY_

extern "C" void initialize(double sampleRateHz); // try 44100

extern "C" void pushOn(int instrumentId, int time, float freq, float amplitude);
extern "C" void pushOff(int instrumentId, int time, float freq, float amplitude);
// extern "C" void pushFreq(int instrumentId, int time, float freq);
extern "C" void pushStop(int time);

extern "C" void writeWav(const char* fileName);

extern "C" void shutdown();

#endif