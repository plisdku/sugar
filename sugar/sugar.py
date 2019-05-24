import ctypes

# ctypes.cdll.LoadLibrary("build/libstkcontrol.dylib")
# _lib = ctypes.CDLL("build/libstkcontrol.dylib")
ctypes.cdll.LoadLibrary("/usr/local/lib/libstkcontrol.dylib")
_lib = ctypes.CDLL("/usr/local/lib/libstkcontrol.dylib")

# initialize(sampleRateHz)
_initialize = _lib.initialize
_initialize.argtypes = [ctypes.c_double]

# shutdown()
_shutdown = _lib.shutdown

# pushOn(id, time, frequency, amplitude)
_pushOn = _lib.pushOn
_pushOn.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.c_float]

# pushOff(id, time, frequency, amplitude)
_pushOff = _lib.pushOff
_pushOff.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.c_float]

# pushStop()
_pushStop = _lib.pushStop

# writeWav(fileName)
_writeWav = _lib.writeWav


class stk_command(object):

    def __init__(self, in_type, in_in_id, in_time, in_freq, in_ampl):
        self.type = in_type
        self.in_id = in_in_id
        self.time = in_time
        self.freq = in_freq
        self.ampl = in_ampl

_commands = []

def note(in_id, in_time_s, duration_s, midi=None, onset_ampl=0.5, offset_ampl = 0.5):

    freq = 440.0 * (2.0 ** ((midi-69)/12.0))

    _commands.append(stk_command("on", in_id, in_time_s, freq, onset_ampl))
    _commands.append(stk_command("off", in_id, in_time_s+duration_s, freq, offset_ampl))

def stop(in_time_s):
    _commands.append(stk_command("stop", 0, in_time_s, 440.0, 1.0))

def write_wav(fileName, sampleRateHz):
    global _commands

    sorted_commands = sorted(_commands, key=lambda x: x.time)

    if sorted_commands[-1].type != "stop":
        sorted_commands.append(stk_command("stop", 0, sorted_commands[-1].time + 4.0, 440.0, 1.0))

    # for ss in sorted_commands:
    #     print ss.time, ss.type, "in_id", ss.in_id, "freq", ss.freq, "ampl", ss.ampl

    _initialize(sampleRateHz)

        # in_id time freq ampl
    for ss in sorted_commands:
        if ss.type == "on":
            # print ss.time, int(ss.time * sampleRateHz)
            _pushOn(ss.in_id, int(ss.time * sampleRateHz), ss.freq, ss.ampl)
        elif ss.type == "off":
            # print int(ss.time * sampleRateHz)
            _pushOff(ss.in_id, int(ss.time * sampleRateHz), ss.freq, ss.ampl)
        elif ss.type == "stop":
            _pushStop(int(ss.time * sampleRateHz))

    _writeWav(fileName)

    _shutdown()

    _commands = []


instrument_names = ["clarinet", "mandolin", "plucked", "flute"]

