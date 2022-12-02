import re

import MySQLdb
import database_utils
import git
import repository_utils


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
        lineSplited = line.split('/')[0]
        ipfound = len(regex.findall(lineSplited[1:]))

        if lineSplited.startswith("+") and ipfound:
            added.append(line[1:])
        elif lineSplited.startswith('-') and ipfound:
            deleted.append(line[1:])

    return (added, deleted)


def process_commit(commit: git.Commit, repositoryProcess: repository_utils.RepositoryProcess):
    ips = []

    if commit.parents and len(commit.parents):
        for altered_file in commit.parents[0].diff(commit, create_patch=True):
            
            add, deleted = process_patch_file_diff(altered_file)
            ipsFound = repositoryProcess.process_file(altered_file.b_path, add, deleted, commit.committed_datetime)

            if ipsFound:
                ips.extend(ipsFound)
    else:
        print(commit)
        raise f'The commit {commit.hexsha} has no Parent'
    
    return ips

def process_repo(repositoryProcess: repository_utils.RepositoryProcess, db: MySQLdb.Connection):
    last_commit = database_utils.getLastCommitProcessed(repositoryProcess.repositoryUrl, db)
    _,commits = repository_utils.build_git_repo_and_get_commits(repositoryProcess, last_commit)
    
    if commits and len(commits):
        for commit in commits:
            ips = process_commit(commit, repositoryProcess)
            print(commit.hexsha)
            # print(ips)
            # break
            database_utils.executeInsert(ips, repositoryProcess.table, db)
        database_utils.saveLastCommit(commits[-1].hexsha, repositoryProcess.repositoryUrl, db)
    else:
        print(f" Repo {repositoryProcess.repositoryUrl} There are no commits to process")

if __name__ == '__main__':
    db = database_utils.connectToDatabase()

    # torRepositoryProcess = repository_utils.TorRepositoryProcess()
    # process_repo(torRepositoryProcess, db)

    # vpnRepositoryProcess = repository_utils.VpnRepositoryProcess()
    # process_repo(vpnRepositoryProcess, db)

    cloudRepositoryProcess = repository_utils.CloudRepositoryProcess()
    process_repo(cloudRepositoryProcess, db)


    



