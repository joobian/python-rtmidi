#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wrap MidiOut to add convenience methods for sending common MIDI events."""

import binascii

import rtmidi
from rtmidi.midiconstants import *


def parse_sysex_string(s):
    """Convert a sysex message string in hexadecimal notation into bytes.

    Example:

        >>> parse_sysex_string("F0 7E 00 09 01 F7")
        b'\xf0~\x00\t\x01\xf7'
    """
    return binascii.unhexlify(s.replace(' ', ''))


class MidiOutWrapper:
    def __init__(self, midi, ch=1):
        self.channel = ch
        self._midi = midi

    def send_channel_message(self, status, data1=None, data2=None, ch=None):
        """Send a MIDI channel mode message."""
        msg = [(status & 0xF0) | ((ch if ch else self.channel) - 1 & 0xF)]

        if data1 is not None:
            msg.append(data1 & 0x7F)

            if data2 is not None:
                msg.append(data2 & 0x7F)

        self._midi.send_message(msg)

    def send_system_common_message(self, status=END_OF_EXCLUSIVE, data1=None,
                                   data2=None):
        """Send a MIDI system common message."""
        msg = [status & 0xF7]

        if msg[0] in (MIDI_TIME_CODE, SONG_POSITION_POINTER, SONG_SELECT):
            msg.append(data1 & 0x7F)

        if msg[0] == SONG_POSITION_POINTER:
            msg.append(data2 & 0x7F)

        self._midi.send_message(msg)

    def send_system_realtime_message(self, status=TIMING_CLOCK):
        """Send a MIDI system real-time message."""
        self._midi.send_message([status & 0xF7], delta=1)

    def send_system_exclusive(self, value=""):
        """Send a MIDI system exclusive (SysEx) message."""
        msg = parse_sysex_string(value)

        if (msg and msg.startswith(b'\xF0') and msg.endswith(b'\xF7') and
                all((val <= 0x7F for val in msg[1:-1]))):
            self._midi.send_message(msg)
        else:
            raise ValueError("Invalid sysex string: %s", msg)

    def send_note_off(self, note=60, velocity=0, ch=None):
        """Send a 'Note Off' message."""
        self.send_channel_message(NOTE_OFF, note, velocity, ch=ch)

    def send_note_on(self, note=60, velocity=127, ch=None):
        """Send a 'Note On' message."""
        self.send_channel_message(NOTE_ON, note, velocity, ch=ch)

    def send_poly_pressure(self, note=60, value=0, ch=None):
        """Send a 'Polyphonic Pressure' (Aftertouch) message."""
        self.send_channel_message(POLY_PRESSURE, note, value, ch=ch)

    def send_control_change(self, cc=0, value=0, ch=None):
        """Send a 'Control Change' message."""
        self.send_channel_message(CONTROL_CHANGE, cc, value, ch=ch)

    def send_program_change(self, program=0, ch=None):
        """Send a 'Program Change' message."""
        self.send_channel_message(PROGRAM_CHANGE, program, ch=ch)

    def send_channel_pressure(self, value=0, ch=None):
        """Send a 'Monophonic Pressure' (Channel Pressure) message."""
        self.send_channel_message(CHANNEL_PRESSURE, value, ch=ch)

    def send_pitch_bend(self, value=8192, ch=None):
        """Send a 'Pitch Bend' message."""
        self.send_channel_message(PITCH_BEND, value & 0x7f,
                                  (value >> 7) & 0x7f, ch=ch)

    def send_bank_select(self, bank=None, msb=None, lsb=None, ch=None):
        """Send 'Bank Select' MSB and/or LSB 'Control Change' messages."""
        if bank is not None:
            msb = (bank << 7) & 0x7F
            lsb = bank & 0x7F

        if msb is not None:
            self.send_control_change(BANK_SELECT_MSB, msb, ch=ch)

        if lsb is not None:
            self.send_control_change(BANK_SELECT_LSB, lsb, ch=ch)

    def send_modulation(self, value=0, ch=None):
        """Send a 'Modulation' (CC #1) 'Control Change' message."""
        self.send_control_change(MODULATION, value, ch=ch)

    def send_breath_controller(self, value=0, ch=None):
        """Send a 'Breath Controller' (CC #3) 'Control Change' message."""
        self.send_control_change(BREATH_CONTROLLER, value, ch=ch)

    def send_foot_controller(self, value=0, ch=None):
        """Send a 'Foot Controller' (CC #4) 'Control Change' message."""
        self.send_control_change(FOOT_CONTROLLER, value, ch=ch)

    def send_channel_volume(self, value=127, ch=None):
        """Send a 'Volume' (CC #7) 'Control Change' message."""
        self.send_control_change(CHANNEL_VOLUME, value, ch=ch)

    def send_balance(self, value=63, ch=None):
        """Send a 'Balance' (CC #8) 'Control Change' message."""
        self.send_control_change(BALANCE, value, ch=ch)

    def send_pan(self, value=63, ch=None):
        """Send a 'Pan' (CC #10) 'Control Change' message."""
        self.send_control_change(PAN, value, ch=ch)

    def send_expression(self, value=127, ch=None):
        """Send a 'Expression' (CC #11) 'Control Change' message."""
        self.send_control_change(EXPRESSION_CONTROLLER, value, ch=ch)

    def send_all_sound_off(self, ch=None):
        """Send a 'All Sound Off' (CC #120) 'Control Change' message."""
        self.send_control_change(ALL_SOUND_OFF, 0, ch=ch)

    def send_reset_all_controllers(self, ch=None):
        """Send a 'All Sound Off' (CC #121) 'Control Change' message."""
        self.send_control_change(RESET_ALL_CONTROLLERS, 0, ch=ch)

    def send_local_control(self, value=1, ch=None):
        """Send a 'Local Control On/Off' (CC #122) 'Control Change' message."""
        self.send_control_change(LOCAL_CONTROL, 127 if bool(value) else 0, ch=ch)

    def send_all_notes_off(self, ch=None):
        """Send a 'All Notes Off' (CC #123) 'Control Change' message."""
        self.send_control_change(ALL_NOTES_OFF, 0, ch=ch)

    # add more convenience methods for other common MIDI events here...


if __name__ == '__main__':
    import time

    mout = rtmidi.MidiOut()
    mout.open_virtual_port()
    input('Connect to new MIDI port and then press key...')
    mw = MidiOutWrapper(mout, ch=3)
    mw.send_program_change(40)
    mw.send_note_on(60)
    time.sleep(1)
    mw.send_note_off(60)
