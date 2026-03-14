# PicoCTF: Forensics - DISKO 3

**Kategori:** Forensics
**Tingkat Kesulitan:** Medium

---

## Deskripsi Tantangan

Tantangan ini memberikan sebuah disk image dan meminta kita untuk menemukan flag di dalamnya. Deskripsi menyebutkan bahwa pencarian flag kali ini tidak sesederhana biasanya.

> _"Can you find the flag in this disk image? This time, its not as plain as you think it is!"_

---

## Analisis & Metodologi

### Observasi Awal

File yang diberikan adalah `disko-3.dd.gz`. Setelah diekstrak, kita mendapatkan `disko-3.dd` berukuran 100MB.

```bash
$ file disko-3.dd
disko-3.dd: DOS/MBR boot sector, code offset 0x58+2, OEM-ID "mkfs.fat", Media descriptor 0xf8, sectors/track 32, heads 8, sectors 204800 (volumes > 32 MB), FAT (32 bit), sectors/FAT 1576, serial number 0x49838d0b, unlabeled
```

Hasil `file` menunjukkan bahwa ini adalah disk image dengan filesystem FAT32.

### Temuan Kunci

Menggunakan `fls` dari The Sleuth Kit untuk melihat struktur file secara rekursif:

```bash
$ fls -r disko-3.dd
...
+ r/r 522627:	daemon.log
+ r/r 522628:	flag.gz
+ r/r * 522629:	_ESSAGES
...
```

Ditemukan file mencurigakan bernama `flag.gz` pada inode `522628`. Selain itu, ada file `_ESSAGES` yang merupakan file terhapus (ditandai dengan `*`).

### Strategi Solve

Pendekatan yang digunakan:
1.  Mengekstrak file `flag.gz` dari disk image menggunakan `icat`.
2.  Mengekstrak konten dari `flag.gz` karena flag seringkali disimpan di dalam file yang dikompresi untuk menghindari deteksi `strings` sederhana.

---

## Eksploitasi (Proof of Concept)

### Step 1: Ekstraksi File dari Disk Image

Gunakan `icat` untuk mengambil konten dari inode `522628` (file `flag.gz`):

```bash
$ icat disko-3.dd 522628 > extracted_flag.gz
```

### Step 2: Dekompresi dan Pembacaan Flag

Gunakan `gunzip` untuk melihat isi dari file yang telah diekstrak:

```bash
$ gunzip -c extracted_flag.gz
Here is your flag
picoCTF{n3v3r_z1p_2_h1d3_7e0a17da}
```

---

## Hasil (Proof)

Output terminal saat flag ditemukan:

```text
$ gunzip -c flag.gz
Here is your flag
picoCTF{n3v3r_z1p_2_h1d3_7e0a17da}
```

**Flag:** `picoCTF{n3v3r_z1p_2_h1d3_7e0a17da}`

---

## Kesimpulan & Mitigasi

Tantangan ini mengajarkan dasar-dasar forensik disk:
- **Root Cause:** Flag tidak disimpan dalam bentuk plain text langsung di disk, melainkan di dalam file terpisah yang dikompresi.
- **Kenapa Berhasil:** Penggunaan tools forensik seperti `fls` dan `icat` memungkinkan kita melihat file yang tersembunyi atau bahkan yang sudah terhapus di dalam filesystem.
- **Mitigasi:** Untuk melindungi data sensitif di disk, gunakan enkripsi full-disk (seperti LUKS atau BitLocker) daripada hanya mengandalkan kompresi atau penghapusan file sederhana.
