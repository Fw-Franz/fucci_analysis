#!/usr/bin/env python

from fucci_analysis import data_annotation
from fucci_analysis import colors
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from platform import system
import sys

X_DIMENSION_WELLS = 12
Y_DIMENSION_WELLS = 8
WELL_COUNT = X_DIMENSION_WELLS * Y_DIMENSION_WELLS

SQUARE_SIZE = 30
X_OFFSET = 1
Y_OFFSET = 1
CANVAS_WIDTH = SQUARE_SIZE * (X_DIMENSION_WELLS + 2 * X_OFFSET)
CANVAS_HEIGHT = SQUARE_SIZE * (Y_DIMENSION_WELLS + 2 * Y_OFFSET)


class Plate():

    def __init__(self):
        self.current_plate_num = 1
        self.data = None

    def main(self):
        self.root = tk.Tk()
        self.left_bar_frame = ttk.Frame(self.root, padding="12 12 12 12")
        self.left_bar_frame.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.W, tk.E, tk.S)
        )
        self.right_bar_frame = ttk.Frame(self.root)
        self.right_bar_frame.grid(
            column=1,
            row=0,
            sticky=(tk.N, tk.W, tk.E, tk.S)
        )
        self.right_bar_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.title("96 Well Data Annotation")
        self.root.option_add('*tearOff', tk.FALSE)
        win = tk.Toplevel(self.root)
        menubar = tk.Menu(win)
        win['menu'] = menubar
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Save', command=self.save)

        filepaths = sys.argv[1:]
        self.open_files(filepaths)
        self.current_condition = tk.StringVar()

        self.condition_to_add = tk.StringVar()
        condition_entry = ttk.Entry(
            self.left_bar_frame,
            textvariable=self.condition_to_add
        )

        def add_condition_and_clear(e):
            self.add_condition(self.condition_to_add.get())
            self.condition_to_add.set("")

        condition_entry.bind(
            '<Return>',
            add_condition_and_clear
        )
        condition_entry.grid(
            column=0,
            row=2
        )
        add_condition_entry = ttk.Button(
            self.left_bar_frame,
            text="Add Condition",
            command=lambda: self.add_condition(self.condition_to_add.get())
        )
        add_condition_entry.bind(
            '<Return>',
            lambda e: self.add_condition(self.condition_to_add.get())
        )
        add_condition_entry.grid(
            column=0,
            row=3
        )

        self.conditions_radio_frame = ttk.Frame(self.left_bar_frame)
        self.conditions_radio_frame.grid(
            column=0,
            row=4,
            sticky=(tk.N, tk.W, tk.S, tk.E)
        )
        self.condition_color_map = {}
        self.color_count = 0
        self.add_condition("None", "white")

        self.frame_to_add = tk.StringVar()
        frame_entry = ttk.Entry(
            self.left_bar_frame,
            textvariable=self.frame_to_add
        )
        frame_entry.bind(
            '<Return>',
            lambda e: self.set_frame(self.frame_to_add.get())
        )
        frame_entry.grid(
            column=0,
            row=0
        )
        frame_button = ttk.Button(
            self.left_bar_frame,
            text="Set frame",
            command=lambda: self.set_frame(self.frame_to_add.get())
        )
        frame_button.grid(
            column=0,
            row=1
        )

        self.root.mainloop()

    def add_condition(self, condition, color=None):
        if condition == "":
            return
        if color is None:
            color = colors.COLORS[self.color_count]
            self.color_count += 1

        self.condition_color_map[condition] = color
        radio = tk.Radiobutton(
            self.conditions_radio_frame,
            text=condition,
            value=condition,
            variable=self.current_condition
        )
        radio.grid(
            sticky=tk.W
        )
        self.current_condition.set(condition)
        print(self.current_condition.get())

    def open_files(self, filepaths=None):
        if filepaths is None or filepaths == []:
            filepaths = filedialog.askopenfilename(
                initialdir="/",
                title="Select file",
                multiple=True,
                filetypes=(("Excel", "*.xlsx"), ("csv", "*.csv"))
            )
        self.data = data_annotation.AnnotatedData(filepaths)
        print(self.data.dataframe)

        self.plate_nums = self.data.plate_nums()

        self.canvas_width = (SQUARE_SIZE *
                             (X_DIMENSION_WELLS + 2 * X_OFFSET))
        self.canvas_height = (SQUARE_SIZE *
                              (Y_DIMENSION_WELLS + 2 * Y_OFFSET) *
                              self.plate_nums)

        self.canvas = tk.Canvas(
            self.right_bar_frame,
            scrollregion=(0, 0, self.canvas_width, self.canvas_height),
            width=self.canvas_width
        )
        canvas_scroll = ttk.Scrollbar(
            self.right_bar_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        self.canvas.configure(
            yscrollcommand=canvas_scroll.set
        )
        self.canvas.grid(
            row=0,
            column=0,
            sticky=(tk.N, tk.W, tk.S, tk.E)
        )
        canvas_scroll.grid(
            row=0,
            column=1,
            sticky=(tk.N, tk.W, tk.S, tk.E)
        )

        def scroll(event):
            # scroll units work differently on different OS
            # see here: https://stackoverflow.com/a/17457843
            if system() == "Darwin":
                conversion = 1
            else:
                conversion = 120
            self.canvas.yview_scroll(-1*event.delta // conversion, "units")

        self.canvas.bind_all(
            "<MouseWheel>",
            scroll
        )

        for plate_num in range(1, self.plate_nums + 1):
            self.add_plate(plate_num)

    @staticmethod
    def xy_to_well_num(x, y):
        return (y * X_DIMENSION_WELLS) + (x + 1)

    @staticmethod
    def well_num_to_xy(well_num):
        return ((well_num - 1) % X_DIMENSION_WELLS,
                (well_num - 1) // X_DIMENSION_WELLS)

    def add_plate(self, plate_num):
        for x in range(X_DIMENSION_WELLS):
            for y in range(Y_DIMENSION_WELLS):
                self.add_square(x, y, plate_num)

    def add_square(self, x, y, plate_num):
        plate_offset = (Y_OFFSET + Y_DIMENSION_WELLS) * (plate_num - 1) + 1
        position = (
            SQUARE_SIZE * (x + X_OFFSET),
            SQUARE_SIZE * (y + plate_offset),
            SQUARE_SIZE * (x + 1 + X_OFFSET),
            SQUARE_SIZE * (y + 1 + plate_offset)
        )
        well_num = self.xy_to_well_num(x, y)
        self.canvas.create_rectangle(
            position,
            fill="white",
            outline="black",
            tags=(f'well_num={well_num}', f'plate_num={plate_num}')
        )
        self.canvas.bind('<ButtonPress-1>', self.click_square)
        self.canvas.bind('<B1-Motion>', self.click_square)

    @staticmethod
    def get_tag_info(tags, prefix):
        try:
            return [int(tag.split(prefix)[1]) for tag in tags
                    if tag[0:len(prefix)] == prefix][0]
        except IndexError:
            return None

    def click_square(self, event):
        square_id = event.widget.find_closest(event.x, event.y)
        tags = self.canvas.gettags(*square_id)
        well_num = self.get_tag_info(tags, "well_num=")
        plate_num = self.get_tag_info(tags, "plate_num=")
        if well_num and plate_num:
            print(f'Clicked: well_num {well_num}, plate_num {plate_num}')
            condition = self.current_condition.get()
            self.canvas.itemconfig(
                square_id,
                fill=self.condition_color_map[condition]
            )
            self.data.set_condition(
                condition,
                well_num,
                plate_num
            )
            print(self.data.dataframe)

    def save(self):
        try:
            path = self.data.save()
            print(f'Saved to {path}')
        except RuntimeError as err:
            message = '\n'.join(["Cannot save:", *err.args])
            messagebox.showinfo(message=message)

    def set_frame(self, frame):
        if frame:
            frame = int(frame)
            self.data.set_frame(frame)
            print(self.data.frame)


if __name__ == "__main__":
    plate = Plate()
    plate.main()
