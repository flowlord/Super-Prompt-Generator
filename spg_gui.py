"""
Interface graphique SPG.

Lancement :
python spg_gui.py
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional, Sequence

from main import (
    APP_DIR,
    DEFAULT_STYLE_FILE,
    Constraints,
    PromptOptions,
    _canon,
    build_choice_fields,
    build_output,
    generate_prompts,
)

APP_TITLE = "SPG — Script Prompt Generator"
RANDOM_LABEL = "random"


class PromptGeneratorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x760")
        self.minsize(960, 620)

        self.style_file_var = tk.StringVar(value=str(DEFAULT_STYLE_FILE))
        self.num_var = tk.StringVar(value="3")
        self.min_age_var = tk.StringVar(value="18")
        self.max_age_var = tk.StringVar(value="45")
        self.seed_var = tk.StringVar(value="")
        self.mode_var = tk.StringVar(value="fixed")
        self.nationality_var = tk.StringVar(value="french")
        self.human_only_var = tk.BooleanVar(value=True)
        self.copy_after_generate_var = tk.BooleanVar(value=True)
        self.sex_var = tk.StringVar(value=RANDOM_LABEL)
        self.phenotype_var = tk.StringVar(value=RANDOM_LABEL)
        self.action_var = tk.StringVar(value=RANDOM_LABEL)
        self.style_var = tk.StringVar(value=RANDOM_LABEL)
        self.status_var = tk.StringVar(value="Prêt.")

        self.choice_fields = build_choice_fields(self.style_file_var.get())
        self._configure_style()
        self._build_layout()
        self._refresh_comboboxes()

    def _configure_style(self) -> None:
        self.configure(bg="#111318")
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background="#111318")
        style.configure("Panel.TFrame", background="#181b22", relief="flat")
        style.configure("App.TLabel", background="#181b22", foreground="#f2f4f8", font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background="#181b22", foreground="#aeb6c2", font=("Segoe UI", 9))
        style.configure("Title.TLabel", background="#181b22", foreground="#ffffff", font=("Segoe UI", 18, "bold"))
        style.configure("Section.TLabel", background="#181b22", foreground="#ffffff", font=("Segoe UI", 11, "bold"))
        style.configure("Status.TLabel", background="#111318", foreground="#aeb6c2", font=("Segoe UI", 9))
        style.configure("App.TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 9))
        style.configure("App.TCheckbutton", background="#181b22", foreground="#f2f4f8", font=("Segoe UI", 10))
        style.configure("App.TRadiobutton", background="#181b22", foreground="#f2f4f8", font=("Segoe UI", 10))
        style.configure("App.TEntry", fieldbackground="#f8fafc")
        style.configure("App.TCombobox", fieldbackground="#f8fafc")

    def _build_layout(self) -> None:
        container = ttk.Frame(self, style="App.TFrame", padding=16)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(container, style="Panel.TFrame", padding=18)
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        sidebar.columnconfigure(0, weight=1)

        main_panel = ttk.Frame(container, style="Panel.TFrame", padding=18)
        main_panel.grid(row=0, column=1, sticky="nsew")
        main_panel.columnconfigure(0, weight=1)
        main_panel.rowconfigure(1, weight=1)

        ttk.Label(sidebar, text="SPG Generator", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            sidebar,
            text="Génère des prompts structurés avec nationalité précise ou aléatoire.",
            style="Muted.TLabel",
            wraplength=310,
        ).grid(row=1, column=0, sticky="w", pady=(4, 18))

        row = 2
        row = self._add_section(sidebar, row, "Mode nationalité")
        ttk.Radiobutton(
            sidebar,
            text="Nationalité précise",
            variable=self.mode_var,
            value="fixed",
            style="App.TRadiobutton",
            command=self._sync_nationality_state,
        ).grid(row=row, column=0, sticky="w", pady=2)
        row += 1
        ttk.Radiobutton(
            sidebar,
            text="Nationalité choisie au hasard",
            variable=self.mode_var,
            value="random",
            style="App.TRadiobutton",
            command=self._sync_nationality_state,
        ).grid(row=row, column=0, sticky="w", pady=2)
        row += 1

        ttk.Label(sidebar, text="Nationalité", style="App.TLabel").grid(row=row, column=0, sticky="w", pady=(10, 4))
        row += 1
        self.nationality_combo = ttk.Combobox(
            sidebar,
            textvariable=self.nationality_var,
            state="normal",
            width=34,
            style="App.TCombobox",
        )
        self.nationality_combo.grid(row=row, column=0, sticky="ew")
        self.nationality_combo.bind("<KeyRelease>", self._filter_nationalities)
        row += 1

        row = self._add_section(sidebar, row + 1, "Paramètres")
        row = self._add_labeled_entry(sidebar, row, "Nombre de prompts", self.num_var)
        row = self._add_labeled_entry(sidebar, row, "Âge minimum", self.min_age_var)
        row = self._add_labeled_entry(sidebar, row, "Âge maximum", self.max_age_var)
        row = self._add_labeled_entry(sidebar, row, "Seed optionnelle", self.seed_var)

        ttk.Checkbutton(
            sidebar,
            text="Forcer race=human",
            variable=self.human_only_var,
            style="App.TCheckbutton",
        ).grid(row=row, column=0, sticky="w", pady=(8, 2))
        row += 1
        ttk.Checkbutton(
            sidebar,
            text="Copier après génération",
            variable=self.copy_after_generate_var,
            style="App.TCheckbutton",
        ).grid(row=row, column=0, sticky="w", pady=(2, 12))
        row += 1

        row = self._add_section(sidebar, row, "Filtres optionnels")
        self.sex_combo = self._add_labeled_combo(sidebar, row, "Sexe", self.sex_var)
        row += 2
        self.phenotype_combo = self._add_labeled_combo(sidebar, row, "Phénotype", self.phenotype_var)
        row += 2
        self.action_combo = self._add_labeled_combo(sidebar, row, "Action", self.action_var)
        row += 2
        self.style_combo = self._add_labeled_combo(sidebar, row, "Style", self.style_var)
        row += 2

        row = self._add_section(sidebar, row, "Fichier styles")
        style_line = ttk.Frame(sidebar, style="Panel.TFrame")
        style_line.grid(row=row, column=0, sticky="ew")
        style_line.columnconfigure(0, weight=1)
        ttk.Entry(style_line, textvariable=self.style_file_var, width=26, style="App.TEntry").grid(row=0, column=0, sticky="ew")
        ttk.Button(style_line, text="...", width=4, command=self._choose_style_file, style="App.TButton").grid(row=0, column=1, padx=(6, 0))
        row += 1
        ttk.Button(sidebar, text="Recharger les styles", command=self._reload_styles, style="App.TButton").grid(row=row, column=0, sticky="ew", pady=(8, 14))
        row += 1

        ttk.Button(
            sidebar,
            text="Générer avec nationalité précise",
            command=lambda: self._generate("fixed"),
            style="Primary.TButton",
        ).grid(row=row, column=0, sticky="ew", pady=(0, 8))
        row += 1
        ttk.Button(
            sidebar,
            text="Générer avec nationalité aléatoire",
            command=lambda: self._generate("random"),
            style="Primary.TButton",
        ).grid(row=row, column=0, sticky="ew")

        ttk.Label(main_panel, text="Résultat", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        output_frame = ttk.Frame(main_panel, style="Panel.TFrame")
        output_frame.grid(row=1, column=0, sticky="nsew", pady=(14, 12))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output_text = tk.Text(
            output_frame,
            wrap="word",
            bg="#0b0d12",
            fg="#f8fafc",
            insertbackground="#f8fafc",
            selectbackground="#334155",
            relief="flat",
            padx=16,
            pady=16,
            font=("Consolas", 11),
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(main_panel, style="Panel.TFrame")
        actions.grid(row=2, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        ttk.Button(actions, text="Copier", command=self._copy_output, style="App.TButton").grid(row=0, column=1, padx=(0, 8))
        ttk.Button(actions, text="Exporter .txt", command=self._save_output, style="App.TButton").grid(row=0, column=2, padx=(0, 8))
        ttk.Button(actions, text="Effacer", command=self._clear_output, style="App.TButton").grid(row=0, column=3)

        ttk.Label(self, textvariable=self.status_var, style="Status.TLabel").pack(fill="x", padx=18, pady=(0, 10))
        self._sync_nationality_state()

    def _add_section(self, parent: ttk.Frame, row: int, label: str) -> int:
        ttk.Label(parent, text=label, style="Section.TLabel").grid(row=row, column=0, sticky="w", pady=(14, 8))
        return row + 1

    def _add_labeled_entry(self, parent: ttk.Frame, row: int, label: str, variable: tk.StringVar) -> int:
        ttk.Label(parent, text=label, style="App.TLabel").grid(row=row, column=0, sticky="w", pady=(4, 3))
        row += 1
        ttk.Entry(parent, textvariable=variable, width=34, style="App.TEntry").grid(row=row, column=0, sticky="ew")
        return row + 1

    def _add_labeled_combo(self, parent: ttk.Frame, row: int, label: str, variable: tk.StringVar) -> ttk.Combobox:
        ttk.Label(parent, text=label, style="App.TLabel").grid(row=row, column=0, sticky="w", pady=(4, 3))
        combo = ttk.Combobox(parent, textvariable=variable, state="readonly", width=34, style="App.TCombobox")
        combo.grid(row=row + 1, column=0, sticky="ew")
        return combo

    def _refresh_comboboxes(self) -> None:
        nationalities = sorted(self.choice_fields.get("nationality", []))
        self.nationality_combo.configure(values=nationalities)
        if self.nationality_var.get() not in nationalities and nationalities:
            self.nationality_var.set(nationalities[0])

        self._set_combo_values(self.sex_combo, "sex", self.sex_var)
        self._set_combo_values(self.phenotype_combo, "phenotype", self.phenotype_var)
        self._set_combo_values(self.action_combo, "action", self.action_var)
        self._set_combo_values(self.style_combo, "image_type", self.style_var)

    def _set_combo_values(self, combo: ttk.Combobox, field_name: str, variable: tk.StringVar) -> None:
        values = [RANDOM_LABEL] + sorted(self.choice_fields.get(field_name, []))
        combo.configure(values=values)
        if variable.get() not in values:
            variable.set(RANDOM_LABEL)

    def _filter_nationalities(self, _event: tk.Event) -> None:
        typed = _canon(self.nationality_var.get())
        values = sorted(self.choice_fields.get("nationality", []))
        if typed:
            values = [value for value in values if typed in value]
        self.nationality_combo.configure(values=values)

    def _sync_nationality_state(self) -> None:
        if self.mode_var.get() == "random":
            self.nationality_combo.configure(state="disabled")
        else:
            self.nationality_combo.configure(state="normal")

    def _choose_style_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Choisir aesthetics.txt",
            initialdir=str(APP_DIR),
            filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")),
        )
        if path:
            self.style_file_var.set(path)
            self._reload_styles()

    def _reload_styles(self) -> None:
        try:
            self.choice_fields = build_choice_fields(self.style_file_var.get())
            self._refresh_comboboxes()
            self.status_var.set("Styles rechargés.")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

    def _read_positive_int(self, variable: tk.StringVar, label: str, minimum: int = 1) -> int:
        try:
            value = int(variable.get().strip())
        except ValueError as exc:
            raise ValueError(f"{label} doit être un nombre entier.") from exc
        if value < minimum:
            raise ValueError(f"{label} doit être supérieur ou égal à {minimum}.")
        return value

    def _read_optional_seed(self) -> Optional[int]:
        raw = self.seed_var.get().strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError as exc:
            raise ValueError("La seed doit être un nombre entier ou rester vide.") from exc

    def _build_constraints(self, mode: str) -> Constraints:
        constraints = Constraints()

        if self.human_only_var.get():
            constraints.require_one("race", "human")

        if mode == "fixed":
            nationality = _canon(self.nationality_var.get())
            if not nationality:
                raise ValueError("Choisis une nationalité précise.")
            if nationality not in self.choice_fields.get("nationality", []):
                raise ValueError(f"Nationalité inconnue : {nationality}")
            constraints.require_one("nationality", nationality)

        for field_name, variable in (
            ("sex", self.sex_var),
            ("phenotype", self.phenotype_var),
            ("action", self.action_var),
            ("image_type", self.style_var),
        ):
            value = variable.get()
            if value and value != RANDOM_LABEL:
                constraints.require_one(field_name, value)

        return constraints

    def _generate(self, forced_mode: Optional[str] = None) -> None:
        mode = forced_mode or self.mode_var.get()
        self.mode_var.set(mode)
        self._sync_nationality_state()

        try:
            prompt_count = self._read_positive_int(self.num_var, "Nombre de prompts", 1)
            min_age = self._read_positive_int(self.min_age_var, "Âge minimum", 0)
            max_age = self._read_positive_int(self.max_age_var, "Âge maximum", 0)
            if min_age > max_age:
                raise ValueError("L'âge minimum ne peut pas être supérieur à l'âge maximum.")
            seed = self._read_optional_seed()
            constraints = self._build_constraints(mode)

            options = PromptOptions(
                n=prompt_count,
                seed=seed,
                min_age=min_age,
                max_age=max_age,
                copy_to_clipboard=False,
                constraints=constraints,
                style_file=self.style_file_var.get(),
            )
            self.choice_fields = build_choice_fields(self.style_file_var.get())
            prompts = generate_prompts(options, self.choice_fields)
            output = build_output(prompts)

            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", output)

            if self.copy_after_generate_var.get():
                self.clipboard_clear()
                self.clipboard_append(output)
                self.status_var.set(f"{len(prompts)} prompt(s) généré(s) et copié(s).")
            else:
                self.status_var.set(f"{len(prompts)} prompt(s) généré(s).")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))
            self.status_var.set("Erreur de génération.")

    def _get_output(self) -> str:
        return self.output_text.get("1.0", "end").strip()

    def _copy_output(self) -> None:
        output = self._get_output()
        if not output:
            self.status_var.set("Aucun texte à copier.")
            return
        self.clipboard_clear()
        self.clipboard_append(output)
        self.status_var.set("Résultat copié.")

    def _save_output(self) -> None:
        output = self._get_output()
        if not output:
            self.status_var.set("Aucun texte à exporter.")
            return
        path = filedialog.asksaveasfilename(
            title="Exporter les prompts",
            initialfile="spg_prompts.txt",
            defaultextension=".txt",
            filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")),
        )
        if not path:
            return
        Path(path).write_text(output, encoding="utf-8")
        self.status_var.set(f"Exporté : {path}")

    def _clear_output(self) -> None:
        self.output_text.delete("1.0", "end")
        self.status_var.set("Résultat effacé.")


def main() -> None:
    app = PromptGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
