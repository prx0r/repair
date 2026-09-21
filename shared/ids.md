# Canonical ID conventions

Never use mutable symbols/names as primary keys.

Format:

`<namespace>:<type>:<stable-value>`

Examples:

- `pow:device_model:<hash>`
- `gtin:product:5012345678900`
- `mpn:component:bosch-00631200`
- `eprel:model:1234567`
- `uk:soc2020:5241`
- `uk:lad:E08000003`
- `uk:company:01234567`
- `lei:entity:213800...`
- `figi:security:BBG...`
- `grid:substation:<operator>:<stable-id>`
- `doi:work:10.xxxx/...`
- `epo:publication:EP1234567A1`

## Identity rule

Aliases are edges, not overwrites.

A model can have:
- OEM model
- commercial name
- GTIN
- EPREL registration
- marketplace spelling
- distributor alias

Preserve all source-native identifiers.

## Entity-resolution confidence

- `1.0`: authoritative exact identifier match
- `0.95+`: exact MPN+brand or LEI/FIGI mapping
- `0.8–0.95`: high-quality normalized composite match
- `<0.8`: do not silently canonicalize; preserve candidate relationship
