#!/usr/bin/python
# vim: set fileencoding=utf-8 : highlight Folded guibg=darkgrey guifg=blue


import os
try:
    import vim
except ImportError:
    vim = None

def getopt(name, default):
    exists=int(vim.eval('exists("%s")' % name))
    if exists:
        return vim.eval(name)
    else:
        return default

# default search path for dictionaries
default_dic_path = os.path.expanduser(os.path.join('~','.vedict'))

# download URLS
dic_urls = {    'edict':    'http://ftp.monash.edu.au/pub/nihongo/edict.gz',
                'enamdict': 'http://ftp.monash.edu.au/pub/nihongo/enamdict.gz' }

# name for results buffer
results_bufname='__vedict__'

# whether to show the results buffer in the current window
use_current_window=False

# if use_current_window is 0, the height of the results window
height=5

# the number of results in batch: search algorithm blocks until this many results are found
batches=5

# the key to toggle visibility of results window on current tab
toggle_key='<c-l>'

# key maps within the results window
window_maps= { 'close()':['q',], 'select':['<cr>',], 'fetch':['<space>',], }

# maps dictionary varieties to their classes
from edict import Edict, GrepFile
_types={ 'edict':Edict, 'grep':GrepFile, } # used by Manager.load to map 'variety' to class      

if vim:
    # allow user to override these
    default_dic_path = getopt('g:vedict_default_dic_path', default_dic_path)
    results_bufname = getopt('g:vedict_results_bufname',results_bufname)
    use_current_window=int(getopt('g:vedict_use_current_window',use_current_window))
    height=getopt('g:vedict_height',height)
    batches=getopt('g:vedict_batches',batches)
    toggle_key=getopt('g:vedict_window_toggle_key',toggle_key)
    window_maps=getopt('g:vedict_window_maps',window_maps)
