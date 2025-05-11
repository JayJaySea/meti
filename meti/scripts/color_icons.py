import re
import os
import argparse
import pathlib
from PIL import Image


def main(args):
    colors = parse_scss_variables(args["colors"])
    icons = load_icons(args["input_dir"])

    color_icons(icons, colors, args["recolor"], args["output_dir"])

def parse_scss_variables(file_path):
    variable_regex = re.compile(r'\$([\w-]+):\s*(.*);')

    variables = {}

    with open(file_path, 'r') as file:
        content = file.read()
        matches = variable_regex.findall(content)
        
        for match in matches:
            variable_name, variable_value = match
            variables[variable_name] = variable_value.strip()

    resolved_variables = resolve_variable_references(variables)
    
    return resolved_variables

def resolve_variable_references(variables):
    resolved_variables = {}

    def resolve_value(value):
        if value.startswith('$'):
            ref_name = value[1:]
            return resolve_value(variables[ref_name])
        return value

    for var_name, var_value in variables.items():
        resolved_variables[var_name] = resolve_value(var_value)
    
    return resolved_variables

def load_icons(icons_dir):
    icons = {}

    for icon in os.listdir(icons_dir):
        path = os.path.join(icons_dir, icon)
        name = icon.split('.')[0]
        icons[name] = Image.open(path).convert("RGBA")


    return icons

def color_icons(icons, colors, recolor, output_dir):
    recolor = recolor.lstrip('#')
    recolor = tuple(int(recolor[i:i+2], 16) for i in (0, 2, 4))

    for (name, icon) in icons.items():
        new_colors = get_new_colors(name, colors)
        data = icon.getdata()

        for new_color in new_colors:
            new_data = []
            
            for item in data:
                if item[:3] == recolor:
                    color_hex = colors[new_color].lstrip('#')
                    new_data.append(tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4)) + (item[3],))
                else:
                    new_data.append(item)

            new_icon = icon.copy()
            new_icon.putdata(new_data)

            new_name = create_icon_name(name, new_color)
            new_icon.save(os.path.join(output_dir, new_name))

def get_new_colors(name, colors):
    new_colors = []
    for color in colors:
        if name in color and 'icon' in color:
            new_colors.append(color)

    return new_colors

def create_icon_name(name, color):
    name_parts = color.split('-')
    if len(name_parts) < 3:
        return name + ".png"

    return name + "-" + name_parts[2] + ".png"



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = "IconPainter",
        description = "Simple script that changes icon color based on .scss file with color definitions. Icons originally should be of single color passed as 'recolor' arg to this program for it to work properly.",
        epilog = "Meant to be compatible with JayJaySea Ags config"
    )

    parser.add_argument('-i', "--input-dir", type=pathlib.Path, required=True)
    parser.add_argument('-c', "--colors", type=pathlib.Path, required=True)
    parser.add_argument('-o', "--output-dir", type=pathlib.Path, required=True)
    parser.add_argument('-r', "--recolor", type=str, required=True)

    args = parser.parse_args()

    color_icons(vars(args))
