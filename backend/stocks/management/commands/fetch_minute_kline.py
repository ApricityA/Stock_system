from django.core.management.base import BaseCommand
from stocks.models import StockInfo, StockMinuteKline
import akshare as ak
from datetime import datetime
import math

class Command(BaseCommand):
    help = '获取股票分钟K线数据（1分钟/5分钟）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='获取股票数量限制（默认0表示全部）'
        )
        parser.add_argument(
            '--period',
            type=str,
            choices=['1', '5'],
            default='5',
            help='K线周期（默认5分钟）'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=5,
            help='获取最近几天数据（默认5天）'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        period = options['period']
        days = options['days']

        stocks = StockInfo.objects.all()
        if limit > 0:
            stocks = stocks[:limit]

        period_map = {'1': '1min', '5': '5min'}
        db_period = period_map[period]

        self.stdout.write(f'开始获取 {stocks.count()} 只股票的{db_period}K线数据...')
        self.stdout.write(f'获取最近 {days} 天数据')

        total_count = 0
        error_count = 0

        for stock in stocks:
            try:
                df = ak.stock_zh_a_hist_min_em(
                    symbol=stock.code,
                    period=period,
                    adjust=''
                )

                if df.empty:
                    continue

                klines = []
                for _, row in df.iterrows():
                    time_str = str(row['时间'])
                    try:
                        trade_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        continue

                    klines.append(StockMinuteKline(
                        code=stock,
                        trade_time=trade_time,
                        period=db_period,
                        open=self._safe_decimal(row.get('开盘')),
                        high=self._safe_decimal(row.get('最高')),
                        low=self._safe_decimal(row.get('最低')),
                        close=self._safe_decimal(row.get('收盘')),
                        volume=self._safe_int(row.get('成交量')),
                        amount=self._safe_decimal(row.get('成交额')),
                    ))

                if klines:
                    StockMinuteKline.objects.bulk_create(
                        klines,
                        ignore_conflicts=True,
                        batch_size=500
                    )
                    total_count += len(klines)

                self.stdout.write(f'  {stock.code} - {stock.name} - {len(klines)} 条')

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.WARNING(f'  {stock.code} - {stock.name} - 获取失败: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'完成！新增: {total_count} 条, 失败: {error_count} 只股票'
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
