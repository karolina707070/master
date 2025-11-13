from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from .models import PartnerContact, Sale
from .forms import PartnerForm


def calculate_discount(total_sales):
    """
    Расчет скидки для партнера на основе общего объема продаж
    до 10000: 0%
    10000-50000: 5%
    50000-300000: 10%
    свыше 300000: 15%
    """
    if total_sales >= 300000:
        return 15
    elif total_sales >= 50000:
        return 10
    elif total_sales >= 10000:
        return 5
    else:
        return 0

def spisok(request):

    partners = PartnerContact.objects.all()

    partner_data = []
    for partner in partners:

        total_sales = Sale.objects.filter(
            partner_name=partner.organization
        ).aggregate(total=models.Sum('quantity'))['total'] or 0


        discount = calculate_discount(total_sales)

        partner_data.append({
            'partner': partner,
            'total_sales': total_sales,
            'discount': discount
        })

    return render(request, 'spisok.html', {'partner_data': partner_data})


def history(request, partner_id):
    partner = get_object_or_404(PartnerContact, id=partner_id)


    sales = Sale.objects.filter(partner_name=partner.organization).select_related('product')


    context = {
        'partner': partner,
        'sales_history': sales,
    }

    return render(request, 'history.html', context)





def glav(request):
    partners = PartnerContact.objects.all()[:3]

    partner_data = []
    for partner in partners:
        total_sales = Sale.objects.filter(
            partner_name=partner.organization
        ).aggregate(total=models.Sum('quantity'))['total'] or 0

        discount = calculate_discount(total_sales)

        partner_data.append({
            'partner': partner,
            'total_sales': total_sales,
            'discount': discount
        })

    return render(request, 'glav.html', {'partner_data': partner_data})



def forma(request, partner_id=None):
    partner = None
    if partner_id:
        partner = get_object_or_404(PartnerContact, id=partner_id)

    if request.method == 'POST':
        form = PartnerForm(request.POST, instance=partner)
        if form.is_valid():
            form.save()
            return redirect('spisok')
    else:
        form = PartnerForm(instance=partner)

    return render(request, 'forma.html', {
        'form': form,
        'partner': partner
    })