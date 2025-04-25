from django.contrib import admin
from django.utils.html import format_html
from .models import District, Neighborhood, Location, Bin, BinStatusHistory


class NeighborhoodInline(admin.TabularInline):
    model = Neighborhood
    extra = 1


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'neighborhood_count')
    search_fields = ('name',)
    inlines = [NeighborhoodInline]
    
    def neighborhood_count(self, obj):
        return obj.neighborhoods.count()
    neighborhood_count.short_description = 'Mahallalar soni'


class LocationInline(admin.TabularInline):
    model = Location
    extra = 1


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'location_count')
    list_filter = ('district',)
    search_fields = ('name', 'district__name')
    inlines = [LocationInline]
    
    def location_count(self, obj):
        return obj.locations.count()
    location_count.short_description = 'Manzillar soni'


class BinInline(admin.TabularInline):
    model = Bin
    extra = 1


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('address', 'neighborhood', 'district', 'bin_count')
    list_filter = ('neighborhood__district', 'neighborhood')
    search_fields = ('address', 'neighborhood__name')
    inlines = [BinInline]
    
    def district(self, obj):
        return obj.neighborhood.district
    district.short_description = 'Tuman'
    
    def bin_count(self, obj):
        return obj.bins.count()
    bin_count.short_description = 'Idishlar soni'


class BinStatusHistoryInline(admin.TabularInline):
    model = BinStatusHistory
    extra = 0
    readonly_fields = ('status', 'created_at')
    can_delete = False
    max_num = 10
    ordering = ('-created_at',)


@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ('bin_id', 'sensor_id', 'display_status', 'location_details', 'last_updated', 'phone_number')
    list_filter = ('status', 'location__neighborhood__district', 'location__neighborhood')
    search_fields = ('bin_id', 'sensor_id', 'location__address')
    readonly_fields = ('last_updated',)
    inlines = [BinStatusHistoryInline]
    list_per_page = 20
    date_hierarchy = 'last_updated'
    
    def display_status(self, obj):
        if obj.status == 'to\'lgan':
            return format_html('<span style="color:red; font-weight:bold;">To\'lgan</span>')
        return format_html('<span style="color:green;">To\'lmagan</span>')
    display_status.short_description = 'Holat'
    
    def location_details(self, obj):
        return f"{obj.location.address} ({obj.location.neighborhood.name}, {obj.location.neighborhood.district.name})"
    location_details.short_description = 'Manzil'
    
    actions = ['mark_as_filled', 'mark_as_not_filled']
    
    def mark_as_filled(self, request, queryset):
        for bin in queryset:
            bin.status = 'to\'lgan'
            bin.save()
            BinStatusHistory.objects.create(bin=bin, status='to\'lgan')
        self.message_user(request, f"{queryset.count()} ta idish to'lgan deb belgilandi.")
    mark_as_filled.short_description = "Tanlangan idishlarni to'lgan deb belgilash"
    
    def mark_as_not_filled(self, request, queryset):
        for bin in queryset:
            bin.status = 'to\'lmagan'
            bin.save()
            BinStatusHistory.objects.create(bin=bin, status='to\'lmagan')
        self.message_user(request, f"{queryset.count()} ta idish to'lmagan deb belgilandi.")
    mark_as_not_filled.short_description = "Tanlangan idishlarni to'lmagan deb belgilash"


@admin.register(BinStatusHistory)
class BinStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('bin', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'bin__location__neighborhood__district', 'bin__location__neighborhood')
    search_fields = ('bin__bin_id', 'bin__location__address')
    date_hierarchy = 'created_at'
    readonly_fields = ('bin', 'status', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False