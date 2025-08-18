import sys
from student_crud import StudentCRUD

class StudentSubjectCLI:
    def __init__(self):
        self.crud = StudentCRUD()
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("STUDENT SUBJECT MANAGEMENT SYSTEM")
        print("="*50)
        print("1. Student Management")
        print("2. Subject Management")
        print("3. Preference Management")
        print("4. Reports")
        print("0. Exit")
        print("-"*50)
    
    def student_menu(self):
        """Student management submenu"""
        while True:
            print("\n--- STUDENT MANAGEMENT ---")
            print("1. Add Student")
            print("2. View All Students")
            print("3. Find Student by Email")
            print("4. Update Student")
            print("5. Delete Student")
            print("0. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.add_student()
            elif choice == '2':
                self.view_all_students()
            elif choice == '3':
                self.find_student_by_email()
            elif choice == '4':
                self.update_student()
            elif choice == '5':
                self.delete_student()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def add_student(self):
        """Add a new student"""
        print("\n--- ADD NEW STUDENT ---")
        email = input("Email: ").strip()
        password = input("Password: ").strip()  # In real app, hash this
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        
        try:
            grade_level = int(input("Grade Level (9-12): ").strip())
            if grade_level < 9 or grade_level > 12:
                print("Grade level must be between 9 and 12")
                return
        except ValueError:
            print("Invalid grade level")
            return
        
        student_id = self.crud.create_student(email, f"hashed_{password}", first_name, last_name, grade_level)
        if student_id > 0:
            print(f"Student added successfully with ID: {student_id}")
    
    def view_all_students(self):
        """View all students"""
        print("\n--- ALL STUDENTS ---")
        students = self.crud.get_all_students()
        
        if not students:
            print("No students found.")
            return
        
        print(f"{'ID':<5} {'Name':<25} {'Email':<30} {'Grade':<6}")
        print("-" * 70)
        
        for student in students:
            name = f"{student['first_name']} {student['last_name']}"
            print(f"{student['id']:<5} {name:<25} {student['email']:<30} {student['grade_level']:<6}")
    
    def find_student_by_email(self):
        """Find student by email"""
        email = input("\nEnter student email: ").strip()
        student = self.crud.get_student_by_email(email)
        
        if student:
            print(f"\nStudent Found:")
            print(f"ID: {student['id']}")
            print(f"Name: {student['first_name']} {student['last_name']}")
            print(f"Email: {student['email']}")
            print(f"Grade Level: {student['grade_level']}")
            print(f"Created: {student['created_at']}")
        else:
            print("Student not found.")
    
    def update_student(self):
        """Update student information"""
        try:
            student_id = int(input("\nEnter student ID to update: ").strip())
        except ValueError:
            print("Invalid student ID")
            return
        
        student = self.crud.get_student(student_id)
        if not student:
            print("Student not found.")
            return
        
        print(f"\nUpdating student: {student['first_name']} {student['last_name']}")
        print("Leave blank to keep current value")
        
        first_name = input(f"First Name ({student['first_name']}): ").strip()
        last_name = input(f"Last Name ({student['last_name']}): ").strip()
        email = input(f"Email ({student['email']}): ").strip()
        grade_input = input(f"Grade Level ({student['grade_level']}): ").strip()
        
        updates = {}
        if first_name:
            updates['first_name'] = first_name
        if last_name:
            updates['last_name'] = last_name
        if email:
            updates['email'] = email
        if grade_input:
            try:
                grade_level = int(grade_input)
                if 9 <= grade_level <= 12:
                    updates['grade_level'] = grade_level
                else:
                    print("Grade level must be between 9 and 12")
                    return
            except ValueError:
                print("Invalid grade level")
                return
        
        if updates:
            self.crud.update_student(student_id, **updates)
        else:
            print("No changes made.")
    
    def delete_student(self):
        """Delete a student"""
        try:
            student_id = int(input("\nEnter student ID to delete: ").strip())
        except ValueError:
            print("Invalid student ID")
            return
        
        student = self.crud.get_student(student_id)
        if not student:
            print("Student not found.")
            return
        
        confirm = input(f"Are you sure you want to delete {student['first_name']} {student['last_name']}? (y/N): ").strip().lower()
        if confirm == 'y':
            self.crud.delete_student(student_id)
        else:
            print("Deletion cancelled.")
    
    def subject_menu(self):
        """Subject management submenu"""
        while True:
            print("\n--- SUBJECT MANAGEMENT ---")
            print("1. View All Subjects")
            print("2. View Subjects by Category")
            print("3. Add New Subject")
            print("0. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.view_all_subjects()
            elif choice == '2':
                self.view_subjects_by_category()
            elif choice == '3':
                self.add_subject()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def view_all_subjects(self):
        """View all subjects"""
        print("\n--- ALL SUBJECTS ---")
        subjects = self.crud.get_all_subjects()
        
        if not subjects:
            print("No subjects found.")
            return
        
        print(f"{'ID':<5} {'Name':<25} {'Category':<15} {'Difficulty':<10} {'Credits':<8}")
        print("-" * 70)
        
        for subject in subjects:
            print(f"{subject['id']:<5} {subject['name']:<25} {subject['category']:<15} {subject['difficulty_level']:<10} {subject['credits']:<8}")
    
    def view_subjects_by_category(self):
        """View subjects by category"""
        categories = ["STEM", "Humanities", "Arts", "Social Sciences"]
        
        print("\nAvailable categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        try:
            choice = int(input("\nSelect category (1-4): ").strip())
            if 1 <= choice <= 4:
                category = categories[choice - 1]
                subjects = self.crud.get_subjects_by_category(category)
                
                print(f"\n--- {category.upper()} SUBJECTS ---")
                if subjects:
                    for subject in subjects:
                        print(f"• {subject['name']} (Difficulty: {subject['difficulty_level']}/5)")
                        print(f"  {subject['description']}")
                        if subject['prerequisites']:
                            print(f"  Prerequisites: {subject['prerequisites']}")
                        print()
                else:
                    print(f"No subjects found in {category} category.")
            else:
                print("Invalid category selection.")
        except ValueError:
            print("Invalid input.")
    
    def add_subject(self):
        """Add a new subject"""
        print("\n--- ADD NEW SUBJECT ---")
        name = input("Subject Name: ").strip()
        description = input("Description: ").strip()
        
        categories = ["STEM", "Humanities", "Arts", "Social Sciences"]
        print("\nCategories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        try:
            cat_choice = int(input("Select category (1-4): ").strip())
            if not (1 <= cat_choice <= 4):
                print("Invalid category selection.")
                return
            category = categories[cat_choice - 1]
            
            difficulty = int(input("Difficulty Level (1-5): ").strip())
            if not (1 <= difficulty <= 5):
                print("Difficulty must be between 1 and 5.")
                return
            
            credits = int(input("Credits (default 1): ").strip() or "1")
            prerequisites = input("Prerequisites (optional): ").strip() or None
            
            subject_id = self.crud.create_subject(name, description, category, difficulty, credits, prerequisites)
            if subject_id > 0:
                print(f"Subject added successfully with ID: {subject_id}")
                
        except ValueError:
            print("Invalid input.")
    
    def preference_menu(self):
        """Preference management submenu"""
        while True:
            print("\n--- PREFERENCE MANAGEMENT ---")
            print("1. Add Student Preference")
            print("2. View Student Preferences")
            print("0. Back to Main Menu")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.add_preference()
            elif choice == '2':
                self.view_preferences()
            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def add_preference(self):
        """Add a student preference"""
        try:
            student_id = int(input("\nEnter student ID: ").strip())
            student = self.crud.get_student(student_id)
            if not student:
                print("Student not found.")
                return
            
            print(f"Adding preference for: {student['first_name']} {student['last_name']}")
            
            # Show available subjects
            subjects = self.crud.get_all_subjects()
            print("\nAvailable subjects:")
            for subject in subjects:
                print(f"{subject['id']}. {subject['name']} ({subject['category']})")
            
            subject_id = int(input("\nEnter subject ID: ").strip())
            if not any(s['id'] == subject_id for s in subjects):
                print("Invalid subject ID.")
                return
            
            interest_level = int(input("Interest Level (1-5): ").strip())
            if not (1 <= interest_level <= 5):
                print("Interest level must be between 1 and 5.")
                return
            
            priority = input("Priority (optional): ").strip()
            priority = int(priority) if priority else None
            
            notes = input("Notes (optional): ").strip() or None
            
            pref_id = self.crud.add_student_preference(student_id, subject_id, interest_level, priority, notes)
            if pref_id > 0:
                print("Preference added successfully!")
                
        except ValueError:
            print("Invalid input.")
    
    def view_preferences(self):
        """View student preferences"""
        try:
            student_id = int(input("\nEnter student ID: ").strip())
            student = self.crud.get_student(student_id)
            if not student:
                print("Student not found.")
                return
            
            preferences = self.crud.get_student_preferences(student_id)
            
            print(f"\n--- PREFERENCES FOR {student['first_name']} {student['last_name']} ---")
            if preferences:
                for pref in preferences:
                    print(f"• {pref['subject_name']} ({pref['category']})")
                    print(f"  Interest Level: {pref['interest_level']}/5")
                    if pref['priority']:
                        print(f"  Priority: {pref['priority']}")
                    if pref['notes']:
                        print(f"  Notes: {pref['notes']}")
                    print()
            else:
                print("No preferences found for this student.")
                
        except ValueError:
            print("Invalid student ID.")
    
    def reports_menu(self):
        """Reports submenu"""
        print("\n--- REPORTS ---")
        print("1. Student Count by Grade")
        print("2. Popular Subjects")
        print("3. Subject Distribution by Category")
        print("0. Back to Main Menu")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            self.student_count_by_grade()
        elif choice == '2':
            print("Popular subjects report - Feature coming soon!")
        elif choice == '3':
            self.subject_distribution()
        elif choice == '0':
            return
        else:
            print("Invalid choice.")
    
    def student_count_by_grade(self):
        """Show student count by grade level"""
        students = self.crud.get_all_students()
        grade_counts = {}
        
        for student in students:
            grade = student['grade_level']
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        print("\n--- STUDENT COUNT BY GRADE ---")
        for grade in sorted(grade_counts.keys()):
            print(f"Grade {grade}: {grade_counts[grade]} students")
    
    def subject_distribution(self):
        """Show subject distribution by category"""
        subjects = self.crud.get_all_subjects()
        category_counts = {}
        
        for subject in subjects:
            category = subject['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print("\n--- SUBJECT DISTRIBUTION BY CATEGORY ---")
        for category, count in category_counts.items():
            print(f"{category}: {count} subjects")
    
    def run(self):
        """Main application loop"""
        print("Welcome to the Student Subject Management System!")
        
        while True:
            self.display_menu()
            choice = input("Enter your choice: ").strip()
            
            if choice == '1':
                self.student_menu()
            elif choice == '2':
                self.subject_menu()
            elif choice == '3':
                self.preference_menu()
            elif choice == '4':
                self.reports_menu()
            elif choice == '0':
                print("Thank you for using the Student Subject Management System!")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Initialize database first
    from database_setup import create_database, seed_sample_data
    create_database()
    seed_sample_data()
    
    # Run the CLI
    cli = StudentSubjectCLI()
    cli.run()
