# ==============================================================================
# PROJECT: OmniOpt AI - Predictive Logistics & Fulfillment Platform
# MODULE: System Architecture & Integration Setup
# RESPONSIBLE ENGINEER: Akash.M (System Integration)
# ==============================================================================

from fastapi import FastAPI, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import HistGradientBoostingRegressor
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

app = FastAPI(title="OmniOpt AI Logistics Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory_db.json")


# ==============================================================================
# MODULE: Database Management & Persistence Layer
# RESPONSIBLE ENGINEER: Akash.M (Database Management)
# DESCRIPTION: Manages database initialization, e-commerce data seeding, 
# in-memory store management, and disk JSON persistence.
# ==============================================================================
class InventoryDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.records: List[Dict[str, Any]] = []
        self.load_or_seed()

    def load_or_seed(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    self.records = json.load(f)
                    if len(self.records) > 0:
                        print(f"✅ Loaded {len(self.records)} records from database cache.")
                        return
            except Exception as e:
                print(f"⚠️ Read from cache failed: {e}")

        # Seed initial dataset if missing
        print("🌱 Seeding realistic e-commerce datasets (Amazon, Flipkart, Meesho, Myntra)...")
        platforms = {
            "Amazon": {"regions": ["North", "South", "East", "West"], "categories": ["Grocery", "Electronics"]},
            "Flipkart": {"regions": ["North", "South", "East", "West"], "categories": ["Electronics", "Furniture"]},
            "Meesho": {"regions": ["North", "South", "East", "West"], "categories": ["Clothing", "Grocery"]},
            "Myntra": {"regions": ["North", "South", "East", "West"], "categories": ["Clothing"]}
        }
        
        products = {
            "Grocery": [("Amazon Pantry Wheat Flour 5kg", 340.0), ("Tata Tea Premium 1kg", 450.0), ("Chocoholic Hazelnut Spread 350g", 380.0)],
            "Electronics": [("iPhone 15 Pro Max 256GB", 145000.0), ("Mi Power Bank 20000mAh", 2100.0), ("boAt Rockerz Bluetooth Headset", 1600.0)],
            "Clothing": [("Roadster Slim Fit Denim Shirt", 1200.0), ("Puma Cotton Crew Neck T-Shirt", 990.0), ("Myntra Designer Silk Saree", 4500.0)],
            "Furniture": [("Solid Wood Study Desk", 13500.0), ("Ergonomic High Back Mesh Chair", 8500.0), ("Duroflex 3-Seater Recliner Sofa", 24900.0)]
        }
        
        start_date = datetime.now() - timedelta(days=60)
        seed = []
        for _ in range(200):
            plat = random.choice(list(platforms.keys()))
            cat = random.choice(platforms[plat]["categories"])
            reg = random.choice(platforms[plat]["regions"])
            p_name, p_price = random.choice(products[cat])
            
            date = start_date + timedelta(days=random.randint(0, 59))
            day_of_week = date.weekday()
            week_mult = 1.30 if day_of_week in [4, 5, 6] else 0.85
            
            base_sales = {"Grocery": 35, "Clothing": 16, "Electronics": 4, "Furniture": 3}[cat]
            expected = base_sales * week_mult * (1.1 if plat in ["Amazon", "Myntra"] else 0.9)
            units_sold = int(max(1, round(random.gauss(expected, expected * 0.15))))
            
            inv = units_sold + random.randint(15, 60)
            store_num = random.randint(1, 3)
            store_id = f"{plat}-{reg[:3].upper()}-{store_num}"
            
            seed.append({
                "Date": date.strftime("%Y-%m-%d"),
                "Store_ID": store_id,
                "Product_ID": p_name,
                "Category": cat,
                "Region": reg,
                "Inventory_Level": inv,
                "Units_Sold": units_sold,
                "Price": p_price
            })
            
        self.records = sorted(seed, key=lambda x: x["Date"], reverse=True)
        self.save_to_disk()

    def save_to_disk(self):
        try:
            with open(self.db_path, "w") as f:
                json.dump(self.records, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to cache database to disk: {e}")

    def get_stock(self, region: str, category: str) -> int:
        for item in self.records:
            if item.get("Region") == region and item.get("Category") == category:
                return int(item.get("Inventory_Level", 0))
        return 0

    def add_record(self, record: Dict[str, Any]):
        self.records.insert(0, record)
        self.save_to_disk()


# ==============================================================================
# MODULE: Machine Learning Demand Forecasting Engine
# RESPONSIBLE ENGINEER: Abisheak.B
# DESCRIPTION: Manages ML pipelines, feature engineering, seasonality adjustments,
# HistGradientBoostingRegressor model training, and dynamic demand forecasting.
# ==============================================================================
# ==============================================================================
# MODULE: ML Demand Forecasting Engine
# RESPONSIBLE ENGINEER: Abisheak.B (ML Demand Forecasting)
# ==============================================================================
class DemandForecaster:
    FESTIVALS = [
        {"name": "Raksha Bandhan", "date": "2026-08-28", "categories": ["Grocery", "Clothing"], "lift": 1.40},
        {"name": "Ganesh Chaturthi", "date": "2026-09-14", "categories": ["Grocery", "Furniture"], "lift": 1.35},
        {"name": "Durga Puja / Dussehra", "date": "2026-10-20", "categories": ["Clothing", "Electronics", "Grocery"], "lift": 1.55},
        {"name": "Dhanteras & Diwali", "date": "2026-11-08", "categories": ["Electronics", "Clothing", "Grocery", "Furniture"], "lift": 1.65}
    ]

    def __init__(self):
        self.pipeline: Pipeline = None
        self.model_info: Dict[str, Any] = {
            "model_name": "HistGradientBoosting Regressor",
            "best_params": {"learning_rate": 0.08, "max_depth": 4, "max_iter": 120},
            "metrics": {"r2": 0.0, "mae": 0.0, "rmse": 0.0},
            "status": "NOT_TRAINED",
            "total_records": 0
        }

    def get_festival_multiplier(self, date_obj: datetime, category: str) -> float:
        for f in self.FESTIVALS:
            f_date = datetime.strptime(f["date"], "%Y-%m-%d")
            if f_date - timedelta(days=7) <= date_obj <= f_date:
                if category in f["categories"]:
                    return f["lift"]
        return 1.0

    def train(self, records: List[Dict[str, Any]]):
        if len(records) < 15:
            self.model_info["status"] = "ERROR: Insufficient data points (needs >= 15)"
            return
            
        try:
            df = pd.DataFrame(records)
            df['Date'] = pd.to_datetime(df['Date'])
            df_clean = df[(df['Date'].dt.year >= 2026) & (df['Store_ID'].str.startswith('AI-AUTO') == False)].copy()
            if len(df_clean) < 15:
                df_clean = df.copy()

            df_clean['Month'] = df_clean['Date'].dt.month
            df_clean['DayOfWeek'] = df_clean['Date'].dt.dayofweek
            df_clean['DayOfMonth'] = df_clean['Date'].dt.day

            df_sorted = df_clean.sort_values('Date')
            df_sorted['Category_Region_Mean'] = df_sorted.groupby(['Category', 'Region'])['Units_Sold'].transform(
                lambda x: x.expanding().mean().shift(1)
            ).fillna(df_sorted['Units_Sold'].mean())

            df_shuffled = df_sorted.sample(frac=1, random_state=42).reset_index(drop=True)
            split_idx = int(len(df_shuffled) * 0.8)
            train_df = df_shuffled.iloc[:split_idx]
            test_df = df_shuffled.iloc[split_idx:]

            features = ['Category', 'Region', 'Price', 'Inventory_Level', 'Month', 'DayOfWeek', 'DayOfMonth', 'Category_Region_Mean']
            X_train, y_train = train_df[features], train_df['Units_Sold']
            X_test, y_test = test_df[features], test_df['Units_Sold']

            preprocessor = ColumnTransformer(
                transformers=[('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['Category', 'Region'])],
                remainder='passthrough'
            )
            preprocessor.set_output(transform="pandas")

            regressor = HistGradientBoostingRegressor(learning_rate=0.08, max_depth=4, max_iter=120, random_state=42)
            eval_pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('regressor', regressor)])
            eval_pipeline.fit(X_train, y_train)
            preds = eval_pipeline.predict(X_test)

            cand_r2 = r2_score(y_test, preds)
            cand_mae = mean_absolute_error(y_test, preds)
            cand_rmse = np.sqrt(mean_squared_error(y_test, preds))

            self.pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('regressor', regressor)])
            self.pipeline.fit(df_sorted[features], df_sorted['Units_Sold'])

            self.model_info = {
                "model_name": "HistGradientBoosting Regressor",
                "best_params": {"selected_algorithm": "HistGradientBoosting Regressor", "learning_rate": 0.08, "max_depth": 4, "max_iter": 120},
                "metrics": {"r2": round(max(0, float(cand_r2)), 4), "mae": round(float(cand_mae), 2), "rmse": round(float(cand_rmse), 2)},
                "status": "ONLINE (Active - HistGradientBoosting Regressor)",
                "total_records": len(df_clean)
            }
            print(f"✅ ML Model Trained: R2={self.model_info['metrics']['r2']}")
        except Exception as e:
            self.model_info["status"] = f"ERROR: Training failed ({str(e)})"
            print(f"❌ ML Training Error: {e}")

    def predict_future_demand(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.DataFrame(records)
        if len(df) == 0:
            return []

        df['Date'] = pd.to_datetime(df['Date'])
        tomorrow = datetime.now() + timedelta(days=1)
        cat_reg_means = df.groupby(['Category', 'Region'])['Units_Sold'].mean().to_dict()
        global_mean = df['Units_Sold'].mean()

        grouped = df.groupby(['Region', 'Category']).agg({'Price': 'mean', 'Inventory_Level': 'last', 'Units_Sold': 'mean'}).reset_index()
        forecasts = []

        for _, row in grouped.iterrows():
            reg, cat = row['Region'], row['Category']
            price, inv, avg_sold = float(row['Price']), int(row['Inventory_Level']), float(row['Units_Sold'])

            if self.pipeline is not None:
                cr_mean = cat_reg_means.get((cat, reg), global_mean)
                input_df = pd.DataFrame([{
                    'Category': cat, 'Region': reg, 'Price': price, 'Inventory_Level': inv,
                    'Month': tomorrow.month, 'DayOfWeek': tomorrow.weekday(), 'DayOfMonth': tomorrow.day,
                    'Category_Region_Mean': cr_mean
                }])
                try:
                    pred = max(0.0, float(self.pipeline.predict(input_df)[0]))
                except Exception:
                    pred = avg_sold * 1.15
            else:
                pred = avg_sold * 1.15

            pred = pred * self.get_festival_multiplier(tomorrow, cat)
            forecasts.append({
                "Region": reg, "Category": cat, "Projected_Demand": round(pred, 2),
                "Avg_Historical_Sales": round(avg_sold, 2), "Current_Inventory": inv, "Price": price
            })
        return forecasts


# Global Instances
db = InventoryDatabase()
forecaster = DemandForecaster()


# ==============================================================================
# MODULE: Backend API Development & Real-Time Communications
# RESPONSIBLE ENGINEER: Afrid Ahamed.B
# DESCRIPTION: Manages WebSocket client connections, REST API endpoints, 
# asynchronous background tasks, and real-time state broadcasting.
# ==============================================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()
main_loop = None

async def broadcast_state_update():
    try:
        payload = {
            "type": "update",
            "inventory": db.records,
            "forecast": forecaster.predict_future_demand(db.records),
            "model_info": forecaster.model_info
        }
        await manager.broadcast(payload)
    except Exception as e:
        print(f"❌ Broadcast Error: {e}")

@app.on_event("startup")
async def startup_event():
    global main_loop
    import asyncio
    main_loop = asyncio.get_running_loop()
    forecaster.train(db.records)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({"type": "status", "data": "CONNECTED"})
        forecast = forecaster.predict_future_demand(db.records)
        await websocket.send_json({"type": "update", "inventory": db.records, "forecast": forecast, "model_info": forecaster.model_info})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/status")
async def check_db():
    return {"status": "ONLINE"}

@app.get("/api/inventory")
async def get_inventory():
    return db.records

@app.post("/api/inventory")
async def save_inventory(request: Request, background_tasks: BackgroundTasks):
    try:
        new_row = await request.json()
        new_row['Inventory_Level'] = int(new_row.get('Inventory_Level', 0))
        new_row['Units_Sold'] = int(new_row.get('Units_Sold', 0))
        new_row['Price'] = float(new_row.get('Price', 0.0))
        if 'Date' not in new_row:
            new_row['Date'] = datetime.now().strftime("%Y-%m-%d")

        db.add_record(new_row)
        background_tasks.add_task(forecaster.train, db.records)
        background_tasks.add_task(broadcast_state_update)
        return {"message": "Data saved successfully!"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/action")
async def handle_action(request: Request, background_tasks: BackgroundTasks):
    try:
        action_data = await request.json()
        category = action_data.get("product_category", "Unknown")
        region = action_data.get("region", action_data.get("hub_city", "Unknown"))
        qty = int(action_data.get("quantity", 0))
        action_type = action_data.get("action_type", "rebalance")
        source_region = action_data.get("source_region", "Main Factory")
        
        today_date = datetime.now().strftime("%Y-%m-%d")
        store_id, product_id, price = "AI-AUTO", "P1001", 100.00
        
        for item in db.records:
            if item.get("Category") == category:
                product_id = item.get("Product_ID")
                price = float(item.get("Price", 100.00))
                break

        if action_type == "transfer":
            current_src = db.get_stock(source_region, category)
            db.records.insert(0, {
                "Date": today_date, "Store_ID": f"{store_id}-{source_region[:3].upper()}-OUT",
                "Product_ID": f"{product_id}-TRF-OUT", "Category": category, "Region": source_region,
                "Inventory_Level": max(0, current_src - qty), "Units_Sold": 0, "Price": price
            })
            current_dest = db.get_stock(region, category)
            db.records.insert(0, {
                "Date": today_date, "Store_ID": f"{store_id}-{region[:3].upper()}-IN",
                "Product_ID": f"{product_id}-TRF-IN", "Category": category, "Region": region,
                "Inventory_Level": current_dest + qty, "Units_Sold": 0, "Price": price
            })
        else:
            current_dest = db.get_stock(region, category)
            db.records.insert(0, {
                "Date": today_date, "Store_ID": f"{store_id}-{region[:3].upper()}-IN",
                "Product_ID": product_id, "Category": category, "Region": region,
                "Inventory_Level": current_dest + qty, "Units_Sold": 0, "Price": price
            })

        db.save_to_disk()
        background_tasks.add_task(forecaster.train, db.records)
        background_tasks.add_task(broadcast_state_update)
        return {"message": "AI Action Saved Successfully!"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/model-info")
async def get_model_info():
    return forecaster.model_info

@app.get("/api/forecast")
async def get_forecast():
    return forecaster.predict_future_demand(db.records)
