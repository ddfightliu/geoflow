#!/usr/bin/env python3
'''Initialize MongoDB for securities trading game system - FIXED VERSION.'''
# Connect to Atlas cluster from config
# Run: python3 init_trading_db_fixed.py

import asyncio
import time
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from backend.auth.config import get_settings
from backend.auth.database import init_db


settings = get_settings()

async def init_trading_database():
    ''' Initialize complete trading database structure.'''

    client = AsyncIOMotorClient(settings.DATABASE_URL)
    db = client.geoflow

    # Drop existing collections for clean start (comment out for production)
    print("Dropping existing collections...")
    collections = await db.list_collection_names()
    for coll in collections:
        await db[coll].drop()
        print(f"Dropped {coll}")

    await init_db()  # User indexes

    # 1. USERS collection - enhanced for trading
    print("\n1. Creating enhanced USERS collection...")
    users = db.users

    await users.create_index([("portfolio.symbol", 1)])
    await users.create_index([("created_at", -1)])

    # Sample users with portfolios
    sample_users = [
        {
            "username": "trader1",
            "email": "trader1@example.com",
            "hashed_password": "$pbkdf2-sha256$29000$abc123def456$hashedvalue123",  # dummy
            "full_name": "专业交易员1",
            "points": 50000.0,
            "portfolio": {
                "holdings": [
                    {"symbol": "AAPL", "shares": 100, "avg_buy_price": 150.0},
                    {"symbol": "TSLA", "shares": 50, "avg_buy_price": 700.0}
                ],
                "total_value": 35000.0
            },
            "trading_history": [],
            "risk_level": "medium",
            "created_at": time.time(),
            "is_active": True,
            "is_superuser": False
        },
        {
            "username": "beginner",
            "email": "beginner@example.com",
            "hashed_password": "$pbkdf2-sha256$29000$xyz789$hashedvalue456",
            "full_name": "新手交易员",
            "points": 10000.0,
            "portfolio": {
                "holdings": [
                    {"symbol": "MSFT", "shares": 20, "avg_buy_price": 300.0}
                ],
                "total_value": 6000.0
            },
            "trading_history": [],
            "risk_level": "low",
            "created_at": time.time(),
            "is_active": True,
            "is_superuser": False
        }
    ]
    result = await users.insert_many(sample_users)
    inserted_ids = [str(ObjectId(oid)) for oid in result.inserted_ids]
    trader1_id = inserted_ids[0]
    print(f"Inserted {len(sample_users)} sample users. Trader1 ID: {trader1_id}")

    # 2. TRANSACTIONS collection - securities trades
    print("\n2. Creating TRANSACTIONS collection...")
    transactions = db.transactions
    await transactions.create_index([("user_id", 1)])
    await transactions.create_index([("symbol", 1)])
    await transactions.create_index([("timestamp", -1)])
    await transactions.create_index([("type", 1), ("symbol", 1)])

    sample_trades = [
        {
            "id": "tx001",
            "user_id": trader1_id,
            "symbol": "AAPL",
            "type": "buy",
            "shares": 100,
            "price": 150.0,
            "total": 15000.0,
            "fee": 15.0,
            "timestamp": time.time(),
            "notes": "首次买入苹果股票"
        },
        {
            "id": "tx002",
            "user_id": trader1_id,
            "symbol": "TSLA",
            "type": "buy",
            "shares": 50,
            "price": 700.0,
            "total": 35000.0,
            "fee": 35.0,
            "timestamp": time.time() - 3600,
            "notes": "特斯拉电动车龙头"
        }
    ]
    await transactions.insert_many(sample_trades)
    print(f"Inserted {len(sample_trades)} sample transactions")

    # 3. SECURITIES collection - 交易品种
    print("\n3. Creating SECURITIES collection...")
    securities = db.securities
    await securities.create_index([("symbol", 1)], unique=True)

    securities_data = [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "type": "stock",
            "sector": "Technology",
            "current_price": 175.50,
            "change_24h": 2.34,
            "volume": 85000000,
            "market_cap": "2800B",
            "pe_ratio": 28.5
        },
        {
            "symbol": "TSLA",
            "name": "Tesla Inc.",
            "type": "stock",
            "sector": "Automotive",
            "current_price": 245.0,
            "change_24h": -1.2,
            "volume": 120000000,
            "market_cap": "780B",
            "pe_ratio": 65.2
        },
        {
            "symbol": "BTCUSD",
            "name": "Bitcoin USD",
            "type": "crypto",
            "sector": "Cryptocurrency",
            "current_price": 67000.0,
            "change_24h": 3.8,
            "volume": 25000000000,
            "market_cap": "1320T"
        }
    ]
    await securities.insert_many(securities_data)
    print(f"Inserted {len(securities_data)} securities")

    # 4. ORDERS collection - 委托订单
    print("\n4. Creating ORDERS collection...")
    orders = db.orders
    await orders.create_index([("user_id", 1)])
    await orders.create_index([("status", 1)])
    await orders.create_index([("symbol", 1), ("status", 1)])
    await orders.create_index([("created_at", -1)])

    print("ORDERS collection ready for limit/market orders")

    # 5. MARKET_DATA collection - K线数据
    print("\n5. Creating MARKET_DATA collection...")
    market_data = db.market_data
    await market_data.create_index([("symbol", 1), ("timestamp", -1)])

    print("MARKET_DATA collection ready for OHLCV data")

    print("\n✅ Trading database 初始化完成！")
    print("Collections: users, transactions, securities, orders, market_data")
    print("Sample data loaded. Ready for securities trading game!")

    client.close()


if __name__ == "__main__":
    asyncio.run(init_trading_database())

