from django.contrib.auth.models import AbstractUser
from django.db import models

# Кастомная модель пользователя
class User(AbstractUser):
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'birth_date']

    def __str__(self):
        return self.email

# Модель для космических миссий
class Mission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    launch_date = models.DateField()
    launch_site = models.CharField(max_length=255)
    landing_date = models.DateField()
    landing_site = models.CharField(max_length=255)
    crew_capacity = models.IntegerField()

    def __str__(self):
        return self.name

# Модель для космических полетов
class SpaceFlight(models.Model):
    flight_number = models.CharField(max_length=50, unique=True)
    destination = models.CharField(max_length=255)
    launch_date = models.DateField()
    seats_available = models.IntegerField()

    def __str__(self):
        return self.flight_number

# Модель для бронирования космических рейсов
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(SpaceFlight, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'flight')

    def __str__(self):
        return f"{self.user.email} - {self.flight.flight_number}"
