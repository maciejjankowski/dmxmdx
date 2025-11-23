#!/usr/bin/env python3
"""
Test script for DMX strobe controller (no hardware required).
This tests the logic without needing actual DMX hardware.
"""

import sys
import time

# Mock serial module for testing
class MockSerial:
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = True
        print(f"[MOCK] Connected to {port} at {baudrate} baud")
    
    def write(self, data):
        # Just track that we're sending data
        return len(data)
    
    def close(self):
        self.is_open = False
        print("[MOCK] Serial port closed")


# Patch serial module
sys.modules['serial'] = type(sys)('serial')
sys.modules['serial'].Serial = MockSerial
sys.modules['serial'].SerialException = Exception

# Now import our module
import dmx_strobe


def test_dmx_usb_initialization():
    """Test DMXUSB class initialization."""
    print("\n--- Test 1: DMXUSB Initialization ---")
    dmx = dmx_strobe.DMXUSB(port='/dev/ttyUSB0')
    assert len(dmx.dmx_data) == 512, "DMX data should have 512 channels"
    assert all(v == 0 for v in dmx.dmx_data), "All channels should be initialized to 0"
    dmx.close()
    print("✓ DMXUSB initialization test passed")


def test_set_channel():
    """Test setting DMX channels."""
    print("\n--- Test 2: Set Channel ---")
    dmx = dmx_strobe.DMXUSB(port='/dev/ttyUSB0')
    
    # Test valid channel
    dmx.set_channel(1, 255)
    assert dmx.dmx_data[0] == 255, "Channel 1 should be set to 255"
    
    # Test boundary values
    dmx.set_channel(512, 128)
    assert dmx.dmx_data[511] == 128, "Channel 512 should be set to 128"
    
    # Test clamping
    dmx.set_channel(1, 300)
    assert dmx.dmx_data[0] == 255, "Value should be clamped to 255"
    
    dmx.set_channel(1, -10)
    assert dmx.dmx_data[0] == 0, "Value should be clamped to 0"
    
    dmx.close()
    print("✓ Set channel test passed")


def test_beamz_led_par():
    """Test BeamZ LED Par 12 LEDs controller."""
    print("\n--- Test 3: BeamZ LED Par 12 LEDs Controller ---")
    dmx = dmx_strobe.DMXUSB(port='/dev/ttyUSB0')
    par = dmx_strobe.BeamZLEDPar(dmx, start_channel=1)
    
    # Test white_full (in 12 LED version, white = R+G+B at 255)
    par.white_full()
    assert dmx.dmx_data[0] == 255, "Dimmer should be 255"
    assert dmx.dmx_data[1] == 255, "Red should be 255 (for white)"
    assert dmx.dmx_data[2] == 255, "Green should be 255 (for white)"
    assert dmx.dmx_data[3] == 255, "Blue should be 255 (for white)"
    
    # Test blackout (6 channels in 12 LED version)
    par.blackout()
    for i in range(6):
        assert dmx.dmx_data[i] == 0, f"Channel {i+1} should be 0 after blackout"
    
    dmx.close()
    print("✓ BeamZ LED Par 12 LEDs controller test passed")


def test_strobe_timing():
    """Test strobe timing calculation."""
    print("\n--- Test 4: Strobe Timing ---")
    dmx = dmx_strobe.DMXUSB(port='/dev/ttyUSB0')
    par = dmx_strobe.BeamZLEDPar(dmx, start_channel=1)
    
    # Test short duration
    start_time = time.time()
    dmx_strobe.strobe_8hz(dmx, par, duration=1)
    elapsed = time.time() - start_time
    
    # Should take approximately 1 second (with some tolerance)
    assert 0.9 <= elapsed <= 1.5, f"Strobe duration should be ~1s, was {elapsed:.2f}s"
    
    # Verify light is off after strobe
    assert dmx.dmx_data[0] == 0, "Light should be off after strobe"
    
    dmx.close()
    print(f"✓ Strobe timing test passed (duration: {elapsed:.2f}s)")


def test_message_format():
    """Test DMX message format."""
    print("\n--- Test 5: DMX Message Format ---")
    dmx = dmx_strobe.DMXUSB(port='/dev/ttyUSB0')
    
    # Set some test data
    dmx.set_channel(1, 255)
    dmx.set_channel(2, 128)
    dmx.set_channel(512, 64)
    
    # The send_dmx method should not raise any exceptions
    try:
        dmx.send_dmx()
        print("✓ DMX message format test passed")
    except Exception as e:
        print(f"✗ DMX message format test failed: {e}")
        raise
    finally:
        dmx.close()


def test_multiple_fixtures():
    """Test controlling multiple fixtures."""
    print("\n--- Test 6: Multiple Fixtures ---")
    dmx = dmx_strobe.DMXUSB(port='/dev/ttyUSB0')
    
    # 6-channel mode: first fixture uses channels 1-6, second uses 7-12
    par1 = dmx_strobe.BeamZLEDPar(dmx, start_channel=1)
    par2 = dmx_strobe.BeamZLEDPar(dmx, start_channel=7)
    
    par1.set_dimmer(255)
    par2.set_dimmer(128)
    
    assert dmx.dmx_data[0] == 255, "Fixture 1 dimmer should be 255"
    assert dmx.dmx_data[6] == 128, "Fixture 2 dimmer should be 128"
    
    dmx.close()
    print("✓ Multiple fixtures test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("DMX Strobe Controller - Test Suite")
    print("=" * 60)
    
    try:
        test_dmx_usb_initialization()
        test_set_channel()
        test_beamz_led_par()
        test_strobe_timing()
        test_message_format()
        test_multiple_fixtures()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
