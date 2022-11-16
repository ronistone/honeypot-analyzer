import os
import git
import ipcalc

TOR_IPS_REPOSITORY = 'https://github.com/SecOps-Institute/Tor-IP-Addresses.git'
TOR_IPS_WORKDIR_PATH = '/tmp/tor-ip'
VPN_LIST_URL = 'https://github.com/X4BNet/lists_vpn.git'
VPN_LIST_WORKDIR_PATH = '/tmp/vpn-list'
IPV6 = 6
IPV4 = 4

class RepositoryProcess:

    def __init__(self, workdirPath, repositoryUrl, branch, table, skipCommitsNum, filesFunctions={}):
        self.filesFunctions = filesFunctions
        self.workdirPath = workdirPath
        self.repositoryUrl = repositoryUrl
        self.branch = branch
        self.table = table
        self.skipCommitsNum = skipCommitsNum
    
    def process_file(self, filename, add, deleted, timestamp):
        if filename in self.filesFunctions:
            return getattr(self, self.filesFunctions[filename])(add, deleted, timestamp)
        else:
            return None


class TorRepositoryProcess(RepositoryProcess):
    def __init__(self):
        super().__init__(
            TOR_IPS_WORKDIR_PATH, 
            TOR_IPS_REPOSITORY, 
            "master",
            "IP",
            10,
            {
                'tor-nodes.lst': 'build_ip_changed',
                'tor-exit-nodes.lst': 'build_exit_nodes_ip_changed'
            }
        )

    def build_exit_nodes_ip_changed(self, add, deleted, timestamp):
        return self.build_ip_changed(add, deleted, timestamp, True)

    def build_ip_changed(self, add, deleted, timestamp, isExit=False):
        ips = []

        ip: str
        for ip in add:
            ips.append({
                'IP': ip,
                'IP_TYPE': 'TOR',
                'IS_EXIT_NODE': isExit,
                'ENTRY_TIME': timestamp,
                'IP_VERSION': IPV6 if ':' in ip else IPV4
            })
        for ip in deleted:
            ips.append({
                'IP': ip,
                'IP_TYPE': 'TOR',
                'IS_EXIT_NODE': isExit,
                'EXIT_TIME': timestamp,
                'IP_VERSION': IPV6 if ':' in ip else IPV4
            })
        return ips

class VpnRepositoryProcess(RepositoryProcess):
        def __init__(self):
            super().__init__(
                VPN_LIST_WORKDIR_PATH, 
                VPN_LIST_URL, 
                "main",
                "SUBNET",
                18,
                {
                    'ipv4.txt': 'build_ip_changed'
                }
            )

        def build_ip_changed(self, add, deleted, timestamp, isExit=False):
            ips = []

            ip: str
            for ip in add:
                subnet = ipcalc.Network(ip)
                netmask = str(subnet.netmask())
                subnet = ip.split('/')[0]
                ips.append({
                    'SUBNET': subnet,
                    'NETMASK': netmask,
                    'IP_TYPE': 'VPN',
                    'ENTRY_TIME': timestamp,
                    'IP_VERSION': IPV4
                })
            for ip in deleted:
                subnet, netmask = ip.split('/')
                ips.append({
                    'SUBNET': subnet,
                    'NETMASK': netmask,
                    'IP_TYPE': 'VPN',
                    'EXIT_TIME': timestamp,
                    'IP_VERSION': IPV4
                })
            return ips

def build_git_repo_and_get_commits(repositoryInfo: RepositoryProcess, last_commit: str):
    try:
        if os.path.exists(repositoryInfo.workdirPath) and os.path.exists(repositoryInfo.workdirPath + '/.git'):
            print('Repo already exists')
            repo = git.Repo(repositoryInfo.workdirPath)
            repo.remotes.origin.pull()
        else:
            repo = git.Repo.clone_from(repositoryInfo.repositoryUrl, repositoryInfo.workdirPath, branch=repositoryInfo.branch)

        if last_commit:
            commits = list(repo.iter_commits(rev=f'{last_commit}..{repo.head.commit.hexsha}'))
        else:
            commits = list(repo.iter_commits())
            commits = commits[:-repositoryInfo.skipCommitsNum]

        if commits and len(commits):
            commits.reverse()
        
        return repo, commits
    except Exception as e:
        print(e)
        raise e

