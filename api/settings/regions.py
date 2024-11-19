import json

from django.http import JsonResponse
from django.views import View
from account.models import Regions, District, Quarters


class LocationAPIView(View):
    def get(self, request, *args, **kwargs):
        regions = list(Regions.objects.values('id', 'name'))
        districts = list(District.objects.values('id', 'name', 'region_id'))
        quarters = list(Quarters.objects.values('id', 'name', 'district_id'))

        return JsonResponse({
            'success': True,
            'regions': regions,
            'districts': districts,
            'quarters': quarters,
        })

    def post(self, request, *args, **kwargs):
        level = request.POST.get("level")
        name = request.POST.get("name")
        code = request.POST.get("code")
        parent_id = request.POST.get("parent_id")

        if level == "region":
            Regions.objects.create(name=name, code=code)
        elif level == "district":
            District.objects.create(name=name, code=code, region_id=parent_id)
        elif level == "quarter":
            Quarters.objects.create(name=name, code=code, district_id=parent_id)
        else:
            return JsonResponse({"success": False, "message": "Invalid level."}, status=400)

        return JsonResponse({"success": True, "message": f"{level.title()} added successfully!"})


class GetLocationsView(View):
    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", "").lower()
        level = request.GET.get("level", "").lower()
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 10))

        regions = list(Regions.objects.values('id', 'name', 'code'))
        districts = list(District.objects.values('id', 'name', 'code', 'region_id'))
        quarters = list(Quarters.objects.values('id', 'name', 'code', 'district_id'))

        if search:
            regions = [r for r in regions if search in r['name'].lower() or search in r['code'].lower()]
            districts = [d for d in districts if search in d['name'].lower() or search in d['code'].lower()]
            quarters = [q for q in quarters if search in q['name'].lower() or search in q['code'].lower()]

        for district in districts:
            region = Regions.objects.filter(id=district['region_id']).first()
            district['parent_name'] = region.name if region else "N/A"
            district['level'] = 'Tuman'

        for quarter in quarters:
            district = District.objects.filter(id=quarter['district_id']).first()
            quarter['parent_name'] = district.name if district else "N/A"
            quarter['level'] = 'Mahalla'

        for region in regions:
            region['parent_name'] = "N/A"
            region['level'] = "Viloyat"

        locations = regions + districts + quarters

        if level:
            locations = [loc for loc in locations if loc['level'].lower() == level]

        locations = sorted(locations, key=lambda x: x['name'])

        total = len(locations)
        locations = locations[start:start + length]

        return JsonResponse({
            "draw": int(request.GET.get("draw", 1)),
            "recordsTotal": total,
            "recordsFiltered": total,
            "data": [
                {
                    "name": location['name'],
                    "code": location['code'],
                    "level": location['level'],
                    "parent_name": location['parent_name']
                }
                for location in locations
            ],
        })


