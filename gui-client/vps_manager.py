#!/usr/bin/env python3
"""
VPS Manager - Interface gráfica para gerenciamento de servidores VPS via SSH
Requer: pip install paramiko
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import paramiko
import os
import time
import json
from pathlib import Path
from datetime import datetime


# ─────────────────────────────────────────────
# TEMA / CORES
# ─────────────────────────────────────────────
BG         = "#0d1117"
BG_CARD    = "#161b22"
BG_INPUT   = "#21262d"
BORDER     = "#30363d"
ACCENT     = "#58a6ff"
ACCENT2    = "#3fb950"
ACCENT3    = "#f78166"
ACCENT_YLW = "#e3b341"
TEXT       = "#e6edf3"
TEXT_DIM   = "#8b949e"
TEXT_DARK  = "#484f58"
FONT_MONO  = ("Courier New", 10)
FONT_UI    = ("Segoe UI", 10) if os.name == "nt" else ("SF Pro Display", 10)
FONT_UI_B  = ("Segoe UI", 10, "bold") if os.name == "nt" else ("SF Pro Display", 10, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold") if os.name == "nt" else ("SF Pro Display", 13, "bold")


# ─────────────────────────────────────────────
# HELPERS VISUAIS
# ─────────────────────────────────────────────
def styled_frame(parent, **kw):
    kw.setdefault("bg", BG_CARD)
    kw.setdefault("relief", "flat")
    return tk.Frame(parent, **kw)


def label(parent, text, color=TEXT, font=None, **kw):
    font = font or FONT_UI
    return tk.Label(parent, text=text, fg=color, bg=kw.pop("bg", BG_CARD),
                    font=font, **kw)


def entry(parent, textvariable=None, show=None, width=30, **kw):
    e = tk.Entry(parent, textvariable=textvariable, show=show,
                 bg=BG_INPUT, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", font=FONT_UI, width=width,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT, **kw)
    return e


def btn(parent, text, command, color=ACCENT, fg=BG, width=14, **kw):
    b = tk.Button(parent, text=text, command=command,
                  bg=color, fg=fg, activebackground=color,
                  activeforeground=fg, relief="flat", font=FONT_UI_B,
                  cursor="hand2", width=width, pady=6, **kw)
    b.bind("<Enter>", lambda e: b.config(bg=_lighten(color)))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b


def _lighten(hex_color):
    """Deixa a cor um pouco mais clara no hover."""
    hex_color = hex_color.lstrip("#")
    rgb = tuple(min(255, int(hex_color[i:i+2], 16) + 20) for i in (0, 2, 4))
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def sep(parent, **kw):
    return tk.Frame(parent, bg=BORDER, height=1, **kw)


# ─────────────────────────────────────────────
# STATUS BADGE
# ─────────────────────────────────────────────
class StatusBadge(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_CARD, **kw)
        self._dot  = tk.Label(self, text="●", font=("Courier New", 12),
                              bg=BG_CARD, fg=TEXT_DARK)
        self._text = tk.Label(self, text="Desconectado", font=FONT_UI,
                              bg=BG_CARD, fg=TEXT_DARK)
        self._dot.pack(side="left", padx=(0, 4))
        self._text.pack(side="left")

    def set(self, state):
        """state: 'disconnected' | 'connecting' | 'connected' | 'error'"""
        cfg = {
            "disconnected": (TEXT_DARK,  TEXT_DARK,  "Desconectado"),
            "connecting":   (ACCENT_YLW, ACCENT_YLW, "Conectando…"),
            "connected":    (ACCENT2,    ACCENT2,    "Conectado"),
            "error":        (ACCENT3,    ACCENT3,    "Erro de conexão"),
        }
        dot_c, txt_c, txt = cfg.get(state, cfg["disconnected"])
        self._dot.config(fg=dot_c)
        self._text.config(fg=txt_c, text=txt)


# ─────────────────────────────────────────────
# LOG WIDGET
# ─────────────────────────────────────────────
class LogBox(tk.Frame):
    def __init__(self, parent, height=12, **kw):
        super().__init__(parent, bg=BG, **kw)
        self.text = scrolledtext.ScrolledText(
            self, bg="#010409", fg=TEXT, font=FONT_MONO,
            relief="flat", height=height, state="disabled",
            insertbackground=ACCENT, wrap="word",
            highlightthickness=1, highlightbackground=BORDER,
        )
        self.text.pack(fill="both", expand=True)
        self.text.tag_config("info",    foreground=ACCENT)
        self.text.tag_config("ok",      foreground=ACCENT2)
        self.text.tag_config("err",     foreground=ACCENT3)
        self.text.tag_config("warn",    foreground=ACCENT_YLW)
        self.text.tag_config("cmd",     foreground=TEXT_DIM)
        self.text.tag_config("out",     foreground=TEXT)
        self.text.tag_config("ts",      foreground=TEXT_DARK)

    def log(self, msg, kind="out"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.text.config(state="normal")
        self.text.insert("end", f"[{ts}] ", "ts")
        self.text.insert("end", msg + "\n", kind)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")


# ─────────────────────────────────────────────
# NÚCLEO SSH
# ─────────────────────────────────────────────
class SSHClient:
    def __init__(self):
        self.client   = None
        self.connected = False

    def connect(self, host, port, user, key_path=None, password=None):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kw = dict(hostname=host, port=int(port), username=user, timeout=15)
        if key_path:
            kw["key_filename"] = key_path
        if password:
            kw["password"] = password
        self.client.connect(**kw)
        self.connected = True

    def exec(self, cmd, timeout=120):
        if not self.connected:
            raise RuntimeError("Não conectado ao servidor.")
        stdin, stdout, stderr = self.client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        return out, err

    def exec_stream(self, cmd, callback, timeout=300):
        """Executa e faz streaming linha a linha via callback(line, kind)."""
        if not self.connected:
            raise RuntimeError("Não conectado ao servidor.")
        transport = self.client.get_transport()
        chan = transport.open_session()
        chan.get_pty()
        chan.exec_command(cmd)
        chan.settimeout(timeout)
        buf = ""
        while True:
            if chan.recv_ready():
                chunk = chan.recv(4096).decode(errors="replace")
                buf += chunk
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    callback(line, "out")
            if chan.recv_stderr_ready():
                chunk = chan.recv_stderr(4096).decode(errors="replace")
                for line in chunk.splitlines():
                    callback(line, "err")
            if chan.exit_status_ready():
                break
            time.sleep(0.05)
        if buf.strip():
            callback(buf, "out")
        return chan.recv_exit_status()

    def disconnect(self):
        if self.client:
            self.client.close()
        self.connected = False


# ─────────────────────────────────────────────
# APLICAÇÃO PRINCIPAL
# ─────────────────────────────────────────────
class VPSManager(tk.Tk):
    SAVE_FILE = Path.home() / ".vps_manager_profiles.json"

    def __init__(self):
        super().__init__()
        self.ssh  = SSHClient()
        self.title("VPS Manager")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.geometry("920x760")
        self.minsize(800, 640)

        # vars
        self.v_host       = tk.StringVar()
        self.v_port       = tk.StringVar(value="22")
        self.v_user       = tk.StringVar(value="root")
        self.v_key        = tk.StringVar()
        self.v_pass       = tk.StringVar()
        self.v_auth_mode  = tk.StringVar(value="key")   # key | password

        self.v_git_repo   = tk.StringVar()
        self.v_git_user   = tk.StringVar()
        self.v_git_email  = tk.StringVar()
        self.v_git_key    = tk.StringVar()
        self.v_proj_dir   = tk.StringVar(value="/root/projeto")
        self.v_script     = tk.StringVar(value="install.sh")
        self.v_screen_name= tk.StringVar(value="app")

        self.v_profile    = tk.StringVar()
        self.profiles     = self._load_profiles()

        self._build_ui()

    # ── BUILD UI ──────────────────────────────
    def _build_ui(self):
        # ── HEADER ──
        hdr = tk.Frame(self, bg=BG, pady=12)
        hdr.pack(fill="x", padx=20)
        tk.Label(hdr, text="⬡  VPS Manager", font=FONT_TITLE,
                 fg=ACCENT, bg=BG).pack(side="left")
        self.badge = StatusBadge(hdr)
        self.badge.pack(side="right")

        sep(self).pack(fill="x", padx=20)

        # ── NOTEBOOK ──
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TNotebook",            background=BG,       borderwidth=0)
        style.configure("TNotebook.Tab",        background=BG_INPUT, foreground=TEXT_DIM,
                        padding=[14, 6],        font=FONT_UI,        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", BG_CARD)],
                  foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=20, pady=10)

        self._tab_ssh(nb)
        self._tab_git(nb)
        self._tab_deploy(nb)
        self._tab_screen(nb)

        # ── LOG ──
        log_frame = styled_frame(self, bg=BG)
        log_frame.pack(fill="both", expand=False, padx=20, pady=(0, 12))
        log_hdr = tk.Frame(log_frame, bg=BG)
        log_hdr.pack(fill="x")
        label(log_hdr, "📋  Log de saída", color=TEXT_DIM, bg=BG).pack(side="left")
        btn(log_hdr, "Limpar", self._clear_log,
            color=BG_INPUT, fg=TEXT_DIM, width=8).pack(side="right")
        self.log = LogBox(log_frame, height=11)
        self.log.pack(fill="both", expand=True, pady=(4, 0))

    # ── TAB: SSH ──────────────────────────────
    def _tab_ssh(self, nb):
        tab = styled_frame(nb)
        nb.add(tab, text="  🔐  Conexão SSH  ")
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)

        # ── Profile selector ──
        pf = styled_frame(tab)
        pf.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 8))
        label(pf, "Perfil salvo:", color=TEXT_DIM).pack(side="left")
        self._profile_cb = ttk.Combobox(pf, textvariable=self.v_profile,
                                        values=list(self.profiles.keys()),
                                        state="readonly", width=22,
                                        font=FONT_UI)
        self._profile_cb.pack(side="left", padx=6)
        btn(pf, "Carregar", self._load_profile, color=BG_INPUT, fg=ACCENT, width=10).pack(side="left", padx=4)
        btn(pf, "Salvar",   self._save_profile, color=BG_INPUT, fg=ACCENT2, width=10).pack(side="left", padx=2)
        btn(pf, "Deletar",  self._del_profile,  color=BG_INPUT, fg=ACCENT3, width=10).pack(side="left", padx=2)

        sep(tab).grid(row=1, column=0, columnspan=2, sticky="ew", padx=16)

        # ── Campos ──
        def row(r, lbl, var, show=None, col=0):
            label(tab, lbl, color=TEXT_DIM).grid(
                row=r, column=col*2, sticky="w", padx=(16 if col==0 else 8, 4), pady=5)
            e = entry(tab, textvariable=var, show=show, width=28)
            e.grid(row=r, column=col*2+1, sticky="ew", padx=(0, 16), pady=5)
            tab.columnconfigure(col*2+1, weight=1)
            return e

        row(2, "Host / IP:",   self.v_host)
        row(2, "Porta:",       self.v_port, col=1)
        row(3, "Usuário:",     self.v_user)

        # ── Auth mode ──
        auth_frm = styled_frame(tab)
        auth_frm.grid(row=4, column=0, columnspan=2, sticky="w", padx=16, pady=(8, 0))
        label(auth_frm, "Autenticação:").pack(side="left", padx=(0, 12))
        for val, txt in [("key", "Chave SSH"), ("password", "Senha")]:
            tk.Radiobutton(auth_frm, text=txt, variable=self.v_auth_mode, value=val,
                           bg=BG_CARD, fg=TEXT, selectcolor=BG_INPUT,
                           activebackground=BG_CARD, activeforeground=ACCENT,
                           font=FONT_UI, cursor="hand2",
                           command=self._toggle_auth).pack(side="left", padx=6)

        # key row
        self._key_frm = styled_frame(tab)
        self._key_frm.grid(row=5, column=0, columnspan=2, sticky="ew", padx=16, pady=4)
        label(self._key_frm, "Caminho da chave:", color=TEXT_DIM).pack(side="left")
        self._key_entry = entry(self._key_frm, textvariable=self.v_key, width=32)
        self._key_entry.pack(side="left", padx=6)
        btn(self._key_frm, "Procurar", self._browse_key,
            color=BG_INPUT, fg=ACCENT, width=9).pack(side="left")

        # password row
        self._pass_frm = styled_frame(tab)
        self._pass_frm.grid(row=6, column=0, columnspan=2, sticky="ew", padx=16, pady=4)
        label(self._pass_frm, "Senha:", color=TEXT_DIM).pack(side="left")
        entry(self._pass_frm, textvariable=self.v_pass, show="●", width=32).pack(side="left", padx=6)

        self._toggle_auth()   # estado inicial

        # ── Botões ──
        btn_frm = styled_frame(tab)
        btn_frm.grid(row=7, column=0, columnspan=2, pady=(12, 16), padx=16, sticky="w")
        btn(btn_frm, "▶  Conectar",     self._connect,    color=ACCENT,  fg=BG,  width=16).pack(side="left", padx=(0, 8))
        btn(btn_frm, "✕  Desconectar",  self._disconnect, color=ACCENT3, fg=BG,  width=16).pack(side="left")

        # ── Teste rápido ──
        sep(tab).grid(row=8, column=0, columnspan=2, sticky="ew", padx=16)
        test_frm = styled_frame(tab)
        test_frm.grid(row=9, column=0, columnspan=2, sticky="ew", padx=16, pady=12)
        label(test_frm, "Comando rápido:", color=TEXT_DIM).pack(side="left")
        self.v_quick_cmd = tk.StringVar(value="uname -a && uptime")
        entry(test_frm, textvariable=self.v_quick_cmd, width=40).pack(side="left", padx=6)
        btn(test_frm, "Executar", self._quick_cmd,
            color=ACCENT_YLW, fg=BG, width=10).pack(side="left")

    # ── TAB: GIT ──────────────────────────────
    def _tab_git(self, nb):
        tab = styled_frame(nb)
        nb.add(tab, text="  🐙  Git  ")

        def row(r, lbl, var, show=None, ph=""):
            lf = styled_frame(tab)
            lf.grid(row=r, column=0, sticky="ew", padx=16, pady=5)
            tab.columnconfigure(0, weight=1)
            label(lf, lbl, color=TEXT_DIM, width=20, anchor="w").pack(side="left")
            e = entry(lf, textvariable=var, show=show, width=46)
            e.pack(side="left", padx=6)
            if ph:
                e.insert(0, ph)
                e.config(fg=TEXT_DIM)
                def on_focus_in(ev, e=e, ph=ph):
                    if e.get() == ph:
                        e.delete(0, "end"); e.config(fg=TEXT)
                def on_focus_out(ev, e=e, ph=ph):
                    if not e.get():
                        e.insert(0, ph); e.config(fg=TEXT_DIM)
                e.bind("<FocusIn>",  on_focus_in)
                e.bind("<FocusOut>", on_focus_out)
            return e

        label(tab, "Configuração Git no Servidor", color=ACCENT,
              font=FONT_UI_B, bg=BG_CARD).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        row(1, "URL do repositório:",  self.v_git_repo,
            ph="git@github.com:usuario/projeto.git")
        row(2, "Nome do usuário Git:", self.v_git_user,  ph="Seu Nome")
        row(3, "E-mail Git:",          self.v_git_email, ph="email@exemplo.com")
        row(4, "Diretório destino:",   self.v_proj_dir,  ph="/root/projeto")

        sep(tab).grid(row=5, column=0, sticky="ew", padx=16, pady=8)

        # ── Chave SSH do servidor para o Git ──
        label(tab, "Chave SSH do servidor (para GitHub/GitLab)",
              color=ACCENT, font=FONT_UI_B, bg=BG_CARD).grid(
            row=6, column=0, sticky="w", padx=16, pady=(0, 4))

        note_txt = ("O VPS Manager pode gerar uma chave no servidor e exibir\n"
                    "a chave pública para que você adicione como Deploy Key.")
        label(tab, note_txt, color=TEXT_DIM, justify="left",
              bg=BG_CARD).grid(row=7, column=0, sticky="w", padx=16)

        key_btn_frm = styled_frame(tab)
        key_btn_frm.grid(row=8, column=0, sticky="w", padx=16, pady=8)
        btn(key_btn_frm, "Gerar chave no servidor", self._gen_ssh_key,
            color=ACCENT_YLW, fg=BG, width=22).pack(side="left", padx=(0, 8))
        btn(key_btn_frm, "Ver chave pública", self._show_pub_key,
            color=BG_INPUT, fg=ACCENT, width=18).pack(side="left")

        sep(tab).grid(row=9, column=0, sticky="ew", padx=16, pady=8)

        # ── Clone ──
        clone_frm = styled_frame(tab)
        clone_frm.grid(row=10, column=0, sticky="w", padx=16, pady=(0, 16))
        btn(clone_frm, "⬇  Clonar repositório", self._git_clone,
            color=ACCENT2, fg=BG, width=22).pack(side="left", padx=(0, 8))
        btn(clone_frm, "↻  Pull (atualizar)", self._git_pull,
            color=BG_INPUT, fg=ACCENT2, width=18).pack(side="left")

    # ── TAB: DEPLOY ───────────────────────────
    def _tab_deploy(self, nb):
        tab = styled_frame(nb)
        nb.add(tab, text="  🚀  Deploy  ")
        tab.columnconfigure(0, weight=1)

        label(tab, "Scripts de Deploy", color=ACCENT, font=FONT_UI_B,
              bg=BG_CARD).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        info = ("Os scripts abaixo devem estar no diretório do projeto.\n"
                "O script de install.sh será executado diretamente.\n"
                "Start e Stop são gerenciados via screen.")
        label(tab, info, color=TEXT_DIM, justify="left",
              bg=BG_CARD).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 8))

        sep(tab).grid(row=2, column=0, sticky="ew", padx=16)

        def field_row(r, lbl, var, ph=""):
            frm = styled_frame(tab)
            frm.grid(row=r, column=0, sticky="ew", padx=16, pady=6)
            label(frm, lbl, color=TEXT_DIM, width=22, anchor="w").pack(side="left")
            e = entry(frm, textvariable=var, width=36)
            e.pack(side="left", padx=6)
            return e

        field_row(3, "Diretório do projeto:", self.v_proj_dir)
        field_row(4, "Script de instalação:", self.v_script)

        sep(tab).grid(row=5, column=0, sticky="ew", padx=16, pady=8)

        # ── Botões de ação ──
        label(tab, "Ações", color=ACCENT, font=FONT_UI_B,
              bg=BG_CARD).grid(row=6, column=0, sticky="w", padx=16, pady=(0, 8))

        actions = styled_frame(tab)
        actions.grid(row=7, column=0, sticky="w", padx=16, pady=(0, 16))

        btn(actions, "⚙  Install",  self._install,
            color=ACCENT, fg=BG,   width=14).pack(side="left", padx=(0, 8))
        btn(actions, "▶  Start",   self._start,
            color=ACCENT2, fg=BG,  width=14).pack(side="left", padx=(0, 8))
        btn(actions, "■  Stop",    self._stop,
            color=ACCENT3, fg=BG,  width=14).pack(side="left")

        sep(tab).grid(row=8, column=0, sticky="ew", padx=16, pady=8)

        # ── Comando personalizado ──
        label(tab, "Comando personalizado", color=ACCENT, font=FONT_UI_B,
              bg=BG_CARD).grid(row=9, column=0, sticky="w", padx=16, pady=(0, 4))
        custom_frm = styled_frame(tab)
        custom_frm.grid(row=10, column=0, sticky="ew", padx=16, pady=(0, 12))
        self.v_custom = tk.StringVar()
        entry(custom_frm, textvariable=self.v_custom, width=46).pack(side="left", padx=(0, 6))
        btn(custom_frm, "Executar", self._run_custom,
            color=ACCENT_YLW, fg=BG, width=10).pack(side="left")

    # ── TAB: SCREEN ───────────────────────────
    def _tab_screen(self, nb):
        tab = styled_frame(nb)
        nb.add(tab, text="  🖥  Screen  ")
        tab.columnconfigure(0, weight=1)

        label(tab, "Gerenciamento de Sessões Screen", color=ACCENT,
              font=FONT_UI_B, bg=BG_CARD).grid(
            row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        frm = styled_frame(tab)
        frm.grid(row=1, column=0, sticky="ew", padx=16, pady=6)
        label(frm, "Nome da sessão screen:", color=TEXT_DIM, width=24,
              anchor="w").pack(side="left")
        entry(frm, textvariable=self.v_screen_name, width=24).pack(side="left", padx=6)

        sep(tab).grid(row=2, column=0, sticky="ew", padx=16, pady=8)

        frm2 = styled_frame(tab)
        frm2.grid(row=3, column=0, sticky="w", padx=16, pady=(0, 8))
        label(frm2, "Script de start:", color=TEXT_DIM, width=24,
              anchor="w").pack(side="left")
        self.v_start_script = tk.StringVar(value="start.sh")
        entry(frm2, textvariable=self.v_start_script, width=24).pack(side="left", padx=6)

        frm3 = styled_frame(tab)
        frm3.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 8))
        label(frm3, "Script de stop:", color=TEXT_DIM, width=24,
              anchor="w").pack(side="left")
        self.v_stop_script = tk.StringVar(value="stop.sh")
        entry(frm3, textvariable=self.v_stop_script, width=24).pack(side="left", padx=6)

        sep(tab).grid(row=5, column=0, sticky="ew", padx=16, pady=8)

        btn_frm = styled_frame(tab)
        btn_frm.grid(row=6, column=0, sticky="w", padx=16, pady=(0, 8))
        btn(btn_frm, "▶  Start (screen)", self._screen_start,
            color=ACCENT2, fg=BG, width=18).pack(side="left", padx=(0, 8))
        btn(btn_frm, "■  Stop (screen)",  self._screen_stop,
            color=ACCENT3, fg=BG, width=18).pack(side="left", padx=(0, 8))
        btn(btn_frm, "↻  Listar sessões", self._screen_list,
            color=BG_INPUT, fg=ACCENT, width=18).pack(side="left")

        sep(tab).grid(row=7, column=0, sticky="ew", padx=16, pady=8)

        btn_frm2 = styled_frame(tab)
        btn_frm2.grid(row=8, column=0, sticky="w", padx=16, pady=(0, 16))
        btn(btn_frm2, "🗑  Encerrar sessão", self._screen_kill,
            color=BG_INPUT, fg=ACCENT3, width=20).pack(side="left", padx=(0, 8))
        btn(btn_frm2, "📄  Ver log da sessão", self._screen_log,
            color=BG_INPUT, fg=ACCENT_YLW, width=20).pack(side="left")

    # ── HELPERS ───────────────────────────────
    def _toggle_auth(self):
        if self.v_auth_mode.get() == "key":
            self._key_frm.grid()
            self._pass_frm.grid_remove()
        else:
            self._key_frm.grid_remove()
            self._pass_frm.grid()

    def _browse_key(self):
        path = filedialog.askopenfilename(
            title="Selecione a chave SSH privada",
            initialdir=str(Path.home() / ".ssh"),
            filetypes=[("Todos os arquivos", "*"), ("Chave SSH", "id_*")],
        )
        if path:
            self.v_key.set(path)

    def _clear_log(self):
        self.log.clear()

    def _thread(self, fn, *args):
        t = threading.Thread(target=fn, args=args, daemon=True)
        t.start()

    def _run_cmd(self, cmd, desc="Executando…", stream=True):
        self.log.log(f"$ {cmd}", "cmd")
        try:
            if stream:
                def cb(line, kind):
                    self.log.log(line, kind)
                code = self.ssh.exec_stream(cmd, cb)
                if code and code != 0:
                    self.log.log(f"[Saiu com código {code}]", "warn")
            else:
                out, err = self.ssh.exec(cmd)
                for line in out.splitlines():
                    self.log.log(line, "out")
                for line in err.splitlines():
                    self.log.log(line, "err")
        except Exception as ex:
            self.log.log(f"Erro: {ex}", "err")

    # ── PROFILES ──────────────────────────────
    def _load_profiles(self):
        try:
            if self.SAVE_FILE.exists():
                return json.loads(self.SAVE_FILE.read_text())
        except Exception:
            pass
        return {}

    def _save_profiles(self):
        try:
            self.SAVE_FILE.write_text(json.dumps(self.profiles, indent=2))
        except Exception as e:
            self.log.log(f"Não foi possível salvar perfil: {e}", "warn")

    def _save_profile(self):
        name = self.v_profile.get().strip()
        if not name:
            name = self.v_host.get() or "novo-perfil"
            self.v_profile.set(name)
        self.profiles[name] = {
            "host": self.v_host.get(), "port": self.v_port.get(),
            "user": self.v_user.get(), "key": self.v_key.get(),
            "auth_mode": self.v_auth_mode.get(),
            "git_repo": self.v_git_repo.get(), "git_user": self.v_git_user.get(),
            "git_email": self.v_git_email.get(), "proj_dir": self.v_proj_dir.get(),
            "script": self.v_script.get(), "screen_name": self.v_screen_name.get(),
            "start_script": self.v_start_script.get(),
            "stop_script": self.v_stop_script.get(),
        }
        self._save_profiles()
        self._profile_cb["values"] = list(self.profiles.keys())
        self.log.log(f"Perfil '{name}' salvo.", "ok")

    def _load_profile(self):
        name = self.v_profile.get()
        p = self.profiles.get(name)
        if not p:
            self.log.log("Selecione um perfil válido.", "warn"); return
        self.v_host.set(p.get("host", ""))
        self.v_port.set(p.get("port", "22"))
        self.v_user.set(p.get("user", "root"))
        self.v_key.set(p.get("key", ""))
        self.v_auth_mode.set(p.get("auth_mode", "key"))
        self.v_git_repo.set(p.get("git_repo", ""))
        self.v_git_user.set(p.get("git_user", ""))
        self.v_git_email.set(p.get("git_email", ""))
        self.v_proj_dir.set(p.get("proj_dir", "/root/projeto"))
        self.v_script.set(p.get("script", "install.sh"))
        self.v_screen_name.set(p.get("screen_name", "app"))
        self.v_start_script.set(p.get("start_script", "start.sh"))
        self.v_stop_script.set(p.get("stop_script", "stop.sh"))
        self._toggle_auth()
        self.log.log(f"Perfil '{name}' carregado.", "ok")

    def _del_profile(self):
        name = self.v_profile.get()
        if name in self.profiles:
            del self.profiles[name]
            self._save_profiles()
            self._profile_cb["values"] = list(self.profiles.keys())
            self.v_profile.set("")
            self.log.log(f"Perfil '{name}' removido.", "warn")

    # ── SSH ACTIONS ───────────────────────────
    def _connect(self):
        def _do():
            self.badge.set("connecting")
            self.log.log(f"Conectando em {self.v_user.get()}@{self.v_host.get()}:{self.v_port.get()}…", "info")
            try:
                key = self.v_key.get() if self.v_auth_mode.get() == "key" else None
                pwd = self.v_pass.get() if self.v_auth_mode.get() == "password" else None
                self.ssh.connect(self.v_host.get(), self.v_port.get(),
                                 self.v_user.get(), key_path=key, password=pwd)
                self.badge.set("connected")
                self.log.log("Conexão SSH estabelecida com sucesso!", "ok")
                out, _ = self.ssh.exec("uname -a && uptime")
                for line in out.splitlines():
                    self.log.log(line, "out")
            except Exception as ex:
                self.badge.set("error")
                self.log.log(f"Falha na conexão: {ex}", "err")
        self._thread(_do)

    def _disconnect(self):
        self.ssh.disconnect()
        self.badge.set("disconnected")
        self.log.log("Desconectado do servidor.", "warn")

    def _quick_cmd(self):
        cmd = self.v_quick_cmd.get().strip()
        if cmd:
            self._thread(self._run_cmd, cmd)

    # ── GIT ACTIONS ───────────────────────────
    def _gen_ssh_key(self):
        def _do():
            self.log.log("Gerando chave SSH no servidor (ed25519)…", "info")
            self._run_cmd('ssh-keygen -t ed25519 -C "vps-deploy" -f ~/.ssh/id_ed25519 -N "" -q || true')
        self._thread(_do)

    def _show_pub_key(self):
        def _do():
            self.log.log("Chave pública do servidor (~/.ssh/id_ed25519.pub):", "info")
            self._run_cmd("cat ~/.ssh/id_ed25519.pub", stream=False)
        self._thread(_do)

    def _git_clone(self):
        repo = self.v_git_repo.get().strip()
        dest = self.v_proj_dir.get().strip()
        user = self.v_git_user.get().strip()
        email = self.v_git_email.get().strip()
        if not repo or not dest:
            self.log.log("Preencha a URL do repositório e o diretório destino.", "warn"); return
        def _do():
            self.log.log(f"Clonando {repo} → {dest}", "info")
            cmds = []
            if user:  cmds.append(f'git config --global user.name "{user}"')
            if email: cmds.append(f'git config --global user.email "{email}"')
            cmds += [
                f'mkdir -p "$(dirname "{dest}")"',
                f'GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git clone "{repo}" "{dest}"',
            ]
            for c in cmds:
                self._run_cmd(c)
        self._thread(_do)

    def _git_pull(self):
        dest = self.v_proj_dir.get().strip()
        def _do():
            self.log.log(f"Atualizando repositório em {dest}…", "info")
            self._run_cmd(f'cd "{dest}" && GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git pull')
        self._thread(_do)

    # ── DEPLOY ACTIONS ────────────────────────
    def _install(self):
        dest   = self.v_proj_dir.get().strip()
        script = self.v_script.get().strip()
        def _do():
            self.log.log(f"Executando {script} em {dest}…", "info")
            self._run_cmd(f'cd "{dest}" && chmod +x "{script}" && bash "{script}"')
        self._thread(_do)

    def _start(self):
        dest    = self.v_proj_dir.get().strip()
        session = self.v_screen_name.get().strip() or "app"
        start   = self.v_start_script.get().strip() or "start.sh"
        def _do():
            self.log.log(f"Iniciando sessão screen '{session}'…", "info")
            cmd = (f'screen -dmS "{session}" bash -c '
                   f'"cd \'{dest}\' && bash \'{start}\' 2>&1 | tee /tmp/{session}.log"')
            self._run_cmd(cmd)
            time.sleep(1)
            self._run_cmd("screen -ls", stream=False)
        self._thread(_do)

    def _stop(self):
        dest    = self.v_proj_dir.get().strip()
        session = self.v_screen_name.get().strip() or "app"
        stop    = self.v_stop_script.get().strip() or "stop.sh"
        def _do():
            self.log.log(f"Parando sessão '{session}'…", "info")
            # Tenta rodar stop.sh se existir, depois mata a sessão screen
            self._run_cmd(f'[ -f "{dest}/{stop}" ] && bash "{dest}/{stop}" || true',
                          stream=False)
            self._run_cmd(f'screen -S "{session}" -X quit 2>/dev/null || true',
                          stream=False)
            self.log.log("Sessão encerrada.", "ok")
        self._thread(_do)

    def _run_custom(self):
        cmd = self.v_custom.get().strip()
        if cmd:
            self._thread(self._run_cmd, cmd)

    # ── SCREEN ACTIONS ────────────────────────
    def _screen_start(self):
        self._start()

    def _screen_stop(self):
        self._stop()

    def _screen_list(self):
        def _do():
            self.log.log("Sessões screen ativas:", "info")
            self._run_cmd("screen -ls", stream=False)
        self._thread(_do)

    def _screen_kill(self):
        session = self.v_screen_name.get().strip() or "app"
        def _do():
            self.log.log(f"Encerrando sessão screen '{session}'…", "warn")
            self._run_cmd(f'screen -S "{session}" -X kill 2>/dev/null || '
                         f'screen -S "{session}" -X quit 2>/dev/null || true',
                         stream=False)
            self.log.log("Sessão removida.", "ok")
        self._thread(_do)

    def _screen_log(self):
        session = self.v_screen_name.get().strip() or "app"
        def _do():
            self.log.log(f"Últimas linhas do log da sessão '{session}':", "info")
            self._run_cmd(f'tail -40 /tmp/{session}.log 2>/dev/null || '
                         f'echo "(log não encontrado em /tmp/{session}.log)"',
                         stream=False)
        self._thread(_do)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    try:
        import paramiko  # noqa: F401
    except ImportError:
        import subprocess, sys
        print("Instalando dependência: paramiko…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])

    app = VPSManager()
    app.mainloop()
