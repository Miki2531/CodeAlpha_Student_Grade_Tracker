import datetime
from tkinter import *
import tkinter.messagebox as mb
from tkinter import ttk
import tkinter as tk
from tkcalendar import DateEntry
import sqlite3


#creating the variables
headlabelfont = ("calibri", 15, 'bold')
labelfont  = ('calibri', 14)
entryfont = ('calibri', 14)

#connectiing to Database
connector = sqlite3.connect('StudentGradeTracker.db')
cursor = connector.cursor()
connector.execute(
    "CREATE TABLE IF NOT EXISTS STUDENT_GRADE(STUDENT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, NAME TEXT, EMAIL TEXT, PHONE_NO TEXT, GENDER TEXT, DOB TEXT, SECTION TEXT )"
    )

cursor.execute('''
    CREATE TABLE IF NOT EXISTS student_courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course TEXT,
        midterm INTEGER,
        final INTEGER,
        assignment INTEGER,
        total_marks INTEGER,
        result INTEGER,
        FOREIGN KEY(student_id) REFERENCES STUDENT_GRADE(STUDENT_ID)
    )
''')

connector.commit()


def add_course_assessment():
    selected_item = tree.focus()
    if not selected_item:
        mb.showerror('Error', 'Please select a student.')
        return
    
    student_id = tree.item(selected_item, 'values')[0]
    course_name = course_var.get()
    if not course_name:
        mb.showerror('Error, Please select a course.')
        return
    
    assessments_window = tk.Toplevel(main)
    assessments_window.title('Add Assessments')
    assessments_window.geometry('400x300')

    Label(assessments_window, text=f"Assessment for {course_name}", font=labelfont).place(x=100, y=10)

    Label(assessments_window, text='Mid Grade:', font=labelfont).place(x=50, y=40)
    mid_grade_entry = Entry(assessments_window, font=labelfont, width=10)
    mid_grade_entry.place(x=150, y=40)

    Label(assessments_window, text='Final Grade:', font=labelfont).place(x=50, y=80)
    final_grade_entry = Entry(assessments_window, font=labelfont, width=10)
    final_grade_entry.place(x=150, y=80)

    Label(assessments_window, text='Assignment Grade:', font=labelfont).place(x= 50, y= 120)
    assignment_grade_entry = Entry(assessments_window, font=labelfont, width=15)
    assignment_grade_entry.place(x=210, y=120)

    def save_assessment():
        mid_grade = mid_grade_entry.get()
        final_grade = final_grade_entry.get()
        assignment_grade = assignment_grade_entry.get()

        if not mid_grade or not final_grade or not assignment_grade:
            mb.showerror('Error', 'Please enter grades for all assessments.')
            return

        # Calculate total marks and determine pass or fail
        total_marks = (int(mid_grade) + int(final_grade) + int(assignment_grade))
        result = 'Pass' if total_marks >= 60 else 'Fail'

        # Insert assessment into the database
        cursor.execute("INSERT INTO student_courses (student_id, course, midterm, final, assignment, total_marks, result) VALUES (?, ?, ?, ?, ?, ?,?)",
                       (student_id, course_name, mid_grade, final_grade, assignment_grade, total_marks, result))
        connector.commit()

        display_assessment_results(mid_grade, final_grade, assignment_grade, total_marks, result)

        mb.showinfo('Success', 'Assessment added successfully.')
        assessments_window.destroy()

    save_button = Button(assessments_window, text='Save Assessment', font=labelfont, command=save_assessment).place(x=150, y=180)


    def display_assessment_results(mid_grade, final_grade, assignment_grade, total_marks, result):
        results_window = tk.Toplevel(main)
        results_window.title('Assessment Results')
        results_window.geometry('300x200')

        tk.Label(results_window, text=f'Midterm Grade: {mid_grade}', font=labelfont).pack()
        tk.Label(results_window, text=f'Final Grade: {final_grade}', font=labelfont).pack()
        tk.Label(results_window, text=f'Assignment Grade: {assignment_grade}', font=labelfont).pack()
        tk.Label(results_window, text=f'Total Marks: {total_marks}', font=labelfont).pack()
        tk.Label(results_window, text=f'Result: {result}', font=labelfont).pack()


items = [ 'name_strvar', 'email_strvar', 'contact_strvar', 'gender_strvar', 'section_var']
def add_record():
    global name_strvar, contact_strvar, email_strvar, dob, gender_strvar, section_var
    name  = name_strvar.get()
    email = email_strvar.get()
    phone = contact_strvar.get()
    gender = gender_strvar.get()
    DOB  = dob.get_date()
    section = section_var.get()

    if not name or not email or not phone or not gender or not DOB or not section:
        mb.showerror('Error!, Please enter all detail.')
    else: 
        try:
            connector.execute(
                'INSERT INTO STUDENT_GRADE(NAME, EMAIL, PHONE_NO, GENDER, DOB, SECTION) VALUES (?,?,?,?,?,?)', (name, email, phone, gender, DOB, section)  
            )
            connector.commit()
            mb.showinfo('Recored inserted', f"Recored of {name} is added.")
            reset_field()
            display_records()

        except:
            for filed in items:
               mb.showerror('Wrong type', f"The type of the values entered {filed} is not accurate. Pls note insert the correct information.")


def reset_field():
    global name_strvar, email_strvar, contact_strvar, dob, gender_strvar, section_var
    for i in items:
        exec(f"{i}.set('')")

    dob.set_date(datetime.datetime.now().date())

def remove_record():
    if not tree.selection():
        mb.showerror('Error, please select an item from the database.')
    else:
        current_item = tree.focus()
        values = tree.item(current_item)
        selection = values['values']
        tree.delete(current_item)

        connector.execute('DELETE FROM STUDENT_GRADE WHERE STUDENT_ID=%d' %selection[0])
        connector.commit()
        mb.showinfo('Successfull, The selected student deleted from the database.')
        display_records()


def view_record():
    global name_strvar, email_strvar, contact_strvar, dob, gender_strvar, section_var
    if not tree.selection():
        mb.showerror('Error, please select the recorede view.')
    else:
        current_item = tree.focus()
        values = tree.item(current_item)
        selection = values['values']

        name_strvar.set(selection[1])
        email_strvar.set(selection[2])
        contact_strvar.set(selection[3])
        gender_strvar.set(selection[4])
        date = datetime.date(int(selection[5][:4]), int(selection[5][5:7]), int(selection[5][8:]))
        dob.set_date(date)
        section_var.set(selection[6])


def reset_form():
    global tree
    tree.delete(*tree.get_children())

    reset_field()

def display_records():
    tree.delete(*tree.get_children())
    c = connector.execute('SELECT * FROM STUDENT_GRADE')
    data = c.fetchall()
    for reades in data:
        tree.insert('', END, values = reades)




main = Tk()
main.title('Student Greade Tracker')
main.geometry("1000x800")
main.resizable(0, 0)


#backgound color
lf_bg = 'SteelBlue'

#creating the stringVar ot IntVar variables
name_strvar = StringVar()
email_strvar = StringVar()
contact_strvar = StringVar()
gender_strvar = StringVar()
section_var = StringVar()
course_var = StringVar()


#creating the main window
Label(main, text="Student Grade Tracker", font='Arial', bg='SkyBlue').pack(side=TOP, fill=X)
left_frame = Frame(main, bg= lf_bg)
left_frame.place(x=0, y=30, height=1000, width=400)
right_frame = Frame(main, bg="gray")
right_frame.place(x=400, y=30, height=1000, width=600)


#component in the left frame
Label(left_frame, text="Name", font=labelfont, bg=lf_bg).place(x=30, y=50)
Label(left_frame, text="Contact Number", font=labelfont, bg=lf_bg).place(x=30, y=100)
Label(left_frame, text="Email Address", font=labelfont, bg=lf_bg).place(x=30, y=150)
Label(left_frame, text="Gender", font=labelfont, bg=lf_bg).place(x=30, y=200)
Label(left_frame, text="Date of Birth(DOB)", font=labelfont, bg= lf_bg).place(x=30, y=250)
Label(left_frame, text="Section", font=labelfont, bg=lf_bg).place(x=30, y=300)


Entry(left_frame, width=20, textvariable=name_strvar, font=entryfont).place(x=170, y=50)
Entry(left_frame, width=19, textvariable=contact_strvar, font=entryfont).place(x=170, y=100)
Entry(left_frame, width=19, textvariable=email_strvar, font=entryfont).place(x=170, y=150)
Entry(left_frame, width=19, textvariable=section_var, font=entryfont).place(x=170, y=300)
OptionMenu(left_frame, gender_strvar, 'M', 'F').place(x=170, y=200, width=70)
dob = DateEntry(left_frame, font=('Arial', 12), width=15)
dob.place(x=180, y=250)


#Button for the function
Button(left_frame, text="Submit and Add Record", font=labelfont, command=add_record, width=18).place(x=80, y=390)
Button(left_frame, text="Delete Record", font=labelfont, command=remove_record, width=15).place(x=30, y=450)
Button(left_frame, text="View Record", font=labelfont, command=view_record, width=15).place(x=200, y=450)
Button(left_frame, text="Clear Fields", font=labelfont, command=reset_field, width=15).place(x=30, y=520)
Button(left_frame, text="Remove database", font=labelfont, command=reset_form, width=15).place(x=200, y=520)



#creating lable for the right frame
Label(right_frame, text="Student Record", font='Arial', bg='DarkBlue', fg='LightCyan').pack(side=TOP, fill = X)
tree =  ttk.Treeview(right_frame, height=100, selectmode=BROWSE, columns=('Stud ID', 'Name', 'Email Addr', 'Contact No', 'Gender', 'Date of Birth', 'Section'))

X_scroller  = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
Y_scroller = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
X_scroller.pack(side=BOTTOM, fill=X)
Y_scroller.pack(side=RIGHT, fill=Y)
tree.config(yscrollcommand=Y_scroller.set, xscrollcommand=X_scroller.set)

tree.heading('Stud ID', text='ID', anchor=CENTER)
tree.heading('Name', text='name', anchor=CENTER)
tree.heading('Email Addr', text='Email ID', anchor=CENTER)
tree.heading('Contact No', text='Phone No', anchor=CENTER)
tree.heading('Gender', text='Gender', anchor=CENTER)
tree.heading('Date of Birth', text='DOB', anchor=CENTER)
tree.heading('Section', text='Section', anchor=CENTER)
tree.column('#0', width=0, stretch=NO)
tree.column('#1', width=40, stretch=NO)
tree.column('#2', width=120, stretch=NO)
tree.column('#3', width=180, stretch=NO)
tree.column('#4', width=60, stretch=NO)
tree.column('#5', width=60, stretch=NO)
tree.column('#6', width=70, stretch=NO)
tree.column('#7', width=120, stretch=NO)
tree.place(y=30, relwidth=1, relheight=0.9, relx=0)
display_records()

# Components in the left frame
Label(left_frame, text="Select Course:", font=('calibri', 14)).place(x=30, y=350)
courses = ['Math', 'Physics', 'Biology', 'Civic', 'History']
course_dropdown = OptionMenu(left_frame, course_var, *courses)
course_dropdown.place(x=170, y=350)

add_course_button = Button(left_frame, text="Add Course Result", font=labelfont, command=add_course_assessment, width=15)
add_course_button.place(x=30, y=570)


main.update()
main.mainloop()










