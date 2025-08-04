# 🧳 AI Itinerary Assistant

An AI-powered travel itinerary generator that creates **personalized multi-day travel plans** based on user input.  
Built with **Python**, **Flask**, and **OpenAI API**, this project demonstrates **prompt engineering** and **AI integration**.

---

## 🚀 Features
- ✅ Generate **customized travel itineraries** with activities, locations, and dining suggestions.
- ✅ Uses **OpenAI API** for natural language processing and dynamic response generation.
- ✅ Supports **Command-Line Interface (CLI)** and **Web UI (Flask)** modes.
- ✅ Easy to deploy (local or cloud via Render/Heroku).

---

## 🗂️ Project Structure
```
├── Chatbot.py          # Main application (Flask server or CLI)
├── templates/          # HTML templates for web interface
├── static/             # Static assets (CSS, JS)
├── requirements.txt    # Python dependencies
└── render.yaml         # Deployment configuration for Render
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-itinerary-assistant.git
cd ai-itinerary-assistant
```

### 2. Create a Virtual Environment (Optional)
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your_api_key_here"
```

---

## ▶️ Usage

### **Run in CLI Mode**
```bash
python Chatbot.py
```
Enter your travel preferences and receive an AI-generated itinerary directly in the terminal.

### **Run with Flask (Web UI)**
```bash
python Chatbot.py
```
Then open:
```
http://127.0.0.1:5000
```

---

## 🌐 Deployment
---
https://chatbot-travel-guide.onrender.com
---

## 🛠️ Tech Stack
- **Python 3.x**
- **Flask**
- **OpenAI API**
- **HTML/CSS (Web UI)**

---

## 📌 Future Improvements
- 🌍 Add user options (budget, travel style, number of days)
- 🗂️ Store itineraries in a database (PostgreSQL)
- 🎨 Improve UI with React or Bootstrap
- ☁️ Deploy a production-ready version with secure API key handling

---

## 👤 Author
**Elly Woo**  
Full-stack developer passionate about AI and sustainable technology.
