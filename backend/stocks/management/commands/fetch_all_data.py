from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = '获取所有股票相关数据（主表+子表）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='获取股票数量限制（默认0表示全部）'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('开始获取股票数据'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        self.stdout.write('\n[1/4] 获取股票基本信息...')
        call_command('fetch_stock_info', limit=limit)

        self.stdout.write('\n[2/4] 获取财务数据...')
        call_command('fetch_financial_data', limit=limit)

        self.stdout.write('\n[3/4] 获取实时行情...')
        call_command('fetch_realtime_data', limit=limit)

        self.stdout.write('\n[4/4] 获取日K线数据...')
        call_command('fetch_daily_kline', limit=limit)

        self.stdout.write('\n' + self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('所有数据获取完成'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
