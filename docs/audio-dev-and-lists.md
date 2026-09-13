# `audio_dev`, graph objects, and runtime lists

## `audio_dev` anchor

The ASCII string `audio_dev` occurs at application offset `0x5BC1A`. The
identified code reference is at `0x4332A`, in the device creation/configuration
area. Nearby direct calls include:

```text
0x433A2 -> 0x3DF5A
0x433EE -> 0x3DF5A
0x433FC -> 0x04E0C
```

The analysis treats these as structural anchors, not as safe global patch
points.

Known command values:

```text
CMD02 = 0x80044102
CMD03 = 0x80044103
CMD05 = 0x80044105
CMD06 = 0x80044106
CMD07 = 0x80044107
```

Across 28 reconstructed direct call sites to the dispatcher at `0x586C`, the
observed counts are one CMD02, one CMD03, three CMD05, three CMD06, and four
real CMD07 sites. No static CMD05/06/07 site uses the same `object + 0x14`
access employed by LIST_A's CMD03 path. These commands remain lifecycle
candidates, not established controls for the local-DSP instance.

## LIST_A iteration

The list head is at runtime `0x01C0BBF4`. Observed iteration:

```text
0x405A0  mov r4, r15
0x405A2  jump to 0x4071C
0x4071C  load r4, [r4]
0x4071E  branch to body if r4 != r15
body     0x405A4
```

`r15` is the list head and `r4` is the current intrusive node. The list is
circular.

Insertion at `0x40122` is equivalent to `list_add_after(new, head)`, making it a
push-front list. Consequently, the first entry is simply the most recently
registered instance; it cannot safely be labelled USB playback or local DSP
without runtime evidence.

## Object model

```text
node = object + 0x24
object + 0x14 = concrete handle used by CMD03
```

Other observed metadata offsets are `+0x00`, `+0x01`, `+0x02`, and `+0x32`.
The CMD03 descriptor built by `0x40530` is temporary stack data.

## Per-instance event lifecycle

Routine `0x40530` also consumes an event object. The following dispatch is
verified from the PI32v2 instruction stream:

```text
event + 0x04 = opcode
event + 0x08 = object
event + 0x0C = payload/reference passed to 0x675A8

opcode 1: add    object + 0x24 to LIST_A through 0x40122
opcode 2: remove object + 0x24 from its list through 0x40192
opcode 4: write  6 to object + 0x00
```

`0x40192` is a conventional intrusive doubly-linked-list removal helper: it
repairs the neighboring links and makes the removed node self-linked. This
proves that LIST_A has per-object add/remove lifecycle handling. It does not
prove that invoking the list helper directly stops audio; removal may only be
bookkeeping after an earlier detach operation.

The callback pointer for `0x40530` is registered at `0x40318` through
`0x42C2A` (not `0x2C2A`, as an earlier decode stated). The same registrar is
used at `0x407B8` for callback `0x41EC6`, supporting a shared event mechanism.

## Safety conclusion

Do not patch the walker, CMD03, the list-removal helper, or the first list entry
globally. The useful next result is the producer of opcode-2 events and a
runtime identity map for the local-DSP object. Only then can the native detach
or release path be assessed safely.
