# Quick Setup Guide

## Step-by-Step Setup for BeamZ LED Par with AVT DMX512 USB Controller

### 1. Hardware Connection (5 minutes)

```
Raspberry Pi USB Port
    |
    v
AVT DMX512 USB Controller
    |
    v (DMX Cable - XLR)
BeamZ LED Par (DMX IN)
```

**Physical Setup:**
1. Connect AVT DMX512 USB controller to Raspberry Pi USB port
2. Connect DMX cable from controller's DMX OUT to Par's DMX IN
3. Power on the BeamZ LED Par fixture
4. Set fixture DMX address to **001** using the control panel

### 2. Software Installation (5 minutes)

```bash
# Clone or download this repository
cd dmxmdx

# Install dependencies
pip3 install -r requirements.txt

# Add user to dialout group for serial port access
sudo usermod -a -G dialout $USER

# Reboot to apply permissions
sudo reboot
```

### 3. Run the Demo (1 minute)

After reboot:

```bash
cd dmxmdx
python3 dmx_strobe.py
```

You should see:
- Console message: "Connected to DMX controller on /dev/ttyUSB0"
- White light strobing at 8Hz for 10 seconds
- Light turns off automatically

### 4. Troubleshooting

**Issue:** "Could not open serial port"
```bash
# Check if device is detected
ls -l /dev/ttyUSB*

# Quick permission fix (temporary)
sudo chmod 666 /dev/ttyUSB0

# Run the script
python3 dmx_strobe.py
```

**Issue:** Light doesn't respond
- Verify DMX address is set to 001 on the fixture
- Check DMX cable is properly connected
- Ensure fixture is in DMX mode (not standalone)

**Issue:** Wrong serial port
```bash
# Find correct port
ls -l /dev/ttyUSB*

# Edit dmx_strobe.py and change:
SERIAL_PORT = '/dev/ttyUSB1'  # or whatever port you found
```

## Testing Without Hardware

You can test the code logic without actual DMX hardware:

```bash
python3 test_dmx_strobe.py
```

This runs unit tests that verify the code functionality using a mock serial connection.

## Customization

### Change Strobe Duration

Edit `dmx_strobe.py`:
```python
STROBE_DURATION = 30  # Strobe for 30 seconds instead of 10
```

### Change DMX Address

If your fixture is at address 10 instead of 1:
```python
PAR_DMX_ADDRESS = 10  # Match your fixture's DMX address
```

### Change Strobe Frequency

For 10Hz instead of 8Hz, edit the `strobe_8hz` function:
```python
cycle_time = 1.0 / 10.0  # Change to 10Hz
```

## DMX Channel Reference

BeamZ LED Par 12 LEDs (6-channel mode):

| Channel | Function | Range | Description |
|---------|----------|-------|-------------|
| 1 | Master Dimmer | 0-255 | Overall brightness |
| 2 | Red | 0-255 | Red LEDs (4x 1W) |
| 3 | Green | 0-255 | Green LEDs (4x 1W) |
| 4 | Blue | 0-255 | Blue LEDs (4x 1W) |
| 5 | Strobe | 0-255 | 0=off, 1-255=slow to fast |
| 6 | Programs | 0-255 | Built-in programs |

**For White Light:** Set all RGB channels (2, 3, 4) to 255

**Note:** The 12 LED version may also support 3, 4, 8, or 11-channel modes. Check your fixture's manual.

## Safety Notes

- **Photosensitive Epilepsy Warning:** Strobe lights can trigger seizures in people with photosensitive epilepsy
- **Eye Safety:** Do not look directly into LED Par lights at full brightness
- **Proper Ventilation:** Ensure adequate cooling for extended operation
- **Electrical Safety:** Use proper power supplies and cables rated for your fixtures
