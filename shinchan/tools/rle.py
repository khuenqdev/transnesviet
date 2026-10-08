# RLE codec compatible with the game's screen decompressor at $D905
def compress(data):
    data=list(data); used=set(data)
    marker=next(v for v in range(256) if v not in used)
    out=[marker]; i=0; n=len(data)
    while i<n:
        j=i
        while j<n and data[j]==data[i] and j-i<255: j+=1
        if j-i>=4: out+=[marker,data[i],j-i]
        else: out+=data[i:j]
        i=j
    return bytes(out)
def decompress(buf,count):
    marker=buf[0]; p=1; out=[]
    while len(out)<count:
        b=buf[p]; p+=1
        if b==marker: v=buf[p]; c=buf[p+1]; p+=2; out+=[v]*(c if c else 256)
        else: out.append(b)
    return out[:count],p
