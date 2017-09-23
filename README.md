# Deep Range Protocol for UAV
### DRP version: 0.2.1

## Getting Started

DRP, uses FSK to send information from the UAV to the Ground Control Station by
using the audio vTX channel and minimodem software (general-purpose software
audio FSK modem).

UAV data -> stp4uav -> vTX (audio channel) ------> GCS -> stp4uav -> Display

### Prerequisites

* [minimodem](http://www.whence.com/minimodem/) - General-purpose software audio FSK modem
* [PyCRC](https://pypi.python.org/pypi/PyCRC) - Python CRC Calculations Modules
* [pymavlink](https://pypi.python.org/pypi/pymavlink) - Pymavlink

### Running in the UAV

### Running in the GCS

To receive information in the GCS from the UAV

```
./start_modem
./start_server
```

## Authors

* **Javier Arellano-Verdejo** - *Initial work* - [javerdejo](https://github.com/javerdejo)

## License

This project is licensed under the MIT License
