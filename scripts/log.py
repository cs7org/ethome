#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Lorenz Ammon
"""

import csv #https://docs.python.org/3/library/csv.html
import datetime

class log(object):
    def __init__(self, Logging, file):
        self.Logging = Logging
        self.Logging.debug('Writing log to file %s' % file)
        self.f = open(file, 'w+', newline='')
        self.csvwriter = csv.writer(self.f, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    def newEntry(self, array):
        array.insert(0, datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+%f"))
        self.csvwriter.writerow(array)
        self.f.flush()
    def __del__(self):
        pass
