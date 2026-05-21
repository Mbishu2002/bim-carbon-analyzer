import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom
import ifcopenshell.util.shape
import pandas as pd


class IFCSlabExtractor:

    # =====================================================
    # INITIALIZATION
    # =====================================================
    def __init__(self, model):

        self.model = model

        self.settings = ifcopenshell.geom.settings()
        self.settings.set(
            self.settings.USE_WORLD_COORDS,
            True
        )

        # -------------------------------------------------
        # UNIT SCALE
        # -------------------------------------------------
        self.unit_scale = self.get_unit_scale()

        print(" Slab Module Initialized")
        print(f" Unit Scale to meters: {self.unit_scale}")

    # =====================================================
    # IFC UNIT DETECTION
    # =====================================================
    def get_unit_scale(self):

        try:

            units = self.model.by_type(
                "IfcUnitAssignment"
            )

            for unit in units:

                for u in unit.Units:

                    if (
                        u.is_a("IfcSIUnit")
                        and u.UnitType == "LENGTHUNIT"
                    ):

                        print("\n===== IFC UNIT DETECTION =====")
                        print(f"Unit Name : {u.Name}")
                        print(f"Prefix    : {u.Prefix}")

                        if u.Prefix == "MILLI":
                            return 0.001

                        elif u.Prefix == "CENTI":
                            return 0.01

                        else:
                            return 1.0

        except Exception as e:

            print(" Unit detection failed")
            print(e)

        return 1.0

    # =====================================================
    # GET IFC SLABS ONLY
    # =====================================================
    def get_slabs(self):

        slabs = list(
            self.model.by_type("IfcSlab")
        )

        print("\n===== SLAB DETECTION =====")
        print(f" IfcSlab detected: {len(slabs)}")

        return slabs

    # =====================================================
    # GET STOREY
    # =====================================================
    def get_storey(self, slab):

        try:

            if slab.ContainedInStructure:

                for rel in slab.ContainedInStructure:

                    if rel.is_a(
                        "IfcRelContainedInSpatialStructure"
                    ):

                        storey = rel.RelatingStructure

                        if storey.is_a(
                            "IfcBuildingStorey"
                        ):

                            return storey.Name

        except:
            pass

        return "Unknown Storey"

    # =====================================================
    # GET MATERIAL
    # =====================================================
    def get_material(self, slab):

        try:

            material = (
                ifcopenshell.util.element.get_material(
                    slab
                )
            )

            if not material:
                return "Unknown"

            # -------------------------------------------------
            # SINGLE MATERIAL
            # -------------------------------------------------
            if material.is_a("IfcMaterial"):

                return material.Name

            # -------------------------------------------------
            # MATERIAL LAYER SET USAGE
            # -------------------------------------------------
            if material.is_a(
                "IfcMaterialLayerSetUsage"
            ):

                layer_set = material.ForLayerSet

                names = []

                for layer in layer_set.MaterialLayers:

                    if layer.Material:

                        names.append(
                            layer.Material.Name
                        )

                return ", ".join(names)

            # -------------------------------------------------
            # MATERIAL LAYER SET
            # -------------------------------------------------
            if material.is_a(
                "IfcMaterialLayerSet"
            ):

                names = []

                for layer in material.MaterialLayers:

                    if layer.Material:

                        names.append(
                            layer.Material.Name
                        )

                return ", ".join(names)

        except:
            pass

        return "Unknown"

    # =====================================================
    # GET AREA
    # =====================================================
    def get_area(self, slab):

        # -------------------------------------------------
        # IFC QUANTITY
        # -------------------------------------------------
        try:

            psets = (
                ifcopenshell.util.element.get_psets(
                    slab
                )
            )

            for qto_name, qto_data in psets.items():

                if "Qto_SlabBaseQuantities" in qto_name:

                    if "NetArea" in qto_data:

                        return (
                            float(
                                qto_data["NetArea"]
                            ),
                            "QTO_NetArea"
                        )

                    if "GrossArea" in qto_data:

                        return (
                            float(
                                qto_data["GrossArea"]
                            ),
                            "QTO_GrossArea"
                        )

        except:
            pass

        # -------------------------------------------------
        # GEOMETRY FALLBACK
        # -------------------------------------------------
        try:

            shape = ifcopenshell.geom.create_shape(
                self.settings,
                slab
            )

            geometry = shape.geometry

            raw_area = geometry.area

            # SCALE TO m
            area = raw_area * (
                self.unit_scale ** 2
            )

            return area, "GEOMETRY"

        except Exception as e:

            print(f" Area failed: {slab.GlobalId}")
            print(e)

            return None, "FAILED"

    # =====================================================
    # GET THICKNESS
    # =====================================================
    def get_thickness(self, slab):

        # -------------------------------------------------
        # MATERIAL LAYERS
        # -------------------------------------------------
        try:

            material = (
                ifcopenshell.util.element.get_material(
                    slab
                )
            )

            # ---------------------------------------------
            # MATERIAL LAYER SET USAGE
            # ---------------------------------------------
            if material.is_a(
                "IfcMaterialLayerSetUsage"
            ):

                layer_set = material.ForLayerSet

                total = 0

                for layer in layer_set.MaterialLayers:

                    total += layer.LayerThickness

                total *= self.unit_scale

                return total, "MATERIAL_LAYER_USAGE"

            # ---------------------------------------------
            # MATERIAL LAYER SET
            # ---------------------------------------------
            if material.is_a(
                "IfcMaterialLayerSet"
            ):

                total = 0

                for layer in material.MaterialLayers:

                    total += layer.LayerThickness

                total *= self.unit_scale

                return total, "MATERIAL_LAYER_SET"

        except:
            pass

        # -------------------------------------------------
        # QTO THICKNESS
        # -------------------------------------------------
        try:

            psets = (
                ifcopenshell.util.element.get_psets(
                    slab
                )
            )

            for qto_name, qto_data in psets.items():

                if "Qto_SlabBaseQuantities" in qto_name:

                    if "Thickness" in qto_data:

                        thickness = float(
                            qto_data["Thickness"]
                        )

                        thickness *= self.unit_scale

                        return (
                            thickness,
                            "QTO_Thickness"
                        )

        except:
            pass

        return None, "NOT_FOUND"

    # =====================================================
    # GET VOLUME
    # =====================================================
    def get_volume(self, slab):

        # -------------------------------------------------
        # IFC QTO VOLUME
        # -------------------------------------------------
        try:

            psets = (
                ifcopenshell.util.element.get_psets(
                    slab
                )
            )

            for qto_name, qto_data in psets.items():

                if "Qto_SlabBaseQuantities" in qto_name:

                    if "NetVolume" in qto_data:

                        return (
                            float(
                                qto_data["NetVolume"]
                            ),
                            "QTO_NetVolume"
                        )

                    if "GrossVolume" in qto_data:

                        return (
                            float(
                                qto_data["GrossVolume"]
                            ),
                            "QTO_GrossVolume"
                        )

        except:
            pass

        # -------------------------------------------------
        # GEOMETRY FALLBACK
        # -------------------------------------------------
        try:

            shape = ifcopenshell.geom.create_shape(
                self.settings,
                slab
            )

            geometry = shape.geometry

            raw_volume = (
                ifcopenshell.util.shape.get_volume(
                    geometry
                )
            )

            # SCALE TO m
            volume = raw_volume * (
                self.unit_scale ** 3
            )

            return volume, "GEOMETRY"

        except Exception as e:

            print(f" Volume failed: {slab.GlobalId}")
            print(e)

            return None, "FAILED"

    # =====================================================
    # MAIN EXTRACTION
    # =====================================================
    def extract(self):

        slabs = self.get_slabs()

        rows = []

        print("\n===== STARTING SLAB EXTRACTION =====")

        for slab in slabs:

            try:

                guid = slab.GlobalId

                name = (
                    slab.Name
                    if slab.Name
                    else "Unnamed Slab"
                )

                storey = self.get_storey(slab)

                material = self.get_material(slab)

                area, area_source = (
                    self.get_area(slab)
                )

                thickness, thickness_source = (
                    self.get_thickness(slab)
                )

                volume, volume_source = (
                    self.get_volume(slab)
                )

                rows.append({

                    "GUID": guid,

                    "Slab_Name": name,

                    "Storey": storey,

                    "Material": material,

                    "Area_m2": area,

                    "Area_Source": area_source,

                    "Thickness_m": thickness,

                    "Thickness_Source":
                        thickness_source,

                    "Volume_m3": volume,

                    "Volume_Source":
                        volume_source
                })

            except Exception as e:

                print(
                    f" Failed slab: {slab.GlobalId}"
                )

                print(e)

        # =================================================
        # DATAFRAME
        # =================================================
        df = pd.DataFrame(rows)

        print("\n===== SLAB DATA PREVIEW =====")

        if not df.empty:

            print(df.head())

        else:

            print(" No slab data extracted")

        return df

    # =====================================================
    # EXPORT TO EXCEL
    # =====================================================
    def export_excel(
        self,
        df,
        filename="Slab_Quantities.xlsx"
    ):

        if df.empty:

            print(" No slab data to export")
            return

        # -------------------------------------------------
        # GROUPING
        # -------------------------------------------------
        grouped = df.groupby(
            ["Storey", "Material"],
            as_index=False
        ).agg({
            "Area_m2": "sum",
            "Volume_m3": "sum"
        })

        # -------------------------------------------------
        # EXPORT
        # -------------------------------------------------
        with pd.ExcelWriter(
            filename,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                sheet_name="Detailed",
                index=False
            )

            grouped.to_excel(
                writer,
                sheet_name="Storey_Material",
                index=False
            )

        print("\n Slab Excel Exported")
        print(f" File: {filename}")


# =========================================================
# STANDALONE TEST
# =========================================================
if __name__ == "__main__":

    from IFCImporter import IFCImporter

    # -----------------------------------------------------
    # IFC FILE PATH
    # -----------------------------------------------------
    file_path = (
        r"C:\Users\macpe\Documents\Masters Thesis"
        r"\Modelling files\Tekla\Tekla_v0.ifc"
    )

    # -----------------------------------------------------
    # LOAD IFC MODEL
    # -----------------------------------------------------
    print("\n===================================")
    print(" STARTING SLAB MODULE TEST")
    print("===================================")

    importer = IFCImporter(file_path)

    model = importer.run()

    # -----------------------------------------------------
    # RUN EXTRACTION
    # -----------------------------------------------------
    if model:

        extractor = IFCSlabExtractor(model)

        df = extractor.extract()

        # -------------------------------------------------
        # VALIDATION PREVIEW
        # -------------------------------------------------
        print("\n===================================")
        print(" SLAB VALIDATION CHECK")
        print("===================================")

        if not df.empty:

            print(df[[
                "Slab_Name",
                "Storey",
                "Material",
                "Area_m2",
                "Thickness_m",
                "Volume_m3"
            ]].head(20))

            # ---------------------------------------------
            # BASIC VALIDATION
            # ---------------------------------------------
            print("\n===================================")
            print(" BASIC VALIDATION")
            print("===================================")

            for index, row in df.head(10).iterrows():

                area = row["Area_m2"]
                thickness = row["Thickness_m"]
                volume = row["Volume_m3"]

                print("\n-------------------------")
                print(f"SLAB: {row['Slab_Name']}")

                print(f"Area      : {area}")
                print(f"Thickness : {thickness}")
                print(f"Volume    : {volume}")

                # -----------------------------------------
                # EXPECTED VOLUME CHECK
                # -----------------------------------------
                if (
                    area is not None
                    and thickness is not None
                    and volume is not None
                ):

                    expected_volume = (
                        area * thickness
                    )

                    difference = abs(
                        expected_volume - volume
                    )

                    print(
                        f"Expected Volume: "
                        f"{expected_volume:.4f}"
                    )

                    print(
                        f"Difference: "
                        f"{difference:.4f}"
                    )

                    if difference < 0.05:

                        print(" VALID")

                    else:

                        print(" CHECK VOLUME")

                else:

                    print(
                        " Missing values "
                        "for validation"
                    )

        else:

            print(" No slab data extracted")

        # -------------------------------------------------
        # EXPORT EXCEL
        # -------------------------------------------------
        output_file = "Slab_Quantities_Test.xlsx"

        extractor.export_excel(
            df,
            filename=output_file
        )

        print("\n===================================")
        print(" TEST COMPLETE")
        print("===================================")

        print(f" Excel File: {output_file}")