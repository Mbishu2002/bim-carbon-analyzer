import pandas as pd
from pathlib import Path


class CarbonCalculator:

    def __init__(self, lca_csv_path=None):

        if lca_csv_path is None:
            lca_csv_path = Path(__file__).parent / "lca_database.csv"

        self.lca = pd.read_csv(lca_csv_path)

    # -------------------------------------------------
    # MATERIAL MATCHING (case + whitespace tolerant)
    # -------------------------------------------------
    def _match_index(self, material_name):
        """Return the row index of the best-matching LCA entry."""

        fallback_idx = self.lca.index[self.lca["Material"] == "Unknown"][0]

        if not isinstance(material_name, str) or not material_name.strip():
            return fallback_idx

        name = material_name.strip().lower()

        for idx, key in self.lca["Material"].items():
            k = str(key).strip().lower()
            if k == name or k in name or name in k:
                return idx

        return fallback_idx

    # -------------------------------------------------
    # MAIN CALCULATION
    # -------------------------------------------------
    def calculate(self, df):
        """
        Joins the extractor output (per-element rows) with LCA factors and
        returns the same dataframe enriched with:
          - EC_factor_kgCO2e_per_m3
          - Density_kg_per_m3
          - Mass_kg
          - EmbodiedCarbon_kgCO2e
        """

        if df.empty:
            return df.assign(
                EC_factor_kgCO2e_per_m3=pd.Series(dtype=float),
                Density_kg_per_m3=pd.Series(dtype=float),
                Mass_kg=pd.Series(dtype=float),
                EmbodiedCarbon_kgCO2e=pd.Series(dtype=float),
            )

        enriched = df.copy()

        idx = enriched["Material"].map(self._match_index)

        enriched["EC_factor_kgCO2e_per_m3"] = (
            self.lca["EC_factor_kgCO2e_per_m3"].reindex(idx).to_numpy()
        )
        enriched["Density_kg_per_m3"] = (
            self.lca["Density_kg_per_m3"].reindex(idx).to_numpy()
        )

        # Volume_m3 is populated for every element by BIMMasterExtractor.
        # Carbon = Volume * EC factor (kgCO2e / m3).
        vol = pd.to_numeric(enriched["Volume_m3"], errors="coerce")

        enriched["Mass_kg"] = vol * enriched["Density_kg_per_m3"]
        enriched["EmbodiedCarbon_kgCO2e"] = vol * enriched["EC_factor_kgCO2e_per_m3"]

        return enriched

    # -------------------------------------------------
    # SUMMARY VIEWS
    # -------------------------------------------------
    @staticmethod
    def totals_by(df, group_cols):
        if df.empty:
            return pd.DataFrame(columns=group_cols + ["EmbodiedCarbon_kgCO2e"])

        return (
            df.groupby(group_cols, dropna=False)["EmbodiedCarbon_kgCO2e"]
            .sum()
            .reset_index()
            .sort_values("EmbodiedCarbon_kgCO2e", ascending=False)
        )
