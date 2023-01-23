from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
from functools import partial
import os, json, shutil, webbrowser, urllib.request

# Tkinter base
root = Tk()

root.title("AppLibrary")
root.geometry("750x700")
root.resizable(False, False)

creator = "jvietman"

# Functions
def loadimage(file, size):
    return ImageTk.PhotoImage(Image.open(file).resize(size))

def pack(folder):
    if os.path.exists(os.getcwd()+"/data/presets/"+folder+"/"+folder+".zip"):
        os.remove(os.getcwd()+"/data/presets/"+folder+"/"+folder+".zip")
    shutil.make_archive(os.getcwd()+"/data/presets/"+folder, 'zip', os.getcwd()+"/data/presets/"+folder)
    shutil.move(os.getcwd()+"/data/presets/"+folder+".zip", os.getcwd()+"/data/presets/"+folder)

## Create new app
def new():
    global data, applist

    win = Toplevel(root)

    win.title("New app")
    win.geometry("700x500")
    win.resizable(False, False)
    win.configure(bg=colors["bg"])

    name = Entry(win, width=17, bg=colors["fg"], font=("", 20), border=0)
    name.place(anchor=NW, relx=0.05, rely=0.05)
    name.insert(0, "name")
    author = Entry(win, width=17, bg=colors["fg"], font=("", 20), border=0)
    author.place(anchor=NW, relx=0.05, rely=0.15)
    author.insert(0, "author")
    description = Text(win, width=40, height=9, bg=colors["fg"], font=("", 13), border=0)
    description.place(anchor=NW, relx=0.05, rely=0.25)
    def cap(e):
        l = description.get("1.0",'end-1c')
        if len(l) >= 360:
            description.delete('1.0', END)
            description.insert(END, l[:360])
    description.bind("<Key>", cap)

    def newbanner():
        global file

        win.withdraw()
        f=filedialog.askopenfilename(
            title = "Select a banner image (must be 1000x1500 pixels)",
            filetypes = (("JPEG", "*.jpg *.jpeg *.jpe *.jfif *.exif"), ("PNG", "*.png"))
        )
        win.deiconify()
        if not len(f) <= 0:
            file = f
            appbanner = loadimage(file, (int(banner[0]*1.3), int(banner[1]*1.3)))
            imgbtn = Button(win, bg=colors["bg"], activebackground=colors["bg"], image=appbanner, border=0, command=newbanner)
            imgbtn.image = appbanner
            imgbtn.place(anchor=NE, relx=0.95, rely=0.05)

    file = "data/image.png"
    path = ""

    def createapp():
        global path, file, applist

        try:
            print(path)
        except:
            win.withdraw()
            messagebox.showerror('Error', 'You did not select an executable.')
            win.deiconify()
            return
        
        try:
            print(file)
        except:
            win.withdraw()
            messagebox.showerror('Error', 'You did not select a banner.')
            win.deiconify()
            return
        
        if not os.path.exists(path):
            win.withdraw()
            messagebox.showerror('Error', 'The path for the executable does not exist.')
            win.deiconify()
            return
        
        filters = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
        filtered = name.get()
        for f in filters:
            filtered = filtered.replace(f, "")
        
        if os.path.exists(os.getcwd()+"/data/presets/"+filtered):
            win.withdraw()
            messagebox.showerror('Error', 'An app with the name "'+filtered+'" already exists.')
            win.deiconify()
            return

        app = {
            "name": name.get(),
            "author": author.get(),
            "description": description.get("1.0",'end-1c'),
            "banner": "data/presets/"+filtered+"/"+os.path.basename(file),
            "path": path,
            "exec": execmd.get()
        }

        os.mkdir(os.getcwd()+"/data/presets/"+filtered)
        shutil.copy(file, os.getcwd()+"/data/presets/"+filtered)
        with open(os.getcwd()+"/data/presets/"+filtered+"/app.json", "w") as f:
            json.dump(app, f)
            f.close()
        pack(filtered)

        data.append(app)
        print(data)
        applist.append(filtered)
        loadlist(applist)
        loadapps()
        win.destroy()

    def importapp():
        win.withdraw()
        preset=filedialog.askopenfilename(
            title = "Select a preset zip file",
            filetypes = [("zip-archive", "*.zip")]
        )
        win.deiconify()
        if not len(preset) <= 0:
            pname = os.path.splitext(os.path.basename(preset))[0]

            if os.path.exists(os.getcwd()+"/data/presets/"+pname):
                win.withdraw()
                messagebox.showerror('Error', 'An app with the name "'+pname+'" already exists.')
                win.deiconify()
                return

            shutil.unpack_archive(preset, os.getcwd()+"/data/presets/"+pname)
            shutil.copy(preset, os.getcwd()+"/data/presets/"+pname)
            with open(os.getcwd()+"/data/presets/"+pname+"/app.json", "r") as f:
                tmpdata = json.load(f)
                f.close()
            applist.append(tmpdata["name"])
            loadlist(applist)
            loadapps()
            win.destroy()

    def exe():
        global path

        win.withdraw()
        p=filedialog.askopenfilename(
            title = "Select an executable",
            filetypes = (("Executable", "*.exe"), ("Python", "*.py *.pyw"))
        )
        win.deiconify()
        if not len(p) <= 0:
            path = p
            ext = os.path.splitext(os.path.basename(path))[1]
            if ext == ".exe":
                execmd.delete(0, END)
                execmd.insert(END, '"'+path+'"')
            elif ext == ".py" or ext == ".pyw":
                execmd.delete(0, END)
                execmd.insert(END, 'python "'+path+'"')
            pathlbl["text"] = os.path.basename(path)

    execmd = Entry(win, width=30, bg=colors["fg"], font=("", 15), border=0)
    execmd.place(anchor=NW, relx=0.05, rely=0.65)
    execmd.insert(END, 'startup command')

    exebtn = Button(win, text="Choose executable", width=15, font=("", 15), bg=colors["fg"], activebackground=colors["bg"], border=0, command=exe)
    exebtn.place(anchor=NW, relx=0.05, rely=0.75)
    pathlbl = Label(win, text="", font=("", 15), bg=colors["bg"], fg=colors["fg"])
    pathlbl.place(anchor=NW, relx=0.32, rely=0.75)

    createbtn = Button(win, text="Create", width=10, font=("", 15), bg=colors["fg"], activebackground=colors["bg"], border=0, command=createapp)
    createbtn.place(anchor=NW, relx=0.05, rely=0.85)

    importbtn = Button(win, text="Import", width=10, font=("", 15), bg=colors["fg"], activebackground=colors["bg"], border=0, command=importapp)
    importbtn.place(anchor=NW, relx=0.25, rely=0.85)

    appbanner = loadimage(file, (int(banner[0]*1.3), int(banner[1]*1.3)))
    imgbtn = Button(win, bg=colors["bg"], activebackground=colors["bg"], image=appbanner, border=0, command=newbanner)
    imgbtn.image = appbanner
    imgbtn.place(anchor=NE, relx=0.95, rely=0.05)

## Start app
def start(index, e):
    if len(data[index]["path"]) <= 0 or not os.path.exists(data[index]["path"]):
        messagebox.showerror('Error', 'No executable given or not found.')
        return
    root.withdraw()
    tmp = os.getcwd()
    os.chdir(os.path.dirname(data[index]["path"]))
    os.system(data[index]["exec"])
    os.chdir(tmp)
    root.deiconify()

## Display app info
def info(index, e):
    global data, applist

    win = Toplevel(root)

    win.title(data[index]["name"]+" by "+data[index]["author"])
    win.geometry("700x500")
    win.resizable(False, False)
    win.configure(bg=colors["bg"])

    img = loadimage(data[index]["banner"], (int(banner[0]*1.3), int(banner[1]*1.3)))
    imglbl = Label(win, bg=colors["bg"], image=img)
    imglbl.image = img
    imglbl.place(anchor=NW, relx=0.05, rely=0.05)
    name = Label(win, text=data[index]["name"], bg=colors["bg"], fg=colors["fg"], font=("", 25))
    name.place(anchor=W, relx=0.5, rely=0.15)
    author = Label(win, text="by "+data[index]["author"], bg=colors["bg"], fg=colors["fg"], font=("", 10))
    author.place(anchor=W, relx=0.5, rely=0.2)

    desc = Label(win, text=data[index]["description"][:360], wraplength=500, justify=LEFT, bg=colors["bg"], fg=colors["fg"], font=("", 12))
    desc.place(anchor=NW, relx=0.05, rely=0.6)

    def delapp():
        global applist

        win.withdraw()
        msg = messagebox.askquestion('Delete App', 'Are you sure you want to delete this app?',
            icon='warning')
        win.deiconify()
        if msg == 'yes':
            if os.path.exists(os.path.dirname(data[index]["banner"])):
                shutil.rmtree(os.path.dirname(data[index]["banner"]))
            del data[index], applist[index]
            loadlist(applist)
            loadapps()
            win.destroy()

    def applypath():
        data[index]["path"] = path.get()
        data[index]["exec"] = exec.get()
        with open("data/presets/"+applist[index]+"/app.json", "w") as f:
            json.dump(data[index], f)
            f.close()
        pack(applist[index])

    pathlbl = Label(win, text="path and startup command:", bg=colors["bg"], fg=colors["fg"], font=("", 12))
    pathlbl.place(anchor=SW, relx=0.05, rely=0.85)
    path = Entry(win, width=35, bg=colors["fg"], font=("", 13), border=0)
    path.place(anchor=SW, relx=0.05, rely=0.91)
    path.insert(END, data[index]["path"])
    exec = Entry(win, width=35, bg=colors["fg"], font=("", 13), border=0)
    exec.place(anchor=SW, relx=0.05, rely=0.96)
    exec.insert(END, data[index]["exec"])
    apply = Button(win, text="Apply", width=10, font=("", 15), bg=colors["fg"], activebackground=colors["bg"], border=0, command=applypath)
    apply.place(anchor=SW, relx=0.55, rely=0.95)

    img = loadimage("data/clear.png", (50, 50))
    delbtn = Button(win, text="Delete", width=10, font=("", 15), bg=colors["fg"], activebackground=colors["bg"], border=0, command=delapp)
    delbtn.image = img
    delbtn.place(anchor=SE, relx=0.95, rely=0.95)

## Open about & help page
def about(e):
    win = Toplevel(root)

    win.title("About & Help")
    win.geometry("700x500")
    win.resizable(False, False)
    win.configure(bg=colors["bg"])

    if os.path.exists("imgs/data.jpg"): os.remove("data/avatar.jpg")
    urllib.request.urlretrieve("https://avatars.githubusercontent.com/u/77661493?v=4", 'data/avatar.jpg')
    while not os.path.exists("data/avatar.jpg"):
        pass

    icon = loadimage("data/avatar.jpg", (200, 200))
    github = loadimage("data/github.png", (40, 40))

    logo = Label(win, image=icon)
    logo.image = icon
    logo.place(anchor=W, relx=0.1, rely=0.3)

    info = Label(win, text="AppLibrary", bg=colors["bg"], fg=colors["fg"], font=("", 15))
    info.place(anchor=W, relx=0.1, rely=0.6)
    author = Label(win, text="Made by "+creator, bg=colors["bg"], fg=colors["fg"], font=("", 10))
    author.place(anchor=W, relx=0.1, rely=0.65)

    linkbtn = Button(win, image=github, width=100, bg=colors["fg"], activebackground=colors["bg"], border=0, command=lambda: webbrowser.open("https://github.com/"+creator))
    linkbtn.image = github
    linkbtn.place(anchor=W, relx=0.1, rely=0.8, relheight=0.1)

    helplbl = Label(win, text="Help:", bg=colors["bg"], fg=colors["fg"], font=("", 15))
    helplbl.place(anchor=NW, relx=0.5, rely=0.3)
    cmdslbl = Label(win, text="Left click = Start app\nMiddle click = Move app one to the right\nRight click = Display and change info about app", justify=LEFT, bg=colors["bg"], fg=colors["fg"], font=("", 12))
    cmdslbl.place(anchor=NW, relx=0.5, rely=0.35)

# Load json
def loadlist(applist):
    global data

    with open("data/apps.json", "w") as f:
        json.dump(applist, f)
        f.close()

    data = []
    for a in applist:
        with open("data/presets/"+a+"/app.json") as f:
            data.append(json.load(f))
            f.close()

with open("data/apps.json", "r") as f:
    applist = json.load(f)
    loadlist(applist)
    f.close()

with open("data/colors.json", "r") as f:
    colors = json.load(f)
    f.close()
root.configure(bg=colors["bg"])

# Load apps
banner = (150, 200)

def loadapps():
    global banner, apps, newbtn, applist

    if 'apps' in globals():
        for a in apps:
            a.destroy()
    apps = []
    if 'newbtn' in globals():
        newbtn.destroy()
    posx = 0.15
    posy = 120

    for i in data:
        img = loadimage(i["banner"], banner)
        apps.append(Button(root, bg=colors["bg"], activebackground=colors["bg"], image=img, border=0))
        apps[len(apps)-1].image = img
        apps[len(apps)-1].place(anchor=CENTER, relx=posx, y=posy)

        def swap(index, e):
            global applist

            if len(applist) >= index:
                applist[index], applist[index+1] = applist[index+1], applist[index]
                loadlist(applist)
                loadapps()
        start_i = partial(start, len(apps)-1)
        swap_i = partial(swap, len(apps)-1)
        info_i = partial(info, len(apps)-1)
        apps[len(apps)-1].bind("<Button-1>", start_i)
        apps[len(apps)-1].bind("<Button-2>", swap_i)
        apps[len(apps)-1].bind("<Button-3>", info_i)
        posx += 0.225
        if posx >= 0.85:
            posx = 0.15
            posy += 220
    img = loadimage("data/new.png", banner)
    newbtn = Button(root, bg=colors["bg"], activebackground=colors["bg"], image=img, border=0, command=new)
    newbtn.image = img
    newbtn.place(anchor=CENTER, relx=posx, y=posy)
loadapps()

root.bind("<Escape>", about)
root.mainloop()