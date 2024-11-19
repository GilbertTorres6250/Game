from tkinter import *
from tkinter import ttk
import sqlite3

newWindow = None
editWindow = None
displayWindow = None
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

win = Tk()
win.geometry("630x400+400+150")
win.title("Cooking Compass")
win.configure(background=b)


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

# PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE PAGE
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

    btt_Conv = ttk.Button(newWindow, text="Add", command=add_recipe)
    btt_Conv.pack(pady=5)

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

def update_recipe_list():
    global current_page

    cursor.execute("SELECT * FROM recipes LIMIT ? OFFSET ?", (recipes_per_page, current_page * recipes_per_page))
    recipes = cursor.fetchall()

    for widget in frame.winfo_children():
        widget.destroy()

    row_count = 0
    column_count = 0

    for recipe in recipes:
        recipe_id, recipe_name, _, _ = recipe
        recipe_button = ttk.Button(frame, text=recipe_name, command=lambda recipe=recipe: display_recipe(*recipe), width=30)
        recipe_button.grid(row=row_count, column=column_count, padx=5, pady=5)
        column_count += 1
        if column_count == 3:
            column_count = 0
            row_count += 1

    add_navigation_buttons()

def add_navigation_buttons():
    global current_page

    for widget in frame_navigation.winfo_children():
        widget.destroy()

    if current_page > 0:
        prev_button = ttk.Button(frame_navigation, text="Previous", command=previous_page)
        prev_button.grid(row=0, column=0, padx=5, pady=5)

    cursor.execute("SELECT COUNT(*) FROM recipes")
    total_recipes = cursor.fetchone()[0]
    if (current_page + 1) * recipes_per_page < total_recipes:
        next_button = ttk.Button(frame_navigation, text="Next", command=next_page)
        next_button.grid(row=0, column=1, padx=5, pady=5)

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


frame = Frame(win, bg=b)
frame.pack(pady=50)

frame_navigation = Frame(win, bg=b)
frame_navigation.pack(pady=10)

update_recipe_list()

labelMain = Label(win, text="Here are your recipes", foreground=f, background=b, font=("impact", 20))
labelMain.place(x=160, y=5)

bt1 = Button(win, text="+", height=2, width=4, bg="light gray", fg=b, activebackground="blue", command=openNewWindow)
bt1.place(x=0, y=1)
bt2 = Button(win, text="PRNT", height=2, width=4, bg="light gray", fg=b, activebackground="blue", command=print_database)
bt2.place(x=40, y=1)


win.resizable(0, 0)
win.mainloop()

connection.close()
