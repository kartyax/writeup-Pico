# picoCTF: Forensics - DISKO 1

**Kategori:** Forensics  
**Tingkat Kesulitan:** Easy

---

## Deskripsi Tantangan

Tantangan ini meminta kita untuk mencari flag yang tersembunyi di dalam sebuah file *disk image*.

> _"Can you find the flag in this disk image? Download the disk image here."_

---

## Analisis & Metodologi

### Observasi Awal

Kita diberikan sebuah file kompresi bernama `disko-1.dd.gz`. Langkah pertama adalah mengekstrak file tersebut untuk mendapatkan file *disk image* mentah (`.dd`).

```bash
$ gunzip disko-1.dd.gz
$ ls -lh disko-1.dd
-rw-rw-r-- 1 k-artya k-artya 50M Mar 14 23:13 disko-1.dd
```

File berukuran 50MB, yang merupakan ukuran standar untuk *disk image* kecil.

### Temuan Kunci

Berdasarkan *hint* dari tantangan: *"Maybe Strings could help? If only there was a way to do that?"*, kita diarahkan untuk mencari teks yang bisa dibaca manusia di dalam file biner tersebut.

### Strategi Solve

Karena ini adalah tantangan Forensics tingkat *Easy*, kemungkinan besar flag disimpan dalam bentuk teks polos (plaintext) di dalam disk image. Kita akan menggunakan utility `strings` untuk mengekstrak semua string dan melakukan `grep` dengan pattern `picoCTF{`.

---

## Eksploitasi (Proof of Concept)

### Step 1: Ekstraksi String & Pencarian Flag

Kita menjalankan perintah `strings` pada file *disk image* dan memfilternya dengan kata kunci flag.

```bash
$ strings disko-1.dd | grep "picoCTF{"
picoCTF{1t5_ju5t_4_5tr1n9_e3408eef}
```

---

## Hasil

Flag ditemukan secara langsung:
`picoCTF{1t5_ju5t_4_5tr1n9_e3408eef}`

---

## Kesimpulan & Mitigasi

Tantangan ini menunjukkan bahwa data sensitif (seperti flag) yang disimpan tanpa enkripsi atau proteksi tambahan pada sebuah media penyimpanan (*disk*) sangat mudah untuk ditemukan hanya dengan menggunakan alat dasar seperti `strings`. Untuk pengamanan, data sensitif harus selalu dienkripsi sebelum disimpan ke media fisik.
