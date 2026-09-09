# Why the chunks are shaped this way

The reasoning behind decisions that were not obvious, moved out of the README so
that it answers "what is this" first. Nothing here is required reading to use
the tables; all of it is required reading before changing how they are cut or
served.

## Why 160 chunks of that size

A chunk is 65,536 deals — Pavlicek's own unit, the one `rpdd.bat` counts in
("160 = all deals").

It is also exactly four of the deal generator's 16,384-deal seed groups, **so
every chunk boundary is a seed boundary.** A reader wanting deals from chunk *N*
seeds from chunk *N* and needs nothing before it. Any other size would force it
to fetch a neighbouring chunk just to work out where it stands, which would make
"fetch one piece" a lie.

640 KiB a chunk, about 300 KB gzipped, which is a reasonable thing for a web
page to fetch.

Chunking was never optional in any case. The whole `rpdd.zdd` is 104,857,600
bytes — exactly 100 MiB, which is exactly GitHub's hard limit for a single file.

## The manifest describes itself

`data/manifest.json` is the entry point, and it carries everything a reader
needs so that nothing has to be hardcoded against this library in particular.

**Chunk paths are relative to the manifest**, so resolving them against the URL
it was fetched from finds the chunks — and mirroring `data/` anywhere, at any
depth, still works. An absolute base URL would tie the file to wherever it
happened to be published, and a mirror would need editing rather than copying.

**`schema` is what a reader checks first.** It is bumped when a change would
make an older reader wrong rather than merely uninformed.

The consequence worth stating: `deals_per_chunk`, `record_bytes`, `total_deals`
and every chunk's `file` and `first_deal` are data. Our library happens to be
160 chunks of 65,536 deals, but that is a hosting decision rather than a
property of Pavlicek's library. A consumer that reads them from the manifest
works against a re-cut library; one that bakes them in does not.

## Where it is served from, and why not raw GitHub

    https://rpdd-library.pages.dev/manifest.json

That is Cloudflare Pages, deployed from `data/` by `.github/workflows/pages.yml`.
The repository is also the host.

The reason is cache lifetime rather than raw throughput, and it is worth being
accurate about that, because measured back-to-back the two hosts fetch a 640 KiB
piece in much the same time.

`raw.githubusercontent.com` serves `Cache-Control: max-age=300`. A consumer
revalidates the same pieces every five minutes, for ever, even though the pieces
cannot change. The copy here is `immutable` with a one-year lifetime, which is
truthful rather than optimistic: a chunk is named for the deals in it and its
digest is in the manifest, so `rpdd-042.zdd` is the same 640 KiB for good.

It is also a source-code host rather than a content one, with rate limits it was
never meant to serve a web app under.

A whole read — two chunks fetched, 100,000 deals generated and paired — lands
around half a second, and about two thirds of that is the fetching.

Reading from GitHub still works and always will. The manifest's paths are
relative, so either base URL resolves correctly and a mirror needs no change
here.

### Two response headers matter

Both are set in `data/_headers`, and a browser consumer depends on them:

| Header | Why |
|---|---|
| `Access-Control-Allow-Origin: *` | every consumer is another origin |
| `Cross-Origin-Resource-Policy: cross-origin` | a consumer under COEP `require-corp` — which any page using threaded WebAssembly must be — blocks a subresource that does not opt in, and **blocks it silently** |

The second is the one that will waste someone's afternoon if it is ever dropped,
because nothing reports an error.

Pieces are served `immutable` for a year: a piece is named for the deals in it
and its digest is in the manifest, so it genuinely never changes. The manifest
itself is not, since it can gain chunks.

## The deals are not data

`rpdd.zip` ships `xxdd.exe`, a 2,560-byte program that recreates the deals from
their index. [rpdd-reader] is that program, ported — so a consumer pairs a chunk
fetched from here with deals it computes:

```rust
use rpdd_reader::Deals;

for packed in Deals::from(4_096_000).take(1000) {
    // 13 bytes: two bits a card, holding the seat. The deal half of a
    // .zrd record, ready for a decoder of that format.
}
```

About 640ns a deal, and it re-seeds every 16,384 deals — so an arbitrary
starting position costs at most 16,383 deals of catch-up, about 10ms, rather
than replaying from the beginning. Every chunk boundary here is a seed boundary,
which is what makes fetching one chunk enough.

This is why the repository holds 100 MiB rather than 241 MB: publishing the
deals alongside their tables would publish the very thing that does not need
publishing.

Nothing about a wrong constant in that generator fails loudly. A mistyped
multiplier still yields four thirteen-card hands, every one a legal deal — just
not his, which would pair every deal with another deal's table. It is therefore
tested against digests of the real library's deals rather than against itself.
Those digests, and the annotated disassembly the constants came from, live with
the crate.

## Why the crate is not in this repository

It used to be. Depending on this repository to get it meant cloning 51 MB packed
to compile eighty lines of Rust, and the two have nothing to do with each
other's release rhythm: these tables will never change again, and that crate
will.

So: **rpdd-library** is the tables, and how they were made. **rpdd-reader** is
the code that reads them, and the account of where its constants came from.

## Re-recording what the generator is tested against

Needs a built `rpdd.zrd` and is done from the other repository:
`scripts/make-deal-digests.py` there takes the path to one. Pavlicek's
`rpdd.bat` produces it from his zip.

[rpdd-reader]: https://github.com/bridge-craftwork/rpdd-reader
