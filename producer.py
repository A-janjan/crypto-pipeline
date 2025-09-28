import json
import time
from confluent_kafka import Producer
import requests

# Kafka config
KAFKA_CONF = {"bootstrap.servers": "localhost:9092"}
TOPIC = "crypto.ticks"
p = Producer(KAFKA_CONF)

# Fetch Binance data
def fetch_binance(symbol="BTCUSDT"):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    r = requests.get(url, timeout=5)
    return r.json()

# Produce to Kafka
def produce(msg):
    p.produce(TOPIC, json.dumps(msg).encode("utf-8"))
    p.flush()
    print(f"✅ Produced to Kafka: {msg['symbol']} | Price: {msg['price']} | Volume: {msg['volume']}")

if __name__ == "__main__":
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    print("🚀 Starting Binance Kafka producer...")
    while True:
        for s in symbols:
            try:
                print(f"⏳ Fetching data for {s}...")
                data = fetch_binance(s)
                msg = {
                    "symbol": s,
                    "price": float(data["lastPrice"]),
                    "volume": float(data["volume"]),
                    "ts": int(time.time() * 1000),
                    "raw": data
                }
                produce(msg)
            except Exception as e:
                print(f"❌ Error fetching or producing {s}: {e}")
        print("⏱ Sleeping for 5 seconds before next fetch...\n")
        time.sleep(5)
