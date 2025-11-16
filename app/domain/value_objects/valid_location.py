from shapely.geometry import Point

class ValidLocation:
    def __init__(self, lat: float, lon: float, boundary):
        point = Point(lon, lat)
        if not boundary.contains(point):
            raise ValueError()
        self.lat = lat
        self.lon = lon

    def to_dict(self):
        return [self.lat, self.lon]