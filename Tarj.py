import fitz  
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import Tk, Button, Label
from datetime import datetime
from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, END
import pandas as pd
import os
from tkinter import Entry, StringVar, filedialog
from tkinter import Tk, Button, Label, ttk
from tkinter import simpledialog
from tkinter import messagebox

import json
config_path = "config_ikarus.json"
 
# ───────────────────────────────
# HISTÓRICO
# ───────────────────────────────
def log_ikarus(acao):
    with open("historico_ikarus.log", "a", encoding="utf-8") as log:
        log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {acao}\n")

def iniciar_interface():
    janela = Tk()
    janela.title("Águia - Assistente Digital")
    janela.geometry("400x350")
    janela.configure(bg="#3a88d6")  
 
    estilo = ttk.Style()
    estilo.configure("Custom.TButton",
                     font=("Segoe UI", 11, "bold"),
                     foreground="white",
                     background="#0074c1",
                     padding=6)
    estilo.map("Custom.TButton",
               background=[("active", "#f7931e")])
 
    janela.title("🦅 Águia - Assistente Digital")
    janela.geometry("400x350")
    janela.configure(bg="#2b547c")

   
    Label(janela, text="🦅 Bem-vindo ao Águia", font=("Arial", 16)).pack(pady=10)
 
   
    Button(janela, text="📂 Ver Histórico de Ações", width=30, command=ver_historico).pack(pady=8)
    Button(janela, text= "🔐 Tarjar Dados Sensíveis em PDF", width=30, command=tarjar_pdf).pack(pady=8)
    Button(janela, text="❌ Sair", width=30, command=janela.destroy).pack(pady=12)

 
    janela.mainloop()
 
def ver_historico():
    historico_janela = Toplevel()
    historico_janela.title("📂 Histórico de Ações do Ikarus")
    historico_janela.geometry("600x400")
    scrollbar = Scrollbar(historico_janela)
    scrollbar.pack(side=RIGHT, fill=Y)
    texto = Text(historico_janela, wrap="word", yscrollcommand=scrollbar.set)
    texto.pack(expand=True, fill="both")
 
    try:
        with open("historico_ikarus.log", "r", encoding="utf-8") as log_file:
            texto.insert(END, log_file.read())
    except FileNotFoundError:
        texto.insert(END, "⚠️ Nenhum histórico encontrado.")
 
    scrollbar.config(command=texto.yview)
  
      

def tarjar_pdf():
    caminho_arquivo = filedialog.askopenfilename(title="Selecione o PDF", filetypes=[("PDF Files", "*.pdf")])
    if not caminho_arquivo:
        return  

    padroes = {
        "CPF": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
        "Telefone": r"\(?\d{2}\)?\s?\d{4,5}-\d{4}",
        "Senha": r"senha:\s?\S+"
 
    }

    doc = fitz.open(caminho_arquivo)
    total_ocultados = 0
    usar_redaction = hasattr(doc, "apply_redactions")

    for page in doc:
        texto_pagina = page.get_text()
        for tipo, padrao in padroes.items():
            for ocorrencia in re.finditer(padrao, texto_pagina, re.IGNORECASE):
                texto_encontrado = ocorrencia.group()
                areas = page.search_for(texto_encontrado)
                for area in areas:
                    if usar_redaction:
                        page.add_redact_annot(area, fill=(0, 0, 0), text="000000")
                    else:
                        page.draw_rect(area, color=(0, 0, 0), fill=(0, 0, 0))
                    total_ocultados += 1

    if total_ocultados > 0:
        if usar_redaction:
            doc.apply_redactions()
        novo_nome = caminho_arquivo.replace(".pdf", "_TARJADO.pdf")
        doc.save(novo_nome)
        doc.close()
        messagebox.showinfo("Sucesso", f"{total_ocultados} dados sensíveis foram tarjados.\nArquivo salvo como:\n{novo_nome}")
        log_ikarus("Dados sensíveis tarjados com sucesso.")
    else:
        doc.close()
        messagebox.showinfo("Nada Encontrado", "Nenhum dado sensível encontrado para tarjar.")
        log_ikarus("Nenhum dado sensível encontrado para tarjar.")

  
if __name__ == "__main__":
    iniciar_interface()