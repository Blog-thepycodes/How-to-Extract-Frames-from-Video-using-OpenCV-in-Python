import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
import threading
import logging
 
 
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
 
 
def format_timedelta(td):
   """Formats timedelta to a string in HH-MM-SS.MS format."""
   result, ms = divmod(td.total_seconds(), 1)
   ms = int(ms * 1000)
   return f"{str(timedelta(seconds=int(result)))}.{ms:03}".replace(":", "-")
 
 
def save_frame(frame, frame_index, fps, output_dir, quality=95):
   """Save a single frame with specified JPEG quality."""
   timestamp = format_timedelta(timedelta(seconds=frame_index / fps))
   frame_filename = os.path.join(output_dir, f"frame-{timestamp}.jpg")
   cv2.imwrite(frame_filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
   logging.info(f"Saved {frame_filename}")
 
 
def extract_frames(video_path, num_frames, output_dir, progress_callback):
   """Extracts a specified number of frames evenly spaced throughout the video."""
   cap = cv2.VideoCapture(video_path)
   if not cap.isOpened():
       messagebox.showerror("Error", "Cannot open video file.")
       return
 
 
   total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
   fps = cap.get(cv2.CAP_PROP_FPS)
   interval = total_frames // num_frames
 
 
   with ThreadPoolExecutor(max_workers=4) as executor:
       for i in range(0, total_frames, interval):
           cap.set(cv2.CAP_PROP_POS_FRAMES, i)
           ret, frame = cap.read()
           if ret:
               executor.submit(save_frame, frame, i, fps, output_dir)
               progress_callback(i / total_frames)
           else:
               logging.warning(f"Skipping frame at index {i}: Cannot read frame.")
 
 
   cap.release()
   progress_callback(1)  # Ensure the progress is set to 100% at the end
 
 
def load_file(entry_widget):
   file_path = filedialog.askopenfilename()
   if file_path:
       entry_widget.delete(0, tk.END)
       entry_widget.insert(0, file_path)
 
 
def select_output_directory(entry_widget):
   directory = filedialog.askdirectory()
   if directory:
       entry_widget.delete(0, tk.END)
       entry_widget.insert(0, directory)
 
 
def start_extraction_thread(video_path, num_frames, output_dir, progress_label):
   if not video_path or not num_frames or not output_dir:
       messagebox.showwarning("Warning", "Please specify a video file, total frames, and output directory.")
       return
 
 
   if not os.path.exists(output_dir):
       os.makedirs(output_dir)
 
 
   threading.Thread(target=extract_frames, args=(video_path, num_frames, output_dir, lambda progress: progress_label.config(text=f"Progress: {int(progress * 100)}%")), daemon=True).start()
 
 
def start_extraction(path_entry, frame_count_entry, output_dir_entry, progress_label):
   video_path = path_entry.get()
   num_frames = int(frame_count_entry.get())
   output_dir = output_dir_entry.get()
   start_extraction_thread(video_path, num_frames, output_dir, progress_label)
 
 
if __name__ == "__main__":
   root = tk.Tk()
   root.title("Frame Extractor Tool - The Pycodes")
   root.geometry("600x300")
 
 
   # Widgets
   path_entry = tk.Entry(root, width=50)
   path_entry.grid(row=0, column=1, padx=10, pady=10)
 
 
   browse_button = tk.Button(root, text="Browse", command=lambda: load_file(path_entry))
   browse_button.grid(row=0, column=2, padx=10, pady=10)
 
 
   frame_count_entry = tk.Entry(root, width=10)
   frame_count_entry.grid(row=1, column=1, padx=10, pady=10)
   frame_count_entry.insert(0, "10")  # Default number of frames
 
 
   frame_count_label = tk.Label(root, text="Total Frames:")
   frame_count_label.grid(row=1, column=0, padx=10, pady=10)
 
 
   output_dir_entry = tk.Entry(root, width=50)
   output_dir_entry.grid(row=2, column=1, padx=10, pady=10)
 
 
   output_dir_button = tk.Button(root, text="Select Output Directory", command=lambda: select_output_directory(output_dir_entry))
   output_dir_button.grid(row=2, column=2, padx=10, pady=10)
 
 
   start_button = tk.Button(root, text="Start Extraction", command=lambda: start_extraction(path_entry, frame_count_entry, output_dir_entry, progress_label))
   start_button.grid(row=3, column=1, padx=10, pady=10)
 
 
   progress_label = tk.Label(root, text="Progress: 0%")
   progress_label.grid(row=4, column=1, padx=10, pady=10)
 
 
   root.mainloop()
