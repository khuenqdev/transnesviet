#!/usr/bin/env python3
"""Emulator smoke test with the bundled FCEUmm libretro core (RAM + input only).
usage: python3 tests/test_playlist_flow.py [path/to/playlist.nes]
Checks (all via $CB, the cutscene seed):
  * START at the title starts cutscene 1 and the game proceeds
  * START during the opening cutscene returns to the title (no black screen)
  * SELECT at the title walks through cutscenes 1,2,3... automatically
"""
import ctypes, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ROM = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / 'release' / 'Ninja_Gaiden_II_Vietnamese_Select_Cutscene_Playlist_FIXED.nes')
CORE = ROOT / 'emulator' / 'fceumm_libretro.so'
SELECT, START = 2, 3

class GI(ctypes.Structure):
    _fields_ = [('path', ctypes.c_char_p), ('data', ctypes.c_void_p), ('size', ctypes.c_size_t), ('meta', ctypes.c_char_p)]
VIDEO = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_size_t)
AUDIO = ctypes.CFUNCTYPE(ctypes.c_size_t, ctypes.c_int16, ctypes.c_int16)
AUDIOB = ctypes.CFUNCTYPE(ctypes.c_size_t, ctypes.POINTER(ctypes.c_int16), ctypes.c_size_t)
POLL = ctypes.CFUNCTYPE(None)
STATE = ctypes.CFUNCTYPE(ctypes.c_int16, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint)
ENV = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_uint, ctypes.c_void_p)

class Emu:
    def __init__(self):
        self.lib = ctypes.CDLL(str(CORE)); self.held = None
        self.cb = (ENV(self.env), VIDEO(lambda *a: None), AUDIO(lambda l, r: 0), AUDIOB(lambda d, n: n), POLL(lambda: None), STATE(self.state))
        L = self.lib
        L.retro_set_environment(self.cb[0]); L.retro_set_video_refresh(self.cb[1]); L.retro_set_audio_sample(self.cb[2])
        L.retro_set_audio_sample_batch(self.cb[3]); L.retro_set_input_poll(self.cb[4]); L.retro_set_input_state(self.cb[5]); L.retro_init()
        d = open(ROM, 'rb').read(); self.buf = ctypes.create_string_buffer(d)
        gi = GI(ROM.encode(), ctypes.cast(self.buf, ctypes.c_void_p), len(d), None); assert L.retro_load_game(ctypes.byref(gi))
        L.retro_get_memory_data.restype = ctypes.c_void_p; self.ram = L.retro_get_memory_data(2)
    def env(self, cmd, data):
        if cmd == 10: ctypes.cast(data, ctypes.POINTER(ctypes.c_int)).contents.value = 1; return True
        return False
    def state(self, port, dev, idx, i): return 1 if (port == 0 and i == self.held) else 0
    def run(self, frames, btn=None):
        self.held = btn
        for _ in range(frames): self.lib.retro_run()
        self.held = None
    def rd(self, a): return ctypes.string_at(self.ram + a, 1)[0]

def boot_to_title():
    e = Emu(); e.run(7650); return e         # opening cutscene (~7500 frames) -> title loop

e = boot_to_title(); e.run(10, START); e.run(400)
assert e.rd(0xCB) == 1, 'START at title should start cutscene 1'
e = boot_to_title(); e.run(10, SELECT); seeds = set()
for _ in range(60):
    e.run(300); seeds.add(e.rd(0xCB))
assert {2, 3, 4} <= seeds, f'SELECT playlist did not advance: {seeds}'
e = Emu(); e.run(1500); e.run(10, START); e.run(180)
assert e.rd(0xCB) == 0, 'START during opening cutscene must return to the title'
e.run(10, START); e.run(400)
assert e.rd(0xCB) == 1, 'then START at the title must start the game'
print('PASS: START / SELECT flow')
