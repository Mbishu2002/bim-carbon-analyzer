import os
import ifcopenshell


class IFCImporter:

    def __init__(self, file_path):

        if isinstance(file_path, list):
            file_path = file_path[0]  # auto-fix list mistake

        self.file_path = file_path
        self.model = None


    def validate_file(self):
        """Check if file exists and is IFC format"""

        # Check existence
        if not os.path.exists(self.file_path):
            print(" ERROR: File does not exist.")
            return False

        # Check extension
        if not self.file_path.lower().endswith(".ifc"):
            print(" WARNING: File is not an IFC format.")
            print(" Please provide a valid .ifc file")
            return False

        print(" File validation passed (IFC format confirmed)")
        return True

    def load_model(self):
        """Load IFC model safely"""
        try:
            self.model = ifcopenshell.open(self.file_path)
            print(" IFC model loaded successfully")
            return True
        except Exception as e:
            print(" ERROR: Failed to load IFC model")
            print(f"Details: {e}")
            return False

    def get_schema(self):
        """Get IFC schema version"""
        if self.model is None:
            print(" ERROR: Model not loaded")
            return None

        schema = self.model.schema
        print(f" IFC Schema detected: {schema}")
        return schema

    def run(self):
        """Full pipeline execution"""
        print("\n===== IFC IMPORT MODULE =====")

        if not self.validate_file():
            return None

        if not self.load_model():
            return None

        schema = self.get_schema()

        print("\n===== SUMMARY =====")
        print(" Model ready for processing")
        print(f" Schema: {schema}")

        return self.model


# -------------------------
# TEST RUN
# -------------------------
if __name__ == "__main__":
    file_path = r"C:\Users\macpe\Documents\Masters Thesis\Modelling files\Revit test file\Wall_Test-1.ifc" # change this

    importer = IFCImporter(file_path)
    model = importer.run()