# 在这里写上你的代码 :-)
'''
实验名称：pyBLE-NRF52840综合测试程序
版本：v1.0
日期：2020.6
作者：01Studio
说明：开发板测试程序
'''
#导入相关模块

import time, board, busio, adafruit_ssd1306, neopixel
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
from pulseio import PWMOut

#DS18X20库模块
from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20

#DHT库模块
import adafruit_dht

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement

#构建BLE对象
ble = BLERadio()
#定义广播名称
ble.name='01Studio'
#服务类型，本例程暂时不提供蓝牙服务
advertisement = ProvideServicesAdvertisement()
#开始广播
ble.start_advertising(advertisement)

#构建I2C对象
i2c = busio.I2C(board.SCK, board.MOSI)

#构建oled对象, 01Studio配套的OLED地址为0x3C
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

#清屏
display.fill(0)
display.show()

#构建LED对象和初始化
LED_B = DigitalInOut(board.BLUE_LED) #定义引脚编号
LED_B.direction = Direction.OUTPUT  #IO为输出

LED_R = DigitalInOut(board.RED_LED) #定义引脚编号
LED_R.direction = Direction.OUTPUT  #IO为输出

#构建按键对象和初始化
switch = DigitalInOut(board.SWITCH) #定义引脚编号
switch.direction = Direction.INPUT #IO为输入
switch.pull = Pull.UP #打开上拉电阻

#pyBLE-NRF52840板载NEOPIXEL(1个灯珠)
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=False)

#ADC初始化
adc = AnalogIn(board.A5) #输入IO

# 初始化DS18B20单总线对象，引脚为D5.
ow = OneWireBus(board.D5)
# 搜索传感器，返回第1个
ds = DS18X20(ow, ow.scan()[0])

# 初始化DHT11对象，引脚为D6.
dht = adafruit_dht.DHT11(board.D6)

#提醒按按键开始
display.text("nRF52840 TEST:", 0, 5, 1, font_name='font5x8.bin')
display.text("Press KEY Start!", 0, 45, 1, font_name='font5x8.bin')
display.show()
while switch.value:
  pass

#阻塞IO，让程序保持运行
while True:
  #功能1，LED红蓝灯测试
  display.fill(0)
  display.text("pyBLE-nRF52840 TEST:", 0, 5, 1, font_name='font5x8.bin')
  display.text("1. LEDs", 0, 30, 1, font_name='font5x8.bin')
  display.show()
  for i in range(5):
    LED_B.value = 1
    LED_R.value = 1
    time.sleep(0.2)
    LED_B.value = 0
    LED_R.value = 0
    time.sleep(0.2)
  #功能2，RGB彩灯测试
  display.fill(0)
  display.text("pyBLE-NRF52840 TEST:", 0, 5, 1, font_name='font5x8.bin')
  display.text("2. RGB LEDs", 0, 30, 1, font_name='font5x8.bin')
  display.show()
  for i in range(3):
    #红色
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(0.7)
    #绿色
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(0.7)
    #蓝色
    pixels.fill((0, 0, 255))
    pixels.show()
    time.sleep(0.7)
  #功能3，ADC
  for i in range(5):
    display.fill(0)
    display.text("pyBLE-NRF52840 TEST:", 0, 5, 1, font_name='font5x8.bin')
    display.text("3. ADC", 0, 30, 1, font_name='font5x8.bin')
    #输出电压，保留2位小数。精度16bit
    display.text(str(round(adc.value*3.3/65535, 2))+' V', 0, 50, 1, font_name='font5x8.bin')
    display.show()
    time.sleep(0.2) #测量周期100ms
  #功能4，蜂鸣器
  display.fill(0)
  display.text("pyBLE-NRF52840 TEST:", 0, 5, 1, font_name='font5x8.bin')
  display.text("4. Beep", 0, 30, 1, font_name='font5x8.bin')
  display.show()
  #PWM构建，蜂鸣器引脚A4
  PWM = PWMOut(board.A4, duty_cycle=32768, frequency=200, variable_frequency=True)
  for i in range(3):
    PWM.frequency = 200
    time.sleep(0.5)
    PWM.frequency = 600
    time.sleep(0.5)
    PWM.frequency = 1000
    time.sleep(0.5)
  PWM.deinit()
  #功能5，DS18B20温度
  for i in range(5):
    display.fill(0)
    display.text("pyBLE-nRF52840:", 0, 5, 1, font_name='font5x8.bin')
    display.text("5. DS18B20", 0, 30, 1, font_name='font5x8.bin')
    #输出电压，保留2位小数。精度16bit
    display.text(str(round(ds.temperature, 2))+' C', 0, 50, 1, font_name='font5x8.bin')
    display.show()
    time.sleep(0.2) #测量周期100ms
  #功能6，DHT11温湿度
  for i in range(4):
    display.fill(0)
    display.text("pyBLE-NRF52840 TEST:", 0, 5, 1, font_name='font5x8.bin')
    display.text("6. DHT11", 0, 30, 1, font_name='font5x8.bin')
    try:
      temperature = dht.temperature #采集温度
      humidity = dht.humidity #采集湿度
      #显示温度数据
      display.text(str(temperature)+' C  '+str(humidity)+' %', 0, 50, 1, font_name='font5x8.bin')
      display.show()
    except RuntimeError as e:
      # Reading doesn't always work! Just print error and we'll try again
      print("Reading from DHT failure: ", e.args)
    time.sleep(2) #采集周期2秒
