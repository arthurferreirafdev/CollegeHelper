'use client';

import { useEffect, useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Plus, Trash2, CheckCircle, AlertTriangle } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState<any[]>([]);
  const [myPreferences, setMyPreferences] = useState<any[]>([]);
  const [studentProfile, setStudentProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // Estados para o Modal de Validação de Período
  const [showWarningModal, setShowWarningModal] = useState(false);
  const [pendingSubject, setPendingSubject] = useState<any>(null);
  
  const { toast } = useToast();
  const token = localStorage.getItem('auth_token');

  useEffect(() => {
    async function fetchData() {
      try {
        const profileRes = await fetch('http://localhost:5000/api/students/profile', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const profileData = await profileRes.json();
        setStudentProfile(profileData.student);

        const subjectsRes = await fetch('http://localhost:5000/api/subjects');
        const subjectsData = await subjectsRes.json();
        setSubjects(subjectsData.subjects);

        const prefsRes = await fetch('http://localhost:5000/api/preferences', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const prefsData = await prefsRes.json();
        setMyPreferences(prefsData.preferences || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [token]);

  // Função para extrair o número do período da string (ex: "2º Período" -> 2)
  const getPeriodNumber = (periodStr: string) => {
    const match = periodStr.match(/\d+/);
    return match ? parseInt(match[0]) : 0;
  };

  const checkAndInclude = (subject: any) => {
    const subjectPeriod = getPeriodNumber(subject.semester);
    const studentPeriod = studentProfile?.grade_level || 1;

    // Se a disciplina for de um período superior ao do aluno, mostra aviso
    if (subjectPeriod > studentPeriod) {
      setPendingSubject(subject);
      setShowWarningModal(true);
    } else {
      executeInclude(subject.id);
    }
  };

  const executeInclude = async (subjectId: number) => {
    try {
      const res = await fetch('http://localhost:5000/api/preferences', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ subject_id: subjectId, interest_level: 5 })
      });
      if (res.ok) {
        toast({ title: "Sucesso", description: "Disciplina incluída na sua grade!" });
        setShowWarningModal(false);
        window.location.reload(); 
      }
    } catch (err) {
      toast({ title: "Erro", description: "Não foi possível incluir.", variant: "destructive" });
    }
  };

  const handleRemove = async (preferenceId: number) => {
    try {
      const res = await fetch(`http://localhost:5000/api/preferences/${preferenceId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        toast({ title: "Removida", description: "Disciplina removida da sua grade." });
        window.location.reload();
      }
    } catch (err) {
      toast({ title: "Erro", description: "Não foi possível remover.", variant: "destructive" });
    }
  };

  if (loading) return <div className="p-12 text-center"><Loader2 className="animate-spin mx-auto" /></div>;

  const myCourseSubjects = subjects.filter(s => s.course_id === studentProfile?.course_id);
  const otherCourseSubjects = subjects.filter(s => s.course_id !== studentProfile?.course_id);
  const selectedIds = myPreferences.map(p => p.subject_id);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Gestão de Disciplinas</h1>

      <Tabs defaultValue="my-course" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-8">
          <TabsTrigger value="my-course">Meu Curso</TabsTrigger>
          <TabsTrigger value="others">Outros Cursos</TabsTrigger>
          <TabsTrigger value="my-list">Minhas Escolhas ({myPreferences.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="my-course" className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {myCourseSubjects.map(sub => (
            <SubjectCard key={sub.id} sub={sub} isIncluded={selectedIds.includes(sub.id)} onInclude={() => checkAndInclude(sub)} />
          ))}
        </TabsContent>

        <TabsContent value="others" className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {otherCourseSubjects.map(sub => (
            <SubjectCard key={sub.id} sub={sub} isIncluded={selectedIds.includes(sub.id)} onInclude={() => checkAndInclude(sub)} />
          ))}
        </TabsContent>

        <TabsContent value="my-list">
          <Card>
            <CardHeader><CardTitle>Grade Atual Selecionada</CardTitle></CardHeader>
            <CardContent>
              {myPreferences.length === 0 ? <p>Nenhuma disciplina selecionada.</p> : (
                <ul className="space-y-4">
                  {myPreferences.map((p: any) => (
                    <li key={p.id} className="flex justify-between items-center p-4 border rounded-lg bg-white shadow-sm">
                      <div className="space-y-1">
                        <span className="font-semibold block">{p.subject_name}</span>
                        <span className="text-sm text-muted-foreground">{p.subject_code}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge className="bg-green-100 text-green-700">Incluída</Badge>
                        <Button 
                          variant="ghost" 
                          size="icon" 
                          onClick={() => handleRemove(p.id)}
                          className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-5 w-5" />
                        </Button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* MODAL DE AVISO DE PERÍODO */}
      <Dialog open={showWarningModal} onOpenChange={setShowWarningModal}>
        <DialogContent className="sm:max-w-md text-center">
          <DialogHeader>
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 mb-4">
              <AlertTriangle className="h-6 w-6 text-amber-600" />
            </div>
            <DialogTitle className="text-center text-xl">Aviso de Período</DialogTitle>
            <DialogDescription className="text-center text-md pt-2">
              A disciplina selecionada pertence ao <strong>{pendingSubject?.semester}</strong>, e poderá ser barrada a matrícula pela coordenação do curso. Tem certeza que deseja adicionar à sua lista?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="sm:justify-center mt-6 gap-2">
            <Button variant="outline" onClick={() => setShowWarningModal(false)} className="px-8">
              Cancelar
            </Button>
            <Button onClick={() => executeInclude(pendingSubject?.id)} className="bg-blue-600 px-8">
              Confirmar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

import { User, CalendarDays } from 'lucide-react'; // Adicione estas importações

function SubjectCard({ sub, isIncluded, onInclude }: any) {
  return (
    <Card className={isIncluded ? "border-green-200 bg-green-50/30" : "hover:shadow-md transition-shadow"}>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <Badge variant="outline" className="text-[10px] uppercase tracking-wider">{sub.category}</Badge>
          <span className="text-xs font-medium text-muted-foreground">{sub.semester}</span>
        </div>
        <CardTitle className="text-lg mt-2">{sub.name}</CardTitle>
        <CardDescription className="font-mono text-xs">{sub.code}</CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4 pb-4">
        <p className="text-sm text-gray-600 line-clamp-2">
          {sub.description || "Sem descrição disponível."}
        </p>
        
        <div className="space-y-2 pt-2 border-t border-slate-100">
          {/* HORÁRIO DA AULA */}
          <div className="flex items-start gap-2 text-xs text-slate-600">
            <CalendarDays className="h-4 w-4 text-blue-500 mt-0.5" />
            <span className="leading-tight">
              <strong>Horário:</strong><br />
              {sub.schedule || "A definir"}
            </span>
          </div>
          
          {/* PROFESSOR RESPONSÁVEL */}
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <User className="h-4 w-4 text-blue-500" />
            <span>
              <strong>Professor:</strong> {sub.teacher_name || "A definir"}
            </span>
          </div>
        </div>
      </CardContent>

      <CardFooter className="pt-0">
        {!isIncluded ? (
          <Button onClick={onInclude} className="w-full bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" /> Incluir na Grade
          </Button>
        ) : (
          <Button variant="outline" disabled className="w-full text-green-700 border-green-200">
            <CheckCircle className="h-4 w-4 mr-2" /> Já Adicionada
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}