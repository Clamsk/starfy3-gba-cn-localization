# v25 validation scope

[简体中文](VALIDATION.md) | [English](VALIDATION.en.md)

This remains a public beta. A complete human playthrough has not been claimed.

Title-credit checks for this version:

- Compared 9 runtime title-animation samples when starting with and without an existing save. Differences were confined to the credit's 120×14-pixel area.
- The original title, characters, clouds, background, START prompt, and copyright text were pixel-identical in these samples.
- Save selection and interrupted-game resume dialogs were pixel-identical to v24.
- Static reconstruction checked the other 38 title/save animation frames, preserving their pixels. The 20 existing START-prompt frames only gained the credit.
- ROM byte differences were confined to the added title-text cache, its loading pointer, and blank title sprite slots. Translation, fonts, and gameplay logic were unchanged from v24.
- BPS restoration was byte-identical to the local v25 image. Rebuilding from local v24 with the credit generator produced the same result.
- Player saves and older version files were untouched. Screenshots and QA dumps remain local and are not published.

The following records are inherited from v24. Their limited scope does not establish full playthrough acceptance.

## v24 validation scope

This version was a public beta; full human playthrough acceptance was not declared complete.

Completed local checks:

- Restored the optimized BPS from the specified Rev0 image. The full output was byte-identical to local v24; both CRC32 and SHA256 were checked.
- Checked font encoding and bitmap pixels for the 309 characters used in item descriptions.
- Checked 32 actual item IDs in the emulator. One additional description, not referenced by the item-page dispatch code, was checked in an isolated QA copy using the same native text-rendering function.
- Actual foreground pixels for all 33 nonempty descriptions matched the expected bitmaps, without clipping, overlapping glyphs, or overflow. The left panel was pixel-identical to the blank base plus text.
- Preserved non-text VRAM and the lower name panel. Fixed-screen samples for hints, costumes, skills, vehicles, and the empty item page matched v23. The background and item animation on the right could be at different frames in the two versions' screenshots.
- Changed only description line breaks, not wording. All existing BMG bytes and other version files were preserved.
- v23 had already passed targeted checks for going through the first door and returning, entering again, pausing and resuming, and both interrupted-save dialogs.

Previews selected descriptions through isolated emulator memory without changing player items or saves. These checks did not test acquiring every item, purchasing every item, or completing the game. Screenshots and VRAM dumps remain local and are not distributed with the repository.

Human acceptance testing is still required for all levels, minigames, the picture book, costume and shop branches, endings, saving/loading, switching between the two characters, contextual translation, and remaining graphics that may contain Japanese text.
