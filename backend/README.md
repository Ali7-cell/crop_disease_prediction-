---
title: Agrilux - AI-Powered Smart Farming Assistant
emoji: 🌾
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# Agrilux API — AI-Powered Smart Farming Assistant


Agrilux is a smart farming backend application designed to assist farmers and agricultural consultants. It leverages Machine Learning models to make predictions for crops, fertilizers, and crop yields based on soil composition, weather, and historical data.

---

## 🚀 Features

- **Crop Prediction**: Recommends the optimal crop to plant based on soil Nitrogen (N), Phosphorus (P), Potassium (K), temperature, humidity, pH, and rainfall.
- **Fertilizer Recommendation**: Recommends the best fertilizer based on soil conditions, crop types, and current moisture levels.
- **Yield Prediction**: Predicts crop yield (in hg/ha) for various crop items across 98 countries using regression models.
- **User Authentication**: Secure JWT-based registration and login system.
- **Prediction History**: Saves all predictions to a PostgreSQL/Neon database, allowing farmers to query past logs with pagination and filters.
- **Profile Management**: Permits users to retrieve and update their profiles securely.

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database**: [PostgreSQL (Neon)](https://neon.tech/) & [SQLAlchemy ORM](https://www.sqlalchemy.org/)
- **Machine Learning**: [Scikit-Learn](https://scikit-learn.org/) & [Joblib](https://joblib.readthedocs.io/)
- **Authentication**: JWT (JSON Web Tokens) with `python-jose` & `passlib`

---

## 📦 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Ali7-cell/crop_disease_prediction-.git
   cd crop_disease_prediction-
   ```

2. **Install Dependencies**:
   Ensure Python 3.10+ is installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory (refer to `.env.example`):
   ```env
   JWT_SECRET=your_jwt_secret_key
   JWT_EXPIRE_MINUTES=60
   DB_URL=postgresql://user:pass@host/dbname?sslmode=require
   CORS_ORIGIN=http://localhost:3000
   ```

4. **Run the Application**:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

---

## 🧪 API Verification & Testing

A verification script `test_endpoints.py` is included to test all endpoints. You can run it to verify functionality:
```bash
python test_endpoints.py
```
