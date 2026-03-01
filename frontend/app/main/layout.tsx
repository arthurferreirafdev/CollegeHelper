'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Navbar } from '@/components/navbar';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from '@/components/ui/button';
import { LockKeyhole, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const [isAuth, setIsAuth] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true); // Novo estado de carregamento
  const [showAuthModal, setShowAuthModal] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // 1. Tenta buscar por todos os nomes possíveis que a equipe pode ter usado
    const token = localStorage.getItem('token') || 
                  localStorage.getItem('jwt') || 
                  localStorage.getItem('auth_token') ||
                  localStorage.getItem('student_token');
    if (token) {
      setIsAuth(true);
      setCheckingAuth(false);
    } else {
      // Se realmente não achou nada em lugar nenhum
      setIsAuth(false);
      setCheckingAuth(false);
      setShowAuthModal(true);
    }
  }, []);

  const handleRedirectLogin = () => {
    setShowAuthModal(false);
    apiClient.logout();
    router.push('/');
  };

  // Enquanto verifica, mostra apenas um carregamento centralizado
  if (checkingAuth) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {isAuth && <Navbar />}
      
      <main className="pb-10">
        {isAuth ? children : <div className="h-screen bg-slate-50" />}
      </main>

      <Dialog open={showAuthModal} onOpenChange={handleRedirectLogin}>
        <DialogContent className="sm:max-w-md text-center pointer-events-none">
          <DialogHeader>
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 mb-4">
              <LockKeyhole className="h-6 w-6 text-amber-600" />
            </div>
            <DialogTitle className="text-center text-xl font-bold">Sessão Necessária</DialogTitle>
            <DialogDescription className="text-center text-md pt-2">
              Você precisa estar logado para acessar esta área. Por favor, identifique-se novamente.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="sm:justify-center mt-4 pointer-events-auto">
            <Button type="button" onClick={handleRedirectLogin} className="px-8 bg-blue-600 hover:bg-blue-700">
              Ir para o Login
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}