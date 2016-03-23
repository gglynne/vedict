import os, re, codecs, urllib, gzip
import config

def wget(url, enc_in, path_out, enc_out):
    """ fetch a gz file, unpack it,  re-encode to disk"""
    filename, headers = urllib.urlretrieve(url)
    with gzip.open(filename) as fp_in, codecs.open(path_out,'w',enc_out) as fp_out:
        line = fp_in.readline()
        while line:
            fp_out.write(line.decode(enc_in))	
            line = fp_in.readline()


class ManagerBackend(dict):
    """ Encapsulates a collection of dictionaries on disk. """

    def __init__(self):
        super(ManagerBackend,self).__init__()
        self.batches=None
        self._iterators=None

    def wget(self, url,name):
        """ Download a dictionary file if not present,"""
        path = os.path.join(config.default_dic_path,name)
        if not os.path.exists(path):
            print("Downloading %s..." % url)
            import vim
            vim.command("redraw")
            wget(url,'euc-jp', path, 'euc-jp')

    def getdics(self):
        """Check for config dir, create it and grab default dictionaries if required"""
        if not os.path.exists(config.default_dic_path):
            os.mkdir(config.default_dic_path)
        self.wget('http://ftp.monash.edu.au/pub/nihongo/edict.gz','edict')
        self.wget('http://ftp.monash.edu.au/pub/nihongo/enamdict.gz','enamdict')




    def load(self, path, variety):
        """ Register a dictionary, loading index if present. 
            path: dictionary filename
        """
        name=path
        path=os.path.join(config.default_dic_path,path)
        if not os.path.exists(path):
            raise Exception("Path %s does not exist." % path)
        if name==None:
            name=os.path.split(path)[1]
        from config import _types
        dic=_types[variety](path,name)
        self[name]=dic
        dic.load_index()
        return dic


    def grep(self, pattern, dicpattern=".*", flags=re.IGNORECASE, batch=None):
        self._iterators=[]
        for name in self.keys():
            if re.match(dicpattern,name):
                self._iterators.append(self[name].grep(pattern,flags))
        if batch!=None:
            self.batches=batch
        else:
            self.batches=config.batches
        pass

    def fetch(self):
        yielded=0
        yielded=self.batches
        while self._iterators and yielded>0:
            for i in self._iterators:
                try:
                    yield i.next()
                    yielded=yielded-1
                except StopIteration:
                    self._iterators.remove(i)
        pass

    def unload(self, name):
        """ Unregister a dictionary """
        if not self.has_key(name):
            print "Dictionary not found."
        else:
            self.pop(name)
        pass

