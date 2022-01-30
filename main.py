from argparse import FileType
import tkinter as tk
from tkinter import BOTH, FLAT, GROOVE, LEFT, RAISED, VERTICAL, HORIZONTAL, RIGHT, RIDGE, ttk, Menu, messagebox
import tkinter.filedialog
import os
from PIL import Image, ImageTk
import random
import pickle


HIGHLIGHT = "grey"
NORMAL = "#F0F0F0"
DANGER = "red"

APP = None
LAYER_SCROLL_VIEW = None


class SaveAsTop(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        super(SaveAsTop, self).__init__(args[0], padx=20, pady=40)
        self.geometry("400x200")
        self.title("Save Project")

        self.input_frame = tk.Frame(self)
        self.input_frame.place(x=20, y=0)

        self.location_label = tk.Label(self.input_frame, text="Path")
        self.location_label.grid(row=0, column=0, sticky="w")

        self.location_entry = tk.Entry(self.input_frame, width=30)
        self.location_entry.grid(row=0, column=1, sticky="w", padx=5)

        self.browse_btn = tk.Button(self.input_frame, text="Browse", bd=1, command=self.browse)
        self.browse_btn.grid(row=0, column=2, sticky="w")

        self.label = tk.Label(self.input_frame, text="Filename")
        self.label.grid(row=1, column=0, sticky="w")

        self.file_name_entry = tk.Entry(self.input_frame, width=40)
        self.file_name_entry.grid(row=1, column=1, columnspan=2, sticky="n", padx=5)

        self.btn_frame = tk.Frame(self)
        self.btn_frame.place(x=160, y=100)

        self.cancel_btn = tk.Button(self.btn_frame, text="Cancel", width=10, bd=1, command=self.cancel)
        self.cancel_btn.grid(row=1, column=3)

        self.save_btn = tk.Button(self.btn_frame, text="Save", width=10, bd=1, command=self.save_project)
        self.save_btn.grid(row=1, column=4)

    def browse(self):
        f = tk.filedialog.askdirectory()
        self.location_entry.insert(0, f)
        self.master.project_path = f
        self.tkraise()
    
    def cancel(self):
        self.destroy()

    def save_project(self):
        if self.location_entry.get() != "":
            self.master.project_name = self.file_name_entry.get()
            self.master.save_project()
            self.destroy()

class MyMenu(Menu):
    def __init__(self, master):
        super(MyMenu, self).__init__(master)
        self.master = master
        self.file_menu = Menu(self, tearoff=0)
        self.file_menu.add_command(label="New Project", command=master.new_project)
        self.file_menu.add_command(label="Open Project", command=master.load_project)
        self.file_menu.add_command(label="Save", command=self.master.save_project)
        self.file_menu.add_command(label="Save As", command=self.master.save_project_as)

        self.add_cascade(label='File', menu=self.file_menu, underline=0)

        self.edit_menu = Menu(self, tearoff=0)
        self.edit_menu.add_command(label="Theme")

        self.add_cascade(label="Edit", menu=self.edit_menu, underline=0)


class Config(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(args[0])
        
        self.file_name_label = tk.Label(self, text="File name")
        self.file_name_label.grid(row=0, column=0, sticky='nw')

        self.file_name_input = tk.Entry(self, width=30)
        self.file_name_input.grid(row=0, column=1, columnspan=2, sticky='nw')

        self.collection_size_label = tk.Label(self, text="Collection size")
        self.collection_size_label.grid(row=1, column=0, sticky="nw")

        self.collecion_size = tk.Entry(self, width=30)
        self.collecion_size.grid(row=1, column=1, columnspan=2, sticky='nw')

        self.save_to_label = tk.Label(self, text="Destination")
        self.save_to_label.grid(row=2, column=0, sticky="w")

        self.save_to = tk.Entry(self, width=22)
        self.save_to.grid(row=2, column=1, sticky='w')

        self.save_to_btn = tk.Button(self, bd=1, text="Browse", command=self.browse)
        self.save_to_btn.grid(row=2, column=2, padx=2)

        self.preview = tk.Button(self, text="Preview", bd=1, width=12, command=args[0].master.preview)
        self.preview.grid(row=3, column=0, pady=5)

        self.generate = tk.Button(self, text="Generate", bd=1, width=25, command=kwargs["generate"])
        self.generate.grid(row=3, column=1, columnspan=2, sticky="nw", padx=2, pady=5)

    def browse(self):
        self.save_to.delete(0, 'end')
        f = tk.filedialog.askdirectory()
        self.save_to.insert(0, f)

class MainGrid(tk.Frame):
    def __init__(self, master, **kwargs):
        super(MainGrid, self).__init__(master, relief=GROOVE, bd=1)

        self.master = master

        self.layer_section_frame = LayerSectionFrame(self)
        self.layer_section_frame.place(x=0, y=0)

        self.file_section_frame = tk.Frame(self, width="100", height="400", relief=GROOVE, bd=1)
        self.file_section_frame.place(x=280, y=0)

        self.file_main_container = tk.Frame(self.file_section_frame)
        self.file_main_container.grid(row=0,  column=0, sticky="nsew")

        self.label = tk.Label(self.file_main_container, text="Please add new layer", pady=10)
        self.label.pack()

        self.file_container = ScrollView(self.file_main_container, width=300, height=300, scroll=False)
        self.file_container.pack()

        self.config_frame = Config(self, generate=kwargs["generate"])
        self.config_frame.place(x=300, y=350)

        self.progress = ttk.Progressbar(self, length=585)
        self.progress.place(x=0, y=455)


class PngFiles(tk.Frame):
    def __init__(self, master, path):
        tk.Frame.__init__(self, master, bd=1, relief=RAISED)

        self.path = path
        self.activeVar = tk.IntVar(value=1)

        self.label = tk.Label(self, text=self.path.split('/')[-1], anchor='w', width=18, justify=LEFT)
        self.label.grid(row=0, column=0)

        self.rarity = tk.Scale(self, orient=HORIZONTAL, label="Rarity", from_=1, to=10)
        self.rarity.set(10)
        self.rarity.grid(row=0, column=1, padx=10)

        self.active = tk.Checkbutton(self, variable=self.activeVar)
        self.active.grid(row=0, column=2)


class Layer(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(Layer, self).__init__(args[0], pady=1)
        self.master = args[0]
        self.file_frame = kwargs['file_frame']
        self.path = kwargs['path']
        self.files = []

        self.file_main_container = tk.Frame(self.file_frame)
        self.file_main_container.grid(row=0,  column=0, sticky="nsew")

        self.folder_layer_label = tk.Label(self.file_main_container, text=self.path.split('/')[-1], font=("Roboto", 10), pady=10)
        self.folder_layer_label.pack()

        self.file_container = ScrollView(self.file_main_container, width=284, height=300, scroll=True)
        self.file_container.pack()

        self.layer_name = tk.Button(self, text=self.path.split('/')[-1], bd=1, padx=5, height=2, width=22, anchor="w", justify=LEFT, command=self.select_self)
        self.layer_name.grid(row=0, column=0, sticky='nsew')
        self.layer_name.bind("<Enter>", self.enter_label)
        self.layer_name.bind("<Leave>", self.leave_label)

        self.delete_btn = tk.Button(self, text="Delete", bd=1, width=10, height=2, padx=0, command=self.delete_layer)
        self.delete_btn.grid(row=0, column=4, sticky='nsew')
        self.delete_btn.bind("<Enter>", self.enter_delete_btn)
        self.delete_btn.bind("<Leave>", self.leave_delete_btn)

    def add_files(self):
        for i in [f for f in os.listdir(self.path) if os.path.splitext(f)[-1] == '.png']:
            file = PngFiles(self.file_container.container, f'{self.path}/{i}')
            file.pack(anchor='w')
            self.files.append(file)
        
    def add_file(self, *args, **kwargs):

        file = PngFiles(self.file_container.container, args[0])
        file.pack(anchor='w')
        file.rarity.set(kwargs['rarity'])

        if kwargs["active"]:
            file.active.select()
        else:
            file.active.deselect()
        
        self.files.append(file)
        
    def leave_label(self, instance):
        self.layer_name.config(bg=NORMAL)

    def enter_label(self, instance):
        self.layer_name.config(bg=HIGHLIGHT)

    def enter_delete_btn(self, instance):
        self.delete_btn.config(bg=DANGER)

    def leave_delete_btn(self, instance):
        self.delete_btn.config(bg=NORMAL)


    def delete_layer(self):
        global APP
        APP.layer_folders.pop(APP.layer_folders.index(self))
        self.file_main_container.destroy()
        self.destroy()

        LAYER_SCROLL_VIEW.reupdate()

    def select_self(self):
        self.file_main_container.tkraise()

class LayerSectionFrame(tk.Frame):
    def __init__(self, master):
        global LAYER_SCROLL_VIEW
        super(LayerSectionFrame, self).__init__(master, width=200, relief=GROOVE, bd=1)
        self.master = master

        self.frame = tk.Frame(self, padx=10, pady=10)
        self.frame.pack(fill='x', expand=1)

        self.label = tk.Label(self.frame, text="Layers", width=20, anchor='w',  justify="left")
        self.label.config(font=('Roboto', 13))
        self.label.grid(row=0, column=0, sticky='w')

        self.add_layer_btn = tk.Button(self.frame, text="Add Layer", bd=1, width=10, command=self.master.master.add_layer)
        self.add_layer_btn.grid(row=0, column=1, sticky='e')

        self.layerscrollview = ScrollView(self, width=255, height=400, scroll=True)
        self.layerscrollview.pack(fill='y')

        LAYER_SCROLL_VIEW = self.layerscrollview

class ScrollView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, args[0], relief=RAISED)

        self.WIDTH = kwargs['width']
        self.HEIGHT = kwargs['height']
        
        self.canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)

        if kwargs['scroll']:
            self.scrollbar = tk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
            self.scrollbar.pack(side=RIGHT, fill='y')

            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.container = tk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.container, anchor='nw')

    def reupdate(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("NFT Generator - untitled")
        self.geometry("608x500")
        self.resizable(0, 0)
        self.config(pady=10)
        self.config(padx=10)

        self.project_name = 'untitled'
        self.project_path = ''

        self.menu = MyMenu(self)
        self.config(menu=self.menu)

        self.layer_folders = []

        self.main_frame = MainGrid(self, generate=self.generate)
        self.main_frame.pack(fill=BOTH, expand="yes")


    def new_project(self):
        self.project_name = 'untitled'
        self.title(f'NFT Generator - {self.project_name}')
        self.refresh()


    def save_project(self):
        
        if self.project_path != "":

            data = {
                "project":self.project_name,
                "folders":[
                    {
                        "layer":f.path,
                        "files":[
                            {
                                "path":x.path,
                                "active":x.activeVar.get(),
                                "rarity":x.rarity.get()
                            } for x in f.files
                        ]
                    } for f in self.layer_folders
                ],
                "file_name":self.main_frame.config_frame.file_name_input.get(),
                "destination": self.main_frame.config_frame.save_to.get(),
                "volume":int(self.main_frame.config_frame.collecion_size.get())
            }

            with open("{}/{}.sc".format(self.project_path, self.project_name), "wb") as project:
                pickle.dump(data, project)

            self.title(f"NFT Generator - {self.project_name}")

            messagebox.showinfo("Success", "Your project has been saved")
        
        else:
            self.save_project_as()


    def save_project_as(self):
        save = SaveAsTop(self)

    
    def refresh(self):
        global LAYER_SCROLL_VIEW

        # delete all layers and filse
        while len(self.layer_folders) > 0:
            self.layer_folders[0].delete_layer()

        self.main_frame.config_frame.collecion_size.delete(0, "end") # collection size
        self.main_frame.config_frame.save_to.delete(0, "end")
        self.main_frame.config_frame.file_name_input.delete(0,"end")


    def load_project(self):
        global LAYER_SCROLL_VIEW

        f = tk.filedialog.askopenfilename()

        if f == "":
            return
            
        if f.split('.')[-1] != "sc":
            messagebox.showerror("Innvalid File", "Unsupported file")
            return

        self.refresh()

        with open(f, "rb") as raw:
            data = pickle.load(raw)

        for d in data["folders"]:
            new_layer = Layer(LAYER_SCROLL_VIEW.container, path=d["layer"], file_frame=self.main_frame.file_section_frame)#, self.second_frame_right, self.left_container.reupdate, self)
            new_layer.pack(padx=5)

            self.layer_folders.append(new_layer)
            self.selected_leyer = new_layer
        
            # update scrollbar
            LAYER_SCROLL_VIEW.reupdate()

            # load file rarity and visibility
            for file in d["files"]:
                new_layer.add_file(file['path'], rarity=file['rarity'], active=file["active"])

        # load project configuration
        self.main_frame.config_frame.collecion_size.insert(0, data["volume"]) # collection size
        self.main_frame.config_frame.save_to.insert(0, data["destination"])
        self.main_frame.config_frame.file_name_input.insert(0, data["file_name"])

        self.title("NFT Generator - {}".format(data["project"]))        
    def generate(self):
        volume = int(self.main_frame.config_frame.collecion_size.get()) # collection size
        save_to_path = self.main_frame.config_frame.save_to.get()
        file_name = self.main_frame.config_frame.file_name_input.get()
        progress = self.main_frame.progress

        if len(self.layer_folders) == 0:
            messagebox.showwarning("Warning", "Please create layers")
        if volume == "":
            messagebox.showerror("Input Error", "Please fill collection size")
        if save_to_path == "":
            messagebox.showerror('Invalid path', "Please fill save to path")
            return
        if not os.path.isdir(save_to_path):
            messagebox.showerror("Invalid path", "Directory doesn't exist")
            return

        for i in range(volume):
            
            images1 = [f.path for f in self.layer_folders[0].files if f.activeVar.get() == 1]

            # collect rarity value of each png file from two layers
            images1_rarity = [m.rarity.get() for m in self.layer_folders[0].files if m.activeVar.get() == 1]
            # get random image from a layer base on rarity value
            img1 = Image.open(random.choices(images1, weights=images1_rarity)[0], mode="r", formats=None)

            for j in range(1, len(self.layer_folders)):
                images2 = [f.path for f in self.layer_folders[j].files if f.activeVar.get() == 1]
                images2_rarity = [m.rarity.get() for m in self.layer_folders[j].files if m.activeVar.get() == 1]
                
                img2 = Image.open(random.choices(images2, weights=images2_rarity)[0], mode="r", formats=None)

                # combine the two images
                intermediate = Image.alpha_composite(img1, img2)
                img1 = intermediate
                self.update_idletasks()

            # commplete the image
            img1.save('{}/{}{}.png'.format(save_to_path, file_name, str(i+1)))

            progress['value'] = 100 / (volume / (i+1))
            self.update_idletasks()

        messagebox.showinfo("Successful", "Generating NFT has been completed")
        progress['value'] = 0


    def preview(self):
        images = [img.path for img in self.layer_folders[0].files]
        img1 = Image.open(random.choice(images))

        for i in range(1, len(self.layer_folders)):
            images = [img.path for img in self.layer_folders[i].files]
            img2 = Image.open(random.choice(images))
            
            intermediate = Image.alpha_composite(img1, img2)
            img1 = intermediate

        img1.save("preview.png")

        prev_win = tk.Toplevel(self)

        image = Image.open("preview.png")

        rezised_img = image.resize((200, 200), Image.ANTIALIAS)
        new_image = ImageTk.PhotoImage(rezised_img)

        canvas = tk.Label(prev_win, image=new_image)
        canvas.image = new_image
        canvas.pack()


    def add_layer(self):
        f = tk.filedialog.askdirectory()
        frame = self.main_frame.layer_section_frame.layerscrollview

        # check if directory exist and has png files
        if os.path.isdir(f) and len([x for x in os.listdir(f) if os.path.splitext(x)[-1] == '.png']) > 0:
            new_layer = Layer(frame.container, path=f, file_frame=self.main_frame.file_section_frame)#, self.second_frame_right, self.left_container.reupdate, self)
            new_layer.pack(padx=5)

            self.layer_folders.append(new_layer)
            self.selected_leyer = new_layer

            # add all files for this folder to the app:
            new_layer.add_files()
        
            # update scrollbar
            frame.reupdate()
        else:
            messagebox.showerror("Empty FIle", "There is no png file in this folder")



if __name__ == "__main__":
    app = App()
    APP = app
    app.mainloop()