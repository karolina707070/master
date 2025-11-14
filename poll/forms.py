from django import forms
from .models import PartnerContact, PartnerType, Organization


class PartnerForm(forms.ModelForm):

    # основная форма для работы с данными партнеров, объединяет данные из нескольких моделей

    # Это поле будет хранить название организации, но обрабатываться отдельно
    organization_name = forms.CharField(
        label='Наименование организации',  # Русская метка поля
        widget=forms.TextInput(attrs={  # Виджет
            'class': 'form-field-input',
            'placeholder': 'Введите наименование организации'  # Подсказка внутри поля
        })
    )

    class Meta:

        model = PartnerContact  # Основная модель
        fields = ['partner_type', 'fio', 'phone', 'email', 'address', 'rating']
        # Указаны все поля из модели PartnerContact, которые будут отображаться в форме.

        widgets = {

            'partner_type': forms.Select(attrs={
                'class': 'form-field-select'  # Выпадающий список
            }),
            # Поле "Тип партнера" реализовано как выпадающий список

            'fio': forms.TextInput(attrs={
                'class': 'form-field-input',
                'placeholder': 'Введите ФИО директора'
            }),
            # Поле ФИО имеет подсказку, помогающую пользователю понять, какие данные нужно вводить

            'phone': forms.TextInput(attrs={
                'class': 'form-field-input',
                'placeholder': '+7 (XXX) XXX-XX-XX'
            }),
            # Подсказка формата телефона помогает пользователю вводить данные в едином стиле

            'email': forms.EmailInput(attrs={
                'class': 'form-field-input',
                'placeholder': 'example@mail.ru'  # Пример формата email
            }),

            'address': forms.TextInput(attrs={
                'class': 'form-field-input',
                'placeholder': 'Введите адрес'  # подсказка
            }),

            'rating': forms.NumberInput(attrs={
                'class': 'form-field-input',
                'min': '0',  # минимальное значение
                'max': '10'  # максимальное значение
            })
            # Рейтинг ограничен диапазоном от 0 до 10, что предотвращает ввод некорректных значений
        }

        labels = {
            # стандартные поля меняются на русскоязычные
            'partner_type': 'Тип партнера',
            'fio': 'ФИО директора',
            'phone': 'Телефон',
            'email': 'Email',
            'address': 'Адрес',
            'rating': 'Рейтинг'
        }

    def __init__(self, *args, **kwargs):

        # Метод инициализации формы

        super().__init__(*args, **kwargs)  # вызов родительского конструктора

        # Ограничиваем queryset для поля partner_type только существующими типами
        self.fields['partner_type'].queryset = PartnerType.objects.all()
        self.fields['partner_type'].empty_label = "Выберите тип партнера"  # Текст по умолчанию
        # Поле "Тип партнера" заполняется реальными данными из базы

        # Автозаполнение поля organization_name при редактировании существующего партнера
        if self.instance and self.instance.pk and self.instance.organization:
            # Если форма открыта для редактирования и у партнера есть организация
            self.fields['organization_name'].initial = self.instance.organization.name
        # При редактировании партнера поле "Название организации" автоматически заполняется текущим значением

    def save(self, commit=True):
        """
        метод сохранения формы
        Обрабатывает дополнительное поле organization_name и связывает его с моделью
        """
        organization_name = self.cleaned_data['organization_name']  # данные из валидированной формы

        # Проверяем, редактируем ли существующего партнера
        if self.instance and self.instance.pk and self.instance.organization:
            # Обновляем существующую организацию
            organization = self.instance.organization
            organization.name = organization_name
            organization.save()
        else:
            # Создаем новую организацию для добавления
            organization = Organization(name=organization_name)
            organization.save()

        # Связь партнера с организацией
        self.instance.organization = organization

        return super().save(commit)
        # Данные сохраняются в две связанные таблицы Organization и PartnerContact

    def clean_organization_name(self):
        # валидация поля organization_name - проверка на пустое значение

        organization_name = self.cleaned_data['organization_name']  # значение после базовой очистки
        if not organization_name.strip():  # не пустая ли строка
            raise forms.ValidationError("Наименование организации не может быть пустым")
        return organization_name

    def clean_rating(self):
        # Валидация поля rating - проверка, что значение не отрицательное

        rating = self.cleaned_data['rating']  # значение после базовой очистки
        if rating < 0:  # рейтинг не отрицательный
            raise forms.ValidationError("Рейтинг не может быть отрицательным")
        return rating