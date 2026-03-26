# picoCTF 2025: Cryptography - ChaCha Slide

**Kategori:** Cryptography  
**Tingkat Kesulitan:** Hard  
**Flag:** `picoCTF{7urn_17_84ck_n0w_a080fb27}`

---

## Deskripsi Tantangan

> Modern authenticated-encryption ciphers like ChaCha20-Poly1305 are great, but they can quickly fall apart if their limits aren't respected. Can you violate the integrity of a message encrypted by this program?

Server menyediakan service di `nc activist-birds.picoctf.net 63005` dan source code `challenge.py`.  
Tujuan: memalsukan autentikasi pesan `"But it's only secure if used correctly!"` dan membuatnya diterima server sebagai valid.

---

## Analisis & Metodologi

### Observasi Awal

```bash
$ nc activist-birds.picoctf.net 63005
Plaintext: 'Did you know that ChaCha20-Poly1305 is an authenticated encryption algorithm?'
Plaintext (hex): 44696420796f75...
Ciphertext (hex): 66fd7c...6732300d2990eebca0ed7b2e

Plaintext: 'That means it protects both the confidentiality and integrity of data!'
Plaintext (hex): 54686174...
Ciphertext (hex): 76fc79...6732300d2990eebca0ed7b2e

What is your message?
```

**Perhatikan:** nonce di kedua ciphertext (`6732300d2990eebca0ed7b2e`) **identik!**

### Temuan Kunci

Membaca `challenge.py`:

```python
key = shasum(shasum(secrets.token_bytes(32) + flag.encode()))

# Generate a random nonce to be extra safe
nonce = secrets.token_bytes(12)

def encrypt(message):
    cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return ciphertext + tag + nonce

goal = "But it's only secure if used correctly!"

# ...
user = bytes.fromhex(input("What is your message? "))
user_message = decrypt(user)
if goal in repr(user_message):
    print(flag)
```

**Bug kritis:** `key` dan `nonce` bersifat konstan untuk seluruh sesi. Kedua pesan dienkripsi dengan **key dan nonce yang sama** — ini adalah **Nonce Reuse** pada ChaCha20-Poly1305.

### Strategi Solve

Nonce reuse pada ChaCha20-Poly1305 membongkar dua kelemahan sekaligus:

1. **Keystream ChaCha20 identik** → dapat di-XOR untuk mendapatkan keystream, lalu mengenkripsi pesan apapun.
2. **Kunci Poly1305 (`r`, `s`) identik** → dapat dipulihkan dengan aljabar, lalu memalsukan tag untuk pesan apapun.

**Teori pemulihan `r`:**

Poly1305 menghitung tag sebagai:
```
tag = (H(r) + s) mod 2^128
```
di mana `H(r) = Σ(block_i × r^(n-i)) mod P` dan `P = 2^130 - 5`.

Dengan dua pasang `(ciphertext, tag)` yang menggunakan `(r, s)` sama:
```
H0(r) + s ≡ T0  (mod 2^128)
H1(r) + s ≡ T1  (mod 2^128)
```
⟹ `H0(r) - H1(r) ≡ T0 - T1  (mod 2^128)`

Ini adalah **persamaan polinomial dalam `r` modulo P** (dengan sedikit ambiguitas dari `mod 2^128`):
```
(poly0 - poly1)(r) ≡ (T0 - T1) + K × 2^128  (mod P)
```
untuk beberapa `K` kecil. Kita cukup mencoba K ∈ {-6..6} dan mencari akar polynomial berderajat ~7 di atas GF(P) menggunakan **algoritma Cantor-Zassenhaus**.

---

## Eksploitasi (Proof of Concept)

### Step 1: Ambil Data dari Server & Verifikasi Nonce Reuse

```python
import socket

HOST, PORT = "activist-birds.picoctf.net", 63005
sock = socket.create_connection((HOST, PORT), timeout=10)
data = b""
while b"What is your message?" not in data:
    data += sock.recv(4096)

lines = data.decode().strip().splitlines()
ct_hex_lines = [l.split(": ")[1] for l in lines if "Ciphertext (hex):" in l]

c0_full = bytes.fromhex(ct_hex_lines[0])
c1_full = bytes.fromhex(ct_hex_lines[1])

# Split: ciphertext | tag(16B) | nonce(12B)
nonce = c0_full[77+16:]
assert c0_full[77+16:] == c1_full[70+16:]  # Nonce reuse confirmed!
```

### Step 2: Implementasi Root Finding atas GF(2^130-5)

Implementasi polynomial arithmetic dan Cantor-Zassenhaus di GF(P):

```python
P = 2**130 - 5

def pad_and_pack(ct):
    """Buat Poly1305 blocks dari ciphertext (tanpa AAD)."""
    blocks = []
    padded = ct + b'\x00' * ((-len(ct)) % 16)
    for i in range(0, len(padded), 16):
        blocks.append(int.from_bytes(padded[i:i+16], 'little') + (1 << 128))
    # length block: penting! juga mendapat sentinel +2^128
    len_block = b'\x00'*8 + len(ct).to_bytes(8, 'little')
    blocks.append(int.from_bytes(len_block, 'little') + (1 << 128))
    return blocks

def poly1305_eval(blocks, r):
    h = 0
    for a in blocks:
        h = (h + a) * r % P
    return h

def roots_gf(f, p):
    """Cari semua akar polynomial f modulo p menggunakan Cantor-Zassenhaus."""
    # 1. Hitung gcd(f, x^p - x) = produk semua faktor linear
    xp = poly_pow_mod([1, 0], p, p, f)  # x^p mod f
    h = poly_gcd(f, poly_sub(xp, [1, 0], p), p)
    # 2. Split h dengan Cantor-Zassenhaus
    return _split(h, p)
```

### Step 3: Pulihkan (r, s) dari Dua Pasang Pesan

```python
def recover_r_s(ct0, t0, ct1, t1):
    blk0 = pad_and_pack(ct0)
    blk1 = pad_and_pack(ct1)
    
    diff = [c0[i] - c1[i] for i in range(max_len)]  # poly koefisien
    diff_t = t0 - t1
    
    for K in range(-6, 7):
        target = diff_t + K * (1 << 128)
        test = list(diff)
        test[-1] = (test[-1] - target) % P
        
        for r_val in roots_gf(test, P):
            h0 = poly1305_eval(blk0, r_val)
            s_val = (t0 - h0) % (1 << 128)
            h1 = poly1305_eval(blk1, r_val)
            if (h1 + s_val) % (1 << 128) == t1:
                return r_val, s_val
```

### Step 4: Forge Tag & Kirim ke Server

```python
goal = b"But it's only secure if used correctly!"

# Keystream dari nonce reuse
keystream = bytes(a ^ b for a, b in zip(ct0, pt0))
goal_ct = bytes(goal[i] ^ keystream[i] for i in range(len(goal)))

# Forge Poly1305 tag dengan r dan s yang sudah dipulihkan
goal_blocks = pad_and_pack(goal_ct)
h = poly1305_eval(goal_blocks, r)
forged_tag = (h + s) % (1 << 128)
tag_bytes = forged_tag.to_bytes(16, 'little')

payload = (goal_ct + tag_bytes + nonce).hex()
sock.sendall((payload + "\n").encode())
```

---

## Hasil (Proof)

```text
=== ChaCha Slide exploit ===
[*] Connecting to activist-birds.picoctf.net:63005
[*] Server output received
[+] Nonce (reused): 1b221c23e1084b70190f0ecf
[*] Recovering Poly1305 (r, s)…
[+] K=0  r=5098152886763970150747794774203327772  s=0xc7b78ec930a4e2739c...
[+] r = 5098152886763970150747794774203327772
[+] s = 265469457528389129761519353790065860911
[+] Payload: 95761e618a4a67e35490ab2276853b51...1b221c23e1084b70190f0ecf
[*] Server response:
'User message (decrypted): b"But it\'s only secure if used correctly!"\npicoCTF{7urn_17_84ck_n0w_a080fb27}\n'
```

**Flag:** `picoCTF{7urn_17_84ck_n0w_a080fb27}`

---

## Kesimpulan & Mitigasi

- **Root Cause:** Server menggunakan nonce yang sama untuk mengenkripsi dua pesan berbeda dalam satu sesi. Ini melanggar aturan fundamental ChaCha20-Poly1305.
  
- **Kenapa Berhasil:**
  1. Nonce reuse → keystream ChaCha20 identik → keystream dapat dipulihkan dan digunakan untuk "encrypt" pesan apapun.
  2. Nonce reuse → kunci Poly1305 `(r, s)` identik di kedua pesan → dapat dipulihkan dengan menyelesaikan persamaan polinomial berderajat ~7 di GF(2^130-5) menggunakan algoritma Cantor-Zassenhaus.

- **Mitigasi:**
  - Gunakan **nonce unik** untuk setiap enkripsi (gunakan counter deterministik atau CSPRNG dengan state yang diupdate).
  - Pertimbangkan **key rotation** per sesi sehingga jika nonce terulang, key-nya berbeda.
  - Jika menggunakan ChaCha20-Poly1305, bersikeras menggunakan ChaCha20-Poly1305 dengan **extended nonce (XChaCha20)** yang memiliki nonce 192-bit — mengurangi risiko collision drastis.
  - Referensi: RFC 8439 Section 4 — "Security Considerations" menyebutkan secara eksplisit bahwa penggunaan nonce yang sama dua kali dengan kunci yang sama adalah "catastrophic failure".

> Bug ini adalah contoh klasik "catastrophic nonce reuse" — satu nonce yang dipakai ulang membuat seluruh keamanan sistem collapse, baik kerahasiaan (ChaCha20) maupun integritas (Poly1305).
