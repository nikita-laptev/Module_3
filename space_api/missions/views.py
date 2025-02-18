from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken

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


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class SpaceFlightViewSet(viewsets.ModelViewSet):
    queryset = SpaceFlight.objects.all()
    serializer_class = SpaceFlightSerializer
    permission_classes = [permissions.IsAuthenticated]


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


class SearchView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')

        missions = Mission.objects.filter(name__icontains=query)
        flights = SpaceFlight.objects.filter(destination__icontains=query)

        mission_data = MissionSerializer(missions, many=True).data
        flight_data = SpaceFlightSerializer(flights, many=True).data

        return Response({"missions": mission_data, "flights": flight_data}, status=status.HTTP_200_OK)


class WatermarkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if 'fileimage' not in request.FILES or 'message' not in request.data:
            return Response({"error": {"code": 400, "message": "Missing file or message"}}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['fileimage']
        message = request.data['message']

        if not (10 <= len(message) <= 20):
            return Response({"error": {"code": 400, "message": "Message must be 10-20 characters"}}, status=status.HTTP_400_BAD_REQUEST)

        image = Image.open(file)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        draw.text((10, 10), message, font=font, fill="white")

        img_io = io.BytesIO()
        image.save(img_io, format="PNG")
        img_io.seek(0)

        return Response({"message": "Watermark added successfully"}, status=status.HTTP_201_CREATED)
