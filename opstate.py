import sys
import subprocess
import os
from pathlib import Path
from update import run, get_commit, get_branch
import time



root = Path(__file__).parent.absolute()
os.chdir(root)

retcode = subprocess.Popen([
    sys.executable,
    'update.py'
]).wait()

print()
if retcode == 1:
    seconds = 5
    while seconds > 0:
        print("\r", end="")
        print(f"pull changes and refresh ... continue in {seconds}s",
              flush=True, end="")
        time.sleep(1)
        seconds -= 1
    print(f"\rpull changes and refresh ... continue now   ")
    run(["git", "pull"])
    print("restarting\n")
    branch = get_branch()
    local, remote = get_commit(branch)
    open(".latest-commit", "w").write(remote)
    os.execl(sys.executable, sys.executable, *sys.argv)
elif retcode == 0:
    print("Nothing to do!")
print("exit.")
