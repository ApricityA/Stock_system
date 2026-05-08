from django.core.management.base import BaseCommand
from stocks.models import StockInfo, StockConcept, StockConceptRel
import akshare as ak

class Command(BaseCommand):
    help = '获取概念板块和行业板块数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='获取板块数量限制（默认0表示全部）'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['concept', 'industry', 'all'],
            default='all',
            help='板块类型（默认全部）'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        board_type = options['type']

        self.stdout.write('开始获取板块数据...')

        if board_type in ('concept', 'all'):
            self._fetch_concept_boards(limit)

        if board_type in ('industry', 'all'):
            self._fetch_industry_boards(limit)

        self.stdout.write(self.style.SUCCESS('板块数据获取完成！'))

    def _fetch_concept_boards(self, limit):
        self.stdout.write('\n[1/2] 获取概念板块...')
        df = ak.stock_board_concept_name_em()
        if limit > 0:
            df = df.head(limit)

        concept_count = 0
        rel_count = 0

        for _, row in df.iterrows():
            concept_code = str(row['板块代码'])
            concept_name = str(row['板块名称'])

            concept, _ = StockConcept.objects.update_or_create(
                code=concept_code,
                defaults={
                    'name': concept_name,
                    'board_type': 'concept',
                }
            )
            concept_count += 1

            try:
                cons_df = ak.stock_board_concept_cons_em(symbol=concept_name)
                stock_codes = cons_df['代码'].tolist()
                stocks = StockInfo.objects.filter(code__in=stock_codes)

                rels = []
                for stock in stocks:
                    rels.append(StockConceptRel(stock=stock, concept=concept))

                if rels:
                    StockConceptRel.objects.bulk_create(rels, ignore_conflicts=True)
                    rel_count += len(rels)

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  {concept_name} - 获取成分股失败: {e}'))

            self.stdout.write(f'  {concept_name} - {concept_code} - {len(cons_df) if "cons_df" in dir() else 0} 只成分股')

        self.stdout.write(f'概念板块: {concept_count} 个, 关联: {rel_count} 条')

    def _fetch_industry_boards(self, limit):
        self.stdout.write('\n[2/2] 获取行业板块...')
        df = ak.stock_board_industry_name_em()
        if limit > 0:
            df = df.head(limit)

        industry_count = 0
        rel_count = 0

        for _, row in df.iterrows():
            industry_code = str(row['板块代码'])
            industry_name = str(row['板块名称'])

            industry, _ = StockConcept.objects.update_or_create(
                code=industry_code,
                defaults={
                    'name': industry_name,
                    'board_type': 'industry',
                }
            )
            industry_count += 1

            try:
                cons_df = ak.stock_board_industry_cons_em(symbol=industry_name)
                stock_codes = cons_df['代码'].tolist()
                stocks = StockInfo.objects.filter(code__in=stock_codes)

                rels = []
                for stock in stocks:
                    rels.append(StockConceptRel(stock=stock, concept=industry))

                if rels:
                    StockConceptRel.objects.bulk_create(rels, ignore_conflicts=True)
                    rel_count += len(rels)

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  {industry_name} - 获取成分股失败: {e}'))

            self.stdout.write(f'  {industry_name} - {industry_code} - {len(cons_df) if "cons_df" in dir() else 0} 只成分股')

        self.stdout.write(f'行业板块: {industry_count} 个, 关联: {rel_count} 条')
