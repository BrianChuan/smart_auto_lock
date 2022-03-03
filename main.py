# 接腳說明: GPIO 19 接至 RFID SPI MOSI(IO3)-45
#           GPIO 21 接至 RFID SPI MISO(IO4)-44
#           GPIO 23 接至 RFID SPI SCLK(IO2)-RxD3
#           GPIO 24 接至 RFID SPI SDA (IO1)-TxD3
#
import RPi.GPIO as GPIO
import MFRC522
import signal
import time, threading

continue_reading = True
card_uid = [0,0,0,0]
user_card = [243,165,101,215]
judge = 0

passwd = [1,2,3,4]
keyin_pw = [0,0,0,0]
time_ = 0



# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print ("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()
   
# DCmotor setup
GPIO.setmode(GPIO.BOARD)
PA            = 33
PB            = 35
PIN_IN        = 37
GPIO.setup(PA, GPIO.OUT) 
pwm1 = GPIO.PWM(PA, 50)
pwm1.start(0)
GPIO.setup(PB, GPIO.OUT)
pwm2 = GPIO.PWM(PB, 50)
pwm2.start(0)

GPIO.setup(38,GPIO.OUT)
p = GPIO.PWM(38,200)


# GPIO DEFINE     27 28 can not use for output
pin_kb_data  = [3,5,7,8]
pin_kb_com   = [10,11,12,13]

TimerCnt_5ms = 1 

for i in range(4):                                #KEYBOAED SCAN
  GPIO.setup(pin_kb_com[i], GPIO.OUT)   
for i in range(4):
  GPIO.output(pin_kb_com[i], True)

for i in range(4):                                #KEYBOAED DATA 
  GPIO.setup(pin_kb_data[i], GPIO.IN)  
  
key_input = 0
scan_key  = 0
key_count = 0
   

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print("please input the password or use the RFID card")

pwm1.ChangeDutyCycle(0)
pwm2.ChangeDutyCycle(0)

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print( "Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
    
        judge = 0
        for i in range (4):
            card_uid[i] = uid[i]
        
        if (card_uid == user_card):
            print("unlock")
            p.start(50)
            time.sleep(0.05)
            p.stop()
            pwm1.ChangeDutyCycle(100)
            pwm2.ChangeDutyCycle(0)
            time.sleep(2)
            pwm1.ChangeDutyCycle(0)
            pwm2.ChangeDutyCycle(0)
            
            
    #key board scan---   
    key_input = 0
    scan_key  = 0x10
   
    for i in range(4): 
      for j in range(4):                            #close all
         GPIO.output(pin_kb_com[j], True)              
      GPIO.output(pin_kb_com[i], False)             #open scan 
      time.sleep(0.0005)
      
      if GPIO.input(pin_kb_data[0]) == 0:             
         key_input = key_input | 0x01
         
      if GPIO.input(pin_kb_data[1]) == 0:             
         key_input = key_input | 0x02  
      if GPIO.input(pin_kb_data[2]) == 0:             
         key_input = key_input | 0x04  
      if GPIO.input(pin_kb_data[3]) == 0:             
         key_input = key_input | 0x08

      if key_input != 0:
         if key_input == 0x01:             
            key_input = 0 
         elif  key_input == 0x02:             
            key_input = 1 
         elif key_input == 0x04:             
            key_input = 2 
         elif key_input == 0x08:             
            key_input = 3 
         key_input = key_input + (i * 4) 
         i = 10
         break
    
    if i > 3 :
             #have key in
        keyin_pw[time_] = key_input
        time_ = time_+1
        print(keyin_pw)
        if time_ == 4:
            time_ = 0
            if keyin_pw == passwd:
                print("unlock")
                keyin_pw =[0,0,0,0]
                p.start(50)
                time.sleep(0.05)
                p.stop()
                pwm1.ChangeDutyCycle(100)
                pwm2.ChangeDutyCycle(0)
                time.sleep(2)
                pwm1.ChangeDutyCycle(0)
                pwm2.ChangeDutyCycle(0)
                print("lock")
            else:
                print("wrong")
                keyin_pw =[0,0,0,0]
           
      
