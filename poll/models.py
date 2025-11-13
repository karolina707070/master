from django.db import models

# Таблица Типы Партнеров
class PartnerType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название типа")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип партнера"
        verbose_name_plural = "Типы партнеров"

# Таблица Организации

class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)


#  Таблица Типы_Материалов
class MaterialType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    defect_percentage = models.DecimalField( max_digits=5, decimal_places=2)


#  Таблица Типы_Продукции

class ProductType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    coefficient = models.DecimalField(max_digits=5, decimal_places=2)


# Таблица Продукция
class Product(models.Model):
    article = models.CharField(max_length=20, primary_key=True)
    product_name = models.CharField(max_length=255)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    min_price_for_partner = models.DecimalField(max_digits=10, decimal_places=2)


# Таблица Партнеры
class PartnerContact(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    partner_type = models.ForeignKey(PartnerType, on_delete=models.CASCADE)
    fio = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    inn = models.CharField(max_length=12, unique=True, blank=True, null=True)
    rating = models.IntegerField()


# Таблица Продажи
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    partner_name = models.ForeignKey(Organization, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sale_date = models.DateField()