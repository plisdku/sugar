#include <iostream>
#include <cstdint>
#include <cmath>

#include "stkcontrol.h"

int main()
{
    std::cout << "Hello, world!\n";

    initialize(44100);

    // for (int nn = 0; nn < 100; nn++)
    // {
    //     pushOn(1, nn*20000, 440.0*(nn+1)/20.0, 0.5);

    //     if (nn > 3)
    //     {
    //         pushOff(1, nn*20000, 440.0*(nn-2)/20.0, 0.5);
    //     }
    // }

    for (int nn = 0; nn < 100; nn++)
    {
        pushOn(1, nn*20000, 440.0, ((nn+1)/100.0));
        // pushOff(1, nn*20000 + 10000, 440.0, 0.5);
    }
    // pushOn(1, 0, 440.0, 0.5);
    // pushOff(1, 22050, 440.0, 0.5);

    // pushOn(0, 0, 440.0, 0.25);
    // pushOn(1, 22050, 550.0, 1.0);
    // pushOff(0, 44100, 440.0, 0.5);
    // pushOff(1, 66150, 550.0, 1.0);
    pushStop(200000);

    writeWav("out.wav");
}
