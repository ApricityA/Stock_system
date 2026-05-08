-- ============================================================
-- 股票系统数据库架构 - 优化版
-- 数据库：PostgreSQL 16
-- 设计者：GLM + 明道（AI 助手）
-- 日期：2026-05-07
-- ============================================================
--
-- 本文件包含完整的数据库表结构设计，按以下顺序：
-- 1. 基础配置与扩展
-- 2. 枚举类型定义
-- 3. 用户与权限系统
-- 4. 股票基础信息
-- 5. 板块与概念
-- 6. 日K线数据（按年分区，自动创建）
-- 7. 分钟K线数据（按月分区，自动创建）
-- 8. 实时行情快照
-- 9. 用户持仓
-- 10. 财务数据
-- 11. 系统任务与日志
-- 12. 系统配置表
--
-- 使用方式：
-- docker exec -it stock_postgres psql -U stockuser -d stockdb -f /docker-entrypoint-initdb.d/init.sql
-- ============================================================

-- ============================================================
-- 1. 基础配置与扩展
-- ============================================================

-- 启用 UUID 生成扩展（用于生成唯一标识符，未来扩展用）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建通用自动更新时间触发器函数
-- 原理：任何表如果有 updated_at 字段，在 UPDATE 之前自动更新为当前时间
-- 用法：在建表后创建触发器即可，不用每张表都写一次
CREATE OR REPLACE FUNCTION update_timestamp_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 2. 枚举类型定义
-- ============================================================

-- 用户角色类型
CREATE TYPE user_role AS ENUM ('USER', 'ADMIN', 'ANALYST');

-- 用户状态类型
CREATE TYPE user_status AS ENUM ('ACTIVE', 'INACTIVE', 'BANNED');

-- 股票状态类型
CREATE TYPE stock_status AS ENUM ('LISTING', 'DELISTING', 'ST', 'PAUSED');

-- K线周期类型
CREATE TYPE kline_period AS ENUM ('1min', '5min', '15min', '30min', '60min');

-- 报告类型
CREATE TYPE report_type AS ENUM ('年报', '半年报', '一季报', '二季报', '三季报');

-- 任务状态类型
CREATE TYPE task_status AS ENUM ('PENDING', 'RUNNING', 'SUCCESS', 'FAILED', 'CANCELLED');

-- 操作类型
CREATE TYPE action_type AS ENUM (
    'LOGIN', 'LOGOUT', 'SELECT_STOCK', 'EXPORT', 'IMPORT', 
    'DELETE', 'UPDATE', 'CREATE', 'VIEW', 'DOWNLOAD'
);

-- 策略类型
CREATE TYPE strategy_type AS ENUM (
    'MA_CROSS', 'MACD', 'RSI', 'KDJ', 'BOLL', 'CUSTOM'
);


-- ============================================================
-- 3. 用户与权限系统
-- ============================================================

-- 用户表：系统用户信息，支持角色分级
-- 说明：
--   - username/email/phone 都是唯一约束，防止重复注册
--   - role 分三种：USER（普通用户）、ADMIN（管理员）、ANALYST（分析师）
--   - status 控制账号状态：ACTIVE（正常）、INACTIVE（未激活）、BANNED（封禁）
--   - password_hash 存加密后的密码，绝不明文存储
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,                      -- 自增主键
    username        VARCHAR(50) UNIQUE NOT NULL,           -- 用户名，唯一
    password_hash   VARCHAR(255) NOT NULL,                  -- 密码的 bcrypt/scrypt 哈希值
    email           VARCHAR(100) UNIQUE,                    -- 邮箱，唯一
    phone           VARCHAR(20) UNIQUE,                     -- 手机号，唯一
    role            user_role DEFAULT 'USER',               -- 角色枚举
    status          user_status DEFAULT 'ACTIVE',           -- 状态枚举
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,  -- 创建时间（带时区）
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP   -- 更新时间（自动更新）
);

-- 触发器：当 users 表的任意行被 UPDATE 时，自动更新 updated_at
-- 原理：BEFORE UPDATE 触发器在数据写入前修改 updated_at 字段
CREATE TRIGGER trigger_users_update
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_timestamp_trigger();


-- ============================================================
-- 4. 股票基础信息
-- ============================================================

-- 股票信息表：记录 A 股所有股票的基本信息
-- 说明：
--   - code 是主键，格式如 "600519.SH"（上海）或 "000001.SZ"（深圳）
--   - industry 行业分类（如 "白酒"），sector 板块分类（如 "消费"）
--   - list_date 上市日期，帮助判断股票历史长度
--   - total_shares 总股本（股），float_shares 流通股本（股）
--   - status 状态：LISTING（上市）、DELISTING（退市）、ST（特别处理）、PAUSED（停牌）
CREATE TABLE stock_info (
    code            VARCHAR(10) PRIMARY KEY,               -- 股票代码，如 "600519.SH"
    name            VARCHAR(50) NOT NULL,                  -- 股票名称，如 "贵州茅台"
    industry        VARCHAR(50),                           -- 所属行业，如 "白酒"
    sector          VARCHAR(50),                           -- 板块，如 "消费"
    list_date       DATE,                                   -- 上市日期
    total_shares    BIGINT,                                 -- 总股本（股）
    float_shares    BIGINT,                                 -- 流通股本（股）
    status          stock_status DEFAULT 'LISTING',         -- 状态枚举
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trigger_stock_info_update
BEFORE UPDATE ON stock_info
FOR EACH ROW EXECUTE FUNCTION update_timestamp_trigger();

-- 为股票名称模糊搜索建索引
-- 原因：用户经常搜索"茅台"这样的中文名称，模糊搜索需要走索引才快
-- 注意：MySQL 用 LIKE，PostgreSQL 用 gin_trgm_ops 支持模糊匹配
CREATE INDEX idx_stock_info_name ON stock_info(name);


-- ============================================================
-- 5. 板块与概念
-- ============================================================

-- 概念板块表：记录题材概念（如 "华为概念"、"新能源汽车"）
-- 说明：
--   - 一个概念可以被多只股票关联（如 "华为概念" 有 100 只股票）
--   - description 存放概念的详细描述（可选）
CREATE TABLE stock_concept (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(50) UNIQUE NOT NULL,            -- 概念名称，唯一
    description     TEXT,                                   -- 概念描述（可选）
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 股票-概念关联表：多对多关系
-- 说明：
--   - 一只股票可以属于多个概念（如茅台同时属于 "白酒" 和 "上证50"）
--   - ON DELETE CASCADE：当股票或概念被删除时，自动删除关联记录
--   - 无需单独建主键，两个外键组合就是主键
CREATE TABLE stock_concept_rel (
    stock_code      VARCHAR(10) REFERENCES stock_info(code) ON DELETE CASCADE,  -- 股票代码
    concept_id      INT REFERENCES stock_concept(id) ON DELETE CASCADE,       -- 概念 ID
    PRIMARY KEY (stock_code, concept_id)                                       -- 联合主键
);


-- ============================================================
-- 6. 日K线数据（按年分区，自动创建）
-- ============================================================

-- 日K线表：记录每只股票每天的开盘、收盘、最高、最低、成交量等
-- 说明：
--   - 核心数据表，数据量最大（约 4000 股票 × 250 交易日/年 ≈ 100 万条/年）
--   - PARTITION BY RANGE 按日期范围分区：查询某个时间段的 K 线只扫对应分区
--   - 分区好处：10 年历史数据查询，只扫目标年份分区，不扫全表
--   - 字段命名：amount = 成交额（元），amplitude = 振幅（%），turnover_rate = 换手率（%）
CREATE TABLE stock_daily_kline (
    code            VARCHAR(10) NOT NULL REFERENCES stock_info(code) ON DELETE CASCADE,  -- 股票代码，外键关联
    trade_date      DATE NOT NULL,                         -- 交易日期（如 2026-05-07）
    open            NUMERIC(10, 3),                        -- 开盘价
    high            NUMERIC(10, 3),                        -- 最高价
    low             NUMERIC(10, 3),                        -- 最低价
    close           NUMERIC(10, 3),                        -- 收盘价
    volume          BIGINT,                                 -- 成交量（股）
    amount          NUMERIC(20, 2),                        -- 成交额（元）
    amplitude       NUMERIC(10, 2),                        -- 振幅 = (最高-最低)/昨收×100%
    turnover_rate   NUMERIC(10, 2),                        -- 换手率 = 成交量/流通股本×100%
    change_amt      NUMERIC(10, 3),                        -- 涨跌额 = 收盘价 - 昨收价
    change_pct      NUMERIC(10, 2),                        -- 涨跌幅 = (收盘价-昨收)/昨收×100%
    PRIMARY KEY (code, trade_date),                         -- 联合主键：代码+日期唯一
    CHECK (high IS NULL OR low IS NULL OR high >= low),    -- 价格合理性检查
    CHECK (high IS NULL OR open IS NULL OR high >= open),  -- 最高价 >= 开盘价
    CHECK (high IS NULL OR close IS NULL OR high >= close),-- 最高价 >= 收盘价
    CHECK (low IS NULL OR open IS NULL OR low <= open),    -- 最低价 <= 开盘价
    CHECK (low IS NULL OR close IS NULL OR low <= close)   -- 最低价 <= 收盘价
) PARTITION BY RANGE (trade_date);                         -- 按交易日期分区

-- 父表索引：按交易日期查（如"近30天"）会用到
CREATE INDEX idx_daily_kline_date ON stock_daily_kline(trade_date);

-- 按股票代码+日期倒序索引（查询某股票历史K线最常用）
CREATE INDEX idx_daily_kline_code_date ON stock_daily_kline(code, trade_date DESC);


-- ============================================================
-- 7. 分钟K线数据（按月分区，自动创建）
-- ============================================================

-- 分钟K线表：记录每只股票每分钟的数据（1分钟K线和5分钟K线）
-- 说明：
--   - 数据量极大：1 只股票每天约 240 条（每分钟1条），4000 只股票 × 240 = 96 万条/天
--   - 按月分区：每月一个分区，过期数据可归档到冷存储
--   - period 字段区分周期：'1min'（1分钟K线）、'5min'（5分钟K线）
--   - trade_time 精确到秒（TIMESTAMPTZ），以便区分盘中连续数据
CREATE TABLE stock_minute_kline (
    code            VARCHAR(10) NOT NULL REFERENCES stock_info(code) ON DELETE CASCADE,  -- 股票代码，外键关联
    trade_time      TIMESTAMPTZ NOT NULL,                   -- 交易时间（精确到秒）
    period          kline_period DEFAULT '1min',            -- K线周期枚举
    open            NUMERIC(10, 3),                        -- 开盘价
    high            NUMERIC(10, 3),                        -- 最高价
    low             NUMERIC(10, 3),                        -- 最低价
    close           NUMERIC(10, 3),                        -- 收盘价
    volume          BIGINT,                                 -- 成交量（股）
    amount          NUMERIC(20, 2),                        -- 成交额（元）
    PRIMARY KEY (code, trade_time, period),                 -- 联合主键：代码+时间+周期
    CHECK (high IS NULL OR low IS NULL OR high >= low),    -- 价格合理性检查
    CHECK (high IS NULL OR open IS NULL OR high >= open),  -- 最高价 >= 开盘价
    CHECK (high IS NULL OR close IS NULL OR high >= close),-- 最高价 >= 收盘价
    CHECK (low IS NULL OR open IS NULL OR low <= open),    -- 最低价 <= 开盘价
    CHECK (low IS NULL OR close IS NULL OR low <= close)   -- 最低价 <= 收盘价
) PARTITION BY RANGE (trade_time);                         -- 按交易时间分区

-- 父表索引：按股票代码+时间倒序查（查最近数据会用）
CREATE INDEX idx_minute_kline_code_time ON stock_minute_kline(code, trade_time DESC);

-- 按周期筛选索引（查询特定周期K线用）
CREATE INDEX idx_minute_kline_period ON stock_minute_kline(period);


-- ============================================================
-- 自动分区管理函数
-- ============================================================

-- 创建日K线单个年份分区函数
-- 用法：SELECT create_daily_partition_if_not_exists('2027-01-01');
CREATE OR REPLACE FUNCTION create_daily_partition_if_not_exists(
    p_start_date    DATE                                    -- 分区起始日期
) RETURNS VOID AS $$
DECLARE
    v_partition_name    TEXT;                               -- 分区名，如 stock_daily_kline_2027
    v_end_date          DATE;                               -- 分区结束日期（起始+1年）
BEGIN
    v_partition_name := 'stock_daily_kline_' || EXTRACT(YEAR FROM p_start_date)::TEXT;
    v_end_date := p_start_date + INTERVAL '1 year';

    IF NOT EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = v_partition_name
          AND n.nspname = 'public'
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF stock_daily_kline FOR VALUES FROM (%L) TO (%L)',
            v_partition_name,
            p_start_date,
            v_end_date
        );
        RAISE NOTICE 'Created daily partition: %', v_partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 批量创建日K线分区函数（支持一次创建多个年份分区）
-- 用法：SELECT create_daily_partitions('2027-01-01', 3);  -- 创建未来3年分区
CREATE OR REPLACE FUNCTION create_daily_partitions(
    p_start_date    DATE,                                   -- 分区起始日期
    p_years         INT DEFAULT 1                           -- 创建年份数量
) RETURNS VOID AS $$
DECLARE
    v_current_date  DATE := p_start_date;
    v_i             INT;
BEGIN
    FOR v_i IN 1..p_years LOOP
        PERFORM create_daily_partition_if_not_exists(v_current_date);
        v_current_date := v_current_date + INTERVAL '1 year';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 创建分钟K线单个月份分区函数
-- 用法：SELECT create_minute_partition_if_not_exists('stock_minute_kline', '2026-06-01');
CREATE OR REPLACE FUNCTION create_minute_partition_if_not_exists(
    p_table_base    TEXT,                                   -- 表名（不含分区后缀）
    p_start_date    DATE                                    -- 分区起始日期
) RETURNS VOID AS $$
DECLARE
    v_partition_name    TEXT;                               -- 分区名，如 stock_minute_kline_2026_06
    v_end_date          DATE;                               -- 分区结束日期（起始+1个月）
BEGIN
    v_partition_name := p_table_base || '_' || to_char(p_start_date, 'YYYY_MM');
    v_end_date := p_start_date + INTERVAL '1 month';

    IF NOT EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = v_partition_name
          AND n.nspname = 'public'
    ) THEN
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
            v_partition_name,
            p_table_base,
            p_start_date,
            v_end_date
        );
        RAISE NOTICE 'Created minute partition: %', v_partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 批量创建分钟K线分区函数（支持一次创建多个月份分区）
-- 用法：SELECT create_minute_partitions('stock_minute_kline', '2026-06-01', 6);  -- 创建未来6个月分区
CREATE OR REPLACE FUNCTION create_minute_partitions(
    p_table_base    TEXT,                                   -- 表名（不含分区后缀）
    p_start_date    DATE,                                   -- 分区起始日期
    p_months        INT DEFAULT 1                           -- 创建月份数量
) RETURNS VOID AS $$
DECLARE
    v_current_date  DATE := p_start_date;
    v_i             INT;
BEGIN
    FOR v_i IN 1..p_months LOOP
        PERFORM create_minute_partition_if_not_exists(p_table_base, v_current_date);
        v_current_date := v_current_date + INTERVAL '1 month';
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 自动创建日K线未来年份分区
CREATE OR REPLACE FUNCTION auto_create_daily_partitions()
RETURNS VOID AS $$
DECLARE
    v_next_year DATE := (DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '1 year')::DATE;
BEGIN
    PERFORM create_daily_partition_if_not_exists(v_next_year);
END;
$$ LANGUAGE plpgsql;

-- 自动创建分钟K线未来月份分区
CREATE OR REPLACE FUNCTION auto_create_minute_partitions()
RETURNS VOID AS $$
DECLARE
    v_next_month DATE := (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month')::DATE;
BEGIN
    PERFORM create_minute_partition_if_not_exists('stock_minute_kline', v_next_month);
END;
$$ LANGUAGE plpgsql;

-- 初始化当前和下一年的日K线分区
SELECT create_daily_partitions(
    (DATE_TRUNC('year', CURRENT_DATE))::DATE,
    2
);

-- 初始化当前和下两个月的分钟K线分区
SELECT create_minute_partitions(
    'stock_minute_kline',
    (DATE_TRUNC('month', CURRENT_DATE))::DATE,
    3
);


-- ============================================================
-- 8. 实时行情快照
-- ============================================================

-- 实时行情表：记录股票当前实时价格和五档买卖盘
-- 说明：
--   - 内存优化：设计成"快照"模式，每次更新是全量替换，不是增量追加
--   - 用途：前端展示实时价格，WebSocket 推送，仪表盘概览
--   - 五档行情：bid1-5 是买一至买五价格和挂单量，ask1-5 是卖一至卖五
--   - prev_close 昨收价，用于计算涨跌幅
--   - 代码是主键（不是自增ID），方便直接用股票代码更新
CREATE TABLE stock_realtime (
    code            VARCHAR(10) PRIMARY KEY REFERENCES stock_info(code),  -- 股票代码，主键
    price           NUMERIC(10, 3),                        -- 最新价
    open            NUMERIC(10, 3),                        -- 今日开盘价
    high            NUMERIC(10, 3),                        -- 今日最高价
    low             NUMERIC(10, 3),                         -- 今日最低价
    prev_close      NUMERIC(10, 3),                        -- 昨收价（用于算涨跌幅）
    volume          BIGINT,                                 -- 成交量（股）
    amount          NUMERIC(20, 2),                        -- 成交额（元）

    -- 买一档至买五档
    bid1            NUMERIC(10, 3), bid_vol1       BIGINT,  -- 买一价，买一量
    bid2            NUMERIC(10, 3), bid_vol2       BIGINT,  -- 买二价，买二量
    bid3            NUMERIC(10, 3), bid_vol3       BIGINT,  -- 买三价，买三量
    bid4            NUMERIC(10, 3), bid_vol4       BIGINT,  -- 买四价，买四量
    bid5            NUMERIC(10, 3), bid_vol5       BIGINT,  -- 买五价，买五量

    -- 卖一档至卖五档
    ask1            NUMERIC(10, 3), ask_vol1       BIGINT,  -- 卖一价，卖一量
    ask2            NUMERIC(10, 3), ask_vol2       BIGINT,  -- 卖二价，卖二量
    ask3            NUMERIC(10, 3), ask_vol3       BIGINT,  -- 卖三价，卖三量
    ask4            NUMERIC(10, 3), ask_vol4       BIGINT,  -- 卖四价，卖四量
    ask5            NUMERIC(10, 3), ask_vol5       BIGINT,  -- 卖五价，卖五量

    update_time     TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,  -- 最后更新时间
    CHECK (high IS NULL OR low IS NULL OR high >= low),     -- 价格合理性检查
    CHECK (high IS NULL OR open IS NULL OR high >= open),   -- 最高价 >= 开盘价
    CHECK (high IS NULL OR price IS NULL OR high >= price), -- 最高价 >= 最新价
    CHECK (low IS NULL OR open IS NULL OR low <= open),     -- 最低价 <= 开盘价
    CHECK (low IS NULL OR price IS NULL OR low <= price)    -- 最低价 <= 最新价
);

-- 自动更新触发器
CREATE TRIGGER trigger_realtime_update
BEFORE UPDATE ON stock_realtime
FOR EACH ROW EXECUTE FUNCTION update_timestamp_trigger();

-- 涨跌幅计算索引（用于涨跌幅排行榜）
-- 说明：建一个表达式索引，按涨跌幅从大到小排序时可以走索引
-- 注意：prev_close=0 时返回 0，避免除零错误
CREATE INDEX idx_realtime_change_pct ON stock_realtime (
    ((CASE WHEN prev_close > 0 THEN (price - prev_close) / prev_close * 100 ELSE 0 END)) DESC
);


-- ============================================================
-- 9. 用户持仓
-- ============================================================

-- 用户持仓表：记录用户买了哪些股票、买了多少、持有成本
-- 说明：
--   - shares：总持仓股数（包含可用和锁定的）
--   - available_shares：可用股数（T+1 机制，今天买的要明天才能卖）
--   - cost_price：成本价（用户买入时的平均价，用于计算盈亏）
--   - UNIQUE(user_id, stock_code)：一个用户对一只股票只有一条持仓记录
--   - shares > 0 约束：持仓股数必须为正，防止恶意数据
--   - ON DELETE CASCADE：删除用户时，其所有持仓记录一并删除
CREATE TABLE user_portfolio (
    id              SERIAL PRIMARY KEY,
    user_id         INT REFERENCES users(id) ON DELETE CASCADE,  -- 用户ID，级联删除
    stock_code      VARCHAR(10) REFERENCES stock_info(code) ON DELETE CASCADE,  -- 股票代码，外键关联
    shares          BIGINT NOT NULL CHECK (shares > 0),         -- 持仓股数，必须 > 0
    available_shares BIGINT NOT NULL DEFAULT 0,                  -- 可用股数（T+1）
    cost_price      NUMERIC(10, 3) NOT NULL,                    -- 成本价
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, stock_code)                                 -- 防止重复建仓
);

CREATE TRIGGER trigger_portfolio_update
BEFORE UPDATE ON user_portfolio
FOR EACH ROW EXECUTE FUNCTION update_timestamp_trigger();

-- 按用户ID查询索引（查询用户持仓用）
CREATE INDEX idx_portfolio_user ON user_portfolio(user_id);


-- ============================================================
-- 10. 财务数据
-- ============================================================

-- 财务数据表：记录股票的财务指标（季报、半年报、年报）
-- 说明：
--   - 每只股票每个报告期只有一条记录
--   - report_type：报告类型（年报、半年报、季报）
--   - revenue：营业收入，net_profit：净利润
--   - eps：每股收益，roe：净资产收益率，pe：市盈率，pb：市净率
--   - UNIQUE(stock_code, report_date, report_type) 防止重复数据
CREATE TABLE stock_financial (
    id              SERIAL PRIMARY KEY,
    stock_code      VARCHAR(10) REFERENCES stock_info(code),  -- 股票代码
    report_date     DATE NOT NULL,                         -- 报告期（如 2026-03-31）
    report_type     report_type,                           -- 报告类型枚举
    revenue         NUMERIC(20, 2),                        -- 营业收入
    net_profit      NUMERIC(20, 2),                        -- 净利润
    eps             NUMERIC(10, 3),                        -- 每股收益
    roe             NUMERIC(10, 2),                        -- 净资产收益率（%）
    pe              NUMERIC(10, 2),                        -- 市盈率
    pb              NUMERIC(10, 2),                        -- 市净率
    UNIQUE(stock_code, report_date, report_type)           -- 唯一约束
);

-- 按股票代码+报告日期倒序索引（查某股票最近财务数据用）
CREATE INDEX idx_financial_code_date ON stock_financial(stock_code, report_date DESC);


-- ============================================================
-- 11. 系统任务与日志
-- ============================================================

-- 选股任务表：记录选股策略的执行情况
-- 说明：
--   - strategy：策略名称（如"均线多头"、"破年新高"）
--   - params：策略参数（JSON格式），如 {"ma_period": 20, "volume_threshold": 1.5}
--   - status：任务状态：PENDING（等待）、RUNNING（执行中）、SUCCESS（完成）、FAILED（失败）、CANCELLED（取消）
--   - started_at/finished_at：记录任务执行时间，用于分析性能
CREATE TABLE selection_task (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100),                          -- 任务名称
    strategy        strategy_type,                         -- 选股策略枚举
    params          JSONB,                                 -- 策略参数（JSON）
    status          task_status DEFAULT 'PENDING',         -- 任务状态枚举
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    started_at      TIMESTAMPTZ,                          -- 任务开始时间
    finished_at     TIMESTAMPTZ                            -- 任务结束时间
);

-- 按状态索引（查待执行/执行中的任务用）
CREATE INDEX idx_task_status ON selection_task(status);

-- 按创建时间倒序索引（查询任务历史用）
CREATE INDEX idx_task_created_at ON selection_task(created_at DESC);


-- 选股结果明细表：每条选股任务的结果（选中了哪些股票）
-- 说明：
--   - task_id 关联到 selection_task.id
--   - score：股票评分（综合多维度计算出来的）
--   - reason：入选原因（如"均线多头排列"、"突破前高"）
CREATE TABLE task_detail (
    id              SERIAL PRIMARY KEY,
    task_id         INT REFERENCES selection_task(id) ON DELETE CASCADE,  -- 关联任务，级联删除
    stock_code      VARCHAR(10) REFERENCES stock_info(code) ON DELETE CASCADE,  -- 股票代码，外键关联
    score           NUMERIC(10, 2),                        -- 选股评分
    reason          TEXT,                                  -- 入选原因说明
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 按股票代码查询索引（查询某股票被哪些任务选中用）
CREATE INDEX idx_detail_stock ON task_detail(stock_code);


-- 操作日志表：记录用户的所有操作行为
-- 说明：
--   - user_id：操作者（为空表示系统自动操作）
--   - action：操作类型（如 "LOGIN"、"CREATE_PORTFOLIO"、"UPDATE_STOCK"）
--   - target：操作对象（如 "USER:5"、"PORTFOLIO:12"）
--   - detail：操作详情（JSON格式，记录修改前后值）
--   - ip_addr：操作者 IP 地址
--   - 定期归档或分区，避免单表数据量过大
CREATE TABLE operation_log (
    id              SERIAL PRIMARY KEY,
    user_id         INT REFERENCES users(id) ON DELETE SET NULL,  -- 操作者ID（可为空，系统操作）
    action          action_type,                           -- 操作类型枚举
    target          VARCHAR(100),                          -- 操作对象
    detail          JSONB,                                 -- 操作详情（JSON）
    ip_addr         VARCHAR(50),                            -- IP 地址
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 按用户ID+时间倒序索引（查某用户操作历史用）
CREATE INDEX idx_log_user_time ON operation_log(user_id, created_at DESC);

-- 按操作类型查询索引（查询特定操作用）
CREATE INDEX idx_log_action ON operation_log(action);


-- ============================================================
-- 12. 系统配置表
-- ============================================================

-- 系统配置表：用于动态管理系统配置项，避免硬编码
-- 说明：
--   - config_key：配置键名（唯一）
--   - config_value：配置值（JSON格式，支持复杂结构）
--   - description：配置说明
--   - 可用于管理：策略列表、K线周期、业务规则等
CREATE TABLE sys_config (
    id              SERIAL PRIMARY KEY,
    config_key      VARCHAR(50) UNIQUE NOT NULL,           -- 配置键名，唯一
    config_value    JSONB NOT NULL,                        -- 配置值（JSON）
    description     TEXT,                                  -- 配置说明
    created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trigger_sys_config_update
BEFORE UPDATE ON sys_config
FOR EACH ROW EXECUTE FUNCTION update_timestamp_trigger();

-- 插入默认配置
INSERT INTO sys_config (config_key, config_value, description) VALUES
('user_roles', '["USER", "ADMIN", "ANALYST"]', '用户角色列表'),
('user_status', '["ACTIVE", "INACTIVE", "BANNED"]', '用户状态列表'),
('stock_status', '["LISTING", "DELISTING", "ST", "PAUSED"]', '股票状态列表'),
('kline_periods', '["1min", "5min", "15min", "30min", "60min"]', 'K线周期列表'),
('report_types', '["年报", "半年报", "一季报", "二季报", "三季报"]', '财务报告类型'),
('task_status', '["PENDING", "RUNNING", "SUCCESS", "FAILED", "CANCELLED"]', '任务状态列表'),
('action_types', '["LOGIN", "LOGOUT", "SELECT_STOCK", "EXPORT", "IMPORT", "DELETE", "UPDATE", "CREATE", "VIEW", "DOWNLOAD"]', '操作类型列表'),
('strategy_types', '["MA_CROSS", "MACD", "RSI", "KDJ", "BOLL", "CUSTOM"]', '选股策略列表'),
('partition_settings', '{"daily_years_ahead": 2, "minute_months_ahead": 3}', '分区创建配置：日K线提前创建年数，分钟K线提前创建月数');


-- ============================================================
-- 附录：维护脚本
-- ============================================================

-- 手动创建日K线分区（按需执行）
-- SELECT create_daily_partition_if_not_exists('2027-01-01');

-- 手动创建分钟K线分区（按需执行）
-- SELECT create_minute_partition_if_not_exists('stock_minute_kline', '2026-06-01');

-- 批量创建分区
-- SELECT create_daily_partitions('2027-01-01', 3);  -- 创建未来3年日K线分区
-- SELECT create_minute_partitions('stock_minute_kline', '2026-06-01', 6);  -- 创建未来6个月分钟K线分区

-- 查看已创建的分区
-- SELECT tablename FROM pg_tables WHERE tablename LIKE 'stock_daily_kline_%' ORDER BY tablename;
-- SELECT tablename FROM pg_tables WHERE tablename LIKE 'stock_minute_kline_%' ORDER BY tablename;

-- 查看定时任务状态
-- SELECT * FROM cron.job;

-- 查看定时任务运行日志
-- SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 10;


-- ============================================================
-- 附录：数据清理策略
-- ============================================================

-- 分钟K线数据量大，建议定期归档：
-- 1. 每天收盘后（15:30 后）将当日数据压缩
-- 2. 超过 30 天的分钟数据归档到冷存储
-- 3. 只在数据库保留最近 30 天的分钟K线
-- 4. 历史数据可通过归档库查询

-- 日K线数据长期保留（分区表，按年查很快）
-- 日K线不做强制归档，保留全部历史
