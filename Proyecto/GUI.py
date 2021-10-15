from sys import int_info
import tkinter as tk
from tkinter import ttk
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
    label_ci.insert(tk.END, "")

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
    label_ci.insert(tk.END, "")
    

def ejecutar():
    filepath = 'executiontemp.decaf'
    with open(filepath, "w") as output_file:
        text = txt_edit.get(1.0, tk.END)
        output_file.write(text)
    errors, ic = executeWalker(filepath)
    lines = len(errors)
    errorsMsg = ''
    for i in range(lines):
        errorsMsg = errorsMsg + errors[i]+'\n'
    if (lines == 0): 
        errorsMsg = "No hay errores"
    label_ci.insert(tk.END, "\t\t\tErrores:\n"+errorsMsg+"\n\n\t\t\tCodigo intermedio:"+ic)

#--------------------------GUI--------------------------
userI = tk.Tk()
userI.title("Proyecto de construcción de compiladores")

userI.rowconfigure(0, minsize=800, weight=1)
userI.columnconfigure(0)
userI.columnconfigure(1)
userI.columnconfigure(2)
userI.columnconfigure(3)

code_frame = ttk.Frame(userI)
code_frame.rowconfigure(0, minsize=800, weight=1)
code_frame.columnconfigure(0, minsize=150, weight=1)
txt_edit = tk.Text(code_frame)
txt_edit.grid(row=0, column=0, sticky="NSEW")
code_frame.grid(column=0, row=0)

ci_frame = ttk.Frame(userI)
ci_frame.rowconfigure(0, minsize=800, weight=1)
ci_frame.columnconfigure(0, weight=1)
label_ci = tk.Text(ci_frame)
label_ci.grid(row=0, column=0, sticky="NSEW", padx=5, pady=5)
ci_frame.grid(column=1, row=0)

buttons_frame = ttk.Frame(userI)
buttons_frame.columnconfigure(0, weight=1)
ttk.Button(buttons_frame, text= 'Abrir', command=abrir).grid(column=0, row=0)
ttk.Button(buttons_frame, text='Guardar', command=guardar).grid(column=0, row=1)
ttk.Button(buttons_frame, text= 'Ejecutar', command=ejecutar).grid(column=0, row=2)
buttons_frame.grid(column=2, row=0)

userI.mainloop()