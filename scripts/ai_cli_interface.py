import os
from chatgpt_integration import ChatGPTSubjectAdvisor
from student_crud import StudentCRUD

class AIAdvisorCLI:
    def __init__(self):
        # Get API key from environment variable or prompt user
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("OpenAI API key not found in environment variables.")
            api_key = input("Please enter your OpenAI API key: ").strip()
            if not api_key:
                print("API key is required to use AI features.")
                exit(1)
        
        self.advisor = ChatGPTSubjectAdvisor(api_key)
        self.crud = StudentCRUD()
    
    def display_menu(self):
        """Display the AI advisor menu"""
        print("\n" + "="*60)
        print("AI-POWERED SUBJECT ADVISOR")
        print("="*60)
        print("1. Get Subject Recommendations")
        print("2. Analyze Subject Fit")
        print("3. Career Pathway Advice")
        print("4. Generate Study Plan")
        print("5. List Students")
        print("0. Exit")
        print("-"*60)
    
    def list_students(self):
        """Display all students for selection"""
        students = self.crud.get_all_students()
        
        if not students:
            print("No students found. Please add students first.")
            return None
        
        print("\n--- AVAILABLE STUDENTS ---")
        print(f"{'ID':<5} {'Name':<25} {'Email':<30} {'Grade':<6}")
        print("-" * 70)
        
        for student in students:
            name = f"{student['first_name']} {student['last_name']}"
            print(f"{student['id']:<5} {name:<25} {student['email']:<30} {student['grade_level']:<6}")
        
        return students
    
    def get_student_selection(self) -> int:
        """Get student selection from user"""
        students = self.list_students()
        if not students:
            return -1
        
        try:
            student_id = int(input("\nEnter student ID: ").strip())
            if any(s['id'] == student_id for s in students):
                return student_id
            else:
                print("Invalid student ID.")
                return -1
        except ValueError:
            print("Invalid input. Please enter a number.")
            return -1
    
    def get_subject_recommendations(self):
        """Get AI-powered subject recommendations"""
        print("\n--- AI SUBJECT RECOMMENDATIONS ---")
        
        student_id = self.get_student_selection()
        if student_id == -1:
            return
        
        additional_context = input("\nEnter additional context (interests, goals, etc.): ").strip()
        
        print("\nGenerating recommendations... (this may take a moment)")
        
        result = self.advisor.get_subject_recommendations(student_id, additional_context)
        
        if result.get("success"):
            print(f"\n{'='*60}")
            print(f"RECOMMENDATIONS FOR {result['student_name'].upper()}")
            print(f"Grade Level: {result['grade_level']}")
            print(f"Generated: {result['timestamp']}")
            print(f"{'='*60}")
            print(result['recommendation'])
        else:
            print(f"Error: {result.get('error')}")
    
    def analyze_subject_fit(self):
        """Analyze how well a subject fits a student"""
        print("\n--- SUBJECT FIT ANALYSIS ---")
        
        student_id = self.get_student_selection()
        if student_id == -1:
            return
        
        # Show available subjects
        subjects = self.crud.get_all_subjects()
        print("\nAvailable subjects:")
        for i, subject in enumerate(subjects, 1):
            print(f"{i}. {subject['name']} ({subject['category']})")
        
        subject_name = input("\nEnter subject name to analyze: ").strip()
        
        print("\nAnalyzing subject fit... (this may take a moment)")
        
        result = self.advisor.analyze_subject_fit(student_id, subject_name)
        
        if result.get("success"):
            print(f"\n{'='*60}")
            print(f"SUBJECT FIT ANALYSIS")
            print(f"Student: {result['student_name']}")
            print(f"Subject: {result['subject']}")
            print(f"Generated: {result['timestamp']}")
            print(f"{'='*60}")
            print(result['analysis'])
        else:
            print(f"Error: {result.get('error')}")
    
    def get_career_advice(self):
        """Get career pathway advice"""
        print("\n--- CAREER PATHWAY ADVICE ---")
        
        student_id = self.get_student_selection()
        if student_id == -1:
            return
        
        career_interest = input("\nEnter career interest/field: ").strip()
        if not career_interest:
            print("Career interest is required.")
            return
        
        print("\nGenerating career advice... (this may take a moment)")
        
        result = self.advisor.get_career_pathway_advice(student_id, career_interest)
        
        if result.get("success"):
            print(f"\n{'='*60}")
            print(f"CAREER PATHWAY ADVICE")
            print(f"Student: {result['student_name']}")
            print(f"Career Interest: {result['career_interest']}")
            print(f"Generated: {result['timestamp']}")
            print(f"{'='*60}")
            print(result['advice'])
        else:
            print(f"Error: {result.get('error')}")
    
    def generate_study_plan(self):
        """Generate a personalized study plan"""
        print("\n--- STUDY PLAN GENERATOR ---")
        
        student_id = self.get_student_selection()
        if student_id == -1:
            return
        
        # Show available subjects
        subjects = self.crud.get_all_subjects()
        print("\nAvailable subjects:")
        for i, subject in enumerate(subjects, 1):
            print(f"{i}. {subject['name']} ({subject['category']})")
        
        print("\nEnter subject names (comma-separated):")
        subject_input = input("Subjects: ").strip()
        selected_subjects = [s.strip() for s in subject_input.split(',') if s.strip()]
        
        if not selected_subjects:
            print("At least one subject is required.")
            return
        
        semester = input("Enter semester (e.g., Fall 2024): ").strip()
        if not semester:
            semester = "Current Semester"
        
        print("\nGenerating study plan... (this may take a moment)")
        
        result = self.advisor.generate_study_plan(student_id, selected_subjects, semester)
        
        if result.get("success"):
            print(f"\n{'='*60}")
            print(f"PERSONALIZED STUDY PLAN")
            print(f"Student: {result['student_name']}")
            print(f"Semester: {result['semester']}")
            print(f"Subjects: {', '.join(result['subjects'])}")
            print(f"Generated: {result['timestamp']}")
            print(f"{'='*60}")
            print(result['study_plan'])
        else:
            print(f"Error: {result.get('error')}")
    
    def run(self):
        """Main application loop"""
        print("Welcome to the AI-Powered Subject Advisor!")
        print("This system uses ChatGPT to provide personalized academic guidance.")
        
        while True:
            self.display_menu()
            choice = input("Enter your choice: ").strip()
            
            if choice == '1':
                self.get_subject_recommendations()
            elif choice == '2':
                self.analyze_subject_fit()
            elif choice == '3':
                self.get_career_advice()
            elif choice == '4':
                self.generate_study_plan()
            elif choice == '5':
                self.list_students()
                input("\nPress Enter to continue...")
            elif choice == '0':
                print("Thank you for using the AI Subject Advisor!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Initialize database first
    from database_setup import create_database, seed_sample_data
    create_database()
    seed_sample_data()
    
    # Run the AI CLI
    cli = AIAdvisorCLI()
    cli.run()
