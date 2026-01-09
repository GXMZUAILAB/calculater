import tkinter as tk
from tkinter import messagebox
import ast


class _SafeEval(ast.NodeVisitor):
    ALLOWED_NODES = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
        ast.UAdd, ast.USub, ast.Load, ast.Call, ast.Name, ast.Tuple,
    )

    def visit(self, node):
        if not isinstance(node, self.ALLOWED_NODES):
            raise ValueError(f"Disallowed expression: {type(node).__name__}")
        return super().visit(node)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.Mod):
            return left % right
        if isinstance(op, ast.Pow):
            return left ** right
        raise ValueError("Unsupported operator")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unsupported unary operator")

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")


def safe_eval(expr: str):
    expr = expr.strip()
    if not expr:
        raise ValueError("Empty expression")
    # Parse expression to AST and evaluate only allowed nodes
    node = ast.parse(expr, mode="eval")
    evaluator = _SafeEval()
    return evaluator.visit(node)


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title("图形化计算器")
        root.resizable(False, False)

        self.display_var = tk.StringVar()

        entry = tk.Entry(root, textvariable=self.display_var, font=("Segoe UI", 18), bd=4, relief=tk.RIDGE, justify='right')
        entry.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=6, pady=6)
        entry.focus_set()

        btn_text = [
            ('7','8','9','/'),
            ('4','5','6','*'),
            ('1','2','3','-'),
            ('0','.','=','+'),
        ]

        for r, row in enumerate(btn_text, start=1):
            for c, ch in enumerate(row):
                action = (lambda ch=ch: self.on_button(ch))
                b = tk.Button(root, text=ch, width=6, height=2, font=("Segoe UI", 14), command=action)
                b.grid(row=r, column=c, padx=4, pady=4)

        clear_btn = tk.Button(root, text='C', width=6, height=2, font=("Segoe UI", 14), command=self.clear)
        clear_btn.grid(row=5, column=0, padx=4, pady=4)
        back_btn = tk.Button(root, text='⌫', width=6, height=2, font=("Segoe UI", 14), command=self.backspace)
        back_btn.grid(row=5, column=1, padx=4, pady=4)
        paren_btn = tk.Button(root, text='()', width=6, height=2, font=("Segoe UI", 14), command=self.insert_parens)
        paren_btn.grid(row=5, column=2, padx=4, pady=4)
        neg_btn = tk.Button(root, text='+/-', width=6, height=2, font=("Segoe UI", 14), command=self.negate)
        neg_btn.grid(row=5, column=3, padx=4, pady=4)

        root.bind('<Return>', lambda e: self.on_button('='))
        root.bind('<KP_Enter>', lambda e: self.on_button('='))
        root.bind('<BackSpace>', lambda e: self.backspace())
        root.bind('<Escape>', lambda e: self.clear())
        root.bind('<Key>', self.on_key)

    def on_button(self, ch: str):
        if ch == '=':
            self.calculate()
            return
        cur = self.display_var.get()
        self.display_var.set(cur + ch)

    def on_key(self, event):
        allowed = '0123456789.+-*/()%'
        if event.char in allowed:
            cur = self.display_var.get()
            self.display_var.set(cur + event.char)

    def clear(self):
        self.display_var.set('')

    def backspace(self):
        cur = self.display_var.get()
        self.display_var.set(cur[:-1])

    def insert_parens(self):
        cur = self.display_var.get()
        # simple heuristic: insert '(' or ')'
        if cur.count('(') == cur.count(')'):
            self.display_var.set(cur + '(')
        else:
            self.display_var.set(cur + ')')

    def negate(self):
        cur = self.display_var.get()
        if not cur:
            self.display_var.set('-')
            return
        try:
            val = safe_eval(cur)
            self.display_var.set(str(-val))
        except Exception:
            # fallback: try to prepend/remove leading '-'
            if cur.startswith('-'):
                self.display_var.set(cur[1:])
            else:
                self.display_var.set('-' + cur)

    def calculate(self):
        expr = self.display_var.get()
        try:
            result = safe_eval(expr)
            # Normalize integer results to int
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.display_var.set(str(result))
        except Exception as e:
            messagebox.showerror("错误", f"无法计算表达式：{e}")


if __name__ == '__main__':
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
