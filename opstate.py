from update import run, get_commit, get_branch
from pathlib import Path
import time
import os
import subprocess
import re
from typing import List, Tuple
import sys
import salt.client


# name of git remote
REMOTE = "origin"


def run(command: List[str]) -> str:
    # run subprocess returning stdout and stderr
    stdout = subprocess.check_output(
        command, stderr=subprocess.STDOUT).decode("utf-8")
    return stdout.strip()


def get_branch() -> str:
    # return the current branch
    return run(["git", "rev-parse", "--abbrev-ref", "HEAD"])


def get_commit(branch: str) -> Tuple[str, str]:
    # return latest repository commit (remote) and latest applied commit (local)
    remote = run(["git", "rev-parse", branch])
    if os.path.exists(".latest-commit"):
        local = open(".latest-commit", "r").read().strip()
    else:
        local = None
    return local, remote


def pull():
    print(f"\ncheck updates for opstate with remote {REMOTE}")
    branch = get_branch()
    print(f"  * local branch: {branch}")
    print(f"  * fetch: {'done' if run(['git', 'fetch', REMOTE]) else 'none'}")

    diff = run(["git", "rev-list", "--left-right", "--count",
                f"origin/{branch}...{branch}"])
    (behind, ahead) = [int(i) for i in re.split(r"\s+", diff, maxsplit=3)][:2]
    if behind:
        print(f"  * behind: {behind} commit{'s' if behind > 1 else ''}")
    if ahead:
        print(f"  * ahead: {ahead} commit{'s' if ahead > 1 else ''}")
    dirty = run(["git", "status", "--porcelain"])
    print(f"  * local worktree: {'clean' if dirty == '' else 'dirty'}")
    print(f"\nidentify changes of {REMOTE}/{branch}")
    if behind:
        if not dirty:
            if not ahead:
                print("  * identify changes")
                log = run(["git", "log", "--oneline", "HEAD..origin"])
                print("\n".join([f"  {line}" for line in log.split("\n")]))
                print(f"  * pull changes from branch {REMOTE}/{branch}")
                run(["git", "pull", "origin"])
            else:
                print("  * local changes ahead, skip pulling!")
        else:
            print("  * worktree not clean, skip pulling!")
    else:
        print("  * no changes found, skip pulling!")

    print(f"\nverify local vs. remote commit of {REMOTE}/{branch}")
    local, remote = get_commit(branch)
    if local != remote:
        print("  * commits differ, update required!")
        sys.exit(1)
    else:
        print("  * commits are identical, skip update!")
        sys.exit(0)


def apply():
    os.environ['SALT_FILE_ROOT'] = './'
    caller = salt.client.Caller(mopts={'file_client': 'local'})
    ret = caller.cmd('state.apply', 'default', test=True)
    print(ret)
    branch = get_branch()
    local, remote = get_commit(branch)
    open(".latest-commit", "w").write(remote)


def main():
    retcode = subprocess.Popen([sys.executable, 'opstate.py', 'pull']).wait()
    print()
    if retcode == 1:
        seconds = 5
        try:
            while seconds > 0:
                print("\r", end="")
                print(f"apply changes ... continue in {seconds}s",
                      flush=True, end="")
                time.sleep(1)
                seconds -= 1
        except KeyboardInterrupt:
            print("\nAborting.")
            sys.exit(2)
        print(f"\rapply changes ... continue now   ")
        run(["git", "pull", "--rebase=true"])
        print("restarting")
        os.execl('/usr/bin/sudo', sys.executable, sys.executable, __file__,
                 'apply')
    elif retcode == 0:
        print("Nothing to do!")
    print("Exiting.\n")


if __name__ == "__main__":
    root = Path(__file__).parent.absolute()
    os.chdir(root)
    if len(sys.argv) == 1:
        main()
    elif sys.argv[1].lower().strip() == "pull":
        pull()
    elif sys.argv[1].lower().strip() == "apply":
        apply()
    else:
        print("help")
