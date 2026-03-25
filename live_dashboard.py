import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Grafik Ayarları
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
plt.subplots_adjust(hspace=0.4)

def animate(i):
    try:
        conn = psycopg2.connect(dbname="portfolio_db", user="postgres", password="pass", host="127.0.0.1", port="5432")
        
        # 1. Veriyi Çek
        query = "SELECT fund_code, price, recorded_at FROM price_history ORDER BY recorded_at DESC LIMIT 100"
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty:
            return

        # 2. Grafikleri Temizle
        for ax in axs.flat:
            ax.clear()

        symbols = df['fund_code'].unique()
        
        # --- İLK 3 ODA: Tekil Hisse Grafikleri ---
        for idx, sym in enumerate(symbols[:3]):
            ax = axs.flat[idx]
            data_sym = df[df['fund_code'] == sym].sort_values('recorded_at')
            
            ax.plot(data_sym['recorded_at'], data_sym['price'], marker='o', label=f"{sym} Fiyat")
            ax.set_title(f"{sym} Anlık Değişim")
            ax.legend()
            ax.tick_params(axis='x', rotation=45)

        # --- 4. ODA (Sağ Alt): Normalize Edilmiş Kıyaslama ---
        ax_norm = axs.flat[3]
        for sym in symbols[:3]:
            data_sym = df[df['fund_code'] == sym].sort_values('recorded_at')
            
            if not data_sym.empty:
                # Veri setindeki ilk fiyatı baz (sıfır noktası) kabul et
                base_price = data_sym['price'].iloc[0]
                
                # Formül: ((Anlık Fiyat / İlk Fiyat) - 1) * 100 = Yüzdelik Değişim
                normalized_price = (data_sym['price'] / base_price - 1) * 100 
                
                # Kıyaslama grafiğine çiz (kalabalık olmasın diye marker koymadık, düz çizgi)
                ax_norm.plot(data_sym['recorded_at'], normalized_price, linewidth=2, label=sym)

        ax_norm.set_title("Portföy Kıyaslaması (% Değişim)")
        ax_norm.axhline(0, color='black', linewidth=1, linestyle='--') # 0% Referans Çizgisi
        ax_norm.legend()
        ax_norm.tick_params(axis='x', rotation=45)

    except Exception as e:
        print(f"Grafik hatası: {e}")

# Fonksiyon dışı, genel ayarlar: 60 saniyede bir güncelle (60000 ms)
ani = animation.FuncAnimation(fig, animate, interval=60000)
print("📈 Grafik paneli başlatıldı. Veriler akıyor...")
plt.show()