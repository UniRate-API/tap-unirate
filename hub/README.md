# Meltano Hub metadata

These files stage the future PR to [`meltano/hub`](https://github.com/meltano/hub)
that lists `tap-unirate` on <https://hub.meltano.com>. **Do not** copy this
directory wholesale into the tap package's publish artifact — it exists only
to make the Hub PR mechanical.

## Layout

```
hub/
├── _data/
│   ├── default_variants.snippet.yml         # one line to add to hub's default_variants.yml
│   └── meltano/extractors/tap-unirate/
│       └── unirate-api.yml                   # the extractor definition (the variant file)
```

## How to open the Hub PR (later session)

1. Fork `meltano/hub`, branch off `main`.
2. Copy `_data/meltano/extractors/tap-unirate/unirate-api.yml` into the same
   path in the fork.
3. Add `tap-unirate: unirate-api` under `extractors:` in the fork's
   `_data/default_variants.yml`, preserving alphabetical order (see
   `default_variants.snippet.yml`).
4. Run the Hub repo's own validation (`make compile` / the JSON-schema check
   in their CI) before pushing.
5. Open the PR from `rob-browncc:add-tap-unirate` → `meltano:main`.

`quality: unknown` is correct for a brand-new tap — the Hub maintainers bump
quality tiers themselves.
