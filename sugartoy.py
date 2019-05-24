import stkcontrol

stkcontrol.note(0, 0, 1.0, 50)
stkcontrol.note(1, 1, 1.0, 60)
stkcontrol.note(3, 2, 1.0, 70)
# stkcontrol.stop(4)
stkcontrol.write_wav("mywav.wav", 44100)