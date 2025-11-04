import csv
import hashlib
import os
import time
import statistics
import sys
import unittest
from collections import defaultdict


def hash_password(u_password):
    return hashlib.sha256(u_password.encode()).hexdigest()

def get_csv(f_name):
    csv_data = []
    with open(f_name, newline='', encoding='utf-8') as f:
        reader_value = csv.DictReader(f)
        for rec in reader_value:
            csv_data.append(rec)
    return csv_data

def csv_write(f_name, col_names: list, data_val):
    with open(f_name, 'w', newline='', encoding='utf-8') as f:
        writer_data = csv.DictWriter(f, fieldnames=col_names, extrasaction='ignore')
        writer_data.writeheader()
        if data_val:
            writer_data.writerows(data_val)


class UserLogin:
    def __init__(self, email_id, hash_pass, u_role):
        self.email_id = email_id
        self.hash_pass = hash_pass
        self.u_role = u_role

class Student:
    def __init__(self, emailId, firstName, lastName, courseId, grade, marks):
        self.email = emailId
        self.FirstName = firstName
        self.LastName = lastName
        self.CourseId = courseId
        self.grade = grade
        self.marks = float(marks)

    def to_dict(self):
        return {

            "Email_Id": self.email,
            "FirstName": self.FirstName,
            "LastName": self.LastName,
            "CourseId": self.CourseId,
            "Grade": self.grade,
            "Marks": self.marks
        }

class Course:
    def __init__(self, CourseId, CourseName, description):
        self.CourseId = CourseId
        self.course_name = CourseName
        self.description = description

    def to_dict(self):
        return {
            "CourseId": self.CourseId,
            "CourseName": self.course_name,
            "CourseDescription": self.description
        }

class MyGradeApp:
    def __init__(self):
        self.login_details = get_csv("login.csv")
        self.professors_details = get_csv("professors.csv")
        self.student_details   = get_csv("students.csv")
        self.courses_details    = get_csv("courses.csv")
        self.curr_user = None


    def login_page(self, u_email, u_password):
        for rec in self.login_details:
            if u_email == rec["Email_id"] and hash_password(u_password) == rec["u_Password"]:
                self.curr_user = UserLogin(u_email, rec["u_Password"], rec["u_Role"])
                print("Login Successful!")
                if self.curr_user.u_role == "student":
                    self.student_options()
                else:
                    self.professor_options()
        else:
            print("Invalid! Please try again!")

    def register_user(self, u_email, u_password, u_role ):
        if not any(u_detail["Email_id"] == u_email for u_detail in self.login_details):
            self.login_details.append({"Email_id": u_email, "u_Password": hash_password(u_password), "u_Role": u_role})
            csv_write("login.csv", ["Email_id","u_Password","u_Role"], self.login_details)
            print("successfully created!")
        else:
            print("Email Id already exist!")
    

    def logout_page(self):
        self.curr_user = None
        print("Logged Out!")

    def reset_password(self,u_email):
        user_exist = next((u1 for u1 in self.login_details if u1["Email_id"] == u_email), None)
        if user_exist:
            new_password = input("Enter your New Password: ")
            user_exist["u_Password"] = hash_password(new_password)
            csv_write("login.csv",  ["Email_id","u_Password","u_Role"], self.login_details)
            print("Changed password successfully.")
        else:
            print("Email id doesn't exist.")


    def student_add(self, email_id, f_name, l_name, course_id,g,m):
        if any(stud["Email_Id"] == email_id for stud in self.student_details):
            print("Email already exist")
            return
        elif not email_id:
            print("Email Id can't be empty.")
            return
        if not any(c["CourseId"] == course_id for c in self.courses_details):
            print("Invalid Course Id")
            return
        new_student = Student(email_id, f_name, l_name, course_id, g, m)
        self.student_details.append(new_student.to_dict())
        csv_write("students.csv", ["Email_Id","FirstName","LastName","CourseId","Grade","Marks"], self.student_details)
        print("Added.")

    
    def update_student(self, email_id, new_m,new_course_id,new_g):
        for stud in self.student_details:
            if email_id == stud["Email_Id"]:
                if new_course_id:
                    if any(c["CourseId"] == new_course_id for c in self.courses_details):
                        stud["CourseId"] = new_course_id
                    else:
                        print("Not found or Not changed.")
                if new_m: 
                    stud["Marks"] = new_m
                if new_g: 
                    stud["Grade"] = new_g
                csv_write("students.csv", ["Email_Id","FirstName","LastName","CourseId","Grade","Marks"], self.student_details)
                print("Record updated.")
                return
        print("Invalid student Id")

    def student_delete(self, email_id):
        prev = len(self.student_details)
        self.student_details = [s for s in self.student_details if email_id != s["Email_Id"]]
        if prev > len(self.student_details):
            csv_write("students.csv", ["Email_Id","FirstName","LastName","CourseId","Grade","Marks"], self.student_details)
            print("Student deleted.")
        else:
            print("Invalid Student Id.")

    def sort_fn(self, sort_value):
        p_val = sort_value.split()
        if p_val:
         f_val = p_val[0]
        else:
         f_val = "name"
        rev = (len(p_val) > 1 and p_val[1] == "desc")
        start = time.time()
        if f_val == "email":
            sorted_l = sorted(self.student_details, key=lambda s: s["Email_Id"].lower(), reverse=rev)
        elif f_val == "marks":
            sorted_l = sorted(self.student_details, key=lambda s: float(s["Marks"]), reverse=rev)
        else:
            sorted_l = sorted(self.student_details, key=lambda s: (s["FirstName"] + " " + s["LastName"]).lower(), reverse=rev)
        end = time.time()
        print(f"Sorting time {end - start:.6f} secs.")
        for detail in sorted_l:
            print(detail)

    def search_fn(self, s_email):
        start = time.time()
        email_found = [s for s in self.student_details if s_email in s["Email_Id"].lower()]
        end = time.time()
        print(f"Search time: {end - start:.6f} secs.")
        if email_found:
            for stud_details in email_found:
                print(stud_details)
        else:
            print("No record.")
   
            print()

    def course_add(self, CourseId, course_name, course_desc):
        if any(CourseId == course["CourseId"] for course in self.courses_details):
            print("Course Id already exist!")
        else:
            course_new = Course(CourseId, course_name, course_desc)
            self.courses_details.append(course_new.to_dict())
            csv_write("courses.csv", ["CourseId", "CourseName", "CourseDescription"], self.courses_details)
            print("Course Added!")
    
    def course_modify(self, course_id, new_courseName, new_courseDesc):
        for course in self.courses_details:
            if course_id == course["CourseId"]:
                if new_courseName: 
                    course["CourseName"] = new_courseName
                if new_courseDesc: 
                    course["CourseDescription"] = new_courseDesc
                csv_write("courses.csv", ["CourseId", "CourseName", "CourseDescription"], self.courses_details)
                print(" updated!")

    def course_delete(self, cid):
        prev = len(self.courses_details)
        self.courses_details = [c for c in self.courses_details if c["CourseId"] != cid]
        if prev > len(self.courses_details):
            csv_write("courses.csv", self.courses_details[0].keys(), self.courses_details)
            print("Course deleted.")
        else:
            print("Not found!")
   
    def course_report(self, course_id):
        course_d = next((c1 for c1 in self.courses_details if course_id == c1["CourseId"]), None)
        if course_d:
         course_heading = f"{course_id} {course_d['CourseName']}"
        else:
            course_heading = course_id
        rec = [s1 for s1 in self.student_details if course_id == s1["CourseId"]]
        print(f"Report for {course_heading}")
        if rec:
            print(f"{'Student Name':28} {'Email Id':26} {'Grade':>7} {'Marks':>7}")
            print("-" * 72)
            for s1 in rec:
                name = f"{s1['FirstName']} {s1['LastName']}"
                print(f"{name:28} {s1['Email_Id']:26} {s1['Grade']:>7} {s1['Marks']:>7}")
            print()

    def add_professor(self, prof_id, p_name, p_rank, p_course_id):
        if any(p["Professor_id"] == prof_id for p in self.professors_details):
            print("Professor Id must be unique")
            return
        elif not prof_id:
            print("Professor id can't be empty.")
            return
        if not any(course["CourseId"] == p_course_id for course in self.courses_details):
            print("Invalid CourseId.")
            return
        new_prof = {"Professor_id": prof_id, "p_Name": p_name, "Rank":p_rank, "CourseId": p_course_id}
        self.professors_details.append(new_prof)
        csv_write('professors.csv', ["Professor_id", "p_Name", "Rank", "CourseId"], self.professors_details)
        print(" Professor Added.")

    def professor_delete(self, p_id):
        prev = len(self.professors_details)
        self.professors_details = [p for p in self.professors_details if p_id != p["Professor_id"]]
        if prev > len(self.professors_details):
            csv_write('professors.csv', ["Professor_id", "p_Name", "Rank", "CourseId"], self.professors_details)
            print("Professor deleted.")
        else:
            print("Invalid Professor id.")

    def update_prof_details(self,p_id, p_name, p_rank,p_cid):
        for p in self.professors_details:
            if p_id == p["Professor_id"]:
                if p_rank:
                    p["Rank"] = p_rank
                if p_name: 
                    p["Name"] = p_name
                if p_cid:
                    if not any(c["CourseId"] == p_cid for c in self.courses_details):
                        print("Invalid Coure id.")
                        return
                    p["CourseId"] = p_cid
                csv_write('professors.csv', ["Professor_id", "p_Name", "Rank", "CourseId"], self.professors_details)
                print("Professor details updated.")
                return
        print("Invalid Professor id.")

    def get_course_details_by_the_professor(self, professor_identifier):
        prof = next((prof1 for prof1 in self.professors_details if professor_identifier == prof1["Professor_id"]), None)
        if prof:
            course_one = next((course1 for course1 in self.courses_details if course1["CourseId"] == prof["CourseId"]), None )
            print(f"\nProfessor: { prof['p_Name'] } ({ prof['Rank'] })")
            if course_one is not None:
                print(f"Teaches the course : { prof["CourseId"] } - { course_one['CourseName']}")
            else:
                print("Course not found.")

            enrolled = [stu for stu in self.student_details if prof["CourseId"] == stu["CourseId"]]
                
            if enrolled:
                print(f"\nStudents that are enrolled in {prof["CourseId"]}:")
                for stu in enrolled:
                    print(f" - {stu['FirstName']} {stu['LastName']} || {stu['Email_Id']} || Grade {stu['Grade']} ({stu['Marks']})")
                print()
            else:
                print("There are zero students enrolled for this particular course.\n")


    def professor_report(self, prof_id):
        prof_deatils = [prof for prof in self.professors_details if prof_id == prof["Professor_id"]]
        if prof_deatils:
            print(f" Professor-wise Report: {prof_deatils[0].get("p_Name", prof_id)} ({prof_deatils[0].get("Rank", "")})")
            courseby_id = {c["CourseId"]: c for c in self.courses_details}
            studentsby_course = defaultdict(list)
            for s in self.student_details:
                studentsby_course[s["CourseId"]].append(s)

            for prof in prof_deatils:
                c = courseby_id.get(prof["CourseId"])
                c_detail = f"{prof["CourseId"]} - {c['CourseName']}" if c else prof["CourseId"]
                print(f"Course: {c_detail}")
                rec = studentsby_course.get(prof["CourseId"], [])
                if not rec:
                    print("  (No enrolled students)")
                    continue
                print(f"{'Student':28} {'Email':26} {'Grade':>7} {'Marks':>7}")
                print("-" * 72)
                for s in rec:
                    name = f"{s['FirstName']} {s['LastName']}"
                    print(f"{name:28} {s['Email_Id']:26} {s['Grade']:>7} {s['Marks']:>7}")
            print()

    def student_report(self, stud_id):
        stu = next((stud for stud in self.student_details if stud_id == stud["Email_Id"]), None)
        if stu:
            prof_details =  next((prof for prof in self.professors_details if stu["CourseId"] == prof["CourseId"]), None)
            course_details = next((c for c in self.courses_details if stu["CourseId"] == c["CourseId"]), None)
            if course_details:
                course_detail = f"{stu['CourseId']} - {course_details['CourseName']}" 
            else:
                course_detail = stu["CourseId"]
            print(f''' 
                  Student : {stu['FirstName']} {stu['LastName']}
                  Email: {stu['Email_Id']}
                  Course: {course_detail}
                  Professor: {prof_details['p_Name']} {prof_details['Rank']}
                  Marks: {stu['Marks']}")
                  Grade: {stu['Grade']}")
                  ''')
        else:
            print("Student not found.")

    def avgMedainReport(self, course_id):
        student_marks = [float(stud["Marks"]) for stud in self.student_details if course_id == stud["CourseId"]]
        if student_marks:
            avg_mark = sum(student_marks) / len(student_marks)
            median_mark = statistics.median(student_marks)
            print(f"Average: {avg_mark:.2f}, Median: {median_mark:.2f}")
        else:
            print("Data havn't uploaded yet.")

    def professor_options(self):
        while True:
            print('''
                1. Add Course
                2. Modify Course  
                3. Delete Course
                4. Course Report
                5. Show Course Details by Professor
                6. Average/median
                7. Add Student
                8. Modify Student
                9. Delete Student
                10. Search Students
                11. Sort Students
                12. Student Report
                13. Add Professor
                14. Modify Professor Details
                15. Delete Professor
                16. Professor Report
                17. Logout
                  ''')
            
            prof_opt = int(input("Enter the option: "))
            if prof_opt == 1:
                c_id = input("Enter Course Id: ")
                c_name = input("Enter Course Name: ")
                c_desc = input("Enter Course Description: ")
                self.course_add(c_id, c_name, c_desc)
            elif prof_opt == 2: 
                course_id = input("Enter course Id: ")
                new_courseName = input("Enter New Course Name or leave empty: ")
                new_courseDesc = input("Enter New Description or leave empty: ")
                self.course_modify(course_id, new_courseName, new_courseDesc)
            elif prof_opt == 3:
                course_id =input("Enter course Id: ")
                self.course_delete(course_id)
            elif prof_opt == 4:
                course_id = input("Enter Course ID: ")
                self.course_report(course_id)
            elif prof_opt == 5:
                professor_identifier = input("Enter Professor Id: ")
                self.get_course_details_by_the_professor(professor_identifier)
            elif prof_opt == 6: 
                course_id = input("Enter Course Id: ")
                self.avgMedainReport(course_id)
            elif prof_opt == 7:
                email_id = input("Enter Email Id: ")
                f_name = input("Enter First Name: ")
                l_name = input("Enter Last Name: ")
                Course_id = input("Assign Course ID: ")
                marks_stud = int(input("Enter Marks: "))
                if marks_stud >= 95:
                    grade_stud = 'A+'
                elif marks_stud >= 89:
                    grade_stud = 'A'
                elif marks_stud >= 73:
                    grade_stud = 'B'
                elif marks_stud >= 60:
                    grade_stud = 'C'
                elif marks_stud >= 50:
                    grade_stud = 'D'
                else:
                    grade_stud = 'F'
                self.student_add(email_id, f_name, l_name, Course_id,grade_stud,marks_stud)
            elif prof_opt == 8:
                email_id = input("Enter student Email Id: ")
                new_course_id  = input("Enter New Course ID or leave empty: ")
                new_ma = float(input("Enter New Marks or leave empty "))
                if new_ma:
                    if new_ma >= 95.0:
                        grade_stud = 'A+'
                    elif new_ma >= 89.0:
                        grade_stud = 'A'
                    elif new_ma >= 73.0:
                        grade_stud = 'B'
                    elif new_ma >= 60.0:
                        grade_stud = 'C'
                    elif new_ma >= 50.0:
                        grade_stud = 'D'
                    else:
                        grade_stud = 'F'
                self.update_student(email_id, new_ma ,new_course_id,grade_stud)
            elif prof_opt == 9:
                email_id = input("Enter student email: ")
                self.student_delete(email_id)
            elif prof_opt == 10:
                search_email = input("Enter email to search: ")
                self.search_fn(search_email)
            elif prof_opt == 11:
                sort_value = input("Sort by name/marks/email : ").lower()
                self.sort_fn(sort_value)
            elif prof_opt == 12:
                stud_id = input("Enter Student Email Id: ")
                self.student_report(stud_id)
            elif prof_opt == 13:
                prof_id = input("Enter Professor Email Id: ")
                p_name = input("Enter Professor Name: ")
                p_rank = input("Enter Professor Rank: ")
                p_course_id = input("Assign Course ID: ")
                self.add_professor(prof_id, p_name, p_rank, p_course_id)
            elif prof_opt == 14:
                prof_id = input("Enter Professor Email Id: ")
                new_pname = input("Enter Professor Name to update or leave empty : ")
                new_prank = input("Enter Professor Rank to update or leave empty : ")
                new_p_cid  = input("Enter Professor Course ID to update or leave empty : ")
                self.update_prof_details(prof_id, new_pname, new_prank,new_p_cid)
            elif prof_opt == 15:
                prof_id = input("Enter Professor Email Id: ")
                self.professor_delete(prof_id)
            elif prof_opt == 16:
                prof_id = input("Enter Professor Email Id: ")
                self.professor_report(prof_id)
            elif prof_opt == 17:
                self.logout_page()
                break
            else:
                print("Invalid Option!")

    def my_courses(self):
        student_a = next((stud for stud in self.student_details if self.curr_user.email_id == stud["Email_Id"]), None)
        for course in self.courses_details:
            if student_a["CourseId"] == course["CourseId"]:
                print(f'''
                        ------ My Course Work -------
                        Course Id: {student_a["CourseId"]}
                        Course Name: {course["CourseName"]}
                        Course Description: {course["CourseDescription"]}
                        ''')

    def student_grades(self):
        for stud in self.student_details:
            if stud["Email_Id"] == self.curr_user.email_id:
                print(f'''
                        ------ View Grades -------
                        Email Id: {stud["Email_Id"]}
                        Name: {stud["FirstName"]} {stud["LastName"]}
                        Course Id: {stud["CourseId"]} 
                        Grade_scored: {stud["Grade"]}
                        Marks_scored: {stud["Marks"]}
                        ''')
                
    def student_progress(self):
        stud = next((stud for stud in self.student_details if self.curr_user.email_id == stud["Email_Id"]), None)
        if stud:
            course_name = next((s_course for s_course in self.courses_details if stud["CourseId"] == s_course["CourseId"]), None)
            if course_name:
                course_n = f"{stud['CourseId']} {course_name['CourseName']}"
            else:
                course_n = stud["CourseId"]
            list_prof = [prof for prof in self.professors_details if stud["CourseId"] == prof["CourseId"]]
            if list_prof:
             for prof in list_prof:
                prof_label = "".join(f"{prof.get('p_Name','Not Known')}".strip().rstrip("()"))
            print(f'''
                    ------ My Progress Report -------
                    Student Name : {stud['FirstName']} {stud['LastName']}
                    Email Id: {stud["Email_Id"]}
                    Course: {course_n}
                    Mark: {stud['Marks']}
                    Grade: {stud['Grade']}
                    Professor Assigned: {prof_label}
                ''')

    def student_options(self):
        while True:
            print(''' 
                      1. My Grades
                      2. My Course Work
                      3. My Progress Report
                      4. Logout
                  ''')
            student_opt = int(input("Enter your option: "))
            if student_opt == 1: 
                self.student_grades()
            elif student_opt == 2: 
                self.my_courses()
            elif student_opt == 3: 
                self.student_progress()
            elif student_opt == 4:
                self.logout_page()
                break
            else:
                print("Invalid!")

class TestCheckMyGrade(unittest.TestCase):
    def setUp(self):
        self.UnitTest = MyGradeApp()

    def test_student_add_delete_modify_unit_test(self):
        initial_length_students = len(self.UnitTest.student_details)
        test_student = Student("test_stu@mysjsu.edu", "TestUnit", "Test_Data", "DATA200", "A", 97)
        
        if not "DATA200" == any(cou["CourseId"] for cou in self.UnitTest.courses_details):
            self.UnitTest.courses_details.append(
                {
                    "CourseId":"DATA200",
                    "CourseName":"testName",
                    "CourseDescription":"test Description"
                }
            )
        self.UnitTest.student_details.append(test_student.to_dict())
        
        self.assertEqual(initial_length_students + 1, len(self.UnitTest.student_details))

        self.UnitTest.student_details[-1]["CourseId"] = "DATA201"
        self.assertEqual("DATA201", self.UnitTest.student_details[-1]["CourseId"])

        stu_details_list = []
        for stu_details in self.UnitTest.student_details:
            if "test_stu@mysjsu.edu" != stu_details["Email_Id"]:
                stu_details_list.append(stu_details)
        self.UnitTest.student_details = stu_details_list
        self.assertEqual(initial_length_students, len(self.UnitTest.student_details))

    def test_course_add_delete_modify_unit_test(self):
        initial_length_courses = len(self.UnitTest.courses_details)
        self.UnitTest.courses_details.append(
            {
                "CourseId":"DATA1001",
                "CourseName":"Test Course for UnitTest",
                "CourseDescription":"Test Description"
            }
        )
        self.assertEqual(1 + initial_length_courses, len(self.UnitTest.courses_details))

        self.UnitTest.courses_details[-1]["CourseDescription"] = "Updated Course Description"
        self.assertEqual("Updated Course Description", self.UnitTest.courses_details[-1]["CourseDescription"])

        cou_list = []
        for cou in self.UnitTest.courses_details:
            if cou["CourseId"] != "DATA1001":
                cou_list.append(cou)
        self.UnitTest.courses_details = cou_list
        self.assertEqual(initial_length_courses, len(self.UnitTest.courses_details))

    def test_professor_add_delete_modify_unit_test(self):
        initial_length_professors = len(self.UnitTest.professors_details)
        if not any("DATA200" == cou["CourseId"] for cou in self.UnitTest.courses_details):
            self.UnitTest.courses_details.append(
                {
                    "CourseId":"DATA1001",
                    "CourseName":"Test Course for UnitTest",
                    "CourseDescription":"Test Description"
                }
            )
        self.UnitTest.professors_details.append(
            {
                "Professor_id":"testProf@mysjsu.edu",
                "p_Name":"Test Professor",
                "Rank":"Assistant Prof",
                "CourseId":"DATA200"
            }
        )
        self.assertEqual(1 + initial_length_professors, len(self.UnitTest.professors_details))

        self.UnitTest.professors_details[-1]["CourseId"] = "DATA201"
        self.assertEqual("DATA201", self.UnitTest.professors_details[-1]["CourseId"])

        prof_list = []
        for prof in self.UnitTest.professors_details:
            if "testProf@mysjsu.edu" != prof["Professor_id"]:
                prof_list.append(prof)
        self.UnitTest.professors_details = prof_list
        self.assertEqual(initial_length_professors, len(self.UnitTest.professors_details))

    def test_student_add_delete_modify_unit_test_1000_students(self):
        initial_length_students_1000 = len(self.UnitTest.student_details)

        start_add_time = time.time()
        test_records = []
        for i in range(1000):
            test_records.append(
                {
                    "Email_Id": f"TestUserEMAIL{i}@mysjsu.edu",
                    "First_Name": "TestUnit",
                    "Last_Name": f"TestUser{i}",
                    "CourseId": "DATA200",
                    "Grade": "A",
                    "Marks": str(90 + (i % 10))
                }
            )
        self.UnitTest.student_details.extend(test_records)
        end_add_time = time.time()
        print(f"Time Taken to add 1000 student records: {end_add_time - start_add_time:.6f}s")
        self.assertEqual(len(self.UnitTest.student_details), 1000 + initial_length_students_1000)

        start_modify_time = time.time()
        for record in self.UnitTest.student_details[-1000:]:
            if record.get("Email_Id", "").startswith("TestUserEMAIL"):
                record["Marks"] = "97"
                record["CourseId"] = "DATA2001"
        end_modify_time = time.time()
        print(f"Time Taken to modify 1000 student records: {end_modify_time - start_modify_time:.6f}s")

        modified_records = []
        for stu in self.UnitTest.student_details:
            if "DATA2001" == stu.get("CourseId") and stu.get("Email_Id", "").startswith("TestUserEMAIL"):
                modified_records.append(stu)

        self.assertEqual(1000, len(modified_records))

        start_delete_time = time.time()
        stu_list = []
        for stu in self.UnitTest.student_details:
            if not stu.get("Email_Id", "").startswith("TestUserEMAIL"):
                stu_list.append(stu)
        end_delete_time = time.time()
        self.UnitTest.student_details = stu_list
        print(f"Time Taken to delete 1000 student records: {end_delete_time - start_delete_time:.6f}s")

        self.assertEqual(len(self.UnitTest.student_details), initial_length_students_1000)


    def test_sort_1000_students(self):
        original_records = list(self.UnitTest.student_details)
        try:
            test_records = []
            # Create 1000 records
            for i in range(1000):
                test_records.append(
                    {
                        "Email_Id": f"TestUser{i}@sjsu.com", 
                        "FirstName": "Test", 
                        "LastName": str(i),
                        "CourseId": "DATA200",
                        "Grade": "A",
                        "Marks": str(90 + (i % 10))
                    }
                )
            self.UnitTest.student_details = test_records

            start_time = time.time()
            stu_list = []
            for stu in self.UnitTest.student_details:
                if "TestUser816" in stu['Email_Id']:
                    stu_list.append(stu)
            end_time = time.time()
            print(f"Time for Search in 1000 student records: {end_time - start_time:.6f}s")

            start_time = time.time()
            sorted(self.UnitTest.student_details, reverse=True, key=lambda stu: float(stu["Marks"]))
            end_time = time.time()
            print(f"Time for Sort by Marks for 1000 student records: {end_time - start_time:.6f}s")

            start_time = time.time()
            sorted(self.UnitTest.student_details, reverse=True, key=lambda stu: stu["Email_Id"])
            end_time = time.time()
            print(f"Time for Sort by Email_Id for 1000 student records: {end_time - start_time:.6f}s")

            self.assertEqual(len(self.UnitTest.student_details), 1000)
        finally:
            self.UnitTest.student_details = original_records

def main_mygradefn():
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        unittest.main(argv=[''], exit=False)
    else:
        my_grade_app = MyGradeApp()
        while True:
            print(''' CheckMyGrade Application 
                      1. Register
                      2. Login
                      3. Reset password
                      4. Exit
                  ''')
            user_input = int(input("Enter an option: "))
            if user_input == 1:
                u_email = input("Enter your email: ")
                u_password = input("Enter your password: ")
                u_role = input("Enter your Role: ")
                my_grade_app.register_user(u_email, u_password, u_role)
            elif user_input == 2:
                u_email = input("Enter your email: ")
                u_password = input("Enter your password: ")
                my_grade_app.login_page(u_email, u_password)
            elif user_input == 3:
                 u_email = input("Enter your email: ")
                 my_grade_app.reset_password(u_email)
            elif user_input == 4:
                break
            else:
                print("Invalid!")
    
if __name__ == "__main__":
    main_mygradefn()
    
