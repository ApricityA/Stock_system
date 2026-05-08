from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


class User(AbstractUser):
    ROLE_CHOICES = [
        ('USER', '普通用户'),
        ('ADMIN', '管理员'),
        ('ANALYST', '分析师'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', '正常'),
        ('INACTIVE', '未激活'),
        ('BANNED', '封禁'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER', verbose_name='角色')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', verbose_name='状态')
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='手机号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StockInfo(models.Model):
    STATUS_CHOICES = [
        ('LISTING', '上市'),
        ('DELISTING', '退市'),
        ('ST', '特别处理'),
        ('PAUSED', '停牌'),
    ]

    code = models.CharField(max_length=10, primary_key=True, verbose_name='股票代码')
    name = models.CharField(max_length=50, verbose_name='股票名称')
    industry = models.CharField(max_length=50, null=True, blank=True, verbose_name='所属行业')
    sector = models.CharField(max_length=50, null=True, blank=True, verbose_name='板块')
    list_date = models.DateField(null=True, blank=True, verbose_name='上市日期')
    total_shares = models.BigIntegerField(null=True, blank=True, verbose_name='总股本')
    float_shares = models.BigIntegerField(null=True, blank=True, verbose_name='流通股本')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='LISTING', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'stock_info'
        verbose_name = '股票信息'
        verbose_name_plural = '股票信息'
        ordering = ['code']
        indexes = [
            models.Index(fields=['name'], name='idx_stock_info_name'),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class StockConcept(models.Model):
    BOARD_TYPE_CHOICES = [
        ('concept', '概念板块'),
        ('industry', '行业板块'),
    ]

    code = models.CharField(max_length=20, unique=True, verbose_name='板块代码')
    name = models.CharField(max_length=50, verbose_name='板块名称')
    board_type = models.CharField(max_length=20, choices=BOARD_TYPE_CHOICES, default='concept', verbose_name='板块类型')
    description = models.TextField(null=True, blank=True, verbose_name='概念描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'stock_concept'
        verbose_name = '概念板块'
        verbose_name_plural = '概念板块'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class StockConceptRel(models.Model):
    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE, to_field='code', verbose_name='股票', db_column='stock_code')
    concept = models.ForeignKey(StockConcept, on_delete=models.CASCADE, to_field='code', verbose_name='概念', db_column='concept_code')

    class Meta:
        db_table = 'stock_concept_rel'
        verbose_name = '股票概念关联'
        verbose_name_plural = '股票概念关联'
        unique_together = ['stock', 'concept']

    def __str__(self):
        return f"{self.stock.code} - {self.concept.name}"


class StockDailyKline(models.Model):
    code = models.ForeignKey(StockInfo, on_delete=models.CASCADE, related_name='daily_klines', verbose_name='股票代码', db_column='code')
    trade_date = models.DateField(verbose_name='交易日期')
    open = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='开盘价')
    high = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='最高价')
    low = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='最低价')
    close = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='收盘价')
    volume = models.BigIntegerField(null=True, blank=True, verbose_name='成交量')
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='成交额')
    amplitude = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='振幅')
    turnover_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='换手率')
    change_amt = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='涨跌额')
    change_pct = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='涨跌幅')

    class Meta:
        db_table = 'stock_daily_kline'
        verbose_name = '日K线数据'
        verbose_name_plural = '日K线数据'
        unique_together = ['code', 'trade_date']
        ordering = ['-trade_date']
        indexes = [
            models.Index(fields=['trade_date'], name='idx_daily_kline_date'),
            models.Index(fields=['code', '-trade_date'], name='idx_daily_kline_code_date'),
        ]

    def __str__(self):
        return f"{self.code_id} - {self.trade_date}"


class StockMinuteKline(models.Model):
    PERIOD_CHOICES = [
        ('1min', '1分钟'),
        ('5min', '5分钟'),
        ('15min', '15分钟'),
        ('30min', '30分钟'),
        ('60min', '60分钟'),
    ]

    code = models.ForeignKey(StockInfo, on_delete=models.CASCADE, related_name='minute_klines', verbose_name='股票代码', db_column='code')
    trade_time = models.DateTimeField(verbose_name='交易时间')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='1min', verbose_name='K线周期')
    open = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='开盘价')
    high = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='最高价')
    low = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='最低价')
    close = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='收盘价')
    volume = models.BigIntegerField(null=True, blank=True, verbose_name='成交量')
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='成交额')

    class Meta:
        db_table = 'stock_minute_kline'
        verbose_name = '分钟K线数据'
        verbose_name_plural = '分钟K线数据'
        unique_together = ['code', 'trade_time', 'period']
        ordering = ['-trade_time']
        indexes = [
            models.Index(fields=['code', '-trade_time'], name='idx_minute_kline_code_time'),
            models.Index(fields=['period'], name='idx_minute_kline_period'),
        ]

    def __str__(self):
        return f"{self.code_id} - {self.trade_time} ({self.period})"


class StockRealtime(models.Model):
    code = models.OneToOneField(StockInfo, on_delete=models.CASCADE, primary_key=True, verbose_name='股票代码', db_column='code')
    price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='最新价')
    open = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='今日开盘价')
    high = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='今日最高价')
    low = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='今日最低价')
    prev_close = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='昨收价')
    volume = models.BigIntegerField(null=True, blank=True, verbose_name='成交量')
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='成交额')

    bid1 = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='买一价')
    bid_vol1 = models.BigIntegerField(null=True, blank=True, verbose_name='买一量')
    bid2 = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='买二价')
    bid_vol2 = models.BigIntegerField(null=True, blank=True, verbose_name='买二量')
    bid3 = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='买三价')
    bid_vol3 = models.BigIntegerField(null=True, blank=True, verbose_name='买三量')
    bid4 = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='买四价')
    bid_vol4 = models.BigIntegerField(null=True, blank=True, verbose_name='买四量')
    bid5 = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='买五价')
    bid_vol5 = models.BigIntegerField(null=True, blank=True, verbose_name='买五量')

    ask1 = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='卖一价')
    ask_vol1 = models.BigIntegerField(null=True, blank=True, verbose_name='卖一量')
    ask2 = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='卖二价')
    ask_vol2 = models.BigIntegerField(null=True, blank=True, verbose_name='卖二量')
    ask3 = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='卖三价')
    ask_vol3 = models.BigIntegerField(null=True, blank=True, verbose_name='卖三量')
    ask4 = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='卖四价')
    ask_vol4 = models.BigIntegerField(null=True, blank=True, verbose_name='卖四量')
    ask5 = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='卖五价')
    ask_vol5 = models.BigIntegerField(null=True, blank=True, verbose_name='卖五量')

    update_time = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')

    class Meta:
        db_table = 'stock_realtime'
        verbose_name = '实时行情'
        verbose_name_plural = '实时行情'

    def __str__(self):
        return f"{self.code_id} - {self.price}"


class UserPortfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios', verbose_name='用户')
    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE, related_name='portfolios', verbose_name='股票')
    shares = models.BigIntegerField(validators=[MinValueValidator(1)], verbose_name='持仓股数')
    available_shares = models.BigIntegerField(default=0, verbose_name='可用股数')
    cost_price = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='成本价')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户持仓'
        verbose_name_plural = '用户持仓'
        unique_together = ['user', 'stock']
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user'], name='idx_portfolio_user'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.stock.code} ({self.shares}股)"


class StockFinancial(models.Model):
    REPORT_TYPE_CHOICES = [
        ('年报', '年报'),
        ('半年报', '半年报'),
        ('季报', '季报'),
    ]

    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE, related_name='financials', verbose_name='股票', db_column='stock_code')
    report_date = models.DateField(verbose_name='报告期')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, null=True, blank=True, verbose_name='报告类型')
    revenue = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='营业收入')
    net_profit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='净利润')
    eps = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='每股收益')
    roe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='净资产收益率')
    pe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='市盈率')
    pb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='市净率')

    class Meta:
        db_table = 'stock_financial'
        verbose_name = '财务数据'
        verbose_name_plural = '财务数据'
        unique_together = ['stock', 'report_date', 'report_type']
        ordering = ['-report_date']
        indexes = [
            models.Index(fields=['stock', '-report_date'], name='idx_financial_code_date'),
        ]

    def __str__(self):
        return f"{self.stock.code} - {self.report_date} ({self.report_type})"


class SelectionTask(models.Model):
    STATUS_CHOICES = [
        ('PENDING', '等待'),
        ('RUNNING', '执行中'),
        ('COMPLETED', '完成'),
        ('FAILED', '失败'),
    ]

    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='任务名称')
    strategy = models.CharField(max_length=50, null=True, blank=True, verbose_name='选股策略')
    params = models.JSONField(null=True, blank=True, verbose_name='策略参数')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')

    class Meta:
        verbose_name = '选股任务'
        verbose_name_plural = '选股任务'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_task_status'),
            models.Index(fields=['-created_at'], name='idx_task_created_at'),
        ]

    def __str__(self):
        return f"{self.name or self.strategy} ({self.get_status_display()})"


class TaskDetail(models.Model):
    task = models.ForeignKey(SelectionTask, on_delete=models.CASCADE, related_name='details', verbose_name='任务')
    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name='股票')
    score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='评分')
    reason = models.TextField(null=True, blank=True, verbose_name='入选原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '选股结果明细'
        verbose_name_plural = '选股结果明细'
        ordering = ['-score']
        indexes = [
            models.Index(fields=['stock'], name='idx_detail_stock'),
        ]

    def __str__(self):
        return f"{self.task.name} - {self.stock.code if self.stock else 'N/A'}"


class OperationLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', '登录'),
        ('LOGOUT', '登出'),
        ('SELECT_STOCK', '选股'),
        ('EXPORT', '导出'),
        ('IMPORT', '导入'),
        ('DELETE', '删除'),
        ('UPDATE', '更新'),
        ('CREATE', '创建'),
        ('VIEW', '查看'),
        ('DOWNLOAD', '下载'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs', verbose_name='操作者')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, null=True, blank=True, verbose_name='操作类型')
    target = models.CharField(max_length=100, null=True, blank=True, verbose_name='操作对象')
    detail = models.JSONField(null=True, blank=True, verbose_name='操作详情')
    ip_addr = models.CharField(max_length=50, null=True, blank=True, verbose_name='IP地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_log_user_time'),
            models.Index(fields=['action'], name='idx_log_action'),
        ]

    def __str__(self):
        return f"{self.action} - {self.target} ({self.created_at})"


class SysConfig(models.Model):
    config_key = models.CharField(max_length=50, unique=True, verbose_name='配置键名')
    config_value = models.JSONField(verbose_name='配置值')
    description = models.TextField(null=True, blank=True, verbose_name='配置说明')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['config_key']

    def __str__(self):
        return f"{self.config_key} ({self.description or 'N/A'})"

    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值"""
        try:
            config = cls.objects.get(config_key=key)
            return config.config_value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_config(cls, key, value, description=None):
        """设置配置值"""
        config, created = cls.objects.update_or_create(
            config_key=key,
            defaults={'config_value': value, 'description': description}
        )
        return config
