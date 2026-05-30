import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re

KEYWORDS  = {"int", "float", "if", "else", "while", "print"}
OPERATORS = {"=", "+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">=", "&&", "||"}
DELIMITERS = {";", "(", ")", "{", "}", ","}

# 1. ÖNCE sınıf tanımı
class Token:
    def __init__(self, line, value, token_type):
        self.line       = line
        self.value      = value
        self.token_type = token_type

    def __repr__(self):
        return f"[{self.token_type}  '{self.value}'  satır:{self.line}]"

# 2. SONRA test
t = Token(1, "int", "INT")
print(t)