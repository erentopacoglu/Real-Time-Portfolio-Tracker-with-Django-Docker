import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Veritabanı bağlantısı
DB_CONFIG = {
    "dbname": "portfolio_db", 
    "user": "postgres",
    "password": "pass", 
    "host": "localhost", 
    "port": "5432"
}

def create_plots():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = "SELECT fund_code, price, recorded_at FROM price_history ORDER BY recorded_at ASC"
        df = pd.read_sql(query, conn)
        conn.close()
    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return

    if df.empty:
        print("Tablo boş, henüz grafik çizilemez!")
        return

    # 2x2'lik grafik alanını oluştur
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('30 Dakikalık Portföy Performans Analizi', fontsize=16)

    symbols = ['THYAO', 'EREGL', 'ASELS']
    colors = ['blue', 'green', 'red']

    # İlk 3 Grafik: Bireysel Fiyat Değişimleri
    for i, sym in enumerate(symbols):
        row = i // 2
        col = i % 2
        data = df[df['fund_code'] == sym]
        
        axs[row, col].plot(data['recorded_at'], data['price'], color=colors[i], marker='o', markersize=3, label=sym)
        axs[row, col].set_title(f'{sym} Ham Fiyat (TL)')
        axs[row, col].grid(True, linestyle='--', alpha=0.7)
        axs[row, col].legend()
        
        # Tarih formatını Saat:Dakika yap
        axs[row, col].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # 4. Grafik: Yüzdesel Karşılaştırma (Normalizasyon)
    axs[1, 1].set_title('Hisselerin % Getiri Karşılaştırması')
    for i, sym in enumerate(symbols):
        # Orijinal veriyi bozmamak için kopyasını alıyoruz
        data = df[df['fund_code'] == sym].copy()
        
        if not data.empty:
            # NORMALIZASYON: İlk fiyatı 100 kabul et veya 0'dan başlat
            # Burada 0'dan başlatıp % değişim görmek en sağlıklısı
            base_price = data['price'].iloc[0]
            data['pct_change'] = ((data['price'] / base_price) - 1) * 100
            
            axs[1, 1].plot(data['recorded_at'], data['pct_change'], label=f"{sym} (%)", color=colors[i], linewidth=2)

    axs[1, 1].axhline(0, color='black', linewidth=1, linestyle='-') # 0 çizgisini belirginleştir
    axs[1, 1].set_ylabel('% Değişim')
    axs[1, 1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    axs[1, 1].grid(True, linestyle='--', alpha=0.7)
    axs[1, 1].legend()

    # X ekseni yazılarını düzelt (hafif yan yatır)
    for ax in axs.flat:
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    create_plots()