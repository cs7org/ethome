# ETHome

ETHome is a proof of concept of a blockchain based organization of a local low voltage energy community. The focus of the concept is efficient use of shared resources to minimize external dependence, and not energy trading. A previously proposed control algorithm, which exploits the power dependency of the efficiency of electrical energy storages, is implemented as a smart contract on a private instance of an Ethereum blockchain to coordinate the operation. It is implemented using four connected Raspberry Pis representing the participating households with pre-given electrical load and photovoltaic conversion as well as a battery. Each household runs an Ethereum full node and an interfacing software. Only the energy technology components are simulated, while the blockchain is actually running on the Raspberry Pis in order to mind the full complexity of the technology.

More info and evaluation of the concept can be found in the original paper:
Jonas Schlund, Lorenz Ammon and Reinhard German, “ETHome: Open-source blockchain based energy community controller,” Ninth ACM International Conference on Future Energy Systems (ACM e-Energy), June 12-15 2018
https://doi.org/3208903.3208929

## Quickstart
Follow these steps to quickly set up the project yourself. 
* make sure you have you private PoA Ethereum network or any test network up and running with a couple of nodes. In our case we used 4 Rasperry Pis in order to represent 4 participating houses. [This](http://chainskills.com/2017/02/24/create-a-private-ethereum-blockchain-with-iot-devices-16/) is a good instruction how to set up the private chain.
* deploy the smart contract ([CommunityController.sol](https://github.com/cs7org/ethome/blob/master/scripts/CommunityController.sol))
```
import json
from solc import compile_source
from web3 import Web3, HTTPProvider

fr = open('CommunityController.sol')
contract_source_code = fr.read()
fr.close()

compiled_sol = compile_source(contract_source_code)
contract_interface = compiled_sol['<stdin>:CommunityController_v13']

#save the abi for contractWrapper-nodes
fw = open('CommunityController_abi.json', 'w+')

json.dump(contract_interface['abi'], fw)
fw.close()

web3 = Web3(HTTPProvider('http://localhost:xxxx')) # replace xxxx 
contract = web3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
tx_hash = contract.deploy(transaction={'from': web3.eth.accounts[0], 'gas': 4100000})
tx_receipt = web3.eth.getTransactionReceipt(tx_hash)
contract_address = tx_receipt['contractAddress']
```
* adjust the contract and node addresses in addresses.py
* register all the participants with their optimal operation points (in mW)
```
from web3 import Web3, HTTPProvider
web3 = Web3(HTTPProvider('http://localhost:xxxx')) # replace xxxx 
import addresses
from contractWrapper import contractWrapper
c=contractWrapper(addresses.CommunityController,'http://localhost:xxxx',0)
c.register(1500000,1500000) #optimal operation points for charging / discharging
```
* adjust your source file path for photovoltaic supply and household demand and the path for the logger in [node.py](https://github.com/cs7org/ethome/blob/master/scripts/node.py)
* make sure the timeStep is in accordance with the resolition of your source files for photovoltaic supply and household demand
* adjust the host port for the contractWrapper in [node.py](https://github.com/cs7org/ethome/blob/master/scripts/node.py)
* parameterize the battery model ([battery.py](https://github.com/cs7org/ethome/blob/master/scripts/battery.py)) or adapt your own battery model considering the interfaces
* start [node.py](https://github.com/cs7org/ethome/blob/master/scripts/node.py) in all of your nodes

## Contributing

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the owners of this repository before making a change. 
