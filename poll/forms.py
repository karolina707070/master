from django import forms
from .models import PartnerContact, PartnerType, Organization


class PartnerForm(forms.ModelForm):
    organization_name = forms.CharField(
        label='Наименование организации',
        widget=forms.TextInput(attrs={
            'class': 'form-field-input',
            'placeholder': 'Введите наименование организации'
        })
    )

    class Meta:
        model = PartnerContact
        fields = ['partner_type', 'fio', 'phone', 'email', 'address', 'rating']
        widgets = {
            'partner_type': forms.Select(attrs={
                'class': 'form-field-select'
            }),
            'fio': forms.TextInput(attrs={
                'class': 'form-field-input',
                'placeholder': 'Введите ФИО директора'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-field-input',
                'placeholder': '+7 (XXX) XXX-XX-XX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-field-input',
                'placeholder': 'example@mail.ru'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-field-input',
                'placeholder': 'Введите адрес'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-field-input',
                'min': '0',
                'max': '10'
            })
        }
        labels = {
            'partner_type': 'Тип партнера',
            'fio': 'ФИО директора',
            'phone': 'Телефон',
            'email': 'Email',
            'address': 'Адрес',
            'rating': 'Рейтинг'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['partner_type'].queryset = PartnerType.objects.all()
        self.fields['partner_type'].empty_label = "Выберите тип партнера"


        if self.instance and self.instance.pk and self.instance.organization:
            self.fields['organization_name'].initial = self.instance.organization.name

    def save(self, commit=True):
        organization_name = self.cleaned_data['organization_name']

        # Всегда создаем новую организацию
        organization = Organization(name=organization_name)
        organization.save()

        self.instance.organization = organization

        return super().save(commit)

    def clean_organization_name(self):
        organization_name = self.cleaned_data['organization_name']
        if not organization_name.strip():
            raise forms.ValidationError("Наименование организации не может быть пустым")
        return organization_name

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if rating < 0:
            raise forms.ValidationError("Рейтинг не может быть отрицательным")
        return rating