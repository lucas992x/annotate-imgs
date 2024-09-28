import argparse, os, os.path, sys, re
import pandas as pd
from sys import platform


# add + if pad does not start with + or -
def fix_pad(pad):
    pad = str(pad)
    if not pad.startswith("-") and not pad.startswith("+"):
        pad = f"+{pad}"
    return pad


# read csv file and fix pads
def read_csv(file_path, sep):
    table = pd.read_csv(file_path, sep=sep)
    if "Padx" in list(table.columns.values) and "Pady" in list(table.columns.values):
        for index, row in table.iterrows():
            row["Padx"] = fix_pad(row["Padx"])
            row["Pady"] = fix_pad(row["Pady"])
    return table


# read file with data of specific item
def read_specific_data(file_path, sep):
    data = {}
    with open(file_path, "r") as file:
        for line in file:
            key, value = line.strip().split(sep)
            data.update({key: value})
    return data


# read file with data of many items
def read_general_data(file_path, sep):
    table = pd.read_csv(file_path, sep=sep)
    fields = list(table.columns.values)
    item = fields[0]
    fields = fields[1:]
    data = {}
    for index, row in table.iterrows():
        item_dict = {}
        for field in fields:
            item_dict.update({field: row[field]})
        data.update({row[item]: item_dict})
    return data


# add general data read from file to existing general data
def merge_general_data(existing_data, new_data):
    for key, value in new_data.items():
        existing_value = existing_data.get(key, None)
        if not existing_value:
            new_value = value
        else:
            new_value = new_value.update(existing_value)
        existing_data.update({key: new_value})
    return existing_data


# replace data in a string getting it from a dictionary
def replace_data(string, data, delimiters, default):
    del1, del2 = delimiters
    for key, value in data.items():
        string = string.replace(f"{del1}{key}{del2}", value)
    string = re.sub(f"{del1}(.+?){del2}", default, string)
    return string


# add code to command that writes text on image
def write_on_img(width, height, font, fonts_exts, color, size, align, text, gravity, padx, pady):  # fmt: skip
    if not os.path.isfile(font):
        for ext in fonts_exts:
            tryfont = f"{font}.{ext}"
            if os.path.isfile(tryfont):
                font = tryfont
                break
    if not os.path.isfile(font):
        raise Exception(f"Cannot find font '{font}'")
    return f' \( \( -size "{width}x{height}" -background "none" -font "{font}" -fill "{color}" -pointsize "{size}" -gravity "{align}" caption:"{text}" \) -gravity "{gravity}" -geometry "{padx}{pady}" \) -composite'


# main
def main():
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseimg", default="base-img.png")
    parser.add_argument("--items", default="")
    parser.add_argument("--itemssep", default=",")
    parser.add_argument("--fontsdir", default="fonts")
    parser.add_argument("--inputgen", default="input-data-general")
    parser.add_argument("--datagensep", default=",")
    parser.add_argument("--inputspec", default="input-data-specific")
    parser.add_argument("--dataspecsep", default="=")
    parser.add_argument("--datadefault", default="???")
    parser.add_argument("--coordstexts", default="coordinates-data.csv")
    parser.add_argument("--coordsimgs", default="coordinates-imgs.csv")
    parser.add_argument("--coordssep", default=",")
    parser.add_argument("--coordsdel", default="<>")
    parser.add_argument("--outputdir", default="output-imgs")
    parser.add_argument("--clearout", default="no")
    parser.add_argument("--outprefix", default="")
    parser.add_argument("--outsuffix", default="")
    args = parser.parse_args()
    # check inputs
    if not os.path.isdir(args.inputgen) and not os.path.isdir(args.inputspec):
        sys.exit("Error: cannot find any directory with data")
    if not args.dataspecsep:
        sys.exit("Error: generic data separator not provided")
    if not args.datagensep:
        sys.exit("Error: specific data separator not provided")
    if not os.path.isfile(args.coordstexts) and not os.path.isfile(args.coordsimgs):
        sys.exit("Error: cannot find any file with coordinates")
    if not args.coordssep:
        sys.exit("Error: coordinates separator not provided")
    if not args.coordsdel:
        sys.exit("Error: delimiters not provided")
    if not os.path.isfile(args.baseimg):
        sys.exit(f"Error: cannot find base image {args.baseimg}")
    # initialize stuff
    img_ext = args.baseimg.split(".")[-1]
    fonts_exts = list(set([f.split(".")[-1] for f in os.listdir(args.fontsdir) if "." in f]))  # fmt: skip
    # create output directory or empty it if needed
    if not os.path.isdir(args.outputdir):
        os.mkdir(args.outputdir)
    elif args.clearout.lower() == "yes":
        files = os.listdir(args.outputdir)
        for file in files:
            os.unlink(os.path.join(args.outputdir, file))
    # read general data
    data_all = {}
    if os.path.isdir(args.inputgen):
        for file in [os.path.join(args.inputgen, f) for f in os.listdir(args.inputgen) if os.path.isfile(os.path.join(args.inputgen, f)) ]:  # fmt: skip
            data_file = read_general_data(file, args.datagensep)
            data_all = merge_general_data(data_all, data_file)
            # data_all.update(data_file)
    # read coordinates (or build empty table if file does not exist)
    if os.path.isfile(args.coordstexts):
        coordinates_data = pd.read_csv(args.coordstexts, sep=args.coordssep)
    else:
        coordinates_data = pd.DataFrame(columns=["placeholder"])
    if os.path.isfile(args.coordsimgs):
        coordinates_imgs = pd.read_csv(args.coordsimgs, sep=args.coordssep)
    else:
        coordinates_imgs = pd.DataFrame(columns=["placeholder"])
    # get list of items to be processed
    if os.path.isfile(args.items):
        with open(args.items, "r") as file:
            items_string = file.read()
    else:
        items_string = args.items
    items = []
    for line in items_string.splitlines():
        items += [i.strip() for i in line.split(args.itemssep) if i.strip()]
    # process items
    print_recap = f"Processing {len(items)} item(s)"
    if len(items) <= 10:
        print_recap += f': {", ".join(items)}'
    print(print_recap)
    for item in items:
        # retrieve item data
        item_data = data_all.get(item, None)
        if not item_data:
            item_data = {}
        item_data_file = os.path.join(args.inputspec, f"{item}.txt")
        if os.path.isfile(item_data_file):
            with open(item_data_file, "r") as file:
                for line in file:
                    key, value = line.strip().split(args.dataspecsep)
                    item_data.update({key: value})
        # initialize command with base image
        command = f'"{args.baseimg}"'
        # add text(s) to base image
        for index, row in coordinates_data.iterrows():
            text = replace_data(row["Text"], item_data, args.coordsdel, args.datadefault)  # fmt: skip
            padx = fix_pad(row["Padx"])
            pady = fix_pad(row["Pady"])
            command += write_on_img(
                row["Width"],
                row["Height"],
                os.path.join(args.fontsdir, row["Font"]),
                fonts_exts,
                row["Color"],
                row["Size"],
                row["Align"],
                text,
                row["Direction"],
                padx,
                pady,
            )
        # add image(s) to base image
        for index, row in coordinates_imgs.iterrows():
            img_path = replace_data(row["Img"], item_data, args.coordsdel, args.datadefault)  # fmt: skip
            if not os.path.isfile(img_path):
                print(f"    Skipping image {img_path}")
            else:
                padx = fix_pad(row["Padx"])
                pady = fix_pad(row["Pady"])
                command = f'\( {command} \) \( "{img_path}" -gravity "{row["Direction"]}" -geometry "{padx}{pady}" \) -composite'
        # add prefix/suffix to output file name if provided
        output_img = os.path.join(args.outputdir, f"{args.outprefix}{item}{args.outsuffix}.{img_ext}")  # fmt: skip
        # refine command and execute it to generate image
        command = f'convert \( {command} \) "{output_img}"'
        if platform == "win32":
            command = command.replace("\(", "(").replace("\)", ")")
        # print(command)
        os.system(command)
        print(f"Created image {output_img}")


# invoke main
if __name__ == "__main__":
    main()

#################################### TESTS ####################################
# cd ~/code/annotate-imgs && python annotate-imgs.py
# print(replace_data('Height is <Height>, weight is <weight>.', { 'height': '21', 'weight': '66', 'something': 'else' }, '<>', '???'))
# print(replace_data('Height is <Height>, weight is <weight>.', { 'height': '21', 'weight': '66', 'something': 'else' }, ['<', '>'], '???'))
