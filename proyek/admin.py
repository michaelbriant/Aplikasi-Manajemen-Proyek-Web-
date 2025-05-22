from django.contrib import admin
from .models import Project, TeamMember

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'start_date', 'end_date', 'supervisor')
    search_fields = ('name', 'supervisor')
    list_filter = ('start_date', 'end_date')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'gender')
