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
        self.root.title("Radar File Chatbot")
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
        
        # Character and result limits
        self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file
        self.MAX_SNIPPET_LENGTH = 200
        self.MAX_RESULTS_DISPLAY = 8
        self.MAX_TOTAL_RESPONSE_LENGTH = 50000  # ~50KB response limit
        self.MAX_FILES_TO_SEARCH = 10000  # Prevent infinite searches
        
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
        header_frame = ttk.LabelFrame(parent, text="Directory Settings", padding=10)
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
        filetype_frame = ttk.LabelFrame(parent, text="File Types to Search", padding=10)
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
        chat_frame = ttk.LabelFrame(parent, text="Chat Interface", padding=10)
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
        
        # Text widget with scrollbar - changed to white background with black text
        self.messages_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg='white',  # Changed to white background
            fg='black',  # Changed to black text
            selectbackground='#d0d0d0',  # Light gray selection
            insertbackground='black',    # Black cursor
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
        """Configure text styling tags - all changed to black for simplicity"""
        self.messages_text.tag_configure('timestamp', foreground='black', font=('Consolas', 9))
        self.messages_text.tag_configure('user', foreground='black', font=('Consolas', 11, 'bold'))
        self.messages_text.tag_configure('bot', foreground='black', font=('Consolas', 11))
        self.messages_text.tag_configure('result', foreground='black', font=('Consolas', 10))
        self.messages_text.tag_configure('path', foreground='black', font=('Consolas', 9))
        self.messages_text.tag_configure('error', foreground='black', font=('Consolas', 11))
        self.messages_text.tag_configure('success', foreground='black', font=('Consolas', 11))
    
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
            text="Search",
            command=self.send_message,
            width=12
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Focus on input
        self.input_entry.focus()
    
    def add_welcome_message(self):
        """Add welcome messages to the chat"""
        self.add_message("Chatbot Ready!", 'bot')
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
            self.add_message(f"Error browsing directory: {str(e)}", 'error')
    
    def update_file_extensions(self):
        """Update file extensions based on checkbox selection"""
        self.file_extensions = [ext for ext, var in self.file_type_vars.items() if var.get()]
        if self.file_extensions:
            self.check_directory()  # Revalidate with new extensions
    
    def check_directory(self):
        """Validate the selected directory and count files"""
        directory = self.dir_var.get().strip()
        
        if not directory:
            self.status_var.set("Please select a directory")
            return False
        
        if not os.path.exists(directory):
            self.status_var.set("Directory does not exist")
            return False
        
        try:
            file_count = 0
            selected_extensions = [ext for ext, var in self.file_type_vars.items() if var.get()]
            
            if not selected_extensions:
                self.status_var.set("Please select at least one file type")
                return False
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(file.lower().endswith(ext.lower()) for ext in selected_extensions):
                        file_count += 1
            
            self.status_var.set(f"Ready - Found {file_count} searchable files")
            self.base_dir = directory
            return True
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            return False
    
    def add_message(self, message, tag='bot'):
        """Enhanced message adding with length check"""
        # Truncate very long messages
        if len(message) > 100000:  # 100KB limit for display
            message = message[:100000] + "\n\nMessage truncated for display"
        
        self.messages_text.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Add message with appropriate tag
        self.messages_text.insert(tk.END, f"{message}\n", tag)
        
        # Limit total text widget content (keep last 1000 lines)
        line_count = int(self.messages_text.index('end-1c').split('.')[0])
        if line_count > 1000:
            self.messages_text.delete('1.0', f'{line_count-1000}.0')
        
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
        self.add_message(f"You: {query}", 'user')
        
        # Validate directory first
        if not self.check_directory():
            self.add_message("Please fix directory settings first", 'error')
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
        """Enhanced search with better phrase matching"""
        try:
            # Clean and validate query
            original_query = query.strip()
            query_lower = original_query.lower()
            
            # Extract keywords for fallback search
            keywords = [word.lower() for word in re.findall(r'\b\w+\b', original_query) if len(word) > 1]
            
            if not keywords:
                self.root.after(0, lambda: self.search_complete("Please provide meaningful search terms (2+ characters)"))
                return
            
            # Initialize counters
            exact_matches = []
            phrase_matches = []
            keyword_matches = []
            files_searched = 0
            files_skipped = 0
            files_error = 0
            selected_extensions = [ext for ext, var in self.file_type_vars.items() if var.get()]
            
            # Walk through directory
            for root, dirs, files in os.walk(self.base_dir):
                for file in files:
                    # Stop if we've searched enough files
                    if files_searched >= self.MAX_FILES_TO_SEARCH:
                        break
                        
                    # Check file extension
                    if not any(file.lower().endswith(ext.lower()) for ext in selected_extensions):
                        continue
                    
                    file_path = os.path.join(root, file)
                    
                    try:
                        # Check file size
                        file_size = os.path.getsize(file_path)
                        if file_size > self.MAX_FILE_SIZE:
                            files_skipped += 1
                            continue
                        
                        if file_size == 0:  # Skip empty files
                            continue
                        
                        files_searched += 1
                        
                        # Read and search file content
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(self.MAX_FILE_SIZE)
                            content_lower = content.lower()
                            
                            # Check for different match types with priority scoring
                            match_type = None
                            relevance_score = 0
                            
                            # 1. EXACT MATCH - Highest Priority (case-insensitive)
                            if query_lower in content_lower:
                                match_type = "exact"
                                # Count occurrences for relevance
                                relevance_score = 1000 + content_lower.count(query_lower) * 100
                                snippet = self.get_snippet_for_phrase(content, original_query)
                                
                                exact_matches.append({
                                    'path': file_path,
                                    'filename': os.path.basename(file_path),
                                    'snippet': snippet,
                                    'size': file_size,
                                    'relevance': relevance_score,
                                    'match_type': 'EXACT MATCH'
                                })
                            
                            # 2. PHRASE-LIKE MATCH - Medium Priority
                            # Check if words appear in sequence (allowing some words in between)
                            elif len(keywords) > 1 and self.check_phrase_proximity(content_lower, keywords):
                                match_type = "phrase"
                                relevance_score = 500 + sum(content_lower.count(kw) for kw in keywords) * 10
                                snippet = self.get_snippet_for_keywords(content, keywords)
                                
                                phrase_matches.append({
                                    'path': file_path,
                                    'filename': os.path.basename(file_path),
                                    'snippet': snippet,
                                    'size': file_size,
                                    'relevance': relevance_score,
                                    'match_type': 'PHRASE MATCH'
                                })
                            
                            # 3. ALL KEYWORDS MATCH - Lower Priority
                            elif all(keyword in content_lower for keyword in keywords):
                                match_type = "keywords"
                                relevance_score = sum(content_lower.count(kw) for kw in keywords) * 5
                                snippet = self.get_snippet_for_keywords(content, keywords)
                                
                                keyword_matches.append({
                                    'path': file_path,
                                    'filename': os.path.basename(file_path),
                                    'snippet': snippet,
                                    'size': file_size,
                                    'relevance': relevance_score,
                                    'match_type': 'KEYWORD MATCH'
                                })
                    
                    except Exception as e:
                        files_error += 1
                        continue
                
                # Break outer loop if limit reached
                if files_searched >= self.MAX_FILES_TO_SEARCH:
                    break
            
            # Combine results with priority: exact matches first, then phrase, then keywords
            all_results = []
            
            # Sort each category by relevance
            exact_matches.sort(key=lambda x: x['relevance'], reverse=True)
            phrase_matches.sort(key=lambda x: x['relevance'], reverse=True)
            keyword_matches.sort(key=lambda x: x['relevance'], reverse=True)
            
            # Combine in priority order
            all_results.extend(exact_matches)
            all_results.extend(phrase_matches)
            all_results.extend(keyword_matches)
            
            # Create response
            response = self.format_prioritized_results(all_results, files_searched, files_skipped, original_query, exact_matches, phrase_matches, keyword_matches)
            
            # Add debug info if there were errors
            if files_error > 0:
                response += f"\n{files_error} files couldn't be read (permissions/encoding issues)"
            
            self.root.after(0, lambda: self.search_complete(response))
            
        except Exception as e:
            error_msg = f"Search failed: {str(e)}\n"
            error_msg += "Please check your directory path and try again."
            self.root.after(0, lambda: self.search_complete(error_msg))
    
    def check_phrase_proximity(self, content, keywords):
        """Check if keywords appear in reasonable proximity (within 50 words of each other)"""
        if len(keywords) < 2:
            return False
            
        # Find positions of all keywords
        word_positions = {}
        words = content.split()
        
        for i, word in enumerate(words):
            word_clean = re.sub(r'[^\w]', '', word.lower())
            if word_clean in keywords:
                if word_clean not in word_positions:
                    word_positions[word_clean] = []
                word_positions[word_clean].append(i)
        
        # Check if we found all keywords
        if len(word_positions) != len(keywords):
            return False
        
        # Check if any combination of keyword positions are within 50 words
        first_keyword_positions = word_positions[keywords[0]]
        
        for pos1 in first_keyword_positions:
            found_all = True
            for keyword in keywords[1:]:
                found_nearby = False
                for pos2 in word_positions[keyword]:
                    if abs(pos2 - pos1) <= 50:  # Within 50 words
                        found_nearby = True
                        break
                if not found_nearby:
                    found_all = False
                    break
            if found_all:
                return True
        
        return False
    
    def get_snippet_for_phrase(self, content, phrase):
        """Get snippet that shows the exact phrase match"""
        phrase_lower = phrase.lower()
        content_lower = content.lower()
        
        # Find the first occurrence
        pos = content_lower.find(phrase_lower)
        if pos == -1:
            return content[:self.MAX_SNIPPET_LENGTH] + "..."
        
        # Get context around the phrase
        start = max(0, pos - 50)
        end = min(len(content), pos + len(phrase) + 50)
        
        snippet = content[start:end]
        
        # Clean up
        snippet = ' '.join(snippet.split())  # Remove extra whitespace
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
            
        return snippet[:self.MAX_SNIPPET_LENGTH]
    
    def get_snippet_for_keywords(self, content, keywords):
        """Get snippet that shows keyword context"""
        # Find the best section that contains multiple keywords
        sentences = re.split(r'[.!?\n]+', content)
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_lower = sentence.lower()
            score = sum(1 for kw in keywords if kw in sentence_lower)
            
            if score > best_score:
                best_score = score
                best_sentence = sentence
        
        if best_sentence:
            if len(best_sentence) > self.MAX_SNIPPET_LENGTH:
                return best_sentence[:self.MAX_SNIPPET_LENGTH-3] + "..."
            return best_sentence
        
        # Fallback to first keyword context
        for keyword in keywords:
            pos = content.lower().find(keyword)
            if pos != -1:
                start = max(0, pos - 50)
                end = min(len(content), pos + len(keyword) + 50)
                context = content[start:end]
                context = ' '.join(context.split())
                
                if start > 0:
                    context = "..." + context
                if end < len(content):
                    context = context + "..."
                    
                return context[:self.MAX_SNIPPET_LENGTH]
        
        return content[:self.MAX_SNIPPET_LENGTH] + "..."
    
    def format_prioritized_results(self, results, files_searched, files_skipped, query, exact_matches, phrase_matches, keyword_matches):
        """Format results with clear priority indication"""
        response_parts = []
        current_length = 0
        
        # Header with search summary
        header = f"SEARCH RESULTS\n"
        header += f"Query: '{query}'\n"
        header += f"Files searched: {files_searched}"
        if files_skipped > 0:
            header += f" (skipped {files_skipped} large files)"
        header += f"\n\n MATCH SUMMARY:\n"
        header += f"  Exact matches: {len(exact_matches)}\n"
        header += f"  Phrase matches: {len(phrase_matches)}\n"
        header += f"  Keyword matches: {len(keyword_matches)}\n"
        header += f"  Total matches: {len(results)}\n"
        header += "=" * 60 + "\n\n"
        
        response_parts.append(header)
        current_length += len(header)
        
        if results:
            displayed_count = 0
            for i, result in enumerate(results, 1):
                if displayed_count >= self.MAX_RESULTS_DISPLAY:
                    break
                
                # Format file size nicely
                size_bytes = result['size']
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes/1024:.1f} KB"
                else:
                    size_str = f"{size_bytes/(1024*1024):.1f} MB"
                
                # Match type indicator
                match_indicator = "[EXACT]" if result['match_type'] == 'EXACT MATCH' else "[PHRASE]" if result['match_type'] == 'PHRASE MATCH' else "[KEYWORD]"
                
                # Create result entry
                result_text = f"[{i}] {match_indicator} {result['match_type']} - {result['filename']}\n"
                result_text += f"    Path: {result['path']}\n"
                result_text += f"    Size: {size_str}\n"
                result_text += f"    Content: {result['snippet']}\n"
                result_text += "-" * 60 + "\n\n"
                
                # Check length limit
                if current_length + len(result_text) > self.MAX_TOTAL_RESPONSE_LENGTH:
                    response_parts.append("More results available but truncated to save space...\n")
                    break
                
                response_parts.append(result_text)
                current_length += len(result_text)
                displayed_count += 1
            
            # Summary of remaining results
            if len(results) > displayed_count:
                remaining = len(results) - displayed_count
                summary = f"\n{remaining} additional matches not shown.\n"
                if len(exact_matches) > 0:
                    summary += "Exact matches are shown first for best relevance.\n"
                response_parts.append(summary)
                
        else:
            no_results = "No files found matching your search.\n\n"
            no_results += "Suggestions:\n"
            no_results += "  • Try different or fewer keywords\n"
            no_results += "  • Check if file types are selected\n"
            no_results += "  • Verify the directory path is correct\n"
            no_results += "  • Check spelling of search terms\n"
            response_parts.append(no_results)
        
        return ''.join(response_parts)
    
    def search_complete(self, message):
        """Handle search completion"""
        self.add_message(message, 'result')
        self.searching = False
        self.send_button.config(state='normal', text="Search")
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
        print("Tkinter is not available. Please install tkinter or use the command-line version.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Failed to start application: {e}")
        print("Try running the command-line version instead.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    
    main()