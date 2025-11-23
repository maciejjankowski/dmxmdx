# DMX512 Controller for Raspberry Pi

Sample DMX512 Python code for controlling BeamZ LED Par 12 LEDs fixtures using an AVT DMX512 USB controller on Raspberry Pi. This project demonstrates an 8Hz white strobe effect.

## Hardware Requirements

- **Raspberry Pi** (any model with USB port - tested on Pi 3/4)
- **AVT DMX512 USB Controller** (Enttec DMX USB Pro compatible)
- **BeamZ LED Par 12 LEDs** (12x 1W LEDs: 4 Red, 4 Green, 4 Blue)
- **DMX Cable** (3-pin or 5-pin XLR)
- **Power supply** for the LED Par

## Hardware Setup

### 1. Connect the DMX Controller

1. Plug the AVT DMX512 USB controller into your Raspberry Pi's USB port
2. The controller should appear as `/dev/ttyUSB0` (or `/dev/ttyUSB1` if other USB serial devices are connected)
3. Verify the connection:
   ```bash
   ls -l /dev/ttyUSB*
   ```

### 2. Set Up the BeamZ LED Par

1. **Set the DMX address on the BeamZ LED Par 12 LEDs:**
   - Use the control panel on the back of the fixture
   - Navigate to DMX address setting (usually in setup menu)
   - Set the address to **001** (or note the address you choose)
   - Set the fixture to **6-channel mode** (RGB mode)

2. **DMX Channel Layout (6-channel mode):**
   - Channel 1: Master Dimmer (0-255)
   - Channel 2: Red (0-255)
   - Channel 3: Green (0-255)
   - Channel 4: Blue (0-255)
   - Channel 5: Strobe (0=off, 1-255=slow to fast)
   - Channel 6: Mode/Programs (0-255)
   
   **Note:** For white light, all RGB channels (2, 3, 4) are set to 255.

3. **Connect DMX cable:**
   - Connect DMX cable from AVT controller's DMX OUT to the BeamZ Par's DMX IN
   - If using multiple fixtures, daisy-chain them using DMX OUT to next fixture's DMX IN
   - Add a DMX terminator to the last fixture in the chain (optional but recommended)

### 3. Power on the Equipment

1. Power on the BeamZ LED Par
2. Ensure the fixture is in DMX mode (not standalone or sound-activated mode)
3. The fixture should now respond to DMX commands

## Software Setup

### 1. Install Python Dependencies

On your Raspberry Pi, run:

```bash
# Update package list
sudo apt-get update

# Install pip if not already installed
sudo apt-get install python3-pip

# Install required Python packages
pip3 install -r requirements.txt
```

### 2. Set Serial Port Permissions

Grant permission to access the USB serial port:

```bash
# Add your user to the dialout group
sudo usermod -a -G dialout $USER

# Log out and log back in for changes to take effect
# Or reboot the Raspberry Pi
sudo reboot
```

Alternatively, for a quick test without rebooting:

```bash
sudo chmod 666 /dev/ttyUSB0
```

## Running the Sample Program

### Basic Usage

Run the strobe program with default settings (DMX address 1, 10 seconds):

```bash
python3 dmx_strobe.py
```

### Configuration

Edit the configuration variables in `dmx_strobe.py`:

```python
SERIAL_PORT = '/dev/ttyUSB0'  # Change if your device is on a different port
PAR_DMX_ADDRESS = 1            # Change to match your fixture's DMX address
STROBE_DURATION = 10           # Duration in seconds
```

### Expected Behavior

When you run the program, you should see:
1. Connection confirmation to the DMX controller
2. White light strobing at 8Hz (8 flashes per second)
3. After the specified duration, the light turns off
4. Clean shutdown message

**Press Ctrl+C to stop the strobe early.**

## Troubleshooting

### "Could not open serial port"

- Check that the USB controller is plugged in: `ls -l /dev/ttyUSB*`
- Verify permissions: `ls -l /dev/ttyUSB0`
- Ensure you're in the dialout group: `groups`
- Try with sudo: `sudo python3 dmx_strobe.py`

### Light doesn't respond

- Verify DMX address on the fixture matches `PAR_DMX_ADDRESS` in the code
- Check DMX cable connections
- Ensure the fixture is in DMX mode (check fixture display)
- Try setting the fixture to address 001 and running the default script
- Test the fixture in standalone mode to verify it's working

### Wrong serial port

If your DMX controller appears as `/dev/ttyUSB1` instead of `/dev/ttyUSB0`:

```bash
# Find the correct port
ls -l /dev/ttyUSB*

# Update the script
SERIAL_PORT = '/dev/ttyUSB1'
```

### Strobe frequency incorrect

The code implements software-based strobing at 8Hz (125ms period, 50% duty cycle). If timing seems off:
- The Raspberry Pi's timing may vary under load
- For precise timing, consider using the fixture's built-in strobe function
- Reduce system load by closing other applications

## Code Structure

- **`DMXUSB` class**: Handles communication with the AVT DMX512 USB controller using the Enttec DMX USB Pro protocol
- **`BeamZLEDPar` class**: Provides high-level control for BeamZ LED Par 12 LEDs fixtures (6-channel mode)
- **`strobe_8hz()` function**: Implements the 8Hz white strobe effect
- **`main()` function**: Entry point that orchestrates the demo

## Customization Examples

### Change strobe frequency

To strobe at a different frequency (e.g., 10Hz):

```python
cycle_time = 1.0 / 10.0  # 10Hz
```

### Use different colors

```python
# Red strobe
par_light.set_dimmer(255)
par_light.set_rgb(255, 0, 0)  # Full red
dmx_controller.send_dmx()

# Blue strobe
par_light.set_dimmer(255)
par_light.set_rgb(0, 0, 255)  # Full blue
dmx_controller.send_dmx()

# Purple strobe
par_light.set_dimmer(255)
par_light.set_rgb(255, 0, 255)  # Red + Blue
dmx_controller.send_dmx()
```

### Control multiple fixtures

```python
par1 = BeamZLEDPar(dmx, start_channel=1)   # First fixture at address 1
par2 = BeamZLEDPar(dmx, start_channel=7)   # Second fixture at address 7 (1+6 channels)
```

## Technical Details

### Protocol

The code uses the **Enttec DMX USB Pro protocol** over serial communication:
- Baudrate: 115200
- Message format: `0x7E | 0x06 | Length_LSB | Length_MSB | DMX_Data | 0xE7`
- DMX universe: 512 channels

### Timing

- 8Hz = 8 cycles per second
- Period = 125ms (0.125 seconds)
- ON time = 62.5ms
- OFF time = 62.5ms

## License

This is sample code provided for educational and demonstration purposes.

## Support

For issues specific to:
- **AVT DMX512 USB Controller**: Consult the manufacturer's documentation
- **BeamZ LED Par**: Check the fixture's user manual for DMX channel layout
- **This code**: Open an issue in this repository