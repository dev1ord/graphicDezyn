import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import threading


class ImageCompressorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Compressor")
        self.geometry("600x650")
        self.resizable(False, False)
        
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header = ttk.Label(
            self, 
            text="Image Compressor", 
            font=("Arial", 16, "bold")
        )
        header.pack(pady=15)
        
        # Input Folder
        input_frame = ttk.LabelFrame(self, text="Input Folder", padding=10)
        input_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Entry(input_frame, textvariable=self.input_folder, width=50).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(input_frame, text="Browse", command=self.select_input_folder).pack(side="left")
        
        # Output Folder
        output_frame = ttk.LabelFrame(self, text="Output Folder (optional)", padding=10)
        output_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Entry(output_frame, textvariable=self.output_folder, width=50).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(output_frame, text="Browse", command=self.select_output_folder).pack(side="left")
        ttk.Button(output_frame, text="Clear", command=lambda: self.output_folder.set("")).pack(side="left", padx=(5, 0))
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(self, text="Compression Settings", padding=15)
        settings_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Quality
        ttk.Label(settings_frame, text="Quality (1-95):").grid(row=0, column=0, sticky="w", pady=10)
        self.quality_var = tk.IntVar(value=60)
        quality_scale = ttk.Scale(
            settings_frame, 
            from_=1, 
            to=95, 
            orient="horizontal", 
            variable=self.quality_var,
            command=self.update_quality_label
        )
        quality_scale.grid(row=0, column=1, sticky="ew", padx=(10, 10))
        self.quality_label = ttk.Label(settings_frame, text="60")
        self.quality_label.grid(row=0, column=2)
        
        # Max Width
        ttk.Label(settings_frame, text="Max Width (px):").grid(row=1, column=0, sticky="w", pady=10)
        self.max_width_var = tk.StringVar(value="1920")
        ttk.Entry(settings_frame, textvariable=self.max_width_var, width=15).grid(row=1, column=1, sticky="w", padx=10)
        
        # Max Height
        ttk.Label(settings_frame, text="Max Height (px):").grid(row=2, column=0, sticky="w", pady=10)
        self.max_height_var = tk.StringVar(value="1080")
        ttk.Entry(settings_frame, textvariable=self.max_height_var, width=15).grid(row=2, column=1, sticky="w", padx=10)
        
        # Keep Format
        self.keep_format_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame, 
            text="Keep original format (uncheck to convert to JPEG)", 
            variable=self.keep_format_var
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=10)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Progress and Logs
        log_frame = ttk.LabelFrame(self, text="Progress", padding=10)
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, width=70, state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=15)
        
        self.compress_button = ttk.Button(button_frame, text="Start Compression", command=self.start_compression)
        self.compress_button.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side="left", padx=5)
        
    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)
    
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def update_quality_label(self, value):
        self.quality_label.config(text=str(int(float(value))))
    
    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.update()
    
    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
    
    def validate_inputs(self):
        if not self.input_folder.get():
            messagebox.showerror("Error", "Please select an input folder.")
            return False
        
        if not os.path.isdir(self.input_folder.get()):
            messagebox.showerror("Error", "Input folder does not exist.")
            return False
        
        try:
            self.quality_var.get()
            max_width = self.max_width_var.get()
            max_height = self.max_height_var.get()
            
            if max_width and int(max_width) <= 0:
                raise ValueError("Max width must be positive")
            if max_height and int(max_height) <= 0:
                raise ValueError("Max height must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return False
        
        return True
    
    def start_compression(self):
        if not self.validate_inputs():
            return
        
        self.compress_button.config(state="disabled")
        self.clear_log()
        
        thread = threading.Thread(target=self.compress_images_thread, daemon=True)
        thread.start()
    
    def compress_images_thread(self):
        try:
            input_folder = self.input_folder.get()
            output_folder = self.output_folder.get() if self.output_folder.get() else None
            quality = self.quality_var.get()
            max_width = int(self.max_width_var.get()) if self.max_width_var.get() else None
            max_height = int(self.max_height_var.get()) if self.max_height_var.get() else None
            keep_format = self.keep_format_var.get()
            
            self.log_message(f"Starting compression from: {input_folder}")
            if output_folder:
                self.log_message(f"Output folder: {output_folder}")
            else:
                self.log_message("Output folder: Same as input (overwrite mode)")
            
            self.compress_images(
                input_folder,
                output_folder,
                quality,
                max_width,
                max_height,
                keep_format
            )
            
            self.log_message("\n✓ Compression complete!")
            messagebox.showinfo("Success", "Image compression completed successfully!")
        
        except Exception as e:
            self.log_message(f"\n✗ Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
        
        finally:
            self.compress_button.config(state="normal")
    
    def compress_images(self, input_folder, output_folder, quality, max_width, max_height, keep_format):
        if output_folder:
            os.makedirs(output_folder, exist_ok=True)
        
        supported_ext = [".jpg", ".jpeg", ".png", ".webp"]
        compressed_count = 0
        failed_count = 0
        
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in supported_ext:
                    continue
                
                input_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, input_folder)
                
                # Output path
                if output_folder:
                    out_dir = os.path.join(output_folder, rel_path)
                    os.makedirs(out_dir, exist_ok=True)
                    output_path = os.path.join(out_dir, file)
                else:
                    output_path = input_path
                
                try:
                    img = Image.open(input_path)
                    
                    # Optional resizing
                    if max_width or max_height:
                        img.thumbnail((max_width or img.width, max_height or img.height))
                    
                    # Format handling
                    save_format = img.format if keep_format else "JPEG"
                    
                    # PNG compression
                    if save_format == "PNG":
                        img.save(output_path, optimize=True)
                    else:
                        img.save(output_path, optimize=True, quality=quality)
                    
                    self.log_message(f"✓ {file}")
                    compressed_count += 1
                
                except Exception as e:
                    self.log_message(f"✗ {file} ({e})")
                    failed_count += 1
        
        self.log_message(f"\nSummary: {compressed_count} succeeded, {failed_count} failed")


if __name__ == "__main__":
    app = ImageCompressorApp()
    app.mainloop()
