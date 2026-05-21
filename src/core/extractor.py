import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom
import ifcopenshell.util.shape
import pandas as pd


class BIMMasterExtractor:
    """Extracts every IfcBuildingElement with classification, storey,
    material, area and volume into a flat DataFrame."""

    def __init__(self, model):
        self.model = model

        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_WORLD_COORDS, True)
        # ifcopenshell.geom returns geometry in SI metres regardless of the
        # IFC file's native length unit, so no extra scaling is needed.

    # -------------------------------------------------
    # CLASSIFICATION
    # -------------------------------------------------
    @staticmethod
    def classify_element(el):
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
        if "Stair" in t:
            return "STAIR"
        if "Roof" in t:
            return "ROOF"
        if "Door" in t:
            return "DOOR"
        if "Window" in t:
            return "WINDOW"
        return "OTHER"

    # -------------------------------------------------
    # STOREY
    # -------------------------------------------------
    @staticmethod
    def get_storey(el):
        try:
            if el.ContainedInStructure:
                for r in el.ContainedInStructure:
                    if r.is_a("IfcRelContainedInSpatialStructure"):
                        s = r.RelatingStructure
                        if s.is_a("IfcBuildingStorey"):
                            return s.Name or "Unnamed Storey"
        except Exception:
            pass
        return "Unknown"

    # -------------------------------------------------
    # MATERIAL
    # -------------------------------------------------
    @staticmethod
    def get_material(el):
        m = ifcopenshell.util.element.get_material(el)
        if not m:
            return "Unknown"
        if hasattr(m, "Name") and m.Name:
            return m.Name
        if m.is_a("IfcMaterialLayerSet") or m.is_a("IfcMaterialLayerSetUsage"):
            try:
                layers = m.MaterialLayers if hasattr(m, "MaterialLayers") else m.ForLayerSet.MaterialLayers
                names = [l.Material.Name for l in layers if l.Material and l.Material.Name]
                if names:
                    return " + ".join(names)
            except Exception:
                pass
        return "Composite"

    # -------------------------------------------------
    # GEOMETRY
    # -------------------------------------------------
    def _shape(self, el):
        return ifcopenshell.geom.create_shape(self.settings, el)

    def get_volume(self, el):
        try:
            shape = self._shape(el)
            return ifcopenshell.util.shape.get_volume(shape.geometry), "GEOM"
        except Exception:
            return None, "FAILED"

    def get_area(self, el):
        try:
            shape = self._shape(el)
            return shape.geometry.area, "GEOM"
        except Exception:
            return None, "FAILED"

    # -------------------------------------------------
    # MAIN EXTRACTION
    # -------------------------------------------------
    def extract(self, progress_cb=None):
        elements = self.model.by_type("IfcBuildingElement")
        total = len(elements)

        rows = []
        for i, el in enumerate(elements):
            try:
                category = self.classify_element(el)
                volume, v_src = self.get_volume(el)
                area, a_src = self.get_area(el)

                if category in ("SLAB", "WALL", "ROOF"):
                    quantity = area
                    unit = "m2"
                else:
                    quantity = volume
                    unit = "m3"

                rows.append({
                    "GUID": el.GlobalId,
                    "Name": getattr(el, "Name", None) or "",
                    "Element_Type": el.is_a(),
                    "Category": category,
                    "Storey": self.get_storey(el),
                    "Material": self.get_material(el),
                    "Quantity": quantity,
                    "Unit": unit,
                    "Volume_m3": volume,
                    "Area_m2": area,
                    "Geom_Source": v_src,
                })
            except Exception:
                continue

            if progress_cb is not None and total:
                progress_cb(int((i + 1) * 100 / total))

        return pd.DataFrame(rows)
