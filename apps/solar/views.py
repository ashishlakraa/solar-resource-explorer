import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .serializers import PVWattsCalculationSerializer, SolarResourceReadingSerializer
from .services import fetch_solar_resource_data, fetch_pvwatts_calculation


logger = logging.getLogger(__name__)

class SolarSiteViewSet(ViewSet):
    """ViewSet for solar site operations."""
    
    serializer_class = SolarResourceReadingSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="latitude",
                location=OpenApiParameter.QUERY,
                description="The latitude coordinate of the solar site",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="longitude",
                location=OpenApiParameter.QUERY,
                description="The longitude coordinate of the solar site",
                required=True,
                type=OpenApiTypes.FLOAT,
            )
        ],
        responses={200: SolarResourceReadingSerializer}
    )
    @action(detail=False, methods=["get"], url_path="detail")
    def solar_resource_data(self, request):
        """Get solar resource details."""
        
        logger.info(f"Received solar site detail request with query params: {request.query_params}")

        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")

        if latitude is None or longitude is None:
            logger.error(f"Missing required query parameters for solar resource data: latitude={latitude}, longitude={longitude}")
            return Response(
                {
                    "detail": "Query parameters 'latitude' and 'longitude' are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        result, status_code = fetch_solar_resource_data(float(latitude), float(longitude))

        if status_code != status.HTTP_200_OK:
            logger.error(f"Error fetching solar resource data for lat: {latitude}, lon: {longitude} with status code: {status_code}")
            return Response(
                {
                    "detail": f"Error fetching solar resource data for lat: {latitude}, lon: {longitude}"
                },
                status=status_code,
            )
        else:
            logger.info(f"Successfully fetched solar resource data for lat: {latitude}, lon: {longitude}")
            serializer = SolarResourceReadingSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="pvwatts-metadata")
    def pvwatts_metadata(self, request):
        """Get PVWatts calculator fields descriptions."""
        serializer = PVWattsCalculationSerializer()
        metadata = {}
        
        for field_name, field in serializer.fields.items():
            metadata[field_name] = {
                "help_text": field.help_text or "",
                "required": field.required,
                "read_only": field.read_only,
            }
        
        return Response(metadata, status=status.HTTP_200_OK)


    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="lat",
                location=OpenApiParameter.QUERY,
                description="The latitude for the location to use (Range: -90 to 90)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="lon",
                location=OpenApiParameter.QUERY,
                description="The longitude for the location to use (Range: -180 to 180)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="system_capacity",
                location=OpenApiParameter.QUERY,
                description="Nameplate capacity in kilowatts (Range: 0.05 to 500000)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="module_type",
                location=OpenApiParameter.QUERY,
                description="""Module type (Options: 0, 1, 2)
                0 = Standard
                1 = Premium
                2 = Thin film""",
                required=True,
                type=OpenApiTypes.INT,
                enum=[0, 1, 2]
            ),
            OpenApiParameter(
                name="losses",
                location=OpenApiParameter.QUERY,
                description="System losses in percent (Range: -5 to 99)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="array_type",
                location=OpenApiParameter.QUERY,
                description="""Array type (Options: 0, 1, 2, 3, 4)
                0 = Fixed - Open Rack
                1 = Fixed - Roof Mounted
                2 = Fixed - 1-Axis
                3 = Fixed - 1-Axis Backtracking
                4 = Fixed - 2-Axis""",
                required=True,
                type=OpenApiTypes.INT,
                enum=[0, 1, 2, 3, 4]
            ),
            OpenApiParameter(
                name="tilt",
                location=OpenApiParameter.QUERY,
                description="Tilt angle in degrees (Range: 0 to 90)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="azimuth",
                location=OpenApiParameter.QUERY,
                description="Azimuth angle in degrees (Range: 0 to 360)",
                required=True,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="dc_ac_ratio",
                location=OpenApiParameter.QUERY,
                description="DC to AC ratio (default: 1.2)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="inv_eff",
                location=OpenApiParameter.QUERY,
                description="Inverter efficiency at rated power (Range: 90 - 99.5, default: 96)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="gcr",
                location=OpenApiParameter.QUERY,
                description="Ground coverage ratio (Range: 0.01 - 0.99, default: 0.4)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="albedo",
                location=OpenApiParameter.QUERY,
                description="Ground reflectance (Range: 0 - 1)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="bifaciality",
                location=OpenApiParameter.QUERY,
                description="Ratio of rear-side efficiency to front-side efficiency (Range: 0 - 1)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="soiling",
                location=OpenApiParameter.QUERY,
                description="Monthly irradiance loss (%) as comma-separated array (12 values, Range: 0 - 100)",
                required=False,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200: PVWattsCalculationSerializer}
    )
    @action(detail=False, methods=["get"], url_path="pvwatts")
    def pvwatts(self, request, pk: int = None):
        """Calculate PVWatts production estimate for a solar site."""
        
        logger.info(f"Received PVWatts calculation request with query params: {request.query_params}")

        # Extract required parameters
        lat = request.query_params.get("lat")
        lon = request.query_params.get("lon")
        system_capacity = request.query_params.get("system_capacity")
        module_type = request.query_params.get("module_type")
        losses = request.query_params.get("losses")
        array_type = request.query_params.get("array_type")
        tilt = request.query_params.get("tilt")
        azimuth = request.query_params.get("azimuth")

        # Validate required parameters
        if any(param is None for param in [lat, lon, system_capacity, module_type, losses, array_type, tilt, azimuth]):
            logger.error(f"Missing required query parameters for PVWatts calculation: lat={lat}, lon={lon}, system_capacity={system_capacity}, module_type={module_type}, losses={losses}, array_type={array_type}, tilt={tilt}, azimuth={azimuth}")
            return Response(
                {
                    "detail": "Query parameters 'lat', 'lon', 'system_capacity', 'module_type', 'losses', 'array_type', 'tilt', and 'azimuth' are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract optional parameters
        dc_ac_ratio = request.query_params.get("dc_ac_ratio")
        inv_eff = request.query_params.get("inv_eff")
        gcr = request.query_params.get("gcr")
        albedo = request.query_params.get("albedo")
        bifaciality = request.query_params.get("bifaciality")
        soiling = request.query_params.get("soiling")

        # Convert to appropriate types
        try:
            lat = float(lat)
            lon = float(lon)
            system_capacity = float(system_capacity)
            module_type = int(module_type)
            losses = float(losses)
            array_type = int(array_type)
            tilt = float(tilt)
            azimuth = float(azimuth)
            
            # Convert optional parameters if provided
            dc_ac_ratio = float(dc_ac_ratio) if dc_ac_ratio is not None else None
            inv_eff = float(inv_eff) if inv_eff is not None else None
            gcr = float(gcr) if gcr is not None else None
            albedo = float(albedo) if albedo is not None else None
            bifaciality = float(bifaciality) if bifaciality is not None else None
            
            # Convert soiling from comma-separated string to list of floats
            if soiling is not None:
                try:
                    soiling = [float(val.strip()) for val in soiling.split(",")]
                    
                    # Validate if soiling list has exactly 12 values
                    if len(soiling) != 12:
                        return Response(
                            {
                                "detail": f"Soiling parameter must contain exactly 12 values (one per month), received {len(soiling)}"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                except (ValueError, TypeError) as e:
                    logger.error(f"Error converting soiling values: {str(e)}")
                    return Response(
                        {
                            "detail": f"Invalid soiling values: {str(e)}. Expected comma-separated list of 12 floats."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting parameter values: {str(e)}")
            return Response(
                {
                    "detail": f"Invalid parameter type: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        result, response_status = fetch_pvwatts_calculation(
            lat=lat,
            lon=lon,
            system_capacity=system_capacity,
            module_type=module_type,
            losses=losses,
            array_type=array_type,
            tilt=tilt,
            azimuth=azimuth,
            dc_ac_ratio=dc_ac_ratio,
            inv_eff=inv_eff,
            gcr=gcr,
            albedo=albedo,
            bifaciality=bifaciality,
            soiling=soiling,
        )

        if response_status != status.HTTP_200_OK:
            logger.error(f"Error fetching PVWatts calculation for lat: {lat}, lon: {lon} with status code: {response_status}")
            return Response(
                {
                    "detail": f"Error fetching PVWatts calculation for lat: {lat}, lon: {lon}"
                },
                status=response_status,
            )
        else:
            logger.info(f"Successfully fetched PVWatts calculation for lat: {lat}, lon: {lon} with system_capacity: {system_capacity}, module_type: {module_type}, losses: {losses}, array_type: {array_type}, tilt: {tilt}, azimuth: {azimuth}")
            serializer = PVWattsCalculationSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
