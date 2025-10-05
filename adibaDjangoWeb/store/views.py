from django.shortcuts import render,redirect
from django import forms
import json
from django.conf import settings
import os
from extra.models import *
from .models import *
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

def getFooter() :
    foot =   {
            'insta': "",
            'tiktok': "",
            'facebook': "",
            'whatsapp': ""
        }
    if Footer.objects.filter().exists():
        footer = Footer.objects.filter().first()
        foot =  {
        'insta' : footer.insta,
            'tiktok' : footer.tiktok,
            'facebook' : footer.facebook,
            'whatsapp' : footer.whatsapp
        }
    return foot

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = [
            'nom_complet',
            'email',
            'numero_telephone',
            'preference_contact',
            'sujet',
            'message',
            'country',
        ]

def check_session_panier(request) :
    token = request.GET.get("token")
    panier = Panier.objects.filter(token=token).first()
    print(panier)
    if not panier:
        p = Panier()
        p.save()
        token = p.token
    return token
def index(request):
    lang = request.GET.get("lang", "fr")  # français par défaut
    token = check_session_panier(request)
    nb_produit_panier = get_panier_count(token)
    devise = request.GET.get("devise", "dhs").lower()
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    footer = getFooter()
    categories_qs = Categorie.objects.filter(archive=False)

    # Construire la liste avec le nom selon la langue
    categories = []
    for cat in categories_qs:
        if lang == "en":
            name = cat.nom_english or cat.nom
        else:
            name = cat.nom
        categories.append({
            "id" : cat.id,
            "name": name,
            "image": cat.image.url if cat.image else None
        })
    context = {
        'footer': footer,
        "categories": categories,
        "lang": lang,
        "nb_produit_panier":nb_produit_panier,
        "token": token,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,'index.html',context)

def aboutUs(request):
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    nb_produit_panier = get_panier_count(token)
    devise = request.GET.get("devise", "dhs").lower()
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    footer = getFooter()
    context = {
        'footer': footer,
        "lang": lang,
        "devise" : devise,
        "nb_produit_panier": nb_produit_panier,
        "token" : token,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,'aboutus.html',context)

@csrf_exempt
def contactUs(request):
    lang = request.GET.get("lang", "fr")  # français par défaut
    token = check_session_panier(request)
    nb_produit_panier = get_panier_count(token)
    devise = request.GET.get("devise", "dhs").lower()
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)

    footer = getFooter()
    context = {
        'footer': footer,
        "lang": lang,
        "devise": devise,
        "nb_produit_panier" : nb_produit_panier,
        "token": token,
        "t": all_translations.get(lang, all_translations["fr"]),
        "form" :"",
    }
    if request.method == "POST":
        data = request.POST.copy()

        # Si user a choisi "other", on concatène avec la valeur du champ texte
        if data.get("country") == "other":
            data["country"] = f"Other: {data.get('other-country')}"

        form = MessageForm(data)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre message a été envoyé avec succès ✅")
            return redirect(f"contact/succes?lang={lang}")
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = MessageForm()
        context["form"] = form
        return render(request, "contact.html", context)
    return render(request,'contact.html',context)

def faqs(request):
    lang = request.GET.get("lang", "fr")
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    token = check_session_panier(request)
    nb_produit_panier = get_panier_count(token)
    devise = request.GET.get("devise", "dhs").lower()
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    faqs_object = Faq.objects.filter(archive=False).order_by('ordre')
    footer = getFooter()
    if lang == 'en':
        faqs = [ {"question": faq.question_english,
             "answer": faq.reponse_english }for faq in faqs_object
        ]
    else:
        faqs = [{"question": faq.question,
                 "answer": faq.reponse} for faq in faqs_object
                ]
    context = {
        'footer': footer,
        "faqs":faqs,
        "nb_produit_panier" : nb_produit_panier,
        "lang": lang,
        "devise": devise,
        "token": token,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,'faqs.html',context)
def temoignage(request):
    lang = request.GET.get("lang", "fr")
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    token = check_session_panier(request)
    nb_produit_panier = get_panier_count(token)
    devise = request.GET.get("devise", "dhs").lower()
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    footer = getFooter()
    temoignages_object = Temoignage.objects.filter(archive=False).order_by('ordre')
    if lang == 'en':
        temoignages = [
            {"name": temoignage.nom_complet, "comment": temoignage.texte_english} for temoignage in temoignages_object
        ]
    else:
        temoignages = [
            {"name": temoignage.nom_complet, "comment": temoignage.texte} for temoignage in temoignages_object
        ]
    context = {
        "lang": lang,
        'footer': footer,
        "nb_produit_panier" : nb_produit_panier,
        "temoignages": temoignages,
        "devise": devise,
        "token": token,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,'temoignage.html',context)

def contactSucces(request):
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    nb_produit_panier = get_panier_count(token)
    devise = request.GET.get("devise", "dhs").lower()
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    footer = getFooter()
    context = {
        'footer': footer,
        "lang": lang,
        "nb_produit_panier" : nb_produit_panier,
        "devise": devise,
        "token": token,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,"post_message_succes.html",context)
def get_panier_count(token):
    panier = Panier.objects.filter(token=token).first()

    if not panier:
        return 0

    # On additionne toutes les quantités, peu importe le type (sc ou pr)
    count = 0

    for item in ItemSousCategoriePanier.objects.filter(panier=panier):
        count += 1

    for item in ItemPromotionPanier.objects.filter(panier=panier):
        count += 1

    return count
def allSelections(request):
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    devise = request.GET.get("devise", "dhs").lower()
    nb_produit_panier = get_panier_count(token)
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    categories_qs = Categorie.objects.filter(archive=False)
    footer = getFooter()
    # Construire la liste avec le nom selon la langue
    categories = []
    for cat in categories_qs:
        if lang == "en":
            name = cat.nom_english or cat.nom
        else:
            name = cat.nom
        categories.append({
            "name": name,
            "image": cat.image.url if cat.image else None
        })
    context = {
        'footer': footer,
        "categories" : categories*5,
        "lang": lang,
        "devise": devise,
        "nb_produit_panier" : nb_produit_panier,
        "token": token,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,"all_categories.html",context)

def catalogue(request):
    lang = request.GET.get("lang", "fr")
    page = int(request.GET.get("page", "1"))
    token = check_session_panier(request)
    nb_produit_panier = get_panier_count(token)
    devise = request.GET.get("devise", "dhs").lower()
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    categories_qs = Categorie.objects.filter(archive=False)
    footer = getFooter()
    if page < 1 :
        page = 1
    debut = (page - 1) * 3
    fin = debut + 3
    total_categories = len(categories_qs)
    total_pages = (total_categories + 2) // 3

    if page < 1 or page > total_pages:
        page = total_pages

    categories_paginated = categories_qs[debut:fin]

    categories = []
    for cat in categories_paginated:
        if lang == "en":
            name = cat.nom_english or cat.nom
            desc = cat.description_english
        else:
            name = cat.nom
            desc = cat.description
        categories.append({
            "id" : cat.id,
            "name": name,
            "image": cat.image.url if cat.image else None,
            "desc" : desc,
            "sous_categories" : [ {
                    "id": sous_categorie.id,
                    "name": sous_categorie.nom if lang=='fr' else sous_categorie.nom_english,
                    "image": sous_categorie.image.url if sous_categorie.image else None,
                }for sous_categorie in SousCategorie.objects.filter(categorie=cat,archive=False)[0:4] ]
        })
    context = {
        "categories" : categories,
        "lang": lang,
        "page" : page,
        "devise": devise,
        'footer': footer,
        "nb_produit_panier" :nb_produit_panier,
        "token": token,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,"catalogue.html",context)

def retourPrixEnBonneForme(prix_obj,devise,retour):
    if not prix_obj:  # ✅ sécurisation
        return None if retour != "str" else "N/A"

    if retour == "str" :
        if devise == "dhs":
            prix = f"{prix_obj.prix_dhs} DHS"
        elif devise == "euro":
            prix = f"{prix_obj.prix_euro} €"
        elif devise == "dollar":
            prix = f"{prix_obj.prix_dollar} $"
        elif devise == "pound":
            prix = f"{prix_obj.prix_pound} £"
        elif devise == "dollar-canadien":
            prix = f"{prix_obj.prix_dollar_canadien} CAD"
        else:
            prix = f"{prix_obj.prix_dhs} DHS"  # valeur par défaut
    else :
        if devise == "dhs":
            prix = prix_obj.prix_dhs
        elif devise == "euro":
            prix = prix_obj.prix_euro
        elif devise == "dollar":
            prix = prix_obj.prix_dollar
        elif devise == "pound":
            prix = prix_obj.prix_pound
        elif devise == "dollar-canadien":
            prix =prix_obj.prix_dollar_canadien
        else:
            prix = prix_obj.prix_dhs # valeur par défaut
    return prix
def get_prix(produit,type_, devise="dhs",retour="str"):
    if type_ == "normal" :
        prix_obj = PrixEnDevise.objects.filter(produit=produit).first()
    else :
        prix_obj = PrixEnDevisePromotionnel.objects.filter(produit=produit).first()

    return retourPrixEnBonneForme(prix_obj,devise,retour)
def selectionById(request,id_selection) :
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    devise = request.GET.get("devise", "dhs").lower()
    nb_produit_panier = get_panier_count(token)
    page = int(request.GET.get("page", "1"))
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    categorie = Categorie.objects.filter(archive=False,id=id_selection).first()
    footer = getFooter()
    sous_categories_qs = SousCategorie.objects.filter(archive=False,categorie=categorie)
    if page < 1:
        page = 1
    debut = (page - 1) * 3
    fin = debut + 3

    total_sous_categories = len(sous_categories_qs)
    total_pages = (total_sous_categories + 2) // 3

    if page < 1 or page > total_pages:
        page = total_pages

    sous_categories_paginated = sous_categories_qs[debut:fin]

    sous_categories = []
    if lang == "en":
        cat_name = categorie.nom_english
        cat_desc = categorie.description_english

    else:
        cat_name = categorie.nom
        cat_desc = categorie.description

    for sous_cat in sous_categories_paginated:
        if lang == "en":

            name = sous_cat.nom_english
            desc = sous_cat.description_english
        else:

            name = sous_cat.nom
            desc = sous_cat.description
        sous_categories.append({
            "id": sous_cat.id,
            "name": name,
            "image": sous_cat.image.url if sous_cat.image else None,
            "desc": desc,
            "produits" : [
                    {
                        "reference": produit_in_sous_categorie.produit.reference,
                        "name": produit_in_sous_categorie.produit.nom_produit if lang == "fr" else produit_in_sous_categorie.produit.nom_produit_english,
                        "image": produit_in_sous_categorie.produit.image.url if produit_in_sous_categorie.produit.image else None,
                        'prix' :  get_prix(produit_in_sous_categorie.produit, "normal",devise),
                    }
                    for produit_in_sous_categorie in ProduitAvecSousCategorie.objects.filter(sous_categorie=sous_cat )[:4] # Récupérer les 4 premiers produits
                ],

        })


    context = {
        "categorie" :{
            "id" : categorie.id,
            "name" : cat_name,
            "image" : categorie.image.url if categorie.image else None,
            "desc" : cat_desc
        },
        "sous_categories": sous_categories,
        "lang": lang,
        "devise": devise,
        "token": token,
        "page": page,
        'footer': footer,
        "nb_produit_panier" : nb_produit_panier,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,'categorie.html',context)

def sousSelectionById(request,id_sous_selection) :
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    devise = request.GET.get("devise", "dhs").lower()
    nb_produit_panier = get_panier_count(token)
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    footer = getFooter()
    sous_categorie = SousCategorie.objects.filter(id=id_sous_selection).first()

    if lang == "en":
        cat_name = sous_categorie.nom_english
        cat_desc = sous_categorie.description_english
        cat_sous_cat_name = sous_categorie.categorie.nom_english

    else:
        cat_name = sous_categorie.nom
        cat_desc = sous_categorie.description
        cat_sous_cat_name = sous_categorie.categorie.nom
    produits = []
    for produit_in_sous_categorie in ProduitAvecSousCategorie.objects.filter(sous_categorie=sous_categorie) :
        produits.append(
            {
                "reference": produit_in_sous_categorie.produit.reference,
                "name": produit_in_sous_categorie.produit.nom_produit if lang == "fr" else produit_in_sous_categorie.produit.nom_produit_english,
                "image": produit_in_sous_categorie.produit.image.url if produit_in_sous_categorie.produit.image else None,
                'prix': get_prix(produit_in_sous_categorie.produit,"normal", devise)
            })


    context = {
        "sous_categorie" :{
            "id" : sous_categorie.id,
            "name" : cat_name,
            "image" : sous_categorie.image.url if sous_categorie.image else None,
            "desc" : cat_desc,
            "categorie" : {
                "name" : cat_sous_cat_name,
                "id" : sous_categorie.categorie.id
            },
            "produits" : produits
        },
        "lang": lang,
        "devise": devise,
        "token": token,
        'footer': footer,
        "nb_produit_panier" : nb_produit_panier,

        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,'sous_categorie.html',context)

def produitByRef(request,ref_produit):
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    devise = request.GET.get("devise", "dhs").lower()
    nb_produit_panier = get_panier_count(token)
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    footer = getFooter()
    produit = Produit.objects.filter(reference=ref_produit).first()
    produit_sc = ProduitAvecSousCategorie.objects.filter(produit=produit).first()

    produits_compl = ProduitComplementaire.objects.filter(produit=produit)
    produits_siml = ProduitSimilaire.objects.filter(produit=produit)
    if lang == 'fr' :
        produit_name = produit.nom_produit
        produit_desc = produit.description
        produit_couleur = produit.couleur
        produit_materiaux = produit.materiaux
    else :
        produit_name = produit.nom_produit_english
        produit_desc = produit.description_english
        produit_couleur = produit.couleur_english
        produit_materiaux = produit.materiaux_english
    context = {
        "produit": {
            "reference": produit.reference,
            "name": produit_name,
            "image": produit.image.url if produit.image else None,
            "prix" : get_prix(produit_sc.produit, "normal",devise),
            "materiaux" : produit_materiaux,
            "couleur" : produit_couleur,
            "desc" : produit_desc,
            'image_supps': [{
                "description": image_produit.description,
                "image": image_produit.image.url if image_produit.image else None,
                }for image_produit in ImageProduit.objects.filter(produit=produit)
            ],
            'sous_categorie': {
                'id': produit_sc.sous_categorie.id,
                'name': produit_sc.sous_categorie.__str__(),
            },
            'categorie': {
                'id': produit_sc.sous_categorie.categorie.id,
                'name': produit_sc.sous_categorie.categorie.__str__(),
            },
            'produits_similaires': [
                {
                    'reference': produit_sim.produit_similaire.reference,
                    'name': produit_sim.produit_similaire.nom_produit,
                    'image': produit_sim.produit_similaire.image.url if produit_sim.produit_similaire.image else None,
                    'prix' : get_prix(produit_sim.produit_similaire,"normal", devise)
                }
                for produit_sim in produits_siml],
            'produits_complementaires': [
                {
                    'reference': produit_com.produit_complementaire.reference,
                    'name': produit_com.produit_complementaire.nom_produit,
                    'image': produit_com.produit_complementaire.image.url if produit_com.produit_complementaire.image else None,
                    'prix': get_prix(produit_com.produit_complementaire,"normal" ,devise)
                }
                for produit_com in produits_compl],


        },
        "lang": lang,
        "devise": devise,
        "token": token,
        'footer': footer,
        "nb_produit_panier" : nb_produit_panier,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,'produit.html',context)


def produitPromoByRef(request, ref_produit):
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    devise = request.GET.get("devise", "dhs").lower()
    nb_produit_panier = get_panier_count(token)
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    footer = getFooter()
    produit = Produit.objects.filter(reference=ref_produit).first()
    produit_promo = ProduitAvecPromotion.objects.filter(produit=produit).first()

    produits_compl = ProduitComplementaire.objects.filter(produit=produit)
    produits_siml = ProduitSimilaire.objects.filter(produit=produit)
    if lang == 'fr':
        produit_name = produit.nom_produit
        produit_desc = produit.description
        produit_couleur = produit.couleur
        produit_materiaux = produit.materiaux
        promo_name = produit_promo.promotion.titre
    else:
        produit_name = produit.nom_produit_english
        produit_desc = produit.description_english
        produit_couleur = produit.couleur_english
        produit_materiaux = produit.materiaux_english
        promo_name = produit_promo.promotion.titre_english
    context = {
        "produit": {
            "reference": produit.reference,
            "name": produit_name,
            "image": produit.image.url if produit.image else None,
            "prix_promo": get_prix(produit_promo.produit,"promo", devise),
            "prix": get_prix(produit_promo.produit, "normal", devise),
            "materiaux": produit_materiaux,
            "couleur": produit_couleur,
            "desc": produit_desc,
            'image_supps': [{
                "description": image_produit.description,
                "image": image_produit.image.url if image_produit.image else None,
            } for image_produit in ImageProduit.objects.filter(produit=produit)
            ],
            'promotion': {
                'id': produit_promo.promotion.id,
                'name': promo_name,
            },
            'produits_similaires': [
                {
                    'reference': produit_sim.produit_similaire.reference,
                    'name': produit_sim.produit_similaire.nom_produit,
                    'image': produit_sim.produit_similaire.image.url if produit_sim.produit_similaire.image else None,
                    'prix': get_prix(produit_sim.produit_similaire, devise,"normal")
                }
                for produit_sim in produits_siml],
            'produits_complementaires': [
                {
                    'reference': produit_com.produit_complementaire.reference,
                    'name': produit_com.produit_complementaire.nom_produit,
                    'image': produit_com.produit_complementaire.image.url if produit_com.produit_complementaire.image else None,
                    'prix': get_prix(produit_com.produit_complementaire, devise,"normal")
                }
                for produit_com in produits_compl],

        },
        "lang": lang,
        "devise": devise,
        "token": token,
        'footer': footer,
        "nb_produit_panier" :nb_produit_panier,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request, 'produit_promo.html', context)


def allSousSelectionBySelectionId(request,id_selection):
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    devise = request.GET.get("devise", "dhs").lower()
    page = int(request.GET.get("page", "1"))
    nb_produit_panier = get_panier_count(token)
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    categorie = Categorie.objects.filter(archive=False, id=id_selection).first()
    footer = getFooter()
    sous_categorie = SousCategorie.objects.filter(archive=False,categorie=categorie)


    sous_categories = []
    if lang == "en":
        cat_name = categorie.nom_english
        cat_desc = categorie.description_english

    else:
        cat_name = categorie.nom
        cat_desc = categorie.description

    for sous_cat in sous_categorie:
        if lang == "en":

            name = sous_cat.nom_english
            desc = sous_cat.description_english
        else:

            name = sous_cat.nom
            desc = sous_cat.description
        sous_categories.append({
            "id": sous_cat.id,
            "name": name,
            "image": sous_cat.image.url if sous_cat.image else None,

        })

    context = {
        "categorie": {
            "id": categorie.id,
            "name": cat_name,
            "image": categorie.image.url if categorie.image else None,
            "desc": cat_desc
        },
        "sous_categories": sous_categories,
        "lang": lang,
        "devise": devise,
        "token": token,
        "page": page,
        'footer': footer,
        "nb_produit_panier" : nb_produit_panier,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,'all_sous_categories_in_categorie.html',context)

def promotions(request):
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    devise = request.GET.get("devise", "dhs").lower()
    nb_produit_panier = get_panier_count(token)
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    promotions = Promotion.objects.filter(active=True).order_by('-date')
    footer = getFooter()
    context = {
        "promotions": [{
            "id": promo.id,
            "name": promo.titre if lang == 'fr' else promo.titre_english,
            "image": promo.image.url if promo.image else None,
        } for promo in promotions],
        "lang": lang,
        "devise": devise,
        "token": token,
        'footer': footer,
        "nb_produit_panier" : nb_produit_panier,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,'promotions.html',context)

def promotionById(request,id_promotion):
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    devise = request.GET.get("devise", "dhs").lower()
    nb_produit_panier = get_panier_count(token)
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    promotion = Promotion.objects.filter(active=True,id=id_promotion).first()
    produits = ProduitAvecPromotion.objects.filter(promotion=promotion)
    footer = getFooter()
    context = {
        "promotion": {
            "name": promotion.titre if lang == 'fr' else promotion.titre_english,
            "image": promotion.image.url if promotion.image else None,
            "desc" : promotion.description if lang == 'fr' else promotion.description_english
        } ,
        "produits" :[ {
            'reference' :produit.produit.reference,
            'name' : produit.produit.nom_produit if lang == 'fr' else produit.produit.nom_produit_english,
            "image" : produit.produit.image.url if produit.produit.image else None,
            "prix" : get_prix(produit.produit,"normal",devise),
            "prix_promo" : get_prix(produit.produit,"promo",devise)

        } for produit in produits],
        "lang": lang,
        "devise": devise,
        'footer': footer,
        "nb_produit_panier" : nb_produit_panier,
        "token": token,
        "t": all_translations.get(lang, all_translations["fr"])
    }
    return render(request,'promotion.html',context)

def addToPanier(request):
    ref_produit = request.GET.get("produit")
    lang = request.GET.get("lang", "fr")
    devise = request.GET.get("devise", "dhs").lower()
    token =  request.GET.get("token")

    type_= request.GET.get("type","")
    produit = Produit.objects.filter(reference=ref_produit).first()
    panier = Panier.objects.filter(token=token).first()
    if not produit:
        messages.error(request, "❌ Produit introuvable.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
    if type_ == "sc" :
         produit_sc = ProduitAvecSousCategorie.objects.filter(produit=produit).first()
         item = ItemSousCategoriePanier.objects.filter(panier=panier, produit=produit_sc).first()
         if item:
             item.quantite += 1
             item.save()
             messages.success(request, f"✅la quantite de  {produit.nom_produit} a été incremnté.")
             return redirect(request.META.get("HTTP_REFERER", "/"))
         else:
             ItemSousCategoriePanier.objects.create(panier=panier, produit=produit_sc, quantite=1)


    elif type_ == "pr" :
        produit_pr = ProduitAvecPromotion.objects.filter(produit=produit).first()
        item = ItemPromotionPanier.objects.filter(panier=panier, produit=produit_pr).first()
        if item:
            item.quantite += 1
            item.save()
            messages.success(request, f"✅la quantite de  {produit.nom_produit} a été incremnté.")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        else:
            ItemPromotionPanier.objects.create(panier=panier, produit=produit_pr, quantite=1)

    else :
        messages.error(request, "❌ type inconnu.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    messages.success(request, f"✅ {produit.nom_produit} a été ajouté au panier.")
    return redirect(request.META.get("HTTP_REFERER", "/"))

def panier(request):
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    devise = request.GET.get("devise", "dhs").lower()
    nb_produit_panier = get_panier_count(token)
    # Traductions si besoin
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    t = all_translations.get(lang, all_translations["fr"])

    panier = Panier.objects.filter(token=token).first()
    items = []
    total = 0
    footer = getFooter()
    if panier:
        # Items sous-catégorie
        for item in ItemSousCategoriePanier.objects.filter(panier=panier):
            produit = item.produit.produit
            prix_c = get_prix(produit,"normal",devise,"int")
            prix = get_prix(produit, "normal", devise,"str")
            sous_total =0
            if prix_c :

                sous_total = prix_c* item.quantite
            total += sous_total

            items.append({
                "type": "sous_categorie",
                "reference": produit.reference,
                "name": produit.nom_produit,
                "image": produit.image.url if produit.image else None,
                "prix": prix,
                "quantite": item.quantite,
                "sous_total": sous_total,
            })

        # Items promotion
        for item in ItemPromotionPanier.objects.filter(panier=panier):
            produit = item.produit.produit
            prix_normal = get_prix(produit,"normal",devise,"int")
            prix_promo = get_prix(produit,"promo",devise,"int")
            sous_total = 0
            if prix_promo   :
                sous_total = prix_promo * item.quantite

            total += sous_total
            prix_promo = get_prix(produit, "promo", devise,"str")

            items.append({
                "type": "promotion",
                "reference": produit.reference,
                "name": produit.nom_produit if lang=='fr' else produit.nom_produit_english,
                "image": produit.image.url if produit.image else None,
                "prix_normal": prix_normal ,
                "prix_promo": prix_promo,
                "quantite": item.quantite,
                "sous_total": sous_total,
            })

    context = {
        "panier": {
            "items": items,
            "total": total,
            "devise": devise
        },
        "t": t,
        'footer': footer,
        "lang": lang,
        "nb_produit_panier" : nb_produit_panier,
        "devise" :devise,
        "token": token,
    }

    return render(request, "panier.html", context)
def checkout(request):
    lang = request.GET.get("lang", "fr")
    token = check_session_panier(request)
    devise = request.GET.get("devise", "dhs").lower()
    nb_produit_panier = get_panier_count(token)
    # Traductions
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    t = all_translations.get(lang, all_translations["fr"])
    footer = getFooter()
    # Récupération panier
    panier = Panier.objects.filter(token=token).first()
    items = []
    total = 0
    total_dhs = 0

    if panier:
        # Items sous-catégorie
        for item in ItemSousCategoriePanier.objects.filter(panier=panier):
            produit = item.produit.produit
            prix_c = get_prix(produit,"normal",devise,"int")
            prix = get_prix(produit, "normal", devise,"str")
            sous_total = prix_c * item.quantite if prix_c else 0

            if devise != "dhs" :

                prix_promo_dhs = get_prix(produit, "normal", devise, "int")
                sous_total_dhs = prix_promo_dhs *item.quantite if prix_promo_dhs else 0
                total_dhs += sous_total_dhs
            total += sous_total

            items.append({
                "type": "sous_categorie",
                "reference": produit.reference,
                "name": produit.nom_produit if lang=='fr' else produit.nom_produit_english,
                "image": produit.image.url if produit.image else None,
                "prix": prix,
                "quantite": item.quantite,
                "sous_total": sous_total,
            })


        # Items promotion
        for item in ItemPromotionPanier.objects.filter(panier=panier):
            produit = item.produit.produit
            prix_normal = get_prix(produit,"normal",devise,"int")
            prix_promo = get_prix(produit,"promo",devise,"int")
            if devise != "dhs" :

                prix_promo_dhs = get_prix(produit, "promo", devise, "int")
                sous_total_dhs = prix_promo_dhs * item.quantite if prix_promo_dhs else 0
                total_dhs += sous_total_dhs
            sous_total = prix_promo * item.quantite if prix_promo else 0
            total += sous_total
            prix_promo = get_prix(produit, "promo", devise)

            items.append({
                "type": "promotion",
                "reference": produit.reference,
                "name": produit.nom_produit if lang=='fr' else produit.nom_produit_english,
                "image": produit.image.url if produit.image else None,
                "prix_normal": prix_normal ,
                "prix_promo": prix_promo,
                "quantite": item.quantite,
                "sous_total": sous_total,
            })

    # Choix du formulaire client


    context = {
        "panier": {
            "items": items,
            "total": total,
            "total_dhs" : total_dhs,
            "devise": devise
        },
        "t": t,
        "lang": lang,
        "token": token,
        'footer': footer,
        "devise" : devise,
        "preference_c": preference_c,
        "nb_produit_panier" : nb_produit_panier,
        "type_client_ou_fournisseur": type_client_ou_fournisseur,
    }

    return render(request, "formulaire_panier.html", context)
def decrementPanier(request):
    ref_produit = request.GET.get("produit")
    lang = request.GET.get("lang", "fr")
    devise = request.GET.get("devise", "dhs").lower()
    token = request.GET.get("token")
    type_ = request.GET.get("type", "")
    produit = Produit.objects.filter(reference=ref_produit).first()
    panier = Panier.objects.filter(token=token).first()

    if not produit:
        messages.error(request, "❌ Produit introuvable.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    if type_ == "sc":
        produit_sc = ProduitAvecSousCategorie.objects.filter(produit=produit).first()
        item = ItemSousCategoriePanier.objects.filter(panier=panier, produit=produit_sc).first()
        if item:
            if item.quantite > 1:
                item.quantite -= 1
                item.save()
                messages.success(request, f"➖ La quantité de {produit.nom_produit} a été réduite.")
            else:
                item.delete()
                messages.success(request, f"🗑️ {produit.nom_produit} a été retiré du panier.")
        else:
            messages.error(request, "❌ Ce produit n'est pas dans le panier.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    elif type_ == "pr":
        produit_pr = ProduitAvecPromotion.objects.filter(produit=produit).first()
        item = ItemPromotionPanier.objects.filter(panier=panier, produit=produit_pr).first()
        if item:
            if item.quantite > 1:
                item.quantite -= 1
                item.save()
                messages.success(request, f"➖ La quantité de {produit.nom_produit} a été réduite.")
            else:
                item.delete()
                messages.success(request, f"🗑️ {produit.nom_produit} a été retiré du panier.")
        else:
            messages.error(request, "❌ Ce produit n'est pas dans le panier.")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    else:
        messages.error(request, "❌ Type inconnu.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
def search(request) :
    lang = request.GET.get("lang", "fr")
    devise = request.GET.get("devise", "dhs").lower()
    token = request.GET.get("token")
    saisie = request.GET.get("saisie")
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    t = all_translations.get(lang, all_translations["fr"])
    footer = getFooter()
    if lang == 'fr' :
        categoriess = Categorie.objects.filter(nom__icontains=saisie,archive=False)
        produit_scc = ProduitAvecSousCategorie.objects.filter(produit__nom_produit__icontains=saisie,produit__archive =False)
        produit_prr = ProduitAvecPromotion.objects.filter(produit__nom_produit__icontains=saisie)
    else:
        categoriess = Categorie.objects.filter(nom_english__icontains=saisie,archive=False)
        produit_scc = ProduitAvecSousCategorie.objects.filter(produit__nom_produit_english__icontains=saisie,produit__archive =False)
        produit_prr = ProduitAvecPromotion.objects.filter(produit__nom_produit_english__icontains=saisie)

    categories = [
        {
            "id": cat.id,
            "name" : cat.nom if lang =='fr' else cat.nom_english,
            "image" : cat.image.url if cat.image else None
        } for cat in categoriess
    ]
    produit_sc = [
        {
            "reference": p_sc.produit.reference,
            "name": p_sc.produit.nom_produit if lang == 'fr' else p_sc.produit.nom_produit_english,
            "image": p_sc.produit.image.url if p_sc.produit.image else None,
            "prix" : get_prix(p_sc.produit,"normal",devise,"str")
        } for p_sc in produit_scc
    ]
    produit_pr = [
        {
            "reference": p_pr.produit.reference,
            "name": p_pr.produit.nom_produit if lang == 'fr' else p_pr.produit.nom_produit_english,
            "image": p_pr.produit.image.url if p_pr.produit.image else None,
            "prix": get_prix(p_pr.produit, "normal", devise, "str"),
            "prix_promo": get_prix(p_pr.produit, "promo", devise, "str")
        } for p_pr in produit_prr
    ]
    nb_produit_panier = get_panier_count(token)
    context = {
        "categories": categories,
        "produit_sc" : produit_sc,
        "produit_pr" :produit_pr,
        "t": t,
        "lang": lang,
        "token": token,
        "devise": devise,
        'footer': footer,
        "saisie" : saisie,
        "nb_produit_panier": nb_produit_panier,
    }

    return render(request,"page_recherche.html",context)



import os, json, uuid
from decimal import Decimal
from django.shortcuts import render, redirect
from django.conf import settings


def valider(request):
    lang = request.GET.get("lang", "fr")
    devise = request.GET.get("devise", "dhs").lower()
    token = request.GET.get("token")

    if request.method != "POST":
        messages.error(request, "Méthode non autorisée.")
        return redirect(f"/panier/checkout?lang={lang}&devise={devise}")

    # Traductions
    file_path = os.path.join(settings.BASE_DIR, "data", "traduction.json")
    with open(file_path, "r", encoding="utf-8") as f:
        all_translations = json.load(f)
    t = all_translations.get(lang, all_translations["fr"])

    # Vérifier panier
    panier = Panier.objects.filter(token=token).first()
    if not panier:
        messages.error(request, "Aucun panier trouvé.")
        return redirect(f"/panier/checkout?lang={lang}&devise={devise}")

    # Récupération du formulaire
    nom_complet = request.POST.get("nom_complet")
    email = request.POST.get("email")
    numero_telephone = request.POST.get("numero_telephone")
    preference_contact = request.POST.get("preference_contact")
    type_paiement = request.POST.get("type_paiement")
    type_client = request.POST.get("type_client")

    if not all([nom_complet, email, numero_telephone, preference_contact, type_client]):
        messages.error(request, "Veuillez remplir tous les champs du formulaire.")
        return redirect(f"/panier/checkout?lang={lang}&devise={devise}&token={token}")

    # Client
    client, created = Client.objects.get_or_create(
        email=email,
        defaults={
            "nom_complet": nom_complet,
            "numero_telephone": numero_telephone,
            "preference_contact": preference_contact,
            "type_client": type_client,
        }
    )
    if not created:
        client.nom_complet = nom_complet
        client.numero_telephone = numero_telephone
        client.preference_contact = preference_contact
        client.type_client = type_client
        client.save()

    # Commande
    commande = Commande.objects.create(
        client=client,
        total_commande=0,
        nb_produits=0,
        preference_contact=preference_contact,
        statut="en_attente",
        etat_paiement="im",
        type_paiement=type_paiement,
    )

    total_commande = Decimal("0.00")
    nb_produits = 0
    print(panier.items_sous_categorie.all())
    # 🧾 Items sous-catégorie
    for item in panier.items_sous_categorie.all():
        produit = item.produit.produit  # Le vrai produit
        print(produit)
        prix_unitaire = Decimal(get_prix(produit, "normal", "dhs", "int"))  # 👈 utilisation get_prix
        total_item = prix_unitaire * item.quantite

        ItemSousCategorieCommande.objects.create(
            commande=commande,
            produit=item.produit,
            quantite=item.quantite,
            prix_unitaire=prix_unitaire,
            total=total_item,
        )
        total_commande += total_item
        nb_produits += item.quantite

    # 🏷️ Items promotion
    for promo_item in panier.items_promotion.all():
        produit = promo_item.produit.produit  # Le vrai produit
        prix_unitaire = Decimal(get_prix(produit, "promo", devise, "int"))  # 👈 utilisation get_prix
        total_item = prix_unitaire * promo_item.quantite

        ItemPromotionCommande.objects.create(
            commande=commande,
            produit=promo_item.produit,
            quantite=promo_item.quantite,
            prix_unitaire=prix_unitaire,
            total=total_item,
        )
        total_commande += total_item
        nb_produits += promo_item.quantite

    # Finaliser
    commande.total_commande = total_commande
    commande.nb_produits = nb_produits
    commande.save()

    # Supprimer le panier
    panier.delete()
    p = Panier()
    p.save()
    token = p.token

    # Message succès
    messages.success(request, f"Votre commande {commande.reference} a été validée avec succès !")
    whatsapp_msg = f"Bonjour, je confirme ma commande %0A"
    whatsapp_msg += f"Référence : {commande.reference}%0A"
    whatsapp_msg += f"Nom : {commande.client.nom_complet}%0A"
    whatsapp_msg += f"Total : {commande.total_commande} {devise.upper()}%0A"

    for item in commande.items_sous_categorie.all():
        whatsapp_msg += f"{item.produit.produit.nom_produit} x{item.quantite} - {item.total} {devise.upper()}%0A"
    for item in commande.items_promotion.all():
        whatsapp_msg += f"{item.produit.produit.nom_produit} x{item.quantite} - {item.total} {devise.upper()}%0A"

    # Page de confirmation
    footer = getFooter()
    context = {
        "t": t,
        "whatsapp_msg" : whatsapp_msg,
        "lang": lang,
        "devise": devise,
        "token" : token,
        "footer": footer,
        "commande": commande,
    }

    return render(request, "rec_commande.html", context)
