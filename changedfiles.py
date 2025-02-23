import os
import os.path
import tempfile
import subprocess
from lxml import etree
from datetime import datetime

def run_git(git_cmd):
    ret = None
    try:
        cmd = ["git"] + git_cmd
        # print(f"running: {cmd}")
        ret = subprocess.run(cmd,
                             capture_output=True,
                             text=True,
                             check=True)
        return ret.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}")
        if ret is not None:
            print(ret.stderr)
        return ""
    
def git_clone(repo):
    "Clones a repo into the current directory and changes to this directory"
    run_git(["clone", "-q", repo])

def get_changed_files(since_commit = None):
    "Returns a list of changed files since the given commit. If since_commit is None, returns a list of files with uncommitted changes."
    cmd = ["diff", "--name-only", since_commit]
    if since_commit is None:
        cmd = cmd[:-1]
    result = run_git(cmd)
    # Split the output into a list of filenames
    changed_files = result.split("\n")
    return [file for file in changed_files if file]  # Remove empty entries

def has_uncommitted_changes():
    "Returns truw if the current working directory has uncommitted changes"
    result = run_git(["status", "--porcelain"])
    return bool(result)  # If output is empty, there are no changes

def current_commit_hash():
    "Returns the commit-hash for HEAD"
    return run_git(["rev-parse", "HEAD"])

def is_valid_commit_hash(commit):
    return run_git(["cat-file", "-t", commit]) == "commit"

def git_toplevel():
    return run_git(["rev-parse", "--show-toplevel"])

def git_remote_origin():
    return run_git(["config", "--get", "remote.origin.url"])

def get_status_string():
    "Returns an xml-formatted string containing the current commit, current user and timestamp"
    xml = etree.Element("status")
    etree.SubElement(xml, "commit"   ).text = current_commit_hash()
    etree.SubElement(xml, "user"     ).text = os.environ.get("USER") or os.environ.get("USERNAME")
    etree.SubElement(xml, "origin"   ).text = git_remote_origin()
    etree.SubElement(xml, "timestamp").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    return etree.tostring(xml, pretty_print=True, encoding="UTF-8").decode("UTF-8")


def read_status_string(status):
    "Parses the xml-string returned from get_status_string and returns as a dict"
    xml = etree.fromstring(status)
    return {"commit":    xml.find("commit").text,
            "user":      xml.find("user").text,
            "origin":    xml.find("origin").text,
            "timestamp": datetime.strptime(xml.find("timestamp").text, "%Y-%m-%d %H:%M:%S.%f")}

dirstack = []
def pushdir(dir):
    dirstack.append(os.path.abspath("."))
    os.chdir(dir)

def popdir():
    if len(dirstack) > 0:
        os.chdir(dirstack.pop())

def clone_and_sync_current_dir(status):
    if has_uncommitted_changes():
        raise Exception("uncommitted changes in {}, aborting".format(os.path.abspath(".")))
    commit = status["commit"]
    if not is_valid_commit_hash(commit):
        raise Exception("unknown commit-hash {}, aborting".format(commit))
    files = [f for f in get_changed_files(commit) if (f != ".gitignore" and f != "README.md")]
    print(files)
    return get_status_string()


def clone_and_sync(status):
    with tempfile.TemporaryDirectory() as temp_dir:
        #print("Temporary directory:", temp_dir)
        pushdir(temp_dir)
        try:
            git_clone(status["origin"])
            ls = os.listdir(".")
            if len(ls) != 1:
                raise Exception(f"unexpected contents of temporary directory {ls}")
            os.chdir(ls[0])
            #print("current directory:", os.path.abspath("."))
            #print("upload these files:")
            clone_and_sync_current_dir(status)
        finally:
            popdir()

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

    status = {"commit": "28e96518240e9ba25b7f6209aa1199388a352d53",
              "origin": "https://github.com/rolfrander/geo.git"}
    clone_and_sync(status)
    clone_and_sync_current_dir(status)