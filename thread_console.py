'''
Created on 8 Mar 2024

@author: Anthony Moulds

Assumptions:
1. All thread devices have Openthread CLI uart interface.
2. All thread devices have 'Zephyr' given as their platform, i.e. firmware developed using Zephyr libs.
2. The TTM thread device has 'NRF5280' in as its version string. 

Expanded on 15 May 2024
1. Added support for EFR32 Silicon Labs boards
2. 
'''


import serial
import time
import os.path



NETWORKKEY = '00112233445566778899aabbccddeeff'
CHANNEL = '15'
PANID = '0xabcd'

FTD_TXPOWER = 0 # dBm
MTD_TXPOWER = -40 # dBm


PING_TARGET_IPADDR = 'fe80:0:0:0:98fc:1b54:7b61:991a'
#PING_TARGET_IPADDR = 'fe80:0:0:0:5039:3727:380:4845'

class ThreadConsole:
    
    def __init__(self, channel, panid, networkkey):  
        self.noOfFoundDevices = 0
        self.threadDevices = []
        self.zephyrDevices = []
        self.efr32Devices = []
        self.channel = channel
        self.panid = panid
        self.networkkey = networkkey
        
    def readSerial(self, com):
        data = com.read(200)     
        return data.decode('utf-8')
        
    def writeSerial(self, com, x):
        com.write(bytes(x, 'utf-8'))
        com.flush()
               
    def writeReadSerial(self, com, x):
        self.writeSerial(com, x)  
        if x in self.efr32Devices:
            com.replace('ot ', '')
        com.readline() # ignore echo'd line    
        return self.readSerial(com)
        
    def printSerial(self,com):
        com.readline() # ignore fist line (echo'd line)             
        r = com.read(80) # upto 10 lines
        print (r.decode("utf-8"))     
        
    def findOtDevices(self):
        print("searching...")
        ttydev = "/dev/ttyACM"         
        self.noOfFoundDevices = 0       
        self.threadDevices = []
        for i in range(1, 20, 1):
            dev = ttydev + str(i)
            if(os.path.exists(dev)):
                #print ("%s exists!" % dev)finf
                try:             
                    # check if we can open it
                    with serial.Serial(dev, baudrate=115200, timeout=0.1, write_timeout=1.0) as ser:
                     
                            rcv = self.writeReadSerial(ser,"ot platform\r\n")                            
                            if(rcv.find("Zephyr") != -1):       
                                print(r"found nRF board")                        
                                self.threadDevices.append(dev)
                                self.zephyrDevices.append(dev)
                                self.noOfFoundDevices += 1
                            rcv = self.writeReadSerial(ser,"platform\r\n")                            
                            if(rcv.find("EFR32") != -1):       
                                print(r"found EFR32 board")                        
                                self.threadDevices.append(dev)
                                self.efr32Devices.append(dev)
                                self.noOfFoundDevices += 1
                except:
                    continue
        return self.noOfFoundDevices


    def configDevice(self, device, otCmds):   
        with serial.Serial(device, baudrate=115200, timeout=0.1, write_timeout=1.0) as ser:
            self.readSerial(ser) # flush read buf
            for cmd in otCmds:
                try:    
                    #print(cmd)              
                    rcv = self.writeReadSerial(ser, cmd + "\r\n")   
                    #print(rcv) 
                    time.sleep(0.1)               
                except:
                    return -1
        return 0


    def configDeviceAsRouter(self,device, txPower):
        print("[%s] configured as FTD" %device)
        otCmds = []   
        otCmds.append("")
        otCmds.append("ot txpower " + str(txPower))
        otCmds.append("ot mode rdn")
        otCmds.append("ot mode dataset init new")        
        otCmds.append("ot dataset channel " + self.channel)
        otCmds.append("ot dataset networkkey " + self.networkkey)
        otCmds.append("ot dataset panid " + self.panid)
        otCmds.append("ot dataset commit active")
        self.configDevice(device, otCmds)
    
    
    def configDeviceAsChild(self,device, txPower):
        print("[%s] configured as MTD" %device)
        otCmds = []   
        otCmds.append("\r\n")
        otCmds.append("ot txpower " + str(txPower))
        otCmds.append("ot mode rn")
        otCmds.append("ot dataset channel " + self.channel)
        otCmds.append("ot dataset networkkey " + self.networkkey)
        otCmds.append("ot dataset panid " + self.panid)
        otCmds.append("ot dataset commit active")
        self.configDevice(device, otCmds)


    def softReset(self, device):
        #print(device)
        otCmds = []   
        otCmds.append("\r\n")
        otCmds.append("ot thread stop")
        otCmds.append("ot ifconfig down")
        self.configDevice(device, otCmds)
        
    def softRestart(self,device):       
        self.stop(device) 
        time.sleep(2.0)
        self.start(device)

    def start(self, dev):      
        rcv = self.writeReadSerial(dev, "\r\not ifconfig up\r\n")    
        if(rcv.find("Done") == -1): 
            return -1  
        rcv = self.writeReadSerial(dev, "\r\not thread start\r\n")   
        if(rcv.find("Done") == -1): 
            return -1  
        return 0

    def stop(self, dev):      
        rcv = self.writeReadSerial(dev, "\r\not thread stop\r\n")   
        if(rcv.find("Done") == -1): 
            return -1  
        rcv = self.writeReadSerial(dev, "\r\not ifconfig down\r\n")
        if(rcv.find("Done") == -1): 
            return -1  
        return 0
              
    def startAll(self):                                         
        for device in self.threadDevices:
            with serial.Serial(device, baudrate=115200, timeout=0.1, write_timeout=1.0) as ser:  
                if(self.start(ser)):
                    print("failed to start %d thread device!" % device)
                time.sleep(0.1)

    def stopAll(self):                                         
        for device in self.threadDevices:
            with serial.Serial(device, baudrate=115200, timeout=0.1, write_timeout=1.0) as ser:  
                if(self.stop(ser)):
                    print("failed to stop %d thread device!" % device)
                time.sleep(0.1)
                
    def softResetAllDevices(self):
        for device in self.threadDevices:
            with serial.Serial(device, baudrate=115200, timeout=0.1, write_timeout=1.0) as ser:  
                self.softReset(ser)

    def softRestartAllDevices(self):
        for device in self.threadDevices:
            with serial.Serial(device, baudrate=115200, timeout=0.1, write_timeout=1.0) as ser:  
                self.softRestart(ser)
                        
        
    def resetAllDevices(self):
        print("resetting network devices...")
        for device in self.threadDevices:
            with serial.Serial(device, baudrate=115200, timeout=0.1) as ser:   
                self.writeSerial(ser, "\r\not reset\r\n")               
        time.sleep(5)
        for device in self.threadDevices:
            with serial.Serial(device, baudrate=115200, timeout=0.1) as ser:                 
                self.writeSerial(ser, "\r\n")  
 
    def hardResetAllDevices(self):  
        pass
              

    def setTTMTxPower(self, txpower):       
        device = self.findTTMDevice()
        if(device == 'none'):
            print("unable to find TTM device!")
            return       
        with serial.Serial(device, baudrate=115200, timeout=0.1) as ser:
            self.writeSerial(ser, "\r\not txpower " + txpower + "\r\n")  
                            
            
    def showDeviceState(self):
        for device in self.threadDevices:
            with serial.Serial(device, baudrate=115200, timeout=0.1) as ser:        
                r = self.writeReadSerial(ser, "ot state\r\n")           
                r = r.replace("uart:~$", '')
                r = r.replace("ot state", '')            
                r = r.replace("Done",'')
                r = r.strip()                    
                s = "unknwown"
                if(r.find("child") != -1):
                    s = "child"
                if(r.find("disabled") != -1):
                    s = "disabled"
                if(r.find("detached") != -1):
                    s = "detached"
                if(r.find("router") != -1):
                    s = "router"
                if(r.find("leader") != -1):
                    s = "leader"                                
                print("[%s] thread state = %s" % (device,s))
  
        
    def configNetwork(self):
        # first, reset network
        #self.resetAllDevices()
        #self.softResetAllDevices()
        
        # configure a device as FTD to act as router
        self.configDeviceAsRouter(self.threadDevices[0], 0)
        # configure others as MTD devices
        for i in range(1,len(self.threadDevices)):
            self.configDeviceAsChild(self.threadDevices[i], -40)  

    def listDevices(self):
        for device in self.threadDevices:
            print(device)
    
    def findTTMDevice(self):
        print("searching...")
        ttydev = "/dev/ttyACM"         
        self.noOfFoundDevices = 0       
        self.threadDevices = []
        for i in range(1, 20, 1):
            dev = ttydev + str(i)
            if(os.path.exists(dev)):
                try:
                    with serial.Serial(dev, baudrate=115200, timeout=0.1, write_timeout=1.0) as ser:    
                        self.writeReadSerial(ser, "\r\n")  
                        self.writeReadSerial(ser, "\r\n")                     
                        self.writeSerial(ser, "version\r\n")                            
                        rcv = self.readSerial(ser)  
                        self.readSerial(ser)  
                        if(rcv.find("NRF52840") != -1):   
                            return dev    
                except:
                    pass
        return "none"
            
    
def main():
    cmd = ' '
    
    console = ThreadConsole(panid=PANID, channel=CHANNEL, networkkey=NETWORKKEY)
    
    while (cmd != 'quit'):
        cmd = input("> ")
        if(cmd == "quit" or cmd == 'q'):
            print("quiting...\n")
            continue
        
        elif(cmd == "state"):
            console.findOtDevices()
            console.showDeviceState()

        elif(cmd == "config"):                    
            print ("finding openthread devices...")
            console.findOtDevices()
            print("found %d nRF devices" % console.noOfFoundDevices)        
            if (console.noOfFoundDevices):                   
                print ("configuring thread network:")
                console.configNetwork()
                
        elif(cmd == "reset"):             
            if(console.noOfFoundDevices == 0):
                console.findOtDevices()
            console.softResetAllDevices()
 
        elif(cmd == "restart"):             
            if(console.noOfFoundDevices == 0):
                console.softRestartAllDevices()
                           
        elif(cmd == "hreset"):             
            console.hardResetAllDevices()

        elif(cmd == "ttmpower"):
            txpower = input("enter tx power in dBm: ")
            if(txpower == "0" or txpower == "-20" or txpower == "-40"):
                console.setTTMTxPower(txpower)    
                print("done")
                
        elif(cmd == "find"):  
            nD = console.findOtDevices()        
            if(nD):
                print("found %d thread devices" % nD)
                #for dev in console.threadDevices:
                #    print("[%s]" % dev)
            else:
                print("no thread devices found!")      

        elif(cmd == "find ttm"):  
            dev = console.findTTMDevice()
            if(dev == "none"):
                print("unable to find TTM")
            else:
                print("TTM on port %s" % dev)
                            
        elif(cmd == "list"):
            console.listDevices()
                      

        elif(cmd == "start"): 
            if (console.noOfFoundDevices):                   
                print ("starting thread devices...")
                console.startAll()  
                print("done")
            else:
                print("you need to configure thread devices first!")      

        elif(cmd == "stop"): 
            if (console.noOfFoundDevices):                   
                print ("stopping thread devices...")
                console.stopAll()  
                print("done")
            else:
                print("you need to configure thread devices first!")  
                                                          
        elif(cmd == "help" or cmd == 'h'):
            print("help menu:")
            print("config\t\tconfigure thread devices")
            print("find\t\tfind number of thread devices")
            print("find ttm\tfind the TTM thread device and report its tty allocation")
            print("list\t\tlist found thread devices")            
            print("reset\t\treset all thread devices")
            print("restart\t\trestart all thread devices")
            print("start\t\tstart the thread devices")
            print("stop\t\tstop the thread devices")
            print("state\t\tshow status of all thread devices")
            print("ttmpower\tset TTM device tx power strength in dBm")
            print("quit\t\tquit")   
        
        elif(len(cmd) != 0):
            print("unknown command!")         



if __name__ == '__main__':
    
    main()
    
    