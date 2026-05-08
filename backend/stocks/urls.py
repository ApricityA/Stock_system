from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StockInfoViewSet, StockConceptViewSet, StockConceptRelViewSet,
    StockDailyKlineViewSet, StockMinuteKlineViewSet, StockRealtimeViewSet,
    UserPortfolioViewSet, StockFinancialViewSet, SelectionTaskViewSet,
    TaskDetailViewSet, OperationLogViewSet, SysConfigViewSet
)

router = DefaultRouter()
router.register(r'stock-info', StockInfoViewSet)
router.register(r'concepts', StockConceptViewSet)
router.register(r'concept-rels', StockConceptRelViewSet)
router.register(r'daily-klines', StockDailyKlineViewSet)
router.register(r'minute-klines', StockMinuteKlineViewSet)
router.register(r'realtime', StockRealtimeViewSet)
router.register(r'portfolios', UserPortfolioViewSet)
router.register(r'financials', StockFinancialViewSet)
router.register(r'selection-tasks', SelectionTaskViewSet)
router.register(r'task-details', TaskDetailViewSet)
router.register(r'operation-logs', OperationLogViewSet)
router.register(r'sys-config', SysConfigViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
