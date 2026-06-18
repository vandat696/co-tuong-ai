# V2 vs V3 Benchmark Results

Date: 2026-06-14

## Purpose

Estimate when Python V3 is stronger than WukongJS V2 after:

- adopting V2-inspired pawn and horse PST values;
- adding lightweight dynamic search evaluation;
- adding a conservative opening book.

These results are an initial strength estimate, not an official Elo test.

## Method

Games started after two fixed opening moves so V3's opening book did not
directly influence the comparison.

Opening families:

1. Central cannon and screen horse.
2. Developed horse and screen horse.
3. Advanced flank pawn and matching pawn reply.

Each configuration used all three openings with colors reversed, for six
games total. Games were limited to 80 or 100 plies depending on the run.

Result notation in this document is:

```text
V3 wins - V2 wins - draws
```

## Same-Depth Results

| V3 depth | V2 depth | Result |
|---:|---:|---:|
| 3 | 3 | `4-0-2` |
| 4 | 4 | `1-0-5` |
| 3 | 4 | `1-0-5` |
| 4 | 5 | `1-0-5` |
| 3 | 5 | `0-0-6` |
| 4 | 6 | `0-0-6` |

V3 showed the clearest advantage at depth 3. It remained competitive when V2
searched one ply deeper. With a two-ply disadvantage, the tested games were
all draws.

## Same-Time Results

| Time per move | Result | Typical V3 depth | Typical V2 depth |
|---:|---:|---:|---:|
| `0.1s` | `0-1-5` | `2.3-2.8` | `4.7-5.7` |
| `0.3s` | `0-5-1` | `3.1-3.6` | `6.3-7.9` |

At equal time controls, V2 currently has a large search-depth advantage and
remains stronger overall.

## Estimated Strength Boundary

The current estimate is:

```text
V3 is competitive or stronger when V3 depth >= V2 depth - 1.
```

Practical interpretation:

- Equal depth 3 favors V3 in the tested positions.
- Equal depth 4 slightly favors V3, but most games draw.
- V3 can remain competitive against V2 with a one-ply disadvantage.
- V3 loses its clear evaluation advantage when V2 searches two or more plies
  deeper.
- At equal unrestricted time controls, V2 is currently stronger.

Approximate V3 time required on the benchmark machine:

| Target depth | Approximate time per move |
|---:|---:|
| 3 | `0.10-0.15s` |
| 4 | `0.30-0.45s` |
| 5 | `1s+` |

## Interpretation

V3 appears to have better evaluation quality per searched node after the
evaluation changes. V2 still searches substantially faster, so its depth
advantage dominates under equal time controls.

The highest-value next optimization target is increasing V3 search speed until
it trails V2 by no more than one completed ply.

## Limitations

- Only three opening families and six games per configuration were tested.
- Deterministic engines produce limited game diversity.
- Draw limits may hide late-game advantages.
- Results depend on the current machine and worktree.
- No confidence interval or Elo estimate was calculated.

Future tests should use a larger opening suite, longer games, repeated runs,
and automated result logging.
