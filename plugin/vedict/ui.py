#!/usr/bin/python
# vim: set fileencoding=utf-8 :
#highlight Folded guibg=darkgrey guifg=blue

import os,re, vim
from config import default_dic_path, batches, _types
from window import ResultsWindow, Window
from backend import ManagerBackend

class Manager(ManagerBackend):
    """ vim interface to ManagerBackend """

    usage="""usage: %s <command>"""

    def __init__(self,root_object):
        super(ManagerBackend,self).__init__()
        self.root_object=root_object
        self.window=ResultsWindow(root_object,maps={
            'close()':( ['q',], False ),
            'fetch()':( ['<space>','n'], False ),
            'fetch_all()':( ['a'], False ),
            'select()' : ( ['<cr>'], False ),
            'preview()' : ( ['p'], False ),
            #'update_preview()':( ['j','k'], True ),
                })
        self._commands={
            'getdics':self.getdics,
            'open':self.open,
            'close':self.close,
            'toggle':self.toggle,
            'list':self.list,
            'load':self.load,
            'unload':self.unload,
            'grep':self.grep,
            'fetch':self.fetch,
            'reindex':self.reindex, }
        pass

    def command(self,*args):
        if len(args)==0:
            print Manager.usage % "Vedict"
            return

        # deal with args like this: one "two two" three four "five" "six six"
        s=args[0]
        args=re.findall('"[^"]+"|[^ ]+',s)
        args=[a.strip('"') for a in args]

        cmd=args[0]
        if self._commands.has_key(cmd):
            self._commands[cmd](*args[1:])
        else:
            print 'command %s not found!' %cmd
        pass

    def preview(self, *args):
        self.window.preview()

    def update_preview(self, *args):
        self.window.update_preview()

    def reindex(self,*args):
        for name in self.keys():
            dic=self[name]
            self.window.status('indexing ' % dic)
            dic.reindex()
            dic.save_index()
        self.window.status('')

    def open(self,*args):
        self.window.open()

    def close(self,*args):
        self.window.close()

    def toggle(self,*args):
        self.window.toggle()

    def list(self, *args):
        self.window.clear()
        self.window.open()
        if len(self.keys())==0:
            self.window.append('No dictionaries loaded.')
        else:
            for name in self.keys():
                self.window.append(str(self[name]))
        pass

    def load(self, *args):
        path,variety=args[0],args[1]
        #if len(args)==3:
                #super(Manager,self).load(path,variety, args[2])
        #else:
        super(Manager,self).load(path,variety)
        pass

    def unload(self, *args):
        super(Manager,self).unload(args[0])

    def getdics(self, *args):
        super(Manager,self).getdics()
        vim.command("echo 'Done!'")
        
    def grep(self, *args):
        enc=vim.eval('&encoding')
        self.pattern=args[0].decode(enc)
        if len(args)==1:
            super(Manager,self).grep(self.pattern)
        elif len(args)==2:
            super(Manager,self).grep(self.pattern, dicpattern=args[1])
        elif len(args)==3:
            super(Manager,self).grep(self.pattern, dicpattern=args[1], batches=int(args[2]))
        self.window.clear()
	
        if self.window.pwin!=None:
            self.window.pwin.open()
        vim.command('set syntax=')
        self.window.open()
        vim.command('set syntax=')
        self.fetch('',None)

    def select(self):
        vim.command('normal yy')
        self.close()

    def fetch_all(self):
        while self.fetch():
            pass
        pass

    def fetch(self, *args):
        enc=vim.eval('&encoding')
        self.window.open()
        self.window.status('Searching...')
        fetched=0

        for result in super(Manager,self).fetch():
            fetched=fetched+1
            self.window.appendResult(result,enc)
            self.window.status('Searching...')

        self.update_preview()

        if fetched==0:
            self.window.status('No more results.')
            return False
        else:
            self.window.status('(n)ext batch, fetch (a)ll')
            return True
        pass
    pass
