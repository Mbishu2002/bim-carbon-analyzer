import os
import ifcopenshell


class IFCImporter:
    """Loads an IFC file and exposes the parsed ifcopenshell model."""

    def __init__(self, file_path):

        if isinstance(file_path, list):
            file_path = file_path[0]

        self.file_path = file_path
        self.model = None
        self.schema = None

    def validate_file(self):
        if not os.path.exists(self.file_path):
            return False, "File does not exist"

        if not self.file_path.lower().endswith(".ifc"):
            return False, "File is not an IFC (.ifc) file"

        return True, "OK"

    def load_model(self):
        try:
            self.model = ifcopenshell.open(self.file_path)
            self.schema = self.model.schema
            return True, self.schema
        except Exception as e:
            return False, str(e)

    def run(self):
        ok, msg = self.validate_file()
        if not ok:
            raise FileNotFoundError(msg)

        ok, info = self.load_model()
        if not ok:
            raise RuntimeError(f"Failed to load IFC model: {info}")

        return self.model
