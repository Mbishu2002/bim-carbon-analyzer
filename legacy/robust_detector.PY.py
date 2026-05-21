import ifcopenshell
import ifcopenshell.geom
import numpy as np


class RobustElementDetector:

    def __init__(self, model):

        self.model = model

        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_WORLD_COORDS, True)

        print(" Robust Detector Initialized")

    # -------------------------------------------------
    # GEOMETRY ANALYSIS
    # -------------------------------------------------
    def get_geometry(self, element):

        try:
            shape = ifcopenshell.geom.create_shape(self.settings, element)
            geom = shape.geometry

            bbox = geom.bbox

            x = bbox.max.x - bbox.min.x
            y = bbox.max.y - bbox.min.y
            z = bbox.max.z - bbox.min.z

            return x, y, z

        except:
            return None

    # -------------------------------------------------
    # CLASSIFY ELEMENT BY GEOMETRY
    # -------------------------------------------------
    def classify_by_geometry(self, element):

        dims = self.get_geometry(element)

        if not dims:
            return "UNKNOWN"

        x, y, z = dims

        # SLAB: wide + thin
        if z < x and z < y:
            return "SLAB"

        # WALL: tall vertical element
        if z > x and z > y:
            return "WALL"

        # COLUMN: tall but narrow footprint
        if z > 2 * max(x, y):
            return "COLUMN"

        # BEAM: horizontal elongated
        if max(x, y) > z:
            return "BEAM"

        return "UNKNOWN"

    # -------------------------------------------------
    # MAIN DETECTION FUNCTION
    # -------------------------------------------------
    def detect_all(self):

        walls = []
        slabs = []
        beams = []
        columns = []

        all_elements = self.model.by_type("IfcProduct")

        for el in all_elements:

            if not hasattr(el, "GlobalId"):
                continue

            # STEP 1: Semantic detection
            if el.is_a("IfcWall"):
                walls.append(el)
                continue

            if el.is_a("IfcSlab"):
                slabs.append(el)
                continue

            if el.is_a("IfcBeam"):
                beams.append(el)
                continue

            if el.is_a("IfcColumn"):
                columns.append(el)
                continue

            # STEP 2: Proxy handling
            if el.is_a("IfcBuildingElementProxy"):

                cls = self.classify_by_geometry(el)

                if cls == "WALL":
                    walls.append(el)
                elif cls == "SLAB":
                    slabs.append(el)
                elif cls == "BEAM":
                    beams.append(el)
                elif cls == "COLUMN":
                    columns.append(el)

        print("\n===== DETECTION SUMMARY =====")
        print("Walls:", len(walls))
        print("Slabs:", len(slabs))
        print("Beams:", len(beams))
        print("Columns:", len(columns))

        return {
            "walls": walls,
            "slabs": slabs,
            "beams": beams,
            "columns": columns
        }