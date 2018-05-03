#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@authors: Lorenz Ammon, Jonas Schlund
"""
import datetime

class dataIn(object):
    def __init__(self, Logging, file, setPointer):
        self.Logging = Logging
        f = open(file)
        self.values = f.read().splitlines() #read file in without newline-characters, instead of just readlines()
        self.values = list(map(int,self.values)) #convert to int
        self.valuesTotal = len(self.values)
        #self.valueNext = 0;
        self.Logging.debug('Read in %i values from file %s' % (self.valuesTotal, file))
        f.close()
        if setPointer: #sets the nextValue to current time
            now = datetime.datetime.now()
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            seconds = (now - midnight).seconds
            self.valueNext = seconds
        else:
            self.valueNext = 0
    def valuesLeft(self):
        return self.valueNext < self.valuesTotal
    def nextValue(self):
        #self.Logging.debug('Giving the next value, value %i out of %i minus 1: %i' % (self.valueNext, self.valuesTotal, self.values[self.valueNext]))
        self.valueNext += 1
        return self.values[self.valueNext-1]
    def __del__(self):
        pass
