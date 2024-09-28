This repository allows to create multiple images starting from same base image and adding text and/or other images over it; requires [ImageMagick](https://imagemagick.org/) and [pandas](https://pandas.pydata.org/). Various sample files are included to make everything clearer (hopefully).

# Setup and usage
All files and directories used by this script are specified by arguments; it is advisable to put them in a separate folder and invoke `annotate-imgs.py` from there.

## Base image
Base image can be any image file and is specified using `--baseimg`.

## Items to be processed
`--items` specifies which items need to be processed, where "item" meaning depends on what is being generated. If `--items` is the path of an existing file its content is read and used as input string, otherwise `--items` itself is used as input; in both cases values are separated using `--itemssep` (default `,`) and can be splitted into multiple lines. In this sample repository, available items are `js` and `nr`.

## Font(s)
The script reads font(s) from directory specified by `--fontsdir`; files can be named in any way, every piece of text added to image requires to specify font file. This sample includes a free font in regular, bold, italic and bold italic versions. File extension can be omitted when indicating font in input files.

## Input data
### General
Each file contained in `--inputgen` directory should be a CSV (or CSV-like) file that contains data referred to all items, with first row as header and item name in first column; its separator can be specified using `--datagensep`. See `input-data-general/data-general-sample.csv` for an example.

### Specific
File contained in `--inputspec` directory should be named as `[item].txt` and contain data for that item; specifically, each row of this file should contain field name and value separated by `--dataspecsep`. See `input-data-specific` directory for samples.

### Placeholders
If any piece of data is missing, placeholder string can be set using `--datadefault`.

## Coordinates
File with coordinates of text(s) added to image can be specified using `--coordstexts`, while images use `--coordsimgs`. They should both be CSV (or CSV-like) files with `--coordssep` as separator; `--coordsdel` indicates the two characters used to identify something that should be picked from item's data: for example, if `--coordsdel` is `<>` then `<property>` indicates field named `property`, which may vary from item to item. See `coordinates-data.csv` and `coordinates-imgs.csv` for samples.

### Data
Each row in `coordinates-data.csv` (or whatever file is used for text) requires the following fields:
- `Text` is the text that needs to be written.
- `Font` is the font, as described in previous section.
- `Color` is the color of text, which can be a hex or a recognized name; see [documentation](https://imagemagick.org/script/color.php) for further info.
- `Size` is the size of the text.
- Text is virtually contained in a rectangle of dimensions `Width` and `Height` and is wrapped inside it; its alignment is specified using `Align`, which can be `north`, `south`, `east`, `west`, `center`, `northwest`, `northeast`, `southeast`, `southwest`.
- Position of this rectangle is specified using `Padx`, `Pady` and `Direction` fields: `Padx` is horizontal coordinate, `Pady` is vertical coordinate, `Direction` has same options as `Align`. Here are some examples:
    - `northwest` value for `Direction` means that `Padx` is distance horizontal between left border of text rectangle and left border of base image, `Pady` is vertical distance between upper border of text rectangle and upper border of base image.
    - `center` value for `Direction` means that `Padx` is horizontal distance between center of text rectangle and center of base image, `Pady` is vertical distance between center of text rectangle and center of base image; positive values put text rectangle at right and lower position respectively, negative values instead put it at left and upper respectively.
    - `south` value for `Direction` means that `Padx` is horizontal distance between center of text rectangle and center of base image, `Pady` is vertical distance between lower border of text rectangle and lower border of base image.

### Images
Each row in `coordinates-imgs.csv` (or whatever file is used for images) requires the following fields:
- `Img` is the path of image that needs to be added over base image.
- `Padx` and `Pady` work as described in previous section. There's no need to specify width and height, image already has a size; be sure to resize all images properly before launching this script.
- `Direction` works as described in previous section.

## Output
Output directory where generated image(s) will be saved is specified using `--outputdir`, it is automatically created if not already existing; if passing `yes` value to `--clearout` its content is cleared before processing items. Output image generated from an item is named as `[prefix][item][suffix].[ext]`, where prefix and suffix are set using `--outprefix` and `--outsuffix` respectively (both empty by default) and extension is same as base image. See `output-imgs` for samples of what is generated starting from provided data and images.
