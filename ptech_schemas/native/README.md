# Native schemas

These files preserve the source-facing contract before normalization.

- Where official fields were verified from current documentation/data schemas, fields are copied by source name.
- Sources with many heterogeneous datasets (NESO, ENERGY STAR, Companies House XBRL, CEC workbook families) intentionally retain the raw source schema per release rather than forcing one guessed static schema here.
- A collector must store the exact raw artifact and release/API version. Normalization is disposable; raw evidence is not.
- Re-run source-schema discovery whenever an API/release changes and version the resulting native schema instead of overwriting it.
