# tap-unirate examples

## 1. Configure

Copy the sample config and drop in your key (get a free one at
<https://unirateapi.com>):

```bash
cp examples/config.sample.json config.json
# edit config.json → set "api_key"
```

`base_currency` is optional (defaults to `USD`) and only affects the
`exchange_rates` stream.

## 2. Discover the catalog

Run discovery to emit the tap's catalog (all three streams and their
JSON schemas) to stdout:

```bash
tap-unirate --config config.json --discover > catalog.json
```

The catalog contains the `currencies`, `exchange_rates`, and `vat_rates`
streams. Edit it to `select`/deselect streams as you like.

## 3. Sync records (Singer stream)

Emit `SCHEMA` and `RECORD` messages for every selected stream:

```bash
tap-unirate --config config.json
```

Pipe it to any Singer target, e.g.:

```bash
tap-unirate --config config.json | target-jsonl
```

## 4. With Meltano

```bash
meltano add extractor tap-unirate
meltano config tap-unirate set api_key $UNIRATE_API_KEY
meltano config tap-unirate set base_currency USD
meltano invoke tap-unirate --discover
meltano run tap-unirate target-jsonl
```
