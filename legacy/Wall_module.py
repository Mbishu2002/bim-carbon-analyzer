import ifcopenshell
import pandas as pd
import ifcopenshell.util.element
import ifcopenshell.geom


class IFCWallExtractor:

    def __init__(self, model):
        self.ifc_path = model
        self.model = model

        print(f" IFC Loaded | Schema: {self.model.schema}")

        # geometry settings (critical for consistent results)
        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_WORLD_COORDS, True)

        self.unit_scale = self.get_ifc_unit_scale()

    # -------------------------------------------------
    # UNIT SYSTEM (CRITICAL FOR ACCURACY)
    # -------------------------------------------------
    def get_ifc_unit_scale(self):
        """Convert IFC units to meters"""
        units = self.model.by_type("IfcUnitAssignment")

        for unit in units:
            for u in unit.Units:
                if u.is_a("IfcSIUnit") and u.UnitType == "LENGTHUNIT":

                    if u.Prefix == "MILLI":
                        return 0.001
                    elif u.Prefix == "CENTI":
                        return 0.01
                    else:
                        return 1.0

        return 1.0

    # -------------------------------------------------
    # WALL SELECTION (ONLY WALLS)
    # -------------------------------------------------
    def get_walls(self):
        """Extract only walls from IFC"""
        walls = self.model.by_type("IfcWall") + self.model.by_type("IfcWallStandardCase")
        print(f" Walls found: {len(walls)}")
        return walls

    # -------------------------------------------------
    # STOREY (LEVEL)
    # -------------------------------------------------
    def get_wall_storey(self, wall):
        """Get building level of wall"""
        if hasattr(wall, "ContainedInStructure") and wall.ContainedInStructure:
            for rel in wall.ContainedInStructure:
                if rel.is_a("IfcRelContainedInSpatialStructure"):
                    storey = rel.RelatingStructure
                    if storey and storey.is_a("IfcBuildingStorey"):
                        return storey.Name
        return "Unknown Storey"

    # -------------------------------------------------
    # WALL AREA (QTO + GEOMETRY FALLBACK)
    # -------------------------------------------------
    def get_wall_area(self, wall):

        qtos = ifcopenshell.util.element.get_psets(wall)

        # 1. QTO METHOD (BEST IF AVAILABLE)
        for qto_name, qto_data in qtos.items():
            if "Qto_WallBaseQuantities" in qto_name:

                if "NetSideArea" in qto_data:
                    return float(qto_data["NetSideArea"]), "QTO_Net"

                if "GrossSideArea" in qto_data:
                    return float(qto_data["GrossSideArea"]), "QTO_Gross"

        # 2. GEOMETRY METHOD (FALLBACK)
        try:
            shape = ifcopenshell.geom.create_shape(self.settings, wall)
            area = shape.geometry.area * (self.unit_scale ** 2)
            return float(area), "GEOMETRY"

        except Exception as e:
            print(f" Area failed for {wall.GlobalId}: {e}")
            return None, "FAILED"

    # -------------------------------------------------
    # MATERIAL LAYERS EXTRACTION
    # -------------------------------------------------
    def get_wall_layers(self, wall):

        layers = []

        if not hasattr(wall, "HasAssociations"):
            return layers

        for rel in wall.HasAssociations:
            if rel.is_a("IfcRelAssociatesMaterial"):

                material = rel.RelatingMaterial

                layer_set = None

                if material.is_a("IfcMaterialLayerSetUsage"):
                    layer_set = material.ForLayerSet

                elif material.is_a("IfcMaterialLayerSet"):
                    layer_set = material

                if layer_set and hasattr(layer_set, "MaterialLayers"):

                    for layer in layer_set.MaterialLayers:

                        name = layer.Material.Name if layer.Material else "Unknown"
                        thickness_m = layer.LayerThickness * self.unit_scale
                        thickness_mm = thickness_m * 1000

                        layers.append({
                            "material": name,
                            "thickness_m": thickness_m,
                            "thickness_mm": thickness_mm
                        })

        return layers

    # -------------------------------------------------
    # MAIN PROCESSOR
    # -------------------------------------------------
    def extract(self):

        walls = self.get_walls()

        rows = []

        for wall in walls:

            guid = wall.GlobalId
            storey = self.get_wall_storey(wall)

            area, area_source = self.get_wall_area(wall)

            wall_type = ifcopenshell.util.element.get_type(wall)
            wall_name = wall_type.Name if wall_type and wall_type.Name else "Unnamed Wall"

            layers = self.get_wall_layers(wall)

            # If no layers  still store wall
            if not layers:

                rows.append({
                    "Wall_GUID": guid,
                    "Wall_Name": wall_name,
                    "Storey": storey,
                    "Area_m2": area,
                    "Area_Source": area_source,
                    "Material": "No Material",
                    "Thickness_m": None,
                    "Thickness_mm": None,
                    "Volume_m3": None
                })

            # If layered wall
            for layer in layers:

                volume = area * layer["thickness_m"] if area else None

                rows.append({
                    "Wall_GUID": guid,
                    "Wall_Name": wall_name,
                    "Storey": storey,
                    "Area_m2": area,
                    "Area_Source": area_source,
                    "Material": layer["material"],
                    "Thickness_m": layer["thickness_m"],
                    "Thickness_mm": layer["thickness_mm"],
                    "Volume_m3": volume
                })

        return pd.DataFrame(rows)

    # -------------------------------------------------
    # EXPORT
    # -------------------------------------------------
    def export_excel(self, df, filename="Wall_Quantities.xlsx"):

        df_group_material = df.groupby(
            ["Wall_Name", "Material"], as_index=False
        ).agg({"Area_m2": "sum", "Volume_m3": "sum"})

        df_group_storey = df.groupby(
            ["Storey", "Material"], as_index=False
        ).agg({"Area_m2": "sum", "Volume_m3": "sum"})

        with pd.ExcelWriter(filename, engine="openpyxl") as writer:

            df.to_excel(writer, sheet_name="Detailed", index=False)
            df_group_material.to_excel(writer, sheet_name="Wall_Material", index=False)
            df_group_storey.to_excel(writer, sheet_name="Storey_Material", index=False)

        print(f" Exported: {filename}")


# -------------------------------------------------
# RUN MODULE
# -------------------------------------------------
if __name__ == "__main__":

    path = r"C:\Users\macpe\Documents\Masters Thesis\Modelling files\Revit test file\Wall_Test-1.ifc"

    extractor = IFCWallExtractor(path)

    df = extractor.extract()

    print("\n===== PREVIEW =====")
    print(df.head())

    extractor.export_excel(df)