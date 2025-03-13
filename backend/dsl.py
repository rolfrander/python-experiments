
import os
import stat

nodir = None

def is_hidden(f):
    return stat.FILE_ATTRIBUTE_HIDDEN & f.stat().st_file_attributes

class Filenav:
    def __init__(self, directory, parent=None):
        self.cur = os.path.abspath(directory)
        self._files = []
        self._dirnames = []
        self.subdirs = {}
        self.parent = parent
        for f in os.scandir(self.cur):
            if os.access(f.path, os.R_OK):
                if f.is_dir() and os.access(f.path, os.X_OK) and not is_hidden(f):
                    self._dirnames.append(f.name)
                elif f.is_file():
                    self._files.append(f.name)
                else:
                    pass

    def cur(self):
        return self.cur
    
    def dirs(self):
        return self._dirnames
    
    def files(self):
        return self._files
    
    def __getitem__(self, dir):
        if dir == "*" or dir == "ANY":
            for d in self._dirnames:
                if not d in self.subdirs:
                    self.subdirs[d] = Filenav("{}{}{}".format(self.cur, os.sep, d), self)
            return Manydirs([s for s in self.subdirs.values()], self)
        elif dir in self.subdirs:
            return self.subdirs[dir]
        else:
            for d in self._dirnames:
                if d==dir:
                    self.subdirs[d] = Filenav("{}{}{}".format(self.cur, os.sep, d), self)
                    return self.subdirs[d]
            return nodir

    def __repr__(self):
        return "<Filenav {}>".format(self.cur)

    def __getattr__(self, name):
        return self.__getitem__(name)
    
    def __iter__(self):
        return iter([self])
    
    def _addselftolist(self, l):
        l.append(self)

class Manydirs(Filenav):
    def __init__(self, filenavs, parent=None):
        if parent == None:
            self.cur="*"
        else:
            self.cur = "{}{}{}".format(parent.cur, os.sep, "*")
        self.filenavs = filenavs
        self.parent = parent

    def __getitem__(self, dir):
        ret = []
        for f in self.filenavs:
            f[dir]._addselftolist(ret)
        if len(ret) == 0:
            return nodir
        if len(ret) == 1:
            return ret[0]
        else:
            return Manydirs(ret, self)

    def _addselftolist(self, l):
        l.extend(self.filenavs)

    def __iter__(self):
        return iter(self.filenavs)

    def __repr__(self):
        return repr(self.filenavs)


class Nodir(Filenav):
    def __init__(self):
        self.cur = "nodir"
        self._files = []
        self._dirnames = []
    
    def __getitem__(self, dir):
        return self

    def __repr__(self):
        return "<Nodir>"

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration
    
    def _addselftolist(self, l):
        pass

nodir = Nodir()

stats = {
        stat.FILE_ATTRIBUTE_ARCHIVE: "ARCHIVE",
        stat.FILE_ATTRIBUTE_COMPRESSED: "COMPRESSED",
        stat.FILE_ATTRIBUTE_DEVICE: "DEVICE",
        stat.FILE_ATTRIBUTE_DIRECTORY: "DIRECTORY",
        stat.FILE_ATTRIBUTE_ENCRYPTED: "ENCRYPTED",
        stat.FILE_ATTRIBUTE_HIDDEN: "HIDDEN",
        stat.FILE_ATTRIBUTE_INTEGRITY_STREAM: "INTEGRITY_STREAM",
        stat.FILE_ATTRIBUTE_NORMAL: "NORMAL",
        stat.FILE_ATTRIBUTE_NOT_CONTENT_INDEXED: "NOT_CONTENT_INDEXED",
        stat.FILE_ATTRIBUTE_NO_SCRUB_DATA: "NO_SCRUB_DATA",
        stat.FILE_ATTRIBUTE_OFFLINE: "OFFLINE",
        stat.FILE_ATTRIBUTE_READONLY: "READONLY",
        stat.FILE_ATTRIBUTE_REPARSE_POINT: "REPARSE_POINT",
        stat.FILE_ATTRIBUTE_SPARSE_FILE: "SPARSE_FILE",
        stat.FILE_ATTRIBUTE_SYSTEM: "SYSTEM",
        stat.FILE_ATTRIBUTE_TEMPORARY: "TEMPORARY",
        stat.FILE_ATTRIBUTE_VIRTUAL: "VIRTUAL"
}

def checkstats(f):
    flags = f.stat().st_file_attributes
    return [stats[s] for s in stats.keys() if s&flags]


if 1==2:
    exec(open("dsl.py").read())
    f=Filenav("/")
    #f["Users"]["rolfn"]["*"]["shelly"]
    for ch in f.Users.rolfn.src:
        print(ch)

