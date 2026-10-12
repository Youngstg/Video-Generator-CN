# Sebentar, Paham. — Skill v2.1.1

Paket skill portabel untuk Codex dan Antigravity, diperbarui 11 Oktober 2026.

## Perubahan v2.1.1 — hemat kuota TTS

Kuota gratis TTS dibatasi per **permintaan** (per menit dan per hari), bukan panjang teks. Sebelumnya satu episode memakai tujuh permintaan (satu per scene). Sekarang:

- `voice.py gemini`: **satu permintaan per episode** untuk seluruh narasi (gaya per bagian lewat `speech_metadata`), dengan `--dry-run` gratis, tanpa pengulangan otomatis, dan buku catatan lokal (`tts-ledger.json`) yang menolak melewati batas harian.
- `voice.py align-full` dan `voice.py split`: menyelaraskan satu take lalu memotongnya menjadi tujuh klip beserta timestamp per scene. Bisa dipakai untuk penyedia mana pun (ElevenLabs, web), bukan hanya Gemini.
- `voice.py quota`: pemakaian hari ini dan waktu reset berikutnya (tengah malam Pasifik, ditampilkan dalam WIB).
- Aturan fallback per episode utuh, dan catatan bahwa grafik "Rate limits by model" di AI Studio menampilkan **puncak 28 hari**, bukan sisa jatah.
- Dependensi opsional: `scripts/requirements-tts.txt`.

## Perubahan v2.1.0 — lebih menarik, teks tidak lagi keluar kotak

**Teks tidak keluar kotak (perbaikan akar masalah)**

- `fit()` dulu mengecilkan teks di bawah 48 px lalu `txt()` memaksanya kembali ke 48 px, sehingga teks melebihi kotak. Sekarang `fit()` berhenti di 48 px dan memunculkan error yang jelas.
- `label()` dulu tidak mengecek posisi terhadap tepi layar. Sekarang label dipecah maksimal dua baris dan ditolak bila terlalu dekat tepi.
- `studio.py check` dulu mengukur header dengan font berat 400, padahal render memakai 700, sehingga lebar dilaporkan terlalu kecil. Sekarang ukurannya sama dengan render.
- Helper baru `chip()` (kotak dibuat dari teks) dan `box_text()` (teks dimuat ke kotak tetap) menggantikan pola "gambar kotak lalu letakkan teks manual".
- Perintah baru `studio.py lint` merekam semua teks dan kotak, lalu menggagalkan: teks melewati kotak, keluar kanvas, menimpa teks lain, atau masuk zona subtitle. Berjalan otomatis di `storyboard` dan `render` (termasuk setiap frame subtitle), dan wajib bersih sebelum `deliver`. Frame yang gagal disimpan dengan kotak merah di `qa/`.

**Lebih eye-catching (tetap gaya pastel editorial)**

- Subtitle karaoke: kata yang sedang diucapkan disorot.
- Backdrop berlapis (spot, rings, blobs, grid, sparkle) dengan pusat mengikuti objek.
- Highlight marker yang menggambar dirinya di bawah baris kedua header.
- Objek muncul dengan efek pop, mengambang halus, dan punya bayangan lembut; panah menggambar dirinya lalu dialiri titik.
- Mode `mood: "dark"` untuk satu scene fokus (scene mekanisme).
- Transisi bervariasi (`push`, `zoom`, `dissolve`) yang memudar lewat warna latar, sehingga dua header tidak pernah bertumpuk.
- Resep komposisi baru: `hero_closeup`, `split_compare`, `flow_three`; panduan hook, satu fokus per scene, dan variasi komposisi di `references/design.md`.

Proyek lama tidak berubah otomatis. Salin `engine.py`, `artwork.py`, dan `illustrations.py` ke salinan proyek, lalu jalankan `lint`.

## Perubahan versi ini

- Ilustrasi objek yang dapat dikenali: Bumi, satelit, mouse, dan objek sesuai topik.
- Animasi menjelaskan proses; kartu teks generik tidak menjadi visual utama.
- Satu fun fact dengan latar belakang, bahasa Indonesia santai, dan istilah teknis Inggris.
- Gaya pastel, subtitle sinkron, tanpa progress bar, serta arahan narasi ekspresif.
- Hasil produksi hanya MP4 vertikal 1080×1920, 30 fps, dan WAV narasi bersih.

## Pakai di proyek

1. Ekstrak ZIP ini.
2. Salin folder `.agents` ke root proyek/repository kamu. Folder ini harus tetap ikut saat mengunggah ke GitHub.
3. Minta agent membaca `.agents/skills/sebentar-paham-video/SKILL.md` dan mengikuti petunjuknya.
4. Untuk pemasangan global, ikuti `references/portability.md` di dalam skill.

Jika sebelumnya sudah memasang versi lama, ganti hanya folder `sebentar-paham-video` setelah menyimpan perubahan pribadimu. Jangan menghapus proyek video atau aset produksi yang sudah dibuat.

## Menjalankan engine

Diperlukan Python 3.10+, FFmpeg/FFprobe, serta dependency dalam `scripts/requirements.txt`.

```bash
python -m pip install -r .agents/skills/sebentar-paham-video/scripts/requirements.txt
python .agents/skills/sebentar-paham-video/scripts/studio.py doctor
```

Skill berisi instruksi, engine, ilustrasi, contoh, dan font beserta lisensinya. Suara ekspresif memerlukan provider TTS yang tersedia tanpa biaya tambahan atau audio yang disediakan. Paket ini tidak menyertakan API key, akses berbayar, atau video final.
