from rest_framework import serializers
from .models import (
    User, StockInfo, StockConcept, StockConceptRel,
    StockDailyKline, StockMinuteKline, StockRealtime,
    UserPortfolio, StockFinancial, SelectionTask, TaskDetail, OperationLog, SysConfig
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class StockInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockInfo
        fields = '__all__'


class StockConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockConcept
        fields = '__all__'


class StockConceptRelSerializer(serializers.ModelSerializer):
    stock_code = serializers.CharField(source='stock.code', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    concept_name = serializers.CharField(source='concept.name', read_only=True)

    class Meta:
        model = StockConceptRel
        fields = ['id', 'stock', 'stock_code', 'stock_name', 'concept', 'concept_name']


class StockDailyKlineSerializer(serializers.ModelSerializer):
    stock_name = serializers.CharField(source='code.name', read_only=True)

    class Meta:
        model = StockDailyKline
        fields = '__all__'


class StockMinuteKlineSerializer(serializers.ModelSerializer):
    stock_name = serializers.CharField(source='code.name', read_only=True)

    class Meta:
        model = StockMinuteKline
        fields = '__all__'


class StockRealtimeSerializer(serializers.ModelSerializer):
    stock_name = serializers.CharField(source='code.name', read_only=True)

    class Meta:
        model = StockRealtime
        fields = '__all__'


class UserPortfolioSerializer(serializers.ModelSerializer):
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    stock_code = serializers.CharField(source='stock.code', read_only=True)

    class Meta:
        model = UserPortfolio
        fields = '__all__'


class StockFinancialSerializer(serializers.ModelSerializer):
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    stock_code = serializers.CharField(source='stock.code', read_only=True)

    class Meta:
        model = StockFinancial
        fields = '__all__'


class TaskDetailSerializer(serializers.ModelSerializer):
    stock_code = serializers.CharField(source='stock.code', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)

    class Meta:
        model = TaskDetail
        fields = '__all__'


class SelectionTaskSerializer(serializers.ModelSerializer):
    details = TaskDetailSerializer(many=True, read_only=True)

    class Meta:
        model = SelectionTask
        fields = '__all__'


class OperationLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = OperationLog
        fields = '__all__'


class SysConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysConfig
        fields = '__all__'
