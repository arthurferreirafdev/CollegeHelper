'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, GradeHoraria } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, Plus, Trash2, Edit, BookOpen, Loader2, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

export default function GradesPage() {
  const router = useRouter();
  const [grade, setGrade] = useState<GradeHoraria | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadGrade();
  }, []);

  const loadGrade = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await apiClient.getGradeHoraria();
      setGrade(response.grade);
    } catch (err: any) {
      if (err.message.includes('404')) {
        setGrade(null);
      } else {
        setError('Erro ao carregar grade horária');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!grade) return;
    
    try {
      setDeleting(true);
      await apiClient.deleteGradeHoraria(grade.id);
      setGrade(null);
      setDeleteDialogOpen(false);
    } catch (err) {
      setError('Erro ao deletar grade horária');
    } finally {
      setDeleting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { label: string; className: string }> = {
      draft: { label: 'Rascunho', className: 'bg-gray-100 text-gray-800' },
      active: { label: 'Ativa', className: 'bg-green-100 text-green-800' },
      completed: { label: 'Concluída', className: 'bg-blue-100 text-blue-800' },
    };
    const config = variants[status] || variants.draft;
    return <Badge className={config.className}>{config.label}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Minhas Grades</h1>
          <p className="text-gray-600 mt-1">Gerencie sua grade horária</p>
        </div>
        {!grade && (
          <Button onClick={() => router.push('/main/grades/new')} className="bg-blue-600 hover:bg-blue-700 text-white">
            <Plus className="h-4 w-4 mr-2" />
            Nova Grade
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {!grade ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Calendar className="h-16 w-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Nenhuma grade encontrada</h3>
            <p className="text-gray-600 text-center mb-6">
              Você ainda não criou uma grade horária. Crie uma agora para começar a organizar suas disciplinas.
            </p>
            <Button onClick={() => router.push('/main/grades/new')} className="bg-blue-600 hover:bg-blue-700 text-white">
              <Plus className="h-4 w-4 mr-2" />
              Criar Grade
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-2xl">Grade Horária</CardTitle>
                <CardDescription className="mt-2">
                  {grade.semester && `Semestre: ${grade.semester}`}
                </CardDescription>
              </div>
              <div className="flex gap-2">
                {getStatusBadge(grade.status)}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <BookOpen className="h-5 w-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">
                      {grade.subjects?.length || 0} disciplinas
                    </p>
                    <p className="text-sm text-gray-600">
                      Total de créditos: {grade.subjects?.reduce((sum, s) => sum + (s.credits || 0), 0) || 0}
                    </p>
                  </div>
                </div>
              </div>

              {grade.subjects && grade.subjects.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-900">Disciplinas:</h4>
                  <div className="grid gap-2">
                    {grade.subjects.map((subject) => (
                      <div key={subject.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">{subject.name}</p>
                          <p className="text-sm text-gray-600">
                            {subject.code} • {subject.category} • {subject.credits} créditos
                          </p>
                        </div>
                        <Badge variant="outline">Nível {subject.difficulty_level}</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <Button
                  onClick={() => router.push(`/main/grades/edit/${grade.id}`)}
                  variant="outline"
                  className="flex-1"
                >
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
                <Button
                  onClick={() => setDeleteDialogOpen(true)}
                  variant="destructive"
                  className="flex-1"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Deletar
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmar exclusão</AlertDialogTitle>
            <AlertDialogDescription>
              Tem certeza que deseja deletar esta grade horária? Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {deleting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Deletar'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
