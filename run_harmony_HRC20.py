from ast import Constant
from secp256k1 import *
from web3 import Web3, EthereumTesterProvider
from eth_utils import event_abi_to_log_topic, to_hex
import json
import sys


# Load abi
with open("./abi/abi_iris.json") as f:
    info_json = json.load(f)
abi_iris = info_json

# Connect to harmony
w3 = Web3(Web3.HTTPProvider('https://api.harmony.one'))

# Contract address
my_contract_address = '0x85FD5f8dBD0c9Ef1806E6c7d4B787d438621C1dC'


# Instantiate contract
contractInstance = w3.eth.contract(address=my_contract_address, abi=abi_iris)

###
### Utility Function
###

def decode_tuple(t, target_field):
    output = dict()

    for i in range(len(t)):
        if isinstance(t[i], (bytes, bytearray)):
            output[target_field[i]['name']] = to_hex(t[i])
        elif isinstance(t[i], (tuple)):
            output[target_field[i]['name']] = decode_tuple(t[i], target_field[i]['components'])
        else:
            output[target_field[i]['name']] = t[i]
    return output

def decode_list_tuple(l, target_field):
    output = l

    for i in range(len(l)):
        output[i] = decode_tuple(l[i], target_field)
    return output

def decode_list(l):
    output = l
    for i in range(len(l)):
        if isinstance(l[i], (bytes, bytearray)):
            output[i] = to_hex(l[i])
        else:
            output[i] = l[i]
    return output

def convert_to_hex(arg, target_schema):
    """
    utility function to convert byte codes into human readable and json serializable data structures
    """
    output = dict()
    for k in arg:
        if isinstance(arg[k], (bytes, bytearray)):
            output[k] = to_hex(arg[k])
        elif isinstance(arg[k], (list)) and len(arg[k]) > 0:
            target = [a for a in target_schema if 'name' in a and a['name'] == k][0]
            if target['type'] == 'tuple[]':
                target_field = target['components']
                output[k] = decode_list_tuple(arg[k], target_field)
            else:
                output[k] = decode_list(arg[k])
        elif isinstance(arg[k], (tuple)):
            target_field = [a['components'] for a in target_schema if 'name' in a and a['name'] == k][0]
            output[k] = decode_tuple(arg[k], target_field)
        else:
            output[k] = arg[k]
    return output


###
### Functions
###
# 
# search for the creator searching by each block and checking each transaction
# explanation: We loop transaction up to the point we found the transaction that created the contract
# See: https://ethereum.stackexchange.com/questions/65194/get-creator-from-contract-address
#      https://stackoverflow.com/questions/54056587/how-to-get-the-address-of-the-contract-creator


def getContractCreatorAddress(inputContractAddress):
    currentBlockNum =w3.eth.blockNumber
    txFound = 0

    while currentBlockNum >= 0 and txFound==0 :
        block = w3.eth.getBlock(currentBlockNum, True)
        transactions = block.transactions

        print ("We are in block: " + str(currentBlockNum))

        for transaction in block.transactions:
            print ("Searching transaction: " + str(transaction))
            #We know this is a Contract deployment
            if transaction['to'] != None:
                receipt = w3.eth.getTransactionReceipt(transaction['hash'].hex())
                print ("Initializer of transaction " + transaction['to'] )
                print ("Looking at hash: " + str(transaction.hash) )
                print ("Looking at hash: " + str(transaction['hash'].hex()) )
                print ("Found contract address: " + str(receipt.contractAddress) )
                
                if receipt.contractAddress != None and receipt.contractAddress.toLowerCase() == inputContractAddress.toLowerCase():
                    txFound = 1;
                    contractCreator = transactions['from']
                    print("Contract Creator Address: " + transactions['from'])
                    break;

        currentBlockNum = currentBlockNum - 1

    return contractCreator

###
### Search for the block where the contract was created
###
def getContractCreationBlock(contract_address):
    highest_block = w3.eth.blockNumber
    lowest_block = 0

    contract_code = w3.eth.getCode(contract_address, highest_block);
    if contract_code == "0x":
        # print("Contract " + contract_address + " does not exist!")
        return -1

    while lowest_block <= highest_block:
        search_block = ((int)((lowest_block + highest_block) / 2))
        # print("lowest_block: " + str(lowest_block))
        # print("search_block: " + str(search_block))
        # print("highest_block: " + str(highest_block))

        contract_code = w3.eth.getCode(contract_address, search_block)
        # print("contract_code: " + contract_code.hex())

        if contract_code.hex() != '0x':
            highest_block = search_block;
        elif contract_code.hex() == '0x':
            lowest_block = search_block;

        if highest_block == lowest_block + 1:
            return highest_block;
            
def getContractCreatorAddress_v2(blockIn, contractAddressIn):
    block = w3.eth.getBlock(blockIn)

    transactions = block.transactions

    for transaction in transactions:
        # print("Transaction: " + transaction.hex())
        receipt = w3.eth.getTransactionReceipt(transaction.hex())

        # print("Receipt: " + str(receipt))

        if (receipt.contractAddress == contractAddressIn):
            return receipt['from']
    return -1;

###
### Get transaction from the blockchain
###
def fetchTransactionForHRC20(contractAddressIn, blockContractCreation):
    currentBlockNum =w3.eth.blockNumber
    fetchTransactionForHRC20BetweenBlocks(contractInstanceIn, blockContractCreation, currentBlockNum)



###
### For better testing we divide into a smaller function so we can express called the blocks interval 
###
def fetchTransactionForHRC20BetweenBlocks(contractInstanceIn,   blockContractCreation, blockContractFinish):
    currentBlockNum = blockContractFinish

    while currentBlockNum >= blockContractCreation:
        block = w3.eth.getBlock(currentBlockNum, True)

        print ("We are in block: " + str(currentBlockNum))

        for transaction in block.transactions:
            print ("Searching transaction: " + str(transaction['hash'].hex()))
            #We know this is a Contract deployment
            if transaction['to'] != None and transaction['to'] == contractInstanceIn.address:
                print ("Looking at hash: " + str(transaction['hash'].hex()) )

                #Get receipt just to log some details
                receipt = w3.eth.getTransactionReceipt(transaction['hash'].hex())
                print ("Initializer of transaction " + transaction['to'] )
                print ("Found hash: " + str(transaction['hash'].hex()) )
                print ("Found receipt: " + str(receipt) )
                print ("Found logs: " + str(receipt['logs']) )
                print ("Found logs data: " + str(receipt['logs'][0]['data']) )
                print ("Found transaction data: " + str(transaction['input']) )
                
                # See: https://towardsdatascience.com/decoding-ethereum-smart-contract-data-eed513a65f76
                try:
                    func_obj, func_params = contractInstanceIn.decode_function_input(transaction['input'])
                    target_schema = [a['inputs'] for a in contractInstanceIn.abi if 'name' in a and a['name'] == func_obj.fn_name][0]
                    decoded_func_params = convert_to_hex(func_params, target_schema)
                    function_name = func_obj.fn_name
                    function_arguments = json.dumps(decoded_func_params)

                    print("            Function name is: " + function_name)
                    print("            Function arguments are: " + function_arguments)


                    # !!!NOT TESTED YET!!!
                    # holders = {}
                    # circulatingSupply = 0
                    # if function_name == 'mint':
                    #     mint_address = function_arguments['to']
                    #     mint_amount = function_arguments['amount']
                    #     holders.update({mint_address : mint_amount})
                    #     circulatingSupply = circulatingSupply + mint_amount
                    # elif function_name == 'burn':
                    #     burn_address = function_arguments['from']
                    #     burn_amount = function_arguments['amount']
                    #     circulatingSupply = circulatingSupply - burn_amount
                    #     holders[burn_address] = holders[burn_address] - burn_amount
                    # elif function_name == 'transfer':
                    #     So on.......

                    # Time to look at the contract argument and make the statistic
                    # Save Circulating supply Search all mint operation and add the values 
                    # Top holders  check mint burn and transfer 

                except:
                    e = sys.exc_info()[0]
                    print('ERROR_DECODE', repr(e), None)

        currentBlockNum = currentBlockNum - 1


###
### Print basic info about the contract
###
def printDetailsFromContract():
    
    #find owner is different than the creator
    ownerContract = contractInstance.functions.owner().call()

    #find name
    nameContract = contractInstance.functions.name().call()

    # This method is too slow
    # creatorContract = getContractCreatorAddress(my_contract_address)


    # an optimized version of finding the creator 
    creationBlockContract = getContractCreationBlock(my_contract_address)
    print("BLOCK creator: " + str(creationBlockContract))
    creatorContract = getContractCreatorAddress_v2(creationBlockContract, my_contract_address)


    #Get total supply
    totalSupply = contractInstance.functions.totalSupply().call()
    decimals = contractInstance.functions.decimals().call()

    totalSupplyWithoutDecimals = int(totalSupply/pow(10, decimals))


    print("Address of contract " + my_contract_address)
    print("Contract name: " + nameContract)
    print("Contract owner: " + ownerContract)
    print("Contract creator: " + str(creatorContract))
    print("Total Supply with decimal: " + str(totalSupply))
    print("Total Supply: " + str(totalSupplyWithoutDecimals))



printDetailsFromContract()
# fetchTransactionForHRC20(my_contract_address, creationBlockContract)
# 29612450
# fetchTransactionForHRC20BetweenBlocks(contractInstance, 29519838, 29519838)


###
### Details as token holders circulating supply and total token holders can be obtain only 
### interrogating the blockchain and creating a local database
###
### You could look from the block the contract was creating(getContractCreationBlock)
### up to the present block and interrogate all transaction all you could look at the events
### but this depends on the smart contract architecture



#for this we will use harmony explorer api