"""
Example usage of the ChatGPT Subject Advisor
This script demonstrates how to use the AI integration programmatically
"""

import os
from chatgpt_integration import ChatGPTSubjectAdvisor
from student_crud import StudentCRUD

def demo_ai_advisor():
    """Demonstrate the AI advisor capabilities"""
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable")
        print("You can get an API key from: https://platform.openai.com/api-keys")
        return
    
    # Initialize the advisor
    advisor = ChatGPTSubjectAdvisor(api_key)
    crud = StudentCRUD()
    
    print("🤖 ChatGPT Subject Advisor Demo")
    print("=" * 50)
    
    # Get a sample student
    students = crud.get_all_students()
    if not students:
        print("No students found. Please run database_setup.py first.")
        return
    
    sample_student = students[0]
    student_id = sample_student['id']
    
    print(f"Demo student: {sample_student['first_name']} {sample_student['last_name']}")
    print(f"Grade Level: {sample_student['grade_level']}")
    
    # Demo 1: Subject Recommendations
    print("\n1️⃣ Getting AI Subject Recommendations...")
    print("-" * 30)
    
    recommendations = advisor.get_subject_recommendations(
        student_id=student_id,
        additional_context="Student enjoys problem-solving and is interested in technology careers"
    )
    
    if recommendations.get("success"):
        print("✅ Recommendations generated successfully!")
        print(f"Preview: {recommendations['recommendation'][:200]}...")
    else:
        print(f"❌ Error: {recommendations.get('error')}")
    
    # Demo 2: Subject Fit Analysis
    print("\n2️⃣ Analyzing Subject Fit...")
    print("-" * 30)
    
    analysis = advisor.analyze_subject_fit(
        student_id=student_id,
        subject_name="Computer Science"
    )
    
    if analysis.get("success"):
        print("✅ Subject analysis completed!")
        print(f"Preview: {analysis['analysis'][:200]}...")
    else:
        print(f"❌ Error: {analysis.get('error')}")
    
    # Demo 3: Career Pathway Advice
    print("\n3️⃣ Getting Career Pathway Advice...")
    print("-" * 30)
    
    career_advice = advisor.get_career_pathway_advice(
        student_id=student_id,
        career_interest="Data Science"
    )
    
    if career_advice.get("success"):
        print("✅ Career advice generated!")
        print(f"Preview: {career_advice['advice'][:200]}...")
    else:
        print(f"❌ Error: {career_advice.get('error')}")
    
    # Demo 4: Study Plan Generation
    print("\n4️⃣ Generating Study Plan...")
    print("-" * 30)
    
    study_plan = advisor.generate_study_plan(
        student_id=student_id,
        selected_subjects=["Mathematics", "Computer Science", "Physics"],
        semester="Spring 2024"
    )
    
    if study_plan.get("success"):
        print("✅ Study plan created!")
        print(f"Preview: {study_plan['study_plan'][:200]}...")
    else:
        print(f"❌ Error: {study_plan.get('error')}")
    
    print("\n🎉 Demo completed!")
    print("\nTo run the interactive CLI, use: python scripts/ai_cli_interface.py")

def save_recommendations_to_file():
    """Example of saving AI recommendations to a file"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable")
        return
    
    advisor = ChatGPTSubjectAdvisor(api_key)
    crud = StudentCRUD()
    
    students = crud.get_all_students()
    if not students:
        print("No students found.")
        return
    
    # Generate recommendations for all students
    print("Generating recommendations for all students...")
    
    with open('student_recommendations.txt', 'w') as f:
        f.write("AI-GENERATED SUBJECT RECOMMENDATIONS\n")
        f.write("=" * 50 + "\n\n")
        
        for student in students:
            print(f"Processing {student['first_name']} {student['last_name']}...")
            
            recommendations = advisor.get_subject_recommendations(
                student_id=student['id'],
                additional_context="General academic guidance"
            )
            
            if recommendations.get("success"):
                f.write(f"Student: {recommendations['student_name']}\n")
                f.write(f"Grade: {recommendations['grade_level']}\n")
                f.write(f"Generated: {recommendations['timestamp']}\n")
                f.write("-" * 40 + "\n")
                f.write(recommendations['recommendation'])
                f.write("\n\n" + "=" * 50 + "\n\n")
            else:
                f.write(f"Error for {student['first_name']} {student['last_name']}: {recommendations.get('error')}\n\n")
    
    print("✅ Recommendations saved to 'student_recommendations.txt'")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run demo")
    print("2. Generate recommendations file")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == '1':
        demo_ai_advisor()
    elif choice == '2':
        save_recommendations_to_file()
    else:
        print("Invalid choice")
