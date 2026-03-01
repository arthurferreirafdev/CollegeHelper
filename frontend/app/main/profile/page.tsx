'use client';

import { useEffect, useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, CheckCircle2 } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
// Importando os componentes de Select do shadcn/ui
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const { toast } = useToast();

  // Lista de cursos fictícia (depois isso pode vir de uma rota GET /api/cursos do backend)
  const cursosDisponiveis = [
    { id: "1", nome: "Sistemas de Informação" },
    { id: "2", nome: "Ciência da Computação" },
  ];

  useEffect(() => {
    async function loadProfile() {
      try {
        const token = localStorage.getItem('token') || localStorage.getItem('jwt') || localStorage.getItem('auth_token');
        if (!token) throw new Error("Token não encontrado");

        const response = await fetch('http://localhost:5000/api/students/profile', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) throw new Error(`Erro na API: ${response.status}`);

        const data = await response.json();
        setProfile(data.student);
      } catch (error) {
        toast({ 
          title: 'Erro de Autenticação', 
          description: 'Sua sessão expirou. Por favor, faça login novamente.', 
          variant: 'destructive' 
        });
      } finally {
        setIsLoading(false);
      }
    }
    
    loadProfile();
  }, [toast]);

  const handleUpdate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSaving(true);

    const formData = new FormData(e.currentTarget);
    const updatedData = {
      first_name: formData.get('first_name'),
      last_name: formData.get('last_name'),
      date_of_birth: formData.get('date_of_birth') || null,
      enrollment_number: formData.get('enrollment_number'), // A chave agora é enrollment_number
      grade_level: parseInt(formData.get('grade_level') as string) || 1, // A chave agora é grade_level
      course_id: formData.get('course_id'), // A chave agora é course_id
    };

    try {
      const token = localStorage.getItem('token') || localStorage.getItem('jwt') || localStorage.getItem('auth_token');
      
      const response = await fetch('http://localhost:5000/api/students/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updatedData)
      });

      if (!response.ok) throw new Error("Falha ao salvar");

      setShowSuccessModal(true);

    } catch (error) {
      toast({ 
        title: 'Erro', 
        description: 'Não foi possível atualizar o perfil. Tente novamente.', 
        variant: 'destructive' 
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <div className="flex justify-center items-center h-full p-12">Carregando perfil...</div>;
  }

  if (!profile) return null;

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Meu Perfil</h1>
        <p className="text-muted-foreground mt-2">
          Gerencie suas informações pessoais e visualize seus dados acadêmicos.
        </p>
      </div>

      <form onSubmit={handleUpdate}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Dados Pessoais</CardTitle>
              <CardDescription>Informações básicas da sua conta de usuário.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Nome</label>
                <Input name="first_name" defaultValue={profile.first_name || profile.nome} required />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Sobrenome</label>
                <Input name="last_name" defaultValue={profile.last_name || ''} required />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Email</label>
                <Input defaultValue={profile.email} disabled className="bg-muted" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Data de Nascimento</label>
                <Input name="date_of_birth" type="date" defaultValue={profile.date_of_birth || profile.data_nascimento || ''} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Dados Acadêmicos</CardTitle>
              <CardDescription>Informações do seu vínculo institucional.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Curso</label>
                <Select name="course_id" defaultValue={profile.course_id?.toString()}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o seu curso" />
                  </SelectTrigger>
                  <SelectContent>
                    {cursosDisponiveis.map((curso) => (
                      <SelectItem key={curso.id} value={curso.id}>
                        {curso.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Matrícula</label>
                <Input name="enrollment_number" placeholder="Ex: 12011BSI200" defaultValue={profile.enrollment_number || ''} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Período Atual</label>
                {/* min="1" garante que ninguém coloque período 0 ou negativo */}
                <Input name="grade_level" type="number" min="1" max="12" defaultValue={profile.grade_level || 1} required />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-end pt-6">
          <Button type="submit" size="lg" disabled={isSaving}>
            {isSaving ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Salvando...</> : "Salvar Alterações"}
          </Button>
        </div>
      </form>

      <Dialog open={showSuccessModal} onOpenChange={setShowSuccessModal}>
        <DialogContent className="sm:max-w-md text-center">
          <DialogHeader>
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100 mb-4">
              <CheckCircle2 className="h-6 w-6 text-green-600" />
            </div>
            <DialogTitle className="text-center text-xl">Perfil Atualizado!</DialogTitle>
            <DialogDescription className="text-center text-md pt-2">
              Suas informações foram salvas com sucesso.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="sm:justify-center mt-4">
            <Button type="button" onClick={() => setShowSuccessModal(false)} className="px-8">
              Entendi
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}