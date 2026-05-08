from django.core.management.base import BaseCommand
from stocks.models import StockInfo, StockDailyKline
import akshare as ak
from datetime import datetime
import math

class Command(BaseCommand):
    help = '获取股票日K线数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='获取股票数量限制（默认0表示全部）'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            default='20240101',
            help='开始日期（默认20240101）'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            default='20261231',
            help='结束日期（默认20261231）'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        start_date = options['start_date']
        end_date = options['end_date']

        stocks = StockInfo.objects.all()
        if limit > 0:
            stocks = stocks[:limit]

        self.stdout.write(f'开始获取 {stocks.count()} 只股票的日K线数据...')
        self.stdout.write(f'日期范围: {start_date} ~ {end_date}')

        total_count = 0
        error_count = 0

        for stock in stocks:
            try:
                df = ak.stock_zh_a_hist(
                    symbol=stock.code,
                    period='daily',
                    start_date=start_date,
                    end_date=end_date
                )

                if df.empty:
                    continue

                klines = []
                for _, row in df.iterrows():
                    trade_date_str = str(row['日期'])
                    try:
                        trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        continue

                    klines.append(StockDailyKline(
                        code=stock,
                        trade_date=trade_date,
                        open=self._safe_decimal(row.get('开盘')),
                        high=self._safe_decimal(row.get('最高')),
                        low=self._safe_decimal(row.get('最低')),
                        close=self._safe_decimal(row.get('收盘')),
                        volume=self._safe_int(row.get('成交量')),
                        amount=self._safe_decimal(row.get('成交额')),
                        amplitude=self._safe_decimal(row.get('振幅')),
                        turnover_rate=self._safe_decimal(row.get('换手率')),
                        change_amt=self._safe_decimal(row.get('涨跌额')),
                        change_pct=self._safe_decimal(row.get('涨跌幅')),
                    ))

                if klines:
                    StockDailyKline.objects.bulk_create(
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
