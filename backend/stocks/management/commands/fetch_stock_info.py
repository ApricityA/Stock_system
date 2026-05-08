from django.core.management.base import BaseCommand
from stocks.models import StockInfo
import akshare as ak
from datetime import datetime

class Command(BaseCommand):
    help = '获取股票基本信息并保存到数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='获取股票数量限制（默认0表示全部）'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        self.stdout.write(f'开始获取股票信息，限制数量: {limit}')

        df = ak.stock_info_a_code_name()
        if limit > 0:
            df = df.head(limit)

        self.stdout.write('正在获取行业板块映射关系...')
        code_to_sector = self._build_sector_map()

        created_count = 0
        updated_count = 0
        error_count = 0

        for _, row in df.iterrows():
            code = row['code']
            name = row['name']

            try:
                individual_info = ak.stock_individual_info_em(symbol=code)
                info_dict = dict(zip(individual_info['item'], individual_info['value']))

                industry = info_dict.get('行业', '')
                sector = code_to_sector.get(code, '')
                list_date_str = info_dict.get('上市时间', '')
                total_shares = info_dict.get('总股本', None)
                float_shares = info_dict.get('流通股', None)

                if isinstance(total_shares, (int, float)):
                    total_shares = int(total_shares)
                else:
                    total_shares = None

                if isinstance(float_shares, (int, float)):
                    float_shares = int(float_shares)
                else:
                    float_shares = None

                list_date = None
                if list_date_str and str(list_date_str).isdigit() and len(str(list_date_str)) == 8:
                    try:
                        list_date = datetime.strptime(str(list_date_str), '%Y%m%d').date()
                    except ValueError:
                        list_date = None

                stock, created = StockInfo.objects.update_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'industry': industry,
                        'sector': sector,
                        'list_date': list_date,
                        'total_shares': total_shares,
                        'float_shares': float_shares,
                        'status': 'LISTING'
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                self.stdout.write(f'  {code} - {name} | 行业: {industry} | 板块: {sector}')

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.WARNING(f'  {code} - {name} - 获取失败: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'完成！新增: {created_count}, 更新: {updated_count}, 失败: {error_count}'
        ))

    def _build_sector_map(self):
        """构建股票代码到行业板块的映射"""
        code_to_sector = {}
        try:
            industry_df = ak.stock_board_industry_name_em()
            for _, row in industry_df.iterrows():
                industry_name = row['板块名称']
                try:
                    cons_df = ak.stock_board_industry_cons_em(symbol=industry_name)
                    for _, stock_row in cons_df.iterrows():
                        code_to_sector[stock_row['代码']] = industry_name
                except Exception:
                    pass
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'获取行业板块映射失败: {e}'))
        return code_to_sector
