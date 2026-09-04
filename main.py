##
# @brief RasberryPi Pico 2 + INA238
# McroPython
# I2C FAST MODE
# BUS電圧、電流をモニタして、USB で Host へ送出する
# tick 毎に値の取得、送出を行う。Default 100ms。
# 起動時に、INA238 の IDs を送出
# shunt register = 0.002 ohm
# Vmax = 20V, Imax = 6A


## @brief INA238 の MANUFACTURER_ID, DEICE_ID を送出

## @brief BUS電圧、電流値の取得

## @brief USB 送出

## @brief tick 毎に値取得、送出処理を起動

## @brief 初期化、main loop
