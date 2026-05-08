from django.core.management.base import BaseCommand
from stocks.models import StockInfo, StockRealtime
import akshare as ak
import math

class Command(BaseCommand):
    help = '获取股票实时行情数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='获取股票数量限制（默认0表示全部）'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        self.stdout.write('开始获取实时行情数据...')

        stocks = StockInfo.objects.all()
        if limit > 0:
            stocks = stocks[:limit]

        stock_codes = list(stocks.values_list('code', flat=True))
        self.stdout.write(f'主表共有 {len(stock_codes)} 只股票')

        df = ak.stock_zh_a_spot_em()
        df = df[df['代码'].isin(stock_codes)]

        created_count = 0
        updated_count = 0
        error_count = 0

        for _, row in df.iterrows():
            code = row['代码']
            try:
                stock = StockInfo.objects.get(code=code)
            except StockInfo.DoesNotExist:
                continue

            try:
                _, created = StockRealtime.objects.update_or_create(
                    code=stock,
                    defaults={
                        'price': self._safe_decimal(row.get('最新价')),
                        'open': self._safe_decimal(row.get('今开')),
                        'high': self._safe_decimal(row.get('最高')),
                        'low': self._safe_decimal(row.get('最低')),
                        'prev_close': self._safe_decimal(row.get('昨收')),
                        'volume': self._safe_int(row.get('成交量')),
                        'amount': self._safe_decimal(row.get('成交额')),
                        'bid1': self._safe_decimal(row.get('买一')),
                        'bid_vol1': self._safe_int(row.get('买一量')),
                        'bid2': self._safe_decimal(row.get('买二')),
                        'bid_vol2': self._safe_int(row.get('买二量')),
                        'bid3': self._safe_decimal(row.get('买三')),
                        'bid_vol3': self._safe_int(row.get('买三量')),
                        'bid4': self._safe_decimal(row.get('买四')),
                        'bid_vol4': self._safe_int(row.get('买四量')),
                        'bid5': self._safe_decimal(row.get('买五')),
                        'bid_vol5': self._safe_int(row.get('买五量')),
                        'ask1': self._safe_decimal(row.get('卖一')),
                        'ask_vol1': self._safe_int(row.get('卖一量')),
                        'ask2': self._safe_decimal(row.get('卖二')),
                        'ask_vol2': self._safe_int(row.get('卖二量')),
                        'ask3': self._safe_decimal(row.get('卖三')),
                        'ask_vol3': self._safe_int(row.get('卖三量')),
                        'ask4': self._safe_decimal(row.get('卖四')),
                        'ask_vol4': self._safe_int(row.get('卖四量')),
                        'ask5': self._safe_decimal(row.get('卖五')),
                        'ask_vol5': self._safe_int(row.get('卖五量')),
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.WARNING(f'  {code} - 获取失败: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'完成！新增: {created_count}, 更新: {updated_count}, 失败: {error_count}'
        ))

    def _safe_decimal(self, value):
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _safe_int(self, value):
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
