from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional

import tkinter as tk
from tkinter import messagebox, ttk


APP_TITLE = "Tea’s konfirmation – 16. maj 2026"
TARGET_DATE = date(2026, 5, 16)
DB_PATH = Path("data/teas_konfirmation.db")

CATEGORIES = [
    "Kirke",
    "Fest",
    "Gæsteliste",
    "Mad & drikke",
    "Tøj",
    "Gaver",
    "Transport",
    "Lokation",
    "Invitationer",
    "Borddækning & pynt",
    "Musik & underholdning",
    "Foto & video",
    "Overnatning",
    "Tidsplan",
    "Diverse",
]

STATUSES = ["Ikke startet", "I gang", "Færdig"]
PRIORITIES = ["Lav", "Normal", "Høj"]


@dataclass
class TodoItem:
    title: str
    description: str
    category: str
    deadline: str
    status: str
    priority: str


@dataclass
class BudgetItem:
    name: str
    amount: float
    category: str
    paid: bool
    date: str


def init_db() -> None:
    is_new = not DB_PATH.exists()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                deadline TEXT,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                paid INTEGER NOT NULL,
                date TEXT NOT NULL
            )
            """
        )
        if is_new:
            seed_db(conn)


def seed_db(conn: sqlite3.Connection) -> None:
    now = datetime.now().strftime("%Y-%m-%d")
    todos = [
        (
            "Book kirke",
            "Kontakt kirken og reserver datoen.",
            "Kirke",
            "2025-11-01",
            "I gang",
            "Høj",
            now,
        ),
        (
            "Udkast til gæsteliste",
            "Første version af gæstelisten.",
            "Gæsteliste",
            "2025-12-15",
            "Ikke startet",
            "Normal",
            now,
        ),
        (
            "Find lokale til fest",
            "Indhent tilbud fra 2-3 lokationer.",
            "Lokation",
            "2026-01-10",
            "Ikke startet",
            "Høj",
            now,
        ),
    ]
    budget = [
        ("Depositum lokale", 5000.0, "Lokation", 0, "2026-01-15"),
        ("Kage", 1200.0, "Mad & drikke", 0, "2026-04-20"),
        ("Fotograf", 3500.0, "Foto & video", 0, "2026-03-01"),
    ]
    conn.executemany(
        """
        INSERT INTO todos
        (title, description, category, deadline, status, priority, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        todos,
    )
    conn.executemany(
        """
        INSERT INTO budget
        (name, amount, category, paid, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        budget,
    )


def query_all(conn: sqlite3.Connection, query: str, params: Iterable = ()) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(query, params)
    return cursor.fetchall()


def parse_date(value: str) -> Optional[date]:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def format_currency(amount: float) -> str:
    return f"{amount:,.0f} kr.".replace(",", ".")


class KonfirmationApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x720")
        self.minsize(960, 640)
        self.configure(bg="#f5f5f7")

        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f5f5f7")
        self.style.configure("TLabel", background="#f5f5f7", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        self.style.configure("Card.TLabelframe", background="#ffffff")
        self.style.configure("Card.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text=APP_TITLE, style="Title.TLabel")
        title.pack(anchor="w")

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=12)

        self.overview_tab = ttk.Frame(self.notebook)
        self.todo_tab = ttk.Frame(self.notebook)
        self.budget_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.overview_tab, text="Overblik")
        self.notebook.add(self.todo_tab, text="Emner/To-do")
        self.notebook.add(self.budget_tab, text="Budget")

        self._build_overview_tab()
        self._build_todo_tab()
        self._build_budget_tab()

        self.refresh_all()

    def refresh_all(self) -> None:
        self.refresh_overview()
        self.refresh_todos()
        self.refresh_budget()

    def _build_overview_tab(self) -> None:
        self.overview_tab.columnconfigure(0, weight=1)
        self.overview_tab.columnconfigure(1, weight=1)

        self.countdown_card = ttk.Labelframe(
            self.overview_tab, text="Nedtælling", style="Card.TLabelframe", padding=16
        )
        self.countdown_card.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.countdown_label = ttk.Label(
            self.countdown_card,
            text="",
            font=("Segoe UI", 24, "bold"),
            background="#ffffff",
        )
        self.countdown_label.pack(anchor="w")

        self.status_card = ttk.Labelframe(
            self.overview_tab, text="Status overblik", style="Card.TLabelframe", padding=16
        )
        self.status_card.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

        self.status_label = ttk.Label(
            self.status_card, text="", background="#ffffff", justify="left"
        )
        self.status_label.pack(anchor="w")

        self.deadline_card = ttk.Labelframe(
            self.overview_tab,
            text="Næste 5 deadlines",
            style="Card.TLabelframe",
            padding=16,
        )
        self.deadline_card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        self.deadline_list = tk.Listbox(
            self.deadline_card,
            height=6,
            font=("Segoe UI", 10),
            bg="#ffffff",
            highlightthickness=0,
            selectbackground="#d7e3ff",
        )
        self.deadline_list.pack(fill=tk.BOTH, expand=True)

        self.overview_empty = ttk.Label(
            self.deadline_card,
            text="Ingen deadlines endnu. Tilføj emner i fanen Emner/To-do.",
            background="#ffffff",
        )

    def _build_todo_tab(self) -> None:
        self.todo_tab.rowconfigure(1, weight=1)
        self.todo_tab.columnconfigure(0, weight=1)

        filters_frame = ttk.Labelframe(
            self.todo_tab, text="Søg og filtrér", style="Card.TLabelframe", padding=12
        )
        filters_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        for i in range(6):
            filters_frame.columnconfigure(i, weight=1)

        ttk.Label(filters_frame, text="Søg").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filters_frame, textvariable=self.search_var)
        search_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12))
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_todos())

        ttk.Label(filters_frame, text="Kategori").grid(row=0, column=1, sticky="w")
        self.filter_category = tk.StringVar(value="Alle")
        category_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.filter_category,
            values=["Alle"] + CATEGORIES,
            state="readonly",
        )
        category_combo.grid(row=1, column=1, sticky="ew", padx=(0, 12))
        category_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_todos())

        ttk.Label(filters_frame, text="Status").grid(row=0, column=2, sticky="w")
        self.filter_status = tk.StringVar(value="Alle")
        status_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.filter_status,
            values=["Alle"] + STATUSES,
            state="readonly",
        )
        status_combo.grid(row=1, column=2, sticky="ew", padx=(0, 12))
        status_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_todos())

        ttk.Label(filters_frame, text="Prioritet").grid(row=0, column=3, sticky="w")
        self.filter_priority = tk.StringVar(value="Alle")
        priority_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.filter_priority,
            values=["Alle"] + PRIORITIES,
            state="readonly",
        )
        priority_combo.grid(row=1, column=3, sticky="ew", padx=(0, 12))
        priority_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_todos())

        ttk.Label(filters_frame, text="Sortér efter").grid(row=0, column=4, sticky="w")
        self.sort_var = tk.StringVar(value="Deadline")
        sort_combo = ttk.Combobox(
            filters_frame,
            textvariable=self.sort_var,
            values=["Deadline", "Prioritet", "Status"],
            state="readonly",
        )
        sort_combo.grid(row=1, column=4, sticky="ew", padx=(0, 12))
        sort_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_todos())

        reset_button = ttk.Button(
            filters_frame, text="Nulstil", command=self.reset_filters
        )
        reset_button.grid(row=1, column=5, sticky="ew")

        list_frame = ttk.Labelframe(
            self.todo_tab, text="Emner", style="Card.TLabelframe", padding=12
        )
        list_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("title", "category", "deadline", "status", "priority")
        self.todo_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.todo_tree.heading("title", text="Titel")
        self.todo_tree.heading("category", text="Kategori")
        self.todo_tree.heading("deadline", text="Deadline")
        self.todo_tree.heading("status", text="Status")
        self.todo_tree.heading("priority", text="Prioritet")
        self.todo_tree.column("title", width=260)
        self.todo_tree.column("category", width=140)
        self.todo_tree.column("deadline", width=120)
        self.todo_tree.column("status", width=120)
        self.todo_tree.column("priority", width=100)
        self.todo_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.todo_tree.yview)
        self.todo_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.todo_empty = ttk.Label(
            list_frame,
            text="Ingen emner matcher dine filtre endnu.",
            background="#ffffff",
        )

        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        for i in range(5):
            button_frame.columnconfigure(i, weight=1)

        ttk.Button(button_frame, text="Tilføj emne", command=self.add_todo).grid(
            row=0, column=0, sticky="ew", padx=4
        )
        ttk.Button(button_frame, text="Redigér", command=self.edit_todo).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        ttk.Button(button_frame, text="Slet", command=self.delete_todo).grid(
            row=0, column=2, sticky="ew", padx=4
        )
        ttk.Button(
            button_frame,
            text="Markér som færdig",
            style="Accent.TButton",
            command=self.mark_todo_done,
        ).grid(row=0, column=3, sticky="ew", padx=4)
        ttk.Button(button_frame, text="Opdatér", command=self.refresh_todos).grid(
            row=0, column=4, sticky="ew", padx=4
        )

    def _build_budget_tab(self) -> None:
        self.budget_tab.rowconfigure(1, weight=1)
        self.budget_tab.columnconfigure(0, weight=1)

        totals_frame = ttk.Labelframe(
            self.budget_tab, text="Budget overblik", style="Card.TLabelframe", padding=12
        )
        totals_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        for i in range(3):
            totals_frame.columnconfigure(i, weight=1)

        self.total_label = ttk.Label(totals_frame, text="Total: 0 kr.")
        self.total_label.grid(row=0, column=0, sticky="w")
        self.paid_label = ttk.Label(totals_frame, text="Betalt: 0 kr.")
        self.paid_label.grid(row=0, column=1, sticky="w")
        self.remaining_label = ttk.Label(totals_frame, text="Rest: 0 kr.")
        self.remaining_label.grid(row=0, column=2, sticky="w")

        list_frame = ttk.Labelframe(
            self.budget_tab, text="Budgetposter", style="Card.TLabelframe", padding=12
        )
        list_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("name", "category", "amount", "paid", "date")
        self.budget_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.budget_tree.heading("name", text="Navn")
        self.budget_tree.heading("category", text="Kategori")
        self.budget_tree.heading("amount", text="Beløb")
        self.budget_tree.heading("paid", text="Betalt")
        self.budget_tree.heading("date", text="Dato")
        self.budget_tree.column("name", width=260)
        self.budget_tree.column("category", width=140)
        self.budget_tree.column("amount", width=120)
        self.budget_tree.column("paid", width=90)
        self.budget_tree.column("date", width=120)
        self.budget_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.budget_tree.yview)
        self.budget_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.budget_empty = ttk.Label(
            list_frame,
            text="Ingen budgetposter endnu. Tilføj den første for at komme i gang.",
            background="#ffffff",
        )

        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        for i in range(4):
            button_frame.columnconfigure(i, weight=1)

        ttk.Button(button_frame, text="Tilføj budgetpost", command=self.add_budget).grid(
            row=0, column=0, sticky="ew", padx=4
        )
        ttk.Button(button_frame, text="Redigér", command=self.edit_budget).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        ttk.Button(button_frame, text="Slet", command=self.delete_budget).grid(
            row=0, column=2, sticky="ew", padx=4
        )
        ttk.Button(button_frame, text="Opdatér", command=self.refresh_budget).grid(
            row=0, column=3, sticky="ew", padx=4
        )

    def reset_filters(self) -> None:
        self.search_var.set("")
        self.filter_category.set("Alle")
        self.filter_status.set("Alle")
        self.filter_priority.set("Alle")
        self.sort_var.set("Deadline")
        self.refresh_todos()

    def refresh_overview(self) -> None:
        days_left = (TARGET_DATE - date.today()).days
        if days_left >= 0:
            countdown_text = f"{days_left} dage til konfirmationen"
        else:
            countdown_text = "Konfirmationen er afholdt"
        self.countdown_label.config(text=countdown_text)

        with sqlite3.connect(DB_PATH) as conn:
            status_counts = query_all(
                conn,
                """
                SELECT status, COUNT(*) as total
                FROM todos
                GROUP BY status
                """,
            )
            counts = {row["status"]: row["total"] for row in status_counts}

            status_lines = [
                f"Ikke startet: {counts.get('Ikke startet', 0)}",
                f"I gang: {counts.get('I gang', 0)}",
                f"Færdig: {counts.get('Færdig', 0)}",
            ]
            self.status_label.config(text="\n".join(status_lines))

            upcoming = query_all(
                conn,
                """
                SELECT title, deadline
                FROM todos
                WHERE deadline IS NOT NULL AND deadline != ''
                ORDER BY deadline ASC
                LIMIT 5
                """,
            )

        self.deadline_list.delete(0, tk.END)
        for row in upcoming:
            deadline = row["deadline"]
            self.deadline_list.insert(tk.END, f"{deadline} · {row['title']}")

        if not upcoming:
            self.overview_empty.pack(anchor="w", pady=(8, 0))
        else:
            self.overview_empty.pack_forget()

    def refresh_todos(self) -> None:
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)

        search = self.search_var.get().strip()
        category = self.filter_category.get()
        status = self.filter_status.get()
        priority = self.filter_priority.get()
        sort = self.sort_var.get()

        query = "SELECT * FROM todos WHERE 1=1"
        params: list[str] = []

        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            like = f"%{search}%"
            params.extend([like, like])
        if category != "Alle":
            query += " AND category = ?"
            params.append(category)
        if status != "Alle":
            query += " AND status = ?"
            params.append(status)
        if priority != "Alle":
            query += " AND priority = ?"
            params.append(priority)

        if sort == "Deadline":
            query += " ORDER BY deadline ASC"
        elif sort == "Prioritet":
            query += (
                " ORDER BY CASE priority "
                "WHEN 'Høj' THEN 1 "
                "WHEN 'Normal' THEN 2 "
                "WHEN 'Lav' THEN 3 END"
            )
        else:
            query += (
                " ORDER BY CASE status "
                "WHEN 'Ikke startet' THEN 1 "
                "WHEN 'I gang' THEN 2 "
                "WHEN 'Færdig' THEN 3 END"
            )

        with sqlite3.connect(DB_PATH) as conn:
            rows = query_all(conn, query, params)

        for row in rows:
            self.todo_tree.insert(
                "",
                tk.END,
                iid=row["id"],
                values=(
                    row["title"],
                    row["category"],
                    row["deadline"],
                    row["status"],
                    row["priority"],
                ),
            )

        if not rows:
            self.todo_empty.grid(row=0, column=0, sticky="nsew")
        else:
            self.todo_empty.grid_forget()

    def refresh_budget(self) -> None:
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)

        with sqlite3.connect(DB_PATH) as conn:
            rows = query_all(
                conn,
                """
                SELECT * FROM budget
                ORDER BY date ASC
                """,
            )

        total = 0.0
        paid_total = 0.0
        for row in rows:
            amount = float(row["amount"])
            total += amount
            if row["paid"]:
                paid_total += amount
            self.budget_tree.insert(
                "",
                tk.END,
                iid=row["id"],
                values=(
                    row["name"],
                    row["category"],
                    format_currency(amount),
                    "Ja" if row["paid"] else "Nej",
                    row["date"],
                ),
            )

        remaining = total - paid_total
        self.total_label.config(text=f"Total: {format_currency(total)}")
        self.paid_label.config(text=f"Betalt: {format_currency(paid_total)}")
        self.remaining_label.config(text=f"Rest: {format_currency(remaining)}")

        if not rows:
            self.budget_empty.grid(row=0, column=0, sticky="nsew")
        else:
            self.budget_empty.grid_forget()

    def add_todo(self) -> None:
        TodoDialog(self, "Tilføj emne", None, self.save_todo)

    def edit_todo(self) -> None:
        selected = self.todo_tree.selection()
        if not selected:
            messagebox.showinfo("Vælg emne", "Vælg et emne for at redigere.")
            return
        todo_id = int(selected[0])
        with sqlite3.connect(DB_PATH) as conn:
            rows = query_all(conn, "SELECT * FROM todos WHERE id = ?", (todo_id,))
        if not rows:
            return
        row = rows[0]
        item = TodoItem(
            title=row["title"],
            description=row["description"],
            category=row["category"],
            deadline=row["deadline"],
            status=row["status"],
            priority=row["priority"],
        )
        TodoDialog(self, "Redigér emne", item, lambda data: self.save_todo(data, todo_id))

    def delete_todo(self) -> None:
        selected = self.todo_tree.selection()
        if not selected:
            messagebox.showinfo("Vælg emne", "Vælg et emne for at slette.")
            return
        todo_id = int(selected[0])
        if not messagebox.askyesno("Slet emne", "Vil du slette dette emne?"):
            return
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        self.refresh_all()

    def mark_todo_done(self) -> None:
        selected = self.todo_tree.selection()
        if not selected:
            messagebox.showinfo("Vælg emne", "Vælg et emne for at markere som færdig.")
            return
        todo_id = int(selected[0])
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE todos SET status = 'Færdig' WHERE id = ?", (todo_id,))
        self.refresh_all()

    def save_todo(self, data: TodoItem, todo_id: Optional[int] = None) -> None:
        if not data.title:
            messagebox.showerror("Manglende titel", "Titel må ikke være tom.")
            return
        if data.deadline and not parse_date(data.deadline):
            messagebox.showerror("Ugyldig dato", "Deadline skal være i formatet ÅÅÅÅ-MM-DD.")
            return
        with sqlite3.connect(DB_PATH) as conn:
            if todo_id is None:
                conn.execute(
                    """
                    INSERT INTO todos
                    (title, description, category, deadline, status, priority, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data.title,
                        data.description,
                        data.category,
                        data.deadline,
                        data.status,
                        data.priority,
                        datetime.now().strftime("%Y-%m-%d"),
                    ),
                )
            else:
                conn.execute(
                    """
                    UPDATE todos
                    SET title = ?, description = ?, category = ?, deadline = ?, status = ?, priority = ?
                    WHERE id = ?
                    """,
                    (
                        data.title,
                        data.description,
                        data.category,
                        data.deadline,
                        data.status,
                        data.priority,
                        todo_id,
                    ),
                )
        self.refresh_all()

    def add_budget(self) -> None:
        BudgetDialog(self, "Tilføj budgetpost", None, self.save_budget)

    def edit_budget(self) -> None:
        selected = self.budget_tree.selection()
        if not selected:
            messagebox.showinfo("Vælg budgetpost", "Vælg en budgetpost for at redigere.")
            return
        budget_id = int(selected[0])
        with sqlite3.connect(DB_PATH) as conn:
            rows = query_all(conn, "SELECT * FROM budget WHERE id = ?", (budget_id,))
        if not rows:
            return
        row = rows[0]
        item = BudgetItem(
            name=row["name"],
            amount=float(row["amount"]),
            category=row["category"],
            paid=bool(row["paid"]),
            date=row["date"],
        )
        BudgetDialog(self, "Redigér budgetpost", item, lambda data: self.save_budget(data, budget_id))

    def delete_budget(self) -> None:
        selected = self.budget_tree.selection()
        if not selected:
            messagebox.showinfo("Vælg budgetpost", "Vælg en budgetpost for at slette.")
            return
        budget_id = int(selected[0])
        if not messagebox.askyesno("Slet budgetpost", "Vil du slette denne budgetpost?"):
            return
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM budget WHERE id = ?", (budget_id,))
        self.refresh_budget()

    def save_budget(self, data: BudgetItem, budget_id: Optional[int] = None) -> None:
        if not data.name:
            messagebox.showerror("Manglende navn", "Navn må ikke være tomt.")
            return
        if not parse_date(data.date):
            messagebox.showerror("Ugyldig dato", "Dato skal være i formatet ÅÅÅÅ-MM-DD.")
            return
        if data.amount <= 0:
            messagebox.showerror("Ugyldigt beløb", "Beløbet skal være større end 0.")
            return
        with sqlite3.connect(DB_PATH) as conn:
            if budget_id is None:
                conn.execute(
                    """
                    INSERT INTO budget
                    (name, amount, category, paid, date)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        data.name,
                        data.amount,
                        data.category,
                        1 if data.paid else 0,
                        data.date,
                    ),
                )
            else:
                conn.execute(
                    """
                    UPDATE budget
                    SET name = ?, amount = ?, category = ?, paid = ?, date = ?
                    WHERE id = ?
                    """,
                    (
                        data.name,
                        data.amount,
                        data.category,
                        1 if data.paid else 0,
                        data.date,
                        budget_id,
                    ),
                )
        self.refresh_budget()
        self.refresh_overview()


class TodoDialog(tk.Toplevel):
    def __init__(
        self,
        parent: KonfirmationApp,
        title: str,
        item: Optional[TodoItem],
        on_save,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()

        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        self.title_var = tk.StringVar(value=item.title if item else "")
        self.desc_var = tk.StringVar(value=item.description if item else "")
        self.category_var = tk.StringVar(value=item.category if item else CATEGORIES[0])
        self.deadline_var = tk.StringVar(value=item.deadline if item else "")
        self.status_var = tk.StringVar(value=item.status if item else STATUSES[0])
        self.priority_var = tk.StringVar(value=item.priority if item else PRIORITIES[1])

        fields = [
            ("Titel", self.title_var),
            ("Beskrivelse", self.desc_var),
            ("Kategori", self.category_var),
            ("Deadline (ÅÅÅÅ-MM-DD)", self.deadline_var),
            ("Status", self.status_var),
            ("Prioritet", self.priority_var),
        ]

        for idx, (label, _) in enumerate(fields):
            ttk.Label(container, text=label).grid(row=idx * 2, column=0, sticky="w")

        ttk.Entry(container, textvariable=self.title_var, width=40).grid(
            row=1, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Entry(container, textvariable=self.desc_var, width=40).grid(
            row=3, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Combobox(
            container,
            textvariable=self.category_var,
            values=CATEGORIES,
            state="readonly",
            width=38,
        ).grid(row=5, column=0, sticky="ew", pady=(0, 8))
        ttk.Entry(container, textvariable=self.deadline_var, width=40).grid(
            row=7, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Combobox(
            container,
            textvariable=self.status_var,
            values=STATUSES,
            state="readonly",
            width=38,
        ).grid(row=9, column=0, sticky="ew", pady=(0, 8))
        ttk.Combobox(
            container,
            textvariable=self.priority_var,
            values=PRIORITIES,
            state="readonly",
            width=38,
        ).grid(row=11, column=0, sticky="ew", pady=(0, 8))

        button_frame = ttk.Frame(container)
        button_frame.grid(row=12, column=0, sticky="ew", pady=(8, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Annuller", command=self.destroy).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(
            button_frame,
            text="Gem",
            style="Accent.TButton",
            command=lambda: self._save(on_save),
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _save(self, on_save) -> None:
        data = TodoItem(
            title=self.title_var.get().strip(),
            description=self.desc_var.get().strip(),
            category=self.category_var.get(),
            deadline=self.deadline_var.get().strip(),
            status=self.status_var.get(),
            priority=self.priority_var.get(),
        )
        on_save(data)
        self.destroy()


class BudgetDialog(tk.Toplevel):
    def __init__(
        self,
        parent: KonfirmationApp,
        title: str,
        item: Optional[BudgetItem],
        on_save,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()

        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        self.name_var = tk.StringVar(value=item.name if item else "")
        self.amount_var = tk.StringVar(value=str(item.amount) if item else "")
        self.category_var = tk.StringVar(value=item.category if item else CATEGORIES[0])
        self.paid_var = tk.BooleanVar(value=item.paid if item else False)
        self.date_var = tk.StringVar(value=item.date if item else "")

        ttk.Label(container, text="Navn").grid(row=0, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.name_var, width=40).grid(
            row=1, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Label(container, text="Beløb (kr.)").grid(row=2, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.amount_var, width=40).grid(
            row=3, column=0, sticky="ew", pady=(0, 8)
        )
        ttk.Label(container, text="Kategori").grid(row=4, column=0, sticky="w")
        ttk.Combobox(
            container,
            textvariable=self.category_var,
            values=CATEGORIES,
            state="readonly",
            width=38,
        ).grid(row=5, column=0, sticky="ew", pady=(0, 8))
        ttk.Checkbutton(container, text="Betalt", variable=self.paid_var).grid(
            row=6, column=0, sticky="w", pady=(0, 8)
        )
        ttk.Label(container, text="Dato (ÅÅÅÅ-MM-DD)").grid(row=7, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.date_var, width=40).grid(
            row=8, column=0, sticky="ew", pady=(0, 8)
        )

        button_frame = ttk.Frame(container)
        button_frame.grid(row=9, column=0, sticky="ew", pady=(8, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Annuller", command=self.destroy).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(
            button_frame,
            text="Gem",
            style="Accent.TButton",
            command=lambda: self._save(on_save),
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _save(self, on_save) -> None:
        try:
            amount = float(self.amount_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Ugyldigt beløb", "Indtast et gyldigt beløb.")
            return
        data = BudgetItem(
            name=self.name_var.get().strip(),
            amount=amount,
            category=self.category_var.get(),
            paid=self.paid_var.get(),
            date=self.date_var.get().strip(),
        )
        on_save(data)
        self.destroy()


def main() -> None:
    init_db()
    app = KonfirmationApp()
    app.mainloop()


if __name__ == "__main__":
    main()
