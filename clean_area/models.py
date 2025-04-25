# models.py
from django.db import models
from django.utils import timezone


class District(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"


class Neighborhood(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='neighborhoods')
    
    def __str__(self):
        return f"{self.name} ({self.district.name})"
    
    class Meta:
        verbose_name = "Mahalla"
        verbose_name_plural = "Mahallalar"


class Location(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE, related_name='locations')
    address = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.address} ({self.neighborhood.name})"
    
    class Meta:
        verbose_name = "Manzil"
        verbose_name_plural = "Manzillar"


class Bin(models.Model):
    STATUS_CHOICES = (
        ('to\'lmagan', 'To\'lmagan'),
        ('to\'lgan', 'To\'lgan'),
    )
    
    bin_id = models.CharField(max_length=50, unique=True)
    sensor_id = models.CharField(max_length=50, unique=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='bins')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to\'lmagan')
    last_updated = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self):
        return f"{self.bin_id} - {self.status}"
    
    class Meta:
        verbose_name = "Axlat idishi"
        verbose_name_plural = "Axlat idishlari"


class BinStatusHistory(models.Model):
    bin = models.ForeignKey(Bin, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20, choices=Bin.STATUS_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.bin.bin_id} - {self.status} ({self.created_at})"
    
    class Meta:
        verbose_name = "Status tarixi"
        verbose_name_plural = "Status tarixlari"
        ordering = ['-created_at']