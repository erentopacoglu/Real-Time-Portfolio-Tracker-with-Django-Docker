import yfinance as yf
import psycopg2
import time
from datetime import datetime

# Veritabanı Ayarları
DB_CONFIG = {
    "dbname": "portfolio_db",
    "user": "postgres",
    "password": "pass",
    "host": "127.0.0.1",
    "port": "5432"
}

# Takip edilecek hisseler
SYMBOLS = ["THYAO.IS", "EREGL.IS", "ASELS.IS"]

def collect_data():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Veri toplama başladı...")

        for sym in SYMBOLS:
            try:
                ticker = yf.Ticker(sym)
                
                # history() veya fast_info yerine en temel info sözlüğünü çekiyoruz
                info = ticker.info
                
                # Yahoo fiyatı bazen 'currentPrice' bazen 'regularMarketPrice' altında gizler
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                
                if current_price is not None:
                    price = float(current_price)
                    clean_sym = sym.replace(".IS", "")
                    
                    cur.execute(
                        "INSERT INTO price_history (fund_code, price) VALUES (%s, %s)",
                        (clean_sym, price)
                    )
                    print(f"  ✅ {clean_sym}: {price:.2f} TL")
                else:
                    print(f"  ⚠️ {sym}: info sözlüğünde fiyat bulunamadı.")
                    
            except Exception as sub_e:
                print(f"  ❌ {sym} hatası: {sub_e}")
                continue
        conn.commit()
        cur.close()

    except Exception as e:
        print(f"‼️ Genel hata: {e}")
    finally:
        if conn:
            conn.close()

# --- ANA DÖNGÜ (DURDURULABİLİR) ---
print("🚀 Veri toplama botu çalışıyor. Durdurmak için Ctrl+C tuşuna basın.")
try:
    iteration = 0
    while True: # Belirli bir sayı yerine sonsuz döngü (sen durdurana kadar)
        iteration += 1
        collect_data()
        print(f"💤 Tur {iteration} bitti. 60 saniye bekleniyor...\n")
        time.sleep(60)

except KeyboardInterrupt:
    print("\n🛑 İşlem kullanıcı tarafından durduruldu (Ctrl+C).")
    print("👋 Veritabanı bağlantıları kapatıldı, çıkış yapılıyor.")

except Exception as main_e:
    print(f"‼️ Beklenmedik hata: {main_e}")