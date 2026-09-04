#
# @brief RasberryPi Pico 2 + INA238
# McroPython
# I2C FAST MODE
# BUS電圧、電流をモニタして、USB で Host へ送出する
# tick 毎に値の取得、送出を行う。Default 100ms。
# 起動時に、INA238 の IDs を送出
# shunt register = 0.002 ohm
# Vmax = 20V, Imax = 6A

import time
from machine import I2C, Pin

# -----------------------------------------------------------------------------
# Settings
# -----------------------------------------------------------------------------
TICK_MS = 100
I2C_ADDR = 0x40
I2C_FREQ = 400000
SHUNT_RESISTOR_OHMS = 0.002
VMAX_VOLTS = 20.0
IMAX_AMPS = 6.0

# -----------------------------------------------------------------------------
# INA238 register map
# -----------------------------------------------------------------------------
REG_CONFIG = 0x00
REG_SHUNT_VOLTAGE = 0x01
REG_BUS_VOLTAGE = 0x02
REG_CURRENT = 0x04
REG_CALIBRATION = 0x05
REG_MANUFACTURER_ID = 0x3E
REG_DEVICE_ID = 0x3F


class INA238:
    def __init__(self, i2c, addr=I2C_ADDR, shunt_ohm=SHUNT_RESISTOR_OHMS,
                 v_max=VMAX_VOLTS, i_max=IMAX_AMPS):
        self.i2c = i2c
        self.addr = addr
        self.shunt_ohm = shunt_ohm
        self.v_max = v_max
        self.i_max = i_max

        self.current_lsb = i_max / 32768.0
        self.calibration = int(0.00512 / (self.current_lsb * self.shunt_ohm))

        self.write_u16(REG_CALIBRATION, self.calibration)

    def write_u16(self, reg, value):
        payload = bytes([(value >> 8) & 0xFF, value & 0xFF])
        self.i2c.writeto_mem(self.addr, reg, payload)

    def read_u16(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        return (data[0] << 8) | data[1]

    def read_s16(self, reg):
        value = self.read_u16(reg)
        if value >= 0x8000:
            value -= 0x10000
        return value

    def manufacturer_id(self):
        return self.read_u16(REG_MANUFACTURER_ID)

    def device_id(self):
        return self.read_u16(REG_DEVICE_ID)

    def bus_voltage_v(self):
        raw = self.read_u16(REG_BUS_VOLTAGE)
        return raw * 0.003125

    def current_a(self):
        raw = self.read_s16(REG_CURRENT)
        return raw * self.current_lsb

    def read_all(self):
        return self.bus_voltage_v(), self.current_a()


# -----------------------------------------------------------------------------
# @brief INA238 の MANUFACTURER_ID, DEICE_ID を送出
# -----------------------------------------------------------------------------
def send_ina_ids(ina):
    mfg = ina.manufacturer_id()
    dev = ina.device_id()
    print("INA238 Manufacturer ID = 0x{:04X}".format(mfg))
    print("INA238 Device ID       = 0x{:04X}".format(dev))


# -----------------------------------------------------------------------------
# @brief BUS電圧、電流値の取得
# -----------------------------------------------------------------------------
def read_voltage_and_current(ina):
    return ina.read_all()


# -----------------------------------------------------------------------------
# @brief USB 送出
# -----------------------------------------------------------------------------
def send_usb(bus_voltage_v, current_a):
    print("BUS = {:.3f} V, CUR = {:.3f} A ({:.1f} mA)".format(
        bus_voltage_v,
        current_a,
        current_a * 1000.0
    ))


# -----------------------------------------------------------------------------
# @brief tick 毎に値取得、送出処理を起動
# -----------------------------------------------------------------------------
def tick_monitor(ina):
    while True:
        bus_voltage_v, current_a = read_voltage_and_current(ina)
        send_usb(bus_voltage_v, current_a)
        time.sleep_ms(TICK_MS)


# -----------------------------------------------------------------------------
# @brief 初期化、main loop
# -----------------------------------------------------------------------------
def main():
    print("Raspberry Pi Pico 2 + INA238")
    print("I2C FAST MODE: 400kHz")
    print("Sample interval: {} ms".format(TICK_MS))

    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=I2C_FREQ)
    devices = i2c.scan()

    if I2C_ADDR not in devices:
        print("INA238 not found on I2C bus.")
        return

    ina = INA238(i2c)
    send_ina_ids(ina)
    tick_monitor(ina)


if __name__ == "__main__":
    main()
