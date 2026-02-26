import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from PIL import Image

# Robust MoviePy Import
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        from moviepy import VideoFileClip
    except ImportError:
        VideoFileClip = None

import vtracer

class DesignerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Toolkit - P.S. Shreyash")
        self.root.geometry("500x350")
        
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill="both", expand=True)

        ttk.Label(self.main_frame, text="Asset Tool: Conversion & Extraction", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        
        self.file_path = tk.StringVar()
        file_frame = ttk.Frame(self.main_frame)
        file_frame.pack(fill="x", pady=5)
        ttk.Entry(file_frame, textvariable=self.file_path).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side="right")

        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=20)

        btn_grid = ttk.Frame(self.main_frame)
        btn_grid.pack(pady=10, fill="x")

        ttk.Button(btn_grid, text="To PNG", command=lambda: self.run_task(self.to_png)).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(btn_grid, text="To JPG", command=lambda: self.run_task(self.to_jpg)).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(btn_grid, text="Vectorize (SVG)", command=lambda: self.run_task(self.to_svg)).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(btn_grid, text="Extract Audio", command=lambda: self.run_task(self.to_mp3)).grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(btn_grid, text="Strip Metadata", command=lambda: self.run_task(self.strip_metadata)).grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(btn_grid, text="Extract Palette", command=lambda: self.run_task(self.get_palette)).grid(row=2, column=1, sticky="ew", padx=2, pady=2)

        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        self.progress = ttk.Progressbar(self.main_frame, mode="determinate")
        self.progress.pack(pady=20, fill="x")
        self.status = ttk.Label(self.main_frame, text="Ready", foreground="gray")
        self.status.pack()

    def browse_file(self):
        file = filedialog.askopenfilename()
        if file: self.file_path.set(file)

    def run_task(self, task_func):
        if not self.file_path.get():
            messagebox.showwarning("Warning", "Select a file first!")
            return
        self.progress.start()
        self.status.config(text="Processing...", foreground="blue")
        threading.Thread(target=task_func, daemon=True).start()

    def finish(self, msg, success=True):
        self.progress.stop()
        if success:
            self.status.config(text="Done!", foreground="green")
            messagebox.showinfo("Success", msg)
        else:
            self.status.config(text="Error", foreground="red")
            messagebox.showerror("Error", msg)

    # --- UPDATED LOGIC FUNCTIONS ---

    def to_png(self):
        try:
            path = self.file_path.get()
            out = os.path.splitext(path)[0] + ".png"
            Image.open(path).save(out, "PNG")
            self.finish(f"Saved: {out}")
        except Exception as e: self.finish(str(e), False)

    def to_jpg(self):
        try:
            path = self.file_path.get()
            out = os.path.splitext(path)[0] + ".jpg"
            img = Image.open(path)
            if img.mode in ("RGBA", "P"): # Handle Transparency
                img = img.convert("RGB")
            img.save(out, "JPEG", quality=90)
            self.finish(f"Saved: {out}")
        except Exception as e: self.finish(str(e), False)

    def to_svg(self):
        try:
            path = self.file_path.get()
            out = os.path.splitext(path)[0] + ".svg"
            # FIX: vtracer updated their function name
            vtracer.convert_image_to_svg_py(path, out)
            self.finish(f"Vectorized: {out}")
        except Exception as e: self.finish(f"Vtracer Error: {str(e)}", False)

    def to_mp3(self):
        path = self.file_path.get()
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.webp']:
            self.finish("You cannot extract audio from an image file!", False)
            return
        
        try:
            out = os.path.splitext(path)[0] + ".mp3"
            with VideoFileClip(path) as clip:
                clip.audio.write_audiofile(out, logger=None)
            self.finish(f"Audio Saved: {out}")
        except Exception as e: self.finish(str(e), False)

    def strip_metadata(self):
        try:
            path = self.file_path.get()
            out = os.path.splitext(path)[0] + "_clean.jpg"
            img = Image.open(path)
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            # Creating a new image object effectively strips metadata
            clean_img = Image.new(img.mode, img.size)
            clean_img.putdata(list(img.getdata()))
            clean_img.save(out)
            self.finish("Metadata removed.")
        except Exception as e: self.finish(str(e), False)

    def get_palette(self):
        try:
            path = self.file_path.get()
            img = Image.open(path).resize((50, 50))
            result = img.convert('P', palette=Image.ADAPTIVE, colors=5)
            palette = result.getpalette()
            color_counts = sorted(result.getcolors(), reverse=True)
            hex_colors = []
            for i in range(min(5, len(color_counts))):
                idx = color_counts[i][1]
                r, g, b = palette[idx*3:idx*3+3]
                hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")
            self.finish(f"Top Colors: {', '.join(hex_colors)}")
        except Exception as e: self.finish(str(e), False)

if __name__ == "__main__":
    root = tk.Tk()
    app = DesignerApp(root)
    root.mainloop()
