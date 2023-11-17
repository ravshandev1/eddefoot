from django.db import models


class Rate(models.Model):
    price = models.PositiveIntegerField(default=0)
    description = models.TextField()

    def __str__(self):
        return f'{self.price}'


class PriceOfSubscribe(models.Model):
    price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.price}"


class Modul(models.Model):
    rate = models.ForeignKey(Rate, models.CASCADE, related_name='moduls')
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to='moduls')
    ordinal_number = models.FloatField()

    def __str__(self):
        return f"{self.rate.price} {self.name}"


class Theme(models.Model):
    modul = models.ForeignKey(Modul, models.CASCADE, related_name='themes')
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to='themes')
    ordinal_number = models.FloatField()

    def __str__(self):
        return self.name


class Exercise(models.Model):
    theme = models.ForeignKey(Theme, models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=250)
    ordinal_number = models.FloatField()
    description = models.TextField(null=True, blank=True)
    video = models.FileField(upload_to='exercises/videos')
    image = models.ImageField(upload_to='exercises/images')
    do_day = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.theme.name} {self.ordinal_number}"
