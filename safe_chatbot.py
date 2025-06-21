#!/usr/bin/env python3
import sys
import os

# Fix for the stderr issue
if hasattr(sys, 'ps1'):
    import io
    sys.stderr = io.StringIO()

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, filedialog, messagebox
    import threading
    from datetime import datetime
    import re
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required packages or check your Python installation")
    sys.exit(1)

class RadarFileChatbot:
    def __init__(self):
        # Initialize root window first
        self.root = tk.Tk()
        self.root.withdraw()  # Hide initially
        
        try:
            self.setup_window()
            self.setup_variables()
            self.create_widgets()
            self.check_directory()
            
            # Show window after everything is set up
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize: {str(e)}")
            self.root.destroy()
            return
    
    def setup_window(self):
        """Configure the main window"""
        self.root.title("🛡️ Radar File Chatbot")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)
        
        # Set window icon (optional)
        try:
            # You can add an icon file here if you have one
            # self.root.iconbitmap('radar_icon.ico')
            pass
        except:
            pass
        
        # Configure style
        style = ttk.Style()
        try:
            style.theme_use('clam')  # Modern looking theme
        except:
            pass  # Use default if clam not available
    
    def setup_variables(self):
        """Initialize all variables"""
        self.base_dir = r"D:\bel\radar_data_sample120"
        self.file_extensions = ['.txt', '.log', '.dat', '.csv']
        self.searching = False
        
        # Tkinter variables
        self.dir_var = tk.StringVar(value=self.base_dir)
        self.status_var = tk.StringVar(value="Initializing...")
        self.input_var = tk.StringVar()
    
    def create_widgets(self):
        """Create all UI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header section
        self.create_header(main_frame)
        
        # File type selection
        self.create_filetype_section(main_frame)
        
        # Chat interface
        self.create_chat_interface(main_frame)
        
        # Welcome message
        self.add_welcome_message()
    
    def create_header(self, parent):
        """Create the header section with directory controls"""
        header_frame = ttk.LabelFrame(parent, text="📁 Directory Settings", padding=10)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Directory selection row
        dir_frame = ttk.Frame(header_frame)
        dir_frame.pack(fill=tk.X)
        
        ttk.Label(dir_frame, text="Base Directory:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=60)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(dir_frame, text="Validate", command=self.check_directory).pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = ttk.Label(header_frame, textvariable=self.status_var)
        self.status_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_filetype_section(self, parent):
        """Create file type selection checkboxes"""
        filetype_frame = ttk.LabelFrame(parent, text="📄 File Types to Search", padding=10)
        filetype_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create checkboxes for file types
        checkbox_frame = ttk.Frame(filetype_frame)
        checkbox_frame.pack(fill=tk.X)
        
        self.file_type_vars = {}
        extensions = ['.txt', '.log', '.dat', '.csv', '.json', '.xml', '.py']
        
        for i, ext in enumerate(extensions):
            var = tk.BooleanVar(value=ext in self.file_extensions)
            self.file_type_vars[ext] = var
            
            cb = ttk.Checkbutton(checkbox_frame, text=ext, variable=var, 
                               command=self.update_file_extensions)
            cb.grid(row=0, column=i, padx=10, sticky=tk.W)
    
    def create_chat_interface(self, parent):
        """Create the main chat interface"""
        chat_frame = ttk.LabelFrame(parent, text="💬 Chat Interface", padding=10)
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Messages area
        self.create_messages_area(chat_frame)
        
        # Input area
        self.create_input_area(chat_frame)
        
        # Progress bar
        self.progress = ttk.Progressbar(chat_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(5, 0))
    
    def create_messages_area(self, parent):
        """Create the scrollable messages area"""
        # Frame for the text widget and scrollbar
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Text widget with scrollbar
        self.messages_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg='#f8f9fa',
            fg='#212529',
            selectbackground='#007bff',
            insertbackground='#007bff',
            relief=tk.FLAT,
            bd=1
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.messages_text.yview)
        self.messages_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack text and scrollbar
        self.messages_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags for styling
        self.configure_text_tags()
        
        # Make text widget read-only
        self.messages_text.config(state=tk.DISABLED)
    
    def configure_text_tags(self):
        """Configure text styling tags"""
        self.messages_text.tag_configure('timestamp', foreground='#6c757d', font=('Consolas', 9))
        self.messages_text.tag_configure('user', foreground='#007bff', font=('Consolas', 11, 'bold'))
        self.messages_text.tag_configure('bot', foreground='#28a745', font=('Consolas', 11))
        self.messages_text.tag_configure('result', foreground='#17a2b8', font=('Consolas', 10))
        self.messages_text.tag_configure('path', foreground='#6c757d', font=('Consolas', 9))
        self.messages_text.tag_configure('error', foreground='#dc3545', font=('Consolas', 11))
        self.messages_text.tag_configure('success', foreground='#28a745', font=('Consolas', 11))
    
    def create_input_area(self, parent):
        """Create the input area with entry and send button"""
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Input entry
        self.input_entry = ttk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=('Consolas', 11)
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_entry.bind('<Return>', self.send_message)
        self.input_entry.bind('<Up>', self.previous_query)  # Optional: history
        
        # Send button
        self.send_button = ttk.Button(
            input_frame,
            text="🔍 Search",
            command=self.send_message,
            width=12
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Focus on input
        self.input_entry.focus()
    
    def add_welcome_message(self):
        """Add welcome messages to the chat"""
        self.add_message("🛡️ Chatbot Ready!", 'bot')
        self.add_message("Welcome! I can help you search through your files.", 'bot')
        self.add_message("-" * 80, 'bot')
    
    def browse_directory(self):
        """Open directory browser dialog"""
        try:
            directory = filedialog.askdirectory(
                initialdir=self.base_dir,
                title="Select Radar Data Directory"
            )
            if directory:
                self.dir_var.set(directory)
                self.base_dir = directory
                self.check_directory()
        except Exception as e:
            self.add_message(f"❌ Error browsing directory: {str(e)}", 'error')
    
    def update_file_extensions(self):
        """Update file extensions based on checkbox selection"""
        self.file_extensions = [ext for ext, var in self.file_type_vars.items() if var.get()]
        if self.file_extensions:
            self.check_directory()  # Revalidate with new extensions
    
    def check_directory(self):
        """Validate the selected directory and count files"""
        directory = self.dir_var.get().strip()
        
        if not directory:
            self.status_var.set("❌ Please select a directory")
            return False
        
        if not os.path.exists(directory):
            self.status_var.set("❌ Directory does not exist")
            return False
        
        try:
            file_count = 0
            selected_extensions = [ext for ext, var in self.file_type_vars.items() if var.get()]
            
            if not selected_extensions:
                self.status_var.set("❌ Please select at least one file type")
                return False
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(file.lower().endswith(ext.lower()) for ext in selected_extensions):
                        file_count += 1
            
            self.status_var.set(f"✅ Ready - Found {file_count} searchable files")
            self.base_dir = directory
            return True
            
        except Exception as e:
            self.status_var.set(f"❌ Error: {str(e)}")
            return False
    
    def add_message(self, message, tag='bot'):
        """Add a message to the chat display"""
        self.messages_text.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Add message with appropriate tag
        self.messages_text.insert(tk.END, f"{message}\n", tag)
        
        # Scroll to bottom
        self.messages_text.see(tk.END)
        self.messages_text.config(state=tk.DISABLED)
        
        # Update display
        self.root.update_idletasks()
    
    def send_message(self, event=None):
        """Handle sending a message/search query"""
        if self.searching:
            return
        
        query = self.input_var.get().strip()
        if not query:
            return
        
        # Clear input
        self.input_var.set("")
        
        # Add user message
        self.add_message(f"🔍 You: {query}", 'user')
        
        # Validate directory first
        if not self.check_directory():
            self.add_message("❌ Please fix directory settings first", 'error')
            return
        
        # Start search
        self.start_search(query)
    
    def start_search(self, query):
        """Start the file search in a background thread"""
        self.searching = True
        self.send_button.config(state='disabled', text="Searching...")
        self.progress.start()
        
        # Run search in background thread
        search_thread = threading.Thread(target=self.search_files, args=(query,), daemon=True)
        search_thread.start()
    
    def search_files(self, query):
        """Perform the actual file search"""
        try:
            # Extract keywords
            keywords = [word.lower() for word in re.findall(r'\b\w+\b', query) if len(word) > 2]
            
            if not keywords:
                self.root.after(0, lambda: self.search_complete("❌ Please provide meaningful search terms"))
                return
            
            # Search files
            results = []
            files_searched = 0
            selected_extensions = [ext for ext, var in self.file_type_vars.items() if var.get()]
            
            for root, dirs, files in os.walk(self.base_dir):
                for file in files:
                    if not any(file.lower().endswith(ext.lower()) for ext in selected_extensions):
                        continue
                    
                    file_path = os.path.join(root, file)
                    files_searched += 1
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            
                            if all(keyword in content for keyword in keywords):
                                snippet = self.get_snippet(content, keywords)
                                results.append({
                                    'path': file_path,
                                    'filename': os.path.basename(file_path),
                                    'snippet': snippet,
                                    'size': os.path.getsize(file_path)
                                })
                    except:
                        continue
            
            # Prepare results
            response = self.format_results(results, files_searched, keywords)
            self.root.after(0, lambda: self.search_complete(response))
            
        except Exception as e:
            error_msg = f"❌ Search error: {str(e)}"
            self.root.after(0, lambda: self.search_complete(error_msg))
    
    def get_snippet(self, content, keywords):
        """Extract relevant snippet containing keywords"""
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                return sentence.strip()[:200] + "..."
        
        return content[:200] + "..."
    
    def format_results(self, results, files_searched, keywords):
        """Format search results for display"""
        response = f"📊 Searched {files_searched} files for: {', '.join(keywords)}\n\n"
        
        if results:
            response += f"✅ Found {len(results)} matching files:\n\n"
            
            for i, result in enumerate(results[:8], 1):  # Show top 8 results
                size_kb = result['size'] / 1024
                response += f"[{i}] {result['filename']} ({size_kb:.1f} KB)\n"
                response += f"📂 {result['path']}\n"
                response += f"📝 {result['snippet']}\n\n"
            
            if len(results) > 8:
                response += f"... and {len(results) - 8} more files\n"
        else:
            response += "❌ No matching files found.\n"
            response += "💡 Try different keywords or check your directory path."
        
        return response
    
    def search_complete(self, message):
        """Handle search completion"""
        self.add_message(message, 'result')
        self.searching = False
        self.send_button.config(state='normal', text="🔍 Search")
        self.progress.stop()
        self.input_entry.focus()
    
    def previous_query(self, event=None):
        """Handle up arrow for query history (optional feature)"""
        pass  # You can implement query history here if needed
    
    def run(self):
        """Start the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            print(f"Error running application: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.searching:
            if messagebox.askokcancel("Quit", "Search in progress. Do you want to quit?"):
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Main function with better error handling"""
    try:
        # Check if we can import tkinter
        import tkinter as tk
        
        # Create and run the application
        app = RadarFileChatbot()
        if app.root.winfo_exists():  # Check if window was created successfully
            app.run()
        
    except ImportError:
        print("❌ Tkinter is not available. Please install tkinter or use the command-line version.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        print("Try running the command-line version instead.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
