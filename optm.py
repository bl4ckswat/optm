import ctypes
import os
import subprocess
import sys
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import pystray
from PIL import Image, ImageDraw

PS = "powershell"
DEF_TIMER = 60
VERSION = "1.0.0"
CREDIT = "Blackswat"

BG = "#000000"
PANEL = "#111111"
FG = "#f2f2f2"
MUTED = "#9a9a9a"
YELLOW = "#f5c518"
BLYELLOW = "#ffd700"
GREEN = "#2e7d32"
RED = "#c62828"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_ps(cmd):
    try:
        r = subprocess.run(
            [PS, "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return (r.returncode == 0, (r.stdout + r.stderr).strip())
    except Exception as e:
        return False, str(e)


def get_status():
    ok, out = run_ps("(Get-MpComputerStatus).RealTimeProtectionEnabled")
    if not ok:
        return None
    return out.strip().splitlines()[-1].strip().lower() == "true"


def set_realtime(enable):
    val = "$false" if enable else "$true"
    return run_ps(f"Set-MpPreference -DisableRealtimeMonitoring {val}")


def make_icon(color):
    img = Image.new("RGB", (64, 64), BG)
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, 56, 56), fill=color)
    d.text((22, 18), "O", fill="black")
    return img


def separator(parent):
    tk.Frame(parent, bg=YELLOW, height=1).pack(fill="x", padx=20, pady=6)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Optimasi v{VERSION}")
        self.geometry("440x560")
        self.configure(bg=BG)
        self.resizable(False, False)

        tk.Label(self, text="OPTIMASI", font=("Segoe UI", 24, "bold"), bg=BG, fg=YELLOW).pack(pady=(12, 0))
        tk.Label(self, text="Defender Toggle — mode performa", font=("Segoe UI", 9), bg=BG, fg=MUTED).pack()
        separator(self)

        tk.Label(self, text="Durasi proteksi nonaktif (menit):", font=("Segoe UI", 10), bg=BG, fg=FG).pack()
        self.timer_var = tk.IntVar(value=DEF_TIMER)
        ttk.Spinbox(self, from_=1, to=600, textvariable=self.timer_var, width=8).pack(pady=4)

        self.countdown_var = tk.StringVar(value="Proteksi aktif")
        tk.Label(self, textvariable=self.countdown_var, font=("Segoe UI", 30, "bold"), bg=BG, fg=YELLOW).pack(pady=6)
        separator(self)

        btns = tk.Frame(self, bg=BG)
        btns.pack(pady=2)
        tk.Button(btns, text="Matikan Proteksi", bg=RED, fg="white", font=("Segoe UI", 11, "bold"),
                  width=16, relief="flat", bd=0, command=self.disable).grid(row=0, column=0, padx=6, pady=2)
        tk.Button(btns, text="Nyalakan Proteksi", bg=GREEN, fg="white", font=("Segoe UI", 11, "bold"),
                  width=16, relief="flat", bd=0, command=self.enable).grid(row=0, column=1, padx=6, pady=2)

        tk.Button(self, text="Minimize ke System Tray", bg=PANEL, fg=FG, font=("Segoe UI", 9),
                  relief="flat", bd=0, command=self.to_tray).pack(pady=4)
        tk.Button(self, text="Buka Pengaturan Tamper Protection", bg=PANEL, fg=YELLOW, font=("Segoe UI", 9),
                  relief="flat", bd=0, command=self.open_tamper).pack(pady=4)
        separator(self)

        tk.Label(self, text="Log Aktivitas", font=("Segoe UI", 10, "bold"), bg=BG, fg=YELLOW).pack()
        logwrap = tk.Frame(self, bg=YELLOW, padx=1, pady=1)
        logwrap.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        self.log = tk.Text(logwrap, height=10, bg=PANEL, fg=FG, font=("Consolas", 9), relief="flat", bd=0)
        self.log.pack(fill="both", expand=True)

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=20, pady=(0, 10))
        tk.Button(bottom, text="About", bg=PANEL, fg=FG, font=("Segoe UI", 9),
                  relief="flat", bd=0, command=self.about).pack(side="right")
        tk.Label(bottom, text=f"v{VERSION}", font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(side="left")

        self._timer_id = None
        self._seconds_left = 0
        self.tray = None
        self.log_msg("Aplikasi siap.")

    def log_msg(self, msg):
        self.log.insert("end", f"[{datetime.now():%H:%M:%S}] {msg}\n")
        self.log.see("end")

    def open_tamper(self):
        try:
            subprocess.Popen(
                [os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Windows Defender", "SecurityHealthUI.exe")],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception:
            try:
                os.startfile("ms-settings:windowsdefender")
            except Exception as e:
                messagebox.showerror("Gagal", f"Tidak bisa membuka Windows Security.\n{e}")
        self.log_msg("Membuka Windows Security — matikan Tamper Protection manual di Virus & threat protection > Manage settings.")

    def about(self):
        messagebox.showinfo(
            "About Optimasi",
            f"Optimasi v{VERSION}\n© 2026 {CREDIT}\n\n"
            "Menonaktifkan sementara proteksi Windows Defender "
            "untuk performa maksimal, lalu menyalakannya kembali otomatis.",
        )

    def disable(self):
        ok, msg = set_realtime(False)
        if ok:
            import time as _t
            _t.sleep(1)
            if get_status() is True:
                messagebox.showerror("Gagal", "Proteksi masih aktif — perubahan diblokir Windows.\nMatikan Tamper Protection terlebih dahulu (tombol di bawah), lalu coba lagi.")
                self.log_msg("Gagal mematikan proteksi: diblokir (Tamper Protection aktif?).")
                return
            mins = max(1, int(self.timer_var.get()))
            self._seconds_left = mins * 60
            self.log_msg(f"Proteksi dimatikan. Auto re-enable dalam {mins} menit.")
            self._tick()
        else:
            messagebox.showerror("Gagal", f"Tidak bisa menonaktifkan.\n{msg}\n\nJalankan sebagai Administrator dan periksa Tamper Protection.")

    def enable(self):
        ok, msg = set_realtime(True)
        if self._timer_id:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        self.countdown_var.set("Proteksi aktif")
        if ok:
            self.log_msg("Proteksi dinyalakan kembali.")
        else:
            messagebox.showerror("Gagal", msg)

    def _tick(self):
        if self._seconds_left <= 0:
            self.countdown_var.set("Proteksi aktif")
            self.enable()
            self.log_msg("Proteksi dinyalakan otomatis.")
            return
        m, s = divmod(self._seconds_left, 60)
        self.countdown_var.set(f"{m:02d}:{s:02d}")
        self._seconds_left -= 1
        self._timer_id = self.after(1000, self._tick)

    def to_tray(self):
        self.withdraw()
        if self.tray is None:
            menu = pystray.Menu(
                pystray.MenuItem("Tampilkan", lambda icon, item: self.after(0, self._restore)),
                pystray.MenuItem("Nyalakan Proteksi", lambda icon, item: self.after(0, self.enable)),
                pystray.MenuItem("Keluar", lambda icon, item: self.after(0, self._quit)),
            )
            icon = pystray.Icon("optm", make_icon(YELLOW if get_status() else RED), "Optimasi", menu)
            self.tray = icon
            threading.Thread(target=icon.run, daemon=True).start()
        self.log_msg("Dioptimalkan ke system tray.")

    def _restore(self):
        super().deiconify()

    def _quit(self):
        if self.tray:
            self.tray.stop()
        self.destroy()


def ensure_admin():
    if is_admin():
        return
    try:
        params = f'"{os.path.abspath(sys.argv[0])}"'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    ensure_admin()
    App().mainloop()
