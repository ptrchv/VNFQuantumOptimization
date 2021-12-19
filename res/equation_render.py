import io
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
from enum import Enum
import sys

class ParserState(Enum):
    WAITING = 0
    EQ_NAME = 1
    READING = 2

def render_equation(equation, out_path):
    fig, ax = plt.subplots(1,1)
    ax.set_axis_off()
    ax.text(0.001, 0.001,'$%s$'%equation, fontsize=20)
    plt.tight_layout()
    fig.patch.set_facecolor('white')

    with io.BytesIO() as png_buf:
        fig.savefig(png_buf, bbox_inches='tight', pad_inches=0, dpi = 100)
        png_buf.seek(0)
        image = Image.open(png_buf)
        image.load()
        inverted_image = ImageOps.invert(image.convert("RGB"))
        cropped = image.crop(inverted_image.getbbox())
        cropped.save(out_path)

def parse_equation_file(infile):
    parse_state = ParserState.WAITING
    eq_name = None
    eq_string = ""
    cont = 1
    for line in infile:
        line = line.strip()
        if line == "":
            pass
        elif parse_state == ParserState.WAITING:
            if not line.startswith("%"):                
                raise ValueError(f'"%" expected at file line [{cont}]')
            line = line.replace("%", "").strip()
            eq_name = line
            parse_state = ParserState.EQ_NAME
        elif parse_state == ParserState.EQ_NAME:
            if not line  == "$$":
                raise ValueError(f'"$$" expected at file line [{cont}]')
            parse_state = ParserState.READING
        elif parse_state == ParserState.READING:
            if line == "$$":
                parse_state = ParserState.WAITING
                yield (eq_name, eq_string)
                eq_string = ""
            else:
                eq_string += line
        cont+=1
    if parse_state != ParserState.WAITING:
        raise ValueError(f'Bad parser termination in state{str(parse_state)}')
            




def main():
    if len(sys.argv) > 2:
        raise ValueError(f'Wrong parameters')
    if len(sys.argv) == 2:
        path = str(sys.argv[1])
    else:
        path = "."
    

    with open(path + "/res/tex/formula.tex") as infile:
        for eq in parse_equation_file(infile):
            render_equation(eq[1], f'{path}/res/img/{eq[0]}.png')

        


if __name__ == "__main__":
    main()