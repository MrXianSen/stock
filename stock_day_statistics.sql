CREATE TABLE Stock_day_statistics
(
	id INT PRIMARY KEY AUTO_INCREMENT,
	stock_code VARCHAR(32),				-- 股票代码
	stock_date DATE,					-- 日期
	stock_day_max_price DECIMAL,		-- 最高价
	stock_day_min_price DECIMAL,		-- 最低价
	stock_day_open_price DECIMAL,		-- 股票开盘价
	stock_day_close_price DECIMAL,		-- 股票收盘价
	stock_volume INT,					-- 股票成交量

	-- 其他数据 --
	-- 一下为预测值 --
	stock_forecast_price DECIMAL,		-- 明日股票价格预测值
	stock_trend BOOLEAN,				-- 预测本周走势
	FOREIGN KEY(stock_code) REFERENCES Stock_base(stock_code)
)