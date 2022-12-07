import database_utils
from pprint import pprint
import math


def binarySearch(dataToSearch: list, value: int):
    init, end = 0, len(dataToSearch) - 1
    mid = math.floor(end/2)

    while init <= end:
        mid = init + ((end-init)//2)
        elem = dataToSearch[mid]
        subnet, netmask = elem['SUBNET_NUM'], elem['NETMASK_NUM']
        matchValue = value & netmask
        if matchValue == subnet:
            return elem
        elif matchValue > subnet:
            init = mid + 1
        else:
            end = mid - 1
    raise 'NOT FOUND'

def buildUpdateStatement(subnetFound, ip):
    return f"UPDATE PROCESSED_IPS set COUNTRY='{subnetFound['COUNTRY']}', PROVIDER='{subnetFound['PROVIDER']}' WHERE ID ={ip['id']}"


if __name__ == "__main__":
    db = database_utils.connectToDatabase()
    providersIps = database_utils.executeQueryMany("""
        SELECT * FROM PROVIDERS WHERE PROVIDERS.SUBNET;
    """, db)

    print('Providers query Done!')

    providersIps = sorted(providersIps, key=lambda k: (k['SUBNET_NUM'], k['NETMASK_NUM']))
    print('Providers ordered')

    print('Providers Processing Done!')
    processedIps = database_utils.executeQueryMany("""
        SELECT * FROM PROCESSED_IPS WHERE PROCESSED_IPS.src_ip;
    """, db)
    print('ProcessedIps query done!')
    print('All queries done!')

    matchIps = []
    notFoundIps = []

    for ip in processedIps:
        try:
            ipFound = binarySearch(providersIps, ip['SRC_IP_NUM'])
            matchIps.append(buildUpdateStatement(ipFound, ip))
        except Exception as e:
            print(e)
            notFoundIps.append(ip['src_ip'])
    if len(notFoundIps):
        print("IPs Not Found:")
        pprint(notFoundIps)

    # print(matchIps)
    print('Finish process IPs')
    print('Initing update database...')
    database_utils.executeUpdateMany(matchIps, db)
