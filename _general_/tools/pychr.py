import os
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk

# ---------------------------------------------------------
# 1. GRAPHICS CODECS (ENCODE / DECODE 8x8 TILES)
# ---------------------------------------------------------

class Codec:
    bytes_per_tile = 16
    max_colors = 4

    @staticmethod
    def decode(data: bytes) -> list[list[int]]:
        raise NotImplementedError

    @staticmethod
    def encode(tile: list[list[int]]) -> bytes:
        raise NotImplementedError


class NES2BPP(Codec):
    bytes_per_tile = 16
    max_colors = 4

    @staticmethod
    def decode(data: bytes) -> list[list[int]]:
        tile = [[0] * 8 for _ in range(8)]
        for y in range(8):
            p0 = data[y]
            p1 = data[y + 8]
            for x in range(8):
                bit = 7 - x
                tile[y][x] = ((p0 >> bit) & 1) | (((p1 >> bit) & 1) << 1)
        return tile

    @staticmethod
    def encode(tile: list[list[int]]) -> bytes:
        out = bytearray(16)
        for y in range(8):
            p0 = p1 = 0
            for x in range(8):
                c = tile[y][x]
                bit = 7 - x
                p0 |= (c & 1) << bit
                p1 |= ((c >> 1) & 1) << bit
            out[y] = p0
            out[y + 8] = p1
        return bytes(out)


class GameBoy2BPP(Codec):
    bytes_per_tile = 16
    max_colors = 4

    @staticmethod
    def decode(data: bytes) -> list[list[int]]:
        tile = [[0] * 8 for _ in range(8)]
        for y in range(8):
            p0 = data[y * 2]
            p1 = data[y * 2 + 1]
            for x in range(8):
                bit = 7 - x
                tile[y][x] = ((p0 >> bit) & 1) | (((p1 >> bit) & 1) << 1)
        return tile

    @staticmethod
    def encode(tile: list[list[int]]) -> bytes:
        out = bytearray(16)
        for y in range(8):
            p0 = p1 = 0
            for x in range(8):
                c = tile[y][x]
                bit = 7 - x
                p0 |= (c & 1) << bit
                p1 |= ((c >> 1) & 1) << bit
            out[y * 2] = p0
            out[y * 2 + 1] = p1
        return bytes(out)


class Genesis4BPP(Codec):
    bytes_per_tile = 32
    max_colors = 16

    @staticmethod
    def decode(data: bytes) -> list[list[int]]:
        tile = [[0] * 8 for _ in range(8)]
        for y in range(8):
            for x in range(8):
                b = data[y * 4 + (x // 2)]
                tile[y][x] = (b >> 4) & 0x0F if (x % 2 == 0) else (b & 0x0F)
        return tile

    @staticmethod
    def encode(tile: list[list[int]]) -> bytes:
        out = bytearray(32)
        for y in range(8):
            for i in range(4):
                hi = tile[y][i * 2] & 0x0F
                lo = tile[y][i * 2 + 1] & 0x0F
                out[y * 4 + i] = (hi << 4) | lo
        return bytes(out)


class SNES4BPP(Codec):
    bytes_per_tile = 32
    max_colors = 16

    @staticmethod
    def decode(data: bytes) -> list[list[int]]:
        tile = [[0] * 8 for _ in range(8)]
        for y in range(8):
            p0 = data[y * 2]
            p1 = data[y * 2 + 1]
            p2 = data[16 + y * 2]
            p3 = data[16 + y * 2 + 1]
            for x in range(8):
                bit = 7 - x
                b0 = (p0 >> bit) & 1
                b1 = (p1 >> bit) & 1
                b2 = (p2 >> bit) & 1
                b3 = (p3 >> bit) & 1
                tile[y][x] = b0 | (b1 << 1) | (b2 << 2) | (b3 << 3)
        return tile

    @staticmethod
    def encode(tile: list[list[int]]) -> bytes:
        out = bytearray(32)
        for y in range(8):
            p0 = p1 = p2 = p3 = 0
            for x in range(8):
                bit = 7 - x
                c = tile[y][x]
                p0 |= (c & 1) << bit
                p1 |= ((c >> 1) & 1) << bit
                p2 |= ((c >> 2) & 1) << bit
                p3 |= ((c >> 3) & 1) << bit
            out[y * 2] = p0
            out[y * 2 + 1] = p1
            out[16 + y * 2] = p2
            out[16 + y * 2 + 1] = p3
        return bytes(out)


FORMATS = {
    "NES 2BPP": NES2BPP,
    "Game Boy 2BPP": GameBoy2BPP,
    "SNES 4BPP": SNES4BPP,
    "Genesis 4BPP": Genesis4BPP,
}

# ---------------------------------------------------------
# 2. PALETTE PRESETS (4-color and 16-color)
# ---------------------------------------------------------

PRESET_PALETTES = {
    "Grayscale": {
        4: [(0, 0, 0), (96, 96, 96), (170, 170, 170), (255, 255, 255)],
        16: [(int(i * 17), int(i * 17), int(i * 17)) for i in range(16)],
    },
    "Game Boy Classic (DMG)": {
        4: [(15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)],
        16: [(int(i * 10), int(i * 15), int(i * 10)) for i in range(16)],
    },
    "Game Boy Pocket": {
        4: [(20, 20, 20), (84, 84, 84), (160, 160, 160), (248, 248, 248)],
        16: [(int(i * 17), int(i * 17), int(i * 17)) for i in range(16)],
    },
    "NES Overworld (Mario)": {
        4: [(96, 160, 248), (0, 168, 0), (224, 136, 0), (184, 96, 0)],
        16: [(0, 0, 0)] * 16,
    },
    "NES Dungeon / Castle": {
        4: [(0, 0, 0), (120, 120, 120), (0, 88, 248), (248, 248, 248)],
        16: [(0, 0, 0)] * 16,
    },
    "NES Fire / Lava": {
        4: [(0, 0, 0), (184, 0, 0), (248, 88, 0), (248, 184, 0)],
        16: [(0, 0, 0)] * 16,
    },
    "Cyberpunk Neon": {
        4: [(13, 12, 29), (48, 32, 128), (234, 0, 217), (255, 255, 255)],
        16: [(int(i * 16), int(i * 8), int(i * 16)) for i in range(16)],
    },
    "SNES / Genesis Vibrant (16c)": {
        4: [(0, 0, 0), (96, 96, 96), (170, 170, 170), (255, 255, 255)],
        16: [
            (0, 0, 0), (24, 24, 88), (104, 32, 32), (152, 32, 32),
            (0, 104, 32), (0, 168, 64), (168, 112, 0), (248, 168, 56),
            (48, 48, 168), (104, 104, 248), (168, 48, 168), (248, 112, 248),
            (0, 168, 168), (112, 248, 248), (184, 184, 184), (255, 255, 255),
        ],
    },
}

# ---------------------------------------------------------
# 3. MAIN GUI APPLICATION
# ---------------------------------------------------------

class RetroTileEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyCHR - Advanced Retro ROM Graphics Editor")
        self.geometry("980x640")
        self.minsize(900, 600)

        # ROM & Data state
        self.rom_data: bytearray | None = None
        self.rom_path: str | None = None
        self.current_offset = 0
        self.codec: type[Codec] = NES2BPP
        self.active_color = 1
        self.selected_tile_idx = 0
        self.active_tile = [[0] * 8 for _ in range(8)]

        # Layout & View configuration
        self.cols_mode = tk.IntVar(value=16)     # Tiles per row (16, 20, 32, 40)
        self.rows_mode = 16                      # Rows displayed per page
        self.arrange_mode = tk.StringVar(value="Linear (1x1)")
        self.sheet_zoom = 2
        self.editor_zoom = 32

        # Active palette buffer
        self.current_palette = list(PRESET_PALETTES["Grayscale"][4])

        self._build_ui()
        self._set_empty_state()

    def _build_ui(self):
        # Top Toolbar 1: File & Codec
        bar1 = ttk.Frame(self, padding=4)
        bar1.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(bar1, text="Open ROM", command=self.open_rom).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar1, text="Save ROM", command=self.save_rom).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar1, text="Save As...", command=self.save_rom_as).pack(side=tk.LEFT, padx=2)

        ttk.Separator(bar1, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Label(bar1, text="Format:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="NES 2BPP")
        format_cb = ttk.Combobox(bar1, textvariable=self.format_var, values=list(FORMATS.keys()), state="readonly", width=14)
        format_cb.pack(side=tk.LEFT, padx=3)
        format_cb.bind("<<ComboboxSelected>>", self._on_format_changed)

        ttk.Separator(bar1, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Label(bar1, text="Offset:").pack(side=tk.LEFT)
        self.offset_entry = ttk.Entry(bar1, width=9)
        self.offset_entry.pack(side=tk.LEFT, padx=2)
        self.offset_entry.insert(0, "0x00000")
        self.offset_entry.bind("<Return>", lambda e: self._jump_offset())

        ttk.Button(bar1, text="Go", width=3, command=self._jump_offset).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar1, text="◀ Prev", command=self._page_prev).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar1, text="Next ▶", command=self._page_next).pack(side=tk.LEFT, padx=2)

        # Top Toolbar 2: Screen Layout & Arrangement
        bar2 = ttk.Frame(self, padding=4)
        bar2.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(bar2, text="Screen Width:").pack(side=tk.LEFT)
        self.layout_cb = ttk.Combobox(
            bar2,
            values=[
                "16 Tiles (128px - YY-CHR Default)",
                "20 Tiles (160px - Game Boy Screen)",
                "32 Tiles (256px - NES/SNES Screen)",
                "40 Tiles (320px - Genesis Screen)",
            ],
            state="readonly",
            width=32,
        )
        self.layout_cb.current(0)
        self.layout_cb.pack(side=tk.LEFT, padx=3)
        self.layout_cb.bind("<<ComboboxSelected>>", self._on_layout_changed)

        ttk.Label(bar2, text="Arrangement:").pack(side=tk.LEFT, padx=(6, 0))
        self.arrange_cb = ttk.Combobox(
            bar2,
            textvariable=self.arrange_mode,
            values=["Linear (1x1)", "8x16 Sprite (1x2)", "16x16 Sprite (2x2)"],
            state="readonly",
            width=18,
        )
        self.arrange_cb.pack(side=tk.LEFT, padx=3)
        self.arrange_cb.bind("<<ComboboxSelected>>", lambda e: self._load_current_page())

        ttk.Label(bar2, text="Zoom:").pack(side=tk.LEFT, padx=(6, 0))
        self.zoom_cb = ttk.Combobox(bar2, values=["1x", "2x", "3x"], state="readonly", width=4)
        self.zoom_cb.current(1)
        self.zoom_cb.pack(side=tk.LEFT, padx=3)
        self.zoom_cb.bind("<<ComboboxSelected>>", self._on_zoom_changed)

        # Main Workspace
        main_frame = ttk.Frame(self, padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left: Scrollable Tile Sheet
        left_frame = ttk.LabelFrame(main_frame, text="ROM Tile Sheet Viewer", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

        sheet_container = ttk.Frame(left_frame)
        sheet_container.pack(fill=tk.BOTH, expand=True)

        self.sheet_canvas = tk.Canvas(sheet_container, bg="#1c1c1c", highlightthickness=0)
        self.vbar = ttk.Scrollbar(sheet_container, orient=tk.VERTICAL, command=self.sheet_canvas.yview)
        self.hbar = ttk.Scrollbar(sheet_container, orient=tk.HORIZONTAL, command=self.sheet_canvas.xview)
        self.sheet_canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.sheet_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sheet_canvas.bind("<Button-1>", self._on_sheet_clicked)

        self.lbl_tile_info = ttk.Label(left_frame, text="Selected Tile: #0 | ROM Offset: 0x00000")
        self.lbl_tile_info.pack(anchor=tk.W, pady=3)

        # Right: 8x8 Tile Editor & Palette Controls
        right_frame = ttk.LabelFrame(main_frame, text="Tile Editor & Palette", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=4)

        self.editor_canvas = tk.Canvas(right_frame, width=256, height=256, bg="#111", highlightthickness=1)
        self.editor_canvas.pack(pady=4)
        self.editor_canvas.bind("<Button-1>", self._on_paint)
        self.editor_canvas.bind("<B1-Motion>", self._on_paint)
        self.editor_canvas.bind("<Button-3>", self._on_pick_color)

        ttk.Label(right_frame, text="Tip: Left-click draw, Right-click sample color", font=("TkDefaultFont", 8)).pack()

        # Palette Settings Frame
        pal_box = ttk.LabelFrame(right_frame, text="Palette Controls", padding=5)
        pal_box.pack(fill=tk.X, pady=8)

        ttk.Label(pal_box, text="Preset:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pal_preset_var = tk.StringVar(value="Grayscale")
        self.pal_preset_cb = ttk.Combobox(
            pal_box, textvariable=self.pal_preset_var, values=list(PRESET_PALETTES.keys()), state="readonly", width=22
        )
        self.pal_preset_cb.grid(row=0, column=1, sticky=tk.W, pady=2)
        self.pal_preset_cb.bind("<<ComboboxSelected>>", self._on_palette_preset_changed)

        ttk.Label(pal_box, text="Colors (Click: select | Right-click: edit):").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(6, 2))

        self.pal_swatches_frame = ttk.Frame(pal_box)
        self.pal_swatches_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)

        btn_edit_color = ttk.Button(pal_box, text="Customize Active Color...", command=self._edit_active_color)
        btn_edit_color.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=4)

    def _set_empty_state(self):
        self._rebuild_palette_ui()
        self._render_editor()

    # -----------------------------------------------------
    # LAYOUT & COORDINATE MAPPING
    # -----------------------------------------------------

    def _get_page_tile_count(self) -> int:
        cols = self.cols_mode.get()
        return cols * self.rows_mode

    def _page_size_bytes(self) -> int:
        return self._get_page_tile_count() * self.codec.bytes_per_tile

    def _tile_idx_to_grid(self, t_idx: int) -> tuple[int, int]:
        """Maps sequential tile index to (col, row) on the sheet based on arrangement."""
        cols = self.cols_mode.get()
        mode = self.arrange_mode.get()

        if mode == "8x16 Sprite (1x2)":
            block_idx = t_idx // 2
            sub = t_idx % 2
            b_col = block_idx % cols
            b_row = block_idx // cols
            return b_col, b_row * 2 + sub

        elif mode == "16x16 Sprite (2x2)":
            meta_cols = max(1, cols // 2)
            meta_idx = t_idx // 4
            sub = t_idx % 4  # 0: TL, 1: TR, 2: BL, 3: BR
            m_col = meta_idx % meta_cols
            m_row = meta_idx // meta_cols
            return m_col * 2 + (sub % 2), m_row * 2 + (sub // 2)

        # Default: Linear (1x1)
        return t_idx % cols, t_idx // cols

    def _grid_to_tile_idx(self, col: int, row: int) -> int:
        """Reverse maps (col, row) on the sheet back to sequential tile index."""
        cols = self.cols_mode.get()
        mode = self.arrange_mode.get()

        if mode == "8x16 Sprite (1x2)":
            b_col = col
            b_row = row // 2
            sub = row % 2
            return (b_row * cols + b_col) * 2 + sub

        elif mode == "16x16 Sprite (2x2)":
            meta_cols = max(1, cols // 2)
            m_col = col // 2
            m_row = row // 2
            sub = (row % 2) * 2 + (col % 2)
            return (m_row * meta_cols + m_col) * 4 + sub

        return row * cols + col

    # -----------------------------------------------------
    # PALETTE MANAGEMENT
    # -----------------------------------------------------

    def _on_palette_preset_changed(self, event=None):
        name = self.pal_preset_var.get()
        num_colors = self.codec.max_colors
        preset = PRESET_PALETTES.get(name, {}).get(num_colors)
        if preset:
            self.current_palette = list(preset)
        else:
            self.current_palette = list(PRESET_PALETTES["Grayscale"][num_colors])

        self._rebuild_palette_ui()
        self._load_current_page()
        self._render_editor()

    def _rebuild_palette_ui(self):
        for w in self.pal_swatches_frame.winfo_children():
            w.destroy()

        for idx, (r, g, b) in enumerate(self.current_palette):
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            btn = tk.Button(
                self.pal_swatches_frame,
                bg=hex_color,
                activebackground=hex_color,
                width=2,
                relief=tk.SUNKEN if idx == self.active_color else tk.RAISED,
                bd=3 if idx == self.active_color else 1,
                command=lambda c=idx: self._select_color(c),
            )
            # Right-click or double-click to customize this color slot
            btn.bind("<Button-3>", lambda e, c=idx: self._edit_color_slot(c))
            btn.bind("<Double-Button-1>", lambda e, c=idx: self._edit_color_slot(c))
            btn.pack(side=tk.LEFT, padx=1)

    def _select_color(self, c_idx: int):
        self.active_color = c_idx
        self._rebuild_palette_ui()

    def _edit_active_color(self):
        self._edit_color_slot(self.active_color)

    def _edit_color_slot(self, c_idx: int):
        cur_r, cur_g, cur_b = self.current_palette[c_idx]
        cur_hex = f"#{cur_r:02x}{cur_g:02x}{cur_b:02x}"
        chosen, _ = colorchooser.askcolor(cur_hex, title=f"Choose Color for Index {c_idx}")
        if chosen:
            r, g, b = [int(v) for v in chosen]
            self.current_palette[c_idx] = (r, g, b)
            self._rebuild_palette_ui()
            self._load_current_page()
            self._render_editor()

    # -----------------------------------------------------
    # FILE OPERATIONS
    # -----------------------------------------------------

    def open_rom(self):
        path = filedialog.askopenfilename(
            filetypes=[("ROM files", "*.nes;*.gb;*.gbc;*.sfc;*.smc;*.bin;*.md"), ("All files", "*.*")]
        )
        if not path:
            return
        with open(path, "rb") as f:
            self.rom_data = bytearray(f.read())
        self.rom_path = path
        self.current_offset = 0
        self.selected_tile_idx = 0
        self._update_offset_entry()
        self.title(f"PyCHR - {os.path.basename(path)}")
        self._load_current_page()

    def save_rom(self):
        if not self.rom_data or not self.rom_path:
            return
        with open(self.rom_path, "wb") as f:
            f.write(self.rom_data)
        messagebox.showinfo("Saved", "ROM changes saved successfully!")

    def save_rom_as(self):
        if not self.rom_data:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".rom",
            filetypes=[("ROM files", "*.nes;*.gb;*.gbc;*.sfc;*.smc;*.bin;*.md"), ("All files", "*.*")],
        )
        if not path:
            return
        self.rom_path = path
        self.save_rom()
        self.title(f"PyCHR - {os.path.basename(path)}")

    # -----------------------------------------------------
    # NAVIGATION & VIEW UPDATES
    # -----------------------------------------------------

    def _on_format_changed(self, event=None):
        self.codec = FORMATS[self.format_var.get()]
        self.active_color = min(self.active_color, self.codec.max_colors - 1)
        self._on_palette_preset_changed()

    def _on_layout_changed(self, event=None):
        raw = self.layout_cb.get()
        if "16 Tiles" in raw:
            self.cols_mode.set(16)
        elif "20 Tiles" in raw:
            self.cols_mode.set(20)
        elif "32 Tiles" in raw:
            self.cols_mode.set(32)
        elif "40 Tiles" in raw:
            self.cols_mode.set(40)
        self._load_current_page()

    def _on_zoom_changed(self, event=None):
        z_str = self.zoom_cb.get()
        self.sheet_zoom = int(z_str[0])
        self._load_current_page()

    def _page_prev(self):
        if not self.rom_data:
            return
        self.current_offset = max(0, self.current_offset - self._page_size_bytes())
        self._update_offset_entry()
        self._load_current_page()

    def _page_next(self):
        if not self.rom_data:
            return
        max_offset = max(0, len(self.rom_data) - self.codec.bytes_per_tile)
        self.current_offset = min(max_offset, self.current_offset + self._page_size_bytes())
        self._update_offset_entry()
        self._load_current_page()

    def _jump_offset(self):
        if not self.rom_data:
            return
        try:
            val = int(self.offset_entry.get(), 16)
            self.current_offset = max(0, min(val, len(self.rom_data) - self.codec.bytes_per_tile))
            self._load_current_page()
        except ValueError:
            self._update_offset_entry()

    def _update_offset_entry(self):
        self.offset_entry.delete(0, tk.END)
        self.offset_entry.insert(0, f"0x{self.current_offset:05X}")

    # -----------------------------------------------------
    # RENDERING & INTERACTION
    # -----------------------------------------------------

    def _load_current_page(self):
        if not self.rom_data:
            return

        bpt = self.codec.bytes_per_tile
        total_tiles = self._get_page_tile_count()
        cols = self.cols_mode.get()
        rows = self.rows_mode

        img_w = cols * 8
        img_h = rows * 8
        sheet_rgb = bytearray(img_w * img_h * 3)

        for t_idx in range(total_tiles):
            offset = self.current_offset + t_idx * bpt
            if offset + bpt <= len(self.rom_data):
                raw = self.rom_data[offset : offset + bpt]
            else:
                raw = bytes(bpt)

            tile = self.codec.decode(raw)
            grid_col, grid_row = self._tile_idx_to_grid(t_idx)
            tile_tx = grid_col * 8
            tile_ty = grid_row * 8

            if tile_ty + 8 > img_h:
                continue

            for y in range(8):
                row_base = (tile_ty + y) * img_w
                for x in range(8):
                    c_idx = tile[y][x]
                    r, g, b = self.current_palette[c_idx]
                    idx = (row_base + (tile_tx + x)) * 3
                    sheet_rgb[idx] = r
                    sheet_rgb[idx + 1] = g
                    sheet_rgb[idx + 2] = b

        ppm = f"P6\n{img_w} {img_h}\n255\n".encode("ascii") + sheet_rgb
        self.sheet_img = tk.PhotoImage(data=ppm).zoom(self.sheet_zoom, self.sheet_zoom)

        scaled_w = img_w * self.sheet_zoom
        scaled_h = img_h * self.sheet_zoom

        self.sheet_canvas.delete("all")
        self.sheet_canvas.config(scrollregion=(0, 0, scaled_w, scaled_h))
        self.sheet_canvas.create_image(0, 0, anchor=tk.NW, image=self.sheet_img)

        self._draw_sheet_cursor()
        self._load_active_tile()

    def _draw_sheet_cursor(self):
        self.sheet_canvas.delete("cursor")
        grid_col, grid_row = self._tile_idx_to_grid(self.selected_tile_idx)
        sz = 8 * self.sheet_zoom
        tx = grid_col * sz
        ty = grid_row * sz
        self.sheet_canvas.create_rectangle(tx, ty, tx + sz, ty + sz, outline="#FF1111", width=2, tags="cursor")

    def _load_active_tile(self):
        bpt = self.codec.bytes_per_tile
        rom_addr = self.current_offset + self.selected_tile_idx * bpt
        if self.rom_data and rom_addr + bpt <= len(self.rom_data):
            self.active_tile = self.codec.decode(self.rom_data[rom_addr : rom_addr + bpt])
        else:
            self.active_tile = [[0] * 8 for _ in range(8)]

        self.lbl_tile_info.config(text=f"Tile: #{self.selected_tile_idx} | ROM Offset: 0x{rom_addr:05X}")
        self._render_editor()

    def _render_editor(self):
        self.editor_canvas.delete("all")
        scale = self.editor_zoom

        for y in range(8):
            for x in range(8):
                c_idx = self.active_tile[y][x]
                r, g, b = self.current_palette[c_idx]
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                self.editor_canvas.create_rectangle(
                    x * scale, y * scale, (x + 1) * scale, (y + 1) * scale, fill=hex_color, outline="#2b2b2b"
                )

    def _on_sheet_clicked(self, event):
        # Translate viewport mouse coordinates to virtual canvas coordinates
        cx = self.sheet_canvas.canvasx(event.x)
        cy = self.sheet_canvas.canvasy(event.y)

        tile_size = 8 * self.sheet_zoom
        col = int(cx // tile_size)
        row = int(cy // tile_size)

        cols = self.cols_mode.get()
        if 0 <= col < cols and 0 <= row < self.rows_mode:
            self.selected_tile_idx = self._grid_to_tile_idx(col, row)
            self._draw_sheet_cursor()
            self._load_active_tile()

    def _on_paint(self, event):
        if not self.rom_data:
            return
        x = event.x // self.editor_zoom
        y = event.y // self.editor_zoom
        if 0 <= x < 8 and 0 <= y < 8:
            if self.active_tile[y][x] != self.active_color:
                self.active_tile[y][x] = self.active_color
                self._save_active_tile_to_rom()
                self._render_editor()
                self._update_tile_in_sheet()

    def _on_pick_color(self, event):
        x = event.x // self.editor_zoom
        y = event.y // self.editor_zoom
        if 0 <= x < 8 and 0 <= y < 8:
            self.active_color = self.active_tile[y][x]
            self._rebuild_palette_ui()

    def _save_active_tile_to_rom(self):
        bpt = self.codec.bytes_per_tile
        rom_addr = self.current_offset + self.selected_tile_idx * bpt
        if rom_addr + bpt <= len(self.rom_data):
            encoded = self.codec.encode(self.active_tile)
            self.rom_data[rom_addr : rom_addr + bpt] = encoded

    def _update_tile_in_sheet(self):
        grid_col, grid_row = self._tile_idx_to_grid(self.selected_tile_idx)
        sz = 8 * self.sheet_zoom
        tx = grid_col * sz
        ty = grid_row * sz

        # Redraw individual tile preview
        for y in range(8):
            for x in range(8):
                r, g, b = self.current_palette[self.active_tile[y][x]]
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                self.sheet_canvas.create_rectangle(
                    tx + x * self.sheet_zoom,
                    ty + y * self.sheet_zoom,
                    tx + (x + 1) * self.sheet_zoom,
                    ty + (y + 1) * self.sheet_zoom,
                    fill=hex_color,
                    outline="",
                )
        self._draw_sheet_cursor()


if __name__ == "__main__":
    app = RetroTileEditor()
    app.mainloop()