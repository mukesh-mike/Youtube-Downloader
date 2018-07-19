from Tkinter import *
from pytube import *
import tkMessageBox
from tkFileDialog import *
import threading
import ttk
from time import *
import requests
from PIL import ImageTk,Image


#Create Widgets in the main Frame
def create_widgets_in_frame1():

    Label(frame1, text="Enter the YouTube URL : ").grid(row=0, column=0, padx=4)
    url = Entry(frame1, width=43)
    url.grid(row=0, column=1)
    global submit_button
    submit_button = Button(frame1, text="submit",command=lambda:remove(url.get()))
    submit_button.grid(row=1, column=0,pady=5)


#Deletes modules from frame2 whenever a new url is entered by user
def remove(link):
    if i.get() > 0 :
        popupMenu.grid_remove()
        download_button.grid_remove()
        pathlabel.grid_remove()
        browsebutton.grid_remove()
        frame2_label.grid_remove()
        pathlb.grid_remove()


    check_link(link)
    i.set(i.get()+1)


# Verifies YouTube URl
def check_link(link):
    try:
        # object creation using YouTube which was imported in the beginning

        global yt
        yt = YouTube(link,on_complete_callback=display_complete)
        global files
        files = yt.streams.filter(progressive=True, file_extension='mp4').order_by("res").all()
        files_audio = yt.streams.filter(only_audio=True, file_extension='mp4').all()
        for j in range(0, len(files_audio)):
            files.append(files_audio[j])

        #print files
        global choices
        choices = get_list(files)
        #print choices

    except:
        connection_err()

    create_widgets_in_frame2()



# Shows Connection Error Whenever a url other than youtube's is submitted by user
def connection_err():
    tkMessageBox.showinfo(
        "Message",
        "Connection Error!!!"
    )



def get_list(file1):
    #l = len(files)
    choice = {}
    for j in range(0,len(file1)):
        size = "{:.2f}".format(file1[j].filesize/1048576.0)
        mp4 = str(file1[j])
        temp = mp4.split('"')
        v_res = temp[5]
        mp5 = str(temp[3])
        temp2 = mp5.split("/")
        if temp2[0] == "audio":
            v_ext = "mp3"
        else:
            v_ext = "mp4"

        v_entry = v_ext + "     " + v_res +"     "+size+" MB"
        choice[v_entry] = j
    return choice



#Creates Second Frame
def create_widgets_in_frame2():
    global tpp
    tpp = StringVar(root)
    tpp.set("<Download_path>") #Set default path where videos/audios will be downloaded
    global tkvar
    tkvar = StringVar(root)
    tkvar.set("")
    frame2.pack(fill=X)

    global popupMenu
    popupMenu = OptionMenu(frame2,tkvar,*choices)
    popupMenu.grid(row=2, column=2, padx=4, sticky=E)
    global frame2_label
    frame2_label = Label(frame2, text="Choose quality :")
    frame2_label.grid(row=2, column=2, sticky=W)
    global download_button
    download_button = Button(frame2, text="download",command=lambda :download_file(tkvar,files,choices,tpp))
    download_button.grid(row=2, column=3)
    global pathlabel
    pathlabel = Label(frame2, text="Path: ")
    pathlabel.grid(row=1, column=1, sticky=E)
    global browsebutton
    browsebutton = Button(frame2, text="Browse", command=browsefunc)
    browsebutton.grid(row=1, column=3, padx=10)
    global pathlb
    pathlb = Label(frame2, textvariable=tpp, width=43, borderwidth=2, relief="ridge")
    pathlb.grid(row=1, column=2)


#Enables Browse option for user
def browsefunc():
    filename = askdirectory()
    tpp.set(filename)



def download_file(tkvar1,files1,choices1,tpp1):
    quality_select = tkvar1.get()
    global destination_select
    destination_select = tpp1.get()

    if quality_select:
        if destination_select:
            no = choices1[quality_select]
            global stream
            stream = files1[no]
            global file_size
            file_size = stream.filesize

            create_download_widget()

            #MultiThreading is used to display progress Bar
            threading.Thread(target=yt.register_on_progress_callback(progress_Check)).start()
            threading.Thread(target=download).start()


        else:
            err_select_destination()
    else :
        err_select_quality()



# Creates seperate download widgets everytime a download button is clicked
def create_download_widget():
    Frame(root, borderwidth=2, height=2, relief=SUNKEN).pack(fill=X)
    frame3 = Frame(root)
    frame3.pack(fill=X)

    #disable download button and submit button
    download_button.config(state="disabled")
    submit_button.config(state="disabled")
    browsebutton.config(state="disabled")



    #variables
    global prog_var
    prog_var = StringVar(root)
    prog_var.set("0%")
    global prog_intvar
    prog_intvar = StringVar(root)
    prog_intvar.set("0")


    # gets video thumbnail
    data = requests.get(yt.thumbnail_url).content
    with open('<thumbnail_name>', 'wb') as file: #e.g.(C:\Users\mukes\Downloads\\file01.jpg)
        file.write(data)

    #displays video thumbnail
    thumb_label = Label(frame3)
    thumb_label.grid(row=0, column=0, rowspan=2, columnspan=2)
    img = ImageTk.PhotoImage(Image.open("<thumbnail_name>")) #e.g.(C:\Users\mukes\Downloads\\file01.jpg)
    thumb_label.image = img
    thumb_label.configure(image=img)

    #displays video title
    th_title = StringVar(frame3)
    th_title.set(yt.title)
    thumb_title = Text(frame3,width=40,height=2,font="Calibri 10",background="gray95")
    thumb_title.insert(INSERT,th_title.get())
    thumb_title.grid(row=0,column=2,sticky=NW,padx=2,pady=2)

    #displays progress bar
    global progressbar
    progressbar = ttk.Progressbar(frame3, orient="horizontal", length=250, mode='determinate', variable=prog_intvar,maximum=100)
    progressbar.grid(row=1,column=2,sticky=SW,padx=5)
    global progress_label
    progress_label = Label(frame3, textvariable=prog_var, text="%", borderwidth=2)
    progress_label.grid(row=1, column=2,sticky=SE)

    #display label for download speed
    global speed
    speed = StringVar(frame3)
    speed.set("0")
    global download_speedlb
    download_speedlb = Label(frame3, textvariable=speed, borderwidth=2)
    download_speedlb.grid(row=1,column=2,sticky=NW)


# function to check download speed
def progress_Check(stream = None, chunk =None, file_handle = None, remaining = None):
    percent = (100.0*(file_size-remaining))/file_size
    temp = ((file_size - remaining)/(1024.0*(time()-start_time)))
    time_remaining = remaining/(temp*1024)
    speed.set("Downloading..... ({:.2f} KB/s) - ".format(temp) + "{:.1f}s remaining".format(time_remaining))
    prog_var.set("{:.1f}%".format(percent))
    prog_intvar.set("{:.1f}".format(percent))
    progress_label.config(textvariable=prog_var)
    download_speedlb.config(textvariable=speed)


# downloads video
def download():
    global start_time
    start_time = time()
    stream.download(destination_select)

# displays error when quality is not selected
def err_select_quality(event=None):
    tkMessageBox.showinfo(
        "Message",
        "Please Select File Quality!!!"
    )

# displays error when destination is not selected
def err_select_destination(event=None):
    tkMessageBox.showinfo(
        "Message",
        "Please Select Destination For Your File!!!"
    )

# displays operations needed to be performed when video is downloaded
def display_complete(stream=None, file_handle=None):
    prog_var.set('')
    prog_intvar.set('0')
    speed.set("Download Complete..... ({:.2f} KB/s) - ".format(file_size/(1024.0*(time()-start_time)))+"{:.1f}s".format(time()-start_time))
    download_speedlb.config(width=37,height=3)
    download_button.config(state="normal")
    submit_button.config(state="normal")
    browsebutton.config(state="normal")





root = Tk()
root.title("YouTube Downloader")
root.resizable(width=False,height=False)
global i
i = IntVar(root)
i.set(0)


#First Frame
frame1 = Frame(root,width=230,height=200)
frame1.pack(fill=X)
create_widgets_in_frame1()
frame2 = Frame(root)

root.mainloop()
