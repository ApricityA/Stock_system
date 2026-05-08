from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from datetime import date, timedelta
from .models import (
    StockInfo, StockConcept, StockConceptRel,
    StockDailyKline, StockMinuteKline, StockRealtime,
    UserPortfolio, StockFinancial, SelectionTask, TaskDetail, OperationLog, SysConfig
)
from .serializers import (
    StockInfoSerializer, StockConceptSerializer, StockConceptRelSerializer,
    StockDailyKlineSerializer, StockMinuteKlineSerializer, StockRealtimeSerializer,
    UserPortfolioSerializer, StockFinancialSerializer, SelectionTaskSerializer,
    TaskDetailSerializer, OperationLogSerializer, SysConfigSerializer
)


class StockInfoViewSet(viewsets.ModelViewSet):
    queryset = StockInfo.objects.all()
    serializer_class = StockInfoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['industry', 'sector', 'status']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name', 'list_date', 'created_at']
    ordering = ['code']

    @action(detail=True, methods=['get'])
    def kline(self, request, pk=None):
        stock = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit = int(request.query_params.get('limit', 120))

        klines = stock.daily_klines.all()
        if start_date:
            klines = klines.filter(trade_date__gte=start_date)
        if end_date:
            klines = klines.filter(trade_date__lte=end_date)
        klines = klines.order_by('-trade_date')[:limit]

        serializer = StockDailyKlineSerializer(klines, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def realtime_data(self, request, pk=None):
        stock = self.get_object()
        try:
            realtime = stock.stockrealtime
            serializer = StockRealtimeSerializer(realtime)
            return Response(serializer.data)
        except StockRealtime.DoesNotExist:
            return Response({'detail': 'No realtime data'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def financials(self, request, pk=None):
        stock = self.get_object()
        limit = int(request.query_params.get('limit', 4))
        financials = stock.financials.order_by('-report_date')[:limit]
        serializer = StockFinancialSerializer(financials, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def concepts(self, request, pk=None):
        stock = self.get_object()
        rels = stock.stockconceptrel_set.select_related('concept')
        data = [{'code': r.concept.code, 'name': r.concept.name, 'board_type': r.concept.board_type} for r in rels]
        return Response(data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        keyword = request.query_params.get('q', '').strip()
        if not keyword:
            return Response({'error': 'q parameter is required'}, status=400)

        stocks = StockInfo.objects.filter(
            Q(code__icontains=keyword) | Q(name__icontains=keyword)
        )[:20]
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def hot(self, request):
        limit = int(request.query_params.get('limit', 10))
        stocks = StockInfo.objects.filter(
            status='normal'
        ).select_related('stockrealtime').order_by('-stockrealtime__turnover_rate')[:limit]
        serializer = self.get_serializer(stocks, many=True)
        return Response(serializer.data)


class StockConceptViewSet(viewsets.ModelViewSet):
    queryset = StockConcept.objects.all()
    serializer_class = StockConceptSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['board_type']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def stocks(self, request, pk=None):
        concept = self.get_object()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        offset = (page - 1) * page_size

        rels = StockConceptRel.objects.filter(concept=concept).select_related('stock')[offset:offset+page_size]
        data = [{
            'code': r.stock.code,
            'name': r.stock.name,
            'industry': r.stock.industry,
            'sector': r.stock.sector,
        } for r in rels]

        total = StockConceptRel.objects.filter(concept=concept).count()
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'stocks': data
        })


class StockConceptRelViewSet(viewsets.ModelViewSet):
    queryset = StockConceptRel.objects.all()
    serializer_class = StockConceptRelSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['stock', 'concept']


class StockDailyKlineViewSet(viewsets.ModelViewSet):
    queryset = StockDailyKline.objects.all()
    serializer_class = StockDailyKlineSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['code', 'trade_date']
    ordering_fields = ['trade_date', 'close', 'volume']
    ordering = ['-trade_date']

    @action(detail=False, methods=['get'])
    def range(self, request):
        code = request.query_params.get('code')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit = int(request.query_params.get('limit', 120))

        if not code:
            return Response({'error': 'code parameter is required'}, status=400)

        klines = StockDailyKline.objects.filter(code=code)
        if start_date:
            klines = klines.filter(trade_date__gte=start_date)
        if end_date:
            klines = klines.filter(trade_date__lte=end_date)
        klines = klines.order_by('-trade_date')[:limit]

        serializer = self.get_serializer(klines, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ma(self, request):
        code = request.query_params.get('code')
        days = int(request.query_params.get('days', 60))

        if not code:
            return Response({'error': 'code parameter is required'}, status=400)

        klines = StockDailyKline.objects.filter(code=code).order_by('-trade_date')[:days]
        data = []
        for k in klines:
            item = {
                'trade_date': k.trade_date,
                'close': k.close,
            }
            if k.close:
                item['ma5'] = self._calc_ma(k, 5)
                item['ma10'] = self._calc_ma(k, 10)
                item['ma20'] = self._calc_ma(k, 20)
                item['ma60'] = self._calc_ma(k, 60)
            data.append(item)
        return Response(data)

    def _calc_ma(self, kline, period):
        klines = StockDailyKline.objects.filter(
            code=kline.code,
            trade_date__lte=kline.trade_date
        ).order_by('-trade_date')[:period]
        closes = [k.close for k in klines if k.close]
        if len(closes) < period:
            return None
        return round(sum(closes) / len(closes), 2)


class StockMinuteKlineViewSet(viewsets.ModelViewSet):
    queryset = StockMinuteKline.objects.all()
    serializer_class = StockMinuteKlineSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['code', 'trade_time', 'period']
    ordering_fields = ['trade_time', 'close', 'volume']
    ordering = ['-trade_time']


class StockRealtimeViewSet(viewsets.ModelViewSet):
    queryset = StockRealtime.objects.all()
    serializer_class = StockRealtimeSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['code__name', 'code__code']
    ordering_fields = ['update_time']
    ordering = ['-update_time']

    @action(detail=False, methods=['get'])
    def batch(self, request):
        codes = request.query_params.get('codes', '').split(',')
        codes = [c.strip() for c in codes if c.strip()]
        if not codes:
            return Response({'error': 'codes parameter is required'}, status=400)

        data = StockRealtime.objects.filter(code__in=codes)
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_gainers(self, request):
        limit = int(request.query_params.get('limit', 10))
        data = StockRealtime.objects.filter(
            change_pct__isnull=False
        ).order_by('-change_pct')[:limit]
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_losers(self, request):
        limit = int(request.query_params.get('limit', 10))
        data = StockRealtime.objects.filter(
            change_pct__isnull=False
        ).order_by('change_pct')[:limit]
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_volume(self, request):
        limit = int(request.query_params.get('limit', 10))
        data = StockRealtime.objects.filter(
            volume__isnull=False
        ).order_by('-volume')[:limit]
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)


class UserPortfolioViewSet(viewsets.ModelViewSet):
    queryset = UserPortfolio.objects.all()
    serializer_class = UserPortfolioSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'stock']
    ordering_fields = ['updated_at', 'shares']
    ordering = ['-updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return UserPortfolio.objects.filter(user=user)
        return UserPortfolio.objects.all()


class StockFinancialViewSet(viewsets.ModelViewSet):
    queryset = StockFinancial.objects.all()
    serializer_class = StockFinancialSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['stock', 'report_date', 'report_type']
    ordering_fields = ['report_date']
    ordering = ['-report_date']


class SelectionTaskViewSet(viewsets.ModelViewSet):
    queryset = SelectionTask.objects.all()
    serializer_class = SelectionTaskSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'strategy']
    ordering_fields = ['created_at', 'started_at', 'finished_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        task = self.get_object()
        details = task.details.all()
        serializer = TaskDetailSerializer(details, many=True)
        return Response(serializer.data)


class TaskDetailViewSet(viewsets.ModelViewSet):
    queryset = TaskDetail.objects.all()
    serializer_class = TaskDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['task', 'stock']
    ordering_fields = ['score', 'created_at']
    ordering = ['-score']


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'action']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and not user.is_staff:
            return OperationLog.objects.filter(user=user)
        return OperationLog.objects.all()


class SysConfigViewSet(viewsets.ModelViewSet):
    queryset = SysConfig.objects.all()
    serializer_class = SysConfigSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['config_key', 'description']
    ordering_fields = ['config_key']
    ordering = ['config_key']
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def get_by_key(self, request):
        key = request.query_params.get('key')
        if not key:
            return Response({'error': 'key parameter is required'}, status=400)
        try:
            config = SysConfig.objects.get(config_key=key)
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except SysConfig.DoesNotExist:
            return Response({'error': 'Config not found'}, status=404)
