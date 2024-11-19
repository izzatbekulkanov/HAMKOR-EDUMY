from django.http import JsonResponse
from account.models import District, Quarters

def get_districts(request, region_id):
    """Viloyatga tegishli tumanlarni qaytaradi."""
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)

def get_quarters(request, district_id):
    """Tuman tegishli mahallalarni qaytaradi."""
    quarters = Quarters.objects.filter(district_id=district_id).values('id', 'name')
    return JsonResponse(list(quarters), safe=False)
