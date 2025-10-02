from django.urls import path

from .views import *

urlpatterns = [
    path("",index,name='index'),
    path("about-us",aboutUs,name="about-us"),
    path("contact",contactUs,name="contact"),
    path("contact/succes",contactSucces,name="contactSucces"),
    path("faqs",faqs,name="faqs"),
    path("catalogue",catalogue,name="catalogue"),
    path("catalogue/selections",allSelections,name="selections"),
    path("catalogue/promotions",promotions,name='promotions'),
    path("catalogue/promotion/<str:id_promotion>",promotionById,name='promotionById'),
    path("catalogue/selection/<int:id_selection>",selectionById,name="selectionById"),
    path('catalogue/sous-selection/<int:id_sous_selection>', sousSelectionById, name="sousSelectionById"),
    path('catalogue/all-sous-selection/<int:id_selection>', allSousSelectionBySelectionId, name="allSousSelectionBySelectionId"),
    path('catalogue/produit/<str:ref_produit>', produitByRef, name="produitByRef"),
    path('catalogue/promotion/produit/<str:ref_produit>', produitPromoByRef, name="produitPromoByRef"),
    path("temoignage", temoignage, name="temoignage"),
    path("panier/add",addToPanier,name="addToPanier"),
    path("panier", panier, name="panier"),
    path("panier/checkout", checkout, name="checkout"),
    path("panier/desincremente",decrementPanier)

]