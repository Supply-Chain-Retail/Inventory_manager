# OmniOpt AI — Predictive Logistics & Fulfillment Platform

OmniOpt AI is an AI-powered predictive inventory management and logistics platform designed to optimize stock availability, demand forecasting, and warehouse operations across multiple regional hubs. The system leverages Artificial Intelligence, Machine Learning, and real-time WebSockets to predict future product demand, automate inventory replenishment, and improve supply chain efficiency.

By combining **HistGradientBoosting Regressor** machine learning models, real-time WebSocket communication, geographic map visualization (Leaflet.js), and intelligent inventory analytics, OmniOpt AI helps businesses reduce stockouts, minimize overstocking, and improve operational decision-making.

---

## 🌟 Key Features

### 📈 Predictive Demand Forecasting
- Forecast future product demand using **HistGradientBoosting Regressor** (`scikit-learn`).
- Predict inventory requirements with high accuracy ($R^2$ scores, MAE, RMSE metrics).
- Incorporates dynamic Indian festival season demand multipliers (Diwali, Durga Puja, Ganesh Chaturthi, Raksha Bandhan).
- Reduces stock shortages and excess holding inventory.

### 📦 Smart Inventory Management
- Monitor stock levels across multiple regional warehouse hubs (North, South, East, West).
- Automatically identify low-stock products and trigger AI stock rebalancing transfers.
- Generate factory replenishment requests when regional inventory dips below safety thresholds.

### ⚡ Real-Time Synchronization & WebSockets
- Live inventory updates using **FastAPI WebSockets** without needing page refreshes.
- Real-time stock movement synchronization between warehouses and active transit tracking.

### 🗺️ Geographic Logistics & Transit Routing
- Route shipments efficiently across regional hubs.
- Display real-time warehouse locations on interactive Leaflet maps with OSRM routing.

---

## 👥 System Modules & Team Responsibilities

| System Module | Team Member | Responsibilities |
| :--- | :--- | :--- |
| **Integration Engineer** | **Akash.M** | Managed the overall project, integrated frontend, backend, ML, and database modules, and ensured smooth system functionality. |
| **Frontend Development** | **Agalya.B** | Designed and developed the user interface, dashboards, charts, and responsive web pages for real-time monitoring. |
| **Backend Development** | **Afrid Ahamed.B** | Developed REST APIs using FastAPI, handled business logic, integrated WebSockets for real-time communication, and connected frontend with ML and database modules. |
| **ML Engineer** | **Abisheak.B** | Built demand forecasting models, performed data preprocessing, feature engineering, model training, and prediction. |
| **Database Management** | **Akash.M** | Designed and managed the database, handled inventory and transaction data, and ensured efficient data storage and retrieval. |

---

## 🏗️ System Architecture

```text
E-Commerce Platforms
(Amazon • Flipkart • Meesho • Myntra)
          │
          ▼
Data Collection & Persistence Layer (InventoryDatabase)
          │
          ▼
Data Preprocessing & Feature Engineering Layer
          │
          ▼
AI Prediction Engine (DemandForecaster)
 ├── HistGradientBoosting Regressor (Scikit-Learn)
 ├── Seasonality & Festival Multipliers
 ├── Inventory Optimization
 └── Stock Replenishment
          │
          ▼
Real-Time WebSocket Synchronization (ConnectionManager)
          │
          ▼
Interactive Dashboard (HTML5 • Tailwind CSS • Chart.js • Leaflet.js)
```

---

## 🛠️ Tech Stack

### Frontend
- **HTML5 & Vanilla JavaScript** (Zero build overhead, high-performance DOM execution)
- **Tailwind CSS** (Responsive UI design, modern card components)
- **Chart.js** (Visual analytics & 30-day forecast graphs)
- **Leaflet.js** (Interactive geographic warehouse map tracking)

### Backend & Object-Oriented Architecture
- **FastAPI** (Asynchronous Python REST API framework)
- **Uvicorn** (ASGI Web Server)
- **WebSockets** (Real-time bi-directional streaming)
- **Object-Oriented Design**: `InventoryDatabase`, `DemandForecaster`, `ConnectionManager`

### AI & Machine Learning
- **Scikit-learn** (`HistGradientBoostingRegressor`, `OneHotEncoder`, `ColumnTransformer`, `Pipeline`)
- **Pandas & NumPy** (Feature engineering, rolling time-series aggregation, data cleaning)

---

## 📂 Project Structure

```text
OmniOpt AI
│
├── main.py              # FastAPI server & Object-Oriented Application (InventoryDatabase, DemandForecaster)
├── index.html           # Interactive Frontend UI (Tailwind CSS, Leaflet Maps, Chart.js)
├── inventory_db.json    # Local JSON database (1,450 e-commerce records)
├── requirements.txt     # Python dependencies (FastAPI, Scikit-learn, Pandas, Uvicorn, WebSockets)
├── .python-version      # Python runtime version configuration (3.11.9)
├── .gitignore           # Git ignore rule specifications
├── README.md            # Project documentation
├── Document/            # Project documentation (.docx)
└── presentation/        # Project presentation slides (.pptx)
```

---

## 📜 License

This project is licensed under the **MIT License**.
