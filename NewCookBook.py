from tkinter import *
from tkinter import ttk
import sqlite3
from tkinter import messagebox

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
win.geometry("630x400+400+150")
win.title("COOKBOOK")
win.configure(background=b)

search_var = StringVar()

def search_recipes():
    global current_page
    current_page = 0
    search_query = search_var.get().lower()
    if search_query:
        cursor.execute("SELECT * FROM recipes WHERE name LIKE ?", ('%' + search_query + '%',))
        recipes = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM recipes LIMIT ? OFFSET ?", (recipes_per_page, current_page * recipes_per_page))
        recipes = cursor.fetchall()

    update_recipe_list(recipes)

def saveColor(background, foreground):
    cursor.execute("INSERT INTO colors (background_color, foreground_color) VALUES (?, ?)",
                   (background, foreground))
    connection.commit()

def loadColor():
    cursor.execute("SELECT * FROM colors ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    if result:
        return result[1], result[2]  # Return the background and foreground colors
    else:
        return "black", "white"

def on_closing_new_window():
    global newWindow
    if newWindow is not None:
        newWindow.destroy()
        newWindow=None

def on_closing_edit_window():
    global editWindow
    if editWindow is not None:
        editWindow.destroy()
        editWindow=None

def on_closing_display_window():
    global displayWindow
    if displayWindow is not None:
        displayWindow.destroy()
        displayWindow=None

def on_closing_menu_window():
    global menuWindow
    if menuWindow is not None:
        menuWindow.destroy()
        menuWindow=None
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

    Label(newWindow,text="NEW RECIPE", background=b, foreground=f, font="impact").pack()

    lbl_newName = ttk.Label(newWindow, text="Name:", background=b, foreground=f, font="impact")
    lbl_newName.place(relx=0.25, rely=0.1,anchor=CENTER)
    ent_newName = ttk.Entry(newWindow)
    ent_newName.pack(pady=5)

    Label(newWindow, text="Ingredients:", background=b, foreground=f, font="bold").pack()

    ent_ingredients = Text(newWindow, width=30, height=5)
    ent_ingredients.pack(pady=5, padx=10, fill=BOTH, expand=True)

    Label(newWindow, text="Directions:", background=b, foreground=f, font="bold").pack()

    ent_directions = Text(newWindow, width=30, height=5)
    ent_directions.pack(pady=5, padx=10, fill=BOTH, expand=True)
    newWindow.protocol("WM_DELETE_WINDOW", on_closing_new_window)

    def add_recipe():
        recipe_name = ent_newName.get()
        recipe_ingredients = ent_ingredients.get("1.0", END)
        recipe_directions = ent_directions.get("1.0", END)
        cursor.execute("INSERT INTO recipes (name, ingredients, directions) VALUES (?, ?, ?)",
                       (recipe_name, recipe_ingredients, recipe_directions))
        connection.commit()
        on_closing_new_window()
        update_recipe_list()

    btt_Add = ttk.Button(newWindow, text="Add", command=add_recipe)
    btt_Add.pack(pady=5)

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

        Label(editWindow, text="Edit Recipe", background=b, foreground=f, font="impact").pack()

        lbl_name = ttk.Label(editWindow, text="Name:", background=b, foreground=f, font="impact")
        lbl_name.place(relx=0.25, rely=0.1, anchor=CENTER)
        ent_name = ttk.Entry(editWindow)
        ent_name.insert(END, recipe_name)
        ent_name.pack(pady=5)

        Label(editWindow, text="Ingredients:", background=b, foreground=f, font="bold").pack()

        ent_ingredients = Text(editWindow, width=30, height=5)
        ent_ingredients.insert(END, ingredients)
        ent_ingredients.pack(pady=5, padx=10, fill=BOTH, expand=True)

        Label(editWindow, text="Directions:", background=b, foreground=f, font="bold").pack()

        ent_directions = Text(editWindow, width=30, height=5)
        ent_directions.insert(END, directions)
        ent_directions.pack(pady=5, padx=10, fill=BOTH, expand=True)
        editWindow.protocol("WM_DELETE_WINDOW", on_closing_edit_window)

        def save_changes():
            new_recipe_name = ent_name.get()
            new_ingredients = ent_ingredients.get("1.0", END)
            new_directions = ent_directions.get("1.0", END)

            cursor.execute("UPDATE recipes SET name=?, ingredients=?, directions=? WHERE id=?",
                           (new_recipe_name, new_ingredients, new_directions, recipe_id))
            connection.commit()
            on_closing_display_window()
            on_closing_edit_window()
            update_recipe_list()

        btt_Save = ttk.Button(editWindow, text="Save", command=save_changes)
        btt_Save.pack(pady=5)

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

    Label(displayWindow, text=f"Name: {recipe_name}", background=b,foreground=f, font="impact").pack()

    Label(displayWindow, text="Ingredients:", background=b, foreground=f, font="bold").pack()

    ent_ingredients = Text(displayWindow, width=30, height=5)
    ent_ingredients.insert(END, ingredients)
    ent_ingredients.config(state='disabled')
    ent_ingredients.pack(pady=5, padx=10, fill=BOTH, expand=True)

    Label(displayWindow, text="Directions:", background=b, foreground=f, font="bold").pack()

    ent_directions = Text(displayWindow, width=30, height=5)
    ent_directions.insert(END, directions)
    ent_directions.config(state='disabled')
    ent_directions.pack(pady=5, padx=10, fill=BOTH, expand=True)

    btt_Edit = ttk.Button(displayWindow, text="Edit", command=edit_recipe)
    btt_Edit.pack(pady=5)

    btt_Delete = ttk.Button(displayWindow, text="Delete", command=delete_recipe)
    btt_Delete.pack(pady=5)
    displayWindow.protocol("WM_DELETE_WINDOW", on_closing_display_window)

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
        recipe_button = ttk.Button(frame, text=recipe_name, command=lambda recipe=recipe: display_recipe(*recipe), width=25, padding=(10,10))
        recipe_button.grid(row=row_count, column=column_count, padx=10, pady=5)
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
                if 'background' in widget.keys():
                    widget.configure(background=b)
                if 'foreground' in widget.keys():
                    widget.configure(foreground=f)
                if isinstance(widget, Text):
                    widget.configure(foreground="black")
                    widget.configure(background="white")
                if isinstance(widget, Entry):
                    widget.configure(foreground="Black")

color_map = {
    "COTTON CANDY": ("#ffccdb", "#24b9bc"),
    "BANANA": ("#f2f1a9", "#bf8040"),
    "MATCHA": ("#8EB288", "#3a4a37"),
    "COFFEE": ("#6f4e37", "#f3e9dc"),
    "MANGO": ("#f4bb44", "#f46344"),
    "WATERMELON": ("#ff6666", "#1c5c0e"),
    "BLUEBERRY": ("#003d99", "#995c00"),
    "PASSIONFRUIT": ("#7b1157", "#e2e046"),
    "OREO": ("#4d4a4b", "#eceaea"),
    "LIME": ("#009900", "#ffff66"),
    "LEMON": ("#ffff66", "#009900"),
    "HONEY": ("#985b10", "#e79a3f"),
    "GUAVA": ("#b6c360", "#ec6a4b"),
    "TOMATO": ("#ff6347", "#6dc242"),
    "COCONUT": ("#965a3e", "#fff2e6"),
    "HONEYDEW": ("#ccffcc", "#00cc00"),
    "PIZZA": ("#ffbf00", "red"),
}

def create_button(name, color_pair):
    return ttk.Button(menuWindow, text=name, command=lambda: set_color(*color_pair))

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
    labelColor.grid(row=0, column=1, padx=20, pady=10)

    for i, (name, color_pair) in enumerate(color_map.items()):
        row = 1 + (i // 3)  # Start from row 1 (to leave row 0 for the title)
        col = i % 3  # Place buttons in 3 columns
        button = create_button(name, color_pair)
        button.grid(row=row, column=col, padx=20, pady=10)
      
def add_navigation_buttons():
    global current_page
    global search_var

    search_query = search_var.get().lower()

  
    for widget in frame_navigation.winfo_children():
        widget.destroy()

    if current_page > 0:
        win.prev_button = Button(win, text="Prev", height=4, width=8, bg="light gray", fg="black", activebackground="blue", command=previous_page)
        win.prev_button.place(x=30, y=300)
        win.prev_button["state"]="normal"
    elif current_page==0:
        if hasattr(win, 'prev_button'):
            win.prev_button["state"]="disabled"


    cursor.execute("SELECT COUNT(*) FROM recipes")
    total_recipes = cursor.fetchone()[0]
    total_pages = (total_recipes + recipes_per_page - 1) // recipes_per_page
    if current_page < total_pages-1:
        win.next_button = Button(win, text="Next", height=4, width=8, bg="light gray", fg="black",activebackground="blue", command=next_page)
        win.next_button.place(x=550, y=300)
        win.next_button["state"] = "normal"
    else:
        if hasattr(win, 'next_button'):
            win.next_button["state"] = "disabled"
    if search_query:
        try:
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE name LIKE ?", ('%' + search_query + '%',))
            win.next_button["state"] = "disabled"
            win.prev_button["state"] = "disabled"
        except Exception as e:
            print(e)
    else:
        cursor.execute("SELECT COUNT(*) FROM recipes")


def previous_page():
    global current_page
    if current_page > 0:
        current_page -= 1
        update_recipe_list()

def next_page():
    global current_page
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
            cursor.execute("DROP TABLE recipes")
            messagebox.showinfo("Recipies Deleted", "Recipies has been deleted successfully.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting the recipies: {e}")

def test():
    for x in range(25):
        cursor.execute("INSERT INTO recipes (name, ingredients, directions) VALUES (?, ?, ?)",
                       (x, x, x))
        connection.commit()
        update_recipe_list()
      
def setColor(b_color, f_color):
    global b, f
    b = b_color
    f = f_color
    saveColor(b, f)  # Save the color to the database
    change()

b, f = loadColor()
win.configure(background=b)
change()

frame = Frame(win, bg=b)
frame.pack(pady=50)

frame_navigation = Frame(win, bg=b)
frame_navigation.pack(pady=10)

update_recipe_list()

labelMain = Label(win, text="COOK BOOK", foreground=f, background=b, font=("impact", 20))
labelMain.place(x=240, y=10)

ent_Search = ttk.Entry(win, textvariable=search_var)
ent_Search.place(x=450,y=20)
ent_Search.bind("<KeyRelease>", lambda event: search_recipes())

bt1 = Button(win, text="+", height=2, width=4, bg=f, fg=b, activebackground="blue", command=openNewWindow)
bt1.place(x=0, y=1)
bt2 = Button(win, text="PRNT", height=2, width=4, bg=f, fg=b, activebackground="blue", command=print_database)
bt2.place(x=40, y=1)
bt3 = Button(win, text="KILL", height=2, width=4, bg=f, fg=b, activebackground="blue", command=drop_table)
bt3.place(x=80, y=1)
bt4 = Button(win, text="ADD", height=2, width=4, bg=f, fg=b, activebackground="blue", command=test)
bt4.place(x=120, y=1)
btM = Button(win, text="MENU", height=2, width=4, bg=f",fg=b, activebackground="blue", command=openMenuWindow)
btM.place(x=160, y=1)

win.resizable(0, 0)
win.mainloop()

connection.close()
