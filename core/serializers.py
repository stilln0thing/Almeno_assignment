from rest_framework import serializers
from .models import Customer

class CustomerRegisterSerializer(serializers.ModelSerializer):
    monthly_income = serializers.IntegerField(write_only=True)
    approved_limit = serializers.FloatField(read_only=True)

    class Meta:
        model = Customer
        fields = ('customer_id', 'first_name', 'last_name', 'age', 'monthly_income', 'phone_number', 'approved_limit')

    def create(self, validated_data):
        income = validated_data.pop('monthly_income')
        approved_limit = round(36 * income, -5)
        return Customer.objects.create(approved_limit=approved_limit, monthly_salary=income, **validated_data)

class LoanEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()