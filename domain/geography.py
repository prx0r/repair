"""Geography — canonical hierarchical UK geography.

Different datasets use different geographic units:
  - Jobs: postcode
  - Grid: DNO/GSP
  - Planning: LAD
  - Apprenticeships: provider/site
  - Labour: LAD/region

This module resolves between them.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GeoLevel(Enum):
    COUNTRY = "country"
    NATION = "nation"
    REGION = "region"
    ITL = "itl"                     # International Territorial Level
    LOCAL_AUTHORITY = "local_authority"
    WARD = "ward"
    POSTCODE_AREA = "postcode_area"  # e.g. "M", "B", "LS"
    POSTCODE_DISTRICT = "postcode_district"  # e.g. "M1", "B1"
    POSTCODE_SECTOR = "postcode_sector"  # e.g. "M1 1"
    POSTCODE = "postcode"
    LAT_LON = "lat_lon"
    DNO = "dno"                     # Distribution Network Operator
    GSP = "gsp"                     # Grid Supply Point
    ISCHRONE = "isochrone"          # Travel time


@dataclass
class Geography:
    """A geographic location with hierarchical resolution."""
    geo_id: str                    # canonical ID, e.g. "LAD:E08000003"
    name: str
    level: GeoLevel

    # Hierarchy (parent references)
    parent_id: str = ""
    country: str = "England"
    nation: str = ""
    region: str = ""
    itl: str = ""
    local_authority: str = ""
    postcode_area: str = ""

    # Coordinates
    lat: float = 0.0
    lon: float = 0.0

    # Grid mapping
    dno: str = ""
    gsp: str = ""

    # Mappings to other systems
    ons_code: str = ""
    gss_code: str = ""


class GeographyResolver:
    """Resolves between different geographic systems."""

    def __init__(self):
        self.geographies: dict[str, Geography] = {}
        self._postcode_index: dict[str, str] = {}  # postcode -> geo_id
        self._lad_index: dict[str, str] = {}       # gss_code -> geo_id
        self._dno_index: dict[str, list] = {}      # dno -> [geo_ids]

    def register(self, geo: Geography):
        self.geographies[geo.geo_id] = geo
        if geo.postcode_area:
            self._postcode_index[geo.postcode_area] = geo.geo_id
        if geo.gss_code:
            self._lad_index[geo.gss_code] = geo.geo_id
        if geo.dno:
            if geo.dno not in self._dno_index:
                self._dno_index[geo.dno] = []
            self._dno_index[geo.dno].append(geo.geo_id)

    def resolve_postcode_area(self, postcode_area: str) -> Optional[Geography]:
        geo_id = self._postcode_index.get(postcode_area.upper())
        return self.geographies.get(geo_id) if geo_id else None

    def resolve_lad(self, gss_code: str) -> Optional[Geography]:
        geo_id = self._lad_index.get(gss_code)
        return self.geographies.get(geo_id) if geo_id else None

    def resolve_dno(self, dno: str) -> list:
        geo_ids = self._dno_index.get(dno, [])
        return [self.geographies[gid] for gid in geo_ids]

    def get_hierarchy(self, geo_id: str) -> list:
        """Return full hierarchy from geo_id up to country."""
        geo = self.geographies.get(geo_id)
        if not geo:
            return []
        chain = [geo]
        current = geo
        while current.parent_id and current.parent_id in self.geographies:
            current = self.geographies[current.parent_id]
            chain.append(current)
        return chain


# ============================================================
# UK GEOGRAPHY TABLE — regions and local authorities
# ============================================================

UK_GEOGRAPHY = GeographyResolver()

# Nations
UK_GEOGRAPHY.register(Geography("nation:england", "England", GeoLevel.NATION, parent_id="country:uk"))
UK_GEOGRAPHY.register(Geography("nation:wales", "Wales", GeoLevel.NATION, parent_id="country:uk"))
UK_GEOGRAPHY.register(Geography("nation:scotland", "Scotland", GeoLevel.NATION, parent_id="country:uk"))
UK_GEOGRAPHY.register(Geography("nation:ni", "Northern Ireland", GeoLevel.NATION, parent_id="country:uk"))
UK_GEOGRAPHY.register(Geography("country:uk", "United Kingdom", GeoLevel.COUNTRY))

# Regions
UK_GEOGRAPHY.register(Geography("region:london", "London", GeoLevel.REGION, parent_id="nation:england"))
UK_GEOGRAPHY.register(Geography("region:south_east", "South East", GeoLevel.REGION, parent_id="nation:england"))
UK_GEOGRAPHY.register(Geography("region:south_west", "South West", GeoLevel.REGION, parent_id="nation:england"))
UK_GEOGRAPHY.register(Geography("region:midlands", "Midlands", GeoLevel.REGION, parent_id="nation:england"))
UK_GEOGRAPHY.register(Geography("region:north_west", "North West", GeoLevel.REGION, parent_id="nation:england"))
UK_GEOGRAPHY.register(Geography("region:north_east", "North East", GeoLevel.REGION, parent_id="nation:england"))
UK_GEOGRAPHY.register(Geography("region:yorkshire", "Yorkshire and the Humber", GeoLevel.REGION, parent_id="nation:england"))

# Key Local Authorities
UK_GEOGRAPHY.register(Geography("LAD:E08000003", "Manchester", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.4808, lon=-2.2426, gss_code="E08000003"))
UK_GEOGRAPHY.register(Geography("LAD:E08000006", "Birmingham", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:midlands", lat=52.4862, lon=-1.8904, gss_code="E08000006"))
UK_GEOGRAPHY.register(Geography("LAD:E08000001", "Barnsley", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:yorkshire", lat=53.5526, lon=-1.4797, gss_code="E08000001"))
UK_GEOGRAPHY.register(Geography("LAD:E08000002", "Coventry", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:midlands", lat=52.4068, lon=-1.5197, gss_code="E08000002"))
UK_GEOGRAPHY.register(Geography("LAD:E08000004", "Sandwell", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:midlands", lat=52.5363, lon=-1.9914, gss_code="E08000004"))
UK_GEOGRAPHY.register(Geography("LAD:E08000005", "Solihull", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:midlands", lat=52.4128, lon=-1.774, gss_code="E08000005"))
UK_GEOGRAPHY.register(Geography("LAD:E08000007", "Bradford", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:yorkshire", lat=53.793, lon=-1.752, gss_code="E08000007"))
UK_GEOGRAPHY.register(Geography("LAD:E08000008", "Calderdale", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:yorkshire", lat=53.7239, lon=-1.862, gss_code="E08000008"))
UK_GEOGRAPHY.register(Geography("LAD:E08000009", "Doncaster", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:yorkshire", lat=53.5228, lon=-1.1284, gss_code="E08000009"))
UK_GEOGRAPHY.register(Geography("LAD:E08000010", "Dudley", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:midlands", lat=52.509, lon=-2.088, gss_code="E08000010"))
UK_GEOGRAPHY.register(Geography("LAD:E08000011", "Gateshead", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_east", lat=54.962, lon=-1.601, gss_code="E08000011"))
UK_GEOGRAPHY.register(Geography("LAD:E08000012", "Kirklees", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:yorkshire", lat=53.6476, lon=-1.7673, gss_code="E08000012"))
UK_GEOGRAPHY.register(Geography("LAD:E08000013", "Knowsley", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.4346, lon=-2.8375, gss_code="E08000013"))
UK_GEOGRAPHY.register(Geography("LAD:E08000014", "Leeds", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:yorkshire", lat=53.8008, lon=-1.5491, gss_code="E08000014"))
UK_GEOGRAPHY.register(Geography("LAD:E08000015", "Liverpool", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.4084, lon=-2.9916, gss_code="E08000015"))
UK_GEOGRAPHY.register(Geography("LAD:E08000016", "Newcastle", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_east", lat=54.9783, lon=-1.6178, gss_code="E08000016"))
UK_GEOGRAPHY.register(Geography("LAD:E08000017", "Nottingham", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:midlands", lat=52.9548, lon=-1.1581, gss_code="E08000017"))
UK_GEOGRAPHY.register(Geography("LAD:E08000018", "Oldham", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.5409, lon=-2.1114, gss_code="E08000018"))
UK_GEOGRAPHY.register(Geography("LAD:E08000019", "Rochdale", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.6164, lon=-2.1575, gss_code="E08000019"))
UK_GEOGRAPHY.register(Geography("LAD:E08000020", "Rotherham", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:yorkshire", lat=53.4326, lon=-1.3635, gss_code="E08000020"))
UK_GEOGRAPHY.register(Geography("LAD:E08000021", "Salford", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.4875, lon=-2.2901, gss_code="E08000021"))
UK_GEOGRAPHY.register(Geography("LAD:E08000022", "Sefton", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.3958, lon=-3.0222, gss_code="E08000022"))
UK_GEOGRAPHY.register(Geography("LAD:E08000023", "Sheffield", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:yorkshire", lat=53.3811, lon=-1.4701, gss_code="E08000023"))
UK_GEOGRAPHY.register(Geography("LAD:E08000024", "St Helens", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.4531, lon=-2.737, gss_code="E08000024"))
UK_GEOGRAPHY.register(Geography("LAD:E08000025", "Sunderland", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_east", lat=54.9069, lon=-1.3838, gss_code="E08000025"))
UK_GEOGRAPHY.register(Geography("LAD:E08000026", "Tameside", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.4808, lon=-2.0629, gss_code="E08000026"))
UK_GEOGRAPHY.register(Geography("LAD:E08000027", "Trafford", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.4225, lon=-2.3486, gss_code="E08000027"))
UK_GEOGRAPHY.register(Geography("LAD:E08000028", "Walsall", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:midlands", lat=52.5862, lon=-1.9774, gss_code="E08000028"))
UK_GEOGRAPHY.register(Geography("LAD:E08000029", "Wigan", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:north_west", lat=53.5448, lon=-2.6318, gss_code="E08000029"))
UK_GEOGRAPHY.register(Geography("LAD:E08000030", "Wolverhampton", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:midlands", lat=52.587, lon=-2.1288, gss_code="E08000030"))
UK_GEOGRAPHY.register(Geography("LAD:E08000031", "Barnet", GeoLevel.LOCAL_AUTHORITY,
    parent_id="region:london", lat=51.6523, lon=-0.2028, gss_code="E08000031"))

# Postcode areas
UK_GEOGRAPHY.register(Geography("postcode_area:M", "Manchester", GeoLevel.POSTCODE_AREA,
    parent_id="LAD:E08000018", lat=53.4808, lon=-2.2426))
UK_GEOGRAPHY.register(Geography("postcode_area:B", "Birmingham", GeoLevel.POSTCODE_AREA,
    parent_id="LAD:E08000006", lat=52.4862, lon=-1.8904))
UK_GEOGRAPHY.register(Geography("postcode_area:LS", "Leeds", GeoLevel.POSTCODE_AREA,
    parent_id="LAD:E08000014", lat=53.8008, lon=-1.5491))
UK_GEOGRAPHY.register(Geography("postcode_area:L", "Liverpool", GeoLevel.POSTCODE_AREA,
    parent_id="LAD:E08000015", lat=53.4084, lon=-2.9916))
UK_GEOGRAPHY.register(Geography("postcode_area:S", "Sheffield", GeoLevel.POSTCODE_AREA,
    parent_id="LAD:E08000023", lat=53.3811, lon=-1.4701))
UK_GEOGRAPHY.register(Geography("postcode_area:NE", "Newcastle", GeoLevel.POSTCODE_AREA,
    parent_id="LAD:E08000016", lat=54.9783, lon=-1.6178))
UK_GEOGRAPHY.register(Geography("postcode_area:NG", "Nottingham", GeoLevel.POSTCODE_AREA,
    parent_id="LAD:E08000017", lat=52.9548, lon=-1.1581))
