import tkinter
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import cv2
import os
import sqlite3
import face_recognition
import re
import datetime

conn = sqlite3.connect("images.db")


face_mode = False
Message_Showing = False
current_person = ""
Registration_ON = False

def Mark_Attendance(roll_number,student_name):
    global conn
    tb_length = 0
    present = False
    current_date = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month) + '-' + str(datetime.datetime.now().day)
    count_row = conn.execute("SELECT COUNT(*) FROM ATTENDANCE")
    for row in count_row:
        tb_length = row[0]
    if tb_length > 0:
        cursor = conn.execute("SELECT * FROM ATTENDANCE")
        for row in cursor:
            date = str(row[2]).split('-')
            if str(row[0]) == str(roll_number) and datetime.datetime.now().year == int(date[0]) and datetime.datetime.now().month == int(date[1]) and datetime.datetime.now().day == int(date[2]):
                present = True

        if present == False:
            conn.execute(
                f"INSERT INTO ATTENDANCE (ROLL_NUMBER,PERSON_NAME,DATE,STATUS) VALUES('{roll_number}','{student_name}','{current_date}','present')")
            conn.commit()

    else:
        conn.execute(f"INSERT INTO ATTENDANCE (ROLL_NUMBER,PERSON_NAME,DATE,STATUS) VALUES('{roll_number}','{student_name}','{current_date}','present')")
        conn.commit()

def Table():
    table_window = Toplevel()
    table_window.geometry(f"480x250+600+200")
    table_window.title("Attendance Sheet")
    table_window.resizable(False, False)

    table = ttk.Treeview(table_window, selectmode="browse")
    table["columns"] = ("1","2","3","4")
    table["show"] = "headings"

    table.column("1",width=100,anchor="c")
    table.column("2",width=120,anchor="se")
    table.column("3",width=100,anchor="se")
    table.column("4",width=100,anchor="se")

    table.heading("1",text="Roll-Number")
    table.heading("2",text="Student-Name")
    table.heading("3",text="Date")
    table.heading("4",text="Status")

    scroll_bar = ttk.Scrollbar(table_window,orient="vertical",command=table.yview)
    scroll_bar.pack(side=RIGHT)

    cursor = conn.execute("SELECT * FROM ATTENDANCE")
    number = 1
    for row in cursor:
        id = "L"+str(number)
        name = str(row[1]).split("_")[0] +" "+ str(row[1]).split("_")[1]
        table.insert("",'end',text=id,values=(row[0],name,row[2],row[3]))
        number += 1
    table.configure(xscrollcommand=scroll_bar.set)

    table.pack()

    table_window.mainloop()

def Enable():
    global face_mode
    face_mode = True

def Disable():
    global face_mode,Registration_ON
    if Registration_ON == False:
        face_mode = False

def Convert(value):
     result = re.sub('[^0-9] | (\\.)',' ',value)
     result = result.replace("[",'')
     result = result.replace("]",'')
     result = re.split(r" +",result)

     for i in range(0,len(result)):
         if len(result[i]) == 0:
             del result[i]
     result = [float(i) for i in result]

     return result


clf = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def Compare(img):
    global x,current_person
    known_faces = []
    person_name = []
    roll_numbers = []
    path = os.getcwd() + "\\Images"
    path = path.replace("\\",'/')

    current_face_encoding = img
    cursor = conn.execute("SELECT ROLL_NUMBER,PERSON_NAME,IMG_ENCODING FROM IMG_TABLE")
    for row in cursor:
        roll_numbers.append(row[0])
        person_name.append(row[1])
        known_faces.append(Convert(row[2]))


    if current_face_encoding:
        face_distance = face_recognition.api.face_distance(known_faces,current_face_encoding[0])
        for x in range(0,len(face_distance)):
            if face_distance[x] < 0.50:
                Mark_Attendance(roll_numbers[x],person_name[x])
                return True
        return False




window = Tk()
cap = cv2.VideoCapture(0)
window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}")

video_Screen_frame = Frame(window, width=window.winfo_screenwidth(), height=window.winfo_screenheight() - 200, bg="white")

video_screen = Label(video_Screen_frame, width=window.winfo_screenwidth(), height=window.winfo_screenheight() - 200)

firstname = ""
lastname = ""
roll_number = ""

def Func():
    pass



def Submit():
    global img,conn,Message_Showing,firstname,lastname,roll_number,face_mode,Registration_ON
    if len(firstname.get()) > 0 and len(lastname.get()) > 0 and len(roll_number.get())>0:
        path = os.getcwd().replace('\\','/')
        path = path + "/Images/"
        filename = firstname.get() + "_" + lastname.get() + ".jpg"
        img.save(f"{path}{filename}")

        img_encoding = cv2.imread(f"{path}{filename}")
        img_encoding = cv2.cvtColor(img_encoding,cv2.COLOR_BGR2RGB)

        face_encoding = face_recognition.api.face_locations(img_encoding)
        face_encoding = face_recognition.api.face_encodings(img_encoding)
        conn.execute(f'''INSERT INTO IMG_TABLE (ROLL_NUMBER,PERSON_NAME,IMG_ENCODING) VALUES('{roll_number.get()}','{filename.split(".")[0]}','{face_encoding[0]}')''')
        conn.commit()
        registration.destroy()
        Message_Showing = False

    else:
        messagebox.showerror("Registration Error","You have not filled out Registration Properly")
        registration.destroy()

    Registration_ON = False


def Register():
    global roll_number,firstname,lastname,registration,Registration_ON,face_mode
    Registration_ON = True
    face_mode = True
    firstname = StringVar()
    lastname = StringVar()
    roll_number = StringVar()
    messagebox.showinfo("Important Note",
                        "Make Sure your face is showing properly on screen and in the Face Box when you register \n Note: If after pressing 'register', the registration box still remains open then your face is not properly positioned on screen and needs to be properly adjusted for registration to be successful")

    registration = Toplevel(window)
    registration.geometry(f"400x150+630+200")
    registration.title("Register")
    registration.resizable(False,False)

    registration.protocol("WM_DELETE_WINDOW",Func)

    fname_label = Label(registration,text="Enter First-Name",font=("helvetica",15))
    fname_label.grid(row=1,column=1)
    fname = Entry(registration,width=30,textvariable=firstname)
    fname.grid(row=1,column=2,padx=10)

    lname_label = Label(registration, text="Enter Last-Name", font=("helvetica", 15))
    lname_label.grid(row=2, column=1)
    lname = Entry(registration, width=30,textvariable=lastname)
    lname.grid(row=2, column=2, padx=10)

    rollnumber_label = Label(registration, text="Enter Roll-Number", font=("helvetica", 15))
    rollnumber_label.grid(row=3, column=1)
    rollnumber = Entry(registration, width=30, textvariable=roll_number)
    rollnumber.grid(row=3, column=2, padx=10)

    submit = Button(registration,text="Register",font=("helvetica",15),width=20,command=Submit)
    submit.place(x=90,y=100)


def Ask_Registration():
    global Message_Showing,face_mode
    if not Message_Showing:
        Message_Showing = True
        response = messagebox.askyesno("Unknown Face Showing","You are not Registered.Would you like to register?")
        if response:
            Register()
        else:
            Message_Showing = False

def show_video():
    global img,i,face_mode,current_person,Registration_ON
    ret,frame = cap.read()
    frame = cv2.resize(frame,(window.winfo_screenwidth()-400,window.winfo_screenheight() - 200))

    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if face_mode:
        faces_boxes = clf.detectMultiScale(gray_img, 1.1, 9)
        if faces_boxes is not ():
            x, y, w, h = faces_boxes[0]
            current_img = cv2.cvtColor(frame[y-20:y+h+20,x-20:x+w+20],cv2.COLOR_BGR2RGB)
            current_face_location = face_recognition.api.face_locations(current_img)
            current_face_encoding = face_recognition.api.face_encodings(current_img,current_face_location)
            if Compare(current_face_encoding) == True:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)
            elif Compare(current_face_encoding) == False:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)
                if Registration_ON == False:
                    Ask_Registration()
            img = Image.fromarray(frame[y-20:y+h+20,x-20:x+w+20])

    Img = ImageTk.PhotoImage(image=(Image.fromarray(frame)))
    video_screen.imgtk = Img
    video_screen.configure(image=Img)

    video_screen.after(20, show_video)

show_video()

register = Button(window,text="Register",width=30,height=3,bd=3,font="italic",bg="red",command=Register)
exit = Button(window,text="Exit",width=13,height=3,bd=3,font="italic",bg="red",command=window.destroy)
enable_Detection = Button(window,text="Enable Detection",width=30,height=3,bd=3,font="italic",bg="red",command=Enable)
disable_Detection = Button(window,text="Disable Detection",width=30,height=3,bd=3,font="italic",bg="red",command=Disable)
attendance_display = Button(window,text="Show Attendance Table",width=30,height=3,bd=3,font="italic",bg="red",command=Table)

video_Screen_frame.pack()
video_screen.pack()
register.pack(side = tkinter.LEFT)
enable_Detection.pack(side= tkinter.LEFT)
disable_Detection.pack(side= tkinter.LEFT)
attendance_display.pack(side=tkinter.LEFT)
exit.pack(side = tkinter.LEFT)
window.mainloop()