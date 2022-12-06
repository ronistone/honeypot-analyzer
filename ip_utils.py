import ipcalc

def convertNetmask(ip):
    try:
        network = ipcalc.Network(ip)
    except Exception as e:
        print("\n\n\n\n\n break -> ", ip ,":\n", e, "\n\n\n")
        raise e
    netmask = str(network.netmask())
    subnet = ip.split('/')[0]
    return subnet,netmask,network