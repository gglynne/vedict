# vim: set fileencoding=utf-8 :
#nmap g<space> :SingleCompileRun<cr>

import unittest

from vedict import config
from vedict.backend import ManagerBackend

class TestVedict(unittest.TestCase):

    def test(self):
        self.assertEqual( config.batches,5,"Failed to fetch config variable" )

        m=ManagerBackend()
        m.checkdics()
        path=name=variety='edict'
        m.load(path=path,variety=variety)
        self.assertEqual( len(m),1,"Failed to load dictionary at %s" % path )

        m.unload(name)
        self.assertEqual( len(m),0,"Failed to unload dictionary at %s" % path )

        m.load(path=path,variety=variety)
        hits= [ h for h in m[name].grep('.*漢字'.decode('utf8'))]
        self.assertTrue(len(hits)>0, "Failed to grep dictionary")


if __name__ == '__main__':
    unittest.main()


