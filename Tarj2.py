import time
from selenium import webdriver
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
 
# ───────────────────────────────
# LOGIN FIAP
# ───────────────────────────────
def abrir_navegador_fiap():
    log_ikarus("Iniciando login no portal FIAP")
    navegador = webdriver.Chrome()
    navegador.get("https://www.fiap.com.br")
    navegador.maximize_window()
    time.sleep(2)
 
    try:
        menu_right = navegador.find_element(By.CLASS_NAME, "menu-right-login")
        menu_right.click()
        time.sleep(2)
 
        abas = navegador.window_handles
        navegador.switch_to.window(abas[1])
 
        navegador.get("https://www2.fiap.com.br")
        navegador.find_element(By.ID, "usuario").send_keys("00000")  # Substituir
        navegador.find_element(By.ID, "senha").send_keys("00000")  # Substituir
        navegador.find_element(By.CLASS_NAME, "a-login-btn").click()
 
        print("✅ Ikarus: Login FIAP realizado com sucesso.")
        log_ikarus("Login no portal FIAP realizado com sucesso")
        time.sleep(30)
 
    except Exception as e:
        print(f"❌ Erro no login FIAP: {e}")
        log_ikarus(f"Erro ao realizar login na FIAP: {e}")
    finally:
        navegador.quit()
 
# ───────────────────────────────
# AUTOMATIZAÇÃO COMPRASNET
# ───────────────────────────────
 
def baixar_excel_comprasnet():
    log_ikarus("Iniciando exportação do ComprasNet")
    navegador = webdriver.Chrome()
    navegador.get("https://contratos.comprasnet.gov.br/transparencia/contratos#") 
    navegador.maximize_window()
 
    wait = WebDriverWait(navegador, 30)
 
    try:
        # Página 1
        botao_excel = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="datatable_button_stack"]/div/button[contains(@class,"buttons-excel")]')))
        botao_excel.click()
        print("✅ Ikarus: Exportado da página 1")
        log_ikarus("Exportado ComprasNet página 1")
        time.sleep(5)
 
        quantidade_paginas = 5
        for i in range(3, 3 + (quantidade_paginas - 1)):
            xpath_pagina = f'//*[@id="crudTable_paginate"]/ul/li[{i}]/a'
            botao_pagina = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_pagina)))
            botao_pagina.click()
            print(f"🔄 Ikarus: Indo para a página {i - 1}")
            log_ikarus(f"Navegando para página {i - 1} no ComprasNet")
 
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="crudTable"]/tbody/tr')))
            time.sleep(2)
 
            botao_excel = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="datatable_button_stack"]/div/button[contains(@class,"buttons-excel")]')))
            botao_excel.click()
            print(f"✅ Ikarus: Exportado da página {i - 1}")
            log_ikarus(f"Exportado ComprasNet página {i - 1}")
            time.sleep(5)
 
        print("🏁 Ikarus: Exportação completa!")
        log_ikarus("Exportação do ComprasNet finalizada com sucesso")
    except Exception as e:
        print(f"❌ Erro durante exportação: {e}")
        log_ikarus(f"Erro na exportação do ComprasNet: {e}")
    finally:
        navegador.quit() 
# ───────────────────────────────
# INTERFACE COM TKINTER
# ───────────────────────────────
def iniciar_interface():
    janela = Tk()
    janela.title("Ikarus - Assistente Digital")
    janela.geometry("400x350")
    janela.configure(bg="#0c6dcf")  # Fundo azul claro
 
    estilo = ttk.Style()
    estilo.configure("Custom.TButton",
                     font=("Arial", 11),
                     foreground="white",
                     background="#0074c1",
                     padding=6)
    estilo.map("Custom.TButton",
               background=[("active", "#f7931e")])
 
    Label(janela, text="🦅 Bem-vindo ao Ikarus", font=("Arial", 16)).pack(pady=10)
 
    Button(janela, text="🔐 Login Portal FIAP", width=30, command=abrir_navegador_fiap).pack(pady=8)
    Button(janela, text="📥 Baixar Excel ComprasNet", width=30, command=baixar_excel_comprasnet).pack(pady=8)
    Button(janela, text="🔔 Verificar Novas Publicações", width=30, command=verificar_novas_publicacoes).pack(pady=8)
    Button(janela, text="📂 Ver Histórico de Ações", width=30, command=ver_historico).pack(pady=8)
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
 
 
def verificar_novas_publicacoes():
    url = "https://clic.prefeitura.sp.gov.br/destaques"
    arquivo_historico = "historico_noticias.json"
 
    # Carrega o histórico de notícias já notificadas
    if os.path.exists(arquivo_historico):
        with open(arquivo_historico, "r", encoding="utf-8") as f:
            noticias_antigas = json.load(f)
    else:
        noticias_antigas = []
 
    # Inicia o navegador
    navegador = webdriver.Chrome()
    navegador.get(url)
    time.sleep(5)  # Aguarda o carregamento da página
 
    # Extrai os títulos das notícias
    elementos_noticias = navegador.find_elements(By.CLASS_NAME, "news-title")  # Ajuste conforme a estrutura real
    noticias_atuais = [elemento.text for elemento in elementos_noticias]
 
    # Identifica novas notícias
    novas_noticias = [noticia for noticia in noticias_atuais if noticia not in noticias_antigas]
 
    # Atualiza o histórico
    if novas_noticias:
        with open(arquivo_historico, "w", encoding="utf-8") as f:
            json.dump(noticias_atuais, f, indent=4, ensure_ascii=False)
 
        # Exibe notificações
        for noticia in novas_noticias:
            messagebox.showinfo("Nova Publicação no CLIC", f"Nova notícia: {noticia}")
 
    navegador.quit()
 
 
# ───────────────────────────────
# EXECUÇÃO
# ───────────────────────────────
if __name__ == "__main__":
    iniciar_interface()