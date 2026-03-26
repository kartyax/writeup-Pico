import sys
from sympy import symbols, Poly, GF

P = 2**130 - 5

def bytes_to_int(b):
    return int.from_bytes(b, 'little')

def int_to_bytes(i, n):
    return i.to_bytes(n, 'little')

def pad_and_pack(C):
    # RFC 8439 Poly1305 input construction
    C_padded = C + b'\x00' * ((16 - (len(C) % 16)) % 16)
    
    blocks = []
    for i in range(0, len(C_padded), 16):
        block = C_padded[i:i+16]
        val = bytes_to_int(block) + (1 << 128)
        blocks.append(val)
    
    len_block = int_to_bytes(0, 8) + int_to_bytes(len(C), 8)
    val = bytes_to_int(len_block)
    blocks.append(val)
    return blocks

def evaluate_poly(blocks, r_val):
    h = 0
    for a in blocks:
        h = ((h + a) * r_val) % P
    return h

def solve_for_r(p_coeffs):
    # We want to find roots of p(r) = sum(c_i * r^i) = 0 mod P
    # Using sympy.polys.polytools.roots on GF(P)
    # But since P is so large, this might be slow.
    # Alternatively, use a known root finding algorithm.
    # For small degree, we can use the following:
    import sympy.polys.polyroots
    r = symbols('r')
    f = Poly(p_coeffs, r, domain=GF(P))
    # print(f"Finding roots for K...")
    try:
        # returns {root: multiplicity}
        res = sympy.polys.polyroots.roots(f)
        return list(res.keys())
    except:
        return []

def solve(c0_full_hex, c1_full_hex, len0, len1):
    c0_full = bytes.fromhex(c0_full_hex)
    c1_full = bytes.fromhex(c1_full_hex)
    
    c0 = c0_full[:len0]
    t0 = bytes_to_int(c0_full[len0:len0+16])
    
    c1 = c1_full[:len1]
    t1 = bytes_to_int(c1_full[len1:len1+16])
    
    blocks0 = pad_and_pack(c0)
    blocks1 = pad_and_pack(c1)
    
    r = symbols('r')
    
    def get_poly_coeffs(blocks):
        # h = (((a1*r + a2)*r + ...)*r + an)*r
        #   = a1*r^n + a2*r^{n-1} + ... + an*r
        n = len(blocks)
        coeffs = [0] * (n + 1)
        for i, a in enumerate(blocks):
            coeffs[n-i] = a
        return coeffs

    coeffs0 = get_poly_coeffs(blocks0)
    coeffs1 = get_poly_coeffs(blocks1)
    
    # We want to find r such that (poly0 - poly1) - (diff_t + K*2^128) = 0 mod 2^{128}?
    # No, (poly0 + s) % 2^128 = t0 => poly0 + s = t0 + k0 * 2^128
    # poly1 + s = t1 + k1 * 2^128
    # => poly0 - poly1 = (t0 - t1) + (k0 - k1) * 2^128
    
    max_len = max(len(coeffs0), len(coeffs1))
    diff_coeffs = [0] * max_len
    for i in range(len(coeffs0)):
        diff_coeffs[i] += coeffs0[i]
    for i in range(len(coeffs1)):
        diff_coeffs[i] -= coeffs1[i]
    
    diff_t = t0 - t1
    
    for K in range(-5, 6):
        current_coeffs = list(diff_coeffs)
        current_coeffs[0] -= (diff_t + K * (1 << 128))
        
        # sympy.roots is slow for GF(P) with large P.
        # Let's try to use the fact that r is small (128 bits) and clamped.
        # Wait! Clamped r has only 106 bits.
        
        # Trial root finding
        f_roots = solve_for_r(current_coeffs[::-1]) # sympy Poly takes [high_deg, ..., low_deg]
        for r_val in f_roots:
            r_val = int(r_val)
            h0 = evaluate_poly(blocks0, r_val)
            s = (t0 - h0) % (1 << 128)
            h1 = evaluate_poly(blocks1, r_val)
            if (h1 + s) % (1 << 128) == t1:
                print(f"FOUND: r={r_val}, s={s}")
                return r_val, s
    return None

if __name__ == "__main__":
    # Challenge data
    c0_hex = "66fd7cded020ea27223e3f41b1e752e66983404841281ed707fb8fc30417440cf18d6f56c6866c8865b57ae6ab8d4099bee0aebd938845759ebb30a279ba2cb9c0f9030fa8c7d10dd15eb2fff1a365fd16c5ef5dc026e201dc3202d86a6732300d2990eebca0ed7b2e"
    c1_hex = "76fc798a8922fa662723705fe5b34af572d76643541856d45abfcab31f13581da1d23410c69129877ffc7affb6915cd7abe7a9fc8e8355309ca73aa479ea37b68ff3421aa581f1c0c7f963f23c85cb646edb4290a7296732300d2990eebca0ed7b2e"
    solve(c0_hex, c1_hex, 77, 70)
