import tkinter as tk
import os
from tkinter.filedialog import askopenfilename, asksaveasfilename


def open_file():
    #validamos que solo pueda ingresar decaf
    filepath = open_file()
    if not filepath:
        return txt_edit.delete(1.0, tk.END)
    with open(filepath, "r") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)

def save_file():
    pass

def run_decaf():
    pass

user_interface = tk.Tk()
user_interface.title("Proyecto de compiladores")
user_interface.rowconfigure(0, minsize = 400, weight = 1)
user_interface.columnconfigure(1, minsize = 800, weight = 1)
user_interface.columnconfigure(2, minsize = 400, weight = 1)

txt_edit = tk.Text(user_interface)
fr_buttons = tk.Frame(user_interface, relief = tk.RAISED, bd = 2)
btn_open = tk.Button(fr_buttons, text = "Abrir nuevo archivo", command = open_file)
btn_run = tk.Button(fr_buttons, text = "Ejecutar", command = run_decaf)
btn_save = tk.Button(fr_buttons, text = "Guardar archivo", command = save_file)

label_errors = tk.Label(user_interface, text="Errores")

btn_open.grid(row = 0, column = 0, sticky = "EW", padx = 5, pady = 3)
btn_run.grid(row = 2, column = 0, sticky = "EW", padx = 5, pady = 3)
btn_save.grid(row = 1, column = 0, sticky = "EW", padx = 5, pady = 3)
fr_buttons.grid(row = 0, column = 0, sticky = "NS")

txt_edit.grid(row=0, column=1, sticky="NSEW")

label_errors.grid(row=0, column=2, sticky="NW", padx=5, pady=5)

user_interface.mainloop()