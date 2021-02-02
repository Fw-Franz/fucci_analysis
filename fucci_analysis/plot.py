#!/usr/bin/env python

from fucci_analysis import data_annotation, main
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sys


class PlotUI:

    def __init__(self):
        self.root = tk.Tk()
        self.left_bar_frame = ttk.Frame(self.root, padding="12 12 12 12")
        self.left_bar_frame.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.W, tk.E, tk.S)
        )
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.title("96 Well Data Annotation")
        self.root.option_add('*tearOff', tk.FALSE)
        win = tk.Toplevel(self.root)
        menubar = tk.Menu(win)
        win['menu'] = menubar
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')

        self.filepaths = sys.argv[1:]
        # if filepaths is None or filepaths == []:
        #     filepaths = filedialog.askopenfilename(
        #         initialdir="/",
        #         title="Select file",
        #         multiple=True,
        #         filetypes=(("csv", "*.csv"))
        #     )

        self.normalization_var = tk.StringVar()
        normalization_box = ttk.Combobox(
            self.left_bar_frame,
            textvariable=self.normalization_var,
            state="readonly"
        )
        normalization_box['values'] = main.NORMALIZATION_TYPES
        normalization_box.grid(
            column=0,
            row=0
        )

        self.x_var_var = tk.StringVar()
        x_var_box = ttk.Combobox(
            self.left_bar_frame,
            textvariable=self.x_var_var,
            state="readonly"
        )
        x_var_box['values'] = main.X_VAR_TYPES
        x_var_box.grid(
            column=0,
            row=1
        )

        self.plot_context_var = tk.StringVar()
        plot_context_box = ttk.Combobox(
            self.left_bar_frame,
            textvariable=self.plot_context_var,
            state="readonly"
        )
        plot_context_box['values'] = main.PLOT_CONTEXT_TYPES
        plot_context_box.grid(
            column=0,
            row=2
        )

        self.hue_split_var = tk.StringVar()
        hue_split_box = ttk.Combobox(
            self.left_bar_frame,
            textvariable=self.hue_split_var,
            state="readonly"
        )
        hue_split_box['values'] = main.HUE_SPLIT_TYPES
        hue_split_box.grid(
            column=0,
            row=3
        )

        run_plots_button = ttk.Button(
            text="Run Plots",
            command=self._run_plots
        )

        self.root.mainloop()

    def _run_plots(self):
        main.create_plots_and_stats(
            normalization=self.normalization_var.get(),
            x_var=self.x_var.get(),
            plot_context=self.plot_context.get(),
            hue_split=self.hue_split_var.get()
        )

if __name__ == "__main__":
    PlotUI()
