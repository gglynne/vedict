#!/usr/bin/python
# vim: set fileencoding=utf-8 :
#highlight Folded guibg=darkgrey guifg=blue

import os,codecs,pickle,re,random
from config import default_dic_path

class EdictResult(list):
	""" A single hit.  """

	def __init__(self,dic,offset,line):
		self.dic=dic
		self.offset=offset
		fields=self._parse(line)
		self.extend(fields)
	
	def _parse(self, line):
		""" extract the reading from the first field if present """
		fields=line.split('/')
		reading=fields[0].find('[')
		if reading!=-1:
				start=reading
				reading=fields[0][start+1:fields[0].find(']')]
				fields[0]=fields[0][0:start-1]
		else:
			reading=''
		ordered=[fields[0],reading]
		ordered.extend(fields[1:])
		return ordered
			
	def __repr__(self):
		return " ".join(self)
	
	def select(self):
		return line
	
	def hi(self,groups):
		cmds=[]
		for i in range(0,len(self)):
			s=self[i].replace("'","\\'")
			s=s.strip()
			if len(s)>0:
				cmds.append("syntax match %s '%s'" % (groups[i % len(groups)], s))
		return cmds


class Edict(object):
	""" Parses, indexes and searches an edict dictionary.  http://www.csse.monash.edu.au/~jwb/edict_doc.html """

	FILE_ENCODING='euc-jp'

	def __init__(self, path,name):
		self.path=path
		self.path_index=path+'.idx'
		self.name=name
		self.index=None
		self.fp=None


	def __repr__(self):
		if self.index==None:
			str_index="no index loaded"
		else:
			str_index="index loaded with %s keys" % len(self.index.keys())

		return '<Edict (%s) `%s` at %s>' % (str_index,self.name,self.path)

	
	def grep(self,pattern, flags=0):
		pattern=pattern.strip()
		if len(pattern)==0:
			return
		head,tail=re.match('([*.]*)(.*)',pattern).groups()
		wildcard=len(head)>0
		if len(tail)==0:
			index_char=None
		else:
			index_char=tail[0]
		if self.index==None:
			offset=0
		elif index_char==None or not self.index.has_key(index_char):
			i=random.randint(0,len(self.index.values())-1)
			offset=self.index.values()[i]
		else:
			offset=self.index[index_char]

		regex=re.compile(pattern,flags)

		if self.fp==None:
			self.fp=open(self.path, 'r')
		self.fp.seek(offset)

		indexed=True
		
		wrapped=False
		matched=False
		while True:
			pos=self.fp.tell()
			raw=self.fp.readline()
			if wrapped and self.fp.tell() > offset:
				break
			line=raw.decode(self.FILE_ENCODING)
			if not line:
				self.fp.seek(0)
				wrapped=True
			elif regex.match(line):
				matched=True
				yield EdictResult(self,offset,line)
			elif (not wildcard) and matched:
				print 'breaking'
				break
		pass

	def save_index(self,limit=None):
		fp=open(self.path_index,'w')
		pickle.dump(self.index,fp)
		fp.close()

	def load_index(self,limit=None):
		if os.path.exists(self.path_index):
			fp=open(self.path_index,'r')
			self.index=pickle.load(fp)
			fp.close()
		pass
	
	def reindex(self,limit=None):
		self.index={}
		fp=codecs.open(self.path,'r',self.FILE_ENCODING) # read encoded to consume lines properly
		while limit==None or limit>0:
			offset=fp.tell()
			line=fp.readline()
			if not line:
				break
			key=line[0]
			if not self.index.has_key(key):
				self.index[key]=offset
			if limit:
				limit=limit-1
		fp.close()

	def index_test(self, limit=None):
		fp=open(self.path, 'r') # read bytes seems to be enough
		for key in self.index.keys():
			offset=self.index[key]
			fp.seek(offset)
			raw=fp.readline()
			line=raw.decode(self.FILE_ENCODING)
			if limit:
				limit=limit-1
				if limit==0:
					break
		fp.close()

	@staticmethod
	def test(fname):
		""" search edict for '漢字' and dump results to console  """
		enc='utf8'
		path=os.path.join(default_dic_path,fname)
		dic=Edict(path,fname)
		dic.load_index()
		for r in dic.grep('.*漢字'.decode(enc)):
			print r.__repr__().encode(enc)
		pass

class GrepResult(list):
	""" A single hit.  """

	def __init__(self,dic,keyword, lines, index,):
		self.dic=dic
		self.keyword=keyword
		self.extend(lines)
	
	def __repr__(self):
		return " ".join(self)
	
	def select(self):
		return line
	
	def hi(self,groups):
		cmds=[]
		for i in range(0,len(self)):
			s=self[i].replace("'","\\'")
			s=s.strip()
			if len(s)>0:
				cmds.append("syntax match %s '%s'" % (groups[i % len(groups)], s))
		return cmds

class GrepFile(object):
	""" a greppable file  """

	FILE_ENCODING=None

	def __init__(self, path,name):
		self.path=path
		self.name=name
		self.index=None
		self.fp=None


	def __repr__(self):
		return '<GrepFile `%s` at %s>' % (self.name,self.path)

	
	def grep(self,pattern, flags=0):
		pattern=pattern.strip()
		if len(pattern)==0:
			return
		regex=re.compile(pattern,flags)
		for i in range(5):
			yield GrepResult("this is a hit")
		pass

	def save_index(self,limit=None):
		pass

	def load_index(self,limit=None):
		pass
	
	def reindex(self,limit=None):
		pass

	@staticmethod
	def test(fname):
		""" search edict for '.*漢字' and dump results to console  """
		enc='utf8'
		path=os.path.join(default_dic_path,fname)
		dic=GrepFile(path,fname)
		for r in dic.grep('.*漢字'.decode(enc)):
			print r.__repr__().encode(enc)
		pass
pass
