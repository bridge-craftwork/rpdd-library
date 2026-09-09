# rpdd-library

Richard Pavlicek's double-dummy tables for 10,485,760 solved bridge deals,
published as chunks a program can fetch one of, with a manifest describing them.

The deals are not here, and do not need to be. They are a pure function of their
index, and [rpdd-reader] is that function. This repository is the half that is
genuinely data.

## Attribution

**The data is Richard Pavlicek's.** He created 10,485,760 random deals and
solved each one twenty ways — almost two years of computer time — then
published the results for anyone to use. © 2007 Richard Pavlicek.

| | |
|---|---|
| His site | [rpbridge.net](https://www.rpbridge.net/) |
| Where he serves it | [Bridge Utilities](https://www.rpbridge.net/rput.htm) |
| The download | [`rpdd.zip`](https://www.rpbridge.net/z/rpdd.zip) — 47 MiB, holding the tables and `xxdd.exe`, his Windows program that recreates the deals |
| His documentation | [`rpdd.txt`](https://www.rpbridge.net/d/rpdd.txt) |

> In the early 2000s I created a database of 10,485,760 random deals. That was
> easy. The daunting task was to solve each deal 20 times to determine the
> double-dummy makes for each hand in each strain, which required almost two
> years of computer time.

He published it "as a courtesy to other programmers and data addicts". This
repository exists to make that courtesy easier to accept: the tables served in
pieces a browser can fetch, and the deals computed rather than shipped.

**Nothing here replaces his site.** If you want the library itself, get it from
him.

### Licensing, stated plainly

`rpdd.txt` carries a copyright notice and an offer of download. It is not a
licence, and it says nothing about redistribution. **Republishing the tables
here goes beyond what he has explicitly granted**, and permission has been
requested — see [the issues](https://github.com/bridge-craftwork/rpdd-library/issues).
Until that is answered, `data/` is published on the reading that mirroring a
freely-offered resource in a more usable shape serves his stated intent. If he
would rather it were not, it comes down.

His distribution as it arrives — `rpdd.zip`, `rpdd.zdd`, `rpdd.zrd`, `rpdd.bat`
and `xxdd.exe` — is deliberately git-ignored and is not republished whole.
`xxdd.exe` least of all, being his program rather than his data.

The [rpdd-reader] crate is a separate question, which is part of why it is a
separate repository: it is our own code, reproducing an algorithm from its
published behaviour, and it carries no data at all.

## What is here

| | |
|---|---|
| `data/zdd/` | the double-dummy tables, 160 chunks of 655,360 bytes |
| `data/manifest.json` | the layout: chunk paths, deal ranges, SHA-256 of each and of the whole |
| `docs/rpdd.txt` | Pavlicek's own documentation of the library |
| `scripts/split-zdd.py` | splitting his `rpdd.zdd` into chunks, and verifying them |

## Use it

The entry point is the manifest, served from Cloudflare Pages:

```
https://rpdd-library.pages.dev/manifest.json
```

```json
{
  "schema": 1,
  "record_bytes": 10,
  "deals_per_chunk": 65536,
  "total_deals": 10485760,
  "chunks": [ { "file": "zdd/rpdd-000.zdd", "first_deal": 0,
                "deals": 65536, "bytes": 655360, "sha256": "…" }, … ]
}
```

Chunk paths are relative to the manifest, so resolving them against the URL it
came from finds the chunks. The deal at index *i* is at byte
`(i % deals_per_chunk) * record_bytes` of the chunk whose `first_deal` covers
it — worked out from the manifest, never from constants baked into a consumer.

Easiest is not to do that yourself. [rpdd-reader] takes "deals from index *N*"
and hands back the URLs it needs:

```rust
use rpdd_reader::{Library, LibraryError, RPDD_MANIFEST};

let mut library = Library::at(RPDD_MANIFEST);
let zrd = loop {
    match library.zrd(deal_index, count) {
        Ok(bytes) => break bytes,
        Err(LibraryError::Needs(urls)) => for url in urls {
            library.supply(&url, fetch(&url))?;    // however you fetch
        },
        Err(other) => return Err(other.into()),
    }
};
```

Reading the chunks from GitHub rather than Pages works too and always will; it
is simply slower.

## Rebuilding from the original

```bash
# Unzip rpdd.zip from rpbridge.net into this directory, then:
scripts/split-zdd.py split      # rpdd.zdd -> data/zdd/ + manifest
scripts/split-zdd.py verify     # digests, and that the chunks rejoin
```

## Where the detail lives

[docs/design.md](docs/design.md) — why the chunks are the size they are, why the
manifest describes itself, why it is served from Pages rather than raw GitHub,
and which two response headers a browser consumer depends on.

## Related

- [rpdd-reader] — turns a deal index into a packed deal and pairs it with these
  tables, so the deals need not be published at all. The code half of this pair
- [bridge-encodings] — reads and writes the `.zrd` and `.zdd` record formats
- [Dealer3] — a worked consumer: it filters deals from a library, so `tricks()`,
  `dds()` and `par()` become lookups rather than searches. Live at
  [bridge-craftwork.com/dealer3](https://bridge-craftwork.com/dealer3/)

[rpdd-reader]: https://github.com/bridge-craftwork/rpdd-reader
[bridge-encodings]: https://github.com/bridge-craftwork/bridge-encodings
[Dealer3]: https://github.com/bridge-craftwork/Dealer3
