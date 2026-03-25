import psycopg2
import pandas as pd

def get_portfolio_summary():
    try:
        # DB Bağlantısı - dbname'i "portfolio_db" olarak güncelledim (resimdeki isme göre)
        conn = psycopg2.connect(
            dbname="portfolio_db", 
            user="postgres", 
            password="pass", 
            host="127.0.0.1", 
            port="5432", 
            connect_timeout=5
        )
        
        # --- TABLO KONTROL BÖLÜMÜ (Debugging) ---
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"--- Veritabanındaki Mevcut Tablolar: {tables} ---")
        # ----------------------------------------

        # 1. Alış verilerini çek
        # Not: Tablo ismi yukarıdaki listede neyse onu buraya yazmalısın.
        query_funds = 'SELECT code, quantity, buy_price FROM "investment_fund"'
        df_portfolio = pd.read_sql(query_funds, conn)
        
        if df_portfolio.empty:
            print("UYARI: 'investment_fund' tablosu bulundu ama içi boş!")
            return pd.DataFrame()

        summary_results = []
        
        for index, row in df_portfolio.iterrows():
            # 2. En son fiyatı çek
            query_last_price = f"SELECT price FROM price_history WHERE fund_code = '{row['code']}' ORDER BY recorded_at DESC LIMIT 1"
            df_last = pd.read_sql(query_last_price, conn)
            
            if not df_last.empty:
                current_price = float(df_last['price'][0])
                cost = float(row['buy_price'])
                qty = float(row['quantity'])
                
                total_cost = cost * qty
                current_value = current_price * qty
                profit_loss = current_value - total_cost
                percentage = (profit_loss / total_cost) * 100
                
                summary_results.append({
                    "Hisse": row['code'],
                    "Adet": qty,
                    "Maliyet": f"{total_cost:.2f} TL",
                    "Değer": f"{current_value:.2f} TL",
                    "Kâr/Zarar": f"{profit_loss:+.2f} TL",
                    "Değişim": f"%{percentage:+.2f}"
                })
        
        conn.close()
        return pd.DataFrame(summary_results)

    except Exception as e:
        print(f"Hata oluştu: {e}")
        return pd.DataFrame()

# Sonucu yazdır
print("\n--- PORTFÖY ÖZETİ ---")
print(get_portfolio_summary())