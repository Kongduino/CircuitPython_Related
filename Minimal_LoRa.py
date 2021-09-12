import time, board, busio, digitalio, adafruit_ssd1306, neopixel
import adafruit_rfm9x, aesio, json
from binascii import hexlify

transmit_interval = 30
cipher = aesio.AES(b'YELLOW SUBMARINEENIRAMBUS WOLLEY', aesio.MODE_ECB)
#neopixel
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1, auto_write=False)
#oled
i2c = busio.I2C(board.SCK, board.MOSI)
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
# Initialize SPI bus.
spi = busio.SPI(board.D11, MOSI=board.D5, MISO=board.MISO)
posY=5
rfm9x=0
#switch = digitalio.DigitalInOut(board.D6)
TRNG = 0
TRNG_index = 0

def hexDump(buf):
  alphabet=b'0123456789abcdef'
  ln = len(buf)
  print("Len of buf: "+str(ln))
  print("   +------------------------------------------------+ +----------------+")
  print("   |.0 .1 .2 .3 .4 .5 .6 .7 .8 .9 .a .b .c .d .e .f | |      ASCII     |")
  i = 0
  while i < ln:
    if i % 128 == 0:
      print("   +------------------------------------------------+ +----------------+")
    s=b'|                                                | |................|'
    s0=list(s)
    ix = 1
    iy = 52
    j=0
    while j < 16:
      if (i + j) < ln:
        c=buf[i+j]
        s0[ix] = alphabet[(c >> 4) & 0x0F]
        ix += 1
        s0[ix] = alphabet[c & 0x0F]
        ix += 2
        if (c > 31 and c < 127):
          s0[iy] = c
        iy += 1
      j += 1
    index = int(i / 16)
    hd=("00"+hex(index)[2:])[-2:]+"."
    s=bytearray(s0)
    s = hd+s.decode()
    print(s)
    i += 16
  print("   +------------------------------------------------+ +----------------+")
  
def decryptBuffer(inp, cipher):
  i=0
  j=len(inp)
  finalBuff=bytearray()
  if j%16 == 0:
    # if we have a packet that's not a multiple of 16
    # we just ignore it and return an empty bytearray
    while i!=j:
      inp0=inp[i:i+16]
      outp = bytearray(16)
      cipher.decrypt_into(inp0, outp)
      finalBuff=finalBuff+outp
      i=i+16
  return finalBuff


def encryptBuffer(inp, cipher):
  i=0
  j=len(inp)
  r=j%16
  if r>0:
    n=16-r
    j = j + n
    supp=bytearray(n)
    x=range(0, n)
    for ix in x:
      supp[ix]=n
    inp=inp+supp
  print(inp.decode())
  finalBuff=bytearray()
  while i!=j:
    inp0=inp[i:i+16]
    outp = bytearray(16)
    cipher.encrypt_into(inp0, outp)
    finalBuff=finalBuff+outp
    i=i+16
  return finalBuff
  
def prepPacket(cnt):
  packet={}
  packet['cmd']='ping'  
  UUID = "0000000"+hex(TRNG[TRNG_index]<<24|TRNG[TRNG_index+1]<<16|TRNG[TRNG_index+2]<<8|TRNG[TRNG_index+3])[2:]
  TRNG_index = TRNG_index + 4
  if TRNG_index == 256:
      print("Restocking up on random bytes!")
      TRNG = rfm9x.stockupRandom()
      hexDump(TRNG)
      TRNG_index = 0
  packet['UUID']=UUID[-8:].upper()
  packet['from']='nRF52'
  packet['count']=cnt
  return encryptBuffer(json.dumps(packet).encode(), cipher)

def sendPacket():
  global pixels, display, rfm9x
  pixels.fill((0, 0, 255))
  pixels.show()
  time.sleep(1.0)
  display.fill((0, 0, 0))
  posY = 5
  print("Sending PING packet")
  display.text("Sending PING packet", 0, posY, 1, font_name='font5x8.bin')
  posY=posY+10
  display.text("message number {}".format(counter), 0, posY, 1, font_name='font5x8.bin')
  posY=posY+10
  display.show()
  packet = prepPacket(counter)
  print("Sending:")
  hexDump(packet)
  rfm9x.send(packet)
  pixels.fill((0, 0, 0))
  pixels.show()

def init():
  global cipher, switch, pixels, i2c, display, counter, posY, TRNG, TRNG_index, rfm9x
  pixels.fill((255, 0, 0))
  pixels.show()
  time.sleep(0.7)
  display.fill(0)
  display.text("nRF52840 LoRa", 22, posY, 1, font_name='font5x8.bin')
  posY=posY+10
  display.show()
  pixels.fill((255, 127, 127))
  pixels.show()
  time.sleep(0.7)
  # set the time interval (seconds) for sending packets
  transmit_interval = 60
  # Define radio parameters.
  RADIO_FREQ_MHZ = 433.125  # Frequency of the radio in Mhz.
  # Define pins connected to the chip.
  CS = digitalio.DigitalInOut(board.D9)
  RESET = digitalio.DigitalInOut(board.D10)
  # Initialze RFM radio
  rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
  display.text("LoRa inited:", 0, posY, 1, font_name='font5x8.bin')
  posY=posY+10
  TRNG = rfm9x.stockupRandom()
  hexDump(TRNG)
  pixels.fill((0, 255, 0))
  pixels.show()
  display.text(". SF: "+str(rfm9x.spreading_factor), 0, posY, 1, font_name='font5x8.bin')
  display.text(". BW: "+str(round(rfm9x.signal_bandwidth/1e3, 1))+" k", 50, posY, 1, font_name='font5x8.bin')
  posY=posY+10
  display.text(". Freq:"+str(round(rfm9x.frequency_mhz, 3)), 0, posY, 1, font_name='font5x8.bin')
  display.text(". CR:4/"+str(rfm9x.coding_rate), 80, posY, 1, font_name='font5x8.bin')
  posY=posY+10
  display.show()
  time.sleep(1.0)
  pixels.fill((0, 0, 0))
  pixels.show()
  rfm9x.tx_power = 23
  # initialize counter
  counter = 0
  
if __name__ == "__main__":
#  global cipher, switch, pixels, i2c, display, counter, posY, TRNG, TRNG_index, rfm9x
  init()
  # send a first broadcast message
  sendPacket()
  # initialize timer
  time_now = time.monotonic() - transmit_interval
  while True:
    if time.monotonic() - time_now > transmit_interval:
      # send a broadcast message
      sendPacket()
      # reset timeer
      time_now = time.monotonic()
      counter = counter + 1
    # Wait to receive packets.
    print("Waiting for packets...")
    display.text("Waiting for packets...", 0, posY, 1, font_name='font5x8.bin')
    display.show()
    # Look for a new packet - wait up to 30 seconds:
    pixels.fill((0, 255, 255))
    pixels.show()
    packet = rfm9x.receive(timeout=10, with_header=True)
    # If no packet was received during the timeout then None is returned.
    pixels.fill((0, 0, 0))
    pixels.show()
    if packet is not None:
      # Received a packet!
      pixels.fill((0, 255, 0))
      pixels.show()
      time.sleep(1.0)
      display.fill(0)
      posY = 5
      display.text("Incoming!", 20, posY, 1, font_name='font5x8.bin')
      posY += 10
      print("\nReceived ("+str(len(packet))+" raw bytes) at RSSI: "+str(rfm9x.rssi)+", SNR: "+str(rfm9x.snr))
      hexDump(packet)
      # send reading after any packet received
      rslt = decryptBuffer(packet, cipher)
      if rslt != b'':
        # if rslt is empty, we failed to decrypt: ignore
        ix = rslt.find(b'\x00')
        #There may be padding bytes after 0x00
        #Remove them
        if ix > -1:
          padding = rslt[ix+1:]
          #print("padding length: "+str(len(padding)))
          #print("padding byte: "+str(padding[0]))
          if len(padding) == padding[0] - 1:
            # messages from Minimal_LoRa are padded with the remaining length as the padding byte
            # ie if there are 11 bytes of padding, we use 0x0b.
            # but the first byte of padding is turned into 0x00, string terminator, to make things easier.
            print("proper padding")
          else:
            print("incorrect padding")
          # Not very important but let's be precise.
        js=0
        # so that later we know whether the JSON parsing succeeded or not
        try:
          js=json.loads(rslt[0:ix].decode())
          # if ix is -1 (nothing found) rslt[0:ix] is the full bytearray
        except:
          print("Error parsing JSON")
        if js != 0:
          UUID = js['UUID']
          sender = js['from']
          cmd = js['cmd']
          print(js)
          print("\n+---------------------------+")
          print(' RSSI   : '+str(rfm9x.rssi))
          print(' SNR    : '+str(rfm9x.snr))
          display.text('RSSI: '+str(rfm9x.rssi)+" SNR: "+str(rfm9x.snr), 0, posY, 1, font_name='font5x8.bin')
          posY += 10
          print(' UUID   : ' + UUID)
          display.text('UUID: ' + UUID, 0, posY, 1, font_name='font5x8.bin')
          posY += 10
          print(' from   : ' + sender)
          display.text('from: ' + sender, 0, posY, 1, font_name='font5x8.bin')
          posY += 10
          print(' cmd    : ' + cmd)
          display.text('cmd: ' + cmd, 0, posY, 1, font_name='font5x8.bin')
          posY += 10
          if cmd == 'pong':
            rcvRSSI = js['rcvRSSI']
            try:
              print(' rcvRSSI: '+str(js['rcvRSSI']))
              display.text('rcvRSSI: '+str(js['rcvRSSI']), 0, posY, 1, font_name='font5x8.bin')
              posY += 10
            except e:
              print(' rcvRSSI: none')
              display.text('rcvRSSI: none', 0, posY, 1, font_name='font5x8.bin')
              posY += 10
          if cmd == 'msg':
            print(' msg  :  '+js['msg'])
            display.text('msg:  '+js['msg'], 0, posY, 1, font_name='font5x8.bin')
          print("+---------------------------+\n")
      else:
        display.text("JSON Parse Error!", 0, 30, 1, font_name='font5x8.bin')
      display.show()
      pixels.fill((0, 0, 0))
      pixels.show()
    else:
      print("Rx Timeout!")
