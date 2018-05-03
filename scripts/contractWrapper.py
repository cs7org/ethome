#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@authors: Lorenz Ammon, Jonas Schlund
"""
#https://pypi.python.org/pypi/web3/4.0.0b5
#https://web3py.readthedocs.io/en/stable/overview.html#overview-type-conversions
#https://web3py.readthedocs.io/en/stable/contracts.html
#https://github.com/ethereum/wiki/wiki/Ethereum-Contract-ABI

import json
from web3 import Web3, HTTPProvider
from web3.contract import Contract#ConciseContract

class contractWrapper(object):
    def __init__(self, address, host, account):
        self.contractAddress = address
        self.web3 = Web3(HTTPProvider(host))
        self.account = account
        
        abiFile = open('CommunityController_abi.json')
        abi = json.load(abiFile)
        abiFile.close()
        self.contract_inst = self.web3.eth.contract(abi, self.contractAddress, ContractFactoryClass=Contract)
        
        self.blockNumber = self.web3.eth.blockNumber
        self.noUsers=self.contract_inst.call({'from': self.web3.eth.accounts[self.account]}).numberOfAdresses()
    def getSetValue(self):
        return self.contract_inst.call({'from': self.web3.eth.accounts[self.account]}).readInstruction()
    def postStatus(self, Pres, SOC):
        self.contract_inst.transact({'from': self.web3.eth.accounts[self.account]}).setSOC(SOC)
        self.contract_inst.transact({'from': self.web3.eth.accounts[self.account]}).setPres(Pres)
    def checkForNewBlock(self):
        if self.web3.eth.blockNumber<=self.blockNumber:
            return False
        else:
            self.blockNumber=self.web3.eth.blockNumber
            self.noUsers=self.contract_inst.call({'from': self.web3.eth.accounts[self.account]}).numberOfAdresses()
            return True
    def register(self,PoptCh,PoptDch):
        self.contract_inst.transact({'from': self.web3.eth.accounts[0]}).register(PoptCh,PoptDch)
    def getBlock(self):
        return self.blockNumber
    def getNoUsers(self):
        return self.noUsers
    def __del__(self):
        pass
