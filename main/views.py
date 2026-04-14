from django.shortcuts import render


def home(request):
    return render(request, "main/home.html")


def solar_resource_detail(request):
    """Display solar resource data for a particular site."""
    # Get parameters from query string
    address = request.GET.get('address', 'Unknown Location')
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    
    # Validate coordinates
    if latitude is None or longitude is None:
        # If coordinates are missing, redirect to home
        return render(request, "main/home.html", {
            "error": "Missing location coordinates. Please select a site first."
        })
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (ValueError, TypeError):
        return render(request, "main/home.html", {
            "error": "Invalid coordinates provided."
        })
    
    # Prepare site context data
    site = {
        'address': address,
        'latitude': latitude,
        'longitude': longitude,
    }
    
    return render(request, "main/solar_resource_detail.html", {
        'site': site
    })
