class GPS(object):

    def __init__(self):
        self.lat = None
        self.lon = None
        self.alt = None
        self.rel_alt = None
        self.hdg = None
        self.sats = None
        self.vel = None
        self.fix = None

    def set_data(self, lat, lon, alt, rel_alt, vel, hdg, fix, sats):
        """
            lat        : Latitude (WGS84, EGM96 ellipsoid), in degrees * 1E7 (int32_t)
            lon        : Longitude (WGS84, EGM96 ellipsoid), in degrees * 1E7 (int32_t)
            alt        : Altitude (AMSL, NOT WGS84), in meters * 1000 (positive for up).
            rel_alt    : Altitude above ground in meters, expressed as * 1000 (millimeters) (int32_t)
            vel        : GPS ground speed (m/s * 100). If unknown, set to: UINT16_MAX (uint16_t)
            hdg        : Vehicle heading (yaw angle) in degrees * 100, 0.0..359.99 degrees.
            sats       : Number of satellites visible. If unknown, set to 255 (uint8_t)
        """

        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.rel_alt = rel_alt
        self.vel = vel
        self.hdg = hdg
        self.fix = fix
        self.sats = sats


class StatusUAV(object):

    def __init__(self):
        self.type_uav = None
        self.autopilot = None
        self.base_mode = None
        self.custom_mode = None
        self.system_status = None

    def set_data(self, type_uav, autopilot, base_mode, custom_mode, system_status):
        """
            type_uav          : Type of the UAV (quadrotor, helicopter, etc.)
            autopilot         : Autopilot type
            base_mode         : System mode bitfield
            custom_mode       : A bitfield for use for autopilot-specific
            system_status     : System status
        """

        self.type_uav = type_uav
        self.autopilot = autopilot
        self.base_mode = base_mode
        self.custom_mode = custom_mode
        self.system_status = system_status
