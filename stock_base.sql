CREATE TABLE Stock_base 			-- 股票基础数据
(
	stock_code VARCHAR(32),			-- 股票代码，主键
	stock_name VARCHAR(64) NOT NULL,	-- 股票名称
	PRIMARY KEY(stock_code)
);