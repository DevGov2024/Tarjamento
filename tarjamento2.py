import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label, Button, Checkbutton, IntVar
import re
from docx import Document

# 1. Dicionário de padrões
padroes = {
    "CPF": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
    "Data": r"\d{2}/\d{2}/\d{4}",
    # Pode adicionar outros
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

# 4. Função principal: abrir Word e exibir ocorrências para tarjamento seletivo
def tarjar_word_seletivo():
    caminho = filedialog.askopenfilename(title="Selecione um arquivo Word", filetypes=[("Word Files", "*.docx")])
    if not caminho:
        return

    try:
        doc = Document(caminho)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir o arquivo Word:\n{e}")
        return

    padroes_escolhidos = selecionar_padroes()
    if not padroes_escolhidos:
        messagebox.showinfo("Cancelado", "Nenhum padrão selecionado.")
        return

    ocorrencias = []  # Armazena (paragrafo_obj, texto_encontrado, var_checkbox)

    # Buscar todas as ocorrências no texto do documento
    for p in doc.paragraphs:
        texto = p.text
        for tipo, padrao in padroes_escolhidos.items():
            for match in re.finditer(padrao, texto):
                encontrado = match.group()
                var = IntVar(value=1)
                ocorrencias.append((p, encontrado, var))

    if not ocorrencias:
        messagebox.showinfo("Nada Encontrado", "Nenhum dado sensível encontrado.")
        return

    # Interface para o usuário selecionar quais tarjados aplicar
    def aplicar_tarjas():
        total = 0
        for p, texto_encontrado, var in ocorrencias:
            if var.get():
                # Substitui todas as ocorrências do texto_encontrado por [TARJADO] no parágrafo
                novo_texto = p.text.replace(texto_encontrado, "[TARJADO]")
                p.text = novo_texto
                total += 1

        if total == 0:
            messagebox.showinfo("Cancelado", "Nenhum dado selecionado para tarjar.")
            return

        novo_nome = caminho.replace(".docx", "_TARJADO.docx")
        doc.save(novo_nome)
        messagebox.showinfo("Sucesso", f"{total} dados tarjados.\nArquivo salvo como:\n{novo_nome}")
        janela.destroy()

    janela = Toplevel()
    janela.title("Escolha o que deseja tarjar")

    for p, texto_encontrado, var in ocorrencias:
        Checkbutton(
            janela,
            text=texto_encontrado,
            variable=var,
            anchor="w",
            width=60,
            justify="left"
        ).pack(anchor="w")

    Button(janela, text="Aplicar Tarjas", command=aplicar_tarjas, bg="black", fg="white").pack(pady=10)
    Button(janela, text="Cancelar", command=janela.destroy).pack()

# 5. Janela principal
root = tk.Tk()
root.title("Tarjador Seletivo de Word")

criar_botao("🔐 Tarjar Word (Seleção Manual)", tarjar_word_seletivo).pack(pady=10)

root.mainloop()

