# Vedict: Fast Japanese / English Dictionary Lookup Vim Plugin

# Created By
Glynne Evans

# Description
This vim plugin provides fast Japanese-to-English and English-to-Japanese
dictionary lookup using files available from the [EDICT][] project.

The project is hosted [GITHUB][here].

[EDICT]: http://www.edrdg.org/jmdict/edict.html

[GITHUB]:https://github.com/gglynne/vedict

# Requirements

- Vim compiled with python
  i.e. this command should return '1':
  :echo has('python')

- EDICT dictionary files, EUC-JP encoded (see below)

# Installation

1. Unpack in your plugin directory

2. Get the dictionaries:

    :Vedict getdics

3. Load the dictionaries and mappings e.g. add the following to your .vimrc:
  
    Vedict load edict edict
    Vedict load enamdict edict
    nmap <c-l> :Vedict toggle<cr>
    vmap <c-l> y:Vedict grep "<c-r>"" edict<cr>
    vmap <c-s-l> y:Vedict grep ".*<c-r>"" edict<cr>
    vmap <c-n> y:Vedict grep <c-r>" enamdict<cr>
    vmap <c-s-n> y:Vedict grep ".*<c-r>"" enamdict<cr>

# Configuration Files

The command 'Vedict getdics' will create a configuration directory
for storing the dictionaries:

    ~.vedict/
    |-edict
    `-enamdict

# Usage

:Vedict load <dictionary name> <dictionary type>

    Register the dictionary.

:Vedict grep <search text>  <dictionary name>

    Search the dictionary sequentially.

:Vedict toggle

    Show or hide the search results.
    
The following maps are available in the results window:

    q 
    Close window.
    
    space / n 
    Get next page of hits.
    
    a 
    Get all hits.
        
    enter
    Select the current hit.
    
# Troubleshooting

E315 errors
This appears to be a vim bug and affects other plugins. Awaiting a fix!
https://github.com/vim/vim/pull/676

# License
The code is available under the [MIT license][]. 
[MIT license]: http://www.opensource.org/licenses/MIT
