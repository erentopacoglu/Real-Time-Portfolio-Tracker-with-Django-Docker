import yfinance as yf
import psycopg2
import time
from datetime import datetime

DB_CONFIG = {
    "dbname": "portfolio_db",
    "user": "postgres",
    "password": "pass",
    "host": "localhost",
    "port": "5432"
}

def collect_data(iteration):
    symbols = ["THYAO.IS", "EREGL.IS", "ASELS.IS"]
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Tur {iteration+1}/30 Başladı...")

    for sym in symbols:
        ticker = yf.Ticker(sym)
        data = ticker.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            print(f"DEBUG: {sym} için fiyat alındı: {price}") # Bu satırı ekle
            # Yeni tabloya kaydet
            cur.execute(
                "INSERT INTO price_history (fund_code, price) VALUES (%s, %s)",
                (sym.replace(".IS", ""), float(price))
            )
        else:
            print(f"DEBUG: {sym} için VERI BOS!") # Bunu da ekle

    
    conn.commit()
    cur.close()
    conn.close()

# Ana Döngü: 30 Dakika Boyunca Çalışır
for i in range(30):
    collect_data(i)
    if i < 29: # Son turda beklemeye gerek yok
        print("Bir sonraki dakika için bekleniyor...")
        time.sleep(60)

print("Veri toplama tamamlandı!")