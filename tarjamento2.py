import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label, Button, Checkbutton, IntVar
import fitz  # PyMuPDF
import re
from docx import Document

from PIL import Image, ImageTk

# 1. Dicionário de padrões
padroes = {
    "CPF": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
    "Data": r"\d{2}/\d{2}/\d{4}",
    # Adicione mais se quiser
}

# 2. Selecionar quais tipos de dados serão buscados
def selecionar_padroes():
    padroes_escolhidos = {}

    def confirmar():
        for chave, var in check_vars.items():
            if var.get():
                padroes_escolhidos[chave] = padroes[chave]
        janela.destroy()

    janela = Toplevel()
    janela.title("Selecionar Dados a Tarjar")
    Label(janela, text="Escolha os tipos de dados a tarjar:").pack(pady=10)

    check_vars = {}
    for chave in padroes:
        var = IntVar(value=1)
        chk = Checkbutton(janela, text=chave, variable=var)
        chk.pack(anchor="w")
        check_vars[chave] = var

    Button(janela, text="Confirmar", command=confirmar).pack(pady=10)
    janela.wait_window()

    return padroes_escolhidos

# 3. Criar botão reutilizável
def criar_botao(texto, comando):
    return tk.Button(root, text=texto, command=comando, width=30, bg="#4a90e2", fg="white", font=("Arial", 10, "bold"))

# 4. Função principal: abrir PDF e exibir opções de tarjamento por ocorrência
def tarjar_pdf_seletivo():
    caminho = filedialog.askopenfilename(title="Selecione um PDF", filetypes=[("PDF", "*.pdf")])
    if not caminho:
        return

    try:
        doc = fitz.open(caminho)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir o PDF:\n{e}")
        return

    if doc.page_count == 0:
        messagebox.showwarning("PDF Vazio", "O PDF não tem páginas.")
        doc.close()
        return

    padroes_escolhidos = selecionar_padroes()
    if not padroes_escolhidos:
        messagebox.showinfo("Cancelado", "Nenhum padrão selecionado.")
        doc.close()
        return

    ocorrencias = []  

    
    for page_num, page in enumerate(doc):
        texto = page.get_text()
        for tipo, padrao in padroes_escolhidos.items():
            for match in re.finditer(padrao, texto, re.IGNORECASE):
                encontrado = match.group()
                areas = page.search_for(encontrado)
                for area in areas:
                    var = IntVar(value=1)
                    ocorrencias.append((page_num, encontrado, area, var))

    if not ocorrencias:
        messagebox.showinfo("Nada Encontrado", "Nenhum dado sensível encontrado.")
        doc.close()
        return

    # 5. Interface para o usuário escolher o que quer tarjar
    def aplicar_tarjas():
        for page_num, texto, area, var in ocorrencias:
            if var.get():
                page = doc[page_num]
                page.draw_rect(area, color=(0, 0, 0), fill=(0, 0, 0))

        novo_nome = caminho.replace(".pdf", "_TARJADO.pdf")
        doc.save(novo_nome)
        messagebox.showinfo("Sucesso", f"PDF salvo como:\n{novo_nome}")
        doc.close()
        janela.destroy()

    janela = Toplevel()
    janela.title("Escolha o que deseja tarjar")

    for i, (page_num, texto, area, var) in enumerate(ocorrencias):
        Checkbutton(
            janela,
            text=f"Página {page_num + 1}: {texto}",
            variable=var,
            anchor="w",
            width=60,
            justify="left"
        ).pack(anchor="w")

    Button(janela, text="Aplicar Tarjas", command=aplicar_tarjas, bg="black", fg="white").pack(pady=10)
    Button(janela, text="Cancelar", command=lambda: (doc.close(), janela.destroy())).pack()

# 6. Janela principal
root = tk.Tk()
root.title("Tarjador Seletivo de PDF")

criar_botao("🔐 Tarjar PDF (Seleção Manual)", tarjar_pdf_seletivo).pack(pady=10)

root.mainloop()

