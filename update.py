import os
from pathlib import Path
import subprocess
import re
from typing import List

root = Path(__file__).parent.absolute()
os.chdir(root)


def run(command: List[str]) -> str:
    stdout = subprocess.check_output(
        command, stderr=subprocess.STDOUT).decode("utf-8")
    return stdout.strip()


branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
print("branch:", branch)
if run(["git", "fetch", "origin"]):
    print("fetch: yes")
else:
    print("fetch: no")

diff = run(["git", "rev-list", "--left-right", "--count",
            f"origin/{branch}...{branch}"])
(behind, ahead) = [int(i) for i in re.split("\s+", diff, maxsplit=3)][:2]
print("behind:", behind)
print("ahead:", ahead)

dirty = run(["git", "status", "--porcelain"])
if not dirty:
    print("worktree:", "clean")
else:
    print("worktree:", "dirty")

remote = run(["git", "rev-parse", branch])
if os.path.exists(".latest-commit"):
    local = open(".latest-commit", "r").read().strip()
else:
    local = None

print("local:", local)
print("remote:", remote)

if (behind and (not ahead) and (not dirty)):
    log = run(["git", "log", "--oneline", "HEAD..origin"])
    print(f"log:\n{log}")
    print("pull changes")
    input("continue?")
    log = run(["git", "pull", "origin"])
    print("pull result:", log)

if local != remote:
    print("deploy!!!")
    #open(".latest-commit", "w").write(remote)
