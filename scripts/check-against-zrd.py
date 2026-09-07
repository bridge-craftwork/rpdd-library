import subprocess, sys
ZRD='/Users/rick/Development/GitHub/rpdd-library/rpdd.zrd'
f=open(ZRD,'rb')
# Groups scattered through the file, including the very last one.
for start in (0, 16384, 4_096_000, 8_192_000, 10_469_376):
    n=16384
    gen=subprocess.run(['./port',str(start),str(n)],capture_output=True,check=True).stdout
    f.seek(start*23)
    raw=f.read(n*23)
    real=b''.join(raw[i*23:i*23+13] for i in range(n))
    ok = gen==real
    print(f"deals {start:>10}-{start+n-1:<10} {'MATCH' if ok else 'MISMATCH'}  ({n} deals)")
    if not ok: sys.exit(1)
