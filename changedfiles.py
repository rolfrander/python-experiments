import os
import os.path
import subprocess
from lxml import etree
from datetime import datetime

def run_git(git_cmd):
    return subprocess.run(["git"] + git_cmd,
                            capture_output=True,
                            text=True,
                            check=True)

def get_changed_files(since_commit = None):
    "Returns a list of changed files since the given commit. If since_commit is None, returns a list of files with uncommitted changes."
    cmd = ["diff", "--name-only", since_commit]
    if since_commit is None:
        cmd = cmd[:-1]
    result = run_git(cmd)
    # Split the output into a list of filenames
    changed_files = result.stdout.strip().split("\n")
    return [file for file in changed_files if file]  # Remove empty entries

def has_uncommitted_changes():
    "Returns truw if the current working directory has uncommitted changes"
    result = run_git(["status", "--porcelain"])
    return bool(result.stdout.strip())  # If output is empty, there are no changes

def current_commit_hash():
    "Returns the commit-hash for HEAD"
    return run_git(["rev-parse", "HEAD"]).stdout.strip()

def get_status_string():
    "Returns an xml-formatted string containing the current commit, current user and timestamp"
    hash = current_commit_hash()
    username = os.environ.get("USER") or os.environ.get("USERNAME")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    xml = etree.Element("status")
    etree.SubElement(xml, "commit").text=hash
    etree.SubElement(xml, "user").text=username
    etree.SubElement(xml, "timestamp").text=current_time
    return etree.tostring(xml, pretty_print=True, encoding="UTF-8").decode("UTF-8")

def git_toplevel():
    return run_git(["rev-parse", "--show-toplevel"]).stdout.strip()

def read_status_string(status):
    "Parses the xml-string returned from get_status_string and returns as a dict"
    xml = etree.fromstring(status)
    return {"commit": xml.find("commit").text,
            "user": xml.find("user").text,
            "timestamp": datetime.strptime(xml.find("timestamp").text, "%Y-%m-%d %H:%M:%S.%f")}

dirstack = []
def pushdir(dir):
    dirstack.append(os.path.abspath("."))
    os.chdir(dir)

def popdir():
    if len(dirstack) > 0:
        os.chdir(dirstack.pop())


if 1==2:
    exec(open("changedfiles.py").read())
    pushdir("C:\\Users\\rolfn\\src\\adventofcode\\2023")
    os.chdir(git_toplevel())
    has_uncommitted_changes()
    get_changed_files("f0c888159")
    get_changed_files()
    current_commit_hash()
    print(read_status_string(get_status_string()))
    popdir()
