# Mini CRM - Backend (FastAPI)

## 🚀 Overview
This is the **Backend** for the Mini CRM system, built with **FastAPI**.  
It exposes REST APIs for managing customers, campaigns, orders, and analytics.

---

## 🛠️ Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/mini-crm-backend.git
   cd mini-crm-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate    # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   uvicorn main:app --reload
   ```

5. Open API docs in browser:
   ```
   http://localhost:8000/docs
   ```

---

## ☁️ Deployment on Render

1. Push your code to GitHub.

2. Go to [Render.com](https://render.com).

3. Create a new **Web Service**:
   - Select your **backend repo**.
   - Runtime: **Python 3.9+**
   - Build Command:  
     ```bash
     pip install -r requirements.txt
     ```
   - Start Command:  
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

4. Configure environment variables (e.g., DATABASE_URL).

5. Deploy 🚀

6. Access backend at:
   ```
   https://your-backend.onrender.com
   ```
