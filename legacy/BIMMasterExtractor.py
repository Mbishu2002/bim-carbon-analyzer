import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom
import ifcopenshell.util.shape
import pandas as pd


class BIMMasterExtractor:

    def __init__(self, model):

        self.model = model

        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_WORLD_COORDS, True)

        self.unit_scale = self.get_unit_scale()

    # -------------------------------------------------
    # UNIT SYSTEM
    # -------------------------------------------------
    def get_unit_scale(self):

        try:
            units = self.model.by_type("IfcUnitAssignment")

            for u in units[0].Units:
                if u.is_a("IfcSIUnit") and u.UnitType == "LENGTHUNIT":
                    if u.Prefix == "MILLI":
                        return 0.001
                    if u.Prefix == "CENTI":
                        return 0.01
                    return 1.0
        except:
            pass

        return 1.0

    # -------------------------------------------------
    # CLASSIFICATION ENGINE (KEY FIX)
    # -------------------------------------------------
    def classify_element(self, el):

        t = el.is_a()

        if "Wall" in t:
            return "WALL"

        if "Slab" in t:
            return "SLAB"

        if "Beam" in t:
            return "BEAM"

        if "Column" in t:
            return "COLUMN"

        if "Footing" in t or "Pile" in t:
            return "FOOTING"

        return "OTHER"

    # -------------------------------------------------
    # STOREY
    # -------------------------------------------------
    def get_storey(self, el):

        try:
            if el.ContainedInStructure:
                for r in el.ContainedInStructure:
                    if r.is_a("IfcRelContainedInSpatialStructure"):
                        s = r.RelatingStructure
                        if s.is_a("IfcBuildingStorey"):
                            return s.Name
        except:
            pass

        return "Unknown"

    # -------------------------------------------------
    # MATERIAL
    # -------------------------------------------------
    def get_material(self, el):

        m = ifcopenshell.util.element.get_material(el)

        if not m:
            return "Unknown"

        if hasattr(m, "Name"):
            return m.Name

        return "Composite"

    # -------------------------------------------------
    # GEOMETRY VOLUME
    # -------------------------------------------------
    def get_volume(self, el):

        try:
            shape = ifcopenshell.geom.create_shape(self.settings, el)
            geom = shape.geometry
            v = ifcopenshell.util.shape.get_volume(geom)
            return v * (self.unit_scale ** 3), "GEOM"
        except:
            return None, "FAILED"

    # -------------------------------------------------
    # GEOMETRY AREA (for slabs/walls)
    # -------------------------------------------------
    def get_area(self, el):

        try:
            shape = ifcopenshell.geom.create_shape(self.settings, el)
            a = shape.geometry.area
            return a * (self.unit_scale ** 2), "GEOM"
        except:
            return None, "FAILED"

    # -------------------------------------------------
    # MAIN EXTRACTION
    # -------------------------------------------------
    def extract(self):

        elements = self.model.by_type("IfcBuildingElement")

        rows = []

        for el in elements:

            try:

                category = self.classify_element(el)

                guid = el.GlobalId
                storey = self.get_storey(el)
                material = self.get_material(el)

                volume, v_src = self.get_volume(el)
                area, a_src = self.get_area(el)

                # -------------------------------------------------
                # QUANTITY LOGIC (CRITICAL FOR CARBON ENGINE)
                # -------------------------------------------------
                if category in ["SLAB", "WALL"]:

                    quantity = area
                    unit = "m2"

                else:

                    quantity = volume
                    unit = "m3"

                rows.append({

                    "GUID": guid,
                    "Element_Type": el.is_a(),
                    "Category": category,
                    "Storey": storey,
                    "Material": material,

                    "Quantity": quantity,
                    "Unit": unit,

                    "Volume_m3": volume,
                    "Area_m2": area,

                    "Source": v_src
                })

            except:
                continue

        return pd.DataFrame(rows)