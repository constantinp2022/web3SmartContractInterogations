import requests
from selenium import webdriver

myContractAddress = '0x85fd5f8dbd0c9ef1806e6c7d4b787d438621c1dc'



def getContractName(contractAddress):
    url = 'https://ctrver.t.hmny.io/fetchContractCode?contractAddress=' + contractAddress
    my_headers = {'Content-Type': 'application/json'}
    r = requests.get(url, headers=my_headers)
    json_response = r.json()

    return json_response['contractName']


def getTokenHolders(contractAddress):
    url = 'https://explorer-v2-api.hmny.io/v0/erc20/token/' + contractAddress + '/holders?limit=100&offset=0'
    # payload = open("requests.json")
    my_headers = {'Content-Type': 'application/json'}
    r = requests.get(url, headers=my_headers)
    json_response = r.json()

    # read json for data 
    # This API Seeems not to work anymore 429 Error


def getTokenHoldersCrawler(contractAddress):

    my_url = 'https://explorer.harmony.one/address/' + contractAddress + '?activeTab=5'
    # resp = requests.get(my_url)
    # print(resp.status_code)
    # print(resp.text)

    driver = webdriver.PhantomJS()
    driver.get(my_url)
    p_element = driver.find_element_by_id(id='StyledTable__StyledTableBody-sc-1m3u5g-3 fqnCHS StyledDataTable__StyledDataTableBody-xrlyjm-3 dbXpni')
    print(p_element)



contractName = getContractName(myContractAddress)
# tokneHolders = getTokenHolders(myContractAddress)
# getTokenHolders(myContractAddress)
getTokenHoldersCrawler(myContractAddress)

print('Contract name: ' + contractName)
# print('Contract holders: ' + tokneHolders)