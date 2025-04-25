# serializers.py
from rest_framework import serializers
from .models import District, Neighborhood, Location, Bin, BinStatusHistory


class BinStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BinStatusHistory
        fields = ['status', 'created_at']


class BinSerializer(serializers.ModelSerializer):
    neighborhood = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    history = BinStatusHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Bin
        fields = ['bin_id', 'sensor_id', 'status', 'neighborhood', 'address', 'last_updated', 'history']
    
    def get_neighborhood(self, obj):
        return obj.location.neighborhood.name
    
    def get_address(self, obj):
        return obj.location.address


class BinUpdateSerializer(serializers.Serializer):
    sensor_id = serializers.CharField(max_length=50)
    status = serializers.ChoiceField(choices=Bin.STATUS_CHOICES)
    api_key = serializers.CharField(max_length=100, write_only=True, required=True)
    location = serializers.CharField(max_length=255, required=False)


class LocationSerializer(serializers.ModelSerializer):
    bins = BinSerializer(many=True, read_only=True)
    neighborhood_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ['id', 'address', 'neighborhood_name', 'bins']
    
    def get_neighborhood_name(self, obj):
        return obj.neighborhood.name


class NeighborhoodSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)
    district_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Neighborhood
        fields = ['id', 'name', 'district_name', 'locations']
    
    def get_district_name(self, obj):
        return obj.district.name


class DistrictSerializer(serializers.ModelSerializer):
    neighborhoods = NeighborhoodSerializer(many=True, read_only=True)
    
    class Meta:
        model = District
        fields = ['id', 'name', 'neighborhoods']


class StatisticsSerializer(serializers.Serializer):
    total_bins = serializers.IntegerField()
    filled_bins = serializers.IntegerField()
    district_name = serializers.CharField()
    last_updated = serializers.DateTimeField()