"""
field addition to the rest_framework.fields

ref: https://github.com/djangonauts/django-rest-framework-gis
"""

from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.contrib.gis.gdal import OGRException
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from rest_framework.fields import WritableField, ImageField

import json

class GeometryField(WritableField):
    """
    A field to handle GeoDjango Geometry fields. 
    
    This is useful when you don't want to use the default rest_framework
    representation of Geometry Fields.
    For example:
    * By default rest_framework's serializer will output a model's PointField(),
      called `location`, will be output as 
        "location": "POINT(-123.0208 44.0464)"
    * However using this GeometryField() in the serializer will output that the
      same PointField() as:
        "location": {
            "type": "Point",
            "coordinates": [-123.0208, 44.0464]
        }
    """
    type_name = 'GeometryField'
    type_label = 'geometry'

    def to_native(self, value):
        if isinstance(value, dict) or value is None:
            return value

        # Get GeoDjango geojson serialization and then convert it _back_ to
        # a Python object
        return json.loads(value.geojson)

    def from_native(self, value):
        if value == '' or value is None:
            return value

        if isinstance(value, dict):
            value = json.dumps(value)

        try:
            return GEOSGeometry(value)
        except (ValueError, GEOSException, OGRException, TypeError) as e:
            raise ValidationError(_('Invalid format: string or unicode input unrecognized as WKT EWKT, and HEXEWKB.'))

        return value


class ImageField(ImageField):
    """
    Customized version of Django rest framework's ImageField that returns the
    absolute url property as opposed to the relative path to the media root
    """
    def to_native(self, value):
        if value:
            request = self.context.get('request', None)
            return request.build_absolute_uri(value.url)
        else:
            return super(ImageField, self).to_native(value)
