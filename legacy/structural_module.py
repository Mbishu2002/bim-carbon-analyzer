import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom
import ifcopenshell.util.shape
import pandas as pd


class IFCStructuralExtractor:

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

        print(" Structural Module Initialized")
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

                        if u.Prefix == "MILLI":
                            return 0.001

                        elif u.Prefix == "CENTI":
                            return 0.01

                        else:
                            return 1.0

        except:
            pass

        return 1.0

    # =====================================================
    # GET STRUCTURAL ELEMENTS ONLY
    # =====================================================
    def get_structural_elements(self):

        columns = list(
            self.model.by_type("IfcColumn")
        )

        beams = list(
            self.model.by_type("IfcBeam")
        )

        footings = list(
            self.model.by_type("IfcFooting")
        )

        print("\n===== STRUCTURAL DETECTION =====")
        print(f" Columns detected : {len(columns)}")
        print(f" Beams detected   : {len(beams)}")
        print(f" Footings detected: {len(footings)}")

        elements = columns + beams + footings

        print(f"\n Total Structural Elements: {len(elements)}")

        return elements

    # =====================================================
    # GET STOREY / LEVEL
    # =====================================================
    def get_storey(self, element):

        try:

            if element.ContainedInStructure:

                for rel in element.ContainedInStructure:

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
    def get_material(self, element):

        try:

            material = (
                ifcopenshell.util.element.get_material(
                    element
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
            # MATERIAL LIST
            # -------------------------------------------------
            if material.is_a("IfcMaterialList"):

                names = []

                for mat in material.Materials:

                    names.append(mat.Name)

                return ", ".join(names)

            # -------------------------------------------------
            # MATERIAL LAYER SET
            # -------------------------------------------------
            if hasattr(material, "MaterialLayers"):

                names = []

                for layer in material.MaterialLayers:

                    if layer.Material:

                        names.append(
                            layer.Material.Name
                        )

                return ", ".join(names)

            # -------------------------------------------------
            # MATERIAL PROFILE SET
            # -------------------------------------------------
            if hasattr(material, "MaterialProfiles"):

                names = []

                for profile in material.MaterialProfiles:

                    if profile.Material:

                        names.append(
                            profile.Material.Name
                        )

                return ", ".join(names)

        except:
            pass

        return "Unknown"

    # =====================================================
    # GET IFC QTO VOLUME
    # =====================================================
    def get_qto_volume(self, element):

        try:

            psets = (
                ifcopenshell.util.element.get_psets(
                    element
                )
            )

            for qto_name, qto_data in psets.items():

                if "Qto_" in qto_name:

                    # -----------------------------------------
                    # NET VOLUME
                    # -----------------------------------------
                    if "NetVolume" in qto_data:

                        volume = float(
                            qto_data["NetVolume"]
                        )

                        return (
                            volume,
                            "QTO_NetVolume"
                        )

                    # -----------------------------------------
                    # GROSS VOLUME
                    # -----------------------------------------
                    if "GrossVolume" in qto_data:

                        volume = float(
                            qto_data["GrossVolume"]
                        )

                        return (
                            volume,
                            "QTO_GrossVolume"
                        )

        except:
            pass

        return None, "NOT_FOUND"

    # =====================================================
    # GEOMETRY VOLUME FALLBACK
    # =====================================================
    def get_geometry_volume(self, element):

        try:

            shape = ifcopenshell.geom.create_shape(
                self.settings,
                element
            )

            geometry = shape.geometry

            raw_volume = (
                ifcopenshell.util.shape.get_volume(
                    geometry
                )
            )

            # ---------------------------------------------
            # SCALE TO m
            # ---------------------------------------------
            volume = raw_volume * (
                self.unit_scale ** 3
            )

            return volume, "GEOMETRY"

        except Exception as e:

            print(
                f" Geometry volume failed:"
                f" {element.GlobalId}"
            )

            print(e)

            return None, "FAILED"

    # =====================================================
    # GET FINAL VOLUME
    # =====================================================
    def get_volume(self, element):

        # -------------------------------------------------
        # 1. IFC QUANTITY
        # -------------------------------------------------
        volume, source = self.get_qto_volume(
            element
        )

        if volume is not None:

            return volume, source

        # -------------------------------------------------
        # 2. GEOMETRY FALLBACK
        # -------------------------------------------------
        volume, source = self.get_geometry_volume(
            element
        )

        return volume, source

    # =====================================================
    # MAIN EXTRACTION
    # =====================================================
    def extract(self):

        elements = (
            self.get_structural_elements()
        )

        rows = []

        print(
            "\n===== STARTING "
            "STRUCTURAL EXTRACTION ====="
        )

        for el in elements:

            try:

                # -----------------------------------------
                # BASIC INFO
                # -----------------------------------------
                guid = el.GlobalId

                element_class = el.is_a()

                name = (
                    el.Name
                    if el.Name
                    else "Unnamed"
                )

                type_obj = (
                    ifcopenshell.util.element.get_type(
                        el
                    )
                )

                element_type = (
                    type_obj.Name
                    if type_obj
                    and type_obj.Name
                    else "No Type"
                )

                storey = self.get_storey(el)

                material = self.get_material(el)

                # -----------------------------------------
                # VOLUME
                # -----------------------------------------
                volume, volume_source = (
                    self.get_volume(el)
                )

                # -----------------------------------------
                # STORE DATA
                # -----------------------------------------
                rows.append({

                    "GUID": guid,

                    "Element_Class":
                        element_class,

                    "Element_Name":
                        name,

                    "Element_Type":
                        element_type,

                    "Storey":
                        storey,

                    "Material":
                        material,

                    "Volume_m3":
                        volume,

                    "Volume_Source":
                        volume_source
                })

            except Exception as e:

                print(
                    f" Failed element:"
                    f" {el.GlobalId}"
                )

                print(e)

        # =================================================
        # DATAFRAME
        # =================================================
        df = pd.DataFrame(rows)

        print(
            "\n===== STRUCTURAL DATA "
            "PREVIEW ====="
        )

        if not df.empty:

            print(df.head(20))

        else:

            print(
                " No structural "
                "data extracted"
            )

        return df

    # =====================================================
    # EXPORT EXCEL
    # =====================================================
    def export_excel(
        self,
        df,
        filename="Structural_Quantities.xlsx"
    ):

        if df.empty:

            print(
                " No structural "
                "data to export"
            )

            return

        # -------------------------------------------------
        # GROUPED SUMMARY
        # -------------------------------------------------
        grouped = df.groupby(
            [
                "Storey",
                "Element_Class",
                "Material"
            ],
            as_index=False
        ).agg({
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
                sheet_name="Storey_Summary",
                index=False
            )

        print("\n Structural Excel Exported")
        print(f" File: {filename}")

    # =====================================================
    # VALIDATION CHECK
    # =====================================================
    def validate_results(self, df):

        print("\n===================================")
        print(" STRUCTURAL VALIDATION CHECK")
        print("===================================")

        if df.empty:

            print(" No data available")

            return

        print(df[[
            "Element_Class",
            "Element_Name",
            "Storey",
            "Material",
            "Volume_m3",
            "Volume_Source"
        ]].head(20))

        # -------------------------------------------------
        # NULL CHECK
        # -------------------------------------------------
        print("\n===== NULL VALUE CHECK =====")

        print(
            df.isnull().sum()
        )

        # -------------------------------------------------
        # ZERO VOLUME CHECK
        # -------------------------------------------------
        print("\n===== ZERO VOLUME CHECK =====")

        zero_volume = df[
            (
                df["Volume_m3"].isnull()
            )
            |
            (
                df["Volume_m3"] <= 0
            )
        ]

        print(
            f" Elements with invalid "
            f"volume: {len(zero_volume)}"
        )

        if not zero_volume.empty:

            print(
                zero_volume[[
                    "Element_Class",
                    "Element_Name",
                    "GUID"
                ]]
            )


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

    print("\n===================================")
    print(" STARTING STRUCTURAL MODULE TEST")
    print("===================================")

    # -----------------------------------------------------
    # LOAD MODEL
    # -----------------------------------------------------
    importer = IFCImporter(file_path)

    model = importer.run()

    # -----------------------------------------------------
    # RUN EXTRACTION
    # -----------------------------------------------------
    if model:

        extractor = IFCStructuralExtractor(
            model
        )

        df = extractor.extract()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
        extractor.validate_results(df)

        # -------------------------------------------------
        # EXPORT
        # -------------------------------------------------
        output_file = (
            "Structural_Quantities_Test.xlsx"
        )

        extractor.export_excel(
            df,
            filename=output_file
        )

        print("\n===================================")
        print(" STRUCTURAL TEST COMPLETE")
        print("===================================")

        print(f" Excel File: {output_file}")