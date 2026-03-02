'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation'; // Importamos o useRouter
import { cn } from '@/lib/utils';
import { GraduationCap, LogOut, User, BookOpen, Send, LayoutDashboard, Calendar } from 'lucide-react';
import { apiClient } from '@/lib/api'; // Importamos o cliente da API

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter(); // Inicializamos o router para o redirecionamento

  const navItems = [
    { name: 'Enviar Grade', href: '/main', icon: Send },
    { name: 'Minhas Grades', href: '/main/grades', icon: Calendar },
    { name: 'Listar Disciplinas', href: '/main/subjects', icon: BookOpen },
    { name: 'Perfil', href: '/main/profile', icon: User },
  ];

  // Função que trata o clique no botão Sair
  const handleLogout = () => {
    // 1. Remove o token (localStorage/Cookies) via apiClient
    apiClient.logout(); 
    
    // 2. Redireciona para a tela de login (raiz)
    router.push('/'); 
  };

  return (
    <nav className="border-b bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-blue-600 rounded-lg">
              <GraduationCap className="h-6 w-6 text-white" />
            </div>
            <span className="font-bold text-xl text-gray-900">CollegeHelper</span>
          </div>

          <div className="flex space-x-6">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex flex-col items-center gap-1 px-2 py-1 text-xs font-medium transition-colors",
                  pathname === item.href 
                    ? "text-blue-700 border-b-2 border-blue-700" 
                    : "text-gray-600 hover:text-blue-600"
                )}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            ))}
          </div>

          {/* Adicionamos o onClick chamando a nossa função */}
          <button 
            onClick={handleLogout}
            className="text-gray-500 hover:text-red-600 flex items-center gap-1 text-sm transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Sair
          </button>
        </div>
      </div>
    </nav>
  );
}