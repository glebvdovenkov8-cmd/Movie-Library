import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library")
        self.root.geometry("750x520")
        self.movies = []
        self.data_file = "movies.json"

        # --- Форма ввода ---
        input_frame = ttk.LabelFrame(root, text="Добавить фильм")
        input_frame.pack(fill="x", padx=10, pady=8)

        fields = [
            ("Название", "title"),
            ("Жанр", "genre"),
            ("Год выпуска", "year"),
            ("Рейтинг (0-10)", "rating")
        ]
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(input_frame, text=f"{label}:").grid(row=i, column=0, padx=5, pady=4, sticky="w")
            entry = ttk.Entry(input_frame, width=35)
            entry.grid(row=i, column=1, padx=5, pady=4)
            self.entries[key] = entry

        ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie).grid(
            row=4, column=0, columnspan=2, pady=8)

        # --- Фильтры ---
        filter_frame = ttk.LabelFrame(root, text="Фильтрация")
        filter_frame.pack(fill="x", padx=10, pady=8)

        ttk.Label(filter_frame, text="По жанру:").grid(row=0, column=0, padx=5)
        self.filter_genre = ttk.Entry(filter_frame, width=18)
        self.filter_genre.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="По году:").grid(row=0, column=2, padx=5)
        self.filter_year = ttk.Entry(filter_frame, width=10)
        self.filter_year.grid(row=0, column=3, padx=5)

        ttk.Button(filter_frame, text="Применить", command=self.apply_filter).grid(row=0, column=4, padx=5)
        ttk.Button(filter_frame, text="Сброс", command=self.reset_filter).grid(row=0, column=5, padx=5)

        # --- Таблица ---
        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=("title", "genre", "year", "rating"), show="headings")
        for col, header, width in [("title", "Название", 220), ("genre", "Жанр", 130), 
                                   ("year", "Год", 70), ("rating", "Рейтинг", 80)]:
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="center" if col != "title" else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- JSON кнопки ---
        io_frame = ttk.Frame(root)
        io_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(io_frame, text="💾 Сохранить в JSON", command=self.save_json).pack(side="left", padx=5)
        ttk.Button(io_frame, text="📂 Загрузить из JSON", command=self.load_json).pack(side="left", padx=5)

        self.load_json()  # Автозагрузка при старте

    def validate(self):
        year_str = self.entries["year"].get().strip()
        rating_str = self.entries["rating"].get().strip()
        if not self.entries["title"].get().strip() or not self.entries["genre"].get().strip():
            messagebox.showerror("Ошибка", "Заполните название и жанр.")
            return None

        try:
            year = int(year_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть целым числом.")
            return None

        try:
            rating = float(rating_str)
            if not (0 <= rating <= 10):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом от 0 до 10.")
            return None

        return {
            "title": self.entries["title"].get().strip(),
            "genre": self.entries["genre"].get().strip(),
            "year": year,
            "rating": round(rating, 1)
        }

    def add_movie(self):
        movie = self.validate()
        if movie:
            self.movies.append(movie)
            self.refresh_table(self.movies)
            for entry in self.entries.values():
                entry.delete(0, tk.END)

    def refresh_table(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for m in data:
            self.tree.insert("", tk.END, values=(m["title"], m["genre"], m["year"], m["rating"]))

    def apply_filter(self):
        f_genre = self.filter_genre.get().strip().lower()
        f_year_str = self.filter_year.get().strip()
        
        try:
            f_year = int(f_year_str) if f_year_str else None
        except ValueError:
            messagebox.showwarning("Предупреждение", "Год фильтра должен быть числом.")
            return

        filtered = []
        for m in self.movies:
            match_g = not f_genre or f_genre in m["genre"].lower()
            match_y = (f_year is None) or (m["year"] == f_year)
            if match_g and match_y:
                filtered.append(m)
        self.refresh_table(filtered)

    def reset_filter(self):
        self.filter_genre.delete(0, tk.END)
        self.filter_year.delete(0, tk.END)
        self.refresh_table(self.movies)

    def save_json(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", "Библиотека сохранена в movies.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_json(self):
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.movies = json.load(f)
            self.refresh_table(self.movies)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.mainloop()