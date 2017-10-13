from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.template import Context
from micro_admin.models import User, Group, Client, LoanAccount, Receipts, GroupMemberLoanAccount, LoanRepaymentEvery, Payments
from micro_admin.forms import LoanAccountForm
from core.utils import send_email_template, unique_random_number
from django.utils.encoding import smart_str
from django.conf import settings
import decimal
import datetime
import xlwt
import csv

d = decimal.Decimal


def client_loan_application(request, client_id):
    form = LoanAccountForm()
    client = get_object_or_404(Client, id=client_id)
    group = Group.objects.filter(clients__id__in=client_id).first()
    account_no = unique_random_number(LoanAccount)
    loan_pay = LoanRepaymentEvery.objects.all()
    if request.method == 'POST':
        form = LoanAccountForm(request.POST)
        if form.is_valid():
            loan_account = form.save(commit=False)
            loan_account.status = "Applied"
            loan_account.created_by = User.objects.get(username=request.user)
            loan_account.client = client
            interest_charged = d(
                (
                    d(loan_account.loan_amount) * (
                        d(loan_account.annual_interest_rate) / 12)
                ) / 100
            )
            loan_account.principle_repayment = d(
                int(loan_account.loan_repayment_every) * (
                    d(loan_account.loan_amount) / d(
                        loan_account.loan_repayment_period)
                )
            )
            loan_account.interest_charged = d(
                int(loan_account.loan_repayment_every) * d(interest_charged))
            loan_account.loan_repayment_amount = d(
                d(loan_account.principle_repayment) + d(
                    loan_account.interest_charged)
            )
            loan_account.total_loan_balance = d(d(loan_account.loan_amount))
            if group:
                loan_account.group = group
            loan_account.save()

            if client.email and client.email.strip():
                send_email_template(
                    subject="Your application for the Personal Loan (ID: %s) has been Received." % loan_account.account_no,
                    template_name="emails/client/loan_applied.html",
                    receipient=client.email,
                    ctx={
                        "client": client,
                        "loan_account": loan_account,
                        "link_prefix": settings.SITE_URL,
                    },
                )
            return JsonResponse({"error": False, "loanaccount_id": loan_account.id})
        else:
            return JsonResponse({"error": True, "message": form.errors})
    context = {
        'form': form, 'client': client, 'account_no': account_no,
        'loan_repayment_every': loan_pay
    }
    return render(request, "client/loan/application.html", context)


def client_loan_list(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    queryset = LoanAccount.objects.filter(client=client)
    return render(request, "client/loan/list_of_loan_accounts.html", {
        'client': client, 'loan_accounts_list': queryset
    })


def client_loan_account(request, pk):
    loan_account = LoanAccount.objects.get(id=pk)
    loan_disbursements = Payments.objects.filter(loan_account=loan_account)
    no_of_repayments_completed = int((loan_account.no_of_repayments_completed) / (loan_account.loan_repayment_every))
    context = {
        "loanaccount": loan_account, 'loan_disbursements': loan_disbursements,
        "no_of_repayments_completed": no_of_repayments_completed
    }
    return render(request, 'client/loan/account.html', context)


def client_loan_deposit_list(request, client_id, loanaccount_id):
    client = get_object_or_404(Client, id=client_id)
    loanaccount = get_object_or_404(LoanAccount, id=loanaccount_id)
    queryset = Receipts.objects.filter(client=client, member_loan_account=loanaccount).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0
    )
    context = {'receipts_lists': queryset, 'loanaccount': loanaccount}
    return render(request, 'client/loan/view_loan_deposits.html', context)


def client_loan_ledger_view(request, client_id, loanaccount_id):
    client = get_object_or_404(Client, id=client_id)
    loanaccount = get_object_or_404(LoanAccount, id=loanaccount_id)
    queryset = Receipts.objects.filter(client=client, member_loan_account=loanaccount).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0
    )
    context = {'client': client, 'loanaccount': loanaccount, 'receipts_list': queryset}
    return render(request, 'client/loan/client_ledger_account.html', context)


def client_ledger_csv_download(request, client_id, loanaccount_id):
    client = get_object_or_404(Client, id=client_id)
    loanaccount = get_object_or_404(LoanAccount, id=loanaccount_id)
    receipts_list = Receipts.objects.filter(
        client=client,
        member_loan_account=loanaccount
    ).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0
    )
    try:
        response = HttpResponse(content_type='application/x-download')
        response['Content-Disposition'] = 'attachment; filename=' + \
            client.first_name + client.last_name + "_ledger.csv"
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))
        group = client.group_set.get()
        writer.writerow([
            smart_str(client.id),
            smart_str(client.first_name),
            smart_str(group.name),
        ])
        writer.writerow([
            smart_str(u"Date"),
            smart_str(u"Recepit No"),
            smart_str(u"Demand Principal"),
            smart_str(u"Demand Interest"),
            smart_str(u"Collecton Principal"),
            smart_str(u"Collecton Interest"),
            smart_str(u"Balance Principal"),
            smart_str(u"Balance Interest"),
            smart_str(u"Loan Outstanding"),
        ])
        for receipt in receipts_list:
            if receipt.demand_loanprinciple_amount_atinstant:
                var1 = d(receipt.demand_loanprinciple_amount_atinstant)
            else:
                var1 = 0
            if receipt.loanprinciple_amount:
                var2 = d(receipt.loanprinciple_amount)
            else:
                var2 = 0
            if var1 > var2:
                balance_principle = d(d(var1) - d(var2))
            else:
                balance_principle = 0
            if receipt.demand_loaninterest_amount_atinstant:
                var4 = d(receipt.demand_loaninterest_amount_atinstant)
            else:
                var4 = 0
            if receipt.loaninterest_amount:
                var5 = d(receipt.loaninterest_amount)
            else:
                var5 = 0
            if var4 > var5:
                balance_interest = d(d(var4) - d(var5))
            else:
                balance_interest = 0
            writer.writerow([
                smart_str(receipt.date),
                smart_str(receipt.receipt_number),
                smart_str(receipt.demand_loanprinciple_amount_atinstant),
                smart_str(receipt.demand_loaninterest_amount_atinstant),
                smart_str(receipt.loanprinciple_amount),
                smart_str(receipt.loaninterest_amount),
                smart_str(balance_principle),
                smart_str(balance_interest),
                smart_str(receipt.principle_loan_balance_atinstant),
            ])
        return response
    except Exception as err:
        errmsg = "%s" % (err)
        return HttpResponse(errmsg)


def client_ledger_excel_download(request, client_id, loanaccount_id):
    client = get_object_or_404(Client, id=client_id)
    loanaccount = get_object_or_404(LoanAccount, id=loanaccount_id)
    receipts_list = Receipts.objects.filter(
        client=client,
        member_loan_account=loanaccount
    ).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0
    )
    try:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=' + \
            client.first_name + client.last_name + "_ledger.xls"
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("Ledger")

        row_num = 0

        columns = [
            (u"Date", 1000),
            (u"Receipt Number", 1000),
            (u"Demand Principal", 2000),
            (u"Demand Interest", 2000),
            (u"Collection Principal", 2000),
            (u"Collection Interest", 2000),
            (u"Balance Principal", 2000),
            (u"Balance Interest", 2000),
            (u"Loan Outstanding", 2000),
        ]

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], font_style)
            ws.col(col_num).width = columns[col_num][1]

        font_style = xlwt.XFStyle()
        font_style.alignment.wrap = 1

        for receipt in receipts_list:
            row_num += 1
            if receipt.demand_loanprinciple_amount_atinstant:
                var1 = d(receipt.demand_loanprinciple_amount_atinstant)
            else:
                var1 = 0
            if receipt.loanprinciple_amount:
                var2 = d(receipt.loanprinciple_amount)
            else:
                var2 = 0
            if var1 > var2:
                balance_principle = d(d(var1) - d(var2))
            else:
                balance_principle = 0
            if receipt.demand_loaninterest_amount_atinstant:
                var4 = d(receipt.demand_loaninterest_amount_atinstant)
            else:
                var4 = 0
            if receipt.loaninterest_amount:
                var5 = d(receipt.loaninterest_amount)
            else:
                var5 = 0
            if var4 > var5:
                balance_interest = d(d(var4) - d(var5))
            else:
                balance_interest = 0

            row = [
                str(receipt.date),
                receipt.receipt_number,
                receipt.demand_loanprinciple_amount_atinstant,
                receipt.demand_loaninterest_amount_atinstant,
                receipt.loanprinciple_amount,
                receipt.loaninterest_amount,
                balance_principle,
                balance_interest,
                receipt.principle_loan_balance_atinstant,
            ]
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response
    except Exception as err:
        errmsg = "%s" % (err)
        return HttpResponse(errmsg)


def client_ledger_pdf_download(request, client_id, loanaccount_id):
    client = get_object_or_404(Client, id=client_id)
    loanaccount = get_object_or_404(LoanAccount, id=loanaccount_id)
    receipts_list = Receipts.objects.filter(
        client=client,
        member_loan_account=loanaccount
    ).exclude(
        demand_loanprinciple_amount_atinstant=0,
        demand_loaninterest_amount_atinstant=0
    )
    try:
        # context = Context({
        #     'pagesize': 'A4', "receipts_list": receipts_list,
        #     "client": client, "mediaroot": settings.MEDIA_ROOT})
        context = dict({
            'pagesize': 'A4', "receipts_list": receipts_list,
            "client": client, "mediaroot": settings.MEDIA_ROOT})
        return render(request, 'pdfledger.html', context)
    except Exception as err:
        errmsg = "%s" % (err)
        return HttpResponse(errmsg)


def group_loan_application(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    account_no = unique_random_number(LoanAccount)
    loan_repayment_every = LoanRepaymentEvery.objects.all()
    form = LoanAccountForm()
    if request.method == 'POST':
        form = LoanAccountForm(request.POST)
        if form.is_valid():
            loan_account = form.save(commit=False)
            if len(group.clients.all()):
                loan_account.status = "Applied"
                loan_account.created_by = User.objects.get(username=request.user)
                loan_account.group = group

                interest_charged = d(
                    (
                        d(loan_account.loan_amount) * (
                            d(loan_account.annual_interest_rate) / 12)
                    ) / 100
                )

                loan_account.principle_repayment = d(
                    int(loan_account.loan_repayment_every) *
                    (
                        d(loan_account.loan_amount) / d(
                            loan_account.loan_repayment_period)
                    )
                )
                loan_account.interest_charged = d(
                    int(loan_account.loan_repayment_every) * d(interest_charged))
                loan_account.loan_repayment_amount = d(
                    d(loan_account.principle_repayment) + d(
                        loan_account.interest_charged)
                )
                loan_account.total_loan_balance = d(d(loan_account.loan_amount))
                loan_account.save()
                loan_amount = (loan_account.loan_amount) / group.clients.all().count()
                for client in group.clients.all():
                    if client.email and client.email.strip():
                        send_email_template(
                            subject="Group Loan (ID: %s) application has been Received."
                                    % loan_account.account_no,
                            template_name="emails/group/loan_applied.html",
                            receipient=client.email,
                            ctx={
                                "client": client,
                                "loan_account": loan_account,
                                "link_prefix": settings.SITE_URL,
                            },
                        )
                    group_member = GroupMemberLoanAccount.objects.create(
                        account_no=loan_account.account_no,
                        client=client, loan_amount=loan_amount,
                        group_loan_account=loan_account, loan_repayment_period=loan_account.loan_repayment_period,
                        loan_repayment_every=loan_account.loan_repayment_every,
                        total_loan_balance=d(loan_amount), status=loan_account.status,
                        annual_interest_rate=loan_account.annual_interest_rate,
                        interest_type=loan_account.interest_type
                    )
                    interest_charged = d(
                        (
                            d(group_member.loan_amount) * (
                                d(loan_account.annual_interest_rate) / 12)
                        ) / 100
                    )

                    group_member.principle_repayment = d(
                        int(group_member.loan_repayment_every) *
                        (
                            d(group_member.loan_amount) / d(
                                group_member.loan_repayment_period)
                        )
                    )
                    group_member.interest_charged = d(
                        int(group_member.loan_repayment_every) * d(interest_charged))
                    group_member.loan_repayment_amount = d(
                        d(group_member.principle_repayment) + d(
                            group_member.interest_charged)
                    )
                    group_member.save()

                return JsonResponse({"error": False, "loanaccount_id": loan_account.id})
            else:
                return JsonResponse({"error": True, "error_message": "Group does not contains any members."})
        else:
            return JsonResponse({"error": True, "message": form.errors})
    context = {
        'form': form, 'group': group, 'account_no': account_no,
        'loan_repayment_every': loan_repayment_every
    }
    return render(request, 'group/loan/application.html', context)


def group_loan_list(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    queryset = LoanAccount.objects.filter(group=group)
    context = {'loan_accounts_list': queryset, 'group': group}
    return render(request, 'group/loan/list_of_loan_accounts.html', context)


def group_loan_account(request, loanaccount_id):
    loan_object = LoanAccount.objects.get(id=loanaccount_id)
    group = loan_object.group
    total_loan_amount_repaid = 0
    total_interest_repaid = 0
    loan_disbursements = Payments.objects.filter(loan_account=loan_object)
    group_members = GroupMemberLoanAccount.objects.filter(group_loan_account=loan_object)
    for member in group_members:
        total_loan_amount_repaid += member.total_loan_amount_repaid
        total_interest_repaid += member.total_interest_repaid
    context = {}
    context['total_loan_amount_repaid'] = total_loan_amount_repaid
    context['total_interest_repaid'] = total_interest_repaid
    context['total_loan_paid'] = total_loan_amount_repaid + total_interest_repaid
    context['group'] = group
    context["loan_disbursements"] = loan_disbursements
    return render(request, 'group/loan/account.html', context)


def group_loan_deposits_list(request, loanaccount_id, group_id):
    loan_account = get_object_or_404(LoanAccount, id=loanaccount_id)
    group = get_object_or_404(Group, id=group_id)
    queryset = Receipts.objects.filter(
        group=group,
        group_loan_account=loan_account
    )
    context = {}
    context["loan_account"] = loan_account
    context["group"] = group
    context['receipts_list'] = queryset
    return render(request, 'group/loan/list_of_loan_deposits.html', context)


def change_loan_account_status(request, pk):
    # if request.method == 'POST':
        loan_object = get_object_or_404(LoanAccount, id=pk)
        if loan_object:
            branch_id = loan_object.group.branch.id
        elif loan_object.client:
            branch_id = loan_object.client.branch.id
        else:
            branch_id = None
        if branch_id:
            if (request.user.is_admin or
                (request.user.has_perm("branch_manager") and
                 request.user.branch.id == branch_id)):
                status = request.GET.get("status")
                if status in ['Closed', 'Withdrawn', 'Rejected', 'Approved']:
                    loan_object.status = request.GET.get("status")
                    loan_object.approved_date = datetime.datetime.now()
                    loan_object.save()
                    if loan_object.client:
                        if loan_object.status == 'Approved':
                            if loan_object.client.email and loan_object.client.email.strip():
                                send_email_template(
                                    subject="Your application for the Personal Loan (ID: %s) has been Approved." % loan_object.account_no,
                                    template_name="emails/client/loan_approved.html",
                                    receipient=loan_object.client.email,
                                    ctx={
                                        "client": loan_object.client,
                                        "loan_account": loan_object,
                                        "link_prefix": settings.SITE_URL,
                                    },
                                )

                    elif loan_object.group:
                        group_member_loans = GroupMemberLoanAccount.objects.filter(group_loan_account=loan_object)
                        group_member_loans.update(status=loan_object.status)
                        group_member_loans.update(loan_issued_date=loan_object.loan_issued_date)
                        group_member_loans.update(interest_type=loan_object.interest_type)
                        for client in loan_object.group.clients.all():
                            if client.email and client.email.strip():
                                send_email_template(
                                    subject="Group Loan (ID: %s) application has been Approved."
                                            % loan_object.account_no,
                                    template_name="emails/group/loan_approved.html",
                                    receipient=client.email,
                                    ctx={
                                        "client": client,
                                        "loan_account": loan_object,
                                        "link_prefix": settings.SITE_URL,
                                    },
                                )
                    data = {"error": False}
                else:
                    data = {"error": True, "error_message": "Status is not in available choices"}
            else:
                data = {"error": True, "error_message": "You don't have permission to change the status."}
        else:
            data = {"error": True, "error_message": "Branch Id not Found"}

        data["success_url"] = reverse('loans:clientloanaccount', kwargs={"pk": loan_object.id})
        return JsonResponse(data)


def issue_loan(request, loanaccount_id):
    loan_account = get_object_or_404(LoanAccount, id=loanaccount_id)
    if loan_account.group or loan_account.client:
        loan_account.loan_issued_date = datetime.datetime.now()
        loan_account.loan_issued_by = request.user
        loan_account.save()

    if loan_account.group:
        group_members = GroupMemberLoanAccount.objects.filter(group_loan_account=loan_account)
        group_members.update(loan_issued_date=datetime.datetime.now())
        url = reverse("loans:grouploanaccount", kwargs={"pk": loan_account.id})
    elif loan_account.client:
        url = reverse("loans:clientloanaccount", kwargs={'pk': loan_account.id})
    else:
        url = "/"
    return HttpResponseRedirect(url)
