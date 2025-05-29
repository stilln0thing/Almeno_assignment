from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework import status
from datetime import datetime, timedelta
from core.models import Customer, Loan
from .serializers import CustomerRegisterSerializer,LoanEligibilitySerializer

class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(CustomerRegisterSerializer(customer).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = LoanEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)

        # 1. Rule: current debt > approved limit → score = 0
        total_current_loans = sum(loan.loan_amount for loan in loans)
        if total_current_loans > customer.approved_limit:
            credit_score = 0
        else:
            # Credit score out of 100
            credit_score = 100

            # a. EMIs paid on time
            total_emis = sum(loan.tenure for loan in loans) or 1
            paid_emis = sum(loan.emis_paid_on_time for loan in loans)
            on_time_ratio = paid_emis / total_emis
            credit_score -= (1 - on_time_ratio) * 30  # Max 30 pt penalty

            # b. Number of loans taken
            if len(loans) > 5:
                credit_score -= 20

            # c. Loan activity in current year
            current_year = datetime.now().year
            recent_loans = [loan for loan in loans if loan.start_date.year == current_year]
            if recent_loans:
                credit_score += 10

            # d. Loan approved volume
            total_volume = sum(loan.loan_amount for loan in loans)
            credit_score += min(20, total_volume / 100000)  # Max 20 bonus for ₹20L+ loans

            credit_score = max(0, min(100, int(credit_score)))

        # Determine interest rate eligibility
        requested_ir = data['interest_rate']
        corrected_ir = requested_ir
        approved = True

        if credit_score > 50:
            pass  # any rate allowed
        elif 30 < credit_score <= 50:
            if requested_ir < 12:
                corrected_ir = 12
        elif 10 < credit_score <= 30:
            if requested_ir < 16:
                corrected_ir = 16
        else:
            approved = False

        # Calculate monthly EMI using compound interest
        def calculate_emi(p, r, n):
            r = r / (12 * 100)
            return round((p * r * ((1 + r) ** n)) / (((1 + r) ** n) - 1), 2)

        new_emi = calculate_emi(data['loan_amount'], corrected_ir, data['tenure'])
        existing_emi_total = sum(calculate_emi(l.loan_amount, l.interest_rate, l.tenure) for l in loans)
        if (existing_emi_total + new_emi) > 0.5 * customer.monthly_salary:
            approved = False

        return Response({
            "customer_id": customer.customer_id,
            "approval": approved,
            "interest_rate": requested_ir,
            "corrected_interest_rate": corrected_ir,
            "tenure": data['tenure'],
            "monthly_installment": new_emi
        }, status=status.HTTP_200_OK)

class CreateLoanView(APIView):
    def post(self, request):
        serializer = LoanEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        loans = Loan.objects.filter(customer=customer)

        # Rule: current debt > approved limit → reject
        total_current_loans = sum(loan.loan_amount for loan in loans)
        if total_current_loans > customer.approved_limit:
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Loan not approved due to debt exceeding limit.",
                "monthly_installment": None
            }, status=200)

        # Compute credit score (same logic as before)
        credit_score = 100
        total_emis = sum(loan.tenure for loan in loans) or 1
        paid_emis = sum(loan.emis_paid_on_time for loan in loans)
        on_time_ratio = paid_emis / total_emis
        credit_score -= (1 - on_time_ratio) * 30
        if len(loans) > 5:
            credit_score -= 20
        current_year = datetime.now().year
        if any(loan.start_date.year == current_year for loan in loans):
            credit_score += 10
        total_volume = sum(l.loan_amount for l in loans)
        credit_score += min(20, total_volume / 100000)
        credit_score = max(0, min(100, int(credit_score)))

        # Interest rate check
        requested_ir = data['interest_rate']
        corrected_ir = requested_ir
        approved = True

        if credit_score > 50:
            pass
        elif 30 < credit_score <= 50:
            if requested_ir < 12:
                corrected_ir = 12
        elif 10 < credit_score <= 30:
            if requested_ir < 16:
                corrected_ir = 16
        else:
            approved = False

        # EMI check
        def calculate_emi(p, r, n):
            r = r / (12 * 100)
            return round((p * r * ((1 + r) ** n)) / (((1 + r) ** n) - 1), 2)

        new_emi = calculate_emi(data['loan_amount'], corrected_ir, data['tenure'])
        existing_emi_total = sum(calculate_emi(l.loan_amount, l.interest_rate, l.tenure) for l in loans)
        if (existing_emi_total + new_emi) > 0.5 * customer.monthly_salary:
            approved = False

        if not approved:
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Loan not approved due to low credit score or high EMI burden.",
                "monthly_installment": new_emi
            }, status=200)

        # Create Loan
        start_date = datetime.today().date()
        end_date = start_date + timedelta(days=data['tenure'] * 30)

        loan = Loan.objects.create(
            customer=customer,
            loan_amount=data['loan_amount'],
            interest_rate=corrected_ir,
            tenure=data['tenure'],
            monthly_installment=new_emi,
            emis_paid_on_time=0,  # New loan, no EMIs paid yet
            start_date=start_date,
            end_date=end_date
        )

        # Update current debt
        customer.current_debt += data['loan_amount']
        customer.save()

        return Response({
            "loan_id": loan.loan_id,
            "customer_id": customer.customer_id,
            "loan_approved": True,
            "message": "Loan approved successfully.",
            "monthly_installment": new_emi
        }, status=status.HTTP_201_CREATED)
    
class ViewLoanDetail(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.select_related("customer").get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)

        customer = loan.customer
        return Response({
            "loan_id": loan.loan_id,
            "customer": {
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "tenure": loan.tenure
        }, status=status.HTTP_200_OK)