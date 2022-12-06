import database_utils
import subprocess
import ip_utils
from multiprocess import Pool


IPsRange = []
inputs = []

def process_line(line):

    line = line.strip()
    line = line.split('\t')
    
    rangesList = subprocess.getoutput(f'ipcalc --no-decorate -d {line[0]}-{line[1]}').split('\n')
    output = []
    for range in rangesList:
        try:
            subnet,netmask,network = ip_utils.convertNetmask(range)
        except Exception as e:
            print(line)
            raise e
        item = {
            'SUBNET': subnet,
            'NETMASK': netmask,
            'ASN': line[2],
            'PROVIDER': line[4]
        }
        if network.version() == 4:
            item['SUBNET_NUM']  = network.network_long()
            item['NETMASK_NUM'] = network.netmask_long()

        if line[3] not in ('Unknown', 'None'):
            item['COUNTRY'] = line[3]
        output.append(item)
    return output

while True:
    try:
        line  = input()
        inputs.append(line)
        
    except Exception as e:
        print(e)
        break

print("Finish read!")
with Pool(32) as pool:
    for subList in pool.map(process_line, inputs):
        for item in subList:
            IPsRange.append(item)

# print(IPsRange)
if __name__ == "__main__":
    print("tamanho:  ", len(IPsRange))
    db = database_utils.connectToDatabase()
    database_utils.executeInsert(IPsRange, 'PROVIDERS', db)