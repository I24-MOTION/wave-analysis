
# make the function to get no input and return the colors
def get_colors(c_id):
    colors = [
        {"name": "darkgreen", "hex": "#006400"},
        {"name": "darkblue", "hex": "#00008b"},
        {"name": "maroon3", "hex": "#b03060"},
        {"name": "orangered", "hex": "#ff4500"},
        {"name": "gold", "hex": "#ffd700"},
        {"name": "chartreuse", "hex": "#7fff00"},
        {"name": "aqua", "hex": "#00ffff"},
        {"name": "fuchsia", "hex": "#ff00ff"},
        {"name": "cornflower", "hex": "#6495ed"},
        {"name": "peachpuff", "hex": "#ffdab9"}
    ]
    hex_values = [color["hex"] for color in colors]
    # Create a matplotlib colormap
    plt_colors = hex_values
    color_index = c_id % 10
    return plt_colors[color_index]