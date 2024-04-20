from time import sleep_ms, ticks_ms                                #include delay time
from machine import I2C, Pin                                       #include hardware device
                                   #define LCD1602 Function device

#import pyb
from machine import UART                                    #include hardware device
from machine import Pin                                     #include hardware device
from time import sleep_ms,sleep_us                          #include delay time


class DHT11:
    def __init__(self,pin_name):
        sleep_ms(1000)
        self.N1 = Pin(pin_name, Pin.OUT)
        self.PinName=pin_name
        sleep_ms(10)
    def read_data(self):
        self.__init__(self.PinName)
        data=[]
        j=0
        N1=self.N1
        N1.low()
        sleep_ms(20)
        N1.high()
        N1 = Pin(self.PinName, Pin.IN)
        sleep_us(30)
        if N1.value() != 0:
            return [0,0]
        while N1.value()==0:
            continue
        while N1.value()==1:
            continue
        while j<40:
            k=0
            while N1.value()==0:
                continue
            while N1.value()==1:
                k+=1
                if k>100:break
            if k<3:
                data.append(0)
            else:
                data.append(1)
            j=j+1
        print('Sensor is working')
        j=0
        humidity_bit=data[0:8]
        humidity_point_bit=data[8:16]
        temperature_bit=data[16:24]
        temperature_point_bit=data[24:32]
        check_bit=data[32:40]
        humidity=0
        humidity_point=0
        temperature=0
        temperature_point=0
        check=0
        for i in range(8):
            humidity+=humidity_bit[i]*2**(7-i)
            humidity_point+=humidity_point_bit[i]*2**(7-i)
            temperature+=temperature_bit[i]*2**(7-i)
            temperature_point+=temperature_point_bit[i]*2**(7-i)
            check+=check_bit[i]*2**(7-i)
        tmp=humidity+humidity_point+temperature+temperature_point
        if check==tmp:
            print('temperature is',temperature,'-wet is',humidity,'%')
        else:
            print('Error:',humidity,humidity_point,temperature,temperature_point,check)
        return [str(temperature),str(humidity)]


# The PCF8574 has a jumper selectable address: 0x20 - 0x27         
DEFAULT_I2C_ADDR = 0x27#0X27#                                      #define I2C Address

dht = DHT11(34)                                                    #define DHT11 pin function:GP15
def readTaHData():
    DATA = dht.read_data()    
    t = DATA[0]                                                    #read Temp.& Humidity
    h = DATA[1]                                                    
    return [str(t),str(h)]                                         

if __name__ == "__main__":    
    while True:
        dat = readTaHData()                                        #read Temp.& Humidity     
        sleep_ms(1000)                                             #delay time 1000ms
        print( readTaHData() )
