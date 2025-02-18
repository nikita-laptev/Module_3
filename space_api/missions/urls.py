from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, LogoutView, MissionViewSet, SpaceFlightViewSet,
    BookingViewSet, SearchView, WatermarkView
)

# Создаем маршрутизатор и регистрируем ViewSet'ы
router = DefaultRouter()
router.register(r'missions', MissionViewSet, basename='mission')
router.register(r'space-flights', SpaceFlightViewSet, basename='spaceflight')
router.register(r'book-flight', BookingViewSet, basename='booking')

urlpatterns = [
    # Аутентификация
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # CRUD API (миссии и полеты)
    path('', include(router.urls)),

    # Поиск по миссиям и полетам
    path('search/', SearchView.as_view(), name='search'),

    # Генерация изображения с водяным знаком
    path('lunar-watermark/', WatermarkView.as_view(), name='lunar-watermark'),
]
