from rest_framework import serializers

from .services import SolarResourceReading, PVWattsCalculation


class SolarResourceReadingSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    annual_avg_dni = serializers.FloatField(allow_null=True)
    annual_avg_ghi = serializers.FloatField(allow_null=True)
    annual_avg_lat_tilt = serializers.FloatField(allow_null=True)
    monthly_avg_dni = serializers.DictField(allow_null=True)
    monthly_avg_ghi = serializers.DictField(allow_null=True)
    monthly_avg_lat_tilt = serializers.DictField(allow_null=True)

    def to_representation(self, instance):
        """Overriding function to re-structure API response. This matches external NREL API response style with inputs and outputs."""
        data = super().to_representation(instance)
        
        # Inputs object
        inputs = {
            "lat": data.get("latitude"),
            "lon": data.get("longitude"),
        }
        
        # Outputs object
        outputs = {}
        
        # Add avg_dni to outputs
        if data.get("annual_avg_dni") is not None or data.get("monthly_avg_dni") is not None:
            outputs["avg_dni"] = {}
            if data.get("annual_avg_dni") is not None:
                outputs["avg_dni"]["annual"] = data.get("annual_avg_dni")
            if data.get("monthly_avg_dni") is not None:
                outputs["avg_dni"]["monthly"] = data.get("monthly_avg_dni")
        
        # Add avg_ghi to outputs
        if data.get("annual_avg_ghi") is not None or data.get("monthly_avg_ghi") is not None:
            outputs["avg_ghi"] = {}
            if data.get("annual_avg_ghi") is not None:
                outputs["avg_ghi"]["annual"] = data.get("annual_avg_ghi")
            if data.get("monthly_avg_ghi") is not None:
                outputs["avg_ghi"]["monthly"] = data.get("monthly_avg_ghi")
        
        # Add avg_lat_tilt to outputs
        if data.get("annual_avg_lat_tilt") is not None or data.get("monthly_avg_lat_tilt") is not None:
            outputs["avg_lat_tilt"] = {}
            if data.get("annual_avg_lat_tilt") is not None:
                outputs["avg_lat_tilt"]["annual"] = data.get("annual_avg_lat_tilt")
            if data.get("monthly_avg_lat_tilt") is not None:
                outputs["avg_lat_tilt"]["monthly"] = data.get("monthly_avg_lat_tilt")
        
        return {
            "inputs": inputs,
            "outputs": outputs,
        }
    
    def create(self, validated_data):
        return SolarResourceReading(**validated_data)


class PVWattsCalculationSerializer(serializers.Serializer):
    # Required input parameters
    latitude = serializers.FloatField(
        help_text="The latitude for the location to use. Range: -90 to 90"
    )
    longitude = serializers.FloatField(
        help_text="The longitude for the location to use. Range: -180 to 180"
    )
    system_capacity = serializers.FloatField(
        help_text="Nameplate capacity (kW). Range: 0.05 to 500000"
    )
    module_type = serializers.IntegerField(
        help_text="Module Type (0=Standard, 1=Premium, 2=Thin Film)"
    )
    losses = serializers.FloatField(
        help_text="System losses (percent). Range: -5 to 99"
    )
    array_type = serializers.IntegerField(
        help_text="Array type. (0=Fixed, 1=Fixed Roof, 2=1-Axis, 3=1-Axis Backtracking, 4=2-Axis)"
    )
    tilt = serializers.FloatField(
        help_text="Tilt angle (degrees). Range: 0 to 90 degrees"
    )
    azimuth = serializers.FloatField(
        help_text="Azimuth angle (degrees). Range: 0 to 360 degrees."
    )
    
    # Optional input parameters
    file_id = serializers.CharField(required=False, allow_null=True, help_text="File ID for solar resource")
    dataset = serializers.CharField(required=False, allow_null=True, help_text="The climate dataset to use")
    radius = serializers.IntegerField(required=False, allow_null=True, help_text="The search radius to use when searching for the closest climate data station (miles). Pass in radius=0 to use the closest station regardless of the distance.")
    timeframe = serializers.CharField(required=False, allow_null=True, help_text="Granularity of the output response (hourly or monthly). Default: hourly")
    dc_ac_ratio = serializers.FloatField(required=False, allow_null=True, help_text="DC to AC ratio. Default: 1.2")
    gcr = serializers.FloatField(required=False, allow_null=True, help_text="Ground coverage ratio. Range: 0.01-0.99, Default: 0.4")
    inv_eff = serializers.FloatField(required=False, allow_null=True, help_text="Inverter efficiency at rated power. Range: 90-99.5, Default: 96")
    bifaciality = serializers.FloatField(required=False, allow_null=True, help_text="The ratio of rear-side efficiency to front-side efficiency. Typically a value between 0.65 and 0.9 provided on the bifacial module datasheeet. Range: 0-1")
    albedo = serializers.FloatField(required=False, allow_null=True, help_text="Ground reflectance. A value of 0 would mean that the ground is completely non-reflective, and a value of 1 would mean that it is completely reflective. Range: 0-1")
    soiling = serializers.ListField(
        child=serializers.FloatField(min_value=0, max_value=100),
        required=False,
        allow_null=True,
        help_text="Reduction in incident solar irradiance caused by dust or other seasonal soiling of the module surface that reduce the radiation incident on the subarray. Monthly irradiance loss (%) for each month (12 values, Range: 0 - 100)"
    )
    
    # Station Info Fields
    station_lat = serializers.FloatField(required=False, allow_null=True, help_text="Latitude of the climate station")
    station_lon = serializers.FloatField(required=False, allow_null=True, help_text="Longitude of the climate station")
    elevation = serializers.FloatField(required=False, allow_null=True, help_text="Elevation of the climate station. (meters)")
    timezone = serializers.FloatField(required=False, allow_null=True, help_text="Timezone offset from GMT.")
    location = serializers.CharField(required=False, allow_null=True, help_text="ID of the climate station.")
    city = serializers.CharField(required=False, allow_null=True, help_text="City where climate station is located.")
    state = serializers.CharField(required=False, allow_null=True, help_text="State where climate station is located.")
    solar_resource_file = serializers.CharField(required=False, allow_null=True, help_text="Solar resource filename.")
    distance = serializers.IntegerField(required=False, allow_null=True, help_text="Distance between the input location and the climate station. (meters)")
    weather_data_source = serializers.CharField(required=False, allow_null=True, help_text="Weather data source")
    
    # Response Output Fields
    ac_annual = serializers.FloatField(required=False, allow_null=True, help_text="Annual AC system output. (kWhac)")
    solrad_annual = serializers.FloatField(required=False, allow_null=True, help_text="Annual solar radiation values. (kWh/m2/day)")
    capacity_factor = serializers.FloatField(required=False, allow_null=True, help_text="The ratio of the system's predicted electrical output in the first year of operation to the nameplate output, which is equivalent to the quantity of energy the system would generate if it operated at its nameplate capacity for every hour of the year. (AC-to-DC)")
    ac_monthly = serializers.ListField(child=serializers.FloatField(), required=False, allow_null=True, help_text="Monthly AC system output. (kWhac)")
    solrad_monthly = serializers.ListField(child=serializers.FloatField(), required=False, allow_null=True, help_text="Monthly solar radiation values. (kWh/m2/day)")
    poa_monthly = serializers.ListField(child=serializers.FloatField(), required=False, allow_null=True, help_text="Monthly plane of array irradiance values. (kWh/m2)")
    dc_monthly = serializers.ListField(child=serializers.FloatField(), required=False, allow_null=True, help_text="Monthly DC array output. (kWhdc)")

    def to_representation(self, instance):
        """Overriding function to re-structure response. This matches external NREL API response style with inputs, station_info, and outputs."""
        data = super().to_representation(instance)
        
        # Inputs object
        inputs = {
            "lat": data.get("latitude"),
            "lon": data.get("longitude"),
            "system_capacity": data.get("system_capacity"),
            "module_type": data.get("module_type"),
            "array_type": data.get("array_type"),
            "losses": data.get("losses"),
            "azimuth": data.get("azimuth"),
            "tilt": data.get("tilt"),
        }
        
        # Add optional input parameters
        optional_inputs = ["file_id", "dataset", "radius", "timeframe", "dc_ac_ratio", "gcr", "inv_eff", "bifaciality", "albedo", "soiling"]
        for field in optional_inputs:
            if data.get(field) is not None:
                inputs[field] = data.get(field)
        
        # Station_info object
        station_info = {
            "lat": data.get("station_lat"),
            "lon": data.get("station_lon"),
            "elev": data.get("elevation"),
            "tz": data.get("timezone"),
            "location": data.get("location"),
            "city": data.get("city"),
            "state": data.get("state"),
            "solar_resource_file": data.get("solar_resource_file"),
            "distance": data.get("distance"),
            "weather_data_source": data.get("weather_data_source"),
        }
        
        # Outputs object
        outputs = {
            "ac_annual": data.get("ac_annual"),
            "solrad_annual": data.get("solrad_annual"),
            "capacity_factor": data.get("capacity_factor"),
            "ac_monthly": data.get("ac_monthly"),
            "solrad_monthly": data.get("solrad_monthly"),
            "poa_monthly": data.get("poa_monthly"),
            "dc_monthly": data.get("dc_monthly"),
        }
        
        # Remove null values from all objects
        inputs = {key: value for key, value in inputs.items() if value is not None}
        station_info = {key: value for key, value in station_info.items() if value is not None}
        outputs = {key: value for key, value in outputs.items() if value is not None}
        
        return {
            "inputs": inputs,
            "station_info": station_info,
            "outputs": outputs,
        }

    def create(self, validated_data):
        return PVWattsCalculation(**validated_data)

