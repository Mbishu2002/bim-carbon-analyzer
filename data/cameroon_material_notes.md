# Cameroon material notes

This file records the internet research used to align `lca_database.csv` more closely with Cameroon construction practice.

## What was updated

- Corrected the `Cement` volumetric factor from `820000` to `820` kgCO2e/m3.
- Kept material names in English for the user-facing database.
- Added English entries for common Cameroon wall and earth materials:
  - `Concrete Block`
  - `Compressed Earth Block`
  - `Laterite Block`
  - `Adobe`
- Added Cameroon-relevant cement product aliases:
  - `CIMENCAM MULTIX`
  - `CIMENCAM ROBUST`
  - `CIMENCAM HYDRO`
  - `CIMENCAM KOSTO`
  - `CIMENCAM SUBLIM`
- Added cement products from other companies active in Cameroon:
  - `Dangote Cement 32.5R`
  - `Dangote 3X Cement 42.5R`
  - `Dangote Cement 52.5`
  - `CIMAF Cement 42.5R`
  - `Medcem Cement 42.5R`
  - `Medcem Cement 35`
  - `Mira Cement 42.5R`
  - `CIMPOR Cement 42.5R`
  - `CIMPOR Cement 32.5`
- Added roofing materials commonly manufactured or used in Cameroon:
  - `Aluzinc Sheet`
  - `Galvanized Steel Sheet`
  - `Roofing Sheet`
  - `Metal Roofing`
  - `Aluminium Roofing Sheet`
  - `Micro-Concrete Roofing Tile`
  - `Concrete Roof Tile`

## Sources consulted

1. CIMENCAM official product page
   - https://www.cimencam.com/fr/produits-et-services
   - Confirms Cameroon-market cement families and that cement is used for blocks (`parpaings`), pavers and concrete.

2. Dangote Cameroon official operations page
   - https://www.dangotecement.com/cameroon/
   - Confirms Cameroon operation and locally sold grades `32.5R CEM II`, `42.5R` and `52.5 CEM I`.

3. MIRA Cement product page
   - https://mira-cement.com/nos-produits-et-services/
   - Confirms `MIRA CO CEMII 42.5R`.

4. CIMPOR Cameroon official pages
   - https://cimporcameroun.com/fr
   - https://cimporcameroun.com/en/83/cem-i-425-r
   - Confirms CIMPOR Cameroon operations and cement products.

5. Medcem official group page
   - https://medcem.com.tr/
   - Confirms Medcem has active mills in Douala, Cameroon.

6. CIMAF Cameroon / group pages
   - https://cimaf.xdesign.ma/implantations/cameroun
   - https://www.cimafgh.com/about-us
   - Confirms CIMAF operates in Cameroon.

7. CIMENCAM company page
   - https://www.cimencam.com/fr/propos-de-nous
   - Confirms CIMENCAM as a major Cameroon construction-material producer.

8. Building Potentials of Stabilized Earth Blocks in Yaounde and Douala (Cameroon)
   - https://catalog.ihsn.org/citations/79708
   - Confirms compressed earth blocks are a relevant Cameroon wall material.

9. Assessment of Soils Developed on Various Formations in Maroua (Far North, Cameroon) for Production of Compressed Earth Bricks
   - https://www.scirp.org/journal/paperinformation?paperid=125785
   - Confirms lateritic soils in Cameroon are suitable for compressed earth brick production.

10. Evaluating Thermal Performance and Environmental Impact of Compressed Earth Blocks with Cocos and Canarium Aggregates: A Study in Douala, Cameroon
   - https://orbi.uliege.be/handle/2268/307353
   - Uses hollow cement block as the reference wall system in Douala, supporting its importance in practice.

11. Typology of Local Construction Materials from the Adamawa and North-West Regions of Cameroon
   - https://file.scirp.org/Html/2-1110126_65809.htm
   - Confirms lateritic soils and other local materials are part of the Cameroon construction material base.

12. Ferrocam official site
   - https://ferrocam.cm/en/
   - Confirms local manufacture/transformation of aluzinc and galvanized steel sheets in Cameroon.

13. Physico-Mechanical Characterisation of Micro-Concrete Roofing Tiles Produced from Bambui (North West Cameroon) and Garoua I (North Cameroon) River Sands
   - https://www.researchgate.net/publication/379899892_Physico-Mechanical_Characterisation_of_Micro-Concrete_Roofing_Tiles_Produced_from_Bambui_North_West_Cameroon_and_Garoua_I_North_Cameroon_River_Sands
   - Confirms micro-concrete roofing tiles are used in Cameroon housing practice.

14. SCNB Woodlink official site
   - https://www.scnbwoodlink.com/
   - Confirms Ayous, Iroko and Sapelli/Sapele are traded Cameroon timber species.

## Assumptions

- Cameroon-specific third-party EPDs were not available for most products, so imported industrial materials still use proxy embodied-carbon factors already present in the database.
- New French/local aliases usually reuse the factor of the parent material they map to.
- Roofing sheet entries were mapped to steel or aluminium proxy factors depending on the sheet type.
