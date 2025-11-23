#!/usr/bin/env python3
"""
DMX512 Strobe Controller for BeamZ LED Par
Uses AVT DMX512 USB Controller on Raspberry Pi

This script creates an 8Hz white strobe effect on a BeamZ LED Par light.
"""

import serial
import time
import sys

class DMXUSB:
    """
    Driver for AVT DMX512 USB controller.
    Uses Enttec DMX USB Pro protocol.
    """
    
    # Enttec DMX USB Pro protocol constants
    START_MSG = 0x7E
    END_MSG = 0xE7
    SEND_DMX = 0x06
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        """
        Initialize DMX USB controller.
        
        Args:
            port: Serial port path (default: /dev/ttyUSB0)
            baudrate: Communication speed (default: 115200)
        """
        try:
            self.serial = serial.Serial(port, baudrate=baudrate, timeout=1)
            print(f"Connected to DMX controller on {port}")
        except serial.SerialException as e:
            print(f"Error: Could not open serial port {port}")
            print(f"Details: {e}")
            sys.exit(1)
        
        # DMX universe - 512 channels (all initialized to 0)
        self.dmx_data = [0] * 512
    
    def set_channel(self, channel, value):
        """
        Set a DMX channel value.
        
        Args:
            channel: DMX channel (1-512)
            value: Channel value (0-255)
        """
        if 1 <= channel <= 512:
            self.dmx_data[channel - 1] = max(0, min(255, value))
        else:
            raise ValueError(f"Channel {channel} out of range (1-512)")
    
    def send_dmx(self):
        """
        Send current DMX data to the controller.
        Uses Enttec DMX USB Pro protocol.
        """
        # Construct the message according to Enttec protocol
        # Message structure: START_MSG | SEND_DMX | Length_LSB | Length_MSB | DMX_Data | END_MSG
        data_length = len(self.dmx_data)
        length_lsb = data_length & 0xFF
        length_msb = (data_length >> 8) & 0xFF
        
        # Build the complete message
        message = bytearray()
        message.append(self.START_MSG)
        message.append(self.SEND_DMX)
        message.append(length_lsb)
        message.append(length_msb)
        message.extend(self.dmx_data)
        message.append(self.END_MSG)
        
        self.serial.write(message)
    
    def blackout(self):
        """Turn off all channels."""
        self.dmx_data = [0] * 512
        self.send_dmx()
    
    def close(self):
        """Close the serial connection."""
        self.blackout()
        self.serial.close()
        print("DMX controller disconnected")


class BeamZLEDPar:
    """
    Controller for BeamZ LED Par 12 LEDs version.
    
    DMX channel layout for BeamZ LED Par 12 LEDs (6-channel mode):
    Channel 1: Dimmer (0-255)
    Channel 2: Red (0-255)
    Channel 3: Green (0-255)
    Channel 4: Blue (0-255)
    Channel 5: Strobe (0=off, 1-255=slow to fast)
    Channel 6: Mode/Programs (0-255)
    
    Note: The 12 LED version has 12x 1W LEDs (4 Red, 4 Green, 4 Blue).
    For white light, all RGB channels should be set to 255.
    """
    
    def __init__(self, dmx_controller, start_channel=1):
        """
        Initialize BeamZ LED Par 12 LEDs controller.
        
        Args:
            dmx_controller: DMXUSB instance
            start_channel: Starting DMX channel for this fixture (default: 1)
        """
        self.dmx = dmx_controller
        self.start_channel = start_channel
    
    def set_dimmer(self, value):
        """Set master dimmer (0-255)."""
        self.dmx.set_channel(self.start_channel, value)
    
    def set_rgb(self, red, green, blue):
        """Set RGB values (0-255 each)."""
        self.dmx.set_channel(self.start_channel + 1, red)
        self.dmx.set_channel(self.start_channel + 2, green)
        self.dmx.set_channel(self.start_channel + 3, blue)
    
    def set_strobe(self, value):
        """Set strobe speed (0=off, 1-255=slow to fast)."""
        self.dmx.set_channel(self.start_channel + 4, value)
    
    def set_mode(self, value):
        """Set mode/program (0-255)."""
        self.dmx.set_channel(self.start_channel + 5, value)
    
    def white_full(self):
        """Turn on white at full brightness (all RGB at 255)."""
        self.set_dimmer(255)
        self.set_rgb(255, 255, 255)  # White = R+G+B at full
        self.set_strobe(0)
        self.set_mode(0)
    
    def blackout(self):
        """Turn off all channels for this fixture."""
        for i in range(6):
            self.dmx.set_channel(self.start_channel + i, 0)


def strobe_8hz(dmx_controller, par_light, duration=10):
    """
    Create an 8Hz white strobe effect.
    
    Args:
        dmx_controller: DMXUSB instance
        par_light: BeamZLEDPar instance
        duration: How long to run the strobe in seconds (default: 10)
    """
    print(f"Starting 8Hz white strobe for {duration} seconds...")
    print("Press Ctrl+C to stop early")
    
    # 8Hz = 8 flashes per second = 0.125 seconds per cycle
    # Each cycle has ON and OFF period
    cycle_time = 1.0 / 8.0  # 0.125 seconds
    on_time = cycle_time / 2  # 50% duty cycle
    off_time = cycle_time / 2
    
    start_time = time.time()
    
    try:
        while (time.time() - start_time) < duration:
            # Turn white ON
            par_light.white_full()
            dmx_controller.send_dmx()
            time.sleep(on_time)
            
            # Turn OFF
            par_light.blackout()
            dmx_controller.send_dmx()
            time.sleep(off_time)
    
    except KeyboardInterrupt:
        print("\nStrobe interrupted by user")
    
    finally:
        # Ensure light is off when done
        par_light.blackout()
        dmx_controller.send_dmx()
        print("Strobe stopped")


def main():
    """
    Main program to demonstrate 8Hz white strobe on BeamZ LED Par 12 LEDs.
    """
    print("=" * 60)
    print("DMX512 BeamZ LED Par 12 LEDs - 8Hz White Strobe Demo")
    print("=" * 60)
    print()
    
    # Configuration
    SERIAL_PORT = '/dev/ttyUSB0'  # Change if your device is on a different port
    PAR_DMX_ADDRESS = 1            # DMX start address of your BeamZ LED Par 12 LEDs
    STROBE_DURATION = 10           # Strobe duration in seconds
    
    # Initialize DMX controller
    dmx = DMXUSB(port=SERIAL_PORT)
    
    # Initialize BeamZ LED Par 12 LEDs (6-channel mode)
    par = BeamZLEDPar(dmx, start_channel=PAR_DMX_ADDRESS)
    
    try:
        # Run the 8Hz strobe
        strobe_8hz(dmx, par, duration=STROBE_DURATION)
        
    finally:
        # Clean shutdown
        dmx.close()
        print("\nProgram completed successfully")


if __name__ == "__main__":
    main()
