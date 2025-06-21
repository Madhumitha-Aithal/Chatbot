🛰️ Radar System Chatbot

A secure, terminal-based AI chatbot that interacts with radar system data by searching and interpreting `.txt` and `.dat` files across deeply nested directories (up to 10 levels). Designed for environments where browser-based tools and databases are not viable.

 🚀 Features

✅ Terminal-based interface — no browser required
🔍 Recursively scans multi-level directories
📂 Reads `.txt` and `.dat` files with UTF-8 encoding
🧠 Uses keyword-based matching for fast retrieval
🔒 Safe: ignores unreadable or binary files
📝 Logs nothing outside the designated directory

---

🛡️ Safety & Security

* Operates within a sandboxed folder
* Handles unreadable files gracefully
* No internet access or external dependencies
* No database connection or persistent storage

💡 How It Works

1. User enters a query like `"signal strength"`
2. Chatbot tokenizes input and scans all text-based files
3. Returns top matching file paths with a preview snippet


🛠️ Requirements

* Python 3.7+
* UTF-8 encoded `.txt` or `.dat` files in `radar_data/`


▶️ Running the Chatbot

python radar_chatbot.py

