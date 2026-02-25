// "use server";
import { RegisterStudentFormData } from "@/components/forms/RegisterStudentForm";

export interface RegisterResponse {
  success?: boolean;
  student_id?: number;
  message?: string;
  error?: string;
}

export async function registerStudent(
  data: RegisterStudentFormData
): Promise<RegisterResponse> {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/students/register`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...data,
          grade_level: Number(data.grade_level), // 🔥 IMPORTANTE
        }),
      }
    );

    const result = await response.json();

    if (!response.ok) {
      return { error: result.error || "Registration failed" };
    }

    return result;

  } catch (error) {
    console.error(error);
    return { error: "Unexpected error occurred" };
  }
}