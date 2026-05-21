from Main import BIMProcessor
import pandas as pd


if __name__ == "__main__":

    ifc_files = [
        r"C:\Users\macpe\Documents\Masters Thesis\Modelling files\Tekla\Tekla_v0.ifc",
        r"C:\Users\macpe\Documents\Masters Thesis\Modelling files\Revit test file\Wall_Test-1.ifc"
    ]

    all_data = []

    for path in ifc_files:

        print("\n===================================")
        print(f" PROCESSING: {path}")
        print("===================================")

        processor = BIMProcessor(path)
        df = processor.run_all()

        if not df.empty:
            all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)

    final_df.to_excel("FINAL_CARBON_DATASET.xlsx", index=False)

    print("\n===== FINAL SUMMARY =====")
    print(final_df.groupby("Category")[["Quantity"]].sum())