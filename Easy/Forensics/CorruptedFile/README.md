# PicoCTF: Forensics - Corrupted file

**Kategori:** Forensics
**Tingkat Kesulitan:** Easy

---

## Deskripsi Tantangan

File ini terlihat rusak... atau benarkah? Mungkin beberapa byte bisa membuat perbedaan besar. Bisakah kamu mencari tahu bagaimana cara menghidupkannya kembali?

> **Hints:** Coba periksa header filenya.

---

## Analisis & Metodologi

### Observasi Awal

File yang diberikan bernama `file`. Saat diperiksa menggunakan `hexdump`, header-nya terlihat tidak standar untuk format file umum, namun ada string `JFIF` yang merupakan ciri khas file **JPEG**.

```bash
$ head -c 32 file | hexdump -C
00000000  5c 78 ff e0 00 10 4a 46  49 46 00 01 01 00 00 01  |\x....JFIF......|
```

Header standar JPEG seharusnya dimulai dengan `FF D8 FF E0` (untuk JFIF). Di file ini, dua byte pertama adalah `5C 78` (atau `\x` dalam ASCII), yang menandakan header-nya korup.

### Strategi Solve

1. Memperbaiki header file dengan mengganti dua byte pertama menjadi `FF D8`.
2. Menyimpan file hasil perbaikan sebagai `.jpg`.
3. Membuka gambar untuk melihat flag.

---

## Eksploitasi (Proof of Concept)

### Step 1: Fix Header Menggunakan Python

Kita bisa menggunakan script python sederhana untuk membaca file, mengganti header-nya, dan menyimpannya kembali.

```python
# Membaca data dari file yang korup
with open('file', 'rb') as f:
    data = f.read()

# Header JPEG standar (JFIF) dimulai dengan FF D8
# Kita ganti 2 byte pertama dan biarkan sisanya
fixed_data = b'\xff\xd8' + data[2:]

# Simpan sebagai file gambar yang valid
with open('recovered.jpg', 'wb') as f:
    f.write(fixed_data)
```

---

## Hasil (Proof)

Setelah file diperbaiki menjadi `recovered.jpg`, gambar dapat dibuka dan menampilkan flag di dalamnya.

![recovered.jpg](file:///home/k-artya/Destop/CTF/PicoCtf/Download/recovered.jpg)

**Flag:** `picoCTF{r3st0r1ng_th3_by73s_939a65f5}`

---

## Kesimpulan & Mitigasi

- **Root Cause:** Header file (Magic Bytes) sengaja diubah/dirusak sehingga sistem operasi tidak mengenali format filenya.
- **Pelajaran:** Selalu periksa signature file (Magic Bytes) menggunakan `hexdump` atau `xxd` jika sebuah file tidak bisa dibuka, terutama jika ada petunjuk string (seperti `JFIF`, `PNG`, `PDF`) di dalam metadatanya.
