from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import User


class Dataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Analysis(models.Model):
    ANALYSIS_TYPES = [
        ('hist', 'Гистограмма'),
        ('scatter', 'Точечный график'),
        ('line', 'Линейный график'),
        ('bar', 'Столбчатая диаграмма'),
        ('pie', 'Круговая диаграмма'),
    ]

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    x_column = models.CharField(max_length=100)
    y_column = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='analysis/')

    def get_absolute_url(self):
        return reverse('view_analysis', args=[str(self.id)])

    def __str__(self):
        return f"{self.get_analysis_type_display()} для {self.dataset.name}"
