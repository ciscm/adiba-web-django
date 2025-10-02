from django.db import models
import uuid
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
preference_c = [
        ('whatsapp_appel', '  Whatsapp'),
        ('telephone_appel', ' Phone'),
        ('email', ' Email'),
    ]

class Footer(models.Model):
    insta = models.CharField(max_length=100,null=True,blank=True)
    tiktok = models.CharField(max_length=100,null=True,blank=True)
    facebook = models.CharField(max_length=100,null=True,blank=True)
    whatsapp = models.CharField(max_length=100,null=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and Footer.objects.exists():
            # Si une instance existe déjà, empêcher la création de nouvelles
            return
        super().save(*args, **kwargs)

    def __str__(self):
        return "Liens Reseaux Sociaux"

class Message(models.Model):
    nom_complet = models.CharField(max_length=200)
    email = models.EmailField()
    numero_telephone = models.CharField(max_length=15)
    preference_contact = models.CharField(max_length=50, choices=preference_c)
    etat =  models.CharField(max_length=50, choices=[
        ('tr', 'Traité'),
        ('nt', 'Non Traité'),
    ],default='nt')
    sujet = models.CharField(max_length=50, choices=[
        ('sc', 'Suivi Commande'),
        ('ap', 'A propos d un produit'),
        ('as', 'A propos Adiba Interieur'),
        ('au', 'Autre'),
    ])
    message = models.TextField()
    country = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'message de {self.nom_complet}'


class Temoignage(models.Model):
    texte = models.CharField(max_length=100)
    texte_english = models.CharField(max_length=100)
    nom_complet = models.CharField(max_length=50,primary_key=True, unique=True)
    date = models.DateField(auto_now_add=True)
    archive = models.BooleanField(default=False)
    ordre = models.PositiveIntegerField()
    def __str__(self):
        return self.nom_complet

class Faq(models.Model):
    question = models.CharField(max_length=100,primary_key=True, unique=True)
    reponse = models.TextField()
    question_english =  models.CharField(max_length=100, unique=True)
    reponse_english = models.TextField()
    date = models.DateField(auto_now_add=True)
    archive = models.BooleanField(default=False)
    ordre = models.PositiveIntegerField()
    def __str__(self):
        return self.question
