# Personal Stock Portfolio Tracker

**Stock Portfolio tracker** is a full-stack web application built with **Python**, **Flask**, **SQLite**, and **Vanilla JavaScript**. It simulates managing a personal stock portfolio by letting users register, log in, look up real‑time quotes, buy and sell shares, and review their transaction history.

The idea originated from a **finance learning project** in the CS50 introduction to Computer Science Course.

---

## 🚀 Features

- 🐍 Backend powered by **Flask**  
- 🔐 **User Authentication** with secure password hashing (`werkzeug.security`)  
- 📊 **Real‑time Stock Quotes** via the Alpha Vantage API  
- 🛒 **Buy & Sell Functionality** that updates user cash balance and portfolio  
- 🧾 **Transaction History** logging buys and sells in a `history` table  
- 🛢️ **SQLite** database schema organized into `users`, `owned_stocks`, and `history`  
- 💾 **Persistent Sessions** using Flask‑Session (filesystem backend)  
- 🧹 **Input Validation & Error Handling** with custom apology pages  

---

## ⚙️ Installation & Setup

### 📋 Prerequisites

- Python 3.8 or higher  
- `pip` (Python package installer)  
- SQLite3 (CLI tool or GUI client)  
- Alpha Vantage API key (free from [Alpha Vantage](https://www.alphavantage.co/))

### 📥 Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/JB007z/Finance.git
   cd stockwise
2. **Install dependencies**  
pip install -r requirements.txt

3. **Create and initialize the database**  
sqlite3 finance.db < schema.sql

4. **Configure environment variables**  
Create a `.env` file with:  
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key  
FLASK_APP=app.py  
FLASK_ENV=development

5. **Start the development server**  
flask run

---

## 🚧 Known Issues

- ⚠️ **API Rate Limits**: Alpha Vantage free tier allows only 5 calls/minute and 500 calls/day  
- 🔄 **No Live Updates**: Stock prices require manual page refresh  
- 💳 **Simulated Transactions**: No real funds are exchanged  
- 📈 **Basic UI/UX**: Minimal styling; may not be fully responsive on all devices  
- 🔑 **“Forgot Password”**: Password reset feature is not implemented  
