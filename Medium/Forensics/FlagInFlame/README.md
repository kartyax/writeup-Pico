# PicoCTF: Forensics - Flag in Flame

**Kategori:** Forensics
**Tingkat Kesulitan:** Medium (Large File)

---

## Deskripsi Tantangan

Tim SOC menemukan file log yang sangat besar setelah pelanggaran baru-baru ini. Bukannya log biasa, mereka menemukan blok teks terenkripsi/terkode yang sangat besar. Misi kita adalah menyelidiki file tersebut dan mengungkap informasi tersembunyi di dalamnya.

> **Hints:** Gunakan base64 untuk men-decode data dan menghasilkan file gambar.

---

## Analisis & Metodologi

### Observasi Awal

File `logs.txt` berisi satu baris string panjang yang terlihat seperti Base64 encoding. Ukuran filenya mencapai ~1.5 MB.
Pembukaan string diawali dengan `iVBORw0KGgo...` yang merupakan header standar untuk file gambar format **PNG** jika di-decode dari Base64.

### Strategi Solve

1. Men-decode string Base64 dari `logs.txt`.
2. Menyimpan hasilnya ke dalam file biner dengan ekstensi `.png`.
3. Memeriksa gambar yang dihasilkan untuk mencari petunjuk atau Flag.

---

## Eksploitasi (Proof of Concept)

### Step 1: Decode Base64 ke Gambar

Menggunakan Python untuk menangani file yang besar dengan efisien:

```python
import base64

# Membaca data encoded dari file
with open('logs.txt', 'r') as f:
    encoded_data = f.read().strip()

# Decode dan simpan sebagai image
with open('output_image.png', 'wb') as f:
    f.write(base64.b64decode(encoded_data))
```

### Step 2: Analisis Gambar

Setelah gambar `output_image.png` dibuka, terlihat gambar seorang hacker. Di bagian paling bawah gambar terdapat deretan string Hexadecimal:

`7069636F4354467B666F72656E736963735F616E616C797369735F69735F616D617A696E675F63373564643038657D`

### Step 3: Decode Hex ke Teks

String hex tersebut dikonversi kembali ke teks:

```python
import binascii
hex_str = '7069636F4354467B666F72656E736963735F616E616C797369735F69735F616D617A696E675F63373564643038657D'
flag = binascii.unhexlify(hex_str).decode()
print(flag)
# Output: picoCTF{forensics_analysis_is_amazing_c75dd08e}
```

---

## Hasil (Proof)

File gambar berhasil direkonstruksi dan flag ditemukan di dalam metadata visual (teks di bawah gambar).

**Flag:** `picoCTF{forensics_analysis_is_amazing_c75dd08e}`

---

## Kesimpulan & Mitigasi

- **Root Cause:** Data disembunyikan menggunakan encoding sederhana (Base64) di dalam file log, dan flag disembunyikan di dalam file gambar menggunakan encoding Hex.
- **Pelajaran:** Penting untuk memeriksa pola string (seperti Magic Bytes Base64) pada file log yang mencurigakan.
