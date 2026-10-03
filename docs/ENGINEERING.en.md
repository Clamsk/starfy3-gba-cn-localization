# Project organization without original asset files

[简体中文](ENGINEERING.md) | [English](ENGINEERING.en.md)

## Reproducible baseline

Input: the user's own original image, with the SHA256 specified in the README.

Process: verify original → verify and apply BPS → verify v25 output → optionally edit Chinese text → generate a local image.

Without text edits, the output is byte-identical to the locally verified v25 image. The public project stores completed code, artwork, and font changes as a delta patch. It does not include full official images or original text extracted during development, an English reference ROM, or historical test ROMs.

## Chinese text and control boundaries

The Chinese table uses `script block:message` keys. Each record lists `slot` and `kind`; only editable translation records contain `zh`. The `control`, `end`, and `preserved` records identify boundaries without storing original packets or text.

The builder restores original control packets from the user's local v25 baseline. Speaker packets replace only the name and update its length; all other control packets are preserved byte for byte. Modified BMG blocks have their INF1 offsets and DAT1 text rebuilt, are placed in reserved free space, and have all corresponding pointers updated. Unmodified blocks are not rebuilt.

The editor preserves the current encoding and accepts only registered characters and game-button icons. Item descriptions are limited to 7 characters per line and 5 lines. Ordinary dialogue, names, and other interface text must still be checked in their actual windows. Color or page-boundary changes require separate engineering work; changing boundary records in the Chinese table cannot bypass validation.

## Fonts and artwork

`fonts/` contains open font source files and licenses, not the original game's fonts. The BPS already includes this version's glyph changes. This project's noncommercial policy does not alter upstream licenses.

Unmodified official artwork is read from the user's source image when applying the patch. For future tile edits, decode tiles, palettes, and maps locally; publish only necessary deltas or original replacement elements, avoiding full official asset files and game screenshots.

## Regenerate a patch

After local edits and acceptance testing, generate a new BPS using Flips delta mode:

```text
flips --create --bps-delta "local/original.gba" "local/Starfy3_CN_edited.gba" "local/candidate.bps"
```

Check patch size, action statistics, and source/target SHA256 values. Restore the image from the patch and compare all target bytes; review Git's tracked-file list before replacing published files. Do not substitute a linear patch that embeds large amounts of relocated data for delta mode.

Keep all original, target, and temporary images, screenshots, and saves in `local/` or a separate workspace. CI neither requires nor accepts ROMs; it checks only the public-file allowlist and patch format.

## Original data for the v25 title credit

`engineering/title_credit_v25.json` contains only the bitmap indices of the original credit “（v25）汉化 by Clamsk” and required addresses. It contains no official images, palettes, original fonts, or screenshots. `scripts/add_title_credit.py` reproduces v25 from the user's local v24 image, reads the cache that must be preserved, verifies input/output SHA256 values, and refuses to overwrite existing files. This optional generator uses the Python standard library; the normal v25 build still follows the BPS process in the README.

```text
python scripts/add_title_credit.py --base "local/Starfy3_CN_v24.gba" --output "local/Starfy3_CN_v25_from_credit.gba"
```

The credit uses 5 blank slots among the existing 13 title sprite slots; the START prompt retains its original 6 sprites. New glyph tiles use an unused blank area of the existing text cache. Only 20 title-animation frames are modified; the other 38 frames and all other background maps are preserved. To support BIOS decompression into VRAM, the new tile cache uses an LZ77 stream without back-references; the delta patch then references matching portions of the original cache.
