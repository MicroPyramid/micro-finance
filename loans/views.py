from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.template import Context
from micro_admin.models import User, Group, Client, LoanAccount, Receipts, GroupMemberLoanAccount, LoanRepaymentEvery, Payments
from django.views.generic import CreateView, DetailView, ListView, View
from micro_admin.forms import LoanAccountForm
from core.utils import send_email_template, unique_random_number
from django.utils.encoding import smart_str
from django.conf import settings
import decimal
import datetime
import xlwt
import csv

d = decimal.Decimal


# Client Loans - (apply, list, detail, repayments-list)
# -------------------------------------------------------

class ClientLoanApplicationView(LoginRequiredMixin, CreateView):
    model = LoanAccount
    form_class = LoanAccountForm
    template_name = "client/loan/application.html"

    def dispatch(self, request, *args, **kwargs):
        self.client = get_object_or_404(Client, id=self.kwargs.get('client_id'))
        return super(ClientLoanApplicationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientLoanApplicationView, self).get_context_data(**kwargs)
        context["account_no"] = unique_random_number(LoanAccount)
        context["loan_repayment_every"] = LoanRepaymentEvery.objects.all()
        context["client"] = self.client
        return context

    def form_valid(self, form):
        loan_account = form.save(commit=False)
        loan_account.status = "Applied"
        loan_account.created_by = User.objects.get(username=self.request.user)
        loan_account.client = self.client
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
        loan_account.save()

        if self.client.email and self.client.email.strip():
            send_email_template(
                subject="Your application for the Personal Loan (ID: %s) has been Received." % loan_account.account_no,
                template_name="emails/client/loan_applied.html",
                receipient=self.client.email,
                ctx={
                    "client": self.client,
                    "loan_account": loan_account,
                    "link_prefix": settings.SITE_URL,
                },
            )
        return JsonResponse({"error": False, "loanaccount_id": loan_account.id})

    def form_invalid(self, form):
        return JsonResponse({"error": True, "message": form.errors})


class ClientLoansListView(LoginRequiredMixin, ListView):
    template_name = "client/loan/list_of_loan_accounts.html"
    context_object_name = "loan_accounts_list"

    def get_queryset(self):
        self.client = get_object_or_404(Client, id=self.kwargs.get("client_id"))
        queryset = LoanAccount.objects.filter(client=self.client)
        return queryset

    def get_context_data(self):
        context = super(ClientLoansListView, self).get_context_data()
        context["client"] = self.client
        return context


class ClientLoanAccount(LoginRequiredMixin, DetailView):
    model = LoanAccount
    pk = 'pk'
    template_name = "client/loan/account.html"

    def get_context_data(self, **kwargs):
        context = super(ClientLoanAccount, self).get_context_data(**kwargs)
        context["loan_disbursements"] = Payments.objects.filter(loan_account=self.object)
        context["no_of_repayments_completed"] = int((self.object.no_of_repayments_completed)/(self.object.loan_repayment_every))
        return context


class ClientLoanDepositsListView(LoginRequiredMixin, ListView):
    model = Receipts
    context_object_name = "receipts_lists"
    template_name = "client/loan/view_loan_deposits.html"

    def get_queryset(self):
        self.client = get_object_or_404(Client, id=self.kwargs.get("client_id"))
        self.loanaccount = get_object_or_404(LoanAccount, id=self.kwargs.get('loanaccount_id'))
        queryset = self.model.objects.filter(
            client=self.client,
            member_loan_account=self.loanaccount
        ).exclude(
            demand_loanprinciple_amount_atinstant=0,
            demand_loaninterest_amount_atinstant=0
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ClientLoanDepositsListView, self).get_context_data(**kwargs)
        context["loanaccount"] = self.loanaccount
        return context


# Client Loans - Ledger (view, CSV, Excel, PDF downloads)
# -------------------------------------------------------

class ClientLoanLedgerView(LoginRequiredMixin, ListView):
    model = Receipts
    context_object_name = "receipts_list"
    template_name = "client/loan/client_ledger_account.html"

    def get_queryset(self):
        self.client = get_object_or_404(Client, id=self.kwargs.get("client_id"))
        self.loanaccount = get_object_or_404(LoanAccount, id=self.kwargs.get("loanaccount_id"))
        queryset = self.model.objects.filter(
            client=self.client,
            member_loan_account=self.loanaccount
        ).exclude(
            demand_loanprinciple_amount_atinstant=0,
            demand_loaninterest_amount_atinstant=0
        )
        return queryset

    def get_context_data(self):
        context = super(ClientLoanLedgerView, self).get_context_data()
        context['client'] = self.client
        context['loanaccount'] = self.loanaccount
        return context


class ClientLedgerCSVDownload(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        client = get_object_or_404(Client, id=kwargs.get("client_id"))
        loanaccount = get_object_or_404(LoanAccount, id=self.kwargs.get("loanaccount_id"))
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
                smart_str(u"Demand Peenal Interest"),
                smart_str(u"Collecton Principal"),
                smart_str(u"Collecton Interest"),
                smart_str(u"Collecton Peenal Interest"),
                smart_str(u"Balance Principal"),
                smart_str(u"Balance Interest"),
                smart_str(u"Balance Peenal Interest"),
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
                    smart_str("0"),
                    smart_str(receipt.loanprinciple_amount),
                    smart_str(receipt.loaninterest_amount),
                    smart_str("0"),
                    smart_str(balance_principle),
                    smart_str(balance_interest),
                    smart_str("0"),
                    smart_str(receipt.principle_loan_balance_atinstant),
                ])
            return response
        except Exception as err:
            errmsg = "%s" % (err)
            return HttpResponse(errmsg)


class ClientLedgerExcelDownload(LoginRequiredMixin, View):

    def get(self, request, **kwargs):
        client = get_object_or_404(Client, id=kwargs.get("client_id"))
        loanaccount = get_object_or_404(LoanAccount, id=self.kwargs.get("loanaccount_id"))
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
                (u"Demand Peenal Interest", 2000),
                (u"Collection Principal", 2000),
                (u"Collection Interest", 2000),
                (u"Collection Peenal Interest", 2000),
                (u"Balance Principal", 2000),
                (u"Balance Interest", 2000),
                (u"Balance Peenal Interest", 2000),
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
                    0,
                    receipt.loanprinciple_amount,
                    receipt.loaninterest_amount,
                    0,
                    balance_principle,
                    balance_interest,
                    0,
                    receipt.principle_loan_balance_atinstant,
                ]
                for col_num in range(len(row)):
                    ws.write(row_num, col_num, row[col_num], font_style)

            wb.save(response)
            return response
        except Exception as err:
            errmsg = "%s" % (err)
            return HttpResponse(errmsg)


class ClientLedgerPDFDownload(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        client = get_object_or_404(Client, id=kwargs.get("client_id"))
        loanaccount = get_object_or_404(LoanAccount, id=self.kwargs.get("loanaccount_id"))
        receipts_list = Receipts.objects.filter(
            client=client,
            member_loan_account=loanaccount
        ).exclude(
            demand_loanprinciple_amount_atinstant=0,
            demand_loaninterest_amount_atinstant=0
        )
        try:
            # template = get_template("pdfledger.html")
            context = Context({
                'pagesize': 'A4', "receipts_list": receipts_list,
                "client": client, "mediaroot": settings.MEDIA_ROOT})
            return render(request, 'pdfledger.html', context)
            # html = template.render(context)
            # result = StringIO.StringIO()
            # # pdf = pisa.pisaDocument(StringIO.StringIO(html), dest=result)
            # if not pdf.err:
            #     return HttpResponse(result.getvalue(),
            #                         content_type='application/pdf')
            # else:
            #     return HttpResponse('We had some errors')
        except Exception as err:
            errmsg = "%s" % (err)
            return HttpResponse(errmsg)


# Group Loans - (apply, list, detail, repayments-list)
# -------------------------------------------------------

class GroupLoanApplicationView(LoginRequiredMixin, CreateView):
    model = LoanAccount
    form_class = LoanAccountForm
    template_name = "group/loan/application.html"

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(Group, id=self.kwargs.get('group_id'))
        return super(GroupLoanApplicationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GroupLoanApplicationView, self).get_context_data(**kwargs)
        context["account_no"] = unique_random_number(LoanAccount)
        context["loan_repayment_every"] = LoanRepaymentEvery.objects.all()
        context["group"] = self.group
        return context

    def form_valid(self, form):
        loan_account = form.save(commit=False)
        if len(self.group.clients.all()):
            loan_account.status = "Applied"
            loan_account.created_by = User.objects.get(username=self.request.user)
            loan_account.group = self.group

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
            loan_amount = (loan_account.loan_amount) / self.group.clients.all().count()
            for client in self.group.clients.all():
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

    def form_invalid(self, form):
        return JsonResponse({"error": True, "message": form.errors})


class GroupLoansListView(LoginRequiredMixin, ListView):
    template_name = "group/loan/list_of_loan_accounts.html"
    context_object_name = "loan_accounts_list"

    def get_queryset(self):
        self.group = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        queryset = LoanAccount.objects.filter(group=self.group)
        return queryset

    def get_context_data(self):
        context = super(GroupLoansListView, self).get_context_data()
        context["group"] = self.group
        return context


class GroupLoanAccount(LoginRequiredMixin, DetailView):
    model = LoanAccount
    pk = 'pk'
    context_object_name = "loan_account"
    template_name = "group/loan/account.html"

    def get_context_data(self, **kwargs):
        total_loan_amount_repaid = 0
        total_interest_repaid = 0
        context = super(GroupLoanAccount, self).get_context_data(**kwargs)
        context['group'] = self.object.group
        group_members = GroupMemberLoanAccount.objects.filter(group_loan_account=self.object)
        context['group_members'] = group_members
        for member in group_members:
            total_loan_amount_repaid += member.total_loan_amount_repaid
            total_interest_repaid += member.total_interest_repaid
        context['total_loan_amount_repaid'] = total_loan_amount_repaid
        context['total_interest_repaid'] = total_interest_repaid
        context['total_loan_paid'] = total_loan_amount_repaid + total_interest_repaid
        return context


class GroupLoanDepositsListView(LoginRequiredMixin, ListView):
    model = Receipts
    context_object_name = "receipts_list"
    template_name = "group/loan/list_of_loan_deposits.html"

    def get_queryset(self):
        self.loan_account = get_object_or_404(LoanAccount, id=self.kwargs.get('loanaccount_id'))
        self.group = get_object_or_404(Group, id=self.kwargs.get("group_id"))
        queryset = self.model.objects.filter(
            group=self.group,
            group_loan_account=self.loan_account
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GroupLoanDepositsListView, self).get_context_data(**kwargs)
        context["loan_account"] = self.loan_account
        context["group"] = self.group
        return context


# Change Loan Account Status (group/client)
class ChangeLoanAccountStatus(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(LoanAccount, id=kwargs.get("pk"))
        if self.object.group:
            branch_id = self.object.group.branch.id
        elif self.object.client:
            branch_id = self.object.client.branch.id
        else:
            branch_id = None
        if branch_id:
            if (request.user.is_admin or
                (request.user.has_perm("branch_manager") and
                 request.user.branch.id == branch_id)):
                status = request.GET.get("status")
                if status in ['Closed', 'Withdrawn', 'Rejected', 'Approved']:
                    self.object.status = request.GET.get("status")
                    self.object.approved_date = datetime.datetime.now()
                    self.object.save()
                    if self.object.client:
                        if self.object.status == 'Approved':
                            if self.object.client.email and self.object.client.email.strip():
                                send_email_template(
                                    subject="Your application for the Personal Loan (ID: %s) has been Approved." % self.object.account_no,
                                    template_name="emails/client/loan_approved.html",
                                    receipient=self.object.client.email,
                                    ctx={
                                        "client": self.object.client,
                                        "loan_account": self.object,
                                        "link_prefix": settings.SITE_URL,
                                    },
                                )

                    elif self.object.group:
                        group_member_loans = GroupMemberLoanAccount.objects.filter(group_loan_account=self.object)
                        group_member_loans.update(status=self.object.status)
                        group_member_loans.update(loan_issued_date=self.object.loan_issued_date)
                        group_member_loans.update(interest_type=self.object.interest_type)
                        for client in self.object.group.clients.all():
                            if client.email and client.email.strip():
                                send_email_template(
                                    subject="Group Loan (ID: %s) application has been Approved."
                                            % self.object.account_no,
                                    template_name="emails/group/loan_approved.html",
                                    receipient=client.email,
                                    ctx={
                                        "client": client,
                                        "loan_account": self.object,
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

        data["success_url"] = reverse('loans:clientloanaccount', kwargs={"pk": self.object.id})
        return JsonResponse(data)


# Issue group/client Loan
class IssueLoan(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        loan_account = get_object_or_404(LoanAccount, id=kwargs.get("loanaccount_id"))
        if loan_account.group or loan_account.client:
            loan_account.loan_issued_date = datetime.datetime.now()
            loan_account.loan_issued_by = self.request.user
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
