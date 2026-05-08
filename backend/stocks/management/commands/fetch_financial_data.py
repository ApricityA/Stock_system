from django.core.management.base import BaseCommand
from stocks.models import StockInfo, StockFinancial
import akshare as ak
from datetime import datetime
import re

class Command(BaseCommand):
    help = '获取股票财务数据并保存到数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='获取股票数量限制（默认0表示全部）'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        stocks = StockInfo.objects.all()
        if limit > 0:
            stocks = stocks[:limit]

        self.stdout.write(f'开始获取 {stocks.count()} 只股票的财务数据...')

        created_count = 0
        updated_count = 0
        error_count = 0

        for stock in stocks:
            try:
                df = ak.stock_financial_abstract_ths(symbol=stock.code)
                if df.empty:
                    self.stdout.write(self.style.WARNING(f'  {stock.code} - {stock.name} - 无财务数据'))
                    continue

                for _, row in df.iterrows():
                    report_date_str = str(row['报告期'])
                    try:
                        report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            report_date = datetime.strptime(report_date_str, '%Y%m%d').date()
                        except ValueError:
                            continue

                    report_type = self._guess_report_type(report_date)

                    revenue = self._parse_value(row.get('营业总收入'))
                    net_profit = self._parse_value(row.get('净利润'))
                    eps = self._parse_value(row.get('基本每股收益'))
                    roe = self._parse_value(row.get('净资产收益率'))
                    pe = None
                    pb = None

                    financial, created = StockFinancial.objects.update_or_create(
                        stock=stock,
                        report_date=report_date,
                        report_type=report_type,
                        defaults={
                            'revenue': revenue,
                            'net_profit': net_profit,
                            'eps': eps,
                            'roe': roe,
                            'pe': pe,
                            'pb': pb,
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                self.stdout.write(f'  {stock.code} - {stock.name} - 获取 {len(df)} 期财务数据')

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.WARNING(f'  {stock.code} - {stock.name} - 获取失败: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'完成！新增: {created_count}, 更新: {updated_count}, 失败: {error_count}'
        ))

    def _guess_report_type(self, report_date):
        month = report_date.month
        if month == 12:
            return '年报'
        elif month == 6:
            return '半年报'
        else:
            return '季报'

    def _parse_value(self, value):
        if value is None or str(value) == 'False':
            return None
        value_str = str(value).strip()
        if value_str == 'False' or value_str == '':
            return None
        value_str = value_str.replace('亿', '00000000').replace('万', '0000').replace('%', '')
        try:
            return float(value_str)
        except ValueError:
            return None
