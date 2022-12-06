import database_utils
import subprocess
import ipcalc
from multiprocess import Pool


IPsRange = []
inputs = []

# item = {
#     'SUBNET': subnet,
#     'NETMASK': netmask,
#     'ASN': line[2],
#     'PROVIDER': line[4],
#     'SUBNET_NUM': network.network_long(),
#     'NETMASK_NUM': network.netmask_long(),
#     'COUNTRY' = line[3]
# }
# print(IPsRange)
def createNetworkObject(provider):
    provider['NETWORK_IP_CALC'] = ipcalc.Network(provider['SUBNET'], provider['NETMASK'])
    return provider

if __name__ == "__main__":
    print("tamanho:  ", len(IPsRange))
    db = database_utils.connectToDatabase()
    providersIps = database_utils.executeQueryMany("""
        SELECT * FROM PROVIDERS WHERE PROVIDERS.SUBNET like '%:%';
    """, db)

    print('Providers query Done!')

    with Pool(64) as pool:
        providersIps = pool.map(createNetworkObject, providersIps)

    print('Providers Processing Done!')
    processedIps = database_utils.executeQueryMany("""
        SELECT * FROM PROCESSED_IPS WHERE PROCESSED_IPS.src_ip like '%:%';
    """, db)
    print('ProcessedIps query done!')
    print('All queries done!')
    i = 0
    for ip in processedIps:

        for provider in providersIps:
            if provider['NETWORK_IP_CALC'].check_collision(ip['src_ip']+'/128'):
                print(f"Colision {provider} -> {ip}")
                raise 'stop'

        i += 1

        if i % 10 == 0:
            print(f'{(i/len(processedIps))*100} IPs processed')
    print(providersIps)
    # database_utils.executeInsert(IPsRange, 'PROVIDERS', db)