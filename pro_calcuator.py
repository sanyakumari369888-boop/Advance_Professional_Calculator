import tkinter as tk
from tkinter import messagebox
import math
import ast
import operator
import sympy as sp

# ---------------- CONFIGURATION ----------------
BG = "#202a30"
DISPLAY_BG = "#111719"
BTN = "#34444e"
BLUE = "#1765b9"
ORANGE = "#ffad18"
RED = "#e54b3f"
TEXT = "#f3f5f6"

root = tk.Tk()
root.title("Professional Calculator")
root.geometry("900x850")
root.minsize(650, 650)
root.configure(bg=BG)

expression = tk.StringVar()
mode = tk.StringVar(value="DEG")
history = []
last_answer = 0

# ---------------- MATH FUNCTIONS ----------------
def angle_value(x):
    return math.radians(x) if mode.get() == "DEG" else x


def sin(x):
    return math.sin(angle_value(x))


def cos(x):
    return math.cos(angle_value(x))


def tan(x):
    return math.tan(angle_value(x))


def asin(x):
    result = math.asin(x)
    return math.degrees(result) if mode.get() == "DEG" else result


def acos(x):
    result = math.acos(x)
    return math.degrees(result) if mode.get() == "DEG" else result


def atan(x):
    result = math.atan(x)
    return math.degrees(result) if mode.get() == "DEG" else result


def factorial(x):
    if x < 0 or int(x) != x:
        raise ValueError(
            "Factorial requires a non-negative integer"
        )
    return math.factorial(int(x))


def percent(x):
    return x / 100


SAFE_FUNCTIONS = {
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "asin": asin,
    "acos": acos,
    "atan": atan,
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "abs": abs,
    "exp": math.exp,
    "factorial": factorial,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "degrees": math.degrees,
    "radians": math.radians,
    "pi": math.pi,
    "e": math.e,
    "ans": 0
}

# ---------------- SAFE EXPRESSION EVALUATOR ----------------
BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_eval(text):
    tree = ast.parse(text, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid value")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)

            if op_type not in BINARY_OPERATORS:
                raise ValueError("Unsupported operator")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if op_type is ast.Pow and abs(right) > 1000:
                raise ValueError("Exponent is too large")

            return BINARY_OPERATORS[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)

            if op_type not in UNARY_OPERATORS:
                raise ValueError("Unsupported operation")

            return UNARY_OPERATORS[op_type](
                evaluate(node.operand)
            )

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Invalid function")

            name = node.func.id

            if name not in SAFE_FUNCTIONS:
                raise ValueError(f"Unknown function: {name}")

            if node.keywords:
                raise ValueError(
                    "Keyword arguments are not allowed"
                )

            args = [evaluate(arg) for arg in node.args]

            if name in ("pi", "e", "ans"):
                raise ValueError("Invalid function call")

            return SAFE_FUNCTIONS[name](*args)

        if isinstance(node, ast.Name):
            if node.id not in SAFE_FUNCTIONS:
                raise ValueError(f"Unknown name: {node.id}")

            value = SAFE_FUNCTIONS[node.id]

            if callable(value):
                raise ValueError("Function needs parentheses")

            return value

        raise ValueError("Invalid expression")

    return evaluate(tree)


# ---------------- DISPLAY OPERATIONS ----------------
def insert(value):
    expression.set(expression.get() + str(value))


def clear():
    expression.set("")


def backspace():
    expression.set(expression.get()[:-1])


def calculate(event=None):
    global last_answer

    text = expression.get().strip()

    if not text:
        return

    try:
        SAFE_FUNCTIONS["ans"] = last_answer
        result = safe_eval(text)

        if isinstance(result, complex):
            output = str(result)
        elif isinstance(result, float):
            output = f"{result:.12g}"
        else:
            output = str(result)

        history.append(f"{text} = {output}")
        last_answer = result
        expression.set(output)

    except Exception as error:
        messagebox.showerror(
            "Calculation Error", str(error)
        )


def toggle_mode():
    mode.set("RAD" if mode.get() == "DEG" else "DEG")
    mode_button.config(text=mode.get())


def add_pi():
    insert("pi")


def add_e():
    insert("e")


def show_history():
    win = tk.Toplevel(root)
    win.title("Calculation History")
    win.geometry("500x400")
    win.configure(bg=BG)

    box = tk.Listbox(
        win,
        bg=DISPLAY_BG,
        fg=TEXT,
        font=("Consolas", 12),
        width=55
    )
    box.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    for item in reversed(history):
        box.insert(tk.END, item)

    def use_selected():
        selected = box.curselection()

        if selected:
            item = box.get(selected[0])
            expression.set(item.split(" = ")[-1])
            win.destroy()

    tk.Button(
        win,
        text="Use Selected Answer",
        command=use_selected,
        bg=BLUE,
        fg="white"
    ).pack(pady=8)


# ---------------- EQUATION SOLVER ----------------
def solve_equation():
    win = tk.Toplevel(root)
    win.title("Polynomial Equation Solver")
    win.geometry("600x480")
    win.configure(bg=BG)

    tk.Label(
        win,
        text="Enter an equation in x",
        bg=BG,
        fg=TEXT,
        font=("Arial", 16, "bold")
    ).pack(pady=12)

    tk.Label(
        win,
        text="Example: x**4 + 2*x - 3 = 0",
        bg=BG,
        fg="#c4d3db",
        font=("Arial", 11)
    ).pack()

    equation = tk.Entry(
        win,
        font=("Consolas", 16),
        width=35
    )
    equation.pack(pady=12)
    equation.insert(0, "x**4 + 2*x - 3 = 0")

    output = tk.Text(
        win,
        height=12,
        width=55,
        bg=DISPLAY_BG,
        fg=TEXT,
        font=("Consolas", 12)
    )
    output.pack(
        padx=12,
        pady=8,
        fill="both",
        expand=True
    )

    def solve():
        output.delete("1.0", tk.END)

        try:
            x = sp.Symbol("x")
            raw = equation.get().replace("^", "**")

            if "=" in raw:
                left, right = raw.split("=", 1)
                expr = sp.sympify(left) - sp.sympify(right)
            else:
                expr = sp.sympify(raw)

            if not expr.has(x):
                raise ValueError("Equation must contain x")

            solutions = sp.solve(expr, x)

            if not solutions:
                output.insert(
                    tk.END,
                    "No symbolic solutions found."
                )
            else:
                output.insert(
                    tk.END,
                    "Equation solutions:\n\n"
                )

                for index, answer in enumerate(solutions, 1):
                    output.insert(
                        tk.END,
                        f"x{index} = {sp.N(answer, 12)}\n"
                    )
                    output.insert(
                        tk.END,
                        f"Exact: {answer}\n\n"
                    )

        except Exception as error:
            output.insert(tk.END, f"Error: {error}")

    tk.Button(
        win,
        text="SOLVE EQUATION",
        command=solve,
        bg=ORANGE,
        fg="black",
        font=("Arial", 12, "bold")
    ).pack(pady=8)


# ---------------- TOP BAR ----------------
top = tk.Frame(root, bg=BG)
top.pack(fill="x", padx=10, pady=8)

tk.Label(
    top,
    text="PROFFESIONAL CALCULATOR",
    bg=BG,
    fg=TEXT,
    font=("Arial", 18, "bold")
).pack(side="left", padx=5)

mode_button = tk.Button(
    top,
    textvariable=mode,
    command=toggle_mode,
    bg=BTN,
    fg=TEXT,
    font=("Arial", 12, "bold"),
    width=7
)
mode_button.pack(side="right", padx=5)

tk.Button(
    top,
    text="HISTORY",
    command=show_history,
    bg=BTN,
    fg=TEXT,
    font=("Arial", 11)
).pack(side="right", padx=5)


# ---------------- DISPLAY ----------------
display = tk.Entry(
    root,
    textvariable=expression,
    font=("Consolas", 25),
    bg=DISPLAY_BG,
    fg=TEXT,
    insertbackground=TEXT,
    justify="right",
    relief="flat",
    bd=10
)
display.pack(
    fill="x",
    padx=12,
    pady=12,
    ipady=18
)

display.focus_set()
display.bind("<Return>", calculate)
display.bind("<KP_Enter>", calculate)
display.bind("<Escape>", lambda event: clear())
display.bind("<BackSpace>", lambda event: backspace())


# ---------------- BUTTON LAYOUT ----------------
buttons = [
    [
        ("(", "(", BTN),
        (")", ")", BTN),
        ("DEL", "DEL", RED),
        ("CLR", "CLR", RED),
        ("SOLVE", "SOLVE", ORANGE)
    ],
    [
        ("sin", "sin(", BTN),
        ("cos", "cos(", BTN),
        ("tan", "tan(", BTN),
        ("log", "log(", BTN),
        ("ln", "ln(", BTN)
    ],
    [
        ("sin-1", "asin(", BTN),
        ("cos-1", "acos(", BTN),
        ("tan-1", "atan(", BTN),
        ("sqrt", "sqrt(", BTN),
        ("x^2", "x^2", BTN)
    ],
    [
        ("x^3", "x^3", BTN),
        ("x^y", "**", BTN),
        ("1/x", "1/x", BTN),
        ("n!", "factorial(", BTN),
        ("%", "/100", BTN)
    ],
    [
        ("pi", "pi", BTN),
        ("e", "e", BTN),
        ("Ans", "ans", BTN),
        ("/", "/", BTN),
        ("*", "*", BTN)
    ],
    [
        ("7", "7", BTN),
        ("8", "8", BTN),
        ("9", "9", BTN),
        ("-", "-", BTN),
        ("+", "+", BTN)
    ],
    [
        ("4", "4", BTN),
        ("5", "5", BTN),
        ("6", "6", BTN),
        ("=", "=", BLUE),
        ("History", "HISTORY", BTN)
    ],
    [
        ("1", "1", BTN),
        ("2", "2", BTN),
        ("3", "3", BTN),
        ("0", "0", BTN),
        (".", ".", BTN)
    ],
    [
        ("sinh", "sinh(", BTN),
        ("cosh", "cosh(", BTN),
        ("tanh", "tanh(", BTN),
        ("abs", "abs(", BTN),
        ("DEG/RAD", "MODE", BTN)
    ],
]

grid = tk.Frame(root, bg=BG)
grid.pack(
    fill="both",
    expand=True,
    padx=8,
    pady=5
)

for r, row in enumerate(buttons):
    grid.grid_rowconfigure(r, weight=1)

    for c, (label, value, color) in enumerate(row):
        grid.grid_columnconfigure(c, weight=1)

        def make_command(v=value, lbl=label):
            def command():
                if lbl == "CLR":
                    clear()

                elif lbl == "DEL":
                    backspace()

                elif lbl == "=":
                    calculate()

                elif lbl == "SOLVE":
                    solve_equation()

                elif lbl == "HISTORY":
                    show_history()

                elif lbl == "DEG/RAD":
                    toggle_mode()

                elif lbl == "x^2":
                    insert("**2")

                elif lbl == "x^3":
                    insert("**3")

                elif lbl == "1/x":
                    insert("**(-1)")

                else:
                    insert(v)

            return command

        tk.Button(
            grid,
            text=label,
            command=make_command(),
            bg=color,
            fg="black" if color == ORANGE else TEXT,
            activebackground="#536875",
            activeforeground="white",
            font=("Arial", 13, "bold"),
            relief="raised",
            bd=2
        ).grid(
            row=r,
            column=c,
            sticky="nsew",
            padx=3,
            pady=3,
            ipadx=2,
            ipady=10
        )

root.mainloop()