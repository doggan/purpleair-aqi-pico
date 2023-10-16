# Air Quality Index LED Display

Display the PurpleAir AQI (Air Quality Index) on a RGB LED via Raspberry Pi Pico W.

The code will use the PurpleAir API to periodically query PM2.5 (AQI) data from a specified sensor. The RGB LED will change color depending on the reading of the sensor. This can be useful for monitoring the outside air quality near your house, for example.

![final-anim.gif](schematic%2Ffinal-anim.gif)

## Usage

- Configure the hardware as illustrated in the schematic below.
- Modify the required constants in `config.py`.
- Deploy code to the Pico W.

## Schematic

![final.png](schematic%2Ffinal.png)
![breadboard](schematic%2Fpico-purpleair_bb.png)
![schematic](schematic%2Fpico-purpleair_schem.png)

## Potential Future Improvements

- Provide a web interface for changing the PurpleAir Station ID, to allow modifying the monitored station/sensor without having to deploy code.
- Send an alert (SMS, email) if AQI exceeds a specified level.
