# Sound Transfer Protocol for an Unmanned Aerial Vehicle
### stp4uav version: 0.0.1

## Getting Started

stp4uav, uses FSK to send information from the UAV to the Ground Control Station by
using the audio vTX channel and minimodem software (general-purpose software
audio FSK modem).

UAV data -> stp4uav -> vTX (audio channel) ------> GCS -> stp4uav -> Display

### Prerequisites

* [minimodem](http://www.whence.com/minimodem/) - General-purpose software audio FSK modem
* [PyCRC](https://pypi.python.org/pypi/PyCRC) - Python CRC Calculations Modules

### Running in the UAV

To send telemetry information from the UAV to the GCS

```
python stp4uav.py -t
```

### Running in the GCS

To receive information in the GCS from the UAV

```
python stp4uav.py -r
```

## Authors

* **Javier Arellano-Verdejo** - *Initial work* - [javerdejo](https://github.com/javerdejo)

## License

This project is licensed under the MIT License
