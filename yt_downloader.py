import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import subprocess
import sys

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.download_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="best")
        self.format_var = tk.StringVar(value="mp4")
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        
        self.setup_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # URL input section
        ttk.Label(main_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Download path section
        ttk.Label(main_frame, text="Download Path:").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        path_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(path_frame, textvariable=self.download_path, width=40).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(path_frame, text="Browse", command=self.browse_path).grid(row=0, column=1, padx=(5, 0))
        
        # Quality selection
        ttk.Label(main_frame, text="Quality:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        quality_combo = ttk.Combobox(main_frame, textvariable=self.quality_var, width=20)
        quality_combo['values'] = ('best', '8K (4320p)', '4K (2160p)', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p', 'worst')
        quality_combo.grid(row=2, column=1, sticky=tk.W, pady=(10, 5))
        
        # Format selection
        ttk.Label(main_frame, text="Format:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        format_combo = ttk.Combobox(main_frame, textvariable=self.format_var, width=20)
        format_combo['values'] = ('mp4', 'webm', 'mkv', 'mp3', 'wav', 'flac')
        format_combo.grid(row=3, column=1, sticky=tk.W, pady=(10, 5))
        
        # Download type selection
        self.download_type = tk.StringVar(value="video")
        ttk.Label(main_frame, text="Download Type:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        type_frame = ttk.Frame(main_frame)
        type_frame.grid(row=4, column=1, sticky=tk.W, pady=(10, 5))
        ttk.Radiobutton(type_frame, text="Video", variable=self.download_type, value="video").grid(row=0, column=0)
        ttk.Radiobutton(type_frame, text="Audio Only", variable=self.download_type, value="audio").grid(row=0, column=1, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(20, 10))
        
        ttk.Button(button_frame, text="Get Info", command=self.get_video_info).grid(row=0, column=0, padx=(0, 10))
        self.download_btn = ttk.Button(button_frame, text="Download", command=self.start_download)
        self.download_btn.grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).grid(row=0, column=2)
        
        # Progress bar
        ttk.Label(main_frame, text="Progress:").grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=7, column=0, columnspan=3, pady=(5, 10))
        
        # Output text area
        ttk.Label(main_frame, text="Output:").grid(row=8, column=0, sticky=(tk.W, tk.N), pady=(10, 5))
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=8, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        self.output_text = tk.Text(text_frame, height=10, width=50)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def check_dependencies(self):
        """Check if yt-dlp is installed"""
        try:
            subprocess.run(['yt-dlp', '--version'], check=True, capture_output=True)
            self.log_output("yt-dlp found and ready to use!\n")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log_output("WARNING: yt-dlp not found!\n")
            self.log_output("Please install yt-dlp using: pip install yt-dlp\n")
            self.log_output("Or download from: https://github.com/yt-dlp/yt-dlp\n\n")
            messagebox.showwarning("Dependency Missing", 
                                 "yt-dlp is required for this application to work.\n\n"
                                 "Please install it using:\npip install yt-dlp")
    
    def browse_path(self):
        """Browse for download directory"""
        path = filedialog.askdirectory(initialdir=self.download_path.get())
        if path:
            self.download_path.set(path)
    
    def log_output(self, message):
        """Add message to output text area"""
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)
        self.root.update()
    
    def clear_fields(self):
        """Clear all input fields and output"""
        self.url_var.set("")
        self.output_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Ready")
    
    def get_video_info(self):
        """Get video information without downloading"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        self.status_var.set("Getting video info...")
        self.log_output(f"Getting info for: {url}\n")
        
        def info_thread():
            try:
                cmd = ['yt-dlp', '--print', 'title', '--print', 'duration', '--print', 'uploader', url]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 3:
                    title = lines[0]
                    duration = lines[1]
                    uploader = lines[2]
                    
                    info_text = f"Title: {title}\n"
                    info_text += f"Duration: {duration}\n"
                    info_text += f"Uploader: {uploader}\n\n"
                    
                    self.log_output(info_text)
                    self.status_var.set("Info retrieved successfully")
                else:
                    self.log_output("Could not retrieve complete video info\n")
                    self.status_var.set("Info retrieval incomplete")
                    
            except subprocess.CalledProcessError as e:
                self.log_output(f"Error getting video info: {e.stderr}\n")
                self.status_var.set("Error getting info")
            except Exception as e:
                self.log_output(f"Unexpected error: {str(e)}\n")
                self.status_var.set("Error")
        
        threading.Thread(target=info_thread, daemon=True).start()
    
    def start_download(self):
        """Start the download process"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        download_path = self.download_path.get()
        if not os.path.exists(download_path):
            messagebox.showerror("Error", "Download path does not exist")
            return
        
        self.download_btn.config(state='disabled')
        self.status_var.set("Downloading...")
        self.progress_var.set(0)
        
        def download_thread():
            try:
                # Build yt-dlp command
                cmd = ['yt-dlp']
                
                # Add output path
                cmd.extend(['-o', os.path.join(download_path, '%(title)s.%(ext)s')])
                
                # Add format selection
                if self.download_type.get() == "audio":
                    if self.format_var.get() in ['mp3', 'wav', 'flac']:
                        cmd.extend(['-x', '--audio-format', self.format_var.get()])
                    else:
                        cmd.extend(['-x', '--audio-format', 'mp3'])
                else:
                    # Video download with best quality format selection
                    format_ext = self.format_var.get()
                    
                    if self.quality_var.get() == "best":
                        cmd.extend(['-f', f'bestvideo[ext={format_ext}]+bestaudio/bestvideo+bestaudio/best[ext={format_ext}]/best'])
                    elif self.quality_var.get() == "worst":
                        cmd.extend(['-f', f'worstvideo[ext={format_ext}]+bestaudio/worstvideo+bestaudio/worst'])
                    elif self.quality_var.get() == "8K (4320p)":
                        cmd.extend(['-f', f'bestvideo[height<=4320][ext={format_ext}]+bestaudio/bestvideo[height<=4320]+bestaudio/best[height<=4320]'])
                    elif self.quality_var.get() == "4K (2160p)":
                        cmd.extend(['-f', f'bestvideo[height<=2160][ext={format_ext}]+bestaudio/bestvideo[height<=2160]+bestaudio/best[height<=2160]'])
                    elif self.quality_var.get() == "1440p":
                        cmd.extend(['-f', f'bestvideo[height<=1440][ext={format_ext}]+bestaudio/bestvideo[height<=1440]+bestaudio/best[height<=1440]'])
                    elif self.quality_var.get() == "1080p":
                        cmd.extend(['-f', f'bestvideo[height<=1080][ext={format_ext}]+bestaudio/bestvideo[height<=1080]+bestaudio/best[height<=1080]'])
                    elif self.quality_var.get() == "720p":
                        cmd.extend(['-f', f'bestvideo[height<=720][ext={format_ext}]+bestaudio/bestvideo[height<=720]+bestaudio/best[height<=720]'])
                    elif self.quality_var.get() == "480p":
                        cmd.extend(['-f', f'bestvideo[height<=480][ext={format_ext}]+bestaudio/bestvideo[height<=480]+bestaudio/best[height<=480]'])
                    elif self.quality_var.get() == "360p":
                        cmd.extend(['-f', f'bestvideo[height<=360][ext={format_ext}]+bestaudio/bestvideo[height<=360]+bestaudio/best[height<=360]'])
                    elif self.quality_var.get() == "240p":
                        cmd.extend(['-f', f'bestvideo[height<=240][ext={format_ext}]+bestaudio/bestvideo[height<=240]+bestaudio/best[height<=240]'])
                    elif self.quality_var.get() == "144p":
                        cmd.extend(['-f', f'bestvideo[height<=144][ext={format_ext}]+bestaudio/bestvideo[height<=144]+bestaudio/best[height<=144]'])
                    else:
                        # Fallback for any other resolution
                        cmd.extend(['-f', f'bestvideo[ext={format_ext}]+bestaudio/bestvideo+bestaudio/best'])
                    
                    # Force output format if different from source
                    if format_ext != 'webm':
                        cmd.extend(['--merge-output-format', format_ext])
                
                # Add URL
                cmd.append(url)
                
                self.log_output(f"Starting download with command: {' '.join(cmd)}\n")
                
                # Execute download
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                         text=True, universal_newlines=True)
                
                # Read output line by line
                for line in process.stdout:
                    self.log_output(line)
                    
                    # Simple progress estimation (yt-dlp output parsing would be more complex)
                    if "%" in line and "ETA" in line:
                        try:
                            # Extract percentage
                            parts = line.split()
                            for part in parts:
                                if part.endswith('%'):
                                    percent = float(part.replace('%', ''))
                                    self.progress_var.set(percent)
                                    break
                        except:
                            pass
                
                process.wait()
                
                if process.returncode == 0:
                    self.progress_var.set(100)
                    self.status_var.set("Download completed successfully!")
                    self.log_output("Download completed!\n")
                    messagebox.showinfo("Success", "Download completed successfully!")
                else:
                    self.status_var.set("Download failed")
                    self.log_output("Download failed!\n")
                    messagebox.showerror("Error", "Download failed. Check output for details.")
                    
            except Exception as e:
                self.log_output(f"Error during download: {str(e)}\n")
                self.status_var.set("Download error")
                messagebox.showerror("Error", f"Download error: {str(e)}")
            
            finally:
                self.download_btn.config(state='normal')
        
        threading.Thread(target=download_thread, daemon=True).start()

def main():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()