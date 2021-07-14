from os import rename
from pathlib import Path

import tkinter as tk
from PIL import ImageTk, Image

from config import IMAGE_FOLDER

images = [str(path).split('/')[-1] for path in Path(IMAGE_FOLDER).rglob('*.jpeg')]
unclassified_images = sorted(filter(
    lambda image: not (image.startswith("0_") or image.startswith("1_") or 'checkpoint' in image),
    images))
current = None
counter = 0


def next_img():
    global current, unclassified_images, counter
    try:
        current = unclassified_images[counter]
    except IndexError:
        root.quit()
        return
    counter += 1
    print(f'{counter}/{len(unclassified_images)}\t{current}')
    try:
        pil_img = Image.open(IMAGE_FOLDER + "/" + current)
    except IOError as ex:
        print(ex)
        next_img()
        return
    width, height = pil_img.size
    max_height = 1000
    if height > max_height:
        resize_factor = max_height / height
        pil_img = pil_img.resize((int(width * resize_factor), int(height * resize_factor)),
                                 resample=Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(pil_img)
    img_label.img = img_tk
    img_label.config(image=img_label.img)


def positive(arg):
    global current
    print("Positive")
    rename(IMAGE_FOLDER + "/" + current, IMAGE_FOLDER + "/1_" + current)
    next_img()


def negative(arg):
    global current
    print("Negative")
    rename(IMAGE_FOLDER + "/" + current, IMAGE_FOLDER + "/0_" + current)
    next_img()


def click_handler(event):
    event.widget.focus_set()  # give keyboard focus to the label
    event.widget.bind('<Left>', negative)
    event.widget.bind('<Right>', positive)


if __name__ == "__main__":
    root = tk.Tk()

    img_label = tk.Label(root)
    img_label.pack()
    img_label.bind("<Button-1>", click_handler)

    btn = tk.Button(root, text='Next image', command=next_img)

    next_img()  # load first image

    root.mainloop()
