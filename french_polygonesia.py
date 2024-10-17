# Attempt to turn
# https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000048234967
# into geoJSON.

import requests
import bs4
import re
from shapely import to_geojson
from shapely.geometry.polygon import orient
from shapely.geometry import Point, Polygon, MultiPolygon, GeometryCollection
import json
from string import ascii_uppercase


id_matcher = re.compile(r"\d{3}-\d{3}")

# Please have a look at the data before assuming this re is overkill.
lll_chunker = re.compile(
    r"^(?P<spam>.*\D : )?(?P<label>[\d\w]+)\s+:\s*(?P<lon>[^<]*)\s*/\s*(?P<lat>[^<]*)"
)


# We strip spaces out before this re sees these strings
dms_chunker = re.compile(
    r'^(?P<d>\d+)°(?P<m>\d+)[′\'](?P<s>[\d,\.]+)["”\']*(?P<h>[NSEOW])?'
)


def dms_to_d(dms):
    dms = dms_chunker.match(dms)
    d = float(dms.group("d"))
    m = float(dms.group("m"))
    s = float(dms.group("s").replace(",", "."))
    d += m / 60
    d += s / (60 * 60)
    if dms.group("h") in ["S", "W", "O"]:
        d *= -1
    return d


def parse_polygon(t):
    lines = t.split("<br/>")

    polygons = []
    points = []

    i = 0  # line counter
    # Polygons are labeled with a number per line. We use that as a check.
    for line in lines:
        line = line.strip()
        if "Zone " in line:
            if len(points) > 2:
                polygons.append(Polygon(points))
            points = []
            i = 0
            continue

        match = lll_chunker.match(line)
        if not match:
            # FIXME: check rejects
            continue

        label = match.group("label")

        longitude = match.group("lon").replace(" ", "")
        latitude = match.group("lat").replace(" ", "")

        label_number = str(i + 1)
        label_letter = ascii_uppercase[i % len(ascii_uppercase)]
        if label not in [label_number, label_letter]:
            # FIXME: warn that there's a numbering error
            pass

        longitude = dms_to_d(longitude)
        latitude = dms_to_d(latitude)

        points.append(Point(longitude, latitude))
        i += 1

    if len(points) > 2:
        polygons.append(Polygon(points))

    polygons = [orient(p, 1.0) for p in polygons]

    return MultiPolygon(polygons)


def parse_site(tr):
    # FIXME: properly insert properties into polygon
    keys = "number", "commune", "name", "department", "polygon", "ministry", "aerozone"
    raw_values = tr.find_all("td")
    values = [v.text for v in raw_values]
    site = dict(zip(keys, values))
    site["polygon"] = parse_polygon(str(raw_values[4]))
    # site["polygon"]["properties"] = {
    #     "number": site["number"],
    #     "ministry": site["ministry"],
    #     "name": site["name"],
    # }
    return site["polygon"]


l_URI = "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000048234967"
html = requests.get(l_URI).content
soup = bs4.BeautifulSoup(html, "html.parser")

# Find every <tr /> on the page that has what looks like a site ID in it.
# This is extremely sloppy but I trust that this is truly one-off code.
site_rows = [tr for tr in soup.select("tr") if id_matcher.match(tr.text)]

sites = [parse_site(row) for row in site_rows]

sites = to_geojson(GeometryCollection(sites))

print(sites)
