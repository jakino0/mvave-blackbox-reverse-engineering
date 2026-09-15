# Complete structural map of firmware V20

The V20 application has now been processed from beginning to end with the
official JieLi PI32v2 instruction decoder. The generated map covers the whole
input address range and records recognized instructions, decoding gaps, direct
calls, candidate function boundaries, printable strings, pointer targets, and
reviewed landmarks.

This is a complete **structural pass**, not a claim that the complete program
has been recovered as readable C. Semantic decompilation remains incomplete:
most mechanically discovered entries still have generated names, indirect
callbacks require manual recovery, and data/code boundaries need review.

## Current results

| Layer | Result | Interpretation |
| --- | ---: | --- |
| Whole-image pass | 655,712 bytes | Every input range was considered |
| Decoder coverage | 617,960 bytes (94.2426%) | Recognized PI32v2 instruction ranges |
| Decoder gaps | 13,224 ranges / 37,752 bytes | Data, alignment, or unresolved decoding |
| Instructions | 222,490 | Recognized instruction records |
| Direct calls | 12,152 sites | Statically resolved calls |
| Direct-call targets | 2,163 | Mechanical function-entry evidence |
| Function map | 2,167 entries | Targets plus reviewed seeds |
| Strings | 6,790 candidates | Includes false positives in code/data |
| String pointer sites | 176 | Aligned pointers to known strings |
| Raw pointer targets | 1,506 | In-image pointer candidates |
| Call-graph components | 30 | Weak components using direct calls only |

## Named code

Seventeen manually reviewed landmarks seed the map. Toolchain matching adds 16
unique exact identities, including `memcmp`, `memmove`, `memset`, `strcat`,
`strcmp`, `strcpy`, `strncmp`, and compiler floating-point helpers. Another five
matches remain candidates because their identity or partition is ambiguous.

The library matcher normalizes operands and requires at least ten consecutive
instructions. Only a match covering an entire mechanical partition with one
unique symbol name is promoted to `library-symbols.csv`. Prefix-only and
multi-name results stay in `library-candidates.csv`.

## What the map supports

The CSV data can be used to:

- move between application offsets and runtime addresses;
- find callers and callees for every resolved direct-call target;
- locate functions associated with referenced strings;
- identify possible tables and callbacks for manual review;
- compare structural changes in later firmware versions;
- attach reviewed names without editing a proprietary binary.

The public output cannot reproduce the firmware byte stream. The byte-bearing
listing stays local. See [the generated-map guide](../analysis/v20/README.md)
for the schema and commands.

## Remaining work

A useful semantic map requires ongoing manual analysis of indirect calls,
interrupt vectors, task tables, protocol handlers, DSP graph objects, global
RAM, and each decoder gap. A function should receive a descriptive name only
after its behavior is supported by control flow, data references, or a second
independent observation.
