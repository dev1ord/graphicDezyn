import os
import sys
import subprocess
from pathlib import Path
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# =====================================================
# AUTO-INSTALL MOVIEPY IF MISSING
# =====================================================

try:
    from moviepy import VideoFileClip
except ImportError:
    print("Installing moviepy...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
    from moviepy import VideoFileClip


SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp")


# =====================================================
# SMART UNIVERSAL IMAGE PROCESSOR
# =====================================================

class ImageProcessor:

    def __init__(self, overwrite=False):
        self.overwrite = overwrite

    def process(self, input_path, output_folder=None,
                quality=75, max_width=None, max_height=None):

        input_path = Path(input_path)

        if not input_path.exists():
            print("❌ Path does not exist.")
            return

        if input_path.is_file():
            self._process_single_file(
                input_path, output_folder, quality, max_width, max_height
            )
        else:
            for file in input_path.rglob("*"):
                if file.suffix.lower() in SUPPORTED_FORMATS:
                    self._process_single_file(
                        file, output_folder, quality, max_width, max_height
                    )

        print("✅ Processing Finished.")

    def _process_single_file(self, file_path, output_folder,
                             quality, max_width, max_height):

        try:
            img = Image.open(file_path)

            # Resize
            if max_width or max_height:
                img.thumbnail((
                    max_width or img.width,
                    max_height or img.height
                ))

            # Determine output path
            if output_folder:
                output_folder = Path(output_folder)
                output_folder.mkdir(parents=True, exist_ok=True)
                output_path = output_folder / file_path.name
            else:
                if self.overwrite:
                    output_path = file_path
                else:
                    output_path = file_path.with_name(
                        file_path.stem + "_processed" + file_path.suffix
                    )

            # Save safely
            save_kwargs = {"optimize": True}
            if file_path.suffix.lower() in (".jpg", ".jpeg", ".webp"):
                save_kwargs["quality"] = quality

            img.save(output_path, **save_kwargs)

            print(f"✅ Processed: {file_path.name}")

        except Exception as e:
            print(f"❌ Failed: {file_path.name} -> {e}")


# =====================================================
# AUDIO EXTRACTION USING MOVIEPY (MODERN IMPORT)
# =====================================================

def extract_audio(video_path, output_audio=None):
    try:
        video_path = Path(video_path)

        if not video_path.exists():
            print("❌ Video file not found.")
            return

        if output_audio is None:
            output_audio = video_path.with_suffix(".mp3")

        with VideoFileClip(str(video_path)) as video:
            if video.audio is None:
                print("❌ No audio stream found.")
                return
            video.audio.write_audiofile(str(output_audio))

        print(f"🎵 Audio extracted: {output_audio}")

    except Exception as e:
        print(f"❌ Audio extraction failed: {e}")


# =====================================================
# TKINTER GUI
# =====================================================

class DesignerToolkitApp:

    def __init__(self, root):
        self.root = root
        self.root.title("HeyNee - Bulk Image Processor")
        self.root.geometry("450x450")
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.quality = tk.IntVar(value=75)
        self.max_width = tk.IntVar(value=0)
        self.max_height = tk.IntVar(value=0)
        self.overwrite = tk.BooleanVar(value=False)

        self.build_ui()

    def build_ui(self):

        ttk.Label(self.root, text="Input File / Folder").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.input_path, width=60).pack()
        ttk.Button(self.root, text="Browse",
                   command=self.browse_input).pack(pady=5)

        ttk.Label(self.root, text="Output Folder (Optional)").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.output_path, width=60).pack()
        ttk.Button(self.root, text="Browse",
                   command=self.browse_output).pack(pady=5)

        ttk.Label(self.root, text="Quality (1-95)").pack()
        ttk.Entry(self.root, textvariable=self.quality).pack()

        ttk.Label(self.root, text="Max Width (Optional)").pack()
        ttk.Entry(self.root, textvariable=self.max_width).pack()

        ttk.Label(self.root, text="Max Height (Optional)").pack()
        ttk.Entry(self.root, textvariable=self.max_height).pack()

        ttk.Checkbutton(self.root,
                        text="Overwrite Original Files",
                        variable=self.overwrite).pack(pady=5)

        ttk.Button(self.root,
                   text="Run Image Processor",
                   command=self.run_processor).pack(pady=10)

        ttk.Button(self.root,
                   text="Extract Audio From Video",
                   command=self.extract_audio_gui).pack(pady=5)

    # -----------------------------

    def browse_input(self):
        path = filedialog.askopenfilename() or filedialog.askdirectory()
        self.input_path.set(path)

    def browse_output(self):
        path = filedialog.askdirectory()
        self.output_path.set(path)

    # -----------------------------

    def run_processor(self):

        if not self.input_path.get():
            messagebox.showerror("Error", "Please select input path.")
            return

        processor = ImageProcessor(overwrite=self.overwrite.get())

        processor.process(
            input_path=self.input_path.get(),
            output_folder=self.output_path.get() or None,
            quality=self.quality.get(),
            max_width=self.max_width.get() or None,
            max_height=self.max_height.get() or None
        )

        messagebox.showinfo("Done", "Image Processing Completed!")

    # -----------------------------

    def extract_audio_gui(self):

        video_file = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.avi")]
        )

        if video_file:
            extract_audio(video_file)
            messagebox.showinfo("Done", "Audio Extraction Completed!")


# =====================================================
# MAIN ENTRY
# =====================================================

if __name__ == "__main__":

    print("🚀 Junior Designer Toolkit Started")
    print("✔ Single file support")
    print("✔ Folder support")
    print("✔ Recursive subfolder support")
    print("✔ Safe overwrite system")
    print("✔ MoviePy audio extraction")
    print("✔ Clean modular design")

    root = tk.Tk()
    app = DesignerToolkitApp(root)
    root.mainloop()
