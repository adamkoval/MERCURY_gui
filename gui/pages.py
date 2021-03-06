import tkinter as tk
import os
import sys
import shutil

import page_utils as pu
sys.path.append("../")
import mcm.func as mcfn
#
#   Pages
#
class HomePage(tk.Frame):
    """
    Contains welcome message and initial setup section.
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.thispage = pu.GenericPage(self, controller, "Home")

        container = tk.Frame(self, bd=5, relief="sunken")
        container.pack()

        # Welcome section
        welcome = tk.Label(container, text="MERCURY_gui",
                font=("adura", 15))
        welcome.pack()
        blurb = tk.Label(container, text=("Welcome to the MERCURY6 gui.\n"
                + "This gui was created as a university assignment.\n"
                + "It is intended to be used as a quick-start tool\n"
                + "for students working with the MERCURY6 symplectic\n"
                + "integrator."), font=("adura", 13))
        blurb.pack()
        signed = tk.Label(container, text="Written by A. Koval, in the year 2020.")
        signed.pack()

        # Setup section
        setup_section = pu.GenericCategory(self, "Initial Setup")
        if not os.path.exists("../mcm/envfile.txt"):
            envfile_button = pu.GenericButton(setup_section, text="Set up paths",
                    command=lambda: self.initial_setup())
            self.thispage.navbar.man_button.configure(state='disabled')
            nav_buttons = self.thispage.navbar.nav_buttons
            [nav_button.button.configure(state='disabled') for nav_button in nav_buttons]
        else:
            text = tk.Label(setup_section, text="envfile.txt already exists\n."
                    + "No action needed.\n")
            text.pack()
            self.thispage.navbar.man_button.configure(state='active')

    # Function to run initial setup window if no envfile.txt is found
    def initial_setup(self):
        envfile = "../mcm/envfile.txt"
        shutil.copyfile("../mcm/envfile_example.txt", envfile)
        envfile_editor = pu.TextEditor(self, envfile,
                comment="Please adjust the following entries according to your specific setup.\n"
                + "\n"
                + "HELP:\n"
                + "'pyenv': local python3 environment. Find it by typing\n"
                + "'which python3' into your (Unix) terminal app.\n"
                + "\n"
                + "'bashenv': local bash environment. Find it by typing\n"
                + "'which bash' into your (Unix) terminal app.\n"
                + "\n"
                + "'mercury_path': relative path (from this file)\n"
                + "to the git-cloned mercury6 directory.\n"
                + "\n"
                + "'results_path': relative path (from this file)\n"
                + "to the desired directory to pipe results to.\n")
        pu.create_setupdir()
        self.thispage.navbar.man_button.configure(state='active')
        nav_buttons = self.thispage.navbar.nav_buttons
        [nav_button.button.configure(state='active') for nav_button in nav_buttons]


class BodiesPage(tk.Frame):
    """
    Allows generation of big and small bodies.
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        pu.GenericPage(self, controller, "Bodies")

        big_section = pu.GenericCategory(self, "Big bodies")
        n_big = pu.count_bodies("big")
        bigin_editor = pu.BodiesEditor(big_section, btype="big", default=n_big)

        small_section = pu.GenericCategory(self, "Small bodies")
        n_small = pu.count_bodies("small")
        small_editor = pu.BodiesEditor(small_section, btype="small", default=n_small)


class SimPage(tk.Frame):
    """
    Allows the setup of simulation parameters, like number of simulations,
    number of parallel processes to run and editing MERCURY6's param.in file,
    and launches simulations, allowing the user to check their status.
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        pu.GenericPage(self, controller, "Simulation")

        # Simulation setup section
        simulation = pu.GenericCategory(self, "Set up sims")
        paramin_button = pu.GenericButton(parent=simulation, text="Edit simulation parameters",
                command=lambda: [pu.create_setupdir(),
                    pu.TextEditor(simulation, file="setup/param.in", comment="")])
        cfgin = "setup/cfg.in"
        if os.path.exists(cfgin):
            cfg = pu.read_cfg(cfgin)
            sims_default = cfg['No. sims'][1:-1]
            pnos_default = cfg['No. parallel'][1:-1]
        else:
            sims_default = ""
            pnos_default = ""
        nosims = pu.GenericInput(simulation, label="No. sims", state='normal', default=sims_default)
        pnos = pu.GenericInput(simulation, label="No. parallel", state='normal', default=pnos_default)
        pnos_disclaimer = tk.Label(simulation, text="WARNING: running too many parallel\nprocesses may saturate the\nmemory pool and cause crashes.")
        pnos_disclaimer.pack()
        entry_objects = (nosims, pnos)
        nos = {}
        store_button = pu.GenericButton(simulation, text="Save config",
                command=lambda: pu.get_cfgentries(entry_objects, nos))

        # Simulation launch section
        run = pu.GenericCategory(self, "Launch sims")
        pre_status_box = pu.StatusBox(run)
        pre_status_box.status_var.set("Ready to run.")
        go_button = pu.GenericButton(run, text="Run",
                command=lambda: pu.run_sims(pre_status_box))

        sim_status_box = pu.StatusBox(run)
        sim_status_box.status_var.set("n_completed = 0")
        check_status_button = pu.GenericButton(run, text="Check status",
                command=lambda: pu.check_sim_status(sim_status_box))


class AnalysisPage(tk.Frame):
    """
    Includes data-conversion section and plotter launch.
    """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        pu.GenericPage(self, controller, "Analysis")

        # Data conversion
        data_conversion = pu.GenericCategory(self, "Convert data")
        paramin_button = pu.GenericButton(data_conversion, text="Edit element.in",
                command=lambda: pu.TextEditor(data_conversion,
                    file="../mcm/converter/element.in", comment=""))
        bigin_button = pu.GenericButton(parent=data_conversion, text="Edit close.in",
                command=lambda: pu.TextEditor(data_conversion,
                    file="../mcm/converter/close.in", comment=""))
        files_input = pu.GenericInput(data_conversion, label="Filetype,Range", state='normal')
        files_input_instructs = tk.Label(data_conversion,
                text="Filetypes include 'xv', 'ce' or 'out'.\n"
                + "Range can have format '0', '0-4', 'all',\n"
                + "where numbers are only an example.")
        files_input_instructs.pack()
        convert_button = pu.GenericButton(data_conversion, text="Launch conversion",
                command=lambda: pu.convert_files(files=files_input.get_input()))

        # Plotter
        plotting = pu.GenericCategory(self, "Plot")
        k_input = pu.GenericInput(plotting, label="File", state="normal")
        generate_options_button = pu.GenericButton(plotting, text="Run plotter",
                 command=lambda: pu.Plotter(plotting, k_input.get_input()))
