# Copyright (C) 2023-2024 Secure Dimensions GmbH, Munich, Germany.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from urllib.parse import urlparse

# STAplus 1.0 clause 13 media types for FeatureOfInterest and Location.encodingType.
# application/vnd.geo+json is the SensorThings 1.0 Table 8-6 ValueCode (STAplus extends STA 1.0).
ENCODING_TYPE_GEOJSON = 'application/geo+json'
ENCODING_TYPE_GEOJSON_VND = 'application/vnd.geo+json'
ENCODING_TYPE_JSON_FG = 'application/vnd.ogc.fg+json'
ENCODING_TYPE_WKT = 'application/wkt'
ENCODING_TYPES = (
    ENCODING_TYPE_GEOJSON,
    ENCODING_TYPE_GEOJSON_VND,
    ENCODING_TYPE_JSON_FG,
    ENCODING_TYPE_WKT,
)

_URI_SCHEME = re.compile(r'^[A-Za-z][A-Za-z0-9+.-]*$')
_URL_SCHEMES = ('http', 'https')


def is_uri(value):
    if not isinstance(value, str):
        return False
    value = value.strip()
    if not value or any(ch.isspace() for ch in value):
        return False
    parsed = urlparse(value)
    if not parsed.scheme or not _URI_SCHEME.fullmatch(parsed.scheme):
        return False
    if parsed.scheme.lower() in _URL_SCHEMES or parsed.scheme.lower() in ('ftp', 'ftps'):
        return bool(parsed.netloc)
    return bool(parsed.netloc or parsed.path)


def is_url(value):
    if not is_uri(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme.lower() in _URL_SCHEMES and bool(parsed.netloc)


def check_encoding_type(value, field_name='encodingType'):
    if value is None or value == '':
        return None
    if not isinstance(value, str):
        raise ValueError(f'{field_name} should be of type str!')
    if value not in ENCODING_TYPES:
        raise ValueError(
            f'{field_name} should be one of: {", ".join(ENCODING_TYPES)}'
        )
    return value


def check_uri(value, field_name='URI'):
    if value is None or value == '':
        return None
    if not isinstance(value, str):
        raise ValueError(f'{field_name} should be of type str!')
    if not is_uri(value):
        raise ValueError(f'{field_name} should be a URI!')
    return value


def check_url(value, field_name='URL'):
    if value is None or value == '':
        return None
    if not isinstance(value, str):
        raise ValueError(f'{field_name} should be of type str!')
    if not is_url(value):
        raise ValueError(f'{field_name} should be a URL!')
    return value
