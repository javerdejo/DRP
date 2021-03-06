# -*- coding: utf-8 -*-

"""
    Author: Javier Arellano-Verdejo
    Date: Sep/2017
    Version: 0.2.2
"""

from __future__ import print_function

import array
import signal
import struct
import sys
import time

from PyCRC.CRC16 import CRC16

from drp import mavcom as mc
from drp import typedata as td

from settings import (INFILE, OUTDIR, MAVADDRESS, MAVPORT)


def start_telemetry_reading(f):
    """
        start_telemetry_reading

        lee el flujo de datos de entrada del archivo 'f'

        :param: f, manejador de archivo devuelto por la funcion open()
        :return: flujo de bytes
    """

    f.seek(0, 2)     # posiciona el apuntador al final del archivo
    pos = f.tell()  # guarda la posicion actual dentro del archivo

    while True:
        f.seek(pos)  # mueve el apuntador a la ultima posicion de lectura
        c = f.read(1)
        pos = f.tell()  # guarda la posicion actual dentro del archivo
        if not c:
            time.sleep(0.1)
            continue

        yield c


def sigint_handler(signum, frame):
    _server.stop()


class DRPServer(object):

    def __init__(self):
        """
            Contrusctor
        """

        global _server
        _server = self

        # messages deffinition
        self.DRP_GOBAL_POSITION = '1'
        self.DRP_ATTITUDE = '2'
        self.DRP_NAV_INFO = '3'
        self.DRP_SENSOR_BANK_1 = '4'
        self.DRP_SENSOR_BANK_2 = '5'

        # definicion de la matriz de adyacencia del AFS para el procesamiento
        # del stream de entrada
        self.AFD = [
            [2, 1, 1],
            [3, 1, 1],
            [3, 4, 3],
            [3, 5, 3],
            [1, 1, 1]
        ]

        self.BYTE_START = 32  # byte de inicio de la transmision (2 bytes)
        self.BYTE_END = 42  # byte de final de comunicación (2 bytes)

        # variables globales para el manejo de estadisticas
        self.packet_error = 0  # numero de paquetes recibidos con exito
        self.packet_ok = 0  # numero de paquetes recibidos con error

        out_fname = OUTDIR + '/' + time.strftime("%Y-%m-%Y_%H-%M-%S_") + 'data.csv'
        self.outfile = open(out_fname, 'w')
        self.infile = open(INFILE, 'rb')

        # TEMPORALES solo para fines de simulacion
        self.lat = 0
        self.lon = 0

        # Comunicación con MavLink
        self.link = mc.Link(MAVADDRESS, MAVPORT)
        self.gps = td.GPS()
        self.status = td.StatusUAV()

    def get_data_index(self, c):
        """
            get_data_index

            devuelve el indice para el acceso al AFD asociado con la entrada

            :param: c, byte de entrada ' ', '*', ?
            :return: indice para acceso a la matriz AFD
        """

        if c == self.BYTE_START:
            return 0
        elif c == self.BYTE_END:
            return 1
        else:
            return 2

    def proccess_stream(self, data):
        """
            proccess_stream

            evalua el flujo de bytes de entrada dentro del AFD dando como resultado
            un paquete de datos

            :param: data, bytes de entrada al AFD
            :return: none
        """

        cstate = 1
        buf = []

        for c in data:
            c = ord(c)
            pstate = cstate
            cstate = self.AFD[cstate-1][self.get_data_index(c)]
            if cstate == 3:
                if pstate == 2:
                    continue
                elif pstate == 4:
                    buf.append(self.BYTE_END)
                    buf.append(c)
                else:
                    buf.append(c)
            elif cstate == 5:
                self.proccess_packet(buf)
                cstate = 1
                buf = []

    def send_mavlink_data(self, gps, status):
        """
            send_mavlink_data()
        """

        self.link.update_status(status)
        self.link.update_gps(gps)

    def start(self):
        """
            start
        """

        # Conecta con el GCS via mavlink
        self.link.connect()

        # Inicia la lectura del flujo de datpos
        data = start_telemetry_reading(self.infile)

        # Procesa el flujo de datos de entrada
        self.proccess_stream(data)

    def stop(self):
        """
            stop()
        """

        # Cierra los archivos de entrada y salida y sale del sistema
        self.infile.close()
        self.outfile.close()
        sys.exit(0)

    def proccess_packet(self, data):
        """
            proccess_packet

            procesa el paquete de datos obtenido por el AFD

            :param: data, paquete de datos extraido por la función 'proccess_stream'
            del lujo de entrada
            :return: none
        """

        """
            ToDo Distinguir entre distintos tipos de packetes
            
            - GPS
            - Sensores
            - Attitud
        """

        message = chr(data[0])
        str_data = array.array('B', data[1:]).tostring()
        if message == self.DRP_GOBAL_POSITION:
            print("DRP_GOBAL_POSITION ")

            data_long = struct.unpack('=iii', str_data)

            # --- Check CRC ---
            data_packed = struct.pack('=ii', data_long[0], data_long[1])
            crc16 = CRC16().calculate(data_packed)

            if data_long[2] == crc16:
                self.packet_ok += 1
                total = self.packet_ok + self.packet_error
                percent = (self.packet_ok * 100.0) / total
                self.outfile.write('{},{},{},{},{:2.2f},{},{},{:f},{:f}\n'
                                   .format(
                                        ord(message),
                                        self.packet_ok,
                                        self.packet_error,
                                        total,
                                        percent,
                                        time.strftime("%d/%m/%Y"),
                                        time.strftime("%H:%M:%S"),
                                        data_long[0]/1000000.0,
                                        data_long[1]/1000000.0
                                    ))
                self.outfile.flush()

                # simula el avance del avion
                if self.lat == 0:
                    self.lat = data_long[0] * 10
                    self.lon = data_long[1] * 10
                else:
                    self.lon += 1000

                self.gps.set_data(self.lat, self.lon, 0, 0, 0, 0, 0, 0)
                self.status.set_data(1, 0, 128, 0, 4)

                self.send_mavlink_data(self.gps, self.status)
            else:
                print("CRC error")
                self.packet_error += 1

        elif message == self.DRP_ATTITUDE:
            print("DRP_ATTITUDE")

            data_long = struct.unpack('=hhhi', str_data)

            # --- Check CRC ---
            data_packed = struct.pack('=hhh', data_long[0], data_long[1], data_long[2])
            crc16 = CRC16().calculate(data_packed)

            if data_long[3] == crc16:
                self.packet_ok += 1
                total = self.packet_ok + self.packet_error
                percent = (self.packet_ok * 100.0) / total
                self.outfile.write('{},{},{},{},{:2.2f},{},{},{:f},{:f},{:f}\n'
                                   .format(
                                        ord(message),
                                        self.packet_ok,
                                        self.packet_error,
                                        total,
                                        percent,
                                        time.strftime("%d/%m/%Y"),
                                        time.strftime("%H:%M:%S"),
                                        data_long[0] / 100.0,
                                        data_long[1] / 100.0,
                                        data_long[2] / 100.0
                                    ))
                self.outfile.flush()

                self.status.set_data(1, 0, 128, 0, 4)

            else:
                print("CRC error")
                self.packet_error += 1

        elif message == self.DRP_NAV_INFO:
            print("DRP_NAV_INFO")

            data_long = struct.unpack('=hhhBi', str_data)

            # --- Check CRC ---
            data_packed = struct.pack('=hhhB', data_long[0], data_long[1], data_long[2], data_long[3])
            crc16 = CRC16().calculate(data_packed)

            if data_long[4] == crc16:
                self.packet_ok += 1
                total = self.packet_ok + self.packet_error
                percent = (self.packet_ok * 100.0) / total
                self.outfile.write('{},{},{},{},{:2.2f},{},{},{:f},{},{},{}\n'
                                   .format(
                                        ord(message),
                                        self.packet_ok,
                                        self.packet_error,
                                        total,
                                        percent,
                                        time.strftime("%d/%m/%Y"),
                                        time.strftime("%H:%M:%S"),
                                        data_long[0] / 100.0,
                                        data_long[1] / 100.0,
                                        data_long[2] / 100.0,
                                        data_long[3] / 100.0,
                                    ))
                self.outfile.flush()

                self.status.set_data(1, 0, 128, 0, 4)

            else:
                print("CRC error")
                self.packet_error += 1

        elif message == self.DRP_SENSOR_BANK_1:
            print("DRP_SENSOR_BANK_1")

            data_long = struct.unpack('=iii', str_data)

            # --- Check CRC ---
            data_packed = struct.pack('=ii', data_long[0], data_long[1])
            crc16 = CRC16().calculate(data_packed)

            if data_long[2] == crc16:
                self.packet_ok += 1
                total = self.packet_ok + self.packet_error
                percent = (self.packet_ok * 100.0) / total
                self.outfile.write('{},{},{},{},{:2.2f},{},{},{:f},{:f}\n'
                                   .format(
                                        ord(message),
                                        self.packet_ok,
                                        self.packet_error,
                                        total,
                                        percent,
                                        time.strftime("%d/%m/%Y"),
                                        time.strftime("%H:%M:%S"),
                                        data_long[0]/1000000.0,
                                        data_long[1]/1000000.0
                                    ))
                self.outfile.flush()

                self.status.set_data(1, 0, 128, 0, 4)

            else:
                print("CRC error")
                self.packet_error += 1

        elif message == self.DRP_SENSOR_BANK_2:
            print("DRP_SENSOR_BANK_2")

            data_long = struct.unpack('=iii', str_data)

            # --- Check CRC ---
            data_packed = struct.pack('=ii', data_long[0], data_long[1])
            crc16 = CRC16().calculate(data_packed)

            if data_long[2] == crc16:
                self.packet_ok += 1
                total = self.packet_ok + self.packet_error
                percent = (self.packet_ok * 100.0) / total
                self.outfile.write('{},{},{},{},{:2.2f},{},{},{:f},{:f}\n'
                                   .format(
                                        ord(message),
                                        self.packet_ok,
                                        self.packet_error,
                                        total,
                                        percent,
                                        time.strftime("%d/%m/%Y"),
                                        time.strftime("%H:%M:%S"),
                                        data_long[0]/1000000.0,
                                        data_long[1]/1000000.0
                                    ))
                self.outfile.flush()

                self.status.set_data(1, 0, 128, 0, 4)

            else:
                print("CRC_ERROR")
                self.packet_error += 1

        else:
            print("unknown message")


if __name__ == '__main__':
    # Manejo de las señales Ctrl + C
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    # Deine la instancia e inicia el servicio
    s = DRPServer()
    s.start()
