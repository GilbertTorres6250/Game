from tkinter import filedialog
from tkinter import *
from tkinter import ttk
import sqlite3
from tkinter import messagebox
from tkinter.simpledialog import askstring
import os

newWindow = None
editWindow = None
displayWindow = None
menuWindow = None
b = "black"
f = "white"
connection = sqlite3.connect('recipes.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    directions TEXT NOT NULL
                )''')
connection.commit()
cursor.execute('''CREATE TABLE IF NOT EXISTS colors (
                    id INTEGER PRIMARY KEY,
                    background_color TEXT,
                    foreground_color TEXT
                )''')
connection.commit()

win = Tk()
win.geometry("630x400")
win.state("zoomed")
win.title("COOKBOOK")
win.configure(background=b)

search_var = StringVar()

def search_recipes():
    global current_page
    current_page = 0
    search_query = search_var.get().lower()
    if search_query:
        cursor.execute("SELECT * FROM recipes WHERE name LIKE ? LIMIT ? OFFSET ?",('%' + search_query + '%', recipes_per_page, current_page * recipes_per_page))
        recipes = cursor.fetchall()

    else:
        cursor.execute("SELECT * FROM recipes LIMIT ? OFFSET ?", (recipes_per_page, current_page * recipes_per_page))
        recipes = cursor.fetchall()
    update_recipe_list(recipes)


def saveColor(background, foreground):
    cursor.execute("INSERT INTO colors (background_color, foreground_color) VALUES (?, ?)",(background, foreground))
    connection.commit()


def loadColor():
    cursor.execute("SELECT * FROM colors ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    if result:
        return result[1], result[2]
    else:
        return "black", "white"


def on_closing_new_window():
    global newWindow
    if newWindow is not None:
        newWindow.destroy()
        newWindow = None


def on_closing_edit_window():
    global editWindow
    if editWindow is not None:
        editWindow.destroy()
        editWindow = None


def on_closing_display_window():
    global displayWindow
    global editWindow
    if editWindow is not None:
        editWindow.destroy()
        editWindow = None
    if displayWindow is not None:
        displayWindow.destroy()
        displayWindow = None


def on_closing_menu_window():
    global menuWindow
    if menuWindow is not None:
        menuWindow.destroy()
        menuWindow = None


# PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE
current_page = 0
recipes_per_page = 12


def openNewWindow():
    global newWindow
    if newWindow is not None:
        newWindow.focus()
        return
    newWindow = Toplevel(win)
    newWindow.title("New Recipe")
    newWindow.geometry("400x400")
    newWindow.configure(background=b)

    lbl_newName = ttk.Label(newWindow, text="Name:", background=b, foreground=f, font="impact")
    lbl_newName.place(relx=0.25, rely=0.04, anchor=CENTER)
    ent_newName = Entry(newWindow,relief=RIDGE, bd=5)
    ent_newName.pack(pady=5)
    ent_newName.exclude_change = True

    Label(newWindow, text="Ingredients:", background=b, foreground=f, font="bold").pack()

    ent_ingredients = Text(newWindow, width=30, height=5,relief=RIDGE, bd=10,)
    ent_ingredients.pack(pady=5, padx=10, fill=BOTH, expand=True)

    Label(newWindow, text="Directions:", background=b, foreground=f, font="bold").pack()

    ent_directions = Text(newWindow, width=30, height=5,relief=RIDGE, bd=10,)
    ent_directions.pack(pady=5, padx=10, fill=BOTH, expand=True,)
    newWindow.protocol("WM_DELETE_WINDOW", on_closing_new_window)

    def add_recipe():
        recipe_name = ent_newName.get()
        recipe_ingredients = ent_ingredients.get("1.0", END).strip()
        recipe_directions = ent_directions.get("1.0", END).strip()
        cursor.execute("INSERT INTO recipes (name, ingredients, directions) VALUES (?, ?, ?)",(recipe_name, recipe_ingredients, recipe_directions))
        connection.commit()
        on_closing_new_window()
        update_recipe_list()

    btt_Add = Button(newWindow, text="Add", command=add_recipe, width=10, relief=RAISED, bd=5, bg=f, fg=b)
    btt_Add.pack(pady=5)
    btI = Button(newWindow, text="IMPORT", command=openImport, width=10, relief=RAISED, bd=5, bg=f, fg=b)
    btI.pack(pady=5)
    newWindow.minsize(width=400,height=400)


def display_recipe(recipe_id, recipe_name, ingredients, directions):
    global displayWindow

    def edit_recipe():
        global editWindow
        if editWindow is not None:
            editWindow.focus()
            return
        editWindow = Toplevel(win)
        editWindow.title("Edit Recipe")
        editWindow.geometry("400x400")
        editWindow.configure(background=b)

        lbl_name = ttk.Label(editWindow, text="Name:", background=b, foreground=f, font="impact")
        lbl_name.place(relx=0.25, rely=0.04, anchor=CENTER)
        ent_name = Entry(editWindow,relief=RIDGE, bd=5)
        ent_name.insert(END, recipe_name)
        ent_name.exclude_change = True
        ent_name.pack(pady=5)

        Label(editWindow, text="Ingredients:", background=b, foreground=f, font="bold").pack()

        ent_ingredients = Text(editWindow, width=30, height=5,relief=RIDGE, bd=10,)
        ent_ingredients.insert(END, ingredients)
        ent_ingredients.pack(pady=5, padx=10, fill=BOTH, expand=True)

        Label(editWindow, text="Directions:", background=b, foreground=f, font="bold").pack()

        ent_directions = Text(editWindow, width=30, height=5,relief=RIDGE, bd=10,)
        ent_directions.insert(END, directions)
        ent_directions.pack(pady=5, padx=10, fill=BOTH, expand=True)
        editWindow.protocol("WM_DELETE_WINDOW", on_closing_edit_window)

        def save_changes():
            new_recipe_name = ent_name.get()
            new_ingredients = ent_ingredients.get("1.0", END).strip()
            new_directions = ent_directions.get("1.0", END).strip()

            cursor.execute("UPDATE recipes SET name=?, ingredients=?, directions=? WHERE id=?",(new_recipe_name, new_ingredients, new_directions, recipe_id))
            connection.commit()
            on_closing_display_window()
            on_closing_edit_window()
            update_recipe_list()

        btt_Save = Button(editWindow, text="Save", command=save_changes, width=10, relief=RAISED, bd=5, bg=f, fg=b)
        btt_Save.pack(pady=5)
        editWindow.minsize(width=400, height=400)

    def delete_recipe():
        cursor.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
        connection.commit()
        on_closing_display_window()
        update_recipe_list()

    if displayWindow is not None:
        displayWindow.focus()
        return
    displayWindow = Toplevel(win)
    displayWindow.title(recipe_name)
    displayWindow.geometry("400x400")
    displayWindow.configure(background=b)

    Label(displayWindow, text=f"Name: {recipe_name}", background=b, foreground=f, font="impact").pack()

    Label(displayWindow, text="Ingredients:", background=b, foreground=f, font="bold").pack()

    ent_ingredients = Text(displayWindow, width=30, height=5,relief=RIDGE, bd=10,)
    ent_ingredients.insert(END, ingredients)
    ent_ingredients.config(state='disabled')
    ent_ingredients.pack(pady=5, padx=10, fill=BOTH, expand=True)

    Label(displayWindow, text="Directions:", background=b, foreground=f, font="bold").pack()

    ent_directions = Text(displayWindow, width=30, height=5,relief=RIDGE, bd=10,)
    ent_directions.insert(END, directions)
    ent_directions.config(state='disabled')
    ent_directions.pack(pady=5, padx=10, fill=BOTH, expand=True)

    btt_Edit = Button(displayWindow, text="Edit", command=edit_recipe, width=10, relief=RAISED, bd=5, bg=f, fg=b)
    btt_Edit.pack(pady=5)

    btt_Delete = Button(displayWindow, text="Delete", command=delete_recipe, width=10, relief=RAISED, bd=5, bg=f, fg=b)
    btt_Delete.pack(pady=5)

    btE = Button(displayWindow, text="EXPORT",command=lambda: makeExport(recipe_id, recipe_name, ingredients, directions), width=10, relief=RAISED, bd=5, bg=f, fg=b)
    btE.place(x=0, y=1)
    displayWindow.protocol()
    displayWindow.protocol("WM_DELETE_WINDOW", on_closing_display_window)
    displayWindow.minsize(width=400,height=400)


def update_recipe_list(recipes=None):
    if recipes is None:
        cursor.execute("SELECT * FROM recipes LIMIT ? OFFSET ?", (recipes_per_page, current_page * recipes_per_page))
        recipes = cursor.fetchall()

    for widget in frame.winfo_children():
        widget.destroy()

    row_count = 0
    column_count = 0

    for recipe in recipes:
        recipe_id, recipe_name, _, _ = recipe
        recipe_button = Button(frame, text=recipe_name, command=lambda recipe=recipe: display_recipe(*recipe),width=30, padx=20,pady= 20,font=20,relief=RIDGE, bd=5)

        recipe_button.grid(row=row_count, column=column_count, padx=10, pady=10,)
        column_count += 1
        if column_count == 3:
            column_count = 0
            row_count += 1
    add_navigation_buttons()


def change():
    for window in [win, newWindow, editWindow, displayWindow, menuWindow]:

        if window:
            window.configure(background=b)
            for widget in window.winfo_children():
                if hasattr(widget, 'exclude_change') and widget.exclude_change:
                    pass
                else:
                    if 'background' in widget.keys():
                        widget.configure(background=b)
                    if 'foreground' in widget.keys():
                        widget.configure(foreground=f)
                    if isinstance(widget, Text):
                        widget.configure(foreground="black", background="white")
                    if isinstance(widget, Button):
                        widget.configure(background=f,foreground=b, activebackground=b, activeforeground=f)
                    if isinstance(widget, Entry):
                        widget.configure(foreground=b, background=f)


color_map = {
    "COFFEE": ("#4d3626", "#f3e9dc"),  # Dark brown
    "HORCHATA": ("#f2e9d9", "#b8976a"),  # Tan
    "DR PEPPER": ("#711f25", "white"),  # Red
    "MATCHA": ("#8EB288", "#3a4a37"),  # Pastel green
    "CREAMSICLE": ("#fbbd60", "#f7e0b6"),  # Orange
    "TARO": ("#9C7F91", "#E3B8C3"),  # Pastel Purple
    "BLUE CHEESE": ("#6a7f8c", "#d1d9e6"),  # Pastel Blue
    "OREO": ("#4d4a4b", "#eceaea"),  # Grey
    "WATERMELON": ("#1c5c0e", "#ff6666"),  # Dark green
    "HONEYDEW": ("#E0E094", "#8AB532"),  # Tan green
    "COTTON CANDY": ("#ffccdb", "#24b9bc"),  # Pink
    "BANANA": ("#f2f1a9", "#bf8040"),  # Yellow
    "BLUEBERRY": ("#003d99", "#995c00"),  # Blue
    "PASSIONFRUIT": ("#7b1157", "#e2e046"),  # Purple
    "COCONUT": ("#965a3e", "#fff2e6"),  # Brown
    "MANGO": ("#f4bb44", "#f46344"),  # Orange
    "LIME": ("#009900", "#ffff66"),  # Lime
    "LEMON": ("#ffff66", "#009900"),  # Yellow
    "PUMPKIN PIE": ("#D97A3B", "#F0A03A"),  # Orange
    "GRAPE": ("#6f2da8", "#E3B8C3"),  # Purple
    "GUAVA": ("#b6c360", "#ec6a4b"),  # Yucky Green
    "TOMATO": ("#ff6347", "#6dc242"),  # Red
    "HONEY": ("#f9c901", "#985b10"),  # Yellow
    "STRAWBERRY MILK": ("#fc5c8c", "#fbd8d8"),  # Pink
}


def create_button(name, color_pair):
    background_color, text_color = color_pair
    return Button(menuWindow,bg=background_color,fg=text_color, text=name, command=lambda: setColor(*color_pair),width=15,relief=RAISED,bd=5)



def makeExport(recipe_id, recipe_name, ingredients, directions):
    filename = f"{recipe_name.replace(' ', '_')}.txt"

    with open(filename, 'w') as file:
        file.write(f"Recipe: {recipe_name}\n")
        file.write(f"Ingredients:\n{ingredients}\n")
        file.write(f"Directions:\n{directions}\n")
    messagebox.showinfo("Export Successful", f"Recipe '{recipe_name}' has been exported to {filename}.")
    on_closing_display_window()


def openImport():
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    #filename = askstring("Import Recipe", "Enter the recipe file name (without extension):")
    if filename:
        #filename = filename.strip() + '.txt'

        if os.path.exists(filename):
            with open(filename, 'r') as file:
                content = file.read()

            lines = content.split("\n")

            if len(lines) >= 3:
                name = lines[0].replace("Recipe: ", "").strip()

                try:
                    ingredients_start = lines.index("Ingredients:") + 1
                    directions_start = lines.index("Directions:") + 1

                    ingredients = "\n".join(lines[ingredients_start:directions_start - 1]).strip()

                    directions = "\n".join(lines[directions_start:]).strip()

                    cursor.execute("INSERT INTO recipes (name, ingredients, directions) VALUES (?, ?, ?)",(name, ingredients, directions))
                    connection.commit()
                    #messagebox.showinfo("Success", f"Recipe '{name}' has been imported successfully.")
                    on_closing_new_window()
                except ValueError:
                    messagebox.showerror("Error","Invalid file format. Ensure the file contains 'Ingredients:' and 'Directions:' sections.")
            else:
                messagebox.showerror("Error","Invalid file format. Ensure the file contains at least Name, Ingredients, and Directions.")
        else:
            messagebox.showerror("Error", f"File '{filename}' not found.")
    else:
        messagebox.showinfo("Import Cancelled", "No file selected for import.")

    update_recipe_list()


def openMenuWindow():
    global menuWindow
    global labelColor

    if menuWindow is not None:
        menuWindow.focus()
        return
    menuWindow = Toplevel(win)
    menuWindow.title("COLOR MENU")
    menuWindow.geometry("400x400")
    menuWindow.resizable(0, 0)
    menuWindow.configure(background=b)
    menuWindow.protocol("WM_DELETE_WINDOW", on_closing_menu_window)

    labelColor = Label(menuWindow, text="COLORWAYS", foreground=f, background=b, font="impact")
    labelColor.grid(row=0, column=1, padx=20, pady=5)

    for i, (name, color_pair) in enumerate(color_map.items()):
        row = 1 + (i // 3)
        col = i % 3
        button = create_button(name, color_pair)
        button.exclude_change = True

        button.grid(row=row, column=col, padx=(3,2), pady=10)


def add_navigation_buttons():
    global current_page
    global search_var

    for widget in frame_navigation.winfo_children():
        widget.destroy()

    cursor.execute("SELECT COUNT(*) FROM recipes")
    total_recipes = cursor.fetchone()[0]
    total_pages = (total_recipes + recipes_per_page - 1) // recipes_per_page

    for page in range(total_pages):
        bubble = Button(frame_navigation, text=str(page + 1), width=2, height=1, bg=f, fg=b, activebackground=b,activeforeground=f,relief=RIDGE, bd=5, font="Bold", command=lambda p=page: go_to_page(p))

        if page == current_page:
            bubble.config(bg=b, fg=f)
        else:
            pass

        bubble.grid(row=0, column=page, padx=5, pady=5)

    if current_page > 0:
        win.prev_button = Button(win, text="Prev",font="bold", height=5, width=10, bg=f, fg=b, activebackground=b,activeforeground=f,relief=RAISED, bd=5,command=previous_page)
        win.prev_button.place(x=20, y=550)
        win.prev_button["state"] = "normal"
    elif current_page == 0:
        if hasattr(win, 'prev_button'):
            win.prev_button["state"] = "disabled"

    if current_page < total_pages - 1:
        win.next_button = Button(win, text="Next",font="bold", height=5, width=10, bg=f, fg=b,activebackground=b,activeforeground=f,relief=RAISED, bd=5, command=next_page)
        win.next_button.place(x=1140, y=550)
        win.next_button["state"] = "normal"
    else:
        if hasattr(win, 'next_button'):
            win.next_button["state"] = "disabled"


def go_to_page(page):
    global current_page
    if win.focus_get() != ent_Search:
        if not search_var.get():
            current_page = page
            update_recipe_list()


def previous_page(event=None):
    global current_page
    if win.focus_get() != ent_Search:
        if not search_var.get():
            if current_page > 0:
                current_page -= 1
                update_recipe_list()


def next_page(event=None):
    global current_page
    if win.next_button['state'] != 'disabled':
        if win.focus_get() != ent_Search:
            if not search_var.get():
                current_page += 1
                update_recipe_list()


def print_database():
    cursor.execute("SELECT * FROM recipes")
    recipes = cursor.fetchall()

    for recipe in recipes:
        recipe_id, name, ingredients, directions = recipe
        print(f"ID: {recipe_id}")
        print(f"Name: {name}")
        print(f"Ingredients: {ingredients}")
        print(f"Directions: {directions}")
        print("-" * 40)


def drop_table():
    confirmation = messagebox.askyesno(
        title="Confirm Deletion",
        message="Are you sure you want to delete all your recipies? This action cannot be undone."
    )
    if confirmation:
        try:
            cursor.execute("SELECT * FROM recipes")
            recipes = cursor.fetchall()
            for recipe in recipes:
                recipe_id, name, ingredients, directions = recipe
                cursor.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
                connection.commit()
            messagebox.showinfo("Recipies Deleted", "Recipies has been deleted successfully.")
            update_recipe_list()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting the recipies: {e}")


def test():
    for x in range(25):
        cursor.execute("INSERT INTO recipes (name, ingredients, directions) VALUES (?, ?, ?)",(x, x, x))
        connection.commit()
        update_recipe_list()


def setColor(b_color, f_color):
    global b, f
    b = b_color
    f = f_color
    saveColor(b, f)
    change()
    add_navigation_buttons()


b, f = loadColor()
win.configure(background=b)
change()

frame = Frame(win, bg=b)
frame.pack(pady=100)

frame_navigation = Frame(win, bg=b)
frame_navigation.pack(pady=10)

update_recipe_list()

labelMain = Label(win, text="COOK BOOK", foreground=f, background=b, font=("impact", 40))
labelMain.place(x=500, y=10)

ent_Search = Entry(win, textvariable=search_var, font=("bold",30), foreground=b, background=f,width=20,relief=RIDGE, bd=10)
ent_Search.place(x=800, y=15)
ent_Search.bind("<KeyRelease>", lambda event: search_recipes())

bt1 = Button(win, text="NEW", height=4, width=8, bg=f, fg=b, activebackground=b,activeforeground=f, command=openNewWindow,relief=RAISED, bd=5)
bt1.place(x=0, y=1)
btP = Button(win, text="PRNT", height=4, width=8, bg=f, fg=b, activebackground=b,activeforeground=f, command=print_database,relief=RAISED, bd=5)
btP.place(x=75, y=1)
btK = Button(win, text="KILL", height=4, width=8, bg=f, fg=b, activebackground=b,activeforeground=f, command=drop_table,relief=RAISED, bd=5)
btK.place(x=150, y=1)
btA = Button(win, text="ADD", height=4, width=8, bg=f, fg=b, activebackground=b,activeforeground=f, command=test,relief=RAISED, bd=5)
btA.place(x=225, y=1)
btM = Button(win, text="MENU", height=4, width=8, bg=f, fg=b, activebackground=b,activeforeground=f, command=openMenuWindow,relief=RAISED, bd=5)
btM.place(x=300, y=1)
win.bind("<Right>", next_page)
win.bind("<Left>", previous_page)
win.bind_all("<Button-1>", lambda event: event.widget.focus_set())
win.resizable(0, 0)
win.mainloop()
connection.close()
