# [Nama CTF Event]: [Kategori] - [Nama Challenge]

**Kategori:** Web Exploitation / Pwn / Crypto / Forensics / Reverse / Misc  
**Tingkat Kesulitan:** Easy / Medium / Hard

---

## Deskripsi Tantangan

Jelasin konteks challenge-nya di sini. Kamu diberikan apa? URL? File? Binary?  
Apa tujuan akhirnya?

> Sertakan kutipan deskripsi asli dari platform jika ada, misal:  
> _"The image link appears broken... twice as badly..."_

---

## Analisis & Metodologi

Jelasin proses lo waktu pertama kali menganalisis challenge ini.

### Observasi Awal

Ceritain apa yang lo lihat pertama kali saat membuka challenge:

- Tampilan awal URL / file yang diberikan
- Tools yang dipakai buat recon awal (`file`, `strings`, `nmap`, `curl`, dll)
- Hal-hal mencurigakan yang lo notice

```bash
# Contoh output recon awal
$ curl -s https://target.ctf.io/
# ... output menarik di sini
```

### Temuan Kunci

Jelasin apa yang jadi titik balik analisis lo. Potongan kode, struktur file, atau behavior aneh yang lo temukan:

```javascript
// Contoh: potongan kode kunci dari source
for (var i = 0; i < LEN; i++) {
  // logika yang mencurigakan
}
```

Artinya / interpretasi lo:

> Jelasin makna dari kode/temuan di atas. Kenapa ini penting? Apa celahnya?

### Strategi Solve

Jelasin pendekatan lo sebelum mulai eksploitasi:

- Kenapa lo pilih approach ini?
- Konsep/teori yang jadi landasan (misal: _Known-Plaintext Attack_, _Format String Bug_, dll)
- Kalau ada rabbit hole, ceritain juga — ini justru bikin write up makin bagus 🐇

---

## Eksploitasi (Proof of Concept)

Jelasin langkah-langkah eksploitasinya secara berurutan.

### Step 1: [Nama Step]

Penjelasan singkat apa yang dilakukan di step ini:

```python
import requests
# kode lengkap di sini, jangan ada bagian yang di-skip
# pembaca harus bisa langsung jalanin ini

TARGET = "http://target.ctf.io:PORT"

# Step 1: ambil data
r = requests.get(f"{TARGET}/endpoint")
data = r.json()
print(f"[*] Data fetched: {len(data)} bytes")
```

### Step 2: [Nama Step]

```python
# lanjutan kode
for item in data:
    # proses data
    pass
```

### Step 3: [Nama Step] _(kalau ada)_

```python
# final payload / decode / reconstruct
result = do_something(data)
print(f"[+] Result: {result}")
```

---

## Hasil (Proof)

Output aktual saat script dieksekusi:

```text
[*] Connecting to target...
[*] Fetched 1337 bytes
[*] Brute forcing...
[+] Match found!

[!!!] FLAG DITEMUKAN: CTF{ini_adalah_flagnya}
```

**Flag:** `CTF{ini_adalah_flagnya}`

---

## Kesimpulan & Mitigasi

Jelasin kenapa challenge ini bisa dipecahkan dan apa pelajaran yang bisa diambil:

- **Root Cause:** Apa celah utamanya?
- **Kenapa Berhasil:** Faktor apa yang memudahkan eksploitasi (misal: predictable header, client-side logic, dll)
- **Mitigasi:** Kalau lo jadi developer, gimana cara nyegah ini?

> Contoh: _"Kerentanan ini bisa dibongkar karena metode enkripsi naif bergantung pada client-side script, dan format file seperti `.png` memiliki header yang predictable — mempermudah Known-Plaintext Attack."_
