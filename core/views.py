import decimal
import calendar

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Q
from datetime import datetime

from .forms import ReceiptForm, PaymentForm, ClientLoanAccountsForm, GetLoanDemandsForm, GetFixedDepositsForm, GetRecurringDepositsForm, \
    GetFixedDepositsPaidForm, GetRecurringDepositsPaidForm, ClientDepositsAccountsForm
from micro_admin.models import Branch, Receipts, PAYMENT_TYPES, Payments, LoanAccount, \
    Group, Client, FixedDeposits, RecurringDeposits, GroupMemberLoanAccount
from .utils import send_email_template
d = decimal.Decimal


@login_required
def client_loan_accounts_view(request):
    form = ClientLoanAccountsForm()
    print("GET")
    if request.method == 'POST':
        form = ClientLoanAccountsForm(request.POST)
        print("Not Valid")
        if form.is_valid():
            if form.client:
                print("Valid")
                loan_accounts_filter = LoanAccount.objects.filter(
                    client=form.client,
                    status='Approved'
                ).filter(Q(total_loan_balance__gt=0) | Q(interest_charged__gt=0)).exclude(loan_issued_by__isnull=True, loan_issued_date__isnull=True)
                member_loan_has_payments = []
                for loan in loan_accounts_filter:
                    payments = Payments.objects.filter(client=form.client, loan_account=loan)
                    if payments:
                        member_loan_has_payments.append(loan.id)
                loan_accounts = loan_accounts_filter.filter(
                    id__in=[int(x) for x in member_loan_has_payments]).values_list("account_no", "loan_amount")
                groups = form.client.group_set.all()
                default_group = groups.first()
                if default_group:
                    group_accounts_filter1 = LoanAccount.objects.filter(
                        group=default_group,
                        status='Approved'
                    ).exclude(loan_issued_by__isnull=True,
                              loan_issued_date__isnull=True)
                    group_accounts_filter = GroupMemberLoanAccount.objects.filter(
                        group_loan_account__in=group_accounts_filter1,
                        client=form.client, status="Approved")
                    group_loan_has_payments = []
                    for loan in group_accounts_filter:
                        payments = Payments.objects.filter(group=default_group, loan_account=loan.group_loan_account)
                        if payments:
                            group_loan_has_payments.append(loan.group_loan_account.id)
                    group_accounts = group_accounts_filter.filter(
                        group_loan_account__in=[int(x) for x in group_loan_has_payments]).values_list("account_no", "loan_amount")
                else:
                    group_accounts = []
                fixed_deposit_accounts = FixedDeposits.objects.filter(
                    client=form.client,
                    status='Opened'
                ).values_list("fixed_deposit_number", "fixed_deposit_amount")
                recurring_deposit_accounts = RecurringDeposits.objects.filter(
                    client=form.client,
                    status="Opened"
                ).values_list("reccuring_deposit_number", "recurring_deposit_amount")
            else:
                loan_accounts = []
                group_accounts = []
                fixed_deposit_accounts = []
                recurring_deposit_accounts = []
                default_group = None
            group = {"group_name": default_group.name if default_group else "",
                     "group_account_number": default_group.account_number if default_group else ""}
            data = {"error": False,
                    "loan_accounts": list(loan_accounts),
                    "group_accounts": list(group_accounts),
                    "fixed_deposit_accounts": list(fixed_deposit_accounts),
                    "recurring_deposit_accounts": list(recurring_deposit_accounts),
                    "group": group if default_group else False}
        else:
            data = {"error": True, "errors": form.errors}
        return JsonResponse(data)


@login_required
def get_loan_demands_view(request):
    form = GetLoanDemandsForm()
    if request.method == 'POST':
        form = GetLoanDemandsForm(request.POST)
        if form.is_valid():
            data = {
                "error": False,
                "demand_loanprinciple": form.loan_account.principle_repayment or 0,
                "demand_loaninterest": form.loan_account.interest_charged or 0
            }
        else:
            data = {"error": True, "errors": form.errors}
        return JsonResponse(data)


@login_required
def get_fixed_deposit_accounts_view(request):
    form = GetFixedDepositsForm()
    if request.method == 'POST':
        form = GetFixedDepositsForm(request.POST)
        if form.is_valid():
            data = {
                "error": False,
                "fixeddeposit_amount": form.fixed_deposit_account.fixed_deposit_amount or 0
            }
        else:
            data = {"error": True, "errors": form.errors}
        return JsonResponse(data)


@login_required
def get_recurring_deposit_accounts_view(request):
    form = GetRecurringDepositsForm()
    if request.method == 'POST':
        form = GetRecurringDepositsForm(request.POST)
        if form.is_valid():
            data = {
                "error": False,
                "recurringdeposit_amount": form.recurring_deposit_account.recurring_deposit_amount or 0
            }
        else:
            data = {"error": True, "errors": form.errors}
        return JsonResponse(data)


@login_required
def loan_valid(request, loan_account):
    form = ReceiptForm()
    if loan_account.status == "Approved":
        if loan_account.loan_issued_date:
            if d(loan_account.total_loan_balance) or d(loan_account.interest_charged) or \
               d(loan_account.loan_repayment_amount) or d(loan_account.principle_repayment):
                if form.cleaned_data.get("loanprinciple_amount") or form.cleaned_data.get("loaninterest_amount"):
                    if d(loan_account.total_loan_amount_repaid) == d(loan_account.loan_amount) and d(loan_account.total_loan_balance) == d(0):
                        if (form.cleaned_data.get("loaninterest_amount")) == \
                           (loan_account.interest_charged):
                            if form.cleaned_data.get("loanprinciple_amount") == loan_account.principle_repayment:
                                loan_account.loan_repayment_amount = 0
                                loan_account.principle_repayment = 0
                                loan_account.interest_charged = 0
                            elif (form.cleaned_data.get("loanprinciple_amount")) < (loan_account.principle_repayment):
                                balance_principle = (loan_account.principle_repayment) -\
                                    (form.cleaned_data.get("loanprinciple_amount"))
                                loan_account.principle_repayment = balance_principle
                                loan_account.loan_repayment_amount = balance_principle
                                loan_account.interest_charged = 0
                        else:
                            if form.cleaned_data.get("loaninterest_amount") < loan_account.interest_charged:
                                if form.cleaned_data.get("loanprinciple_amount") == loan_account.principle_repayment:
                                    balance_interest = loan_account.interest_charged -\
                                        form.cleaned_data.get("loaninterest_amount")
                                    loan_account.interest_charged = balance_interest
                                    loan_account.loan_repayment_amount = balance_interest
                                    loan_account.principle_repayment = 0
                                # if form.cleaned_data.get("loanprinciple_amount"):
                                #     if form.cleaned_data.get("loanprinciple_amount") < \
                                #             loan_account.principle_repayment:
                                #         balance_principle = loan_account.principle_repayment -\
                                #             form.cleaned_data.get("loanprinciple_amount")
                                #         loan_account.principle_repayment = d(balance_principle)
                                #         balance_interest = loan_account.interest_charged -\
                                #             form.cleaned_data.get("loaninterest_amount")
                                #         loan_account.interest_charged = d(balance_interest)
                                #         loan_account.loan_repayment_amount = d(balance_principle) +\
                                #             d(balance_interest)

                    elif loan_account.total_loan_amount_repaid < loan_account.loan_amount and loan_account.total_loan_balance:
                        if int(loan_account.no_of_repayments_completed) >= int(loan_account.loan_repayment_period):
                            if form.cleaned_data.get("loaninterest_amount") ==\
                                    loan_account.interest_charged:
                                if loan_account.interest_type == "Flat":
                                    loan_account.interest_charged = (int(loan_account.loan_repayment_every) *
                                                                        (loan_account.loan_amount * (loan_account.annual_interest_rate / 12)) / 100)
                                elif loan_account.interest_type == "Declining":
                                    loan_account.interest_charged = (int(loan_account.loan_repayment_every) *
                                                                        ((loan_account.total_loan_balance * (
                                                                            loan_account.annual_interest_rate / 12)) / 100))
                            elif form.cleaned_data.get("loaninterest_amount") < loan_account.interest_charged:
                                balance_interest = loan_account.interest_charged -\
                                    form.cleaned_data.get("loaninterest_amount")
                                if loan_account.interest_type == "Flat":
                                    interest_charged = (int(loan_account.loan_repayment_every) *
                                                        ((loan_account.loan_amount * (
                                                            loan_account.annual_interest_rate / 12)) / 100))
                                elif loan_account.interest_type == "Declining":
                                    interest_charged = ((int(loan_account.loan_repayment_every) * ((loan_account.total_loan_balance) * (
                                        (loan_account.annual_interest_rate) / 12)) / 100))
                                loan_account.interest_charged = (balance_interest + interest_charged)

                            if form.cleaned_data.get("loanprinciple_amount") == \
                                    loan_account.principle_repayment:
                                loan_account.principle_repayment = \
                                    loan_account.total_loan_balance
                                loan_account.loan_repayment_amount = \
                                    ((loan_account.total_loan_balance) +
                                        (loan_account.interest_charged))
                            elif form.cleaned_data.get("loanprinciple_amount") < (loan_account.principle_repayment):
                                principle_repayable = ((loan_account.loan_amount) / (loan_account.loan_repayment_period))
                                lastmonth_bal = (((principle_repayable) * (
                                    loan_account.no_of_repayments_completed)) - (loan_account.total_loan_amount_repaid))
                                balance_principle = d(d(d(loan_account.loan_repayment_amount) - d(
                                    loan_account.interest_charged)) - d(form.cleaned_data.get("loanprinciple_amount")))
                                loan_account.principle_repayment =\
                                    ((loan_account.total_loan_balance))
                                loan_account.loan_repayment_amount = (
                                    (loan_account.total_loan_balance) +
                                    (loan_account.interest_charged))

                        elif int(loan_account.no_of_repayments_completed) < int(loan_account.loan_repayment_period):
                            principle_repayable = (
                                (loan_account.loan_amount) / (loan_account.loan_repayment_period))
                            if loan_account.interest_type == "Flat":
                                if (form.cleaned_data.get("loaninterest_amount")) ==\
                                        (loan_account.interest_charged):
                                    interest_charged = (
                                        int(loan_account.loan_repayment_every) * (
                                            ((loan_account.loan_amount) * (
                                                (loan_account.annual_interest_rate) / 12)) / 100))
                                    balance_interest = \
                                        d(loan_account.interest_charged) -\
                                        d(form.cleaned_data.get("loaninterest_amount"))

                                    loan_account.interest_charged = d(balance_interest + interest_charged)

                                elif (form.cleaned_data.get("loaninterest_amount")) <\
                                        (loan_account.interest_charged):
                                    balance_interest = \
                                        d(loan_account.interest_charged) -\
                                        d(form.cleaned_data.get("loaninterest_amount"))

                                    interest_charged = (
                                        int(loan_account.loan_repayment_every) * (
                                            ((loan_account.loan_amount) * (
                                                (loan_account.annual_interest_rate) / 12)) / 100))

                                    loan_account.interest_charged = d(balance_interest + interest_charged)

                                elif (form.cleaned_data.get("loaninterest_amount")) >\
                                        (loan_account.interest_charged):
                                    interest_charged = (
                                        int(loan_account.loan_repayment_every) * (
                                            ((loan_account.loan_amount) * (
                                                (loan_account.annual_interest_rate) / 12)) / 100))

                                    loan_account.interest_charged = d(balance_interest + interest_charged)

                            elif loan_account.interest_type == "Declining":
                                if (form.cleaned_data.get("loaninterest_amount")) <=\
                                        (loan_account.interest_charged):
                                    interest_charged = (
                                        int(loan_account.loan_repayment_every) * (
                                            ((loan_account.total_loan_balance) * (
                                                (loan_account.annual_interest_rate) / 12)) / 100))
                                    balance_interest = d(loan_account.interest_charged) - d(form.cleaned_data.get("loaninterest_amount"))
                                    loan_account.interest_charged = d(balance_interest + interest_charged)

                                elif (form.cleaned_data.get("loaninterest_amount")) >\
                                        (loan_account.interest_charged):
                                    interest_charged = (
                                        int(loan_account.loan_repayment_every) * (
                                            ((loan_account.total_loan_balance) * (
                                                (loan_account.annual_interest_rate) / 12)) / 100))

                                    balance_interest = (form.cleaned_data.get("loaninterest_amount")) -\
                                        (loan_account.interest_charged)
                                    loan_account.interest_charged = d(balance_interest + interest_charged)
                            lastmonth_bal = (((principle_repayable) * (
                                loan_account.no_of_repayments_completed)) - (loan_account.total_loan_amount_repaid))
                            if (form.cleaned_data.get("loanprinciple_amount")) == (
                                    (int(loan_account.loan_repayment_every) * (
                                        principle_repayable))):
                                if ((int(loan_account.no_of_repayments_completed) + int(loan_account.loan_repayment_every)) == int(
                                        loan_account.loan_repayment_period)):
                                    loan_account.principle_repayment = (
                                        loan_account.total_loan_balance)
                                    loan_account.loan_repayment_amount = (
                                        (loan_account.total_loan_balance) +
                                        (loan_account.interest_charged))
                                elif (loan_account.total_loan_balance) <\
                                    ((int(loan_account.loan_repayment_every) * (
                                        principle_repayable))):
                                    loan_account.principle_repayment = (
                                        loan_account.total_loan_balance)
                                    loan_account.loan_repayment_amount = (
                                        (loan_account.total_loan_balance) +
                                        (loan_account.interest_charged))
                                else:
                                    loan_account.principle_repayment = (
                                        int(loan_account.loan_repayment_every) *
                                        ((loan_account.loan_amount) /
                                            (loan_account.loan_repayment_period))) + (lastmonth_bal)
                                    loan_account.loan_repayment_amount = (
                                        (loan_account.principle_repayment) +
                                        (loan_account.interest_charged))
                            elif (form.cleaned_data.get("loanprinciple_amount")) <\
                                    ((int(loan_account.loan_repayment_every) * (principle_repayable))):
                                balance_principle = (
                                    ((int(loan_account.loan_repayment_every) *
                                        (principle_repayable))) - (form.cleaned_data.get("loanprinciple_amount")))
                                lastmonth_bal = ((
                                    (((principle_repayable))) * (loan_account.no_of_repayments_completed))) - (loan_account.total_loan_amount_repaid)
                                if (int(loan_account.no_of_repayments_completed) + int(loan_account.loan_repayment_every) == int(
                                        loan_account.loan_repayment_period)):
                                    loan_account.principle_repayment = (
                                        loan_account.total_loan_balance)
                                    loan_account.loan_repayment_amount = (
                                        (loan_account.total_loan_balance) +
                                        (loan_account.interest_charged))
                                elif (loan_account.total_loan_balance) <\
                                        ((int(loan_account.loan_repayment_every) *
                                            (principle_repayable))):
                                    loan_account.principle_repayment = (loan_account.total_loan_balance)
                                    loan_account.loan_repayment_amount = (
                                        (loan_account.total_loan_balance) + (loan_account.interest_charged))
                                else:
                                    loan_account.principle_repayment = (
                                        (int(loan_account.loan_repayment_every) *
                                            (principle_repayable)) + (lastmonth_bal))
                                    loan_account.loan_repayment_amount = (
                                        (loan_account.principle_repayment) +
                                        (loan_account.interest_charged))
                            elif (form.cleaned_data.get("loanprinciple_amount")) > (int(loan_account.loan_repayment_every) * (principle_repayable)):
                                balance_principle = ((form.cleaned_data.get("loanprinciple_amount")) - (
                                    int(loan_account.loan_repayment_every) * (principle_repayable)))
                                if ((int(loan_account.no_of_repayments_completed) + int(
                                        loan_account.loan_repayment_every)) == int(loan_account.loan_repayment_period)):
                                    loan_account.principle_repayment = (
                                        loan_account.total_loan_balance)
                                    loan_account.loan_repayment_amount = (
                                        (loan_account.total_loan_balance) +
                                        (loan_account.interest_charged))
                                elif (form.cleaned_data.get("loanprinciple_amount") == loan_account.principle_repayment):
                                    loan_account.principle_repayment = (
                                        (int(loan_account.loan_repayment_every) *
                                            (principle_repayable)))
                                    loan_account.loan_repayment_amount = (
                                        (loan_account.principle_repayment) +
                                        (loan_account.interest_charged))
                                elif (loan_account.total_loan_balance) <\
                                        ((int(loan_account.loan_repayment_every) *
                                            (principle_repayable))):
                                    loan_account.principle_repayment = (loan_account.total_loan_balance)
                                    loan_account.loan_repayment_amount = (
                                        (loan_account.total_loan_balance) + (loan_account.interest_charged))
                                else:
                                    loan_account.principle_repayment = (
                                        (int(loan_account.loan_repayment_every) *
                                            (principle_repayable)) + (lastmonth_bal))
                                    loan_account.loan_repayment_amount = (
                                        (loan_account.principle_repayment) +
                                        (loan_account.interest_charged))
    return loan_account


@login_required
def receipts_deposit(request):
    form = ReceiptForm()
    if request.method == 'POST':
        form = ReceiptForm(request.POST)
        if form.is_valid():
            client = form.client
            client_group = form.client_group
            var_demand_loanprinciple_amount_atinstant = 0
            var_demand_loaninterest_amount_atinstant = 0
            if form.cleaned_data.get("sharecapital_amount"):
                client.sharecapital_amount += \
                    (form.cleaned_data.get("sharecapital_amount", 0))
            if form.cleaned_data.get("entrancefee_amount"):
                client.entrancefee_amount += \
                    (form.cleaned_data.get("entrancefee_amount", 0))
            if form.cleaned_data.get("membershipfee_amount"):
                client.membershipfee_amount += \
                    (form.cleaned_data.get("membershipfee_amount", 0))
            if form.cleaned_data.get("bookfee_amount"):
                client.bookfee_amount += \
                    (form.cleaned_data.get("bookfee_amount", 0))

            if form.loan_account:
                # personal
                loan_account = form.loan_account
                if form.cleaned_data.get("loan_account_no"):
                    if form.cleaned_data.get("loanprocessingfee_amount"):
                        loan_account.loanprocessingfee_amount += \
                            (form.cleaned_data.get("loanprocessingfee_amount", 0))
                if loan_account.status == "Approved":
                    if (loan_account.total_loan_balance)\
                       or (loan_account.interest_charged)\
                       or (loan_account.loan_repayment_amount)\
                       or (loan_account.principle_repayment):
                        var_demand_loanprinciple_amount_atinstant = \
                            (loan_account.principle_repayment)
                        var_demand_loaninterest_amount_atinstant = \
                            (loan_account.interest_charged)
            if form.group_loan_account:
                # group
                group_loan_account = form.group_loan_account
                if form.cleaned_data.get("group_loan_account_no"):
                    if form.cleaned_data.get("loanprocessingfee_amount"):
                        group_loan_account.loanprocessingfee_amount += \
                            (form.cleaned_data.get("loanprocessingfee_amount"), 0)
                if group_loan_account.status == "Approved":
                    if (group_loan_account.total_loan_balance)\
                       or (group_loan_account.interest_charged)\
                       or (group_loan_account.loan_repayment_amount)\
                       or (group_loan_account.principle_repayment):
                        var_demand_loanprinciple_amount_atinstant = \
                            (form.group_member_loan_account.principle_repayment)
                        var_demand_loaninterest_amount_atinstant = \
                            (form.group_member_loan_account.interest_charged)

            if form.savings_account:
                savings_account = form.savings_account
                if form.cleaned_data.get("savingsdeposit_thrift_amount"):
                    # personal
                    savings_account.savings_balance += \
                        (form.cleaned_data.get("savingsdeposit_thrift_amount"))
                    savings_account.total_deposits += \
                        (form.cleaned_data.get("savingsdeposit_thrift_amount"))

                if form.cleaned_data.get('recurring_deposit_account_no'):
                    recurring_deposit_account = RecurringDeposits.objects.filter(
                        reccuring_deposit_number=form.cleaned_data.get('recurring_deposit_account_no')
                    ).first()
                    if recurring_deposit_account:
                        if form.cleaned_data.get('recurringdeposit_amount'):
                            if int(recurring_deposit_account.number_of_payments) <= int(recurring_deposit_account.recurring_deposit_period):
                                if d(recurring_deposit_account.recurring_deposit_amount) == d(form.cleaned_data.get('recurringdeposit_amount')):
                                    savings_account.recurringdeposit_amount += \
                                        (form.cleaned_data.get('recurringdeposit_amount'))
                                    recurring_deposit_account.number_of_payments += 1
                                    if int(recurring_deposit_account.number_of_payments) == int(recurring_deposit_account.recurring_deposit_period):
                                        recurring_deposit_account.status = 'Paid'
                                    recurring_deposit_account.save()
                                    recurring_deposit_account = recurring_deposit_account

                if form.cleaned_data.get('fixed_deposit_account_no'):
                    fixed_deposit_account = FixedDeposits.objects.filter(
                        fixed_deposit_number=form.cleaned_data.get('fixed_deposit_account_no')
                    ).first()
                    if fixed_deposit_account:
                        if form.cleaned_data.get('fixeddeposit_amount'):
                            if d(fixed_deposit_account.fixed_deposit_amount) == d(form.cleaned_data.get('fixeddeposit_amount')):
                                savings_account.fixeddeposit_amount += \
                                    (form.cleaned_data.get('fixeddeposit_amount'))
                                fixed_deposit_account.status = 'Paid'
                                fixed_deposit_account.save()
                                fixed_deposit_account = fixed_deposit_account

            if form.group_savings_account:
                # group
                group_savings_account = form.group_savings_account
                if form.cleaned_data.get("savingsdeposit_thrift_amount"):
                    group_savings_account.savings_balance += \
                        (form.cleaned_data.get("savingsdeposit_thrift_amount"))
                    group_savings_account.total_deposits += \
                        (form.cleaned_data.get("savingsdeposit_thrift_amount"))

            if form.cleaned_data.get("insurance_amount"):
                client.insurance_amount += (form.cleaned_data.get("insurance_amount", 0))

            if form.cleaned_data.get("loanprinciple_amount") \
               or (form.cleaned_data.get("loaninterest_amount")) != 0:
                if form.loan_account:
                    loan_account = loan_valid(form, loan_account)
                elif form.group_loan_account:
                    group_member_loan_account = form.group_member_loan_account
                    group_loan_account = loan_valid(form, group_member_loan_account)
            if form.cleaned_data.get("sharecapital_amount") or\
                    form.cleaned_data.get("entrancefee_amount") or\
                    form.cleaned_data.get("membershipfee_amount") or\
                    form.cleaned_data.get("bookfee_amount") or\
                    form.cleaned_data.get("loanprocessingfee_amount") or\
                    form.cleaned_data.get("savingsdeposit_thrift_amount") or\
                    form.cleaned_data.get("fixeddeposit_amount") or\
                    form.cleaned_data.get("recurringdeposit_amount") or\
                    form.cleaned_data.get("loanprinciple_amount") or\
                    form.cleaned_data.get("insurance_amount") or\
                    form.cleaned_data.get("loaninterest_amount") != 0:
                receipt_number = form.cleaned_data.get("receipt_number")
                branch = Branch.objects.get(id=form.data.get("branch"))
                date = form.cleaned_data.get("date")
                receipt = Receipts.objects.create(
                    date=date,
                    branch=branch,
                    receipt_number=receipt_number,
                    client=client,
                    group=client_group,
                    staff=request.user
                )
                if form.cleaned_data.get("sharecapital_amount"):
                    receipt.sharecapital_amount = form.cleaned_data.get("sharecapital_amount")
                if form.cleaned_data.get("entrancefee_amount"):
                    receipt.entrancefee_amount = form.cleaned_data.get("entrancefee_amount")
                if form.cleaned_data.get("membershipfee_amount"):
                    receipt.membershipfee_amount = form.cleaned_data.get("membershipfee_amount")
                if form.cleaned_data.get("bookfee_amount"):
                    receipt.bookfee_amount = form.cleaned_data.get("bookfee_amount")
                if form.cleaned_data.get("loanprocessingfee_amount"):
                    receipt.loanprocessingfee_amount = form.cleaned_data.get("loanprocessingfee_amount")
                    if form.loan_account:
                        receipt.member_loan_account = loan_account
                    if form.group_loan_account:
                        receipt.group_loan_account = group_loan_account
                if form.cleaned_data.get("savingsdeposit_thrift_amount"):
                    receipt.savingsdeposit_thrift_amount = form.cleaned_data.get("savingsdeposit_thrift_amount")
                    receipt.savings_balance_atinstant = savings_account.savings_balance
                if form.savings_account:
                    if form.cleaned_data.get('fixed_deposit_account_no') and form.cleaned_data.get("fixeddeposit_amount"):
                        receipt.fixed_deposit_account = FixedDeposits.objects.filter(
                            fixed_deposit_number=form.cleaned_data.get('fixed_deposit_account_no')).first()
                    if form.cleaned_data.get("fixeddeposit_amount"):
                        receipt.fixeddeposit_amount = form.cleaned_data.get("fixeddeposit_amount")
                    if form.cleaned_data.get("recurringdeposit_amount") and form.cleaned_data.get('recurring_deposit_account_no'):
                        receipt.recurring_deposit_account = RecurringDeposits.objects.filter(
                            reccuring_deposit_number=form.cleaned_data.get('recurring_deposit_account_no')).first()
                    if form.cleaned_data.get("recurringdeposit_amount"):
                        receipt.recurringdeposit_amount = form.cleaned_data.get("recurringdeposit_amount")
                if form.cleaned_data.get("insurance_amount"):
                    receipt.insurance_amount = form.cleaned_data.get("insurance_amount")
                if form.cleaned_data.get("loanprinciple_amount"):
                    receipt.loanprinciple_amount = form.cleaned_data.get("loanprinciple_amount")
                    if form.loan_account:
                        receipt.member_loan_account = loan_account
                    if form.group_loan_account:
                        receipt.group_loan_account = form.group_loan_account
                if form.cleaned_data.get("loaninterest_amount") != 0:
                    receipt.loaninterest_amount = form.cleaned_data.get("loaninterest_amount")
                    if form.loan_account:
                        receipt.member_loan_account = loan_account
                    if form.group_loan_account:
                        receipt.group_loan_account = form.group_loan_account
                if form.loan_account:
                    receipt.demand_loanprinciple_amount_atinstant = var_demand_loanprinciple_amount_atinstant
                    receipt.demand_loaninterest_amount_atinstant = var_demand_loaninterest_amount_atinstant
                    receipt.principle_loan_balance_atinstant = loan_account.total_loan_balance
                if form.group_loan_account:
                    receipt.demand_loanprinciple_amount_atinstant = var_demand_loanprinciple_amount_atinstant
                    receipt.demand_loaninterest_amount_atinstant = var_demand_loaninterest_amount_atinstant
                    receipt.principle_loan_balance_atinstant = group_loan_account.total_loan_balance
                # save data
                receipt.save()
                client.save()
                if form.loan_account:
                    if d(loan_account.total_loan_amount_repaid) == d(loan_account.loan_amount) \
                       and d(loan_account.total_loan_balance) == d(0) and d(loan_account.interest_charged) == d(0):
                        loan_account.status = "Closed"
                        loan_account.closed_date = datetime.now().date()
                        if loan_account.client:
                            if loan_account.client.email and loan_account.client.email.strip():
                                send_email_template(
                                    subject="Your application for the Personal Loan (ID: %s) has been Closed." % loan_account.account_no,
                                    template_name="emails/client/loan_closed.html",
                                    receipient=loan_account.client.email,
                                    ctx={
                                        "client": loan_account.client,
                                        "loan_account": loan_account,
                                        "link_prefix": settings.SITE_URL,
                                    },
                                )
                    loan_account.save()
                if form.group_loan_account:
                    if d(group_loan_account.total_loan_amount_repaid) == d(group_loan_account.loan_amount) and \
                       d(group_loan_account.total_loan_balance) == d(0) and d(group_loan_account.interest_charged) == d(0):
                        group_loan_account.status = "Closed"
                    group_loan_account.save()
                    group_member_loan_account = GroupMemberLoanAccount.objects.filter(group_loan_account=form.group_loan_account)
                    if group_member_loan_account:
                        count = 0
                        for group_member in group_member_loan_account:
                            if group_member.status == "Closed":
                                count += 1
                        if count == group_member_loan_account.count():
                            group_loan = LoanAccount.objects.get(id=form.group_loan_account.id)
                            group_loan.status = "Closed"
                            group_loan.interest_charged = 0
                            group_loan.save()
                            for client in group_loan.group.clients.all():
                                if client.email and client.email.strip():
                                    send_email_template(
                                        subject="Group Loan (ID: %s) application has been Closed."
                                                % group_loan.account_no,
                                        template_name="emails/group/loan_closed.html",
                                        receipient=client.email,
                                        ctx={
                                            "client": client,
                                            "loan_account": group_loan,
                                            "link_prefix": settings.SITE_URL,
                                        },
                                    )
                if form.savings_account:
                    savings_account.save()
                if form.group_savings_account:
                    group_savings_account.save()

            data = {"error": False}
        else:
            data = {"error": True, "message": form.errors}
        return JsonResponse(data)
    else:
        branches = Branch.objects.all()
    return render(request, "core/receiptsform.html", {'branches': branches})


def payslip_create_view(request):
    form = PaymentForm()
    if request.method == 'POST':
        form = PaymentForm(request.POST, user=request.user)
        if form.is_valid():
            pay_slip = form.save()
            if pay_slip.loan_account:
                loan_account = LoanAccount.objects.get(id=pay_slip.loan_account.id)
                loan_account.loan_issued_date = pay_slip.date
                loan_account.save()
                group_members = GroupMemberLoanAccount.objects.filter(group_loan_account=pay_slip.loan_account)
                if group_members:
                    group_members.update(loan_issued_date=pay_slip.date)
            data = {"error": False, 'pay_slip': pay_slip.id}
        else:
            data = {"error": True, "errors": form.errors}
        return JsonResponse(data)
    else:
        branches = Branch.objects.all()
    return render(request, "core/paymentform.html", {'branches': branches, 'voucher_types': PAYMENT_TYPES})


def get_group_loan_accounts(request):
    group_name = request.GET.get("group_name", None)
    group_account_number = request.GET.get('group_account_no', None)
    loan_accounts_data = []
    if group_name and group_account_number:
        group_filter = Group.objects.filter(
            name__iexact=group_name,
            account_number=group_account_number)
        if group_filter:
            group = group_filter.first()
            loan_accounts = LoanAccount.objects.filter(group=group, status='Approved', loan_issued_date__isnull=True)
            # if loan_accounts:
            #     for account in loan_accounts:
            #         loan_accounts_data[account.id] = account.account_no
            loan_accounts_data = loan_accounts.values_list("id", "account_no", "loan_amount")
        else:
            return JsonResponse({"error": True,
                                 "data": list(loan_accounts_data)})

    return JsonResponse({"error": False, "data": list(loan_accounts_data)})


def get_member_loan_accounts(request):
    client_name = request.GET.get("client_name", None)
    client_account_number = request.GET.get('client_account_number', None)
    loan_accounts_data = []
    if client_name and client_account_number:
        member_filter = Client.objects.filter(
            first_name__iexact=client_name,
            account_number=client_account_number)
        if member_filter:
            client = member_filter.first()
            loan_accounts = LoanAccount.objects.filter(client=client, status='Approved', loan_issued_date__isnull=True)
            # if loan_accounts:
            #     for account in loan_accounts:
            #         loan_accounts_data[account.id] = account.account_no
            loan_accounts_data = loan_accounts.values_list("id", "account_no", "loan_amount")
        else:
            return JsonResponse({"error": True,
                                 "data": list(loan_accounts_data)})

    return JsonResponse({"error": False, "data": list(loan_accounts_data)})


def client_deposit_accounts_view(request):
    form = ClientDepositsAccountsForm()
    if form.is_valid():
        if form.client:
            fixed_deposit_accounts = []
            recurring_deposit_accounts = []
            if form.pay_type == 'FixedWithdrawal':
                fixed_deposit_accounts = FixedDeposits.objects.filter(
                    client=form.client,
                    status='Paid'
                ).values_list("fixed_deposit_number", "fixed_deposit_amount")
            elif form.pay_type == 'RecurringWithdrawal':
                recurring_deposit_accounts_filter = RecurringDeposits.objects.filter(
                    client=form.client
                ).exclude(number_of_payments=0).exclude(status='Closed')
                recurring_deposit_accounts = \
                    recurring_deposit_accounts_filter.values_list(
                        "reccuring_deposit_number", "recurring_deposit_amount")
        else:
            fixed_deposit_accounts = []
            recurring_deposit_accounts = []
        data = {"error": False,
                "fixed_deposit_accounts": list(fixed_deposit_accounts),
                "recurring_deposit_accounts": list(recurring_deposit_accounts)}
    else:
        data = {"error": True, "errors": form.errors}
    return JsonResponse(data)


def get_fixed_deposit_paid_accounts_view(request):
    client = Client.objects.filter(
        first_name__iexact=request.GET.get('client_name'),
        account_number=request.GET.get('client_account_number')).first()
    form = GetFixedDepositsPaidForm(client=client if client else None)
    if form.is_valid():
        fixed_deposit = form.fixed_deposit_account
        # interest_charged = (fixed_deposit.fixed_deposit_amount * (
        #     fixed_deposit.fixed_deposit_interest_rate / 12)) / 100
        # fixed_deposit_interest_charged = interest_charged * d(
        #     fixed_deposit.fixed_deposit_period)
        # total_amount = \
        #     fixed_deposit.fixed_deposit_amount + fixed_deposit_interest_charged
        current_date = datetime.now().date()
        year_days = 366 if calendar.isleap(current_date.year) else 365
        interest_charged = (fixed_deposit.fixed_deposit_amount * fixed_deposit.fixed_deposit_interest_rate) / (d(year_days) * 100)
        days_to_calculate = (current_date - fixed_deposit.deposited_date).days
        calculated_interest_money_till_date = interest_charged * days_to_calculate
        fixed_deposit_interest_charged = calculated_interest_money_till_date
        total_amount = fixed_deposit.fixed_deposit_amount + calculated_interest_money_till_date
        data = {
            "error": False,
            "fixeddeposit_amount": fixed_deposit.fixed_deposit_amount or 0,
            "interest_charged": round(fixed_deposit_interest_charged, 6),
            'total_amount': round(total_amount, 6)
        }

    else:
        data = {"error": True, "errors": form.errors}
    return JsonResponse(data)


def get_recurring_deposit_paid_accounts_view(request):
    client = Client.objects.filter(
        first_name__iexact=request.GET.get('client_name'),
        account_number=request.GET.get('client_account_number')).first()
    form = GetRecurringDepositsPaidForm(client=client)
    if form.is_valid():
        recurring_deposit = form.recurring_deposit_account
        recurring_deposit_amount = d(recurring_deposit.recurring_deposit_amount) * recurring_deposit.number_of_payments
        # interest_charged = (recurring_deposit_amount * (
        #     recurring_deposit.recurring_deposit_interest_rate / 12)) / 100
        # recurring_deposit_interest_charged = interest_charged * d(
        #     recurring_deposit.recurring_deposit_period)
        # total_amount = \
        #     recurring_deposit_amount + recurring_deposit_interest_charged
        current_date = datetime.now().date()
        year_days = 366 if calendar.isleap(current_date.year) else 365
        interest_charged = (recurring_deposit_amount * recurring_deposit.recurring_deposit_interest_rate) / (d(year_days) * 100)
        days_to_calculate = (current_date - recurring_deposit.deposited_date).days
        recurring_deposit_interest_charged = interest_charged * days_to_calculate
        total_amount = recurring_deposit_amount + recurring_deposit_interest_charged
        data = {
            "error": False,
            "recurringdeposit_amount": recurring_deposit_amount,
            "interest_charged": round(recurring_deposit_interest_charged, 6),
            'total_amount': round(total_amount, 6)
        }
    else:
        data = {"error": True, "errors": form.errors}
    return JsonResponse(data)
