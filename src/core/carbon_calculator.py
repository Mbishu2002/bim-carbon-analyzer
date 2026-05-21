from pathlib import Path

import pandas as pd

from src.core.paths import resource_path


class CarbonCalculator:
    """Joins extractor output with the LCA database to compute embodied
    carbon per element."""

    def __init__(self, lca_csv_path=None):
        if lca_csv_path is None:
            lca_csv_path = resource_path("data/lca_database.csv")
        self.lca = pd.read_csv(lca_csv_path)
        self._fallback_idx = self.lca.index[self.lca["Material"] == "Unknown"][0]

        # Pre-sort keys by length (descending) so the most specific match wins
        # e.g. "Concrete Masonry Units" -> "Masonry", not "Concrete".
        self._keys_sorted = sorted(
            [(idx, str(k).strip().lower()) for idx, k in self.lca["Material"].items()],
            key=lambda x: len(x[1]),
            reverse=True,
        )

    # -------------------------------------------------
    # MATERIAL MATCHING (case + whitespace tolerant, longest-match wins)
    # -------------------------------------------------
    def _match_index(self, material_name):
        if not isinstance(material_name, str) or not material_name.strip():
            return self._fallback_idx

        name = material_name.strip().lower()

        # 1. Exact match first.
        for idx, k in self._keys_sorted:
            if k == name:
                return idx

        # 2. Longest substring match (key contained in material name).
        for idx, k in self._keys_sorted:
            if k and k in name:
                return idx

        # 3. Reverse: material name contained in key (short element name vs
        # long DB key) - last resort.
        for idx, k in self._keys_sorted:
            if name and name in k:
                return idx

        return self._fallback_idx

    # -------------------------------------------------
    # LOOKUP HELPERS (used by the mapping UI)
    # -------------------------------------------------
    def available_materials(self) -> list[str]:
        """Sorted list of all LCA database entries (for the override
        dropdown)."""
        return sorted(self.lca["Material"].astype(str).tolist())

    def factor_for(self, lca_material: str) -> tuple[float, float]:
        """Return (EC_factor_kgCO2e_per_m3, Density_kg_per_m3) for an exact
        LCA material name. Falls back to the Unknown row."""
        matches = self.lca[self.lca["Material"] == lca_material]
        row = matches.iloc[0] if not matches.empty else self.lca.iloc[self._fallback_idx]
        return float(row["EC_factor_kgCO2e_per_m3"]), float(row["Density_kg_per_m3"])

    def suggest(self, ifc_material: str) -> str:
        """Auto-suggest an LCA material name for a raw IFC material."""
        idx = self._match_index(ifc_material)
        return str(self.lca.loc[idx, "Material"])

    # -------------------------------------------------
    # MAIN CALCULATION
    # -------------------------------------------------
    def calculate(self, df, material_map: dict[str, str] | None = None):
        """Enrich `df` with EC factor / mass / embodied carbon columns.

        material_map: optional {raw_ifc_material -> exact_lca_material}. When
        provided, each row uses the user-chosen LCA entry rather than the
        fuzzy auto-match.
        """
        if df.empty:
            return df.assign(
                Mapped_Material=pd.Series(dtype=str),
                EC_factor_kgCO2e_per_m3=pd.Series(dtype=float),
                Density_kg_per_m3=pd.Series(dtype=float),
                Mass_kg=pd.Series(dtype=float),
                EmbodiedCarbon_kgCO2e=pd.Series(dtype=float),
            )

        enriched = df.copy()

        if material_map:
            mapped_names = enriched["Material"].map(
                lambda m: material_map.get(m, self.suggest(m))
            )
        else:
            mapped_names = enriched["Material"].map(self.suggest)

        enriched["Mapped_Material"] = mapped_names

        # Look up factors by the (now exact) Mapped_Material name.
        factor_lookup = self.lca.set_index("Material")
        ec = mapped_names.map(
            lambda n: float(factor_lookup.loc[n, "EC_factor_kgCO2e_per_m3"])
            if n in factor_lookup.index
            else float(self.lca.loc[self._fallback_idx, "EC_factor_kgCO2e_per_m3"])
        )
        dens = mapped_names.map(
            lambda n: float(factor_lookup.loc[n, "Density_kg_per_m3"])
            if n in factor_lookup.index
            else float(self.lca.loc[self._fallback_idx, "Density_kg_per_m3"])
        )

        enriched["EC_factor_kgCO2e_per_m3"] = ec.to_numpy()
        enriched["Density_kg_per_m3"] = dens.to_numpy()

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
