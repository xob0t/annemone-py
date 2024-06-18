## All credit goes to https://github.com/illixion/Annemone

Requires hidapi.dll from https://github.com/libusb/hidapi

Example usage

```
controller = LEDController()
blue_color = [0, 0, 255]
key_colors = {"space": blue_color}
controller.set_individual_keys(key_colors)
```
