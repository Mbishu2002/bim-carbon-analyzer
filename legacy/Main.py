from IFCImporter import IFCImporter
from BIMMasterExtractor import BIMMasterExtractor
import pandas as pd


class BIMProcessor:

    def __init__(self, ifc_path):
        self.ifc_path = ifc_path
        self.model = None

    def load_ifc(self):

        importer = IFCImporter(self.ifc_path)
        self.model = importer.run()

        if not self.model:
            raise Exception("IFC load failed")

    def run_all(self):

        print("\n BIM PIPELINE START")

        self.load_ifc()

        extractor = BIMMasterExtractor(self.model)
        df = extractor.extract()

        print("\n===== CLEAN DATA PREVIEW =====")
        print(df.head())

        self.export(df)

        return df

    def export(self, df):

        with pd.ExcelWriter("BIM_Master_Quantities.xlsx", engine="openpyxl") as writer:

            df.to_excel(writer, sheet_name="MASTER_TABLE", index=False)

            df.groupby(["Category", "Material", "Unit"]).agg({
                "Quantity": "sum"
            }).to_excel(writer, sheet_name="CARBON_INPUT", index=True)

        print(" Excel exported: BIM_Master_Quantities.xlsx")