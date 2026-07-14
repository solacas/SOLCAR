# This file is needed for  passing variable to base.html
from .models import Car, Privacy, Ads


def ad_processor(request):
    return {
        'ad' : Ads.objects.first()
    }