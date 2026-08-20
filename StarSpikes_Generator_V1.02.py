# SPDX-License-Identifier: GPL-3.0-or-later
#
# Star Spikes Generator for Siril V1.0.2
# Jerome Desvignes (JeX), 2026
# jex3dvf@gmail.com
#
# Add StarSpikes on your images in SIRIL
#
# Version 1.0.2 (Gestion entiers & floats arrondis a 2 decimales)
#                Suport Unicode etendu espace et acccents
#                Dark Mode Title Bar Windows 10/11
#

import os
import sys
import ctypes
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk


def set_dark_title_bar(window):
    """Active la barre de titre sombre sous Windows 10 et 11."""
    if sys.platform != "win32":
        return
    try:
        window.update()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        
        # 20 pour Win 11 et versions recentes de Win 10
        # 19 pour les builds Windows 10 anterieures
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        value = ctypes.c_int(2)
        res = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 
            DWMWA_USE_IMMERSIVE_DARK_MODE, 
            ctypes.byref(value), 
            ctypes.sizeof(value)
        )
        if res != 0:
            DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, 
                ctypes.byref(value), 
                ctypes.sizeof(value)
            )
    except Exception:
        pass


class AigrettesGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Star Spikes Generator V1.0.2")
        self.root.geometry("1280x920")

        # Zoom
        self.zoom_level = 1.0
        self.zoom_factor = 1.1

        # Images
        self.img_orig = None
        self.img_processed = None
        self.photo_preview = None

        self._setup_siril_theme()
        self._create_widgets()
        
        # Application de la barre de titre sombre
        set_dark_title_bar(self.root)

    # ------------------------------------------------------------------
    # THEME
    # ------------------------------------------------------------------
    def _setup_siril_theme(self):
        """Palette reprenant le dark theme de SIRIL."""
        bg_color = "#2b2b2b"
        panel_bg = "#272727"
        canvas_bg = "#1e1e1e"
        entry_bg = "#3c3c3c"
        entry_fg = "#e0e0e0"
        slider_bg = "#3c3c3c"
        label_fg = "#dcdcdc"
        button_bg = "#3c3c3c"
        button_fg = "#e0e0e0"
        active_color = "#4cc2ff"   # Bleu accent Siril
        frame_bg = "#2b2b2b"

        self.bg_color = bg_color
        self.panel_bg = panel_bg
        self.canvas_bg = canvas_bg
        self.active_color = active_color

        self.root.configure(bg=bg_color)

        style = ttk.Style(self.root)
        style.theme_use('clam')

        style.configure('.', background=panel_bg, foreground=label_fg,
                        fieldbackground=entry_bg, troughcolor=slider_bg,
                        bordercolor=frame_bg, lightcolor=frame_bg,
                        darkcolor=frame_bg, focuscolor=active_color)

        style.configure('TFrame', background=panel_bg)

        style.configure('TLabelFrame', background=panel_bg, foreground=label_fg,
                        bordercolor=frame_bg, lightcolor=frame_bg, darkcolor=frame_bg)
        style.configure('TLabelFrame.Label', background=panel_bg, foreground=active_color,
                        font=('Segoe UI', 9, 'bold'))

        style.configure('TLabel', background=panel_bg, foreground=label_fg,
                        font=('Segoe UI', 9))

        style.configure('TEntry', fieldbackground=entry_bg, foreground=entry_fg,
                        insertcolor=entry_fg, bordercolor=frame_bg)

        style.configure('TButton', background=button_bg, foreground=button_fg,
                        bordercolor=frame_bg, focusthickness=1, focuscolor=active_color)
        style.map('TButton',
                  background=[('active', active_color), ('pressed', active_color)],
                  foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])

        style.configure('TRadiobutton', background=panel_bg, foreground=label_fg)
        style.map('TRadiobutton',
                  background=[('active', panel_bg)],
                  foreground=[('active', active_color)],
                  indicatorcolor=[('selected', active_color), ('!selected', entry_bg)])

        style.configure('TScale', background=panel_bg, troughcolor=slider_bg)
        style.configure('Horizontal.TScale',
                        background=panel_bg,
                        troughcolor=slider_bg,
                        bordercolor=panel_bg,
                        lightcolor=active_color,
                        darkcolor=active_color)
        style.map('Horizontal.TScale',
                  background=[('active', panel_bg)],
                  lightcolor=[('active', active_color), ('!active', active_color)],
                  darkcolor=[('active', active_color), ('!active', active_color)])

        style.configure('TSeparator', background=frame_bg)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _create_widgets(self):
        self.root.configure(bg=self.bg_color)

        # ---------- Panneau gauche ----------
        panel = ttk.LabelFrame(self.root, text=" Spikes Parameters ", padding=10)
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        btn_load = ttk.Button(panel, text="1. Load Image", command=self.load_image)
        btn_load.pack(fill=tk.X, pady=(0, 8))

        # --- Detection des etoiles ---
        ttk.Label(panel, text="── Stars Detection ──",
                  foreground=self.active_color).pack(pady=(4, 4))
        self.slider_threshold = self._add_slider(panel, "Bright Star threshold (0-255) :",
                                                 0, 255, 220, is_integer=True)
        self.slider_max_stars = self._add_slider(panel, "Max Stars (0 = unlimited) :",
                                                 0, 500, 12, is_integer=True)
        self.slider_min_size = self._add_slider(panel, "Star Min Size (px²) :",
                                                1, 100, 75, is_integer=True)

        # --- Modulation par la Luminosite / etoile ---
        ttk.Label(panel, text="── Auto Brightness Scaling ──",
                  foreground=self.active_color).pack(pady=(10, 4))
        self.slider_lum_scale = self._add_slider(panel, "Auto-Scale Luminosity (%) :",
                                                 0, 100, 12.0, is_integer=False)
        self.slider_compression = self._add_slider(panel, "Dynamic Range Compression :",
                                                   0.1, 2.0, 1.0, is_integer=False)

        # --- Apparence des aigrettes ---
        ttk.Label(panel, text="── Spikes Look ──",
                  foreground=self.active_color).pack(pady=(10, 4))
        self.slider_length = self._add_slider(panel, "Base Length (% Image Size) :",
                                              1, 50, 4.0, is_integer=False)
        self.slider_size_factor = self._add_slider(panel, "Star Size Factor → Length :",
                                                   0, 10, 2.5, is_integer=False)
        self.slider_thickness = self._add_slider(panel, "Base Thickness (px) :",
                                                 1, 20, 1.0, is_integer=False)
        self.slider_angle = self._add_slider(panel, "Rotation Angle (degres) :",
                                             0, 360, 0.0, is_integer=False)

        ttk.Label(panel, text="Branches Number:").pack(anchor=tk.W, pady=(6, 0))
        self.branch_mode = tk.IntVar(value=4)
        frame_radio = ttk.Frame(panel)
        frame_radio.pack(fill=tk.X, pady=(2, 6))
        ttk.Radiobutton(frame_radio, text="4 branches (Newton/RC)",
                        variable=self.branch_mode, value=4).pack(anchor=tk.W)
        ttk.Radiobutton(frame_radio, text="6 branches (JWST/Aperture)",
                        variable=self.branch_mode, value=6).pack(anchor=tk.W)

        self.slider_blur = self._add_slider(panel, "Softening / Blur (px) :",
                                            1, 51, 5, is_integer=True)
        self.slider_intensity = self._add_slider(panel, "Global Opacity (%) :",
                                                 0, 100, 100.0, is_integer=False)

        # --- Effets ---
        ttk.Label(panel, text="── Effets ──",
                  foreground=self.active_color).pack(pady=(10, 4))
        self.slider_chroma = self._add_slider(panel, "Chromatic Aberration (px) :",
                                              0, 10, 8, is_integer=True)

        # --- Boutons d'action ---
        ttk.Button(panel, text="🔍 PREVIEW ",
                   command=self.generate_preview).pack(fill=tk.X, pady=(12, 4))
        ttk.Button(panel, text="💾 Save Image",
                   command=self.save_image).pack(fill=tk.X, pady=4)

        # ---------- Zone canvas ----------
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_frame, bg=self.canvas_bg, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        self.canvas.bind("<ButtonPress-3>", self._on_pan_start)
        self.canvas.bind("<B3-Motion>", self._on_pan_move)

    def _add_slider(self, parent, label_text, min_val, max_val, default_val, is_integer=False):
        """Cree un label + slider + entry synchronises (entier ou float à 2 decimales)."""
        ttk.Label(parent, text=label_text).pack(anchor=tk.W, pady=(4, 0))
        row = ttk.Frame(parent)
        row.pack(fill=tk.X)

        var = tk.DoubleVar(value=float(default_val))
        entry_var = tk.StringVar()

        def format_val(val):
            if is_integer:
                return f"{int(round(float(val)))}"
            else:
                return f"{float(val):.2f}"

        entry_var.set(format_val(default_val))

        entry = ttk.Entry(row, width=6, textvariable=entry_var)
        entry.pack(side=tk.RIGHT, padx=(5, 0))

        def on_slider_move(val):
            v = float(val)
            if is_integer:
                v = int(round(v))
                var.set(v)
            else:
                v = round(v, 2)
                var.set(v)
            entry_var.set(format_val(v))

        slider = ttk.Scale(row, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                           variable=var, command=on_slider_move)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def on_entry_change(event=None):
            try:
                raw_val = float(entry_var.get().replace(',', '.'))
                val = max(min_val, min(max_val, raw_val))
                if is_integer:
                    val = int(round(val))
                else:
                    val = round(val, 2)
                var.set(val)
                entry_var.set(format_val(val))
            except ValueError:
                entry_var.set(format_val(var.get()))

        entry.bind("<Return>", on_entry_change)
        entry.bind("<FocusOut>", on_entry_change)

        return var

    # ------------------------------------------------------------------
    # ZOOM / PAN
    # ------------------------------------------------------------------
    def _on_mousewheel(self, event):
        if self.img_processed is None:
            return
        if event.num == 5 or event.delta < 0:
            self.zoom_level /= self.zoom_factor
        else:
            self.zoom_level *= self.zoom_factor
        self.zoom_level = max(0.05, min(self.zoom_level, 20.0))
        self.display_image(self.img_processed)

    def _on_pan_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    # ------------------------------------------------------------------
    # LOGIQUE IMAGE
    # ------------------------------------------------------------------
    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.tif *.tiff"),
                       ("Tous fichiers", "*.*")]
        )
        if not path:
            return

        try:
            stream = np.fromfile(path, dtype=np.uint8)
            img = cv2.imdecode(stream, cv2.IMREAD_UNCHANGED)
        except Exception:
            img = None

        if img is None:
            messagebox.showerror("Erreur", "Impossible de charger cette image.\nVerifiez le format du fichier.")
            return

        if img.dtype != np.uint8:
            img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        self.img_orig = img
        self.img_processed = img.copy()
        self.zoom_level = 1.0
        self.display_image(self.img_processed)

    def detect_stars(self):
        """Detecte les etoiles brillantes et retourne liste de (x, y, taille_px, luminosite, flux)."""
        gray = cv2.cvtColor(self.img_orig, cv2.COLOR_BGR2GRAY)

        threshold = int(self.slider_threshold.get())
        min_size = int(self.slider_min_size.get())
        max_stars = int(self.slider_max_stars.get())

        _, binary = cv2.threshold(gray, threshold, 254, cv2.THRESH_BINARY)
        binary = np.clip(binary, 0, 254).astype(np.uint8)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary, connectivity=8)

        stars = []
        for i in range(1, num_labels):  # 0 = fond
            area = stats[i, cv2.CC_STAT_AREA]
            if area < min_size:
                continue
            cx, cy = centroids[i]
            size_px = 2.0 * np.sqrt(area / np.pi)
            star_mask = (labels == i)
            brightness = float(gray[star_mask].mean())
            flux = float(area * (brightness / 255.0))
            stars.append((cx, cy, size_px, brightness, flux))

        stars.sort(key=lambda s: s[4], reverse=True)
        if max_stars > 0:
            stars = stars[:max_stars]

        return stars

    def _draw_tapered_spike(self, mask, cx, cy, angle_rad, length, base_thickness,
                            base_intensity, chroma_amount, n_segments=24):
        """Dessine une branche d'aigrette effilee avec chromatisme."""
        dx_dir = np.cos(angle_rad)
        dy_dir = np.sin(angle_rad)

        prev_x, prev_y = cx, cy

        for seg in range(1, n_segments + 1):
            t1 = seg / n_segments

            x1 = cx + dx_dir * length * t1
            y1 = cy + dy_dir * length * t1

            taper = (1.0 - t1) ** 1.5
            thickness = max(1, int(round(base_thickness * taper)))
            intensity = base_intensity * (0.15 + 0.85 * taper)

            k = chroma_amount / 10.0

            if k <= 0.0:
                r, g, b = 1.0, 1.0, 1.0
            else:
                warm = np.clip(1.0 - (t1 * 2.2), 0.0, 1.0)
                cold = np.clip((t1 - 0.35) / 0.65, 0.0, 1.0)

                r_base, g_base, b_base = 1.0, 1.0, 1.0
                r_warm, g_warm, b_warm = 1.0, 0.55, 0.25
                r_cold, g_cold, b_cold = 0.45, 0.35, 1.0

                r = r_base * (1 - k) + (r_warm * warm + r_cold * cold) * k
                g = g_base * (1 - k) + (g_warm * warm + g_cold * cold) * k
                b = b_base * (1 - k) + (b_warm * warm + b_cold * cold) * k

                m = max(r, g, b, 1.0)
                r, g, b = r / m, g / m, b / m

            color = (b * intensity, g * intensity, r * intensity)

            cv2.line(mask,
                     (int(round(prev_x)), int(round(prev_y))),
                     (int(round(x1)), int(round(y1))),
                     color, thickness, cv2.LINE_AA)

            prev_x, prev_y = x1, y1

    def generate_preview(self):
        if self.img_orig is None:
            messagebox.showwarning("Attention", "Veuillez d'abord charger une image.")
            return

        h, w = self.img_orig.shape[:2]
        mask = np.zeros((h, w, 3), dtype=np.float32)

        stars = self.detect_stars()
        if not stars:
            messagebox.showinfo("Info", "Aucune etoile detectee avec ces paramètres.")
            return

        length_pct = self.slider_length.get() / 100.0
        base_length = length_pct * max(w, h)
        size_factor = self.slider_size_factor.get()
        base_thickness = max(1.0, self.slider_thickness.get())
        angle_offset_deg = self.slider_angle.get()
        n_branches = self.branch_mode.get()
        chroma_offset = int(self.slider_chroma.get())

        auto_scale_ratio = self.slider_lum_scale.get() / 100.0
        gamma = max(0.05, self.slider_compression.get())

        max_flux = max(s[4] for s in stars) if stars else 1.0
        if max_flux <= 0:
            max_flux = 1.0

        if n_branches == 4:
            branch_angles_deg = [0, 90, 180, 270]
        else:
            branch_angles_deg = [0, 60, 120, 180, 240, 300]

        for (cx, cy, size_px, brightness, flux) in stars:
            relative_flux = np.clip(flux / max_flux, 0.001, 1.0)
            compressed_factor = float(relative_flux ** gamma)

            final_factor = (1.0 - auto_scale_ratio) * 1.0 + auto_scale_ratio * compressed_factor
            final_factor = max(0.1, final_factor)

            star_spike_length = (base_length + (size_px * size_factor)) * final_factor
            star_thickness = max(1, int(round(base_thickness * (final_factor ** 0.6))))
            star_intensity = 255.0 * np.clip(0.35 + 0.65 * final_factor, 0.2, 1.0)

            for ang_deg in branch_angles_deg:
                angle_rad = np.deg2rad(ang_deg + angle_offset_deg)
                self._draw_tapered_spike(mask, cx, cy, angle_rad, star_spike_length,
                                         star_thickness, star_intensity, chroma_offset)

        # Flou gaussien pour adoucir
        blur_size = int(self.slider_blur.get())
        if blur_size % 2 == 0:
            blur_size += 1
        if blur_size > 1:
            mask = cv2.GaussianBlur(mask, (blur_size, blur_size), 0)

        # Fusion avec l'image d'origine
        alpha = self.slider_intensity.get() / 100.0
        img_float = self.img_orig.astype(np.float32)
        result = cv2.addWeighted(img_float, 1.0, mask, alpha, 0)
        self.img_processed = np.clip(result, 0, 255).astype(np.uint8)

        self.display_image(self.img_processed)

    def display_image(self, img_bgr):
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        h, w = img_rgb.shape[:2]

        new_w = max(1, int(w * self.zoom_level))
        new_h = max(1, int(h * self.zoom_level))

        img_resized = cv2.resize(img_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        pil_img = Image.fromarray(img_resized)
        self.photo_preview = ImageTk.PhotoImage(pil_img)

        self.canvas.delete("all")
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            canvas_w, canvas_h = 800, 600

        x_pos = canvas_w // 2
        y_pos = canvas_h // 2

        self.canvas.create_image(x_pos, y_pos, image=self.photo_preview, anchor=tk.CENTER)

    def save_image(self):
        if self.img_processed is None:
            messagebox.showwarning("Attention", "Aucune image à enregistrer.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Fichier PNG", "*.png"), ("Fichier TIFF", "*.tif"), ("Fichier JPG", "*.jpg")]
        )
        if save_path:
            try:
                ext = os.path.splitext(save_path)[1]
                success, encoded_img = cv2.imencode(ext, self.img_processed)
                if success:
                    encoded_img.tofile(save_path)
                    messagebox.showinfo("Succès", f"Image enregistree sous :\n{save_path}")
                else:
                    messagebox.showerror("Erreur", "echec de l'encodage de l'image.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AigrettesGeneratorApp(root)
    root.mainloop()