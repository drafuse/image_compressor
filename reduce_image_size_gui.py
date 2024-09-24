import tkinter as tk
from tkinter import filedialog, messagebox, font, Label
from PIL import Image, ImageTk
import os
import webbrowser


def reduce_image_size(input_path, output_path, target_size_kb):
    target_size = target_size_kb * 1024  # Convert target size to bytes
    initial_quality = 95  # Starting quality
    min_quality = 10  # Minimum quality to ensure image is not too degraded
    broad_step = 5  # Larger step for initial reduction
    fine_step = 1  # Smaller step for fine-tuning
    tolerance = 10240  # Allowable deviation from target size in bytes (10 KB)

    with Image.open(input_path) as img:
        img_format = img.format.upper()  # Capture the format of the image and convert it to uppercase
        exif_data = img.info.get('exif')

        # Inner function to save with quality settings
        def save_with_quality(quality, img_format):
            if img_format in ['TIFF', 'TIF']:
                img_format = 'TIFF'  # Standardize to TIFF
                if exif_data:
                    img.save(output_path, format=img_format, compression="tiff_jpeg", quality=quality, exif=exif_data)
                else:
                    img.save(output_path, format=img_format, compression="tiff_jpeg", quality=quality)
            else:
                if exif_data:
                    img.save(output_path, format=img_format, quality=quality, optimize=True, exif=exif_data)
                else:
                    img.save(output_path, format=img_format, quality=quality, optimize=True)

        # Broad reduction loop
        quality = initial_quality
        while quality >= min_quality:
            save_with_quality(quality, img_format)
            if os.path.getsize(output_path) <= target_size:
                break
            quality -= broad_step

        # Fine-tuning loop
        low_quality = quality
        high_quality = quality + broad_step
        while high_quality - low_quality > fine_step:
            quality = (low_quality + high_quality) // 2
            save_with_quality(quality, img_format)
            current_size = os.path.getsize(output_path)

            if target_size - tolerance <= current_size <= target_size:
                break
            elif current_size < target_size - tolerance:
                low_quality = quality + fine_step
            else:
                high_quality = quality - fine_step

        # Final adjustment if still needed
        if os.path.getsize(output_path) > target_size:
            save_with_quality(low_quality, img_format)


def select_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.tiff;*.tif;*.bmp")]
    )
    if file_path:
        image_path.set(file_path)
        bulk_folder.set("")  # Clear folder selection if single image is selected


def select_output_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_folder.set(folder_selected)


def select_bulk_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        bulk_folder.set(folder_selected)
        image_path.set("")  # Clear single image selection if folder is selected


def compress_images():
    if bulk_folder.get():
        input_folder = bulk_folder.get()
        output_dir = output_folder.get()
        target_size_kb = target_size.get()

        if not target_size_kb.isdigit():
            messagebox.showerror("Error", "Please enter a valid target size in KB!")
            return

        supported_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']
        try:
            for root, _, files in os.walk(input_folder):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in supported_formats:
                        input_path = os.path.join(root, file)
                        output_path = os.path.join(output_dir, f"compressed_{file}")
                        reduce_image_size(input_path, output_path, int(target_size_kb))
            messagebox.showinfo("Success", "All images in the folder have been compressed!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compress images in folder: {str(e)}")

    elif image_path.get():
        input_path = image_path.get()
        output_dir = output_folder.get()
        target_size_kb = target_size.get()

        if not target_size_kb.isdigit():
            messagebox.showerror("Error", "Please enter a valid target size in KB!")
            return

        output_path = os.path.join(output_dir, f"compressed_{os.path.basename(input_path)}")

        try:
            reduce_image_size(input_path, output_path, int(target_size_kb))
            messagebox.showinfo("Success", f"Image compressed and saved at: {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compress image: {str(e)}")
    else:
        messagebox.showerror("Error", "Please select an image or a folder containing images.")


# Function to open the GitHub link
def open_github():
    webbrowser.open("https://github.com/drafuse")

# Create the GUI window
app = tk.Tk()
app.title("Image Compressor")
app.configure(bg="#1e1e1e")  # Dark background
app.geometry("600x500")  # Set initial size
app.minsize(400, 300)  # Minimum size for the window

# Set app icon
def set_app_icon():
    ico_icon_path = "compressor_icon.ico"  # Use the ICO file path
    app.iconbitmap(ico_icon_path)  # Set the icon for the window

# Set a modern font
app_font = font.Font(family='Segoe UI', size=12)
header_font = font.Font(family='Segoe UI', size=16, weight='bold')

# Variables to hold file and folder paths
image_path = tk.StringVar()
output_folder = tk.StringVar()
bulk_folder = tk.StringVar()
target_size = tk.StringVar()

# Frame for the image selection
image_frame = tk.Frame(app, bg="#1e1e1e")
image_frame.pack(pady=10, fill='both', expand=True)

# Section header
image_header = tk.Label(image_frame, text="Select Image(s)", bg="#1e1e1e", fg="white", font=header_font)
image_header.pack(pady=5)

# Select Image button
select_button = tk.Button(image_frame, text="Select Single Image", command=select_image, font=app_font, bg="#4CAF50",
                          fg="white")
select_button.pack(pady=5, fill='x')

# Image path entry
image_label = tk.Entry(image_frame, textvariable=image_path, font=app_font)
image_label.pack(pady=5, fill='x', expand=True)

# Select Bulk Folder button
bulk_button = tk.Button(image_frame, text="Select Folder with Images", command=select_bulk_folder, font=app_font,
                        bg="#4CAF50", fg="white")
bulk_button.pack(pady=5, fill='x')

# Bulk folder path entry
bulk_folder_label = tk.Entry(image_frame, textvariable=bulk_folder, font=app_font)
bulk_folder_label.pack(pady=5, fill='x', expand=True)

# Frame for the target size and output selection
target_frame = tk.Frame(app, bg="#1e1e1e")
target_frame.pack(pady=10, fill='both', expand=True)

# Section header
target_header = tk.Label(target_frame, text="Target Size & Output", bg="#1e1e1e", fg="white", font=header_font)
target_header.pack(pady=5)

# Target Size label and entry
target_size_label = tk.Label(target_frame, text="Target Size (KB):", bg="#1e1e1e", fg="white", font=app_font)
target_size_label.pack(pady=5)
target_size_entry = tk.Entry(target_frame, textvariable=target_size, font=app_font, width=10)
target_size_entry.pack(pady=5)

# Select Output Folder button
output_button = tk.Button(target_frame, text="Select Output Folder", command=select_output_folder, font=app_font,
                          bg="#4CAF50", fg="white")
output_button.pack(pady=5, fill='x')

# Output folder path entry
output_label = tk.Entry(target_frame, textvariable=output_folder, font=app_font)
output_label.pack(pady=5, fill='x', expand=True)

# Compress Images button
compress_button = tk.Button(target_frame, text="Compress Images", command=compress_images, font=app_font, bg="#4CAF50",
                            fg="white")
compress_button.pack(pady=10, fill='x')

# Information Label with hyperlink
info_frame = tk.Frame(app, bg="#1e1e1e")
info_frame.pack(pady=10, fill='both', expand=True)

info_label = tk.Label(info_frame, text="Image Compressor (version 0.1) | Built by Dan Rafuse\nContact: ", bg="#1e1e1e",
                      fg="white", font=app_font)
info_label.pack(pady=10, anchor='s')

github_link = tk.Label(info_frame, text="GitHub", fg="#4CAF50", bg="#1e1e1e", font=app_font, cursor="hand2")
github_link.pack(anchor='s')
github_link.bind("<Button-1>", lambda e: open_github())

# Run the GUI loop
app.mainloop()
