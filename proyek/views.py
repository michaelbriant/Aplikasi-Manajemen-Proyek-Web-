from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Project, TeamMember
from .forms import ProjectForm, TeamMemberForm
from django.template.loader import render_to_string

# ------------------- HOMEPAGE -------------------
def homepage(request):
    semua_proyek = Project.objects.all()
    return render(request, 'proyek/homepage.html', {'semua_proyek': semua_proyek})

# ------------------- TAMBAH PROYEK -------------------
def tambah_proyek(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            proyek = form.save(commit=False)
            proyek.save()

            anggota_ids = request.POST.get('members', '')
            if anggota_ids:
                try:
                    id_list = [int(x) for x in anggota_ids.split(',') if x.strip().isdigit()]
                    proyek.members.set(id_list)
                except ValueError:
                    pass  # amanin kalau ada input aneh

            return redirect('homepage')
    else:
        form = ProjectForm()

    anggota_list = TeamMember.objects.all()
    return render(request, 'proyek/form_proyek.html', {
        'form': form,
        'anggota_list': anggota_list
    })

# ------------------- EDIT PROYEK -------------------
def edit_proyek(request, pk):
    proyek = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=proyek)
        if form.is_valid():
            proyek = form.save(commit=False)
            proyek.save()

            anggota_ids = request.POST.get('members', '')
            if anggota_ids:
                id_list = [int(id.strip()) for id in anggota_ids.split(',') if id.strip().isdigit()]
                proyek.members.set(id_list)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                updated_html = render_to_string('proyek/profil_proyek_part.html', {'project': proyek})
                return JsonResponse({'success': True, 'updatedHtml': updated_html})

            return redirect('homepage')
    else:
        form = ProjectForm(instance=proyek)

    anggota_list = TeamMember.objects.all()
    return render(request, 'proyek/edit_proyek.html', {
        'form': form,
        'anggota_list': anggota_list,
        'proyek': proyek
    })

# ------------------- ANGGOTA -------------------
def tambah_anggota(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    else:
        form = TeamMemberForm()
    return render(request, 'proyek/profil_anggota.html', {'form': form})

def list_anggota(request):
    query = request.GET.get('q')
    if query:
        anggota_list = TeamMember.objects.filter(name__icontains=query).order_by('name')
    else:
        anggota_list = TeamMember.objects.all().order_by('name')
    return render(request, 'proyek/profile_team.html', {'anggota_list': anggota_list})

def edit_anggota(request, pk):
    anggota = get_object_or_404(TeamMember, pk=pk)
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=anggota)
        if form.is_valid():
            form.save()
            return redirect('list_anggota')
    else:
        form = TeamMemberForm(instance=anggota)
    return render(request, 'proyek/profil_anggota.html', {'form': form})

def hapus_anggota(request, pk):
    anggota = get_object_or_404(TeamMember, pk=pk)
    anggota.delete()
    return redirect('list_anggota')

def detail_anggota(request, pk):
    anggota = get_object_or_404(TeamMember, pk=pk)
    return render(request, 'proyek/detail_anggota.html', {'anggota': anggota})

# ------------------- HAPUS PROYEK -------------------
def hapus_proyek(request, pk):
    proyek = get_object_or_404(Project, pk=pk)
    proyek.delete()
    return redirect('homepage')
