# Optimasi

Aplikasi desktop kecil (Python + Tkinter) untuk menonaktifkan sementara Windows Defender Real-Time Protection saat Anda butuh laptop bekerja maksimal — untuk coding, gaming, rendering, editing video, atau tugas berat lainnya. Setelah waktu yang ditentukan, proteksi dinyalakan kembali secara otomatis. Tujuannya: mengurangi beban CPU/RAM dari proses pemindaian latar belakang Defender agar laptop lebih ringan dan optimal.

## Fitur

- Menonaktifkan dan mengaktifkan kembali Real-Time Protection Defender
- Timer otomatis (default 60 menit) yang menyalakan kembali proteksi
- Status proteksi saat ini ditampilkan di antarmuka
- Otomatis meminta hak Administrator (UAC) saat dijalankan

## Cara Kerja

1. Aplikasi memanggil PowerShell:
   - Mematikan: `Set-MpPreference -DisableRealtimeMonitoring $true`
   - Menyalakan: `Set-MpPreference -DisableRealtimeMonitoring $false`
2. Status dibaca dari `Get-MpComputerStatus`
3. Saat proteksi dimatikan, countdown berjalan; ketika habis, proteksi dinyalakan lagi otomatis.

## Cara Penggunaan

### Prasyarat
- Windows 10/11
- Python 3.x
- Hak Administrator
- Library: `pip install pystray pillow`

### Menjalankan
```bash
python optm.py
```
Aplikasi akan meminta izin Administrator (UAC) secara otomatis.

### Langkah
1. Klik **Matikan Proteksi** — Real-Time Protection Defender dimatikan, countdown mulai.
2. Coding, gaming, atau kerja berat dengan bebas. Proteksi akan menyala kembali otomatis setelah waktu yang ditentukan.
3. Atau klik **Nyalakan Proteksi** kapan saja untuk mengaktifkannya manual.
4. Klik **Refresh** untuk memperbarui status proteksi.

## Catatan & Peringatan

- **Tamper Protection** dapat memblokir perubahan. Jika gagal, nonaktifkan dulu di:
  Windows Security → Virus & threat protection → Manage settings → Tamper Protection → Off.
- Selama proteksi nonaktif, laptop **tidak terlindungi** — jangan mengunduh file dari sumber tidak tepercaya atau browsing situs berisiko.
- Beberapa edisi Windows 11 Home tidak mengizinkan penonaktifan via PowerShell; gunakan juga exclusion folder sebagai alternatif.

## Menambahkan Exclusion Folder (Alternatif Lebih Aman)
Untuk hanya mengecualikan folder proyek tanpa mematikan seluruh proteksi:
```powershell
Set-MpPreference -ExclusionPath "C:\path\ke\proyek"
```

## Build Menjadi EXE

Gunakan PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --uac-admin --name optm --version-file version_info.txt optm.py
```

- `--onefile` : satu file exe
- `--windowed` : tanpa console
- `--uac-admin` : minta izin Administrator saat double-click
- `--version-file` : menyematkan info versi/credit ke exe

Hasilnya di folder `dist/optm.exe`.

## Lisensi
Untuk penggunaan pribadi dan edukasi.
© 2026 Blackswat
