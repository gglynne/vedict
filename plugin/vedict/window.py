#!/usr/bin/python
# vim: set fileencoding=utf-8 :
#highlight Folded guibg=darkgrey guifg=blue

import vim, re

from config import use_current_window, results_bufname

def MapAppendCascaded(lhs, rhs, mapMode):
    # Determine the map mode from the map command.
    mapChar = vim.eval('strpart("%s", 0, 1)' % mapMode)
    # Check if this is already mapped.
    oldrhs = vim.eval('maparg("%s", "%s")' % (lhs, mapChar))
    if oldrhs != None:
        slf = oldrhs
    else:
        slf = lhs
    cmd=mapMode + 'oremap  <buffer> <silent> ' +  lhs + ' ' + slf + rhs
    #print cmd
    vim.command(cmd)


def vimstatus(msg):
    """ show a message in the vim status bar """
    msg=msg.replace('\\','\\\\')
    msg=msg.replace(' ','\ ')
    vim.command('set <buffer> laststatus=2|set statusline=%s|redraw' % msg)

def getbuffer(pattern):
    """ get the first buffer with a name that matches """
    regex=re.compile(pattern)
    for b in vim.buffers:
        if b.name!=None and regex.match(b.name):
                return b
    return None

def bufwinnr(name):
    """ the number of the first window associated with name, or -1 """
    expr='bufwinnr("%s")' % name
    return int(vim.eval(expr))

class Window(object):
    """ Manages a window for displaying stuff in. Adapted from 
        http://www.vim.org/scripts/script.php?script_id=207 
        and
        http://vim.1045645.n5.nabble.com/Creating-using-background-hidden-buffers-td1143991.html
    """

    def __init__( self, 
                  root_object, 
                  bufname, 
                  maps={ 'close()':(['q',], False)},
                  vert=False, 
                  height=None):
        self.root_object=root_object
        self.last_buffer=None
        self.last_winnr=None
        self._buffer=None
        self.bufname=bufname
        self.maps=maps
        self.height=height
        self.vert=vert
        pass

    laststatus=None

    def status(self,msg):
        #""" show a message in the vim status bar """
        msg=msg.replace('\\','\\\\')
        msg=msg.replace(' ','\ ')
        self.open()
        #vim.command('set laststatus=2|set statusline=%s|redraw' % msg)
        vim.command('setlocal statusline=%s|redraw' % msg)
    
    def nop(self):
        pass

    def open(self,scroll_to_end=False):
        self._open()
        if scroll_to_end:
            vim.command('normal G')
        pass

    def close(self):
        """ close any window on the current tab """
        self.status('')
        if use_current_window and self.last_buffer:
            vim.command('buffer %s' % self.last_buffer)
        else:
            # close our window
            winnum = bufwinnr(self.bufname) 
            if winnum!=-1:
                    vim.command('%swincmd w' % winnum)
                    vim.command('q')

            if self.last_winnr!=None:
                    vim.command('%swincmd w' % self.last_winnr)
            self.last_winnr=None


    def _open(self,scroll_to_end=False):
        """ open the window"""

        if self.buffer==vim.current.buffer:
            return

        # Save the current buffer and window number so we can return there on close()
        self.last_buffer=vim.current.buffer.number
        self.last_winnr=vim.eval('winnr()')

        # get the number of the first window on this tab that hosts this buffer
        winnum = bufwinnr(self.bufname) 
        if winnum!=-1:
            # the window is open so jump to it
            vim.command('%swincmd w' % winnum)
            vim.command('setlocal modifiable')
            return

        # no window, so...

        if use_current_window:
            # switch buffer in current window
            vim.command('buffer %s' % self.buffer.number)
        else:

            # Open a new window at the bottom
            if self.height==None:
                height=""
            else:
                height=self.height

            if self.vert:
                winsplit='silent! setlocal spr | silent! %s vsplit +buffer%s'
                vim.command(winsplit %(height, self.buffer.number))
            else:
                winsplit='silent! botright %s split +buffer%s'
                vim.command(winsplit %(height, self.buffer.number))
                    
    
    def clear(self):
        self.buffer[:] = None

    def append(self,s):
        """ append text to the buffer silently, creating it if necessary """
        if len(self.buffer[0])==0:
            self.buffer[0]=s
        else:
            self.buffer.append(s)
        pass


    def toggle(self):
        """ hide or show the window """
        if self.isopen():
            self.close()
        else:
            self.open()

    def isopen(self):
        """ if the window is open on the current tab """
        winnum = bufwinnr(self.bufname) 
        return winnum!=-1

    def buffgetter(self):
        """ creates a buffer it doesn't exist """
        if self._buffer==None:
            self._buffer=getbuffer(self.bufname)
            if self._buffer==None:
                self._buffer=self.makebuffer(self.bufname) # make a new buffer silently
        return self._buffer

    buffer = property(buffgetter)

    def makebuffer(self,name):
        """ create a buffer in the background """
        # save the current buffer
        b_current=vim.current.buffer

        # stop ui from updating
        vim.command('set lazyredraw')
        
        # create
        #vim.command('edit %s' % name)
        vim.command('split %s' % name)

        if vim.current.buffer.name.endswith(name):
            self.initbuffer(self.maps, self.root_object)
            b_new=vim.current.buffer
        else:
            b_new=None

        # restart ui update

        #vim.command('buffer %s' % b_current.number)
        vim.command('quit')
        vim.command('set nolazyredraw')
        return b_new

    def initbuffer(self,maps,root_object):
        """ Mark the buffer as scratch, but let it remain hidden when window quit """

        vim.command("setlocal buftype=nofile")
        vim.command("setlocal bufhidden=hide")
        vim.command("setlocal noswapfile")
        vim.command("setlocal nowrap")
        vim.command("setlocal nobuflisted")
        vim.command("setlocal winfixheight")
        vim.command("setlocal wrap")

        # Setup the cpoptions properly for the maps to work
        vim.command("let old_cpoptions = &cpoptions")
        vim.command("set cpoptions&vim")

        # Create mappings 
        for cmd in maps.keys():
            keys, passthrough=maps[cmd]
            for key in keys:
                if  passthrough:
                    MapAppendCascaded( key, ":py %s.%s<CR>" % (root_object, cmd), 'n' )
                else:
                    #cmd= "nmap <buffer> <silent> %s :py %s.%s<CR>" % (key, root_object, cmd)
                    #cmd= "nmap %s :py %s.%s" % (key, root_object, cmd)
                    #cmd= "nmap %s :py %s" % (key, root_object)
                    vim.command( "nmap <buffer> <silent> %s :py %s.%s<CR>" % (key, root_object, cmd) )

        #" Restore the previous cpoptions settings
        vim.command("let &cpoptions = old_cpoptions")

    @staticmethod
    def test():
        w=Window('w')
        w.open()
        print w.last_buffer
        print w.last_winnr
    pass



class R(list):
    """ one result in a set of results """
    def __init__(self, dic,fields):
        self.dic=dic
        self.extend(fields)
    
    def __repr__(self):
        return " ".join(self)
    
    def hi(self,groups):
        cmds=[]
        for i in range(0,len(self)):
                cmds.append('syntax match %s "%s"' % (groups[i % len(groups)], self[i]))
        return cmds
	

class ResultsWindow(Window):

    def __init__(self,root_object=None,maps={ 'close()':['q',], }):
        self.root_object=root_object
        super(ResultsWindow,self).__init__(root_object,results_bufname,maps=maps,vert=False, height=5)
        self._results=[]
        self.pwin=None

    def clear(self):
        super(ResultsWindow,self).clear()
        self._results=[]

    def close(self):
        super(ResultsWindow,self).close()
        if self.pwin:
            self.preview_close()

    groups=['Title','LineNr','MoreMsg']

    def appendResult(self,r,enc):
        self._results.append(r)
        self.append(r.__repr__().encode(enc))
        for cmd in r.hi(self.groups):
            try:
                vim.command(cmd.encode(enc))
            except:
                pass
        vim.command('normal G')
    
    def update_preview(self):
        if self.pwin==None:
            return
        row, col=vim.current.window.cursor
        r=self._results[row-1]
        enc=vim.eval('&encoding')
        self.pwin.clear()
        s=r.__repr__().encode(enc)
        self.pwin.append(s)
        self.pwin.open(s)
        for cmd in r.hi(self.groups):
            try:
                vim.command(cmd.encode(enc))
            except:
                pass
        self.open()


    def preview(self):
        #self.open()
        if self.pwin==None:
            self.pwin=Window(
                root_object=self.root_object+'.window', 
                bufname=self.bufname+'_preview', 
                maps={ 'preview_close()':( ['q',], False ), },
                vert=True, 
                height=None
                )
        self.pwin.open()
        #self.update_preview()
        self.open()
    
    def preview_close(self):
        self.pwin.close()


    @staticmethod
    def test():
        w=ResultsWindow('w')
        w.open()
        enc=vim.eval('&encoding')
        # objects to display
        results=[]
        results.append( R(r'c:\working\test',['Zs', 'Earth Fault Impedance', 'The resistance between live and earth.']) )
        results.append( R(r'c:\working\test',['head word', 'definition here', 'notes here']) )
        results.append( R(r'c:\working\test',['Zs', 'Earth Fault Impedance', 'The resistance between live and earth.']) )
        for r in results:
            w.appendResult(r,enc)
        pass
