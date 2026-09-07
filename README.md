# rpdd-library

Richard Pavlicek's library of 10,485,760 solved bridge deals, in a form a
program can fetch a piece of: the double-dummy tables as seed-aligned chunks,
and a crate that reproduces the deals those tables belong to.

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

The `rpdd-deals` crate is a separate question: it is our own code, reproducing
an algorithm from its published behaviour, and algorithms are not what copyright
covers. It carries no data.

## What is here

| | |
|---|---|
| `data/zdd/` | the double-dummy tables, 160 chunks of 655,360 bytes |
| `data/manifest.json` | chunk index, deal ranges, SHA-256 of each and of the whole |
| `crate/` | `rpdd-deals`, which turns a deal index into a packed deal |
| `docs/` | the annotated disassembly and a Python reference for the generator |
| `fixtures/` | digests of the real library's deals, which the crate is tested against |
| `scripts/` | splitting, verifying, and rebuilding the fixtures |

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
their index. The `rpdd-deals` crate is that program, ported:

```rust
use rpdd_deals::Deals;

for packed in Deals::from(4_096_000).take(1000) {
    // 13 bytes: two bits a card, holding the seat. The deal half of a
    // .zrd record, ready for a decoder of that format.
}
```

Roughly 800ns a deal, and it re-seeds every 16,384 deals — so an arbitrary
starting position costs at most 16,383 deals of catch-up, about 13ms, rather
than replaying from the beginning.

### It is tested against the real library, not against itself

Nothing about a wrong constant fails loudly. A mistyped multiplier still yields
four thirteen-card hands, every one a legal deal — just not his, which would
pair every deal with another deal's table. So `fixtures/deal-digests.json`
holds SHA-256 digests of the real library's deals, one per seed group, scattered
through the file and including the first and the last, and the crate is checked
against those. Changing one hex digit of one multiplier fails that test and
nothing else.

## Rebuilding from the original

```bash
# Unzip rpdd.zip from rpbridge.net into this directory, then:
scripts/split-zdd.py split      # rpdd.zdd -> data/zdd/ + manifest
scripts/split-zdd.py verify     # digests, and that the chunks rejoin

# With a built rpdd.zrd present, re-record what the crate is tested against:
scripts/make-deal-digests.py
```

`rpdd.zip`, `rpdd.zdd`, `rpdd.zrd`, `rpdd.bat` and `xxdd.exe` are deliberately
git-ignored. They are his distribution as it arrives, and not ours to republish
whole — `xxdd.exe` least of all, being his program rather than his data.

## Related

- [bridge-encodings](https://github.com/bridge-craftwork/bridge-encodings) reads
  and writes the `.zrd` and `.zdd` record formats
- [dealer3](https://github.com/bridge-craftwork/Dealer3) filters deals from a
  library, so `tricks()`, `dds()` and `par()` become lookups rather than searches
