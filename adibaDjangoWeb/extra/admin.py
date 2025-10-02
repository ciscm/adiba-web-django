from django.contrib import admin
from django.utils.html import format_html

from .models import Faq, Temoignage,Message,Footer

@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ('insta', 'tiktok', 'facebook', 'whatsapp')


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ['question', 'reponse', 'archive', 'ordre', 'date']
    search_fields = ['question', 'question_english']
    date_hierarchy = 'date'

    fieldsets = (
        ('Français', {
            'fields': ('question', 'reponse')
        }),
        ('English', {
            'fields': ('question_english', 'reponse_english')
        }),
        ('Autres informations', {
            'fields': ('archive', 'ordre')
        }),
    )


@admin.register(Temoignage)
class TemoignageAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'texte', 'texte_english', 'archive', 'ordre', 'date']
    search_fields = ['nom_complet']
    date_hierarchy = 'date'

    fieldsets = (
        ('informations', {
            'fields': ('nom_complet', 'archive', 'ordre')
        }),
        ('Français', {
            'fields': ('texte',)
        }),
        ('English', {
            'fields': ('texte_english',)
        }),

    )

class MessageAdmin(admin.ModelAdmin) :
    list_display = ['nom_complet', 'email', 'preference_contact','sujet','etat', 'date','message']
    search_fields = ['nom_complet']
    list_filter = ['sujet','etat']
    date_hierarchy = 'date'
    readonly_fields  = ('nom_complet', 'email', 'preference_contact','sujet', 'date','message')
    def has_add_permission(self, request):
        return False


    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Message,MessageAdmin)
