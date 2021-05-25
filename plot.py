#!/usr/bin/env python

import data_annotation, main
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sys
import pdb

class PlotUI:

    def __init__(self, filepaths):
        self.root = tk.Tk()
        self.checkbox_frame = ttk.Frame(self.root, padding="12 12 12 12")
        self.select_frame = ttk.Frame(self.root, padding="36 12 12 12")
        self.checkbox_frame.grid(
            column=0,
            row=0,
            sticky=(tk.N, tk.W, tk.E, tk.S)
        )
        self.select_frame.grid(
            column=1,
            row=0,
            sticky=(tk.N, tk.W, tk.E, tk.S)
        )

        self.canvas_width = 100
        self.canvas_height = 50

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.title("96 Well Data Annotation")
        self.root.option_add('*tearOff', tk.FALSE)
        win = tk.Toplevel(self.root)
        menubar = tk.Menu(win)
        win['menu'] = menubar
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')

        if filepaths is None or filepaths == []:
            self.filepaths = filedialog.askopenfilename(
                initialdir="/",
                title="Select file",
                multiple=True,
                filetypes=(("csv", "*.csv"),)
            )
        else:
            self.filepaths = filepaths

        self.data = data_annotation.AnnotatedData(self.filepaths)
        self.data.load_annotated_files()
        self.conditions = self.data.get_conditions()
        self.days = range(self.data.start_day(), self.data.end_day() + 1)

        self.lineplots_var = tk.BooleanVar(value=True)
        lineplots_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.lineplots_var,
            text="lineplots"
        )
        lineplots_checkbox.grid(
            column=0,
            row=0,
            sticky=tk.W
        )

        self.stackedbarplots_var = tk.BooleanVar()
        stackedbarplots_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.stackedbarplots_var,
            text="stackedbarplots"
        )
        stackedbarplots_checkbox.grid(
            column=0,
            row=1,
            sticky=tk.W
        )

        self.boxplots_var = tk.BooleanVar()
        boxplots_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.boxplots_var,
            text="boxplots"
        )
        boxplots_checkbox.grid(
            column=0,
            row=2,
            sticky=tk.W
        )

        self.individual_plots_var = tk.BooleanVar()
        individual_plots_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.individual_plots_var,
            text="individual_plots"
        )
        individual_plots_checkbox.grid(
            column=0,
            row=3,
            sticky=tk.W
        )

        self.saveplots_var = tk.BooleanVar(value=True)
        saveplots_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.saveplots_var,
            text="saveplots"
        )
        saveplots_checkbox.grid(
            column=0,
            row=4,
            sticky=tk.W
        )

        self.plots_var = tk.BooleanVar(value=True)
        plots_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.plots_var,
            text="plots"
        )
        plots_checkbox.grid(
            column=0,
            row=5,
            sticky=tk.W
        )

        self.colormap_plot_var = tk.BooleanVar()
        colormap_plot_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.colormap_plot_var,
            text="colormap_plot"
        )
        colormap_plot_checkbox.grid(
            column=0,
            row=6,
            sticky=tk.W
        )

        self.cmap_discrete_var = tk.BooleanVar()
        cmap_discrete_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.cmap_discrete_var,
            text="cmap_discrete"
        )
        cmap_discrete_checkbox.grid(
            column=0,
            row=7,
            sticky=tk.W
        )

        self.do_ttest_var = tk.BooleanVar()
        do_ttest_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.do_ttest_var,
            text="do_ttest"
        )
        do_ttest_checkbox.grid(
            column=0,
            row=8,
            sticky=tk.W
        )

        self.do_wilcoxon_test_var = tk.BooleanVar()
        do_wilcoxon_test_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.do_wilcoxon_test_var,
            text="do_wilcoxon_test"
        )
        do_wilcoxon_test_checkbox.grid(
            column=0,
            row=9,
            sticky=tk.W
        )

        self.do_anova_var = tk.BooleanVar()
        do_anova_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.do_anova_var,
            text="do_anova"
        )
        do_anova_checkbox.grid(
            column=0,
            row=10,
            sticky=tk.W
        )

        self.do_tukey_test_var = tk.BooleanVar()
        do_tukey_test_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.do_tukey_test_var,
            text="do_tukey_test"
        )
        do_tukey_test_checkbox.grid(
            column=0,
            row=11,
            sticky=tk.W
        )

        self.save_excel_stats_var = tk.BooleanVar()
        save_excel_stats_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            variable=self.save_excel_stats_var,
            text="save_excel_stats"
        )
        save_excel_stats_checkbox.grid(
            column=0,
            row=12,
            sticky=tk.W
        )


        normalization_label = ttk.Label(
            self.select_frame,
            text="Normalization Type",
            justify="left"
        )
        normalization_label.grid(
            column=0,
            row=0,
            sticky=tk.W
        )
        self.normalization_var = tk.StringVar()
        normalization_box = ttk.Combobox(
            self.select_frame,
            textvariable=self.normalization_var,
            state="readonly",
            values=main.NORMALIZATION_TYPES
        )
        normalization_box.current(0)
        normalization_box.grid(
            column=1,
            row=0
        )

        analyze_method_label = ttk.Label(
            self.select_frame,
            text="Analyze Method",
            justify="left"
        )
        analyze_method_label.grid(
            column=0,
            row=1,
            sticky=tk.W
        )
        self.analyze_method_var = tk.StringVar()
        analyze_method_box = ttk.Combobox(
            self.select_frame,
            textvariable=self.analyze_method_var,
            state="readonly",
            values=main.ANALYZE_METHODS
        )
        analyze_method_box.current(0)
        analyze_method_box.grid(
            column=1,
            row=1
        )

        x_var_label = ttk.Label(
            self.select_frame,
            text="X variable",
            justify="left"
        )
        x_var_label.grid(
            column=0,
            row=2,
            sticky=tk.W
        )
        self.x_var_var = tk.StringVar()
        x_var_box = ttk.Combobox(
            self.select_frame,
            textvariable=self.x_var_var,
            state="readonly",
            values=main.X_VAR_TYPES
        )
        x_var_box.current(0)
        x_var_box.grid(
            column=1,
            row=2
        )

        plot_context_label = ttk.Label(
            self.select_frame,
            text="Plot Context",
            justify="left"
        )
        plot_context_label.grid(
            column=0,
            row=3,
            sticky=tk.W
        )
        self.plot_context_var = tk.StringVar()
        plot_context_box = ttk.Combobox(
            self.select_frame,
            textvariable=self.plot_context_var,
            state="readonly",
            values=main.PLOT_CONTEXT_TYPES
        )
        plot_context_box.current(0)
        plot_context_box.grid(
            column=1,
            row=3
        )

        hue_split_label = ttk.Label(
            self.select_frame,
            text="Hue Split"
        )
        hue_split_label.grid(
            column=0,
            row=4,
            sticky=tk.W
        )
        self.hue_split_var = tk.StringVar()
        hue_split_box = ttk.Combobox(
            self.select_frame,
            textvariable=self.hue_split_var,
            state="readonly",
            values=main.HUE_SPLIT_TYPES
        )
        hue_split_box.current(0)
        hue_split_box.grid(
            column=1,
            row=4
        )

        control_condition_label = ttk.Label(
            self.select_frame,
            text="Control condition"
        )
        control_condition_label.grid(
            column=0,
            row=5,
            sticky=tk.W
        )
        self.control_condition_var = tk.StringVar()
        control_condition_box = ttk.Combobox(
            self.select_frame,
            textvariable=self.control_condition_var,
            state="readonly",
            values=list(self.conditions)
        )
        control_condition_box.current(0)
        control_condition_box.grid(
            column=1,
            row=5
        )

        box_day_label = ttk.Label(
            self.select_frame,
            text="Box day"
        )
        box_day_label.grid(
            column=0,
            row=6,
            sticky=tk.W
        )
        self.box_day_var = tk.IntVar()
        box_day_box = ttk.Combobox(
            self.select_frame,
            textvariable=self.box_day_var,
            state="readonly",
            values=list(self.days)
        )
        box_day_box.current(0)
        box_day_box.grid(
            column=1,
            row=6
        )


        stats_var_label = ttk.Label(
            self.select_frame,
            text="Stats var"
        )
        stats_var_label.grid(
            column=0,
            row=7,
            sticky=tk.W
        )
        self.stats_var_var = tk.StringVar()
        stats_var_box = ttk.Combobox(
            self.select_frame,
            textvariable=self.stats_var_var,
            state="readonly",
            values=main.STATS_VARS_TYPES
        )
        stats_var_box.current(0)
        stats_var_box.grid(
            column=1,
            row=7
        )

        conditions_override_label = ttk.Label(
            self.select_frame,
            text="Conditions override"
        )
        conditions_override_label.grid(
            column=0,
            row=8,
            sticky=tk.W
        )

        self.conditions_override_listbox = tk.Listbox(
            self.select_frame,
            width=self.canvas_width,
            selectmode=tk.MULTIPLE
        )
        for condition in self.conditions:
            self.conditions_override_listbox.insert(tk.END, condition)
        self.conditions_override_listbox.grid(
            column=1,
            row=8
        )

        run_plots_button = ttk.Button(
            self.select_frame,
            text="Run Plots",
            command=self._run_plots
        )
        run_plots_button.grid(
            column=1,
            row=10,
            sticky=tk.E
        )

        self.root.mainloop()

    def _get_conditions_override(self):
        selected = self.conditions_override_listbox.curselection()
        return [self.conditions_override_listbox.get(i) for i in selected]

    def _run_plots(self):
        try:
            main.create_plots_and_stats(
                normalization_type=self.normalization_var.get(),
                analyze_method=self.analyze_method_var.get(),
                x_var=self.x_var_var.get(),
                plot_context=self.plot_context_var.get(),
                hue_split=self.hue_split_var.get(),
                control_condition=self.control_condition_var.get(),
                conditions_override = self._get_conditions_override(),
                filepaths=self.filepaths,
                stats_vars=[self.stats_var_var.get()],
                box_day=int(self.box_day_var.get()),
                plots=self.plots_var.get(),
                lineplots=self.lineplots_var.get(),
                boxplots=self.boxplots_var.get(),
                stackedbarplots=self.stackedbarplots_var.get(),
                individual_plots=self.individual_plots_var.get(),
                save_plots=self.saveplots_var.get(),
                colormap_plot=self.colormap_plot_var.get(),
                cmap_discrete=self.cmap_discrete_var.get(),
                do_ttest=self.do_ttest_var.get(),
                do_wilcoxon_test=self.do_wilcoxon_test_var.get(),
                do_anova=self.do_anova_var.get(),
                do_tukey_test=self.do_tukey_test_var.get(),
                save_excel_stats=self.save_excel_stats_var.get()
            )
        except RuntimeError as err:
            pdb.set_trace()
            message = '\n'.join(["Cannot run plots:", *err.args])
            messagebox.showinfo(message=message)

if __name__ == "__main__":
    filepaths = sys.argv[1:]
    PlotUI(filepaths)
