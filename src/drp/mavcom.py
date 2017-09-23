from pymavlink import mavutil
import time


class Link(object):

    def __init__(self, ip, port):
        self.gps = None
        self.ip = ip
        self.master = None
        self.port = port
        self.tic = time.time()
        self.uav = None

    def connect(self):
        """
            connect()
        """
        str_conn = 'udp:' + self.ip + ':' + str(self.port)
        self.master = mavutil.mavlink_connection(str_conn, input=False, source_system=255)

    def update_gps(self, gps):
        """
            update_gps()
        """
        self.gps = gps

        toc = time.time() - self.tic
        time_usec = int(round(toc * 1000))

        # from pymavlink:
        # global_position_int_send(time_boot_ms, lat, lon, alt, relative_alt, vx, vy, vz, hdg)
        self.master.mav.global_position_int_send(time_usec, gps.lat, gps.lon, gps.alt, gps.rel_alt, 0, 0, 0, gps.hdg)

        # from pymavlink:
        # gps_raw_int_send(time_usec, fix_type, lat, lon, alt, eph, epv, vel, cog, satellites_visible)
        self.master.mav.gps_raw_int_send(time_usec, gps.fix, gps.lat, gps.lon, gps.alt, 0, 0, gps.vel, 0, gps.sats)

    def update_status(self, uav):
        """
            update_status()
        """
        self.uav = uav

        # from pymavlink:
        # heartbeat_send(type_uav, autopilot, base_mode, custom_mode, system_status)
        self.master.mav.heartbeat_send(uav.type_uav, uav.autopilot, uav.base_mode, uav.custom_mode, uav.system_status)
