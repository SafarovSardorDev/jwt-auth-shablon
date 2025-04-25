# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db.models import Count
from .models import District, Neighborhood, Location, Bin, BinStatusHistory
from .serializers import (
    DistrictSerializer, NeighborhoodSerializer, LocationSerializer, 
    BinSerializer, BinUpdateSerializer, StatisticsSerializer
)
from django.conf import settings
import re


# Faqat ro'yxatdan o'tgan foydalanuvchilar uchun
class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]  # Faqat ro'yxatdan o'tganlar uchun


# Faqat ro'yxatdan o'tgan foydalanuvchilar uchun
class NeighborhoodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer
    permission_classes = [IsAuthenticated]  # Faqat ro'yxatdan o'tganlar uchun
    
    def get_queryset(self):
        district_id = self.request.query_params.get('district', None)
        if district_id:
            return Neighborhood.objects.filter(district_id=district_id)
        return Neighborhood.objects.all()


# Faqat ro'yxatdan o'tgan foydalanuvchilar uchun
class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]  # Faqat ro'yxatdan o'tganlar uchun
    
    def get_queryset(self):
        neighborhood_id = self.request.query_params.get('neighborhood', None)
        if neighborhood_id:
            return Location.objects.filter(neighborhood_id=neighborhood_id)
        return Location.objects.all()


# Faqat ro'yxatdan o'tgan foydalanuvchilar uchun
class BinViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bin.objects.all()
    serializer_class = BinSerializer
    permission_classes = [IsAuthenticated]  # Faqat ro'yxatdan o'tganlar uchun
    
    def get_queryset(self):
        queryset = Bin.objects.all()
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status == "to'lgan":
            queryset = queryset.filter(status="to'lgan")
        elif status == "to'lmagan":
            queryset = queryset.filter(status="to'lmagan")
            
        # Filter by location
        location_id = self.request.query_params.get('location', None)
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        
        return queryset


# Arduino uchun AllowAny qoldirildi, chunki Arduino tizimga kirishdan foydalana olmaydi
@api_view(['POST'])
@permission_classes([AllowAny])
def bin_status_update(request):
    """
    Arduino orqali yuborilgan ma'lumotlarni qabul qilish
    API kalit orqali autentifikatsiya qilinadi
    """
    serializer = BinUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        # API kalitni tekshirish
        api_key = serializer.validated_data.get('api_key')
        if api_key != settings.ARDUINO_API_KEY:
            return Response({"error": "Noto'g'ri API kalit"}, status=status.HTTP_401_UNAUTHORIZED)
        
        sensor_id = serializer.validated_data.get('sensor_id')
        new_status = serializer.validated_data.get('status')
        
        try:
            bin_obj = Bin.objects.get(sensor_id=sensor_id)
            
            # Statusni yangilash faqat agar o'zgargan bo'lsa
            if bin_obj.status != new_status:
                bin_obj.status = new_status
                bin_obj.save()
                
                # Status tarixini saqlash
                BinStatusHistory.objects.create(
                    bin=bin_obj,
                    status=new_status
                )
                
                return Response({
                    "success": True, 
                    "message": f"Sensor {sensor_id} statusi yangilandi: {new_status}"
                })
            return Response({
                "success": True, 
                "message": f"Status allaqachon {new_status}"
            })
            
        except Bin.DoesNotExist:
            # Agar sensor_id mavjud bo'lmasa va location berilgan bo'lsa, 
            # yangi idish yaratamiz
            location_text = serializer.validated_data.get('location', None)
            
            if location_text:
                # Manzilni ajratib olish
                match = re.search(r'Manzil: ([^,]+), ([^,]+), (.+)', location_text)
                if match:
                    district_name = match.group(1).strip()
                    street_name = match.group(2).strip()
                    address = match.group(3).strip()
                    
                    # Tumanni topish yoki yaratish
                    district, _ = District.objects.get_or_create(name=district_name)
                    
                    # Mahallani topish yoki yaratish
                    neighborhood, _ = Neighborhood.objects.get_or_create(
                        name=street_name,
                        district=district
                    )
                    
                    # Manzilni topish yoki yaratish
                    location, _ = Location.objects.get_or_create(
                        neighborhood=neighborhood,
                        address=address
                    )
                    
                    # Yangi idish yaratish
                    bin_id = f"idish_{neighborhood.name.lower()}_{Bin.objects.count() + 1}"
                    bin_obj = Bin.objects.create(
                        bin_id=bin_id,
                        sensor_id=sensor_id,
                        location=location,
                        status=new_status,
                        phone_number=request.data.get('phone_number', None)
                    )
                    
                    # Status tarixini saqlash
                    BinStatusHistory.objects.create(
                        bin=bin_obj,
                        status=new_status
                    )
                    
                    return Response({
                        "success": True, 
                        "message": f"Yangi idish qo'shildi: {bin_id}"
                    })
            
            return Response(
                {"error": f"{sensor_id} sensorli idish topilmadi"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Faqat ro'yxatdan o'tgan foydalanuvchilar uchun
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Faqat ro'yxatdan o'tganlar uchun
def statistics(request):
    """
    Umumiy statistikani qaytarish
    """
    district_id = request.query_params.get('district', None)
    
    if district_id:
        district = District.objects.get(id=district_id)
        total_bins = Bin.objects.filter(location__neighborhood__district=district).count()
        filled_bins = Bin.objects.filter(
            location__neighborhood__district=district, 
            status="to'lgan"
        ).count()
        district_name = district.name
    else:
        # Bitta tuman haqida ma'lumot bor bo'lgani uchun
        district = District.objects.first()
        total_bins = Bin.objects.count()
        filled_bins = Bin.objects.filter(status="to'lgan").count()
        district_name = district.name if district else "Barcha tumanlar"
    
    data = {
        'district_name': district_name,
        'total_bins': total_bins,
        'filled_bins': filled_bins,
        'last_updated': timezone.now()
    }
    
    serializer = StatisticsSerializer(data)
    return Response(serializer.data)