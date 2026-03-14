import sys

def iroot(k, n):
    u, s = n, n + 1
    while u < s:
        s = u
        t = (k - 1) * s + n // pow(s, k - 1)
        u = t // k
    return s

def solve():
    with open("message.txt", "r") as f:
        lines = f.readlines()
        n = int(lines[0].split("=")[1].strip())
        e = int(lines[1].split("=")[1].strip())
        c = int(lines[2].split("=")[1].strip())

    print(f"n: {hex(n)[:50]}...")
    print(f"e: {e}")
    print(f"c: {hex(c)[:50]}...")

    # For e=20, we check if c is a perfect 20th power.
    # But wait, e=20 is even. Plaintext m could be m or (n-m).
    # Also, m^e might be slightly larger than c, like c, c+n, c+2n...
    # Low exponent attack usually means m^e < n.
    
    for k in range(100):
        val = c + k * n
        m = iroot(e, val)
        if pow(m, e, n) == (c % n):
            print(f"Found m for k={k}!")
            try:
                flag = bytes.fromhex(hex(m)[2:]).decode()
                print(f"Flag: {flag}")
                return
            except:
                # Try adding a leading zero if length is odd
                h = hex(m)[2:]
                if len(h) % 2 != 0: h = '0' + h
                try:
                    flag = bytes.fromhex(h).decode()
                    print(f"Flag: {flag}")
                    return
                except:
                    pass
    
    # If not found with simple iroot, maybe e is small but m^e > n?
    # Or maybe e=20 is NOT the real e? No, e=20 is very small.
    print("Flag not found with simple low exponent attack.")

if __name__ == "__main__":
    solve()
