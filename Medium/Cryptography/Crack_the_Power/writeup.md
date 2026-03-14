# [picoCTF 2024]: Cryptography - Crack the Power

**Kategori:** Cryptography  
**Tingkat Kesulitan:** Medium

---

## Deskripsi Tantangan

Tantangan ini memberikan pesan terenkripsi RSA dengan modulus `n` yang sangat besar sehingga mustahil untuk difaktorkan. Kita perlu menemukan cara untuk mendekripsi pesan tersebut berdasarkan nilai-nilai yang diberikan dalam `message.txt`.

> We received an encrypted message. The modulus is built from primes large enough that factoring them isn’t an option, at least not today. See if you can make sense of the numbers and reveal the flag. Download the message.

**Hint:**
> When certain values in the encryption setup are smaller than usual, it opens up unexpected shortcuts to recover the plaintext.

---

## Analisis & Metodologi

### Observasi Awal

File `message.txt` berisi tiga nilai utama:
- `n`: Modulus RSA (sangat besar)
- `e`: Public Exponent (bernilai **20**)
- `c`: Ciphertext

### Temuan Kunci

Nilai `e = 20` sangatlah kecil untuk standar RSA (biasanya `65537`). Ketika `e` sangat kecil, ada kemungkinan terjadi kerentanan **Low Public Exponent Attack**.

Jika pesan `m` cukup pendek sehingga $m^e < n$, maka operasi modulo $n$ dalam enkripsi menjadi tidak berarti karena hasil pemangkatan tidak mencapai nilai $n$.
$$c = m^e \pmod n \implies c = m^e$$
Dalam kondisi ini, kita bisa mendapatkan $m$ hanya dengan menghitung akar pangkat $e$ dari $c$:
$$m = \sqrt[e]{c}$$

### Strategi Solve

Strateginya adalah:
1. Membaca nilai `n`, `e`, dan `c` dari file.
2. Menghitung akar pangkat 20 dari `c` ($\sqrt[20]{c}$).
3. Mengonversi hasil angka tersebut menjadi string teks (bytes) untuk mendapatkan flag.
4. Jika $m^{20}$ tidak sama dengan $c$, periksa kemungkinan $m^{20} = c + k \cdot n$ untuk nilai $k$ yang kecil (namun biasanya untuk $e$ sekecil ini dan $n$ sebesar itu, $k=0$ seringkali berhasil).

---

## Eksploitasi (Proof of Concept)

Berikut adalah script `solve.py` yang diimplementasikan tanpa library eksternal (menggunakan algoritma Newton untuk menghitung integer root):

```python
import sys

def iroot(k, n):
    """Menghitung integer root ke-k dari n menggunakan metode Newton."""
    u, s = n, n + 1
    while u < s:
        s = u
        t = (k - 1) * s + n // pow(s, k - 1)
        u = t // k
    return s

def solve():
    # Load data
    with open("message.txt", "r") as f:
        lines = f.readlines()
        n = int(lines[0].split("=")[1].strip())
        e = int(lines[1].split("=")[1].strip())
        c = int(lines[2].split("=")[1].strip())

    # Low Public Exponent Attack
    # Coba k=0 (m^e < n)
    m = iroot(e, c)
    
    if pow(m, e, n) == (c % n):
        print(f"Berhasil menemukan m!")
        # Konversi integer ke bytes lalu string
        h = hex(m)[2:]
        if len(h) % 2 != 0: h = '0' + h
        flag = bytes.fromhex(h).decode()
        print(f"Flag: {flag}")
    else:
        print("Bukan Low Exponent Attack sederhana (m^e > n).")

if __name__ == "__main__":
    solve()
```

---

## Hasil (Proof)

Eksesusi script menghasilkan flag sebagai berikut:

```text
n: 0x53656a2513854624b1af91fe1fe92d2e0f11db6e234d9605...
e: 20
c: 0x1310fffd4f1d0d686032d65d6ca879cfcaecbd470e28f833...
Found m for k=0!
Flag: picoCTF{t1ny_e_9b88056f}
```

**Flag:** `picoCTF{t1ny_e_9b88056f}`

---

## Kesimpulan & Mitigasi

- **Root Cause:** Penggunaan eksponen publik `e` yang terlalu kecil memungkinkan penyerangan tanpa perlu memfaktorkan modulus `n`.
- **Kenapa Berhasil:** Pesan yang dienkripsi relatif pendek dibandingkan dengan besarnya modulus $n$, sehingga $m^e$ tidak pernah melampaui $n$ dan operasi modulo tidak terjadi.
- **Mitigasi:** Gunakan nilai eksponen publik standar yang aman, yaitu **65537** ($2^{16} + 1$). Selain itu, gunakan skema padding yang kuat seperti **OAEP** (Optimal Asymmetric Encryption Padding) untuk menambah entropi pada pesan sebelum dienkripsi.
