"""
Mundo peças - Sistema Gerenciador de Mecânica Automotiva (versão didática)
Requisitos atendidos (resumo):
- GUI em Tkinter com 12 telas/janelas distintas
- Login e diferenciação de usuários: cliente x administrador
- Cadastro de usuários (com foto path), peças e ferramentas
- Integração com banco SQLite (cria DB e insere 6 cadastros de exemplo)
- Dashboard com algumas sugestões simples (indicador financeiro básico)
- Todas as telas podem exibir imagens (use placeholder/logo)
- Nome da oficina: "Auto Repair"
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sqlite3
import os
import datetime

DB_NAME = "Mundo_peças.db"
LOGO_PATH = "logo.png"  # colocar logo da mecânica aqui (ou deixar placeholder)

# ---------- Banco de Dados ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabelas: usuarios, peças, ferramentas, serviços, pedidos
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            fullname TEXT,
            email TEXT,
            phone TEXT,
            role TEXT, -- 'admin' ou 'client'
            photo TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS peças(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            sku TEXT UNIQUE,
            qty INTEGER,
            price REAL,
            description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS ferramentas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            code TEXT UNIQUE,
            available INTEGER,
            description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS serviços(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            description TEXT,
            price REAL,
            date TEXT,
            status TEXT,
            FOREIGN KEY(client_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS pedidos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER,
            total REAL,
            date TEXT,
            paid INTEGER,
            FOREIGN KEY(service_id) REFERENCES services(id)
        )
    ''')

    # Inserir dados de exemplo mínimos (6 cadastros)
    try:
        c.execute("INSERT INTO users(username,password,fullname,email,phone,role,photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("admin", "admin123", "Administrador chefe", "admin@autorepair.com", "1198765432", "admin", ""))
    except sqlite3.IntegrityError:
        pass
    try:
        c.execute("INSERT INTO users(username,password,fullname,email,phone,role,photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("cliente1", "cli123", "João Silva", "enzo@mail.com", "11988880000", "client", ""))
    except sqlite3.IntegrityError:
        pass
    try:
        c.execute("INSERT INTO users(username,password,fullname,email,phone,role,photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("cliente2", "cli123", "Guilherme Gomes", "guilherme@mail.com", "11977770000", "client", ""))
    except sqlite3.IntegrityError:
        pass
    try:
        c.execute("INSERT INTO users(username,password,fullname,email,phone,role,photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  ("cliente3", "cli123", "Igor Souza", "igor@mail.com", "11966660000", "client", ""))
    except sqlite3.IntegrityError:
        pass
    # mais 4 cadastros (peças/ferramentas)
    try:
        c.execute("INSERT INTO parts(name,sku,qty,price,description) VALUES (?, ?, ?, ?, ?)",
                  ("Filtro de Óleo", "P-OIL-001", 20, 35.0, "Filtro padrão para motores 1.6/2.0"))
    except sqlite3.IntegrityError:
        pass
    try:
        c.execute("INSERT INTO parts(name,sku,qty,price,description) VALUES (?, ?, ?, ?, ?)",
                  ("Pastilha de Freio", "P-BRK-002", 50, 80.0, "Pastilha dianteira"))
    except sqlite3.IntegrityError:
        pass
    try:
        c.execute("INSERT INTO tools(name,code,available,description) VALUES (?, ?, ?, ?)",
                  ("Macaco Hidráulico", "T-JCK-001", 1, "Capacidade 2 toneladas"))
    except sqlite3.IntegrityError:
        pass
    try:
        c.execute("INSERT INTO tools(name,code,available,description) VALUES (?, ?, ?, ?)",
                  ("Chave de Roda", "T-WLK-002", 5, "Padrão 17mm"))
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()

# ---------- Utilitários ----------
def format_currency(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ---------- App UI ----------
class MundopeçasApp:
    def __init__(self, root):
        self.root = root
        root.title("Mundo peças - Sistema Gerenciador de Mecânica")
        root.geometry("1440x900")
        root.resizable(False, False)
        self.conn = sqlite3.connect(DB_NAME)
        self.user = None  # usuário logado (dict)
        self.logo_img = None

        # Cria todas as telas (12) como métodos que constroem janelas Toplevel quando chamados.
        # Tela principal: Welcome -> Login
        self.build_welcome_screen()

    # --- helpers para imagens (logo/placeholder) ---
    def load_logo(self, w=200, h=100):
        if os.path.exists(LOGO_PATH):
            try:
                img = Image.open(LOGO_PATH)
            except Exception:
                img = Image.new("RGB", (w,h), (180,180,180))
        else:
            img = Image.new("RGB", (w,h), (180,180,180))
        img = img.resize((w,h))
        self.logo_img = ImageTk.PhotoImage(img)
        return self.logo_img

    # 1) Tela de Boas-vindas (Welcome)
    def build_welcome_screen(self):
        self.clear_root()
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        logo = self.load_logo(360,150)
        lbl_logo = ttk.Label(frame, image=logo)
        lbl_logo.image = logo
        lbl_logo.pack(pady=10)

        title = ttk.Label(frame, text="Bem-vindo ao Auto Repair", font=("Segoe UI", 20))
        title.pack(pady=8)

        desc = ttk.Label(frame, text="Sistema simplificado de gestão para mecânica automotiva.", wraplength=700)
        desc.pack(pady=6)

        btn_login = ttk.Button(frame, text="Entrar (Login)", command=self.build_login_screen)
        btn_login.pack(pady=8)
        btn_register = ttk.Button(frame, text="Registrar Cliente", command=self.build_register_screen)
        btn_register.pack(pady=4)

        # quick sample buttons to open other windows (for demo/navigation)
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(pady=12)
        ttk.Button(nav_frame, text="Dashboard", command=self.build_dashboard).grid(row=0, column=0, padx=6)
        ttk.Button(nav_frame, text="Cadastrar Peças", command=self.build_parts_screen).grid(row=0, column=1, padx=6)
        ttk.Button(nav_frame, text="Cadastrar Ferramentas", command=self.build_tools_screen).grid(row=0, column=2, padx=6)
        ttk.Button(nav_frame, text="Serviços", command=self.build_services_screen).grid(row=0, column=3, padx=6)

        footer = ttk.Label(frame, text="Auto Repair • Simulação educacional • Dados fictícios", font=("Segoe UI", 8))
        footer.pack(side=tk.BOTTOM, pady=8)

    # 2) Tela de Login
    def build_login_screen(self):
        self.clear_root()
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Login", font=("Segoe UI", 16)).pack(pady=6)

        form = ttk.Frame(frame)
        form.pack(pady=8)
        ttk.Label(form, text="Usuário:").grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
        user_entry = ttk.Entry(form)
        user_entry.grid(row=0, column=1, pady=4)
        ttk.Label(form, text="Senha:").grid(row=1, column=0, sticky=tk.E, padx=4, pady=4)
        pass_entry = ttk.Entry(form, show="*")
        pass_entry.grid(row=1, column=1, pady=4)

        def attempt_login():
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            c = self.conn.cursor()
            c.execute("SELECT id,username,fullname,email,phone,role,photo FROM users WHERE username=? AND password=?",
                      (username, password))
            row = c.fetchone()
            if row:
                self.user = {
                    "id": row[0], "username": row[1], "fullname": row[2],
                    "email": row[3], "phone": row[4], "role": row[5], "photo": row[6]
                }
                messagebox.showinfo("Login", f"Bem-vindo, {self.user['fullname']} ({self.user['role']})")
                self.build_dashboard()
            else:
                messagebox.showerror("Login", "Usuário ou senha inválidos.")

        ttk.Button(frame, text="Entrar", command=attempt_login).pack(pady=6)
        ttk.Button(frame, text="Voltar", command=self.build_welcome_screen).pack()

    # 3) Tela de Registro de Cliente
    def build_register_screen(self):
        self.clear_root()
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Registrar Novo Cliente", font=("Segoe UI", 16)).pack(pady=6)
        form = ttk.Frame(frame)
        form.pack(pady=8)

        labels = ["Usuário", "Senha", "Nome Completo", "Email", "Telefone", "Caminho Foto"]
        entries = []
        for i, lab in enumerate(labels):
            ttk.Label(form, text=lab + ":").grid(row=i, column=0, sticky=tk.E, padx=4, pady=4)
            e = ttk.Entry(form, width=40)
            e.grid(row=i, column=1, pady=4)
            entries.append(e)

        def browse_photo():
            path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.gif"), ("Todos", "*.*")])
            if path:
                entries[5].delete(0, tk.END)
                entries[5].insert(0, path)

        ttk.Button(form, text="Procurar Foto", command=browse_photo).grid(row=5, column=2, padx=6)

        def register_client():
            vals = [e.get().strip() for e in entries]
            if not all(vals[:5]):
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios.")
                return
            try:
                c = self.conn.cursor()
                c.execute("INSERT INTO users(username,password,fullname,email,phone,role,photo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (vals[0], vals[1], vals[2], vals[3], vals[4], "client", vals[5]))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Cliente registrado com sucesso.")
                self.build_login_screen()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Usuário já existe.")

        ttk.Button(frame, text="Registrar", command=register_client).pack(pady=8)
        ttk.Button(frame, text="Voltar", command=self.build_welcome_screen).pack()

    # 4) Dashboard (após login)
    def build_dashboard(self):
        self.clear_root()
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(frame)
        top.pack(fill=tk.X)
        logo = self.load_logo(160,70)
        l = ttk.Label(top, image=logo)
        l.image = logo
        l.pack(side=tk.LEFT, padx=6)
        user_str = f"Convidado" if not self.user else f"{self.user['fullname']} ({self.user['role']})"
        ttk.Label(top, text=f"Auto Repair — Dashboard\nUsuário: {user_str}", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=6)

        # quick stats
        stats = ttk.Frame(frame)
        stats.pack(pady=10)
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM parts")
        parts_n = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM tools")
        tools_n = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users")
        users_n = c.fetchone()[0]
        ttk.Label(stats, text=f"Peças cadastradas: {parts_n}", font=("Segoe UI", 10)).grid(row=0, column=0, padx=8)
        ttk.Label(stats, text=f"Ferramentas cadastradas: {tools_n}", font=("Segoe UI", 10)).grid(row=0, column=1, padx=8)
        ttk.Label(stats, text=f"Usuários cadastrados: {users_n}", font=("Segoe UI", 10)).grid(row=0, column=2, padx=8)

        # simple financial suggestion: if many parts stock low -> suggest reorder
        c.execute("SELECT name, qty FROM parts ORDER BY qty ASC LIMIT 5")
        low = c.fetchall()
        sugg_frame = ttk.LabelFrame(frame, text="Sugestões e Alertas")
        sugg_frame.pack(fill=tk.X, padx=6, pady=8)
        if low:
            lines = []
            for name, qty in low:
                if qty <= 5:
                    lines.append(f"Repor peça '{name}' (estoque: {qty})")
            if lines:
                ttk.Label(sugg_frame, text="\n".join(lines)).pack(padx=6, pady=6)
            else:
                ttk.Label(sugg_frame, text="Estoque saudável no momento.").pack(padx=6, pady=6)
        else:
            ttk.Label(sugg_frame, text="Sem peças cadastradas.").pack(padx=6, pady=6)

        # Navigation grid to other windows (total windows = 12 across app)
        nav = ttk.Frame(frame)
        nav.pack(pady=10)
        ttk.Button(nav, text="1. Cadastro de Peças", width=20, command=self.build_parts_screen).grid(row=0, column=0, padx=6, pady=4)
        ttk.Button(nav, text="2. Cadastro de Ferramentas", width=20, command=self.build_tools_screen).grid(row=0, column=1, padx=6, pady=4)
        ttk.Button(nav, text="3. Cadastro de Usuários", width=20, command=self.build_user_management).grid(row=0, column=2, padx=6, pady=4)
        ttk.Button(nav, text="4. Serviços (Ordens)", width=20, command=self.build_services_screen).grid(row=1, column=0, padx=6, pady=4)
        ttk.Button(nav, text="5. Faturamento", width=20, command=self.build_invoices_screen).grid(row=1, column=1, padx=6, pady=4)
        ttk.Button(nav, text="6. Relatórios", width=20, command=self.build_reports_screen).grid(row=1, column=2, padx=6, pady=4)
        ttk.Button(nav, text="7. Fluxograma (visual)", width=20, command=self.build_flowchart_screen).grid(row=2, column=0, padx=6, pady=4)
        ttk.Button(nav, text="8. Wireframe (projeto)", width=20, command=self.build_wireframe_screen).grid(row=2, column=1, padx=6, pady=4)
        ttk.Button(nav, text="9. Sobre / Contato", width=20, command=self.build_about_screen).grid(row=2, column=2, padx=6, pady=4)
        ttk.Button(nav, text="10. Configurações", width=20, command=self.build_settings_screen).grid(row=3, column=0, padx=6, pady=4)
        ttk.Button(nav, text="11. Tela de Ajuda", width=20, command=self.build_help_screen).grid(row=3, column=1, padx=6, pady=4)
        ttk.Button(nav, text="12. Sair", width=20, command=self.logout).grid(row=3, column=2, padx=6, pady=4)

    # 5) Tela de cadastro de peças
    def build_parts_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Cadastro de Peças - Auto Repair")
        win.geometry("700x500")
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(frame)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
        right = ttk.Frame(frame, width=260)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=6)

        tree = ttk.Treeview(left, columns=("sku","qty","price"), show="headings")
        tree.heading("sku", text="SKU")
        tree.heading("qty", text="Qtd")
        tree.heading("price", text="Preço")
        tree.pack(fill=tk.BOTH, expand=True)
        self.refresh_parts_tree(tree)

        # form in right
        ttk.Label(right, text="Adicionar / Atualizar Peça", font=("Segoe UI", 10)).pack(pady=6)
        f_entries = {}
        for label in ["Nome","SKU","Quantidade","Preço","Descrição"]:
            ttk.Label(right, text=label+":").pack(anchor=tk.W)
            e = ttk.Entry(right, width=30)
            e.pack(pady=2)
            f_entries[label.lower()] = e

        def add_part():
            try:
                name = f_entries["nome"].get().strip()
                sku = f_entries["sku"].get().strip()
                qty = int(f_entries["quantidade"].get())
                price = float(f_entries["preço"].get().replace(",", "."))
                desc = f_entries["descrição"].get().strip()
                if not name or not sku:
                    raise ValueError("Nome e SKU obrigatórios.")
                c = self.conn.cursor()
                c.execute("INSERT INTO parts(name,sku,qty,price,description) VALUES (?, ?, ?, ?, ?)",
                          (name, sku, qty, price, desc))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Peça adicionada.")
                self.refresh_parts_tree(tree)
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(right, text="Adicionar Peça", command=add_part).pack(pady=6)
        ttk.Button(right, text="Fechar", command=win.destroy).pack(pady=4)

    def refresh_parts_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        c.execute("SELECT name,sku,qty,price FROM parts")
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[1], row[2], format_currency(row[3])) , text=row[0])

    # 6) Tela de cadastro de ferramentas
    def build_tools_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Cadastro de Ferramentas - Auto Repair")
        win.geometry("700x450")
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame, columns=("code","available"), show="headings")
        tree.heading("code", text="Código")
        tree.heading("available", text="Disponível")
        tree.pack(fill=tk.BOTH, expand=True)

        # form
        form = ttk.Frame(win)
        form.pack(pady=6)
        ttk.Label(form, text="Nome").grid(row=0,column=0,padx=4,pady=4)
        name_e = ttk.Entry(form); name_e.grid(row=0,column=1)
        ttk.Label(form, text="Código").grid(row=1,column=0,padx=4,pady=4)
        code_e = ttk.Entry(form); code_e.grid(row=1,column=1)
        ttk.Label(form, text="Quantidade").grid(row=2,column=0,padx=4,pady=4)
        qty_e = ttk.Entry(form); qty_e.grid(row=2,column=1)

        def add_tool():
            try:
                name = name_e.get().strip()
                code = code_e.get().strip()
                qty = int(qty_e.get())
                if not name or not code:
                    raise ValueError("Nome e código obrigatórios.")
                c = self.conn.cursor()
                c.execute("INSERT INTO tools(name,code,available,description) VALUES (?, ?, ?, ?)",
                          (name, code, qty, ""))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Ferramenta adicionada.")
                self.refresh_tools_tree(tree)
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(form, text="Adicionar Ferramenta", command=add_tool).grid(row=3,column=0,columnspan=2,pady=6)
        ttk.Button(form, text="Fechar", command=win.destroy).grid(row=4,column=0,columnspan=2,pady=4)
        self.refresh_tools_tree(tree)

    def refresh_tools_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        c.execute("SELECT name,code,available FROM tools")
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[1], row[2]), text=row[0])

    # 7) Tela de Gerenciamento de Usuários (apenas para admin)
    def build_user_management(self):
        if not self.user or self.user["role"] != "admin":
            messagebox.showwarning("Acesso", "Apenas administradores podem acessar o gerenciamento de usuários.")
            return
        win = tk.Toplevel(self.root)
        win.title("Gerenciamento de Usuários - Auto Repair")
        win.geometry("700x450")
        frame = ttk.Frame(win, padding=10); frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame, columns=("email","phone","role"), show="headings")
        tree.heading("email", text="Email")
        tree.heading("phone", text="Telefone")
        tree.heading("role", text="Role")
        tree.pack(fill=tk.BOTH, expand=True)
        self.refresh_users_tree(tree)

        def remove_user():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Info", "Selecione um usuário.")
                return
            item = tree.item(sel[0])
            username = item["values"][0]
            if username == self.user["username"]:
                messagebox.showwarning("Aviso", "Você não pode remover a si mesmo.")
                return
            c = self.conn.cursor()
            c.execute("DELETE FROM users WHERE username=?", (username,))
            self.conn.commit()
            self.refresh_users_tree(tree)
            messagebox.showinfo("OK", "Usuário removido.")

        ttk.Button(win, text="Remover Usuário Selecionado", command=remove_user).pack(pady=6)
        ttk.Button(win, text="Fechar", command=win.destroy).pack()

    def refresh_users_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        c.execute("SELECT username,email,phone,role FROM users")
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3]))

    # 8) Tela de Serviços (ordens de serviço)
    def build_services_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Serviços - Ordens de Serviço")
        win.geometry("800x500")
        frame = ttk.Frame(win, padding=8); frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame, columns=("client","price","date","status"), show="headings")
        tree.heading("client", text="Cliente")
        tree.heading("price", text="Preço")
        tree.heading("date", text="Data")
        tree.heading("status", text="Status")
        tree.pack(fill=tk.BOTH, expand=True)
        self.refresh_services_tree(tree)

        form = ttk.Frame(win); form.pack(pady=6)
        ttk.Label(form, text="Cliente (username):").grid(row=0,column=0)
        client_e = ttk.Entry(form); client_e.grid(row=0,column=1)
        ttk.Label(form, text="Descrição:").grid(row=1,column=0)
        desc_e = ttk.Entry(form, width=50); desc_e.grid(row=1,column=1)
        ttk.Label(form, text="Preço:").grid(row=2,column=0)
        price_e = ttk.Entry(form); price_e.grid(row=2,column=1)

        def add_service():
            cl_user = client_e.get().strip()
            desc = desc_e.get().strip()
            try:
                price = float(price_e.get().replace(",","."))
            except:
                messagebox.showerror("Erro","Preço inválido.")
                return
            c = self.conn.cursor()
            c.execute("SELECT id FROM users WHERE username=?", (cl_user,))
            row = c.fetchone()
            if not row:
                messagebox.showerror("Erro","Cliente não encontrado.")
                return
            client_id = row[0]
            date = datetime.date.today().isoformat()
            c.execute("INSERT INTO services(client_id,description,price,date,status) VALUES (?, ?, ?, ?, ?)",
                      (client_id, desc, price, date, "Aberto"))
            self.conn.commit()
            messagebox.showinfo("OK","Serviço cadastrado.")
            self.refresh_services_tree(tree)

        ttk.Button(form, text="Adicionar Serviço", command=add_service).grid(row=3,column=0,columnspan=2,pady=6)
        ttk.Button(form, text="Fechar", command=win.destroy).grid(row=4,column=0,columnspan=2,pady=4)

    def refresh_services_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        c.execute('''
            SELECT s.id, u.username, s.price, s.date, s.status FROM services s
            LEFT JOIN users u ON s.client_id = u.id
            ORDER BY s.date DESC
        ''')
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[1], format_currency(row[2]), row[3], row[4]), text=str(row[0]))

    # 9) Tela de Faturamento / Invoices
    def build_invoices_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Faturamento - Auto Repair")
        win.geometry("700x450")
        frame = ttk.Frame(win, padding=8); frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame, columns=("service","total","date","paid"), show="headings")
        tree.heading("service", text="Serviço ID")
        tree.heading("total", text="Total")
        tree.heading("date", text="Data")
        tree.heading("paid", text="Pago")
        tree.pack(fill=tk.BOTH, expand=True)
        self.refresh_invoices_tree(tree)

        form = ttk.Frame(win); form.pack(pady=6)
        ttk.Label(form, text="Serviço ID:").grid(row=0,column=0)
        sid_e = ttk.Entry(form); sid_e.grid(row=0,column=1)
        ttk.Label(form, text="Total:").grid(row=1,column=0)
        tot_e = ttk.Entry(form); tot_e.grid(row=1,column=1)
        paid_var = tk.IntVar()
        ttk.Checkbutton(form, text="Pago", variable=paid_var).grid(row=2,column=0,columnspan=2)

        def add_invoice():
            try:
                sid = int(sid_e.get())
                total = float(tot_e.get().replace(",","."))
                paid = int(paid_var.get())
            except:
                messagebox.showerror("Erro","Valores inválidos.")
                return
            c = self.conn.cursor()
            c.execute("INSERT INTO invoices(service_id,total,date,paid) VALUES (?, ?, ?, ?)",
                      (sid, total, datetime.date.today().isoformat(), paid))
            self.conn.commit()
            messagebox.showinfo("OK","Fatura gerada.")
            self.refresh_invoices_tree(tree)

        ttk.Button(form, text="Gerar Fatura", command=add_invoice).grid(row=3,column=0,columnspan=2,pady=6)
        ttk.Button(form, text="Fechar", command=win.destroy).grid(row=4,column=0,columnspan=2,pady=4)

    def refresh_invoices_tree(self, tree):
        for r in tree.get_children():
            tree.delete(r)
        c = self.conn.cursor()
        c.execute("SELECT id, service_id, total, date, paid FROM invoices ORDER BY date DESC")
        for row in c.fetchall():
            tree.insert("", tk.END, values=(row[1], format_currency(row[2]), row[3], "Sim" if row[4] else "Não"))

    # 10) Relatórios (simples)
    def build_reports_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Relatórios - Auto Repair")
        win.geometry("600x400")
        frame = ttk.Frame(win, padding=10); frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Relatórios Rápidos", font=("Segoe UI", 12)).pack(pady=6)
        rpt = tk.Text(frame, height=18)
        rpt.pack(fill=tk.BOTH, expand=True)

        # Gerar relatório com dados resumo
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*), SUM(price) FROM services")
        services_cnt, services_sum = c.fetchone()
        services_sum = services_sum or 0.0
        c.execute("SELECT COUNT(*), SUM(total) FROM invoices")
        inv_cnt, inv_sum = c.fetchone()
        inv_sum = inv_sum or 0.0
        report_text = f"""
Relatório - Auto Repair
Data de geração: {datetime.datetime.now().isoformat()}
Total de serviços cadastrados: {services_cnt}
Receita potencial (soma preços serviços): {format_currency(services_sum)}

Total de faturas geradas: {inv_cnt}
Receita faturada: {format_currency(inv_sum)}

Observações:
- Verificar peças com estoque baixo no Dashboard.
- Conferir ferramentas emprestadas/indisponíveis.
"""
        rpt.insert("1.0", report_text)
        ttk.Button(frame, text="Fechar", command=win.destroy).pack(pady=6)

    # 11) Fluxograma (visual simplificado) - apenas uma tela com imagem/placeholder
    def build_flowchart_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Fluxograma - Processo (Exemplo)")
        win.geometry("800x600")
        frame = ttk.Frame(win, padding=8); frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Fluxograma do Processo (exemplo)", font=("Segoe UI", 12)).pack(pady=6)
        canvas = tk.Canvas(frame, bg="white", width=760, height=520)
        canvas.pack()
        # desenhar um fluxograma simples
        canvas.create_rectangle(50,30,320,90, fill="#e6f2ff")
        canvas.create_text(185,60, text="Entrada de Cliente / Agendamento")
        canvas.create_line(185,90,185,150, arrow=tk.LAST)
        canvas.create_rectangle(50,150,320,210, fill="#fff2cc")
        canvas.create_text(185,180, text="Diagnóstico / Análise do Veículo")
        canvas.create_line(185,210,185,270, arrow=tk.LAST)
        canvas.create_rectangle(50,270,320,330, fill="#e6ffe6")
        canvas.create_text(185,300, text="Execução do Serviço / Reparo")
        canvas.create_line(320,300,500,300, arrow=tk.LAST)
        canvas.create_rectangle(500,260,740,340, fill="#f3e6ff")
        canvas.create_text(620,300, text="Entrega / Faturamento / Pós-venda")

    # 12) Wireframe (tela de projeto) - placeholder
    def build_wireframe_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Wireframe - Protótipo")
        win.geometry("700x520")
        f = ttk.Frame(win, padding=8); f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text="Wireframe - Protótipo de Telas (Baixa/Alta Fidelidade)", font=("Segoe UI", 12)).pack(pady=6)
        # placeholder: list dos 12 janelas e breve descrição
        txt = tk.Text(f, height=22)
        entries = [
            "1. Welcome (Boas-vindas)",
            "2. Login",
            "3. Registro Cliente",
            "4. Dashboard",
            "5. Cadastro de Peças",
            "6. Cadastro de Ferramentas",
            "7. Gerenciamento de Usuários (admin)",
            "8. Serviços (Ordens)",
            "9. Faturamento",
            "10. Relatórios",
            "11. Fluxograma",
            "12. Wireframe / Protótipo"
        ]
        txt.insert("1.0", "Lista de Telas e Propósitos:\n\n" + "\n".join(entries))
        txt.pack(fill=tk.BOTH, expand=True)
        ttk.Button(f, text="Fechar", command=win.destroy).pack(pady=6)

    # --- telas auxiliares: About, Settings, Help ---
    def build_about_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Sobre / Contato - Auto Repair")
        win.geometry("500x360")
        f = ttk.Frame(win, padding=10); f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text="Auto Repair", font=("Segoe UI", 14)).pack(pady=6)
        ttk.Label(f, text="Sistema de gestão para mecânica automotiva\nDados fictícios - Projeto Escolar").pack(pady=6)
        ttk.Label(f, text="Contato: contato@autorepair.com\nTelefone: (11) 9876-5432").pack(pady=6)
        ttk.Label(f, text="Endereço: Rua Eusebio stevaux, 823 - Santo Amaro, São Paulo").pack(pady=6)
        ttk.Button(f, text="Fechar", command=win.destroy).pack(pady=8)

    def build_settings_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Configurações - Auto Repair")
        win.geometry("500x320")
        f = ttk.Frame(win, padding=10); f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text="Configurações Gerais").pack(pady=6)
        ttk.Label(f, text="Alterar logo (substituir arquivo logo.png):").pack(anchor=tk.W)
        def change_logo():
            p = filedialog.askopenfilename(filetypes=[("PNG/JPG", "*.png;*.jpg;*.jpeg")])
            if p:
                try:
                    # sobrescreve logo.png
                    ext = os.path.splitext(p)[1].lower()
                    newpath = LOGO_PATH
                    with open(p, "rb") as src, open(newpath, "wb") as dst:
                        dst.write(src.read())
                    messagebox.showinfo("OK", "Logo atualizada. Reinicie a aplicação para ver mudanças.")
                except Exception as e:
                    messagebox.showerror("Erro", str(e))
        ttk.Button(f, text="Selecionar nova logo", command=change_logo).pack(pady=6)
        ttk.Button(f, text="Fechar", command=win.destroy).pack(pady=8)

    def build_help_screen(self):
        win = tk.Toplevel(self.root)
        win.title("Ajuda - Auto Repair")
        win.geometry("600x420")
        f = ttk.Frame(win, padding=10); f.pack(fill=tk.BOTH, expand=True)
        help_txt = """
Manual Rápido:
- Faça login com usuário 'admin' / senha 'admin123' (admin de exemplo).
- Registre clientes via tela 'Registrar Cliente'.
- Cadastre peças e ferramentas no menu correspondente.
- Registre serviços (ordens) indicando username do cliente.
- Gere faturas para serviços.
- Apenas administradores podem remover usuários.

Dica:
- Substitua 'logo.png' pelo logo da sua startup.
- Exporte relatórios copiando o conteúdo da tela Relatórios.
"""
        ttk.Label(f, text=help_txt, justify=tk.LEFT).pack()
        ttk.Button(f, text="Fechar", command=win.destroy).pack(pady=6)

    def logout(self):
        self.user = None
        messagebox.showinfo("Logout", "Você saiu da sessão.")
        self.build_welcome_screen()

    # Limpa conteúdo da root para trocar telas (sem criar novas janelas)
    def clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

# ---------- execução ----------
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = MundopeçasApp(root)
    root.mainloop()


