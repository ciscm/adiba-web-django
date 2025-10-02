from django.contrib import admin
from .models import *
from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from extra.models import Footer
import uuid


from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

class ProduitSousCategorieInline(admin.TabularInline):
    model = ProduitAvecSousCategorie
    extra = 1  # Nombre de lignes vides pour ajouter des produits
    autocomplete_fields = ['produit']  # Permet une recherche facile des produits
    max_num = 50
class ProduitPromotionInline(admin.TabularInline):
    model = ProduitAvecPromotion
    extra = 1  # Nombre de lignes vides pour ajouter des produits
    autocomplete_fields = ['produit']  # Permet une recherche facile des produits
    raw_id_fields = ['produit']
    max_num = 20


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Français', {
            'fields': ('nom', 'description', 'image')
        }),
        ('English', {
            'fields': ('nom_english', 'description_english')
        }),
        ('Autres informations', {
            'fields': ( 'archive',),
        }),
    )

    readonly_fields = ('nb_sous_categorie', 'nb_produits', 'date')
    list_display = ('nom', 'nom_english', 'nb_sous_categorie', 'nb_produits', 'archive')
    list_filter = ('archive',)
    search_fields = ('nom', 'nom_english', 'description', 'description_english')


class PromotionAdmin(admin.ModelAdmin):
    # Décomposer l'affichage par sections dans le formulaire
    fieldsets = (
        ('Informations en français', {
            'fields': ('titre', 'description')
        }),
        ('Informations en anglais', {
            'fields': ('titre_english', 'description_english')
        }),
        ('Autres informations', {
            'fields': ('image', 'active')
        }),
    )

    # Colonnes affichées dans la liste
    list_display = ['titre', 'titre_english', 'display_image', 'active', 'date']

    # Barre de recherche
    search_fields = ['titre', 'titre_english']

    # Barre de hiérarchie sur la date
    date_hierarchy = 'date'

    # Inline pour produits liés
    inlines = [ProduitPromotionInline]

    # Affichage de l'image dans l'admin
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "Pas d'image"

    display_image.short_description = 'Aperçu'



# Inline pour les images associées à un produit
class ImageProduitInline(admin.TabularInline):
    model = ImageProduit
    extra = 1  # Nombre de formulaires vides d'ajout d'image supplémentaires
    max_num = 5  # Limite d'images par produit (optionnel)


class PrixEnDeviseInline(admin.TabularInline):
    model = PrixEnDevise
    extra = 0  # Nombre de formulaires vides d'ajout d'image supplémentaires
    max_num = 1  # Limite d'images par produit (optionnel)
    readonly_fields = ('prix_euro', 'prix_dollar', 'prix_pound', 'prix_dollar_canadien')  # Champs non modifiables


class PrixPromotionnelEnDeviseInline(admin.TabularInline):
    model = PrixEnDevisePromotionnel
    extra = 0  # Nombre de formulaires vides d'ajout d'image supplémentaires
    max_num = 1  # Limite d'images par produit (optionnel)
    readonly_fields = ('prix_euro', 'prix_dollar', 'prix_pound', 'prix_dollar_canadien')
# Inline pour les produits complémentaires
class ProduitComplementaireInline(admin.TabularInline):
    model = ProduitComplementaire
    fk_name = 'produit'
    extra = 0  # Nombre de formulaires supplémentaires
    max_num = 5  # Limite de produits complémentaires (optionnel)
    verbose_name = "Produit complémentaire"
    verbose_name_plural = "Produits complémentaires"


class ProduitSimilaireInline(admin.TabularInline):
    model = ProduitSimilaire
    fk_name = 'produit'
    extra = 0
    max_num = 3
    verbose_name = "Produit similaires"
    verbose_name_plural = "Produits similaires"
class ProduitResource(resources.ModelResource):
    fournisseur = fields.Field(
        column_name='fournisseur',
        attribute='fournisseur',
        widget=ForeignKeyWidget(Fournisseur, 'nom_complet')  # Supposons que le nom du fournisseur est utilisé pour lier
    )

    prix = fields.Field(
        column_name='prix',  # Nom de la colonne dans le fichier d'import
        attribute='prix_dhs',  # Cet attribut sera géré manuellement
    )

    class Meta:
        model = Produit
        import_id_fields = ['nom_produit']
        fields = ('nom_produit', 'motif', 'dimension', 'materiaux', 'description',
                  'couleur', 'image', 'fournisseur', 'en_stock', 'date', 'archive', 'prix')

    def before_import_row(self, row, **kwargs):
        """Avant l'importation d'une ligne, s'assurer que la référence est générée automatiquement."""
        if not Produit.objects.filter(nom_produit=row.get('nom_produit')).exists():
            row['reference'] = uuid.uuid4().hex[:8]  # Générer une référence unique

    def before_import(self, dataset, **kwargs):
        for row in dataset.dict:
            prix_dhs = row.get('prix', None)
            if prix_dhs:
                try:
                    # Assurez-vous que prix_dhs est un Decimal
                    row['prix'] = Decimal(prix_dhs)
                except (ValueError, InvalidOperation):
                    row['prix'] = Decimal(0)  # Si la conversion échoue, utilisez 0
        return dataset

    def after_save_instance(self, instance, new, **kwargs):
        prix_dhs = instance.prix_dhs
        if prix_dhs:
            try:
                prix_instance = PrixEnDevise.objects.get(produit=instance)
                prix_instance.prix_dhs = prix_dhs
                prix_instance.save()
            except PrixEnDevise.DoesNotExist:
                prixdevice = PrixEnDevise(produit=instance, prix_dhs=prix_dhs)
                print("prix : ",type(prixdevice.prix_dhs))
                prixdevice.save()


class ProduitAdmin(ImportExportModelAdmin):
    resource_class = ProduitResource
    list_display = ('reference', 'display_image','nom_produit','description', 'en_stock', 'archive','date')
    list_filter = ( 'en_stock', 'archive')
    search_fields = ('nom_produit', 'reference')
    inlines = [ImageProduitInline, PrixEnDeviseInline,PrixPromotionnelEnDeviseInline, ProduitComplementaireInline, ProduitSimilaireInline]  # Ajoute les inlines d'images et de produits complémentaires
    fieldsets = (
        ("Informations en français", {
            'fields': (
                'nom_produit',
                'materiaux',
                'description',
                'couleur',
            )
        }),
        ("Informations en anglais", {
            'fields': (
                'nom_produit_english',
                'materiaux_english',
                'description_english',
                'couleur_english',
            )
        }),
        ("Autres informations", {
            'fields': (
                'motif',
                'dimension',
                'image',
                'fournisseur',
                'en_stock',
                'archive',
            )
        }),
    )
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "Pas d'image"

    display_image.short_description = 'Aperçu'
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['nom_complet','adresse_postale','numero_telephone','preference_contact','type_fournisseur','nb_produits','date']
    search_fields = ('nom_complet',)
    list_filter = ['preference_contact','type_fournisseur','nb_produits']
    date_hierarchy = 'date'
@admin.register(TauxChange)
class TauxChangeAdmin(admin.ModelAdmin):
    list_display = ('euro', 'dollar', 'pound', 'dollar_canadien')

    # Personnaliser l'affichage des champs pour les rendre visibles comme labels

    def has_add_permission(self, request):
        # Interdire l'ajout si une instance existe déjà
        return not TauxChange.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Interdire la suppression
        return False
@admin.register(SousCategorie)
class SousCategorieAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Français', {
            'fields': ('nom', 'description', 'image')
        }),
        ('English', {
            'fields': ('nom_english', 'description_english')
        }),
        ('Autres informations', {
            'fields': ( 'categorie','archive',),
        }),
    )

    readonly_fields = ( 'nb_produits', 'date')
    list_display = ('nom', 'nom_english','categorie', 'nb_produits', 'archive')
    list_filter = ('archive','categorie')
    search_fields = ('nom', 'nom_english', 'description', 'description_english')
    inlines = [ProduitSousCategorieInline]



admin.site.register(Panier,PanierAdmin)

admin.site.register(Fournisseur, FournisseurAdmin)

admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Produit, ProduitAdmin)

admin.site.site_header = _('Administration Adiba Interieur')
admin.site.site_title = _('Administration Adiba Interieur')
admin.site.site_index = _('Bienvenue chez Adiba Interieur')