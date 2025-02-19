from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken

from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import io

from .models import User, Mission, SpaceFlight, Booking
from .serializers import UserSerializer, RegisterSerializer, MissionSerializer, SpaceFlightSerializer, BookingSerializer

# Регистрация пользователя
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

# Авторизация и выдача токена
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            update_last_login(None, user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'message': 'Login failed'}, status=status.HTTP_403_FORBIDDEN)

# Выход (очистка токена)
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# CRUD API для космических миссий
class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    permission_classes = [permissions.IsAuthenticated]

# CRUD API для космических полетов
class SpaceFlightViewSet(viewsets.ModelViewSet):
    queryset = SpaceFlight.objects.all()
    serializer_class = SpaceFlightSerializer
    permission_classes = [permissions.IsAuthenticated]

# API для бронирования космических полетов
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        flight_number = request.data.get("flight_number")
        try:
            flight = SpaceFlight.objects.get(flight_number=flight_number)
        except SpaceFlight.DoesNotExist:
            return Response({"error": {"code": 404, "message": "Flight not found"}}, status=status.HTTP_404_NOT_FOUND)

        if flight.seats_available <= 0:
            return Response({"error": {"code": 400, "message": "No seats available"}}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.create(user=request.user, flight=flight)
        flight.seats_available -= 1
        flight.save()

        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

# API для поиска по миссиям и пилотам
class SearchView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')

        missions = Mission.objects.filter(name__icontains=query)
        flights = SpaceFlight.objects.filter(destination__icontains=query)

        mission_data = MissionSerializer(missions, many=True).data
        flight_data = SpaceFlightSerializer(flights, many=True).data

        return Response({"missions": mission_data, "flights": flight_data}, status=status.HTTP_200_OK)

# API для получения информации о Гагарине
class GagarinFlightView(APIView):
    def get(self, request):
        data = {
            "data": [
                {
                    "mission": {
                        "name": "Восток 1",
                        "launch_details": {
                            "launch_date": "1961-04-12",
                            "launch_site": {
                                "name": "Космодром Байконур",
                                "location": {
                                    "latitude": "45.9650000",
                                    "longitude": "63.3050000"
                                }
                            }
                        },
                        "flight_duration": {
                            "hours": 1,
                            "minutes": 48
                        },
                        "spacecraft": {
                            "name": "Восток 3KA",
                            "manufacturer": "OKB-1",
                            "crew_capacity": 1
                        }
                    },
                    "landing": {
                        "date": "1961-04-12",
                        "site": {
                            "name": "Смеловка",
                            "country": "СССР",
                            "coordinates": {
                                "latitude": "51.2700000",
                                "longitude": "45.9970000"
                            }
                        },
                        "details": {
                            "parachute_landing": True,
                            "impact_velocity_mps": 7
                        }
                    },
                    "cosmonaut": {
                        "name": "Юрий Гагарин",
                        "birthdate": "1934-03-09",
                        "rank": "Старший лейтенант",
                        "bio": {
                            "early_life": "Родился в Клушино, Россия.",
                            "career": "Отобран в отряд космонавтов в 1960 году...",
                            "post_flight": "Стал международным героем."
                        }
                    }
                }
            ]
        }
        return Response(data, status=status.HTTP_200_OK)

# API для генерации изображжений с водяным знаком
class WatermarkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if 'fileimage' not in request.FILES or 'message' not in request.data:
            return Response({"error": {"code": 400, "message": "Missing file or message"}},
                            status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['fileimage']
        message = request.data['message']

        if not (10 <= len(message) <= 20):
            return Response({"error": {"code": 400, "message": "Message must be 10-20 characters"}},
                            status=status.HTTP_400_BAD_REQUEST)

        # Открываем изображение
        image = Image.open(file)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        draw.text((10, 10), message, font=font, fill="white")

        # Сохраняем в поток и отправляем как HTTP-ответ
        img_io = io.BytesIO()
        image.save(img_io, format="PNG")
        img_io.seek(0)

        return HttpResponse(img_io, content_type="image/png")
