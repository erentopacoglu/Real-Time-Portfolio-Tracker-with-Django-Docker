from django.db import models

# Create your models here.

class Fund(models.Model):
    # TTE, MKG gibi fon kodları
    code = models.CharField(max_length=10)
    # Alınan pay adedi
    quantity = models.FloatField()
    # Birim alış fiyatı (12 basamak, 4 ondalık)
    buy_price = models.DecimalField(max_digits=12, decimal_places=4)
    # İşlem tarihi (Otomatik eklenir)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.quantity} units"