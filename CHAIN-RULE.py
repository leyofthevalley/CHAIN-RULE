#To run the code. First, install the sympy by typing 'pip install sympy' on the terminal.
#Make sure to have python first.

import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp

total_chain_result = None
result_boxes = []
focused_entry = None

def validate_input(expression):
    try:
        expression = expression.replace('^', '**')
        return sp.sympify(expression, locals={
            "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
            "exp": sp.exp, "log": sp.log, "sqrt": sp.sqrt
        })
    except (sp.SympifyError, SyntaxError):
        raise ValueError("Invalid input! Use correct syntax: e.g., '2*x', 'x^2', or 'sin(u)'.")

def chain_rule_calculator(inner_func, outer_func, variable):
    x = sp.symbols(variable)
    inner = validate_input(inner_func)
    u = sp.Function('u')(x)

    outer_expr = validate_input(outer_func.replace('u', str(u)))
    inner_derivative = sp.diff(inner, x)

    outer_func_clean = outer_func.replace(' ', '').lower()
    manual = False

    if outer_func_clean == "sin(u)":
        outer_derivative = sp.cos(u)
        manual = True
        outer_rule_str = "cos(u)"
    elif outer_func_clean == "cos(u)":
        outer_derivative = -sp.sin(u)
        manual = True
        outer_rule_str = "-sin(u)"
    elif outer_func_clean == "tan(u)":
        outer_derivative = sp.sec(u)**2
        manual = True
        outer_rule_str = "sec(u)^2"
    elif outer_func_clean == "cot(u)":
        outer_derivative = -sp.csc(u)**2
        manual = True
        outer_rule_str = "-csc(u)^2"
    elif outer_func_clean == "csc(u)":
        outer_derivative = -sp.csc(u) * sp.cot(u)
        manual = True
        outer_rule_str = "-csc(u) cot(u)"
    elif outer_func_clean == "sec(u)":
        outer_derivative = sp.sec(u) * sp.tan(u)
        manual = True
        outer_rule_str = "sec(u) tan(u)"
    elif '^' in outer_func_clean:
        base, exponent = outer_func_clean.split('^')
        if base == 'u' and exponent.isnumeric():
            outer_derivative = int(exponent) * u**(int(exponent) - 1)
            manual = True
            outer_rule_str = f"{exponent}*u^{int(exponent) - 1}"
    else:
        outer_derivative = sp.diff(outer_expr, u)
        outer_rule_str = str(outer_derivative)

    substituted = outer_derivative.subs(u, inner)
    result = substituted * inner_derivative

    steps = (
        f"Step-by-step solution (Chain Rule):\n\n"
        f"1. Let g({x}) = {inner}\n"
        f"2. Let f(u) = {outer_func}\n"
        f"3. Compute g'({x}) = {inner_derivative}\n"
        f"4. Compute f'(u) = {outer_rule_str}\n"
        f"5. Substitute u = g({x}) into f'(u): f'(g({x})) = {substituted}\n"
        f"6. Multiply by g'({x}): {substituted} * {inner_derivative}\n"
        f"7. Simplify: {sp.simplify(result)}"
    )
    return sp.simplify(result), steps

def quotient_rule_calculator(numerator, denominator, variable):
    x = sp.symbols(variable)
    num = validate_input(numerator)
    denom = validate_input(denominator)
    num_derivative = sp.diff(num, x)
    denom_derivative = sp.diff(denom, x)
    result = (num_derivative * denom - num * denom_derivative) / denom**2
    steps = (
        f"Step-by-step solution (Quotient Rule):\n\n"
        f"1. Let u(x) = {num}, v(x) = {denom}\n"
        f"2. Compute u'({x}) = {num_derivative}, v'({x}) = {denom_derivative}\n"
        f"3. Apply the quotient rule:\n"
        f"   (u' * v - u * v') / v^2 = ({num_derivative} * {denom} - {num} * {denom_derivative}) / ({denom})^2\n"
        f"4. Simplify: {sp.simplify(result)}"
    )
    return sp.simplify(result), steps

def calculate():
    global total_chain_result
    mode = mode_var.get()
    steps_box.delete("1.0", tk.END)
    try:
        if mode == "Chain Rule":
            inner = inner_entry.get()
            outer = outer_entry.get()
            var = variable_entry.get()
            result, steps = chain_rule_calculator(inner, outer, var)
            total_chain_result = total_chain_result + result if total_chain_result else result
            output_var.set(str(sp.simplify(total_chain_result)))
            steps_box.insert(tk.END, steps)
        elif mode == "Quotient Rule":
            numerator = inner_entry.get()
            denominator = outer_entry.get()
            var = variable_entry.get()
            result, steps = quotient_rule_calculator(numerator, denominator, var)
            output_var.set(str(result))
            steps_box.insert(tk.END, steps)
            total_chain_result = None
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_more():
    if mode_var.get() != "Chain Rule":
        messagebox.showinfo("Not Supported", "Add Equation is only for Chain Rule mode.")
        return
    current_result = output_var.get().strip()
    print(f"DEBUG: Current Result = {current_result}")  # Debugging line
    if not current_result:
        messagebox.showinfo("Error", "No result available. Please calculate first.")
        return
    label_text = f"Base Result: {current_result}" if not result_boxes else f"Combined Result: {current_result}"
    add_result_to_history(label_text)
    inner_entry.delete(0, tk.END)
    outer_entry.delete(0, tk.END)
    steps_box.delete("1.0", tk.END)

def add_result_to_history(label_text):
    print(f"DEBUG: Adding to history: {label_text}")
    result_label = ttk.Entry(history_frame, width=54)
    result_label.insert(0, label_text)
    result_label.config(state="readonly")
    result_label.grid(column=0, row=len(result_boxes), padx=5, pady=2)
    result_boxes.append(result_label)
    print(f"DEBUG: Total results in history: {len(result_boxes)}")

def reset_fields():
    global total_chain_result, result_boxes
    inner_entry.delete(0, tk.END)
    outer_entry.delete(0, tk.END)
    variable_entry.delete(0, tk.END)
    output_var.set("")
    steps_box.delete("1.0", tk.END)
    total_chain_result = None
    for box in result_boxes:
        box.destroy()
    result_boxes.clear()

def update_fields(*args):
    reset_fields()
    mode = mode_var.get()
    label1.config(text="Inner Function (e.g., 2*x+5)" if mode == "Chain Rule" else "Numerator")
    label2.config(text="Outer Function (e.g., u^2)" if mode == "Chain Rule" else "Denominator")

def set_focused_entry(event):
    global focused_entry
    focused_entry = event.widget

def insert_to_focused_entry(value):
    if focused_entry:
        focused_entry.insert(tk.END, value)

def clear_focused_entry():
    if focused_entry:
        focused_entry.delete(0, tk.END)

def backspace_focused_entry():
    if focused_entry:
        current = focused_entry.get()
        focused_entry.delete(0, tk.END)
        focused_entry.insert(0, current[:-1])

root = tk.Tk()
root.title("Derivative Calculator - Chain & Quotient Rule")
root.configure(bg="#1e1e2f")
root.resizable(True, True)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 1366  
window_height = 850  

position_x = (screen_width - window_width) // 2
position_y = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

style = ttk.Style()
style.theme_use('default')
style.configure("TLabel", font=("Arial", 13), background="#1e1e2f", foreground="white")
style.configure("TEntry", font=("Arial", 14), padding=5)
style.configure("TButton", font=("Arial", 12), padding=5)
style.configure("TCombobox", font=("Arial", 13))
style.configure("TLabelframe", background="#1e1e2f", foreground="white")
style.configure("TLabelframe.Label", background="#1e1e2f", foreground="white")
style.configure("TFrame", background="#1e1e2f")

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

top_frame = ttk.Frame(root, style="TFrame")
top_frame.grid(column=0, row=0, columnspan=2, padx=10, pady=10, sticky="ew")

title_label = ttk.Label(
    top_frame,
    text="DERIVATIVE CALCULATOR - CHAIN AND QUOTIENT RULE",
    font=("Arial", 16, "bold"),
    background="#1e1e2f",
    foreground="white",
    anchor="center"
)
title_label.pack(fill="x", padx=10, pady=(10, 5))

instruction_frame = ttk.LabelFrame(top_frame, text="Instructions", padding=10, style="TLabelframe")
instruction_frame.pack(fill="x", padx=10, pady=5)

instruction_text = (
    "1. Select the mode: Chain Rule or Quotient Rule.\n"
    "2. Fill in the required functions and variable (e.g., x).\n"
    "   - Chain Rule: use 'u' for outer function (e.g., sin(u), u^2, etc.)\n"
    "   - Quotient Rule: specify numerator and denominator.\n"
    "3. Click 'Calculate' to compute the derivative.\n\n"
    "Limitations:\n"
    "- Use '*' for multiplication (2*x not 2x).\n"
    "- Use '^' or '**' for powers.\n"
    "- Supported functions: sin, cos, tan, log, exp, sqrt.\n"
    "- Only basic single-variable functions are supported."
)
instruction_label = ttk.Label(instruction_frame, text=instruction_text, justify="left", style="TLabel", anchor="w")
instruction_label.pack(fill="x", padx=10, pady=5)

mode_var = tk.StringVar(value="Chain Rule")
output_var = tk.StringVar()

# Left Section: Calculator
left_frame = ttk.Frame(root, style="TFrame")
left_frame.grid(column=0, row=1, padx=10, pady=15, sticky="nsew")

ttk.Label(left_frame, text="Select Mode:").grid(column=0, row=0, padx=10, pady=5, sticky="w")
mode_menu = ttk.Combobox(left_frame, textvariable=mode_var, values=["Chain Rule", "Quotient Rule"], state="readonly", width=20)
mode_menu.grid(column=1, row=0, padx=10, pady=5, sticky="w")
mode_menu.configure(font=("Arial", 13)) 
mode_menu.bind("<<ComboboxSelected>>", update_fields)

label1 = ttk.Label(left_frame, text="Inner Function:")
label1.grid(column=0, row=1, padx=10, pady=5, sticky="w")
inner_entry = ttk.Entry(left_frame, width=40)
inner_entry.grid(column=1, row=1, padx=10, pady=5, sticky="w")

label2 = ttk.Label(left_frame, text="Outer Function:")
label2.grid(column=0, row=2, padx=10, pady=5, sticky="w")
outer_entry = ttk.Entry(left_frame, width=40)
outer_entry.grid(column=1, row=2, padx=10, pady=5, sticky="w")

ttk.Label(left_frame, text="Variable (e.g., x):").grid(column=0, row=3, padx=10, pady=5, sticky="w")
variable_entry = ttk.Entry(left_frame, width=15)
variable_entry.grid(column=1, row=3, padx=10, pady=5, sticky="w")


inner_entry.bind("<FocusIn>", set_focused_entry)
outer_entry.bind("<FocusIn>", set_focused_entry)
variable_entry.bind("<FocusIn>", set_focused_entry)

button_frame = ttk.Frame(left_frame, style="TFrame")
button_frame.grid(column=0, row=4, columnspan=2, pady=10)
ttk.Button(button_frame, text="Calculate", command=calculate).grid(column=0, row=0, padx=5)
ttk.Button(button_frame, text="Reset", command=reset_fields).grid(column=1, row=0, padx=5)
ttk.Button(button_frame, text="Add Equation", command=add_more).grid(column=2, row=0, padx=5)

ttk.Label(left_frame, text="Current Result:").grid(column=0, row=5, padx=10, pady=5, sticky="w")
ttk.Entry(left_frame, textvariable=output_var, width=55).grid(column=1, row=5, padx=10, pady=5, sticky="w")

ttk.Label(left_frame, text="Previous Results:").grid(column=0, row=6, padx=10, pady=10, sticky="w")

history_frame = ttk.Frame(left_frame, style="TFrame")
history_frame.grid(column=1, row=6, padx=10, pady=10, sticky="w")
left_frame.rowconfigure(7, weight=1)
history_frame.columnconfigure(0, weight=1)

button_panel = ttk.LabelFrame(left_frame, text="Input Buttons", padding=10, style="TLabelframe")
button_panel.grid(column=0, row=8, columnspan=2, padx=10, pady=10)


buttons = [
    ['7', '8', '9', '(', ')', 'Clear', '←'],
    ['4', '5', '6', '*', '/', 'sin', 'cos'],
    ['1', '2', '3', '+', '-', 'tan', 'log'],
    ['exp', '0', '.', 'u', 'x', '^', '^2']
]

for r, row in enumerate(buttons):
    for c, char in enumerate(row):
        action = lambda val=char: insert_to_focused_entry(val if val != '^2' else '**2')
        ttk.Button(button_panel, text=char, width=9, command=action).grid(row=r, column=c, padx=2, pady=2)

for child in button_panel.winfo_children():
    if child['text'] == 'Clear':
        child.config(command=clear_focused_entry)
    elif child['text'] == '←':
        child.config(command=backspace_focused_entry)

right_frame = ttk.Frame(root, style="TFrame")
right_frame.grid(column=1, row=1, padx=10, pady=10, sticky="nsew")

ttk.Label(right_frame, text="Step-by-step Solution:").grid(column=0, row=0, padx=10, pady=(0, 5), sticky="nw")
steps_box = tk.Text(right_frame, width=55, bg="#282c34", fg="white", font=("Courier", 12))
steps_box.grid(column=0, row=1, padx=10, pady=5, sticky="nsew")


update_fields()
root.update()
left_frame.columnconfigure(1, weight=1)
right_frame.columnconfigure(0, weight=1)
right_frame.rowconfigure(1, weight=1)
root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp

total_chain_result = None
result_boxes = []
focused_entry = None

def validate_input(expression):
    try:
        expression = expression.replace('^', '**')
        return sp.sympify(expression, locals={
            "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
            "exp": sp.exp, "log": sp.log, "sqrt": sp.sqrt
        })
    except (sp.SympifyError, SyntaxError):
        raise ValueError("Invalid input! Use correct syntax: e.g., '2*x', 'x^2', or 'sin(u)'.")

def chain_rule_calculator(inner_func, outer_func, variable):
    x = sp.symbols(variable)
    inner = validate_input(inner_func)
    u = sp.Function('u')(x)

    outer_expr = validate_input(outer_func.replace('u', str(u)))
    inner_derivative = sp.diff(inner, x)

    outer_func_clean = outer_func.replace(' ', '').lower()
    manual = False

    if outer_func_clean == "sin(u)":
        outer_derivative = sp.cos(u)
        manual = True
        outer_rule_str = "cos(u)"
    elif outer_func_clean == "cos(u)":
        outer_derivative = -sp.sin(u)
        manual = True
        outer_rule_str = "-sin(u)"
    elif outer_func_clean == "tan(u)":
        outer_derivative = sp.sec(u)**2
        manual = True
        outer_rule_str = "sec(u)^2"
    elif outer_func_clean == "cot(u)":
        outer_derivative = -sp.csc(u)**2
        manual = True
        outer_rule_str = "-csc(u)^2"
    elif outer_func_clean == "csc(u)":
        outer_derivative = -sp.csc(u) * sp.cot(u)
        manual = True
        outer_rule_str = "-csc(u) cot(u)"
    elif outer_func_clean == "sec(u)":
        outer_derivative = sp.sec(u) * sp.tan(u)
        manual = True
        outer_rule_str = "sec(u) tan(u)"
    elif '^' in outer_func_clean:
        base, exponent = outer_func_clean.split('^')
        if base == 'u' and exponent.isnumeric():
            outer_derivative = int(exponent) * u**(int(exponent) - 1)
            manual = True
            outer_rule_str = f"{exponent}*u^{int(exponent) - 1}"
    else:
        outer_derivative = sp.diff(outer_expr, u)
        outer_rule_str = str(outer_derivative)

    substituted = outer_derivative.subs(u, inner)
    result = substituted * inner_derivative

    steps = (
        f"Step-by-step solution (Chain Rule):\n\n"
        f"1. Let g({x}) = {inner}\n"
        f"2. Let f(u) = {outer_func}\n"
        f"3. Compute g'({x}) = {inner_derivative}\n"
        f"4. Compute f'(u) = {outer_rule_str}\n"
        f"5. Substitute u = g({x}) into f'(u): f'(g({x})) = {substituted}\n"
        f"6. Multiply by g'({x}): {substituted} * {inner_derivative}\n"
        f"7. Simplify: {sp.simplify(result)}"
    )
    return sp.simplify(result), steps

def quotient_rule_calculator(numerator, denominator, variable):
    x = sp.symbols(variable)
    num = validate_input(numerator)
    denom = validate_input(denominator)
    num_derivative = sp.diff(num, x)
    denom_derivative = sp.diff(denom, x)
    result = (num_derivative * denom - num * denom_derivative) / denom**2
    steps = (
        f"Step-by-step solution (Quotient Rule):\n\n"
        f"1. Let u(x) = {num}, v(x) = {denom}\n"
        f"2. Compute u'({x}) = {num_derivative}, v'({x}) = {denom_derivative}\n"
        f"3. Apply the quotient rule:\n"
        f"   (u' * v - u * v') / v^2 = ({num_derivative} * {denom} - {num} * {denom_derivative}) / ({denom})^2\n"
        f"4. Simplify: {sp.simplify(result)}"
    )
    return sp.simplify(result), steps

def calculate():
    global total_chain_result
    mode = mode_var.get()
    steps_box.delete("1.0", tk.END)
    try:
        if mode == "Chain Rule":
            inner = inner_entry.get()
            outer = outer_entry.get()
            var = variable_entry.get()
            result, steps = chain_rule_calculator(inner, outer, var)
            total_chain_result = total_chain_result + result if total_chain_result else result
            output_var.set(str(sp.simplify(total_chain_result)))
            steps_box.insert(tk.END, steps)
        elif mode == "Quotient Rule":
            numerator = inner_entry.get()
            denominator = outer_entry.get()
            var = variable_entry.get()
            result, steps = quotient_rule_calculator(numerator, denominator, var)
            output_var.set(str(result))
            steps_box.insert(tk.END, steps)
            total_chain_result = None
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_more():
    if mode_var.get() != "Chain Rule":
        messagebox.showinfo("Not Supported", "Add Equation is only for Chain Rule mode.")
        return
    current_result = output_var.get().strip()
    print(f"DEBUG: Current Result = {current_result}")  # Debugging line
    if not current_result:
        messagebox.showinfo("Error", "No result available. Please calculate first.")
        return
    label_text = f"Base Result: {current_result}" if not result_boxes else f"Combined Result: {current_result}"
    add_result_to_history(label_text)
    inner_entry.delete(0, tk.END)
    outer_entry.delete(0, tk.END)
    steps_box.delete("1.0", tk.END)

def add_result_to_history(label_text):
    print(f"DEBUG: Adding to history: {label_text}")
    result_label = ttk.Entry(history_frame, width=54)
    result_label.insert(0, label_text)
    result_label.config(state="readonly")
    result_label.grid(column=0, row=len(result_boxes), padx=5, pady=2)
    result_boxes.append(result_label)
    print(f"DEBUG: Total results in history: {len(result_boxes)}")

def reset_fields():
    global total_chain_result, result_boxes
    inner_entry.delete(0, tk.END)
    outer_entry.delete(0, tk.END)
    variable_entry.delete(0, tk.END)
    output_var.set("")
    steps_box.delete("1.0", tk.END)
    total_chain_result = None
    for box in result_boxes:
        box.destroy()
    result_boxes.clear()

def update_fields(*args):
    reset_fields()
    mode = mode_var.get()
    label1.config(text="Inner Function (e.g., 2*x+5)" if mode == "Chain Rule" else "Numerator")
    label2.config(text="Outer Function (e.g., u^2)" if mode == "Chain Rule" else "Denominator")

def set_focused_entry(event):
    global focused_entry
    focused_entry = event.widget

def insert_to_focused_entry(value):
    if focused_entry:
        focused_entry.insert(tk.END, value)

def clear_focused_entry():
    if focused_entry:
        focused_entry.delete(0, tk.END)

def backspace_focused_entry():
    if focused_entry:
        current = focused_entry.get()
        focused_entry.delete(0, tk.END)
        focused_entry.insert(0, current[:-1])

root = tk.Tk()
root.title("Derivative Calculator - Chain & Quotient Rule")
root.configure(bg="#1e1e2f")
root.resizable(True, True)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 1366  
window_height = 850  

position_x = (screen_width - window_width) // 2
position_y = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

style = ttk.Style()
style.theme_use('default')
style.configure("TLabel", font=("Arial", 13), background="#1e1e2f", foreground="white")
style.configure("TEntry", font=("Arial", 14), padding=5)
style.configure("TButton", font=("Arial", 12), padding=5)
style.configure("TCombobox", font=("Arial", 12))
style.configure("TLabelframe", background="#1e1e2f", foreground="white")
style.configure("TLabelframe.Label", background="#1e1e2f", foreground="white")
style.configure("TFrame", background="#1e1e2f")

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

top_frame = ttk.Frame(root, style="TFrame")
top_frame.grid(column=0, row=0, columnspan=2, padx=10, pady=10, sticky="ew")

title_label = ttk.Label(
    top_frame,
    text="DERIVATIVE CALCULATOR - CHAIN AND QUOTIENT RULE",
    font=("Arial", 16, "bold"),
    background="#1e1e2f",
    foreground="white",
    anchor="center"
)
title_label.pack(fill="x", padx=10, pady=(10, 5))

instruction_frame = ttk.LabelFrame(top_frame, text="Instructions", padding=10, style="TLabelframe")
instruction_frame.pack(fill="x", padx=10, pady=5)

instruction_text = (
    "1. Select the mode: Chain Rule or Quotient Rule.\n"
    "2. Fill in the required functions and variable (e.g., x).\n"
    "   - Chain Rule: use 'u' for outer function (e.g., sin(u), u^2, etc.)\n"
    "   - Quotient Rule: specify numerator and denominator.\n"
    "3. Click 'Calculate' to compute the derivative.\n\n"
    "Limitations:\n"
    "- Use '*' for multiplication (2*x not 2x).\n"
    "- Use '^' or '**' for powers.\n"
    "- Supported functions: sin, cos, tan, log, exp, sqrt.\n"
    "- Only basic single-variable functions are supported."
)
instruction_label = ttk.Label(instruction_frame, text=instruction_text, justify="left", style="TLabel", anchor="w")
instruction_label.pack(fill="x", padx=10, pady=5)

mode_var = tk.StringVar(value="Chain Rule")
output_var = tk.StringVar()

# Left Section: Calculator
left_frame = ttk.Frame(root, style="TFrame")
left_frame.grid(column=0, row=1, padx=10, pady=15, sticky="nsew")

ttk.Label(left_frame, text="Select Mode:").grid(column=0, row=0, padx=10, pady=5, sticky="w")
mode_menu = ttk.Combobox(left_frame, textvariable=mode_var, values=["Chain Rule", "Quotient Rule"], state="readonly", width=20)
mode_menu.grid(column=1, row=0, padx=10, pady=5, sticky="w")
mode_menu.configure(font=("Arial", 13)) 
mode_menu.bind("<<ComboboxSelected>>", update_fields)

label1 = ttk.Label(left_frame, text="Inner Function:")
label1.grid(column=0, row=1, padx=10, pady=5, sticky="w")
inner_entry = ttk.Entry(left_frame, width=40)
inner_entry.grid(column=1, row=1, padx=10, pady=5, sticky="w")

label2 = ttk.Label(left_frame, text="Outer Function:")
label2.grid(column=0, row=2, padx=10, pady=5, sticky="w")
outer_entry = ttk.Entry(left_frame, width=40)
outer_entry.grid(column=1, row=2, padx=10, pady=5, sticky="w")

ttk.Label(left_frame, text="Variable (e.g., x):").grid(column=0, row=3, padx=10, pady=5, sticky="w")
variable_entry = ttk.Entry(left_frame, width=15)
variable_entry.grid(column=1, row=3, padx=10, pady=5, sticky="w")


inner_entry.bind("<FocusIn>", set_focused_entry)
outer_entry.bind("<FocusIn>", set_focused_entry)
variable_entry.bind("<FocusIn>", set_focused_entry)

button_frame = ttk.Frame(left_frame, style="TFrame")
button_frame.grid(column=0, row=4, columnspan=2, pady=10)
ttk.Button(button_frame, text="Calculate", command=calculate).grid(column=0, row=0, padx=5)
ttk.Button(button_frame, text="Reset", command=reset_fields).grid(column=1, row=0, padx=5)
ttk.Button(button_frame, text="Add Equation", command=add_more).grid(column=2, row=0, padx=5)

ttk.Label(left_frame, text="Current Result:").grid(column=0, row=5, padx=10, pady=5, sticky="w")
ttk.Entry(left_frame, textvariable=output_var, width=55).grid(column=1, row=5, padx=10, pady=5, sticky="w")

ttk.Label(left_frame, text="Previous Results:").grid(column=0, row=6, padx=10, pady=10, sticky="w")

history_frame = ttk.Frame(left_frame, style="TFrame")
history_frame.grid(column=1, row=6, padx=10, pady=10, sticky="w")
left_frame.rowconfigure(7, weight=1)
history_frame.columnconfigure(0, weight=1)

button_panel = ttk.LabelFrame(left_frame, text="Input Buttons", padding=10, style="TLabelframe")
button_panel.grid(column=0, row=8, columnspan=2, padx=10, pady=10)

buttons = [
    ['7', '8', '9', '+', '-', '(', ')'],
    ['4', '5', '6', '*', '/', '^', 'x'],
    ['1', '2', '3', 'u', 'sin', 'cos', 'exp'],
    ['0', '.', 'Clear', '←', 'log', 'tan', '^2']
]

for r, row in enumerate(buttons):
    for c, char in enumerate(row):
        action = lambda val=char: insert_to_focused_entry(val if val != '^2' else '**2')
        ttk.Button(button_panel, text=char, width=9, command=action).grid(row=r, column=c, padx=2, pady=2)

for child in button_panel.winfo_children():
    if child['text'] == 'Clear':
        child.config(command=clear_focused_entry)
    elif child['text'] == '←':
        child.config(command=backspace_focused_entry)

# Right Section: Solution
right_frame = ttk.Frame(root, style="TFrame")
right_frame.grid(column=1, row=1, padx=10, pady=10, sticky="nsew")

ttk.Label(right_frame, text="Step-by-step Solution:").grid(column=0, row=0, padx=10, pady=(0, 5), sticky="nw")
steps_box = tk.Text(right_frame, width=55, bg="#282c34", fg="white", font=("Courier", 12))
steps_box.grid(column=0, row=1, padx=10, pady=5, sticky="nsew")


update_fields()
root.update()
left_frame.columnconfigure(1, weight=1)
right_frame.columnconfigure(0, weight=1)
right_frame.rowconfigure(1, weight=1)
root.mainloop()