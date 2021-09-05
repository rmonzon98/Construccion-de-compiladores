from sys import int_info
import tkinter as tk
import os
from tkinter.constants import ANCHOR
from tkinter.filedialog import askopenfilename, asksaveasfilename
from main import *

#--------------------------functions--------------------------
def abrir():
    filepath = askopenfilename(
        filetypes=[("Decaf", "*.decaf")]
    )
    if not filepath:
        return
    txt_edit.delete(1.0, tk.END)
    with open(filepath, "r") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)
    label_errors.config(text='')
    label_symbol.config(text='')

def guardar():
    filepath = asksaveasfilename(
        defaultextension="decaf",
        filetypes=[("Decaf", "*.decaf")],
    )
    if not filepath:
        return
    with open(filepath, "w") as output_file:
        text = txt_edit.get(1.0, tk.END)
        output_file.write(text)
    label_errors.config(text='')
    label_symbol.config(text='')
    

def ejecutar():
    filepath = askopenfilename(
        filetypes=[("Decaf", "*.decaf")]
    )
    if not filepath:
        return
    txt_edit.delete(1.0, tk.END)
    with open(filepath, "r") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)

    errors, info = executeWalker(filepath)

    label_symbol.config(text=info)

    n = len(errors)
    errorsMsg = ''
    for i in range(n):
        errorsMsg = errorsMsg + errors[i]+'\n'
    if (n == 0): 
        errorsMsg = "No hay errores"
    label_errors.config(text=errorsMsg)

#--------------------------GUI--------------------------
userI = tk.Tk()
userI.title("Proyecto de construcción de compiladores")
userI.rowconfigure(0, minsize=800, weight=1)
userI.columnconfigure(0, minsize=400, weight=1)
userI.columnconfigure(1, minsize=400, weight=1)
txt_edit = tk.Text(userI)
fr_left_panel = tk.Frame(userI)
btn_open = tk.Button(fr_left_panel, text="Abrir", command=abrir)
btn_save = tk.Button(fr_left_panel, text="guardar", command=guardar)
btn_run = tk.Button(fr_left_panel, text="Ejecutar", command=ejecutar)
label_errors = tk.Label(fr_left_panel, text="")
label_symbol = tk.Label(fr_left_panel, text="")
btn_open.grid(row=0, column=0, sticky="EW", padx=5)
btn_save.grid(row=1, column=0, sticky="EW", padx=5)
btn_run.grid(row=2, column=0, sticky="EW", padx=5)
label_errors.grid(row=0, column=2, sticky="E", padx=5, pady=5)
label_symbol.grid(row=0, column=1, sticky="E", padx=5, pady=5)
fr_left_panel.grid(row=0, column=0, sticky="NS")
txt_edit.grid(row=0, column=1, sticky="NSEW")
userI.mainloop()