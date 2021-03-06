class Reader:
    def __init__(self,s):
        self.s=s
        self.pos=0
    def copy_bytes(self,n,orig_pos=None):
        pos=self.pos
        if orig_pos!=None:
            pos=orig_pos
        res=self.s[pos:pos+n]
        if orig_pos==None:
            self.pos+=n
        if self.pos>len(self.s):
            self.pos=len(self.s)
        return res
    def read_bytes(self,n,pos=None):
        return self.copy_bytes(n,pos)
    def read_byte(self,pos=None):
        return self.read_bytes(1,pos)[0]
    def unread_bytes(self,n):
        self.pos-=n
    def seek_substr(self,_str,orig_pos=None):
        pos=self.pos
        if orig_pos!=None:
            pos=orig_pos
        if _str in self.s[pos:]:
            res=self.s.index(_str,pos)
            self.pos=res+len(_str)
            return _str
        return None #explicit

import struct
OBJECT_END = 'stop_object'
class SkypeLevelDBReader (Reader):
    def __init__(self,s,encoding='utf-8'):
        super(SkypeLevelDBReader,self).__init__(s)
        self.encoding=encoding
    def read_int(self):
        res=[]
        while True:
            x=self.read_byte()
            res.append(x&127)
            if x&128==0:
                break
        res_n=0
        for i in res[::-1]:
            res_n=(res_n<<7)+i
        return res_n
    def read_double(self):
        return struct.unpack('<d',self.read_bytes(8))[0]
    def read_str(self):
        _len=self.read_int()
        return self.copy_bytes(_len).decode(self.encoding)
    def read_unicode(self):
        _len=self.read_int()
        raw_str=self.copy_bytes(_len)
        return ''.join(chr((i<<8)+j) for i,j in zip(raw_str[1::2],raw_str[::2]))
    def read_something(self):
        d={
            'o':self.read_object,
            'I':self.read_int,
            'N':self.read_double,
            'T':lambda:True,
            'F':lambda:False,
            '_':lambda:None,
            '"':self.read_str,
            'c':self.read_unicode,
            '\x00':{'c':self.read_unicode},
            '{':lambda:Exception(OBJECT_END),
            'A':self.read_array,
            'a':self.read_array_lower,
            '0':lambda:'',#self.not_implemented,
            }
        pos=self.pos
        _d=d
        while True:
            smth=chr(self.read_byte())
            if smth not in _d:
                raise Exception(pos)
            if not isinstance(_d[smth],dict):
                return _d[smth]()
            else:
                _d=_d[smth]
    def read_object(self):
        res=[]
        while True:
            res.append(self.read_something())
            if isinstance(res[-1],Exception):
                del res[-1]
                _len = self.read_int()
                assert len(res)==_len*2
                return {k:v for k,v in zip(res[::2],res[1::2])}
    def read_array(self):
        _len=self.read_int()
        res=[self.read_something() for i in range(_len)]
        assert self.read_bytes(2)==b'$\x00'
        assert self.read_int()==_len
        return res

    def read_array_lower(self):
        #print(self.pos)
        _len=self.read_int()
##        if _len!=0:
##            raise NotImplementedError
        res=[self.read_something() for i in range(_len*2)]
        assert self.read_bytes(1)==b'@'
        assert self.read_int()==_len
        assert self.read_int()==_len
        return {k:v for k,v in zip(res[::2],res[1::2])}

    def not_implemented(self):
        raise NotImplementedError

if __name__=='__main__':
    #for json output
    import json
    #for sys.argv
    import sys
    #the python leveldb wrapper itself
    import plyvel
    path=(
        #'/home/user/work/skype_db/1/IndexedDB/file__0.indexeddb.leveldb'
        #'/home/user/work/skype_db/3_win/file__0.indexeddb.leveldb'
        sys.argv[1]
        )
    #we need some custom comparator
    #because there is no comparator in the skype
    #leveldb database
    #and it (the python wrapper) throws an error in this case
    def comparator(a,b):
        for i,j in zip(a,b):
            if i>j:return 1
            if i<j:return -1
            
        if len(a)>len(b):return 1
        if len(a)<len(b):return -1
        return 0
    #we open the db
    db = plyvel.DB(path,comparator=comparator,comparator_name=b'idb_cmp1')
    #and read it
    x=list(db)
    #and we close the db
    db.close()
    #this step is unneeded
    x_=sorted(x,key=lambda x:-len(x[1]))
    #encoding
    encoding=(
        'utf-8' if len(sys.argv)<=3 else sys.argv[3]
        #'cp1251'
        )
    #the result
    y=[]
    #n is for debugging purposes
    #we also don't use k here
    for n,(k,v) in enumerate(x_):
        #init the reader
        r=SkypeLevelDBReader(v,encoding)
        #seek to the start (most likely there will be an object -- 'o'
        if (not r.seek_substr(b'\xff\x14\xff\r')
            and not r.seek_substr(b'\xff\x13\xff\r')):
            #skip if there's no b'\xff\x14\xff\r'
            #or b'\xff\x14\xff\r' for windows
            continue
        try:
            #this does the thing
            y.append(r.read_something())
            #ensure we have read all this
            assert r.pos==len(r.s)
        except NotImplementedError:
            #for debugging
            print(n,r.pos-2,r.s[r.pos-2:r.pos-2+20])
    #output
    with open(sys.argv[2],'wt') as fp:
        json.dump(y,fp)
