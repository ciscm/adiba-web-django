from django.db import models
from extra.models import preference_c
import uuid
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

import os
type_client_ou_fournisseur = [
    ('professionnel', ' Professionnel'),
    ('particulier', ' Particulier'),

]
class Promotion(models.Model):
    titre = models.CharField(max_length=50,unique=True)
    titre_english =models.CharField(max_length=50)
    description = models.CharField(max_length=200,default="",null=False)
    description_english = models.CharField(max_length=200,default="",null=False)
    image = models.ImageField(upload_to='images/promotion/', blank=True)
    date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=False)
    def __str__(self):
        return self.titre

class Categorie(models.Model):
    nom = models.CharField(max_length=100,unique=True)
    nom_english = models.CharField(max_length=100,unique=True)
    image = models.ImageField(upload_to='images/categorie/', blank=True)
    nb_sous_categorie = models.IntegerField(default=0,editable=False)
    nb_produits = models.IntegerField(default=0,editable=False)
    date = models.DateField(auto_now_add=True)
    archive = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    description_english = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nom

class SousCategorie(models.Model):
    nom = models.CharField(max_length=100,unique=True)
    nom_english = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='images/sous categorie/', blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL,null=True)
    nb_produits = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    archive = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    description_english = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return self.nom

class Fournisseur(models.Model):
    nom_complet = models.CharField(max_length=50)
    preference_contact = models.CharField(max_length=50,choices=preference_c)
    numero_telephone = models.CharField(max_length=20)
    adresse_postale = models.CharField(max_length=100,default="Maroc")
    type_fournisseur = models.CharField(max_length=15,choices=type_client_ou_fournisseur)
    nb_produits = models.IntegerField(default=0)
    date = models.DateField(auto_now=True)
    def __str__(self):
        return self.nom_complet

class Produit(models.Model):
    reference = models.CharField(max_length=8, primary_key=True, unique=True, editable=False)
    nom_produit = models.CharField(max_length=100,unique=True)
    nom_produit_english = models.CharField(max_length=100)
    motif = models.CharField(max_length=100)
    dimension = models.CharField(max_length=100, null=True, blank=True)
    materiaux = models.CharField(max_length=100)
    materiaux_english = models.CharField(max_length=100)
    description = models.TextField(max_length=100,null=True)
    description_english = models.TextField(max_length=100, null=True)
    couleur = models.CharField(max_length=100)
    couleur_english = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/produit/', blank=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL ,null=True)  # Ajoute le modèle Fournisseur
    en_stock = models.IntegerField(default=0)
    date = models.DateField(auto_now=True)
    archive = models.BooleanField(default=False)


    def __str__(self):
        return self.nom_produit

    def save(self, *args, **kwargs):
        if not self.reference:
            while True:
                ref = uuid.uuid4().hex[:8].upper()
                if not Produit.objects.filter(reference=ref).exists():
                    self.reference = ref
                    break
        super().save(*args, **kwargs)
class ProduitAvecSousCategorie(models.Model):
    produit = models.ForeignKey(Produit,on_delete=models.CASCADE)
    sous_categorie = models.ForeignKey(SousCategorie, on_delete=models.SET_NULL,null=True)
    class Meta:
        verbose_name = "Produit avec Sous-catégorie"
        verbose_name_plural = "Produits avec Sous-catégorie"

    def __str__(self):
        return self.produit.nom_produit

class ProduitAvecPromotion(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE,related_name='produit_prt')
    promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL,null=True)
    class Meta:
        verbose_name = "Produit en Promotion"
        verbose_name_plural = "Produits en Promotion"

    def __str__(self):
        return self.produit.nom_produit

class ProduitComplementaire(models.Model):
    produit = models.ForeignKey(Produit, related_name='complementaires', on_delete=models.CASCADE)
    produit_complementaire = models.ForeignKey(Produit, related_name='complementaire_de', on_delete=models.CASCADE,blank=True,null=True  )

    def __str__(self):
        return self.produit_complementaire.__str__()

    def clean(self):
        # Vérifier si le produit_complementaire est lié à une sous-catégorie
        has_sous_categorie = ProduitAvecSousCategorie.objects.filter(
            produit=self.produit_complementaire
        ).exists()

        # Vérifier si le produit_complementaire est lié à une promotion
        has_promotion = ProduitAvecPromotion.objects.filter(
            produit=self.produit_complementaire
        ).exists()

        # Si ni sous-catégorie ni promotion → erreur
        if not (has_sous_categorie or has_promotion):
            raise ValidationError(
                {
                    "produit_complementaire": "Le produit complémentaire doit appartenir à une sous-catégorie ou avoir une promotion."}
            )

    def save(self, *args, **kwargs):
        # Appelle clean() avant d’enregistrer
        self.clean()
        super().save(*args, **kwargs)

class ProduitSimilaire(models.Model):
    produit = models.ForeignKey(Produit, related_name='similaires', on_delete=models.CASCADE)
    produit_similaire = models.ForeignKey(Produit, related_name='similaires_de', on_delete=models.CASCADE,blank=True,null=True )

    def __str__(self):
        return self.produit_similaire.__str__()

    def clean(self):
        # Vérifier si le produit_complementaire est lié à une sous-catégorie
        has_sous_categorie = ProduitAvecSousCategorie.objects.filter(
            produit=self.produit_similaire
        ).exists()

        # Vérifier si le produit_complementaire est lié à une promotion
        has_promotion = ProduitAvecPromotion.objects.filter(
            produit=self.produit_similaire
        ).exists()

        # Si ni sous-catégorie ni promotion → erreur
        if not (has_sous_categorie or has_promotion):
            raise ValidationError(
                {
                    "produit_complementaire": "Le produit similaire doit appartenir à une sous-catégorie ou avoir une promotion."}
            )

    def save(self, *args, **kwargs):
        # Appelle clean() avant d’enregistrer
        self.clean()
        super().save(*args, **kwargs)

class ImageProduit(models.Model):
    image = models.ImageField(upload_to='images/produits/images-supplementaires/')
    description = models.CharField(max_length=255, blank=True, null=True)
    produit = models.ForeignKey(Produit, related_name='images', on_delete=models.CASCADE)
    def __str__(self):
        return f"Image  {self.produit.nom_produit}"



class PrixEnDevise(models.Model):
    produit = models.OneToOneField(Produit, on_delete=models.CASCADE)
    prix_dhs = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                       validators=[MinValueValidator(0.01)])
    prix_euro = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                        validators=[MinValueValidator(0.01)])
    prix_dollar = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                          validators=[MinValueValidator(0.01)])
    prix_pound = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                         validators=[MinValueValidator(0.01)])
    prix_dollar_canadien = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                                   validators=[MinValueValidator(0.01)])

    def __str__(self):
            return self.produit.__str__()

    def save(self, *args, **kwargs):
        """
        Mettre à jour les devises automatiquement lors de la sauvegarde.
        """
        taux_change = TauxChange.objects.get()

        # Calculer les prix en devises
        self.prix_euro = Decimal(self.prix_dhs) * Decimal(taux_change.euro)
        self.prix_dollar = Decimal(self.prix_dhs) * Decimal(taux_change.dollar)
        self.prix_pound = Decimal(self.prix_dhs) * Decimal(taux_change.pound)
        self.prix_dollar_canadien = Decimal(self.prix_dhs) * Decimal(taux_change.dollar_canadien)


        # Appeler la méthode parent pour sauvegarder
        super().save(*args, **kwargs)

class PrixEnDevisePromotionnel(models.Model):
    produit = models.OneToOneField(Produit, on_delete=models.CASCADE)
    prix_dhs = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                       validators=[MinValueValidator(0.00)])
    prix_euro = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                        validators=[MinValueValidator(0.00)])
    prix_dollar = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                          validators=[MinValueValidator(0.00)])
    prix_pound = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                         validators=[MinValueValidator(0.00)])
    prix_dollar_canadien = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,
                                                   validators=[MinValueValidator(0.00)])

    def __str__(self):
            return self.produit.__str__()

    def save(self, *args, **kwargs):
        """
        Mettre à jour les devises automatiquement lors de la sauvegarde.
        """
        taux_change = TauxChange.objects.get()

        # Calculer les prix en devises
        self.prix_euro = self.prix_dhs * Decimal(taux_change.euro)
        self.prix_dollar = self.prix_dhs * Decimal(taux_change.dollar)
        self.prix_pound = self.prix_dhs * Decimal(taux_change.pound)
        self.prix_dollar_canadien = self.prix_dhs * Decimal(taux_change.dollar_canadien)


        # Appeler la méthode parent pour sauvegarder
        super().save(*args, **kwargs)




class TauxChange(models.Model):
    euro = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    dollar = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pound = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    dollar_canadien = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Vérifie qu'une seule instance existe
        if not self.pk and TauxChange.objects.exists():
            raise ValueError("Il ne peut y avoir qu'une seule instance de TauxChange.")
        super().save(*args, **kwargs)
    def __str__(self):
        return "Taux Change Devises"

    class Meta:
        verbose_name = "Taux de Change"
        verbose_name_plural = "Taux de Change"


class Panier(models.Model):
    token = models.CharField(max_length=100, unique=True)  # Identifiant unique pour le panier
    date = models.DateTimeField(auto_now_add=True)
    total_commande = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        # Si la référence n'est pas déjà définie, générez-en une
        if not self.token:
            self.token = uuid.uuid4().hex[:8]  # Générer une référence unique
        super().save(*args, **kwargs)
    def __str__(self):
        return "Panier " + self.token

class ItemSousCategoriePanier(models.Model):
    panier = models.ForeignKey(Panier, related_name='items_sous_categorie', on_delete=models.CASCADE)
    produit = models.ForeignKey(ProduitAvecSousCategorie, on_delete=models.DO_NOTHING)
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.produit.__str__()

class ItemPromotionPanier(models.Model):
    panier = models.ForeignKey(Panier, related_name='items_promotion', on_delete=models.CASCADE)
    produit = models.ForeignKey(ProduitAvecPromotion, on_delete=models.DO_NOTHING)
    quantite = models.PositiveIntegerField(default=1)

class Client(models.Model):
    email = models.EmailField(max_length=254)  # Clé unique pour l'email
    nom_complet = models.CharField(max_length=100)
    numero_telephone = models.CharField(max_length=15)
    preference_contact = models.CharField(max_length=50,choices=preference_c)
    nb_commandes = models.IntegerField(default= 0)
    type_client = models.CharField(max_length=50,choices=type_client_ou_fournisseur)
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.nom_complet


class Commande(models.Model):
    reference = models.CharField(max_length=8, primary_key=True, unique=True, editable=False)
    client = models.ForeignKey(Client,on_delete=models.DO_NOTHING, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    preference_contact = models.CharField(max_length=17,choices=preference_c,default='email')
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En Attente'),
        ('validee', 'Validée'),
        ('rejettee', 'Rejetée'),
    ],default='en_attente')
    etat_paiement = models.CharField(max_length=25, choices=[
        ('pa', 'Payé'),
        ('im', 'Impayé'),
        ('at', 'En Attente de Confirmation'),
    ],default='im')
    type_paiement = models.CharField(max_length=25, choices=[
        ('autre', 'Autres'),
        ('virement', 'Par Virement Bancaire'),
        ('espece', 'Especes'),
    ],default='espece')
    total_commande = models.DecimalField(max_digits=10, decimal_places=2)
    nb_produits = models.IntegerField(default=0)
    def __str__(self):
        return self.reference

    def save(self, *args, **kwargs):
        if not self.reference:
            while True:
                ref = uuid.uuid4().hex[:8].upper()
                if not Commande.objects.filter(reference=ref).exists():
                    self.reference = ref
                    break
        super().save(*args, **kwargs)



class ItemSousCategorieCommande(models.Model):
    commande = models.ForeignKey(Commande, related_name='items_sous_categorie', on_delete=models.CASCADE)
    produit = models.ForeignKey(ProduitAvecSousCategorie, on_delete=models.DO_NOTHING)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def save(self, *args, **kwargs):
        # aller chercher le prix en DHS depuis ton objet produit
        # calculer le total
        self.total = self.prix_unitaire * self.quantite
        super().save(*args, **kwargs)

    def __str__(self):
        return self.produit.produit.nom_produit

class ItemPromotionCommande(models.Model):
    commande = models.ForeignKey(Commande, related_name='items_promotion', on_delete=models.CASCADE)
    produit = models.ForeignKey(ProduitAvecPromotion, on_delete=models.DO_NOTHING)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def save(self, *args, **kwargs):
        self.total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)
    def __str__(self):
        return self.produit.__str__()