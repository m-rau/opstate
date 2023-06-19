import os
import subprocess
import re
from typing import List
import sys

REMOTE = "origin"


def run(command: List[str]) -> str:
    stdout = subprocess.check_output(
        command, stderr=subprocess.STDOUT).decode("utf-8")
    return stdout.strip()


def main():
    print(f"check updates for opstate with remote \"{REMOTE}\"")
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    print("  * local branch:", branch)
    print("  * fetch update: ", end="")
    if run(["git", "fetch", REMOTE]):
        print("OK")
    else:
        print("none")

    diff = run(["git", "rev-list", "--left-right", "--count",
                f"origin/{branch}...{branch}"])
    (behind, ahead) = [int(i) for i in re.split("\s+", diff, maxsplit=3)][:2]

    if behind:
        print("  * behind:", behind)
    if ahead:
        print("  * ahead:", ahead)

    dirty = run(["git", "status", "--porcelain"])
    print("  * local worktree: ", end="")
    if not dirty:
        print("clean")
    else:
        print("dirty")

    print(f"verify pull of changes in \"{REMOTE}/{branch}\"")
    if behind:
        if not dirty:
            if not ahead:
                print(f"  * identify changes ")
                log = run(["git", "log", "--oneline", "HEAD..origin"])
                print("\n".join([f"  {line}" for line in log.split("\n")]))
                print(f"  * pull changes from branch \"{REMOTE}/{branch}\"")
                run(["git", "pull", "origin"])
            else:
                print("  * local changes ahead, skip pulling!")
        else:
            print("  * worktree not clean, skip pulling!")
    else:
        print("  * no changes found, skip pulling!")

    print(f"verify local vs. remote commit in {REMOTE}/{branch}")
    remote = run(["git", "rev-parse", branch])
    if os.path.exists(".latest-commit"):
        local = open(".latest-commit", "r").read().strip()
    else:
        local = None
    print("  * local commit hash:", local)
    print("  * remote commit hash:", remote)

    if local != remote:
        print("  * commits differs, update required!")
        sys.exit(1)
    else:
        print("  * commits are identical, skip update!")
        sys.exit(0)


if __name__ == "__main__":
    main()
