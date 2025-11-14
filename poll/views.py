from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from .models import PartnerContact, Sale
from .forms import PartnerForm


def calculate_discount(total_sales):
    """
     функция для расчета скидки на основе объема продаж
    пороговые значения для определения процента скидки

    - до 10,000: 0% скидки
    - 10,000-50,000: 5% скидки
    - 50,000-300,000: 10% скидки
    - свыше 300,000: 15% скидки
    """
    try:
        if total_sales >= 300000:
            return 15
        elif total_sales >= 50000:
            return 10
        elif total_sales >= 10000:
            return 5
        else:
            return 0
    except Exception as e:
        return 0
        #  При любой ошибке возвращаем 0% скидки
        #  функция не сломает приложение


def spisok(request):
    # Отображение списка всех партнеров с расчетом скидок
    try:
        #  Получаем всех партнеров из базы данных
        partners = PartnerContact.objects.all()

        partner_data = []
        #  Для каждого партнера рассчитываем общие продажи и скидку
        for partner in partners:
            try:
                # Суммируем количество продаж по организации партнера
                total_sales = Sale.objects.filter(
                    partner_name=partner.organization
                ).aggregate(total=models.Sum('quantity'))['total'] or 0
                # Используется агрегация БД для суммы

                discount = calculate_discount(total_sales)

                partner_data.append({
                    'partner': partner,
                    'total_sales': total_sales,
                    'discount': discount
                })
                # Для каждого партнера формируется набор данных:
                # информация о партнере, продажи и скидка
            except Exception as e:
                continue
                # Обработчик предотвращает падение всего списка из-за проблемы с одним партнером

        return render(request, 'spisok.html', {'partner_data': partner_data})
        # Передаем данные в шаблон для отображения

    except Exception as e:
        return render(request, 'spisok.html', {'partner_data': []})
        # При общей ошибке возвращаем пустой список


def history(request, partner_id):
    # Отображение истории продаж конкретного партнера
    try:
        # Получаем партнера по ID
        partner = get_object_or_404(PartnerContact, id=partner_id)
        # Используется функция для обработки случая "объект не найден"

        # Фильтруем продажи по организации партнера
        sales = Sale.objects.filter(
            partner_name=partner.organization
        ).select_related('product')
        # select_related загружает связанные данные о продуктах за один запрос

        context = {
            'partner': partner,
            'sales_history': sales,
        }

        return render(request, 'history.html', context)

    except Exception as e:
        return redirect('spisok')
        # При любой ошибке перенаправляем на список партнеров


def glav(request):
    # Главная страница с топ-3 партнерами
    try:
        # только первых 3 партнеров из базы
        partners = PartnerContact.objects.all()[:3]
        #  ограничение выборки для показа

        partner_data = []
        for partner in partners:
            try:
                total_sales = Sale.objects.filter(
                    partner_name=partner.organization
                ).aggregate(total=models.Sum('quantity'))['total'] or 0

                discount = calculate_discount(total_sales)

                partner_data.append({
                    'partner': partner,
                    'total_sales': total_sales,
                    'discount': discount
                })
            except Exception as e:
                continue

        return render(request, 'glav.html', {'partner_data': partner_data})

    except Exception as e:
        return render(request, 'glav.html', {'partner_data': []})
        # Главная страница всегда доступна, даже если
        # данные о партнерах временно недоступны


def forma(request, partner_id=None):
    """
     функция для добавления и редактирования партнеров
   как GET, так и POST запросы
    """
    try:
        partner = None
        if partner_id:
            #  передан partner_id - это режим редактирования
            partner = get_object_or_404(PartnerContact, id=partner_id)


        if request.method == 'POST':
            # Обработка отправки формы
            form = PartnerForm(request.POST, instance=partner)
            #  Форма автоматически определяет - создание это
            # или редактирование на основе параметра instance

            if form.is_valid():
                #  Данные прошли проверку
                try:
                    form.save()
                    return redirect('spisok')

                except Exception as e:

                    return render(request, 'forma.html', {
                        'form': form,
                        'partner': partner,
                        'error': 'Ошибка при сохранении данных'
                    })
                    #  понятное сообщение об ошибке
        else:

            form = PartnerForm(instance=partner)
            # Форма автоматически заполняется данными партнера при редактировании

        return render(request, 'forma.html', {
            'form': form,
            'partner': partner
        })

    except Exception as e:
        return redirect('spisok')
        #  При любой критической ошибке происходит редирект на список