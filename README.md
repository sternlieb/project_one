# Question & Answer Web Application

A simple full-stack web application where users can ask questions and receive responses from a server.

## 🚀 Features

- **Client Side**: Clean, responsive web interface
- **Server Side**: Python Flask API
- **Real-time Communication**: Client-server communication via HTTP requests
- **Interactive UI**: Question input, answer display, and reset functionality
- **Error Handling**: Comprehensive error handling and user feedback

## 📁 Project Structure

```
project_one/
├── client/                 # Frontend files
│   ├── index.html         # Main HTML file
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── script.js      # Client-side JavaScript
├── server/                # Backend files
│   ├── main.py           # Flask server
│   └── requirements.txt  # Python dependencies
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.7+ installed on your system
- A modern web browser

### 1. Install Python Dependencies

Navigate to the server directory and install the required packages:

```bash
cd server
pip install -r requirements.txt
```

### 2. Start the Server

Run the Flask server:

```bash
python main.py
```

The server will start on `http://localhost:5000`

You should see:
```
🚀 Question & Answer Server Starting...
📡 Server will run on: http://localhost:5000
🔄 CORS enabled for client communication
```

### 3. Open the Client

Open the client-side application by opening `client/index.html` in your web browser:

**Option 1: Double-click the file**
- Navigate to the `client` folder
- Double-click `index.html`

**Option 2: From terminal**
```bash
cd client
open index.html  # On macOS
# or
start index.html  # On Windows
# or
xdg-open index.html  # On Linux
```

## 🎯 How to Use

1. **Start the Server**: Make sure the Python server is running on port 5000
2. **Open the Client**: Load the HTML file in your browser
3. **Ask a Question**: Type any question in the text area
4. **Get an Answer**: Click "Send Question" - the server will respond with "answer"
5. **Reset**: Click "Reset" to clear both text areas and ask a new question

## 🔧 API Endpoints

The server provides the following endpoints:

- **GET /**: Server information
- **GET /health**: Health check
- **POST /ask**: Send a question, receive an answer
  - Request: `{"question": "your question here"}`
  - Response: `{"answer": "answer", "question": "your question", "timestamp": "..."}`

## 🚨 Troubleshooting

**"Server is not running" error:**
- Make sure you've installed the Python dependencies: `pip install -r requirements.txt`
- Ensure the server is running: `python main.py`
- Check that the server is accessible at `http://localhost:5000`

**CORS errors:**
- The server includes CORS headers, but if you're still getting errors, make sure you're opening the HTML file directly (not through a file:// URL in some cases)

**Dependencies not found:**
```bash
cd server
pip install Flask Flask-CORS
```

## 🎨 Customization

You can easily customize the application:

- **Change the answer**: Edit the `answer = "answer"` line in `server/main.py`
- **Modify styling**: Edit `client/css/style.css`
- **Add features**: Extend `client/js/script.js` and `server/main.py`

## 📝 Development

To make changes:

1. Edit the files as needed
2. Restart the server if you changed Python code
3. Refresh the browser if you changed client-side code
4. Commit your changes:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push
   ```

## 🤝 Contributing

1. Make your changes
2. Test both client and server
3. Commit and push to GitHub

---

Built with ❤️ using HTML, CSS, JavaScript, and Python Flask
