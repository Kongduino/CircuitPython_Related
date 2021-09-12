import board, busio, time
from micropython import const
from myUtils import hexDump

DEFAULT_IIC_ADDR = const(0x40)
SELECT_COMM_CMD = const(0X88)
NO_ERROR = const(0)
ERROR_PARAM = const(-1)
ERROR_COMM = const(-2)
ERROR_OTHERS = const(-128)
i2c = 0

class HM330X:
  _IIC_ADDR = 0
  _mySCL = 0
  _mySDA = 0
  i2c = 0
  temp = bytearray(2)
  msgs = ["sensor num: ", "PM1.0 (CF=1, Standard particulate matter): ",
          "PM2.5 (CF=1, Standard particulate matter): ", "PM10  (CF=1, Standard particulate matter): ",
          "PM1.0 (Atmospheric environment): ", "PM2.5 (Atmospheric environment): ", "PM10  (Atmospheric environment): "
        ]

  def IIC_SEND_CMD(self, CMD):
    global i2c
    i2c = busio.I2C(self._mySCL, self._mySDA)
    if i2c.try_lock() == True:
      self.temp[0] = self._IIC_ADDR
      self.temp[1] = CMD
      i2c.writeto(self._IIC_ADDR, self.temp)
      buff=bytearray(1)
      i2c.readfrom_into(0x40, buff)
      i2c.unlock()
      return buff[0]
    else:
      print("Couldn't get lock")
      return -1
    i2c.deinit()

  def __init__(self, mySCL, mySDA, addr=DEFAULT_IIC_ADDR):
    self._mySCL = mySCL
    self._mySDA = mySDA
    #print("SCL = "+str(mySCL))
    #print("SDA = "+str(mySDA))
    self._IIC_ADDR = addr
    return

  def init(self):
    return self.IIC_SEND_CMD(SELECT_COMM_CMD)

  def read_sensor_value(self, data):
    time_out_count = 0
    if i2c.try_lock() == True:
      i2c.readfrom_into(self._IIC_ADDR, data)
      ix = 0
      sum = 0
      while ix<28:
        sum += int(data[ix])
        ix+=1
      return (sum & 0xFF) == data[28]

