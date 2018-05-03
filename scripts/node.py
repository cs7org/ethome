#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@authors: Lorenz Ammon, Jonas Schlund
"""

import time, datetime
import logging #https://docs.python.org/3/library/logging.html#logging-levels https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
logging.basicConfig(level=logging.DEBUG)
Logging = logging.getLogger(__name__)

import dataIn
dataPV = dataIn.dataIn(logging.getLogger("dataPV"), '../yourpath/yourPVsourcefile.txt',False) #call class dataIn of module dataIn
dataHH = dataIn.dataIn(logging.getLogger("dataHH"), '../yourpath/yourHHsourcefile.txt',False)

import log
logger = log.log(logging.getLogger("logger"), datetime.datetime.now().strftime("../yourpath/log-%Y%m%d-%H%M%S.csv"))
logger.newEntry(['blocknumber[-]','number_of_users[-]','battery_management_command[mW]','power_battery[mW]','power_residual[mW]','SOC[m%]','load_household[mW]','production_pv[mW]', 'losses_ch[mWs]', 'losses_dch[mWs]', 'losses_idle_int[mWs]', 'losses_idle_ext[mWs]', 'time waited[us]'])

import addresses #addresses of nodes & contract

from numpy import mean

from contractWrapper import contractWrapper #communication with contract via web3
c=contractWrapper(addresses.CommunityController,'http://localhost:xxxx',0) # insert your port

import battery #simple battery model
b=battery.battery(4,3,4,0) #Net capacity: 4kWk, maximum power: 3kW (charging), 4kW (discharging), Net energy content at start: 0kWh

#optional factors to scale the input data
facPV = 1
facHH = 1

setValue = 0 #charging/discharging command for battery management

Pbat = 0 #charging/discharging action of battery

counter = 0 #counter in order to estimate when next block is expected

mAvgCounter  = 0 #counter for 15s mAvg

timeStep = 1 #timeStep for while loop, in accordance with input data

tw = 0 #waiting time

t1 = time.time() #start time for sleep duration

#read in next load and production data
pv = dataPV.nextValue() * facPV
hh = dataHH.nextValue() * facHH

#calculate residual load
Pres = hh-pv
mAvg=[]
for i in range(0,30):
    mAvg.append(Pres)

while dataPV.valuesLeft() and dataHH.valuesLeft():
    try:
        #new block?
        if c.checkForNewBlock():
            Logging.info("New block found")
            #Get new command for battery management from blockchain
            setValue = c.getSetValue()
            Logging.info("New Set Value: " + str(setValue))
            #Post new values to blockchain
            counter = 0
        #no new block
        else:
            #wait till new block is expected to come, then post new status
            counter+=timeStep
            if counter >12:
                #either post current value or moving average 
                c.postStatus(Pres,b.SOC()) 
                #c.postStatus(int(mean(mAvg)),b.SOC()) #post mean of moving average in order to avoid posting a momentary peak
                counter=7
        noUsers = c.getNoUsers()
    except Exception as e:
        Logging.info(e)
        setValue=Pres
        Logging.info("Operating battery alone: " + str(setValue))
        noUsers = 0
    #charge/discharge battery according to setValue for the next timeStep
    if setValue > 0:
        Pbat = b.discharge(setValue,timeStep)
    elif setValue == 0:
        Pbat = b.idle(timeStep)
    else:
        Pbat = b.charge(setValue,timeStep)

    logger.newEntry([c.getBlock(),noUsers,setValue,Pbat,Pres,b.SOC(),hh,pv,b.E_losses_charge(),b.E_losses_discharge(),b.E_losses_idle_internal(),b.E_losses_idle_external(),tw]) #load and production just to have it in the same file)
    
    t2 = time.time() #Logging.info("Sleep duration: %f" % (1 - t2 + t1))
    time.sleep(max(timeStep - t2 + t1,0)) #wait one timeStep minus execution time until next run; TODO: fix workaround 
    tt = time.time() #start time for sleep duration
    tw = (timeStep - t2 + t1)*1000000
    #Logging.info('Waited for ' + str(tw) + 'ms')
    t1 = tt
    #read in next load and production data
    pv = dataPV.nextValue() * facPV
    hh = dataHH.nextValue() * facHH
    
    #calculate residual load
    Pres = hh-pv

    #add Pres in mAvg
    mAvg[mAvgCounter%30]=Pres
    mAvgCounter+=1

Logging.debug('Exited loop')
