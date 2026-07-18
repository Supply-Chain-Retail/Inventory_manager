# OmniOpt AI — Predictive Logistics & Fulfillment Platform

OmniOpt AI is a modern, enterprise-grade inventory intelligence and predictive logistics platform designed to optimize e-commerce supply chain operations. By utilizing a hybrid machine learning model for demand forecasting and real-time transit routing, it enables automated inter-hub inventory rebalancing and weather-driven safety stock adjustments.

---

## 🚀 Key Features

*   **Ensemble Demand Forecasting:** Utilizes a custom Hybrid Ensemble Regressor (**HistGradientBoosting** + **RandomForest**) trained on historical multi-platform retail data, achieving a high prediction accuracy of **$R^2 = 0.946$** (94.6%).
*   **Active Transit & Restock Countdown Tracking:** Simulated real-time tracking panel showing shipments currently in transit (e.g., Factory Restocks or Inter-Hub Transfers) with active progress bars. Stock is only committed to the database once the countdown finishes.
*   **Low Stock & Direct Factory Replenishment:** Auto-detects under-stocked hubs and matches them with regional surplus hubs for stock transfers. If no surplus exists, it automatically triggers a direct factory replenishment request.
*   **Real-Time Weather Telemetry:** Integrates the Open-Meteo API to calculate weather-driven demand multipliers (e.g., rainfall increases clothing/umbrella demand, extreme heat increases grocery/beverage demand) in real-time.
*   **E-Commerce Live Sales Simulator:** Simulates real-time e-commerce purchases streaming in every 3 seconds from major platforms (Amazon, Flipkart, Meesho, Myntra), decrementing physical stock and trigger-retraining the ML model.
*   **Geographic Route Engine:** Displays fulfillment centers and calculates road-route geometries using Leaflet.js with high-contrast, premium CartoDB Positron maps (all labels in English).

---

## 🛠️ Technology Stack

*   **Frontend:** HTML5, TailwindCSS, JavaScript (ES6+), Leaflet.js (Mapping), Chart.js (Data Visualization), WebSockets (Real-Time Sync).
*   **Backend:** FastAPI, Uvicorn, Pandas, NumPy, Scikit-Learn, LightGBM, Asyncio.
*   **Database:** Portable JSON cache (`inventory_db.json`) with an automatic static JSON fallback for static web hosting.

---

## ⚙️ Local Development Setup

To run the project locally on your machine, follow these steps:

### 1. Clone the repository
```bash
git clone https://github.com/Supply-Chain-Retail/Inventory_manager.git
cd Inventory_manager
```

### 2. Set up a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or: .venv\Scripts\activate  # On Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Backend API
Start the FastAPI server on port 8000:
```bash
uvicorn main:app --reload
```
The backend will load the data, train the forecast pipeline, and serve endpoints on `http://127.0.0.1:8000` (including WebSockets on `/ws`).

### 5. Launch the Dashboard
Simply open the local `index.html` file in your web browser (or run a local static server). Because the backend is running locally, the dashboard will connect via WebSockets and display **`ONLINE (Real-Time WS)`**.

---

## 🌐 Production Deployment

This project is configured for cloud deployment:
1.  **Frontend:** Deployed statically on **GitHub Pages**. If the backend server goes offline or is inaccessible, the frontend automatically falls back to fetching `./inventory_db.json` statically to keep the dashboard interactive.
2.  **Backend:** Hosted as a Web Service on **Render** (linked via WebSockets).
