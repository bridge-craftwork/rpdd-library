# rpdd-library

Richard Pavlicek's library of 10,485,760 solved bridge deals, in a form a
program can fetch a piece of: the double-dummy tables as seed-aligned chunks,
with a manifest describing them.

**The deals are not here, and do not need to be.** They are a pure function of
their index, and [rpdd-reader](https://github.com/bridge-craftwork/rpdd-reader) is that
function — a dependency-free crate that turns a deal index into thirteen packed
bytes. This repository is the half that is data.

## Attribution

**The data is Richard Pavlicek's.** `rpdd.zip` at
[rpbridge.net](https://www.rpbridge.net/) — © 2007 Richard Pavlicek — holds
10,485,760 random deals and the complete twenty-cell double-dummy table for each
one. His own `rpdd.txt` records what that cost:

> In the early 2000s I created a database of 10,485,760 random deals. That was
> easy. The daunting task was to solve each deal 20 times to determine the
> double-dummy makes for each hand in each strain, which required almost two
> years of computer time.

He published it "as a courtesy to other programmers and data addicts". This
repository exists to make that courtesy easier to accept: the tables served in
pieces a browser can fetch, and the deals computed rather than shipped.

**Nothing here is a replacement for his site.** If you want the library itself,
get it from [rpbridge.net](https://www.rpbridge.net/).

### Licensing, stated plainly

`rpdd.txt` carries a copyright notice and an offer of download. It is not a
licence, and it says nothing about redistribution. **Republishing the tables
here goes beyond what he has explicitly granted**, and permission has been
requested — see the issues. Until that is answered, `data/` is published on the
reading that mirroring a freely-offered resource in a more usable shape serves
his stated intent. If he would rather it were not, it comes down.

The [rpdd-reader](https://github.com/bridge-craftwork/rpdd-reader) crate is a separate
question, which is part of why it is now a separate repository: it is our own
code, reproducing an algorithm from its published behaviour, and algorithms are
not what copyright covers. It carries no data.

## What is here

| | |
|---|---|
| `data/zdd/` | the double-dummy tables, 160 chunks of 655,360 bytes |
| `data/manifest.json` | the layout: chunk paths, deal ranges, SHA-256 of each and of the whole |
| `docs/rpdd.txt` | Pavlicek's own documentation of the library |
| `scripts/split-zdd.py` | splitting his `rpdd.zdd` into chunks, and verifying them |

The generator, its disassembly, and the digests it is tested against moved to
[rpdd-reader](https://github.com/bridge-craftwork/rpdd-reader). A git dependency on this
repository cloned 51MB packed to compile eighty lines of Rust, and these tables
will never change again while that crate will.

## The manifest describes itself

`data/manifest.json` is the entry point, and it carries everything a reader
needs so that nothing has to be hardcoded against this library in particular:

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

**Chunk paths are relative to the manifest**, so resolving them against the URL
it was fetched from finds the chunks — and mirroring `data/` anywhere, at any
depth, still works. An absolute base URL would tie the file to wherever it
happened to be published.

**`schema` is what a reader checks first.** It is bumped when a change would
make an older reader wrong rather than merely uninformed.

So the deal at index *i* is at byte `(i % deals_per_chunk) * record_bytes` of
the chunk whose `first_deal` covers it, and a consumer works that out from the
manifest rather than from constants baked into its own code.

## Where it is served from

    https://rpdd-library.pages.dev/manifest.json

The repository is also the host. That is Cloudflare Pages, deployed from
`data/` by `.github/workflows/pages.yml`, and it exists because reading the
pieces from `raw.githubusercontent.com` was slow: no edge caching, about
600 KB/s measured from a browser, and rate limits it was never meant to serve
under. A 100,000-deal run reads two pieces and spent roughly 2.1 seconds of a
2.4 second run fetching them.

Two response headers matter, and both are set in `data/_headers`:

| Header | Why |
|---|---|
| `Access-Control-Allow-Origin: *` | every consumer is another origin |
| `Cross-Origin-Resource-Policy: cross-origin` | a consumer under COEP `require-corp` — which any page using threaded WebAssembly must be — blocks a subresource that does not opt in, and blocks it silently |

Pieces are served `immutable` for a year, because a piece is named for the
deals in it and its digest is in the manifest, so it genuinely never changes.
The manifest is not, since it can gain chunks.

Reading it from GitHub still works and always will; it is simply slower. The
manifest's paths are relative, so either base URL resolves correctly, and a
mirror needs no change here.

## Why 160 chunks of that size

A chunk is 65,536 deals — Pavlicek's own unit, the one `rpdd.bat` counts in
("160 = all deals"). It is also exactly four of the deal generator's
16,384-deal seed groups, **so every chunk boundary is a seed boundary**: a
reader wanting deals from chunk N seeds from chunk N and needs nothing before
it. Any other size would force it to fetch a neighbour to find where it stands.

640 KiB a chunk, about 300 KB gzipped, which is a reasonable thing for a web
page to fetch. The whole file is 104,857,600 bytes — exactly 100 MiB, which is
exactly GitHub's hard limit for a single file, so chunking was never optional.

## The deals are not data

`rpdd.zip` ships `xxdd.exe`, a 2,560-byte program that recreates the deals from
their index. The [rpdd-reader](https://github.com/bridge-craftwork/rpdd-reader) crate is that
program, ported — so a consumer pairs a chunk fetched from here with deals it
computes:

```rust
use rpdd::Deals;

for packed in Deals::from(4_096_000).take(1000) {
    // 13 bytes: two bits a card, holding the seat. The deal half of a
    // .zrd record, ready for a decoder of that format.
}
```

About 640ns a deal, and it re-seeds every 16,384 deals — so an arbitrary
starting position costs at most 16,383 deals of catch-up, about 10ms, rather
than replaying from the beginning. Every chunk boundary here is a seed
boundary, which is what makes fetching one chunk enough.

Nothing about a wrong constant in that generator fails loudly: a mistyped
multiplier still yields four thirteen-card hands, every one a legal deal — just
not his, which would pair every deal with another deal's table. It is therefore
tested against digests of the real library's deals rather than against itself.
Those digests, and the annotated disassembly the constants came from, live with
the crate.

## Rebuilding from the original

```bash
# Unzip rpdd.zip from rpbridge.net into this directory, then:
scripts/split-zdd.py split      # rpdd.zdd -> data/zdd/ + manifest
scripts/split-zdd.py verify     # digests, and that the chunks rejoin
```

Re-recording what the generator is tested against needs a built `rpdd.zrd` and
is done from the other repository: `scripts/make-deal-digests.py` there takes
the path to one.

`rpdd.zip`, `rpdd.zdd`, `rpdd.zrd`, `rpdd.bat` and `xxdd.exe` are deliberately
git-ignored. They are his distribution as it arrives, and not ours to republish
whole — `xxdd.exe` least of all, being his program rather than his data.

## Related

- [rpdd-reader](https://github.com/bridge-craftwork/rpdd-reader) turns a deal index into a
  packed deal, so the deals need not be published at all
- [bridge-encodings](https://github.com/bridge-craftwork/bridge-encodings) reads
  and writes the `.zrd` and `.zdd` record formats
- [dealer3](https://github.com/bridge-craftwork/Dealer3) filters deals from a
  library, so `tricks()`, `dds()` and `par()` become lookups rather than searches
