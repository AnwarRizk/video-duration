#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess, os, sys, threading, time
from urllib.parse import unquote, urlparse

VENDOR_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "vendor")
if os.path.isdir(VENDOR_DIR) and VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TKDND_AVAILABLE = True
    APP_BASE = TkinterDnD.Tk
except Exception:
    DND_FILES = None
    TKDND_AVAILABLE = False
    APP_BASE = tk.Tk

# ── palette ───────────────────────────────────────────────────────────────────
BG      = "#1e1f26"
BG2     = "#16171d"
BG3     = "#2a2b35"
PANEL   = "#252631"
BORDER  = "#33364a"
FG      = "#e8eaf0"
FG2     = "#9395a5"
ACCENT  = "#5b6ef5"
ACCENT2 = "#7c8cf8"
GREEN   = "#3ecf8e"
RED     = "#f87272"
RED_DIM = "#5a1e1e"
AMBER   = "#f5a623"
ROW_A   = "#1e1f26"
ROW_B   = "#22232e"
SEL     = "#2e3050"

FONT_FAMILY = "Noto Sans Arabic"
MONO_FAMILY = "Noto Sans Arabic"

VIDEO_EXTS = {
    '.mp4','.mkv','.avi','.mov','.webm',
    '.flv','.wmv','.m4v','.ts','.mpg','.mpeg','.3gp','.ogv'
}
EXT_COLOR = {
    '.mp4':'#7c8cf8', '.mkv':'#3ecf8e', '.avi':'#f5a623',
    '.mov':'#e879f9', '.webm':'#22d3ee', '.flv':'#fb923c',
    '.wmv':'#f87272', '.m4v':'#a78bfa',
}

ARABIC_FORMS = {
    "\u0621": ("\ufe80", None, None, None),
    "\u0622": ("\ufe81", "\ufe82", None, None),
    "\u0623": ("\ufe83", "\ufe84", None, None),
    "\u0624": ("\ufe85", "\ufe86", None, None),
    "\u0625": ("\ufe87", "\ufe88", None, None),
    "\u0626": ("\ufe89", "\ufe8a", "\ufe8b", "\ufe8c"),
    "\u0627": ("\ufe8d", "\ufe8e", None, None),
    "\u0628": ("\ufe8f", "\ufe90", "\ufe91", "\ufe92"),
    "\u0629": ("\ufe93", "\ufe94", None, None),
    "\u062a": ("\ufe95", "\ufe96", "\ufe97", "\ufe98"),
    "\u062b": ("\ufe99", "\ufe9a", "\ufe9b", "\ufe9c"),
    "\u062c": ("\ufe9d", "\ufe9e", "\ufe9f", "\ufea0"),
    "\u062d": ("\ufea1", "\ufea2", "\ufea3", "\ufea4"),
    "\u062e": ("\ufea5", "\ufea6", "\ufea7", "\ufea8"),
    "\u062f": ("\ufea9", "\ufeaa", None, None),
    "\u0630": ("\ufeab", "\ufeac", None, None),
    "\u0631": ("\ufead", "\ufeae", None, None),
    "\u0632": ("\ufeaf", "\ufeb0", None, None),
    "\u0633": ("\ufeb1", "\ufeb2", "\ufeb3", "\ufeb4"),
    "\u0634": ("\ufeb5", "\ufeb6", "\ufeb7", "\ufeb8"),
    "\u0635": ("\ufeb9", "\ufeba", "\ufebb", "\ufebc"),
    "\u0636": ("\ufebd", "\ufebe", "\ufebf", "\ufec0"),
    "\u0637": ("\ufec1", "\ufec2", "\ufec3", "\ufec4"),
    "\u0638": ("\ufec5", "\ufec6", "\ufec7", "\ufec8"),
    "\u0639": ("\ufec9", "\ufeca", "\ufecb", "\ufecc"),
    "\u063a": ("\ufecd", "\ufece", "\ufecf", "\ufed0"),
    "\u0641": ("\ufed1", "\ufed2", "\ufed3", "\ufed4"),
    "\u0642": ("\ufed5", "\ufed6", "\ufed7", "\ufed8"),
    "\u0643": ("\ufed9", "\ufeda", "\ufedb", "\ufedc"),
    "\u0644": ("\ufedd", "\ufede", "\ufedf", "\ufee0"),
    "\u0645": ("\ufee1", "\ufee2", "\ufee3", "\ufee4"),
    "\u0646": ("\ufee5", "\ufee6", "\ufee7", "\ufee8"),
    "\u0647": ("\ufee9", "\ufeea", "\ufeeb", "\ufeec"),
    "\u0648": ("\ufeed", "\ufeee", None, None),
    "\u0649": ("\ufeef", "\ufef0", None, None),
    "\u064a": ("\ufef1", "\ufef2", "\ufef3", "\ufef4"),
    "\u067e": ("\ufb56", "\ufb57", "\ufb58", "\ufb59"),
    "\u0686": ("\ufb7a", "\ufb7b", "\ufb7c", "\ufb7d"),
    "\u0698": ("\ufb8a", "\ufb8b", None, None),
    "\u06a9": ("\ufb8e", "\ufb8f", "\ufb90", "\ufb91"),
    "\u06af": ("\ufb92", "\ufb93", "\ufb94", "\ufb95"),
    "\u06cc": ("\ufbfc", "\ufbfd", "\ufbfe", "\ufbff"),
}


def ui_font(size=10, weight=None):
    return (FONT_FAMILY, size, weight) if weight else (FONT_FAMILY, size)


def mono_font(size=10):
    return (MONO_FAMILY, size)


def _has_arabic(text):
    return any("\u0600" <= ch <= "\u06ff" for ch in str(text))


def _can_connect_prev(ch):
    forms = ARABIC_FORMS.get(ch)
    return bool(forms and forms[1])


def _can_connect_next(ch):
    forms = ARABIC_FORMS.get(ch)
    return bool(forms and forms[2])


def _shape_arabic_segment(segment):
    shaped = []
    for i, ch in enumerate(segment):
        forms = ARABIC_FORMS.get(ch)
        if not forms:
            shaped.append(ch)
            continue

        prev_ch = segment[i - 1] if i else ""
        next_ch = segment[i + 1] if i + 1 < len(segment) else ""
        joins_prev = _can_connect_next(prev_ch) and _can_connect_prev(ch)
        joins_next = _can_connect_next(ch) and _can_connect_prev(next_ch)

        if joins_prev and joins_next and forms[3]:
            shaped.append(forms[3])
        elif joins_prev:
            shaped.append(forms[1])
        elif joins_next and forms[2]:
            shaped.append(forms[2])
        else:
            shaped.append(forms[0])
    return "".join(reversed(shaped))


def _space_leads_to_arabic(text, pos):
    while pos < len(text) and text[pos].isspace():
        pos += 1
    return pos < len(text) and text[pos] in ARABIC_FORMS


def display_text(text):
    text = str(text)
    if not _has_arabic(text):
        return text

    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in ARABIC_FORMS:
            start = i
            i += 1
            while i < len(text):
                ch = text[i]
                if ch in ARABIC_FORMS:
                    i += 1
                elif ch.isspace() and _space_leads_to_arabic(text, i):
                    i += 1
                else:
                    break
            out.append(_shape_arabic_segment(text[start:i]))
        else:
            out.append(ch)
            i += 1
    return "".join(out)

# ── helpers ───────────────────────────────────────────────────────────────────
def get_duration(path):
    try:
        r = subprocess.run(
            ['ffprobe','-v','quiet','-show_entries','format=duration',
             '-of','csv=p=0', path],
            capture_output=True, text=True, timeout=15)
        v = r.stdout.strip()
        return float(v) if v else 0.0
    except Exception:
        return 0.0

def fmt_dur(s):
    s = int(s)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def fmt_size(b):
    for u in ('B','KB','MB','GB'):
        if b < 1024: return f"{b:.0f} {u}"
        b /= 1024
    return f"{b:.1f} TB"

def apply_dark_treeview(style, name="Dark.Treeview"):
    style.configure(name,
        background=BG, fieldbackground=BG, foreground=FG,
        rowheight=28, font=ui_font(10), borderwidth=0,
        relief="flat")
    style.configure(f"{name}.Heading",
        background=BG3, foreground=FG2,
        font=ui_font(9, "bold"), relief="flat", padding=(8,6))
    style.map(name,
        background=[("selected", SEL)],
        foreground=[("selected","#ffffff")])

# ── label-button helper ───────────────────────────────────────────────────────
def lbtn(parent, text, cmd, bg=BG3, fg=FG, hbg=BORDER,
         padx=14, pady=7, font_size=10):
    b = tk.Label(parent, text=text, bg=bg, fg=fg,
                 font=ui_font(font_size), padx=padx, pady=pady,
                 cursor="hand2", relief="flat")
    b.bind("<Button-1>", lambda e: cmd())
    b.bind("<Enter>",    lambda e: b.config(bg=hbg))
    b.bind("<Leave>",    lambda e: b.config(bg=bg))
    return b

# ── custom file browser ───────────────────────────────────────────────────────
class FileBrowser(tk.Toplevel):
    def __init__(self, parent, start_dir=None, mode="files"):
        super().__init__(parent)
        self.title("Select videos" if mode=="files" else "Select folder")
        self.configure(bg=BG2)
        self.geometry("860x560")
        self.minsize(600, 400)
        self.transient(parent)

        self.result   = []
        self.mode     = mode
        self.cur_dir  = os.path.realpath(start_dir or os.path.expanduser("~"))
        self._history = [self.cur_dir]
        self._hpos    = 0
        self._sel     = set()       # selected file paths
        self._rows    = []          # list of (iid, fullpath, is_dir, name)

        # apply style ONCE here, before building widgets
        st = ttk.Style(self)
        st.theme_use("clam")
        apply_dark_treeview(st, "B.Treeview")
        st.configure("Vertical.TScrollbar",
            background=BG3, troughcolor=BG2, arrowcolor=FG2, borderwidth=0)

        self._build()
        self._populate(self.cur_dir)
        self.update_idletasks()
        self.wait_visibility()
        self.grab_set()
        self.focus_set()

    # ── layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # nav bar
        nav = tk.Frame(self, bg=BG2, pady=8, padx=10)
        nav.pack(fill="x")

        lbtn(nav, " ← ", self._go_back, padx=10, pady=5).pack(side="left", padx=(0,3))
        lbtn(nav, " ↑ ", self._go_up,   padx=10, pady=5).pack(side="left", padx=(0,10))

        self._path_var = tk.StringVar(value=self.cur_dir)
        path_entry = tk.Entry(nav, textvariable=self._path_var,
                              bg=BG3, fg=FG, insertbackground=FG,
                              relief="flat", font=mono_font(10),
                              highlightthickness=1,
                              highlightcolor=ACCENT, highlightbackground=BORDER)
        path_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0,8))
        path_entry.bind("<Return>", lambda e: self._navigate(self._path_var.get()))

        lbtn(nav, "Go", lambda: self._navigate(self._path_var.get()),
             padx=12, pady=5).pack(side="left")

        # body: sidebar + file list
        body = tk.Frame(self, bg=BG2)
        body.pack(fill="both", expand=True, padx=10, pady=(0,8))

        self._build_sidebar(body)
        self._build_filelist(body)

        # bottom bar
        bot = tk.Frame(self, bg=BG2, padx=12, pady=10)
        bot.pack(fill="x")

        hint = ("Ctrl/Shift+click for multiple" if self.mode=="files"
                else "Navigate to the desired folder")
        tk.Label(bot, text=hint, bg=BG2, fg=FG2, font=ui_font(9)).pack(side="left")

        lbtn(bot, "Cancel", self.destroy,
             padx=14, pady=6).pack(side="right", padx=(8,0))

        ok_text = "Add selected files" if self.mode=="files" else "Select this folder"
        lbtn(bot, ok_text, self._confirm,
             bg=ACCENT, fg="#fff", hbg=ACCENT2,
             padx=14, pady=6).pack(side="right")

    def _build_sidebar(self, parent):
        side = tk.Frame(parent, bg=PANEL, width=170)
        side.pack(side="left", fill="y", padx=(0,8))
        side.pack_propagate(False)

        def section(title):
            tk.Label(side, text=title, bg=PANEL, fg=FG2,
                     font=ui_font(9), pady=8, padx=12, anchor="w").pack(fill="x")

        section("PLACES")
        bookmarks = [
            ("Home",      os.path.expanduser("~")),
            ("Desktop",   os.path.expanduser("~/Desktop")),
            ("Downloads", os.path.expanduser("~/Downloads")),
            ("Videos",    os.path.expanduser("~/Videos")),
            ("Documents", os.path.expanduser("~/Documents")),
            ("/ (root)",  "/"),
        ]
        for label, path in bookmarks:
            if os.path.isdir(path):
                self._place_btn(side, label, path)

        tk.Frame(side, bg=BORDER, height=1).pack(fill="x", pady=6, padx=8)
        section("DRIVES")
        for base in ("/media", "/mnt"):
            if os.path.isdir(base):
                try:
                    for item in sorted(os.listdir(base)):
                        full = os.path.join(base, item)
                        if os.path.isdir(full):
                            self._place_btn(side, f"  {item}", full)
                except Exception:
                    pass

    def _place_btn(self, parent, label, path):
        b = tk.Label(parent, text=label, bg=PANEL, fg=FG,
                     font=ui_font(10), padx=14, pady=6,
                     anchor="w", cursor="hand2")
        b.pack(fill="x")
        b.bind("<Button-1>", lambda e, p=path: self._navigate(p))
        b.bind("<Enter>",    lambda e: b.config(bg=BG3))
        b.bind("<Leave>",    lambda e: b.config(bg=PANEL))

    def _build_filelist(self, parent):
        right = tk.Frame(parent, bg=BG2)
        right.pack(side="left", fill="both", expand=True)

        # filter bar
        fbar = tk.Frame(right, bg=BG3, padx=10, pady=6)
        fbar.pack(fill="x", pady=(0,4))

        tk.Label(fbar, text="Search:", bg=BG3, fg=FG2,
                 font=ui_font(10)).pack(side="left")

        self._filter_var = tk.StringVar()
        self._filter_var.trace_add("write", lambda *a: self._apply_filter())
        tk.Entry(fbar, textvariable=self._filter_var,
                 bg=BG2, fg=FG, insertbackground=FG,
                 relief="flat", font=ui_font(10), width=22,
                 highlightthickness=1,
                 highlightcolor=ACCENT, highlightbackground=BORDER
                 ).pack(side="left", ipady=4, padx=8)

        if self.mode == "files":
            self._vid_only = tk.BooleanVar(value=True)
            tk.Checkbutton(fbar, text="Videos only",
                           variable=self._vid_only,
                           bg=BG3, fg=FG, selectcolor=BG3,
                           activebackground=BG3, activeforeground=FG,
                           relief="flat", font=ui_font(10),
                           command=lambda: self._populate(self.cur_dir)
                           ).pack(side="left")

        self._sel_lbl = tk.Label(fbar, text="", bg=BG3,
                                  fg=GREEN, font=ui_font(10, "bold"))
        self._sel_lbl.pack(side="right", padx=6)

        # treeview + scrollbar in their own frame
        tv_frame = tk.Frame(right, bg=BG2)
        tv_frame.pack(fill="both", expand=True)

        cols = ("name","size","modified") if self.mode=="files" else ("name","modified")
        self.tree = ttk.Treeview(tv_frame, columns=cols,
                                 show="headings",
                                 selectmode="extended" if self.mode=="files" else "browse",
                                 style="B.Treeview")

        self.tree.heading("name",     text="Name")
        self.tree.column("name", width=380, minwidth=180, stretch=True)

        if self.mode == "files":
            self.tree.heading("size",     text="Size",    anchor="e")
            self.tree.heading("modified", text="Modified")
            self.tree.column("size",     width=80,  minwidth=60,  stretch=False, anchor="e")
            self.tree.column("modified", width=160, minwidth=100, stretch=False)
        else:
            self.tree.heading("modified", text="Modified")
            self.tree.column("modified", width=200, minwidth=100, stretch=False)

        vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<Double-Button-1>",  self._on_double)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Return>",           self._on_double)

    # ── navigation ───────────────────────────────────────────────────────────
    def _navigate(self, path):
        path = os.path.realpath(path)
        if not os.path.isdir(path):
            return
        self.cur_dir = path
        self._path_var.set(path)
        if self._hpos < len(self._history) - 1:
            self._history = self._history[:self._hpos+1]
        self._history.append(path)
        self._hpos = len(self._history) - 1
        self._sel.clear()
        self._populate(path)

    def _go_back(self):
        if self._hpos > 0:
            self._hpos -= 1
            p = self._history[self._hpos]
            self.cur_dir = p
            self._path_var.set(p)
            self._populate(p)

    def _go_up(self):
        self._navigate(os.path.dirname(self.cur_dir))

    # ── populate ─────────────────────────────────────────────────────────────
    def _populate(self, path):
        self.tree.delete(*self.tree.get_children())
        self._rows = []

        try:
            entries = sorted(os.scandir(path),
                             key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            tk.Label(self.tree, text="Permission denied", fg=RED, bg=BG).pack()
            return

        vid_filter = (self.mode == "files" and
                      hasattr(self, '_vid_only') and self._vid_only.get())

        for i, entry in enumerate(entries):
            if entry.name.startswith("."):
                continue
            is_dir = entry.is_dir(follow_symlinks=False)
            ext    = os.path.splitext(entry.name)[1].lower()
            is_vid = ext in VIDEO_EXTS

            if self.mode == "files" and not is_dir and vid_filter and not is_vid:
                continue
            if self.mode == "folder" and not is_dir:
                continue

            try:
                st    = entry.stat()
                mtime = time.strftime("%Y-%m-%d  %H:%M", time.localtime(st.st_mtime))
                size  = fmt_size(st.st_size) if not is_dir else ""
            except Exception:
                mtime = size = ""

            # text label with leading icon using plain ASCII
            prefix = "[D] " if is_dir else ("[V] " if is_vid else "[F] ")
            label  = prefix + display_text(entry.name)

            if self.mode == "files":
                values = (label, size, mtime)
            else:
                values = (label, mtime)

            tag  = "dir" if is_dir else ("vid" if is_vid else "other")
            rtag = f"row{'a' if i%2==0 else 'b'}"
            iid  = self.tree.insert("", "end", values=values, tags=(tag, rtag))
            self._rows.append((iid, entry.path, is_dir, entry.name))

        # tag colors
        self.tree.tag_configure("dir",   foreground=ACCENT2)
        self.tree.tag_configure("vid",   foreground=GREEN)
        self.tree.tag_configure("other", foreground=FG2)
        self.tree.tag_configure("rowa",  background=ROW_A)
        self.tree.tag_configure("rowb",  background=ROW_B)

        self._apply_filter()
        self._update_sel_lbl()

    def _apply_filter(self):
        q = self._filter_var.get().lower()
        for iid, path, is_dir, name in self._rows:
            if q and q not in name.lower():
                self.tree.detach(iid)
            else:
                try:
                    self.tree.reattach(iid, "", "end")
                except Exception:
                    pass

    # ── events ────────────────────────────────────────────────────────────────
    def _on_double(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        for r_iid, path, is_dir, name in self._rows:
            if r_iid == iid:
                if is_dir:
                    self._navigate(path)
                elif self.mode == "files":
                    self._sel = {path}
                    self._confirm()
                return

    def _on_select(self, event=None):
        if self.mode != "files":
            return
        lookup = {r[0]: r for r in self._rows}
        for iid in self.tree.selection():
            if iid in lookup:
                _, path, is_dir, _ = lookup[iid]
                if not is_dir:
                    self._sel.add(path)
        self._update_sel_lbl()

    def _update_sel_lbl(self):
        n = len(self._sel)
        self._sel_lbl.config(
            text=(f"{n} file{'s' if n!=1 else ''} selected" if n else ""))

    def _confirm(self):
        if self.mode == "files":
            if not self._sel:
                lookup = {r[0]: r for r in self._rows}
                for iid in self.tree.selection():
                    if iid in lookup:
                        _, path, is_dir, _ = lookup[iid]
                        if not is_dir:
                            self._sel.add(path)
            self.result = list(self._sel)
        else:
            self.result = [self.cur_dir]
        self.destroy()


# ── main window ───────────────────────────────────────────────────────────────
class App(APP_BASE):
    def __init__(self):
        super().__init__()
        self.title("Video Duration Calculator")
        self.geometry("920x620")
        self.minsize(700, 450)
        self.configure(bg=BG)

        self._files     = {}   # path -> duration
        self._sizes     = {}   # path -> bytes
        self._row_paths = {}   # tree iid -> original path
        self._row_names = {}   # tree iid -> original file name
        self._last_dir  = os.path.expanduser("~")

        st = ttk.Style(self)
        st.theme_use("clam")
        apply_dark_treeview(st, "Treeview")
        st.configure("Vertical.TScrollbar",
            background=BG3, troughcolor=BG, arrowcolor=FG2,
            borderwidth=0, gripcount=0)
        st.configure("TProgressbar",
            background=ACCENT, troughcolor=BG3, borderwidth=0, thickness=4)

        self._build()
        self._enable_drag_drop()

    # ── layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # accent line + header
        tk.Frame(self, bg=ACCENT, height=3).pack(fill="x")

        hdr = tk.Frame(self, bg=BG2, padx=18, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="▶  Video Duration Calculator",
                 bg=BG2, fg=FG, font=ui_font(15, "bold")).pack(side="left")
        tk.Label(hdr, text="Calculate total playtime of your video collection",
                 bg=BG2, fg=FG2, font=ui_font(10)).pack(side="left", padx=18)

        # toolbar
        tb = tk.Frame(self, bg=PANEL, padx=14, pady=9)
        tb.pack(fill="x")

        lbtn(tb, "+ Add files",  self.add_files,
             bg=ACCENT, fg="#fff", hbg=ACCENT2).pack(side="left", padx=(0,6))
        lbtn(tb, "+ Add folder", self.add_folder).pack(side="left", padx=(0,16))

        tk.Frame(tb, bg=BORDER, width=1).pack(side="left", fill="y", pady=3, padx=(0,16))

        lbtn(tb, "Remove selected", self.remove_selected,
             bg=RED_DIM, fg=RED, hbg="#7a2828",
             padx=10, pady=5, font_size=9).pack(side="left", padx=(0,6))
        lbtn(tb, "Clear all", self.clear_all,
             padx=10, pady=5, font_size=9).pack(side="left")

        # search
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *a: self._apply_search())
        sf = tk.Frame(tb, bg=BG3,
                      highlightthickness=1, highlightbackground=BORDER)
        sf.pack(side="right")
        tk.Label(sf, text=" search ", bg=BG3, fg=FG2,
                 font=ui_font(10)).pack(side="left")
        tk.Entry(sf, textvariable=self._search_var, bg=BG3, fg=FG,
                 insertbackground=FG, relief="flat", font=ui_font(10),
                 width=18).pack(side="left", ipady=6, padx=(0,6))

        # empty-state placeholder
        self._empty = tk.Frame(self, bg=BG, pady=60)
        tk.Label(self._empty, text="No videos added yet",
                 bg=BG, fg=FG2, font=ui_font(14)).pack()
        tk.Label(self._empty,
                 text='Drag videos here, or click  "+ Add files"  /  "+ Add folder"',
                 bg=BG, fg=FG2, font=ui_font(10)).pack(pady=8)
        self._empty.pack(fill="both", expand=True)

        # file table (hidden until files are added)
        self._tf = tk.Frame(self, bg=BG)
        cols = ("#","ext","filename","duration","size","path")
        self.tree = ttk.Treeview(self._tf, columns=cols,
                                 show="headings", selectmode="extended")

        specs = [
            ("#",        "#",        44,  "center", False),
            ("ext",      "Type",     68,  "center", False),
            ("filename", "File name",240, "w",      True),
            ("duration", "Duration", 96,  "center", False),
            ("size",     "Size",     82,  "e",      False),
            ("path",     "Path",     260, "w",      True),
        ]
        for col, heading, w, anchor, stretch in specs:
            self.tree.heading(col, text=heading, anchor=anchor)
            self.tree.column(col, width=w, minwidth=max(40,w//2),
                             stretch=stretch, anchor=anchor)

        vsb = ttk.Scrollbar(self._tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<Button-3>", self._right_click)
        self.tree.bind("<Delete>",   lambda e: self.remove_selected())

        self._ctx = tk.Menu(self, tearoff=0, bg=BG3, fg=FG,
                            activebackground=ACCENT, activeforeground="#fff",
                            relief="flat", bd=1)
        self._ctx.add_command(label="  Remove selected",       command=self.remove_selected)
        self._ctx.add_command(label="  Open containing folder",command=self._open_folder)

        # stats bar (always visible at bottom)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", side="bottom")
        sb = tk.Frame(self, bg=BG2, padx=16, pady=11)
        sb.pack(fill="x", side="bottom")

        self._s_total = self._stat_card(sb, "Total duration", "—",    GREEN)
        self._s_total.pack(side="left", padx=(0,6))
        tk.Frame(sb, bg=BORDER, width=1).pack(side="left", fill="y", pady=2, padx=6)
        self._s_count = self._stat_card(sb, "Files",          "0",    ACCENT2)
        self._s_count.pack(side="left", padx=(0,6))
        tk.Frame(sb, bg=BORDER, width=1).pack(side="left", fill="y", pady=2, padx=6)
        self._s_avg   = self._stat_card(sb, "Average",        "—",    AMBER)
        self._s_avg.pack(side="left", padx=(0,6))
        tk.Frame(sb, bg=BORDER, width=1).pack(side="left", fill="y", pady=2, padx=6)
        self._s_size  = self._stat_card(sb, "Total size",     "—",    FG2)
        self._s_size.pack(side="left")

        right_sb = tk.Frame(sb, bg=BG2)
        right_sb.pack(side="right")
        self._status_var = tk.StringVar(value="Ready")
        tk.Label(right_sb, textvariable=self._status_var,
                 bg=BG2, fg=FG2, font=ui_font(10)).pack(anchor="e")
        self._prog_var = tk.DoubleVar(value=0)
        self._prog = ttk.Progressbar(right_sb, variable=self._prog_var,
                                     maximum=100, length=200, mode="determinate")

    def _stat_card(self, parent, label, val, color):
        f = tk.Frame(parent, bg=BG2)
        tk.Label(f, text=label, bg=BG2, fg=FG2, font=ui_font(9)).pack(anchor="w")
        v = tk.Label(f, text=val, bg=BG2, fg=color, font=ui_font(13, "bold"))
        v.pack(anchor="w")
        f._v = v
        return f

    def _set_stat(self, card, val):
        card._v.config(text=val)

    # ── visibility ────────────────────────────────────────────────────────────
    def _show_table(self, show):
        if show:
            self._empty.pack_forget()
            self._tf.pack(fill="both", expand=True)
        else:
            self._tf.pack_forget()
            self._empty.pack(fill="both", expand=True)

    # ── actions ───────────────────────────────────────────────────────────────
    def add_files(self):
        dlg = FileBrowser(self, start_dir=self._last_dir, mode="files")
        self.wait_window(dlg)
        if dlg.result:
            self._last_dir = os.path.dirname(dlg.result[0])
            self._load_files(dlg.result)

    def add_folder(self):
        dlg = FileBrowser(self, start_dir=self._last_dir, mode="folder")
        self.wait_window(dlg)
        if dlg.result:
            folder = dlg.result[0]
            self._last_dir = folder
            paths = self._video_files_in_folder(folder)
            if not paths:
                messagebox.showinfo("No videos",
                    "No supported video files found in that folder.",
                    parent=self)
                return
            self._load_files(paths)

    def _enable_drag_drop(self):
        if not TKDND_AVAILABLE:
            self._status_var.set("Drag and drop needs: python3 -m pip install tkinterdnd2")
            return

        for widget in (self, self._empty, self._tf, self.tree):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop)
            widget.dnd_bind("<<DragEnter>>", self._on_drag_enter)
            widget.dnd_bind("<<DragLeave>>", self._on_drag_leave)
        self._status_var.set("Ready - drag videos or folders here")

    def _on_drag_enter(self, event):
        self._status_var.set("Drop to add videos")
        return event.action

    def _on_drag_leave(self, event):
        self._status_var.set("Ready - drag videos or folders here")
        return event.action

    def _on_drop(self, event):
        paths = self._video_files_from_paths(self._drop_paths(event.data))
        if paths:
            self._last_dir = os.path.dirname(paths[0])
            self._load_files(paths)
            self._status_var.set(f"Added {len(paths)} dropped item(s)")
        else:
            self._status_var.set("No supported video files in drop")
        return event.action

    def _drop_paths(self, data):
        paths = []
        for item in self.tk.splitlist(data):
            if item.startswith("file://"):
                parsed = urlparse(item)
                item = unquote(parsed.path)
            paths.append(os.path.realpath(item))
        return paths

    def _video_files_from_paths(self, paths):
        videos = []
        for path in paths:
            path = os.path.realpath(path)
            if os.path.isdir(path):
                videos.extend(self._video_files_in_folder(path))
            elif os.path.splitext(path)[1].lower() in VIDEO_EXTS:
                videos.append(path)
        return videos

    def _video_files_in_folder(self, folder):
        videos = []
        try:
            for root, _, files in os.walk(folder):
                for filename in files:
                    if os.path.splitext(filename)[1].lower() in VIDEO_EXTS:
                        videos.append(os.path.join(root, filename))
        except Exception:
            return []
        return sorted(videos)

    def _load_files(self, paths):
        new = [p for p in paths if p not in self._files]
        if not new:
            return
        self._show_table(True)
        self._prog.pack(anchor="e", pady=(4,0))
        self._status_var.set(f"Reading 0 / {len(new)}…")
        threading.Thread(target=self._read_durations,
                         args=(new,), daemon=True).start()

    def _read_durations(self, paths):
        total = len(paths)
        for i, p in enumerate(paths):
            dur = get_duration(p)
            try:   sz = os.path.getsize(p)
            except: sz = 0
            self._files[p] = dur
            self._sizes[p] = sz
            self.after(0, self._add_row, p, os.path.basename(p), dur, sz)
            self.after(0, self._prog_var.set, (i+1)/total*100)
            self.after(0, self._status_var.set, f"Reading {i+1} / {total}…")
        self.after(0, self._refresh_stats)
        self.after(0, self._status_var.set, f"Done — {len(self._files)} file(s)")
        self.after(700, self._prog.pack_forget)
        self.after(700, self._prog_var.set, 0)

    def _add_row(self, path, name, dur, size):
        ext  = os.path.splitext(name)[1].lower()
        n    = len(self.tree.get_children()) + 1
        ok   = dur > 0
        rtag = "rowa" if n % 2 == 1 else "rowb"
        stag = "ok" if ok else "err"
        iid = self.tree.insert("", "end", tags=(stag, rtag), values=(
            n,
            ext.lstrip(".").upper() or "?",
            display_text(name),
            fmt_dur(dur) if ok else "error",
            fmt_size(size) if size else "—",
            display_text(path),
        ))
        self._row_paths[iid] = path
        self._row_names[iid] = name
        self.tree.tag_configure("ok",   foreground=FG)
        self.tree.tag_configure("err",  foreground=RED)
        self.tree.tag_configure("rowa", background=ROW_A)
        self.tree.tag_configure("rowb", background=ROW_B)
        self.tree.yview_moveto(1.0)

    def remove_selected(self):
        for iid in self.tree.selection():
            path = self._row_paths.get(iid)
            if not path:
                continue
            self._files.pop(path, None)
            self._sizes.pop(path, None)
            self._row_paths.pop(iid, None)
            self._row_names.pop(iid, None)
            self.tree.delete(iid)
        self._renumber()
        self._refresh_stats()

    def clear_all(self):
        self.tree.delete(*self.tree.get_children())
        self._files.clear()
        self._sizes.clear()
        self._row_paths.clear()
        self._row_names.clear()
        self._refresh_stats()
        self._status_var.set("Cleared.")

    def _renumber(self):
        for i, iid in enumerate(self.tree.get_children(), 1):
            vals    = list(self.tree.item(iid, "values"))
            vals[0] = i
            rtag    = "rowa" if i % 2 == 1 else "rowb"
            old     = [t for t in self.tree.item(iid,"tags")
                       if t not in ("rowa","rowb")]
            self.tree.item(iid, values=vals, tags=old+[rtag])

    def _refresh_stats(self):
        total = sum(self._files.values())
        count = len(self._files)
        tsize = sum(self._sizes.values())
        if count:
            self._set_stat(self._s_total, fmt_dur(total))
            self._set_stat(self._s_count, str(count))
            self._set_stat(self._s_avg,   fmt_dur(total / count))
            self._set_stat(self._s_size,  fmt_size(tsize))
        else:
            for card, val in [(self._s_total,"—"),(self._s_count,"0"),
                              (self._s_avg,"—"),(self._s_size,"—")]:
                self._set_stat(card, val)
            self._show_table(False)

    def _apply_search(self):
        q = self._search_var.get().lower()
        for iid, path in self._row_paths.items():
            name = self._row_names.get(iid, "")
            path = path.lower()
            name = name.lower()
            if q and q not in name and q not in path:
                self.tree.detach(iid)
            else:
                try: self.tree.reattach(iid, "", "end")
                except Exception: pass

    def _right_click(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            if row not in self.tree.selection():
                self.tree.selection_set(row)
            self._ctx.post(event.x_root, event.y_root)

    def _open_folder(self):
        sel = self.tree.selection()
        if sel:
            path = self._row_paths.get(sel[0])
            if path:
                subprocess.Popen(["xdg-open", os.path.dirname(path)])


if __name__ == "__main__":
    App().mainloop()
