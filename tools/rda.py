"""Minimal RDA v2.2 reader: list / extract files matching a substring."""
import struct, sys, zlib, os
def blocks(f):
    f.seek(0); hdr=f.read(18)
    assert hdr==b'Resource File V2.2', hdr
    f.seek(18+766); nxt=struct.unpack('<Q',f.read(8))[0]
    size=os.fstat(f.fileno()).st_size
    while nxt < size:
        f.seek(nxt)
        flags,count,dsize,dunc,nn=struct.unpack('<IIQQQ',f.read(32))
        yield nxt,flags,count,dsize,dunc
        nxt=nn
def entries(f):
    for off,flags,count,dsize,dunc in blocks(f):
        if flags & 8: continue
        f.seek(off-dsize); d=f.read(dsize)
        if flags & 2: raise SystemExit('encrypted block')
        if flags & 1: d=zlib.decompress(d)
        mr=None
        if flags & 4:
            f.seek(off-dsize-16); csz,usz=struct.unpack('<QQ',f.read(16))
            f.seek(off-dsize-16-csz); raw=f.read(csz)
            mr = zlib.decompress(raw) if flags & 1 else raw
        for i in range(count):
            e=d[i*560:(i+1)*560]
            name=e[:520].decode('utf-16-le').split('\0')[0]
            o,c,s,ts,_=struct.unpack('<QQQQQ',e[520:560])
            yield name,o,c,s,ts,flags,mr
def read(f,o,c,s,flags,mr):
    if mr is not None: return mr[o:o+s]
    f.seek(o); raw=f.read(c)
    return zlib.decompress(raw) if (flags&1) else raw
if __name__=='__main__':
    path,pat=sys.argv[1],sys.argv[2]; out=sys.argv[3] if len(sys.argv)>3 else None
    with open(path,'rb') as f:
        for name,o,c,s,ts,flags,mr in entries(f):
            if pat in name:
                print(name,s,ts)
                if out:
                    p=os.path.join(out,os.path.basename(path),name); os.makedirs(os.path.dirname(p),exist_ok=True)
                    open(p,'wb').write(read(f,o,c,s,flags,mr))
