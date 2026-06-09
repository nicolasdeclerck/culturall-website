from django import forms


class ContactForm(forms.Form):
    """Formulaire de contact rendu côté serveur (équivalent du ContactForm.tsx).

    Les quatre champs sont requis (les valeurs composées uniquement d'espaces
    sont rejetées, CharField appliquant `strip=True` par défaut).
    """

    name = forms.CharField(
        label="Nom",
        max_length=150,
        error_messages={"required": "Le nom est requis."},
    )
    email = forms.EmailField(
        label="Email",
        error_messages={
            "required": "L'email est requis.",
            "invalid": "Veuillez saisir une adresse email valide.",
        },
    )
    subject = forms.CharField(
        label="Sujet",
        max_length=255,
        error_messages={"required": "Le sujet est requis."},
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"rows": 6}),
        error_messages={"required": "Le message est requis."},
    )
