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
if run(["git", "fetch"]):
    print("fetch: yes")
else:
    print("fetch: no")

diff = run(["git", "rev-list", "--left-right", "--count",
            f"origin/{branch}...{branch}"])
(behind, ahead) = [int(i) for i in re.split("\s+", diff, maxsplit=3)][:2]
print("behind:", behind)
print("ahead:", ahead)

clean = run(["git", "status", "--porcelain"])
if not clean:
    print("worktree:", "clean")
else:
    print("worktree:", "not clean")

if (behind and not ahead and clean):
    print("pull changes")