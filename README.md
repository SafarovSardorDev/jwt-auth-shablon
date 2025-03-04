# JWT Authentication API

This project implements JWT authentication using Django Rest Framework (DRF) and Simple JWT. It provides secure user authentication and token-based access control.

## 🚀 Features
- User registration with JWT authentication
- Login and token generation
- Refresh token functionality
- Secure API endpoints with authentication
- Google OAuth integration

---

## 📌 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/jwt-auth.git
cd jwt-auth
```

### 2️⃣ Create & Activate Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run Migrations
```bash
python manage.py migrate
```

### 5️⃣ Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6️⃣ Run the Server
```bash
python manage.py runserver
```

---

## 🔑 API Endpoints

### 📝 Authentication

#### 🔹 Register a New User
```http
POST /auth/register/
```
**Request Body:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "phone": "+998901234567",
  "password": "testpassword"
}
```

#### 🔹 Login and Get JWT Token
```http
POST /auth/login/
```
**Request Body:**
```json
{
  "username": "testuser",
  "password": "testpassword"
}
```
**Response:**
```json
{
  "access": "JWT_ACCESS_TOKEN",
  "refresh": "JWT_REFRESH_TOKEN"
}
```

#### 🔹 Refresh Access Token
```http
POST /auth/token/refresh/
```
**Request Body:**
```json
{
  "refresh": "JWT_REFRESH_TOKEN"
}
```

---

### 📝 User Profile (Protected Route)
#### 🔹 Get User Profile
```http
GET /api/users/profile/
```
**Headers:**
```http
Authorization: Bearer JWT_ACCESS_TOKEN
```
**Response:**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "phone": "+998901234567"
}
```

---

## 🔧 Technologies Used
- **Python** & **Django**
- **Django Rest Framework (DRF)**
- **Simple JWT**
- **Google OAuth2**

---

## 🎯 Contribution
1. Fork the repository 🍴
2. Create a new branch 🌿
3. Commit changes ✨
4. Push to your branch 🚀
5. Create a pull request 🔥

---

## 📜 License
This project is licensed under the MIT License.

---

### ⭐ Don't forget to star the repo if you found it useful! ⭐

