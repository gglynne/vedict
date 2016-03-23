

let dbg=0

if dbg 
	" F5 will rerun this script after it has been sourced
	map <buffer> <f5> :w<cr>:so % <cr>
else
	if exists("g:vedict_loaded") | finish | endif
endif
let g:vedict_loaded=1

python << EOF
#  lets python ignore everything above this line (docstring). """

import vim, os
dbg=vim.eval('dbg')

if not dbg:
    print 'put production initializer here'
    vim.command('finish')

# nobble path for libs
lib=os.path.join(vim.eval("expand('<sfile>:p:h')"),'vedict')
import sys

if not lib in sys.path:
    sys.path.append(lib)

import config
reload(config)

import edict
reload(edict)

import ui
reload(ui)

# everything implemented in python via this object
root_object='_vedict'
_vedict=ui.Manager(root_object)

vim.command('command! -nargs=* Vedict exec(\'py %s.command(<q-args>)\')' % root_object)
#vim.command('Vedict load edict edict')
#vim.command('Vedict load enamdict edict')
#vim.command('nmap <c-l> :Vedict toggle<cr>')
#vim.command('vmap <c-l> y:Vedict grep "<c-r>"" edict<cr>')
#vim.command('vmap <c-s-l> y:Vedict grep ".*<c-r>"" edict<cr>')
#vim.command('vmap <c-n> y:Vedict grep <c-r>" enamdict<cr>')
#vim.command('vmap <c-s-n> y:Vedict grep ".*<c-r>"" enamdict<cr>')

#def test():
	#edict.Edict.test('edict')
	#edict.GrepFile.test()
	#from edict import GrepFile

	#path=os.path.join(os.path.expanduser('~'),'mandrake/jp/')
	#fname='vocab.utf'
	#enc='utf8'
	#dic=GrepFile(path,fname)
	#for r in dic.grep('.*漢字'.decode(enc)):
		##print r.__repr__().encode(enc)
		#pass

	#import window
	#reload(window)
	#window.Window.test()
	#window.ResultsWindow.test()

EOF
