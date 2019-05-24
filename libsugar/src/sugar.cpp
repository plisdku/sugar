#include <iostream>
#include <cstdint>
#include <cstdlib>
#include <stdexcept>

#include "stkcontrol.h"
#include "InstrumentBank.h"

#include "stk/RtAudio.h"

#include "stk/FileLoop.h"
#include "stk/FileWvOut.h"
#include "stk/Clarinet.h"
#include "stk/BlowHole.h"
#include "stk/Saxofony.h"
#include "stk/Flute.h"
#include "stk/Brass.h"
#include "stk/BlowBotl.h"
#include "stk/Bowed.h"
#include "stk/Plucked.h"
#include "stk/StifKarp.h"
#include "stk/Sitar.h"
#include "stk/Mandolin.h"
#include "stk/Rhodey.h"
#include "stk/Wurley.h"
#include "stk/TubeBell.h"
#include "stk/HevyMetl.h"
#include "stk/PercFlut.h"
#include "stk/BeeThree.h"
#include "stk/FMVoices.h"
#include "stk/VoicForm.h"
#include "stk/Moog.h"
#include "stk/Simple.h"
#include "stk/Drummer.h"
#include "stk/BandedWG.h"
#include "stk/Shakers.h"
#include "stk/ModalBar.h"
#include "stk/Mesh2D.h"
#include "stk/Resonate.h"
#include "stk/Whistle.h"

using namespace stk;

    // initialize();
    // blockUntilDone();
    // shutdown();

enum {kOn, kOff, kFreq, kStop};
struct Cmd
{
    int instr_;
    int type_;
    int time_;
    float arg0_;
    float arg1_;

    Cmd() : instr_(0), type_(kOn), time_(0), arg0_(0.0), arg1_(0.0)
    {
    }

    Cmd(int instrumentId, int type, int time, float arg0, float arg1) :
        instr_(instrumentId), type_(type), time_(time), arg0_(arg0), arg1_(arg1)
    {
    }

    static Cmd on(int instrumentId, int time, float freq, float amplitude)
    {
        return Cmd(instrumentId, kOn, time, freq, amplitude);
    }

    // static Cmd off(int instrumentId, int time, float amplitude)
    // {
    //     return Cmd(instrumentId, kOff, time, amplitude, 0.0);
    // }
    static Cmd off(int instrumentId, int time, float freq, float amplitude)
    {
        return Cmd(instrumentId, kOff, time, freq, amplitude);
    }

    // static Cmd frequency(int instrumentId, int time, float freq)
    // {
    //     return Cmd(instrumentId, kFreq, time, freq, 0.0);
    // }

    static Cmd stop(int time)
    {
        return Cmd(0, kStop, time, 0.0, 0.0);
    }
};

// std::vector<Instrmnt*> gInstruments;
std::vector<InstrumentBank*> gInstruments;
std::vector<Cmd> gCommands;
double gSampleRateHz;

void initialize(double sampleRateHz)
{
    Stk::showWarnings(true);
    Stk::setSampleRate(sampleRateHz);
    Stk::setRawwavePath("/Users/paul/Documents/Projects/Music/STK/stk/rawwaves/");

    // We have ten fingers... so we can play ten clarinets.  Right?
    // How about twenty?

    gSampleRateHz = sampleRateHz;
    gInstruments = std::vector<InstrumentBank*>();
    gInstruments.push_back(InstrumentBank::create<Clarinet>(20));
    gInstruments.push_back(InstrumentBank::create<Mandolin>(20, 196.0));
    gInstruments.push_back(InstrumentBank::create<Plucked>(20));
    gInstruments.push_back(InstrumentBank::create<Flute>(20, 260.0));

    gCommands = std::vector<Cmd>();
}


void shutdown()
{
    gCommands.clear();
    for (int ii = 0; ii < gInstruments.size(); ii++)
    {
        delete gInstruments[ii];
    }
    gInstruments.clear();
}


void pushOn(int instrumentId, int time, float freq, float amplitude)
{
    gCommands.push_back(Cmd::on(instrumentId, time, freq, amplitude));
}

void pushOff(int instrumentId, int time, float freq, float amplitude)
{
    gCommands.push_back(Cmd::off(instrumentId, time, freq, amplitude));
}

// void pushFreq(int instrumentId, int time, float freq)
// {
//     gCommands.push_back(Cmd::frequency(instrumentId, time, freq));
// }

void pushStop(int time)
{
    gCommands.push_back(Cmd::stop(time));
}

void writeWav(const char* fileName)
{
    FileWvOut outputFile;
    outputFile.openFile(fileName, 1, FileWrite::FILE_WAV, Stk::STK_SINT16);

    int iCmd = 0;

    int maxSamples = gSampleRateHz * 3600;
    bool isDone = false;
    for (int ii = 0; ii < maxSamples && !isDone; ii++)
    {
        // Handle command queue
        while (iCmd < gCommands.size() && ii >= gCommands[iCmd].time_)
        {
            const Cmd & cmd = gCommands[iCmd];
            // Instrmnt* instrument = gInstruments.at(cmd.instr_);

            if (cmd.instr_ < 0 || cmd.instr_ >= gInstruments.size())
            {
                throw std::runtime_error("Instrument index out of range");
            }

            InstrumentBank* instrument = gInstruments.at(cmd.instr_);

            switch (cmd.type_)
            {
                case kOn:
                    // std::cerr << "Command on.\n";
                    instrument->noteOn(cmd.arg0_, cmd.arg1_);
                    break;
                case kOff:
                    // std::cerr << "Command off.\n";
                    instrument->noteOff(cmd.arg0_, cmd.arg1_);
                    // instrument->noteOff(cmd.arg0_);
                    break;
                case kFreq:
                    // instrument->setFrequency(cmd.arg0_);
                    break;
                case kStop:
                    // std::cerr << "Command stop.\n";
                    isDone = true;
                    break;
                default:
                    break;
            }
            iCmd++;
        }

        StkFloat sum = 0.0;
        for (int ii = 0; ii < gInstruments.size(); ii++)
        {
            sum += gInstruments[ii]->tick();
        }
        outputFile.tick(sum);
    }

    outputFile.closeFile();
}

