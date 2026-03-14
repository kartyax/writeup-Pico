# PicoCTF: Forensics - DISKO 2

**Kategori:** Forensics
**Tingkat Kesulitan:** Medium

---

## Deskripsi Tantangan

Tantangan ini meminta kita untuk mencari flag di dalam sebuah disk image. Terdapat peringatan bahwa "langkah yang salah" bisa membuat segalanya hilang, dan petunjuk bahwa yang benar adalah Linux.

> _"Can you find the flag in this disk image? The right one is Linux! One wrong step and its all gone!"_

---

## Analisis & Metodologi

### Observasi Awal

File yang diberikan adalah `disko-2.dd.gz`. Setelah diekstrak, kita mendapatkan `disko-2.dd`.

```bash
$ mmls disko-2.dd
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0000053247   0000051200   Linux (0x83)
003:  000:001   0000053248   0000118783   0000065536   Win95 FAT32 (0x0b)
004:  -------   0000118784   0000204799   0000086016   Unallocated
```

Disk image ini memiliki dua partisi utama:
1.  Partisi Linux (Start: 2048, Length: 51200)
2.  Partisi Win95 FAT32 (Start: 53248)

### Temuan Kunci

Jika kita melakukan `strings` pada seluruh disk image, kita akan menemukan ribuan string flag palsu (red herrings) dengan format `picoCTF{4_P4Rt_1t_i5_...}`. Mengikuti petunjuk *"The right one is Linux"*, kita harus fokus pada partisi Linux.

### Strategi Solve

Pendekatan yang digunakan:
1.  Mengisolasi partisi Linux dari disk image menggunakan `dd`.
2.  Mencari string flag di dalam partisi yang sudah diisolasi. Karena petunjuk mengatakan "The right one is Linux", flag yang asli seharusnya berada di sana.

---

## Eksploitasi (Proof of Concept)

### Step 1: Isolasi Partisi Linux

Berdasarkan output `mmls`, partisi Linux dimulai pada sektor 2048 dengan panjang 51200 sektor. Kita gunakan `dd` untuk menyalin bagian tersebut ke file baru:

```bash
$ dd if=disko-2.dd bs=512 skip=2048 count=51200 of=linux_part.img
51200+0 records in
51200+0 records out
26214400 bytes (26 MB, 25 MiB) copied, 0.156 s, 168 MB/s
```

### Step 2: Menemukan Flag

Gunakan `strings` pada partisi yang telah diisolasi:

```bash
$ strings linux_part.img | grep "picoCTF"
picoCTF{4_P4Rt_1t_i5_a93c3ba0}
```

Berbeda dengan file utama yang berisi ribuan flag palsu, pada partisi Linux ini hanya ditemukan tepat satu string flag.

---

## Hasil (Proof)

Output aktual saat pencarian flag dilakukan pada partisi Linux:

```text
$ strings linux_part.img | grep "picoCTF"
picoCTF{4_P4Rt_1t_i5_a93c3ba0}
```

**Flag:** `picoCTF{4_P4Rt_1t_i5_a93c3ba0}`

---

## Kesimpulan & Mitigasi

Tantangan ini menekankan pentingnya analisis partisi dalam forensik disk:
- **Root Cause:** Penyerang/pembuat tantangan sengaja menanam banyak data palsu di luar area yang dituju untuk membingungkan analis.
- **Kenapa Berhasil:** Dengan membedah struktur MBR (Master Boot Record) dan mengisolasi partisi yang relevan, kita bisa mengabaikan "noise" (red herrings) yang ada di partisi lain.
- **Mitigasi:** Analis forensik harus selalu memverifikasi integritas dan konteks data. Dalam skenario nyata, teknik penyembunyian data seperti *Slack Space* atau partisi tersembunyi sering digunakan untuk menyembunyikan artefak.
