# starfy3-gba-cn-localization

[简体中文](README.md) | [English](README.en.md)

A Simplified Chinese localization project for *Densetsu no Starfy 3* (GBA).

This unofficial, free, noncommercial project provides a translation delta patch and editing tools. The current public release is **v25 beta**. A complete human playthrough has not been completed; this is not a final, fully validated translation.

## Rights and distribution

Copyright in the original work belongs to Nintendo / TOSE.

This is an unofficial fan project, unaffiliated with the rights holders.

The game has not received an official Chinese release. This patch is intended for users who have legally obtained access to the game through Nintendo Switch Online or another lawful channel.

The project will be removed immediately if the rights holders object.

This project has no commercial activity: no fees, donations, advertising, or sales of patches, project files, or translated ROM images.

Please supply your own original ROM image. This repository provides no ROMs, ROM download links, or instructions on where to obtain them. The repository, release attachments, and documentation contain no official logos, cover or cartridge images, game screenshots, official artwork files, or dumps of the original Japanese or English reference text.

Nintendo's [official game catalog](https://www.nintendo.com/en-gb/Nintendo-Switch-Online/Classic-games/Classic-games-Nintendo-Switch-Online-2719182.html) lists the game as available in Japanese only; this status was last checked on 2026-10-02.

## Apply the patch

Use `patches/Starfy3_CN_v25_Rev0.bps` with the Japanese Rev0 image. These checksums apply to the **uncompressed file**:

| Field | Value |
| --- | --- |
| Original image size | 16,777,216 bytes (16 MiB) |
| Original CRC32 | `FCAF1AA8` |
| Original SHA256 | `8a7eff8a20319a966465da429dfbb744def4d12f1353f22f21743259c2247533` |
| Patch size | 677,697 bytes (about 662 KiB) |
| Output SHA256 | `acc0fca232ba9fd5ae3816defb27ae1546400cd9287a9820fe71e3adc7f8d139` |

Apply the patch locally using a BPS-compatible tool such as [Flips](https://github.com/Sir-Walrus/Flips). Alternatively, run the included tool with Python 3.10 or later; no third-party dependencies are required:

```text
python scripts/build.py --source "local/original.gba" --output "local/Starfy3_CN_v25.gba"
```

The tool strictly verifies the source, patch, and output checksums. It does not download images or overwrite existing files. Keep the generated image local; do not commit it or upload it as a release attachment.

Use the game's normal save files for continued testing, with a separate save directory for this version. Do not load emulator save states from older versions: they restore old fonts, tiles, and memory state.

## Progress and limitations

- Covers 2,304 script messages while preserving control-command boundaries. Translation and proofreading were assisted by GPT; human reports of mistranslations and context issues are welcome.
- Includes earlier menu and tutorial localization, preservation of the artwork style, HUD scene-reload fixes, and save-dialog fixes.
- v25 adds the title credit “（v25）汉化 by Clamsk” (Chinese localization by Clamsk) in an unused title area, using native bitmap lettering, a gold gradient, and a blue outline. The existing title, characters, background, and START prompt are preserved.
- Inherits v24's native 12×12 bitmap font for item descriptions. All 33 nonempty descriptions were reflowed by changing line breaks only, without changing their wording.
- Some graphics that may contain Japanese text, including posters, level signs, and multiplayer prompts, remain to be reviewed and localized. Human acceptance testing is still incomplete for all levels, minigames, the picture book, costumes, shops, endings, saving/loading, and switching between the two characters.
- This is a beta; the character encoding has not been declared frozen. See the [validation record](docs/VALIDATION.en.md) for the actual scope of testing.

## Project files and editing

The current BPS patch provides a reproducible v25 baseline. Original code, graphics, and control data are read from the user's local image and are not distributed separately with the project.

`translation/messages.zh.json` contains this version's Chinese text and control-boundary positions, without Japanese/English reference text or raw control packets. `translation/encoding.json` preserves the current encoding. `engineering/bmg_layout.json` records script addresses and pointer locations.

Copy the Chinese table to `local/edits.zh.json`, change only the `zh` fields, and rebuild locally:

```text
python scripts/build.py --source "local/original.gba" --edits "local/edits.zh.json" --output "local/Starfy3_CN_edited.gba"
```

The builder preserves unedited text and control packets, rejects control-boundary changes, and checks the item-description limit of 7 characters per line and 5 lines. New Chinese characters require additional glyphs and encoding entries; the current editor rejects characters outside the encoding table. Other dialogue still requires human layout review. Artwork changes are included in the delta patch; full original images and screenshots are not included. See the [engineering documentation](docs/ENGINEERING.en.md).

Open fonts and their original licenses are in `fonts/`. Rights belong to the respective font authors; see [NOTICE](NOTICE.en.md).

## Publication and backups

Only delta patches, original project code, Chinese translations, open fonts, and text documentation are published. BPS uses SourceRead / SourceCopy to reference unchanged data in the user's source image and TargetCopy to deduplicate data. Patch restoration has been verified against the full v25 SHA256.

`.gitignore` excludes images, saves, screenshots, executables, and backups. Run `python scripts/audit_public.py` before committing; CI also checks files actually tracked by Git. Patches must remain below the 1 MiB release gate.

The publisher keeps a complete local ZIP backup of the development workspace and a Git bundle of repository history. These backups are not uploaded. Maintainers should keep their own offline copies rather than relying on GitHub as the only copy.
