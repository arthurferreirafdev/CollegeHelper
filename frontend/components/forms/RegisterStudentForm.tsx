"use client";

import { useState } from "react";

export interface RegisterStudentFormData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  grade_level: string;
  date_of_birth?: string;
  phone_number?: string;
  guardian_email?: string;
}

interface Props {
  onSubmit: (data: RegisterStudentFormData) => void;
  loading?: boolean;
  error?: string | null;
}

export default function RegisterStudentForm({
  onSubmit,
  loading = false,
  error = null,
}: Props) {
  const [formData, setFormData] = useState<RegisterStudentFormData>({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    grade_level: "",
    date_of_birth: "",
    phone_number: "",
    guardian_email: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="bg-white/80 backdrop-blur-xl shadow-2xl shadow-black/10 rounded-3xl p-8 border border-gray-200/60">
        
        <h2 className="text-3xl font-semibold text-center tracking-tight text-gray-900">
          Registrar estudante
        </h2>

        

        <form onSubmit={handleSubmit} className="space-y-4 mt-6">

          <Input name="email" type="email" placeholder="Email" required onChange={handleChange} />
          <Input name="password" type="password" placeholder="Password" required onChange={handleChange} />
          <Input name="first_name" type="text" placeholder="First Name" required onChange={handleChange} />
          <Input name="last_name" type="text" placeholder="Last Name" required onChange={handleChange} />
          <Input name="grade_level" type="text" placeholder="Grade Level" required onChange={handleChange} />
          <Input name="date_of_birth" type="date" onChange={handleChange} />
          <Input name="phone_number" type="text" placeholder="Phone Number" onChange={handleChange} />
          <Input name="guardian_email" type="email" placeholder="Guardian Email" onChange={handleChange} />

          {error && (
            <p className="text-red-500 text-sm text-center pt-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-4 bg-blue-500 hover:bg-blue-600 active:scale-[0.98] transition-all text-white font-medium py-3 rounded-2xl shadow-md disabled:opacity-60"
          >
            {loading ? "Creating..." : "Registrar estudante"}
          </button>

        </form>
      </div>
    </div>
  );
}

function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className="w-full bg-gray-100 focus:bg-white transition-all duration-200 
                 border border-transparent focus:border-blue-400
                 rounded-2xl px-4 py-3 text-sm outline-none
                 shadow-inner focus:shadow-md"
    />
  );
}