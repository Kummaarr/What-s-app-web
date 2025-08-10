# WhatsApp Web Clone — FastAPI + React (Render-ready)

## 📌 Overview
A WhatsApp Web–like clone with:
- **FastAPI backend** + **Socket.IO** for real-time chat
- **React (Vite)** frontend styled like WhatsApp Web
- **MongoDB** for storing messages & statuses
- **One-click Render deployment** (frontend + backend in one service)
- **Auto sample data loader** on first deploy

---

## 🖥 1. Run Locally

### Requirements
- Python **3.10+**
- Node.js **16+**
- MongoDB running locally or Atlas URI

### Steps
```bash
# 1. Unzip the project
unzip whatsapp_web_clone_hybrid.zip
cd whatsapp_web_clone_hybrid

# 2. Install frontend
cd frontend
npm install
npm run build
cd ..

# 3. Install backend
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 4. Copy frontend build into backend/static
mkdir -p static
cp -r ../frontend/dist/* ./static/

# 5. (Optional) Load sample data
python load_sample_data.py

# 6. Run the backend server
uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
