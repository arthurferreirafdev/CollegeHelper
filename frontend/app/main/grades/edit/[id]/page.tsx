'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { apiClient, GradeHoraria, Subject } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Loader2, Save, Plus, X, BookOpen } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

export default function EditGradePage() {
  const router = useRouter();
  const params = useParams();
  const gradeId = Number(params.id);

  const [grade, setGrade] = useState<GradeHoraria | null>(null);
  const [semester, setSemester] = useState('');
  const [status, setStatus] = useState('draft');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [addingSubject, setAddingSubject] = useState(false);

  useEffect(() => {
    loadGrade();
    loadSubjects();
  }, [gradeId]);

  const loadGrade = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getGradeHoraria();
      setGrade(response.grade);
      setSemester(response.grade.semester || '');
      setStatus(response.grade.status);
    } catch (err: any) {
      setError('Erro ao carregar grade');
    } finally {
      setLoading(false);
    }
  };

  const loadSubjects = async () => {
    try {
      const response = await apiClient.getSubjects();
      setSubjects(response.subjects);
    } catch (err) {
      console.error('Erro ao carregar disciplinas');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError('');
      await apiClient.updateGradeHoraria(gradeId, { semester, status });
      router.push('/main/grades');
    } catch (err: any) {
      setError(err.message || 'Erro ao atualizar grade');
    } finally {
      setSaving(false);
    }
  };

  const handleAddSubject = async (subjectId: number) => {
    try {
      setAddingSubject(true);
      await apiClient.addSubjectToGrade(gradeId, subjectId);
      await loadGrade();
      setDialogOpen(false);
    } catch (err: any) {
      setError('Erro ao adicionar disciplina');
    } finally {
      setAddingSubject(false);
    }
  };

  const handleRemoveSubject = async (subjectId: number) => {
    try {
      await apiClient.removeSubjectFromGrade(gradeId, subjectId);
      await loadGrade();
    } catch (err: any) {
      setError('Erro ao remover disciplina');
    }
  };

  const availableSubjects = subjects.filter(
    (s) => !grade?.subjects?.some((gs) => gs.id === s.id)
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <Button variant="ghost" onClick={() => router.back()} className="mb-6">
        <ArrowLeft className="h-4 w-4 mr-2" />
        Voltar
      </Button>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Editar Grade Horária</CardTitle>
            <CardDescription>Atualize as informações da grade</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="semester">Semestre</Label>
                <Input
                  id="semester"
                  placeholder="Ex: 2024.1"
                  value={semester}
                  onChange={(e) => setSemester(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <Select value={status} onValueChange={setStatus}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Rascunho</SelectItem>
                    <SelectItem value="active">Ativa</SelectItem>
                    <SelectItem value="completed">Concluída</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                disabled={saving}
              >
                {saving ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Salvar Alterações
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Disciplinas</CardTitle>
                <CardDescription>
                  {grade?.subjects?.length || 0} disciplinas adicionadas
                </CardDescription>
              </div>
              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                    <Plus className="h-4 w-4 mr-2" />
                    Adicionar
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Adicionar Disciplina</DialogTitle>
                    <DialogDescription>
                      Selecione uma disciplina para adicionar à grade
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-2 mt-4">
                    {availableSubjects.length === 0 ? (
                      <p className="text-center text-gray-500 py-8">
                        Todas as disciplinas já foram adicionadas
                      </p>
                    ) : (
                      availableSubjects.map((subject) => (
                        <div
                          key={subject.id}
                          className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                        >
                          <div className="flex-1">
                            <p className="font-medium">{subject.name}</p>
                            <p className="text-sm text-gray-600">
                              {subject.code} • {subject.category} • {subject.credits} créditos
                            </p>
                          </div>
                          <Button
                            size="sm"
                            onClick={() => handleAddSubject(subject.id)}
                            disabled={addingSubject}
                          >
                            {addingSubject ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              'Adicionar'
                            )}
                          </Button>
                        </div>
                      ))
                    )}
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </CardHeader>
          <CardContent>
            {!grade?.subjects || grade.subjects.length === 0 ? (
              <div className="text-center py-8">
                <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Nenhuma disciplina adicionada</p>
              </div>
            ) : (
              <div className="space-y-2">
                {grade.subjects.map((subject) => (
                  <div
                    key={subject.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="font-medium">{subject.name}</p>
                      <p className="text-sm text-gray-600">
                        {subject.code} • {subject.category} • {subject.credits} créditos
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="outline">Nível {subject.difficulty_level}</Badge>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleRemoveSubject(subject.id)}
                      >
                        <X className="h-4 w-4 text-red-600" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
