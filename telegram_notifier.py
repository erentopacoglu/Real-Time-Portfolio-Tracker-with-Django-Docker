import requests
import psycopg2
import time
from datetime import datetime

# --- AYARLAR ---
TOKEN = "8606886121:AAEjhuBVzrc6yzPEjSSAJY_FfW2I5Vnu7RQ" # Örn: "123456:ABC-DEF..."
CHAT_ID = "5756073337" # Örn: "987654321"

# Takip Edilecek Alarm Limitleri
# Fiyat bu aralığın dışına çıkarsa mesaj atar.
ALERTS = {
    "THYAO": {"min": 290.00, "max": 298.00},
    "ASELS": {"min": 341.00, "max": 345.00},
    "EREGL": {"min": 27.50, "max": 29.00}
}

def send_telegram_msg(message):
    """Telegram API üzerinden mesaj gönderir."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"  ✉️ Bildirim gönderildi: {message[:30]}...")
        else:
            print(f"  ❌ Telegram Hatası: {response.text}")
    except Exception as e:
        print(f"  ‼️ Bağlantı Hatası: {e}")

def check_alerts():
    """DB'deki son fiyatları kontrol eder."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="portfolio_db", 
            user="postgres", 
            password="pass", 
            host="127.0.0.1", 
            port="5432"
        )
        cur = conn.cursor()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Alarmlar kontrol ediliyor...")

        for sym, limits in ALERTS.items():
            # Veritabanındaki en güncel fiyatı çek
            cur.execute(f"SELECT price FROM price_history WHERE fund_code = '{sym}' ORDER BY recorded_at DESC LIMIT 1")
            row = cur.fetchone()
            
            if row:
                current_price = float(row[0])
                
                # MÜHENDİSLİK KONTROLÜ: Limit aşımı var mı?
                if current_price <= limits['min']:
                    send_telegram_msg(f"🚨 DÜŞÜŞ ALARMI: {sym} kritik seviyede! \nFiyat: {current_price:.2f} TL (Limit: {limits['min']})")
                elif current_price >= limits['max']:
                    send_telegram_msg(f"🚀 YÜKSELİŞ ALARMI: {sym} hedefi aştı! \nFiyat: {current_price:.2f} TL (Limit: {limits['max']})")
        
        cur.close()
    except Exception as e:
        print(f"‼️ DB Hatası: {e}")
    finally:
        if conn:
            conn.close()

# --- ANA DÖNGÜ ---
if __name__ == "__main__":
    print("🔔 Portföy Alarm Sistemi Devreye Girdi...")
    # İlk çalıştığında bir 'Test' mesajı gönderelim ki bağlantıdan emin olalım
    send_telegram_msg("🤖 Sistem aktif! Portföyünü izlemeye başladım.")
    
    while True:
        check_alerts()
        # 5 dakikada bir kontrol et (Senin terciğine göre 60 saniye de olabilir)
        time.sleep(300)