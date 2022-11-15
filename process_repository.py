import database_utils
import git
import os
import re

TOR_IPS_REPOSITORY = 'https://github.com/SecOps-Institute/Tor-IP-Addresses.git'
TOR_IPS_WORKDIR_PATH = '/tmp/tor-ip'
IPV6 = 6
IPV4 = 4

def process_patch_file_diff(filediff):
    diff = str(filediff).split("\n")
    added, deleted = get_diff_splited(diff)
    print(f"Add: {len(added)}, deleted: {len(deleted)}")
    return added, deleted

def get_diff_splited(data):
    deleted = []
    added = []
    line: str
    ip_regex = "((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$))"
    regex = re.compile(ip_regex)
    for line in data:
        ipfound = len(regex.findall(line[1:]))
        if line.startswith("+") and ipfound:
            added.append(line[1:])
        elif line.startswith('-') and ipfound:
            deleted.append(line[1:])
    return (added, deleted)

def build_exit_nodes_ip_changed(add, deleted, timestamp):
    return build_ip_changed(add, deleted, timestamp, True)

def build_ip_changed(add, deleted, timestamp, isExit=False):
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


def process_commit(commit: git.Commit):
    nodes,exitNodes = [],[]
    if commit.parents and len(commit.parents):
        for altered_file in commit.parents[0].diff(commit, create_patch=True):
            
            add, deleted = process_patch_file_diff(altered_file)
            changed_date = commit.committed_datetime
            if altered_file.b_path == 'tor-nodes.lst':
                nodes = build_ip_changed(add, deleted, changed_date)
            elif altered_file.b_path == 'tor-exit-nodes.lst':
                exitNodes = build_exit_nodes_ip_changed(add, deleted, changed_date)
    else:
        print(commit)
        raise f'The commit {commit.hexsha} has no Parent'
    
    nodes.extend(exitNodes)
    return nodes

def build_git_repo():
    try:
        if os.path.exists(TOR_IPS_WORKDIR_PATH) and os.path.exists(TOR_IPS_WORKDIR_PATH + '/.git'):
            print('Repo already exists')
            repo = git.Repo(TOR_IPS_WORKDIR_PATH)
            repo.remotes.origin.pull()
        else:
            repo = git.Repo.clone_from(TOR_IPS_REPOSITORY, TOR_IPS_WORKDIR_PATH, branch="master")
        return repo
    except Exception as e:
        print(e)
        raise e


if __name__ == '__main__':
    db = database_utils.connectToDatabase()
    repo, last_commit = build_git_repo(), database_utils.getLastCommitProcessed(db)

    commits = list(repo.iter_commits(rev=f'{last_commit}..{repo.head.commit.hexsha}'))
    commits.reverse()

    for commit in commits:
        ips = process_commit(commit)
        print(commit.hexsha)

        database_utils.executeInsert(ips, "IP", db)
    database_utils.saveLastCommit(commits[-1].hexsha, db)



