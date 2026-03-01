"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import RegisterStudentForm, {
  RegisterStudentFormData,
} from "@/components/forms/RegisterStudentForm";
import { registerStudent } from "./actions";

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (data: RegisterStudentFormData) => {
    setLoading(true);
    setError(null);

    const result = await registerStudent(data);

    if (result.error) {
      setError(result.error);
      setLoading(false);
      return;
    }

    router.push("/login");
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-4
                     bg-gradient-to-br from-gray-50 via-white to-gray-100">
      <RegisterStudentForm
        onSubmit={handleRegister}
        loading={loading}
        error={error}
      />
    </main>
  );
}