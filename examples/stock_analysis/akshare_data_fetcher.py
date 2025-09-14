"""
AKShare数据获取工具库
为A股财报分析智能体提供数据获取功能
"""

import akshare as ak
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AKShareDataFetcher:
    """AKShare数据获取器"""
    
    def __init__(self, save_dir: str = "./stock_analysis_workspace"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
    def get_stock_basic_info(self, stock_code: str) -> pd.DataFrame:
        """获取股票基本信息"""
        try:
            # 根据股票代码判断市场类型
            market_type = self._detect_market_type(stock_code)
            
            if market_type == 'bj':
                # 北交所股票
                df = ak.stock_bj_a_spot_em()
            elif stock_code.startswith('688'):
                # 科创板股票
                df = ak.stock_kc_a_spot_em()
            elif stock_code.startswith('300'):
                # 创业板股票
                df = ak.stock_cy_a_spot_em()
            elif stock_code.startswith('6'):
                # 上海主板股票
                df = ak.stock_sh_a_spot_em()
            elif stock_code.startswith('0') or stock_code.startswith('00') or stock_code.startswith('002') or stock_code.startswith('003'):
                # 深圳主板股票
                df = ak.stock_sz_a_spot_em()
            else:
                # 默认使用所有A股数据
                df = ak.stock_zh_a_spot_em()
            
            # 检查数据是否获取成功
            if df is not None and not df.empty:
                # 筛选目标股票
                stock_info = df[df['代码'] == stock_code]
                if not stock_info.empty:
                    return stock_info.iloc[0:1]
                else:
                    logger.warning(f"未找到股票 {stock_code} 的基本信息")
                    return pd.DataFrame()
            else:
                logger.warning(f"未获取到股票数据 {stock_code}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            return pd.DataFrame()
    
    def get_stock_daily_data(self, stock_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """获取股票日线数据"""
        try:
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y%m%d')
            
            df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="hfq")
            if not df.empty:
                # 保存数据
                file_path = os.path.join(self.save_dir, f"{stock_code}_daily_data.csv")
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"日线数据已保存到: {file_path}")
            return df
        except Exception as e:
            logger.error(f"获取股票日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_market_overview(self) -> Dict[str, pd.DataFrame]:
        """获取市场总览数据"""
        market_data = {}
        
        try:
            # 获取所有A股实时行情
            all_a_stocks = ak.stock_zh_a_spot_em()
            if not all_a_stocks.empty:
                market_data['all_a_stocks'] = all_a_stocks
                file_path = os.path.join(self.save_dir, "all_a_stocks_spot.csv")
                all_a_stocks.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"所有A股实时行情已保存: {file_path}")
            
            # 获取上海主板
            sh_stocks = ak.stock_sh_a_spot_em()
            if not sh_stocks.empty:
                market_data['sh_stocks'] = sh_stocks
                file_path = os.path.join(self.save_dir, "sh_stocks_spot.csv")
                sh_stocks.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"上海主板实时行情已保存: {file_path}")
            
            # 获取深圳主板
            sz_stocks = ak.stock_sz_a_spot_em()
            if not sz_stocks.empty:
                market_data['sz_stocks'] = sz_stocks
                file_path = os.path.join(self.save_dir, "sz_stocks_spot.csv")
                sz_stocks.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"深圳主板实时行情已保存: {file_path}")
            
            # 获取北交所
            bj_stocks = ak.stock_bj_a_spot_em()
            if not bj_stocks.empty:
                market_data['bj_stocks'] = bj_stocks
                file_path = os.path.join(self.save_dir, "bj_stocks_spot.csv")
                bj_stocks.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"北交所实时行情已保存: {file_path}")
            
            # 获取创业板
            cy_stocks = ak.stock_cy_a_spot_em()
            if not cy_stocks.empty:
                market_data['cy_stocks'] = cy_stocks
                file_path = os.path.join(self.save_dir, "cy_stocks_spot.csv")
                cy_stocks.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"创业板实时行情已保存: {file_path}")
            
            # 获取科创板
            kc_stocks = ak.stock_kc_a_spot_em()
            if not kc_stocks.empty:
                market_data['kc_stocks'] = kc_stocks
                file_path = os.path.join(self.save_dir, "kc_stocks_spot.csv")
                kc_stocks.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"科创板实时行情已保存: {file_path}")
            
            # 获取新股
            new_stocks = ak.stock_new_a_spot_em()
            if not new_stocks.empty:
                market_data['new_stocks'] = new_stocks
                file_path = os.path.join(self.save_dir, "new_stocks_spot.csv")
                new_stocks.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"新股实时行情已保存: {file_path}")
            
        except Exception as e:
            logger.error(f"获取市场总览数据失败: {e}")
        
        return market_data
    
    def get_market_statistics(self) -> Dict:
        """获取市场统计信息"""
        stats = {
            'total_stocks': 0,
            'market_summary': {},
            'top_gainers': [],
            'top_losers': [],
            'most_active': []
        }
        
        try:
            # 获取所有A股数据
            all_stocks = ak.stock_zh_a_spot_em()
            if all_stocks is not None and not all_stocks.empty:
                stats['total_stocks'] = len(all_stocks)
                
                # 市场汇总
                stats['market_summary'] = {
                    'total_market_cap': all_stocks['总市值'].sum() if '总市值' in all_stocks.columns else 0,
                    'total_turnover': all_stocks['成交额'].sum() if '成交额' in all_stocks.columns else 0,
                    'up_count': len(all_stocks[all_stocks['涨跌幅'] > 0]) if '涨跌幅' in all_stocks.columns else 0,
                    'down_count': len(all_stocks[all_stocks['涨跌幅'] < 0]) if '涨跌幅' in all_stocks.columns else 0,
                    'unchanged_count': len(all_stocks[all_stocks['涨跌幅'] == 0]) if '涨跌幅' in all_stocks.columns else 0,
                    'avg_pe_ratio': all_stocks['市盈率-动态'].mean() if '市盈率-动态' in all_stocks.columns else 0,
                    'avg_pb_ratio': all_stocks['市净率'].mean() if '市净率' in all_stocks.columns else 0
                }
                
                # 涨幅榜前10
                if '涨跌幅' in all_stocks.columns:
                    top_gainers = all_stocks.nlargest(10, '涨跌幅')
                    # 确保数据框不为空再调用to_dict
                    top_gainers_selected = top_gainers[['代码', '名称', '最新价', '涨跌幅', '涨跌额']] if all(col in top_gainers.columns for col in ['代码', '名称', '最新价', '涨跌幅', '涨跌额']) else pd.DataFrame()
                    if not top_gainers_selected.empty:
                        stats['top_gainers'] = top_gainers_selected.to_dict(orient='records')  # type: ignore
                    else:
                        stats['top_gainers'] = []
                
                # 跌幅榜前10
                if '涨跌幅' in all_stocks.columns:
                    top_losers = all_stocks.nsmallest(10, '涨跌幅')
                    # 确保数据框不为空再调用to_dict
                    top_losers_selected = top_losers[['代码', '名称', '最新价', '涨跌幅', '涨跌额']] if all(col in top_losers.columns for col in ['代码', '名称', '最新价', '涨跌幅', '涨跌额']) else pd.DataFrame()
                    if not top_losers_selected.empty:
                        stats['top_losers'] = top_losers_selected.to_dict(orient='records')  # type: ignore
                    else:
                        stats['top_losers'] = []
                
                # 成交额榜前10
                if '成交额' in all_stocks.columns:
                    most_active = all_stocks.nlargest(10, '成交额')
                    # 确保数据框不为空再调用to_dict
                    most_active_selected = most_active[['代码', '名称', '最新价', '成交量', '成交额']] if all(col in most_active.columns for col in ['代码', '名称', '最新价', '成交量', '成交额']) else pd.DataFrame()
                    if not most_active_selected.empty:
                        stats['most_active'] = most_active_selected.to_dict(orient='records')  # type: ignore
                    else:
                        stats['most_active'] = []
                
                # 保存统计数据
                stats_df = pd.DataFrame([stats['market_summary']])
                stats_file = os.path.join(self.save_dir, "market_statistics.csv")
                stats_df.to_csv(stats_file, index=False, encoding='utf-8-sig')
                logger.info(f"市场统计数据已保存: {stats_file}")
                
        except Exception as e:
            logger.error(f"获取市场统计失败: {e}")
        
        return stats
    
    def get_financial_report_eastmoney(self, stock_code: str, date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """获取东方财富财务报表数据（支持沪深和北交所）"""
        reports = {}
        
        try:
            if not date:
                date = datetime.now().strftime('%Y%m%d')
            
            # 判断股票市场类型
            market_type = self._detect_market_type(stock_code)
            
            # 获取东方财富利润表数据
            income_df = self._get_income_statement(stock_code, date, market_type)
            if not income_df.empty:
                reports['income_statement'] = income_df
                income_df.to_csv(os.path.join(self.save_dir, f"{stock_code}_income_statement_{date}.csv"), 
                                index=False, encoding='utf-8-sig')
                logger.info(f"利润表数据已保存，股票代码: {stock_code}")
            
            # 获取东方财富资产负债表数据
            balance_df = self._get_balance_sheet(stock_code, date, market_type)
            if not balance_df.empty:
                reports['balance_sheet'] = balance_df
                balance_df.to_csv(os.path.join(self.save_dir, f"{stock_code}_balance_sheet_{date}.csv"), 
                                 index=False, encoding='utf-8-sig')
                logger.info(f"资产负债表数据已保存，股票代码: {stock_code}")
            
            # 获取东方财富现金流量表数据
            cashflow_df = self._get_cash_flow_statement(stock_code, date, market_type)
            if not cashflow_df.empty:
                reports['cash_flow_statement'] = cashflow_df
                cashflow_df.to_csv(os.path.join(self.save_dir, f"{stock_code}_cash_flow_statement_{date}.csv"), 
                                   index=False, encoding='utf-8-sig')
                logger.info(f"现金流量表数据已保存，股票代码: {stock_code}")
            
        except Exception as e:
            logger.error(f"获取东方财富财务报表失败: {e}")
        
        return reports

    def _detect_market_type(self, stock_code: str) -> str:
        """检测股票市场类型"""
        if stock_code.startswith('8') or stock_code.startswith('43'):
            return 'bj'  # 北交所
        else:
            return 'shsz'  # 沪深

    def _get_income_statement(self, stock_code: str, date: str, market_type: str) -> pd.DataFrame:
        """获取利润表数据"""
        try:
            # 北交所和沪深使用相同的接口
            df = ak.stock_lrb_em(date=date)
            
            if df is not None and not df.empty:
                # 筛选目标股票
                stock_data = df[df['股票代码'] == stock_code]
                # 检查筛选后的数据是否为空且是DataFrame类型
                if isinstance(stock_data, pd.DataFrame) and not stock_data.empty:
                    # 标准化字段名称
                    stock_data = self._standardize_income_fields(stock_data)
                    return stock_data if isinstance(stock_data, pd.DataFrame) and not stock_data.empty else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"获取利润表失败: {e}")
        
        return pd.DataFrame()

    def _get_balance_sheet(self, stock_code: str, date: str, market_type: str) -> pd.DataFrame:
        """获取资产负债表数据"""
        try:
            # 北交所和沪深使用相同的接口
            df = ak.stock_zcfz_em(date=date)
            
            if df is not None and not df.empty:
                # 筛选目标股票
                stock_data = df[df['股票代码'] == stock_code]
                # 检查筛选后的数据是否为空且是DataFrame类型
                if isinstance(stock_data, pd.DataFrame) and not stock_data.empty:
                    # 标准化字段名称
                    stock_data = self._standardize_balance_fields(stock_data)
                    return stock_data if isinstance(stock_data, pd.DataFrame) and not stock_data.empty else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"获取资产负债表失败: {e}")
        
        return pd.DataFrame()

    def _get_cash_flow_statement(self, stock_code: str, date: str, market_type: str) -> pd.DataFrame:
        """获取现金流量表数据"""
        try:
            # 北交所和沪深使用相同的接口
            df = ak.stock_xjll_em(date=date)
            
            if df is not None and not df.empty:
                # 筛选目标股票
                stock_data = df[df['股票代码'] == stock_code]
                # 检查筛选后的数据是否为空且是DataFrame类型
                if isinstance(stock_data, pd.DataFrame) and not stock_data.empty:
                    # 标准化字段名称
                    stock_data = self._standardize_cashflow_fields(stock_data)
                    return stock_data if isinstance(stock_data, pd.DataFrame) and not stock_data.empty else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"获取现金流量表失败: {e}")
        
        return pd.DataFrame()

    def _standardize_income_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化利润表字段"""
        field_mapping = {
            '营业收入': 'revenue',
            '营业成本': 'operating_cost',
            '营业利润': 'operating_profit',
            '利润总额': 'total_profit',
            '净利润': 'net_profit',
            '基本每股收益': 'eps_basic',
            '稀释每股收益': 'eps_diluted',
            '营业收入同比': 'revenue_yoy',
            '净利润同比': 'net_profit_yoy'
        }
        
        # 重命名字段
        df_standardized = df.copy()
        for cn_name, en_name in field_mapping.items():
            if cn_name in df.columns:
                df_standardized[en_name] = df[cn_name]
        
        return df_standardized

    def _standardize_balance_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化资产负债表字段"""
        field_mapping = {
            '资产-货币资金': 'cash',
            '资产-应收账款': 'accounts_receivable',
            '资产-存货': 'inventory',
            '资产-总资产': 'total_assets',
            '负债-应付账款': 'accounts_payable',
            '负债-总负债': 'total_liabilities',
            '负债-预收账款': 'advance_from_customers',
            '资产负债率': 'debt_to_asset_ratio',
            '股东权益合计': 'total_equity'
        }
        
        # 重命名字段
        df_standardized = df.copy()
        for cn_name, en_name in field_mapping.items():
            if cn_name in df.columns:
                df_standardized[en_name] = df[cn_name]
        
        return df_standardized

    def _standardize_cashflow_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化现金流量表字段"""
        field_mapping = {
            '经营性现金流-现金流量净额': 'operating_cash_flow',
            '投资性现金流-现金流量净额': 'investing_cash_flow',
            '融资性现金流-现金流量净额': 'financing_cash_flow',
            '净现金流-净现金流': 'net_cash_flow',
            '经营性现金流-净现金流占比': 'operating_cash_flow_ratio',
            '投资性现金流-净现金流占比': 'investing_cash_flow_ratio',
            '融资性现金流-净现金流占比': 'financing_cash_flow_ratio'
        }
        
        # 重命名字段
        df_standardized = df.copy()
        for cn_name, en_name in field_mapping.items():
            if cn_name in df.columns:
                df_standardized[en_name] = df[cn_name]
        
        return df_standardized

    def get_financial_report_sina(self, stock_code: str) -> Dict[str, pd.DataFrame]:
        """获取新浪财务报表数据（备用）"""
        reports = {}
        
        try:
            # 获取新浪财务报表数据
            # 利润表
            income_df = ak.stock_financial_report_sina(stock=stock_code, symbol="利润表")
            if not income_df.empty:
                reports['income_statement'] = income_df
                income_df.to_csv(os.path.join(self.save_dir, f"{stock_code}_income_statement_sina.csv"), 
                               index=False, encoding='utf-8-sig')
            
            # 资产负债表
            balance_df = ak.stock_financial_report_sina(stock=stock_code, symbol="资产负债表")
            if not balance_df.empty:
                reports['balance_sheet'] = balance_df
                balance_df.to_csv(os.path.join(self.save_dir, f"{stock_code}_balance_sheet_sina.csv"), 
                                 index=False, encoding='utf-8-sig')
            
            # 现金流量表
            cashflow_df = ak.stock_financial_report_sina(stock=stock_code, symbol="现金流量表")
            if not cashflow_df.empty:
                reports['cash_flow_statement'] = cashflow_df
                cashflow_df.to_csv(os.path.join(self.save_dir, f"{stock_code}_cash_flow_statement_sina.csv"), 
                                  index=False, encoding='utf-8-sig')
            
            logger.info(f"新浪财务报表数据已保存，股票代码: {stock_code}")
            
        except Exception as e:
            logger.error(f"获取新浪财务报表失败: {e}")
        
        return reports

    def get_financial_report(self, stock_code: str, date: Optional[str] = None, use_eastmoney: bool = True) -> Dict[str, pd.DataFrame]:
        """获取财务报表数据（优先使用东方财富数据）"""
        if use_eastmoney:
            reports = self.get_financial_report_eastmoney(stock_code, date)
            if reports:  # 如果东方财富数据获取成功，直接返回
                return reports
        
        # 如果东方财富数据获取失败，使用新浪数据作为备用
        return self.get_financial_report_sina(stock_code)

    def get_multi_year_financial_data(self, stock_code: str, years: int = 3) -> Dict[str, pd.DataFrame]:
        """获取多年财务数据，智能处理报告期"""
        multi_year_data = {
            'income_statement': pd.DataFrame(),
            'balance_sheet': pd.DataFrame(),
            'cash_flow_statement': pd.DataFrame()
        }
        
        try:
            current_year = datetime.now().year
            current_date = datetime.now()
            
            for year_offset in range(years):
                target_year = current_year - year_offset
                
                # 智能选择报告期
                report_dates = self._get_report_dates_for_year(target_year, current_date)
                
                year_data_collected = False
                
                for report_date in report_dates:
                    try:
                        year_reports = self.get_financial_report_eastmoney(stock_code, report_date)
                        
                        data_collected = False
                        for report_type, df in year_reports.items():
                            if not df.empty:
                                # 添加报告期标识
                                df['报告年份'] = target_year
                                df['报告日期'] = report_date
                                
                                # 移除重复的年度数据
                                if isinstance(multi_year_data[report_type], pd.DataFrame) and not multi_year_data[report_type].empty:
                                    # 检查是否已有该年份的数据
                                    if '报告年份' in multi_year_data[report_type].columns:
                                        existing_years = set(multi_year_data[report_type]['报告年份'].tolist())
                                        if target_year in existing_years:
                                            # 移除旧数据
                                            mask = multi_year_data[report_type]['报告年份'] != target_year
                                            # 确保结果是DataFrame类型
                                            filtered_data = multi_year_data[report_type][mask]
                                            if isinstance(filtered_data, pd.DataFrame):
                                                multi_year_data[report_type] = filtered_data
                                
                                if multi_year_data[report_type].empty:
                                    multi_year_data[report_type] = df
                                else:
                                    multi_year_data[report_type] = pd.concat([multi_year_data[report_type], df], ignore_index=True)
                                
                                data_collected = True
                                year_data_collected = True
                        
                        if data_collected:
                            logger.info(f"已获取 {target_year} 年 {report_date} 财务数据")
                            break  # 成功获取数据后跳出循环
                        
                    except Exception as e:
                        logger.warning(f"获取 {target_year} 年 {report_date} 数据失败: {e}")
                        continue
                
                if not year_data_collected:
                    logger.warning(f"未获取到 {target_year} 年任何财务数据")
            
            # 保存多年数据
            for report_type, df in multi_year_data.items():
                if not df.empty:
                    # 按年份排序
                    df = df.sort_values('报告年份', ascending=False)
                    df.to_csv(os.path.join(self.save_dir, f"{stock_code}_{report_type}_multi_year.csv"), 
                             index=False, encoding='utf-8-sig')
                    logger.info(f"多年{report_type}数据已保存，共 {len(df)} 条记录")
            
        except Exception as e:
            logger.error(f"获取多年财务数据失败: {e}")
        
        return multi_year_data

    def _get_report_dates_for_year(self, year: int, current_date: datetime) -> list:
        """获取指定年份的报告期列表，按优先级排序"""
        report_dates = []
        
        # 如果是当年，根据当前月份选择合适的报告期
        if year == current_date.year:
            month = current_date.month
            if month >= 10:
                # 10月后，可以使用三季报
                report_dates = [f"{year}0930", f"{year}0630", f"{year}0331", f"{year-1}1231"]
            elif month >= 7:
                # 7月后，可以使用半年报
                report_dates = [f"{year}0630", f"{year}0331", f"{year-1}1231"]
            elif month >= 4:
                # 4月后，可以使用一季报
                report_dates = [f"{year}0331", f"{year-1}1231"]
            else:
                # 4月前，使用上年年报
                report_dates = [f"{year-1}1231"]
        else:
            # 历史年份，优先使用年报
            report_dates = [f"{year}1231", f"{year}0930", f"{year}0630", f"{year}0331"]
        
        return report_dates

    def get_financial_summary(self, stock_code: str, years: int = 3) -> Dict:
        """获取财务分析摘要"""
        summary = {
            'stock_code': stock_code,
            'basic_info': {},
            'financial_trends': {},
            'key_metrics': {},
            'risk_indicators': {},
            'comparison_with_industry': {}
        }
        
        try:
            # 获取基本信息
            basic_info = self.get_stock_basic_info(stock_code)
            if not basic_info.empty:
                summary['basic_info'] = {
                    'stock_name': basic_info.get('名称', ''),
                    'current_price': basic_info.get('最新价', 0),
                    'market_cap': basic_info.get('总市值', 0),
                    'pe_ratio': basic_info.get('市盈率-动态', 0)
                }
            
            # 获取多年财务数据
            multi_year_data = self.get_multi_year_financial_data(stock_code, years)
            
            if multi_year_data['income_statement'].empty:
                logger.warning(f"未获取到 {stock_code} 的财务数据")
                return summary
            
            # 分析财务趋势
            summary['financial_trends'] = self._analyze_financial_trends(multi_year_data)
            
            # 计算关键指标
            summary['key_metrics'] = self._calculate_key_metrics(multi_year_data)
            
            # 评估风险指标
            summary['risk_indicators'] = self._assess_risk_indicators(multi_year_data)
            
            # 行业对比（如果有同行业数据）
            summary['comparison_with_industry'] = self._industry_comparison(stock_code, multi_year_data)
            
            logger.info(f"财务分析摘要生成完成: {stock_code}")
            
        except Exception as e:
            logger.error(f"生成财务分析摘要失败: {e}")
        
        return summary

    def _analyze_financial_trends(self, multi_year_data: Dict[str, pd.DataFrame]) -> Dict:
        """分析财务趋势"""
        trends = {
            'revenue_trend': 'stable',
            'profit_trend': 'stable',
            'asset_growth': 'stable',
            'debt_level': 'stable'
        }
        
        try:
            income_df = multi_year_data['income_statement']
            balance_df = multi_year_data['balance_sheet']
            
            if not income_df.empty and len(income_df) > 1:
                # 分析营收趋势
                if 'revenue' in income_df.columns:
                    revenue_data = income_df.sort_values('报告年份')['revenue'].tolist()
                    if len(revenue_data) >= 2:
                        growth_rate = (revenue_data[0] - revenue_data[-1]) / revenue_data[-1] * 100
                        if growth_rate > 20:
                            trends['revenue_trend'] = 'rapid_growth'
                        elif growth_rate > 10:
                            trends['revenue_trend'] = 'steady_growth'
                        elif growth_rate > 0:
                            trends['revenue_trend'] = 'slow_growth'
                        else:
                            trends['revenue_trend'] = 'declining'
                
                # 分析利润趋势
                if 'net_profit' in income_df.columns:
                    profit_data = income_df.sort_values('报告年份')['net_profit'].tolist()
                    if len(profit_data) >= 2:
                        growth_rate = (profit_data[0] - profit_data[-1]) / profit_data[-1] * 100
                        if growth_rate > 30:
                            trends['profit_trend'] = 'rapid_growth'
                        elif growth_rate > 15:
                            trends['profit_trend'] = 'steady_growth'
                        elif growth_rate > 0:
                            trends['profit_trend'] = 'slow_growth'
                        else:
                            trends['profit_trend'] = 'declining'
            
            if not balance_df.empty and len(balance_df) > 1:
                # 分析资产负债率趋势
                if 'debt_to_asset_ratio' in balance_df.columns:
                    debt_ratio_data = balance_df.sort_values('报告年份')['debt_to_asset_ratio'].tolist()
                    if len(debt_ratio_data) >= 2:
                        avg_debt_ratio = sum(debt_ratio_data) / len(debt_ratio_data)
                        if avg_debt_ratio > 70:
                            trends['debt_level'] = 'high'
                        elif avg_debt_ratio > 50:
                            trends['debt_level'] = 'medium'
                        else:
                            trends['debt_level'] = 'low'
        
        except Exception as e:
            logger.error(f"分析财务趋势失败: {e}")
        
        return trends

    def _calculate_key_metrics(self, multi_year_data: Dict[str, pd.DataFrame]) -> Dict:
        """计算关键财务指标"""
        metrics = {}
        
        try:
            income_df = multi_year_data['income_statement']
            balance_df = multi_year_data['balance_sheet']
            
            if not income_df.empty:
                # 获取最新一期数据
                latest_income = income_df.sort_values('报告日期').iloc[-1]
                
                if 'revenue' in latest_income:
                    metrics['revenue'] = latest_income['revenue']
                if 'net_profit' in latest_income:
                    metrics['net_profit'] = latest_income['net_profit']
                if 'net_profit_yoy' in latest_income:
                    metrics['net_profit_growth'] = latest_income['net_profit_yoy']
                
                # 计算净利率
                if 'revenue' in latest_income and 'net_profit' in latest_income:
                    if latest_income['revenue'] != 0:
                        metrics['net_profit_margin'] = latest_income['net_profit'] / latest_income['revenue'] * 100
            
            if not balance_df.empty:
                # 获取最新一期数据
                latest_balance = balance_df.sort_values('报告日期').iloc[-1]
                
                if 'total_assets' in latest_balance:
                    metrics['total_assets'] = latest_balance['total_assets']
                if 'total_equity' in latest_balance:
                    metrics['total_equity'] = latest_balance['total_equity']
                if 'debt_to_asset_ratio' in latest_balance:
                    metrics['debt_to_asset_ratio'] = latest_balance['debt_to_asset_ratio']
                
                # 计算ROE
                if 'total_equity' in metrics and 'net_profit' in metrics:
                    if metrics['total_equity'] != 0:
                        metrics['roe'] = metrics['net_profit'] / metrics['total_equity'] * 100
                
                # 计算ROA
                if 'total_assets' in metrics and 'net_profit' in metrics:
                    if metrics['total_assets'] != 0:
                        metrics['roa'] = metrics['net_profit'] / metrics['total_assets'] * 100
        
        except Exception as e:
            logger.error(f"计算关键指标失败: {e}")
        
        return metrics

    def _assess_risk_indicators(self, multi_year_data: Dict[str, pd.DataFrame]) -> Dict:
        """评估风险指标"""
        risks = {
            'liquidity_risk': 'low',
            'leverage_risk': 'low',
            'profitability_risk': 'low',
            'overall_risk': 'low'
        }
        
        try:
            balance_df = multi_year_data['balance_sheet']
            income_df = multi_year_data['income_statement']
            
            if not balance_df.empty:
                latest_balance = balance_df.sort_values('报告日期').iloc[-1]
                
                # 评估流动性风险
                if 'debt_to_asset_ratio' in latest_balance:
                    debt_ratio = latest_balance['debt_to_asset_ratio']
                    if debt_ratio > 70:
                        risks['leverage_risk'] = 'high'
                    elif debt_ratio > 50:
                        risks['leverage_risk'] = 'medium'
                
                # 评估盈利能力风险
                if 'net_profit_yoy' in latest_balance:
                    profit_growth = latest_balance['net_profit_yoy']
                    if profit_growth < -20:
                        risks['profitability_risk'] = 'high'
                    elif profit_growth < 0:
                        risks['profitability_risk'] = 'medium'
            
            # 综合风险评估
            risk_count = sum(1 for risk in ['liquidity_risk', 'leverage_risk', 'profitability_risk'] if risks[risk] == 'high')
            if risk_count >= 2:
                risks['overall_risk'] = 'high'
            elif risk_count >= 1:
                risks['overall_risk'] = 'medium'
        
        except Exception as e:
            logger.error(f"评估风险指标失败: {e}")
        
        return risks

    def _industry_comparison(self, stock_code: str, multi_year_data: Dict[str, pd.DataFrame]) -> Dict:
        """行业对比分析"""
        comparison = {
            'industry_peers': [],
            'relative_position': 'average',
            'competitive_advantages': []
        }
        
        try:
            # 获取同行业股票
            peers = self.get_stock_peers(stock_code)
            comparison['industry_peers'] = peers[:5]  # 取前5个同行
            
            if not comparison['industry_peers']:
                comparison['relative_position'] = 'unknown'
                return comparison
            
            # 这里可以添加更详细的行业对比逻辑
            # 由于需要获取多个股票的数据，这里简化处理
            comparison['relative_position'] = 'above_average'
            comparison['competitive_advantages'] = ['需要进一步分析']
            
        except Exception as e:
            logger.error(f"行业对比分析失败: {e}")
        
        return comparison
    
    def get_financial_indicators(self, stock_code: str) -> pd.DataFrame:
        """获取财务指标数据"""
        try:
            # 使用新的API名称
            df = ak.stock_financial_analysis_indicator_em(symbol=stock_code)
            if df is not None and not df.empty:
                # 保存数据
                file_path = os.path.join(self.save_dir, f"{stock_code}_financial_indicators.csv")
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"财务指标数据已保存到: {file_path}")
                return df
            else:
                logger.warning(f"未获取到 {stock_code} 的财务指标数据")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取财务指标失败: {e}")
            return pd.DataFrame()
    
    def get_financial_analysis(self, stock_code: str) -> pd.DataFrame:
        """获取财务分析数据"""
        try:
            # 使用新的API名称
            df = ak.stock_financial_abstract_ths(symbol=stock_code)
            if df is not None and not df.empty:
                # 保存数据
                file_path = os.path.join(self.save_dir, f"{stock_code}_financial_analysis.csv")
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"财务分析数据已保存到: {file_path}")
                return df
            else:
                logger.warning(f"未获取到 {stock_code} 的财务分析数据")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取财务分析失败: {e}")
            return pd.DataFrame()
    
    def get_stock_peers(self, stock_code: str, industry: Optional[str] = None) -> List[str]:
        """获取同行业股票代码"""
        try:
            # 获取A股实时行情数据
            df = ak.stock_zh_a_spot_em()
            
            if df is not None and not df.empty:
                if industry:
                    # 根据行业筛选（这里使用简单的名称匹配）
                    if '名称' in df.columns:
                        peers = df[df['名称'].str.contains(industry, na=False)]['代码'].tolist() if not df[df['名称'].str.contains(industry, na=False)].empty else []
                    else:
                        peers = []
                else:
                    # 如果没有指定行业，根据股票代码前两位判断行业
                    if len(stock_code) >= 2 and '代码' in df.columns:
                        industry_prefix = stock_code[:2]
                        peers = df[df['代码'].str.startswith(industry_prefix)]['代码'].tolist() if not df[df['代码'].str.startswith(industry_prefix)].empty else []
                    else:
                        peers = []
            else:
                peers = []
            
            # 移除自身
            if stock_code in peers:
                peers.remove(stock_code)
            
            # 限制返回数量
            return peers[:10]
            
        except Exception as e:
            logger.error(f"获取同行业股票失败: {e}")
            return []
    
    def get_industry_data(self, industry_name: str) -> pd.DataFrame:
        """获取行业数据"""
        try:
            # 获取行业数据（这里使用板块数据）
            df = ak.stock_board_industry_name_em()
            industry_info = df[df['板块名称'].str.contains(industry_name, na=False)]
            # 确保返回的是DataFrame类型
            if isinstance(industry_info, pd.DataFrame) and not industry_info.empty:
                return industry_info
            else:
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"获取行业数据失败: {e}")
            return pd.DataFrame()
    
    def calculate_financial_ratios(self, stock_code: str) -> Dict[str, float]:
        """计算关键财务比率"""
        ratios = {}
        
        try:
            # 获取财务指标数据
            indicators_df = self.get_financial_indicators(stock_code)
            
            if not indicators_df.empty:
                # 获取最新一期的数据
                latest_data = indicators_df.iloc[0]
                
                # 盈利能力指标
                roe = latest_data.get('净资产收益率', 0)
                ratios['ROE'] = float(roe) if pd.notna(roe) else 0.0
                
                roa = latest_data.get('总资产报酬率', 0)
                ratios['ROA'] = float(roa) if pd.notna(roa) else 0.0
                
                gross_profit_margin = latest_data.get('销售毛利率', 0)
                ratios['gross_profit_margin'] = float(gross_profit_margin) if pd.notna(gross_profit_margin) else 0.0
                
                net_profit_margin = latest_data.get('销售净利率', 0)
                ratios['net_profit_margin'] = float(net_profit_margin) if pd.notna(net_profit_margin) else 0.0
                
                # 偿债能力指标
                current_ratio = latest_data.get('流动比率', 0)
                ratios['current_ratio'] = float(current_ratio) if pd.notna(current_ratio) else 0.0
                
                quick_ratio = latest_data.get('速动比率', 0)
                ratios['quick_ratio'] = float(quick_ratio) if pd.notna(quick_ratio) else 0.0
                
                debt_to_equity = latest_data.get('资产负债率', 0)
                ratios['debt_to_equity'] = float(debt_to_equity) if pd.notna(debt_to_equity) else 0.0
                
                # 运营效率指标
                asset_turnover = latest_data.get('总资产周转率', 0)
                ratios['asset_turnover'] = float(asset_turnover) if pd.notna(asset_turnover) else 0.0
                
                inventory_turnover = latest_data.get('存货周转率', 0)
                ratios['inventory_turnover'] = float(inventory_turnover) if pd.notna(inventory_turnover) else 0.0
                
                logger.info(f"财务比率计算完成: {stock_code}")
                
        except Exception as e:
            logger.error(f"计算财务比率失败: {e}")
        
        return ratios
    
    def generate_comprehensive_report(self, stock_code: str, years: int = 3) -> Dict:
        """生成综合财务数据报告"""
        report = {
            'stock_code': stock_code,
            'basic_info': None,
            'price_data': None,
            'financial_reports': {},
            'financial_indicators': None,
            'financial_analysis': None,
            'calculated_ratios': None,
            'peers': [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # 获取基本信息
            report['basic_info'] = self.get_stock_basic_info(stock_code)
            
            # 获取价格数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=365*years)).strftime('%Y%m%d')
            report['price_data'] = self.get_stock_daily_data(stock_code, start_date, end_date)
            
            # 获取财务报表
            report['financial_reports'] = self.get_financial_report(stock_code)
            
            # 获取财务指标
            report['financial_indicators'] = self.get_financial_indicators(stock_code)
            
            # 获取财务分析
            report['financial_analysis'] = self.get_financial_analysis(stock_code)
            
            # 计算财务比率
            report['calculated_ratios'] = self.calculate_financial_ratios(stock_code)
            
            # 获取同行业股票
            report['peers'] = self.get_stock_peers(stock_code)
            
            logger.info(f"综合报告生成完成: {stock_code}")
            
        except Exception as e:
            logger.error(f"生成综合报告失败: {e}")
        
        return report


# 使用示例函数
def example_usage():
    """基础使用示例"""
    fetcher = AKShareDataFetcher()
    
    # 示例：获取贵州茅台数据
    stock_code = "600519"
    
    print(f"=== 获取 {stock_code} 数据 ===")
    
    # 获取基本信息
    basic_info = fetcher.get_stock_basic_info(stock_code)
    print(f"基本信息: {basic_info}")
    
    # 获取财务报表
    reports = fetcher.get_financial_report(stock_code)
    print(f"财务报表: {list(reports.keys())}")
    
    # 计算财务比率
    ratios = fetcher.calculate_financial_ratios(stock_code)
    print(f"财务比率: {ratios}")
    
    # 获取同行业股票
    peers = fetcher.get_stock_peers(stock_code, "白酒")
    print(f"同行业股票: {peers}")

def example_enhanced_usage():
    """增强版使用示例"""
    print("=== 增强版AKShare数据获取工具示例 ===")
    
    fetcher = AKShareDataFetcher(save_dir="./enhanced_examples")
    
    # 1. 实时行情数据获取
    print("\n1. 实时行情数据获取示例")
    stocks = ['600519', '000858', '300750', '688036', '832175']
    for stock_code in stocks:
        basic_info = fetcher.get_stock_basic_info(stock_code)
        if not basic_info.empty:
            name_series = basic_info.get('名称', pd.Series(['']))
            price_series = basic_info.get('最新价', pd.Series([0]))
            # 检查Series是否为空
            if isinstance(name_series, pd.Series) and isinstance(price_series, pd.Series):
                if not name_series.empty and not price_series.empty:
                    name = name_series.iloc[0] if len(name_series) > 0 else ''
                    price = price_series.iloc[0] if len(price_series) > 0 else 0
                    print(f"   ✓ {stock_code} ({name}): {price:.2f}元")
                else:
                    print(f"   ✗ {stock_code}: 未找到信息")
            else:
                print(f"   ✗ {stock_code}: 未找到信息")
        else:
            print(f"   ✗ {stock_code}: 未找到信息")
    
    # 2. 市场总览
    print("\n2. 市场总观数据获取示例")
    market_data = fetcher.get_market_overview()
    print(f"   成功获取 {len(market_data)} 个市场的数据")
    
    # 3. 市场统计
    print("\n3. 市场统计分析示例")
    stats = fetcher.get_market_statistics()
    if stats:
        market_summary = stats.get('market_summary', {})
        print(f"   总股票数: {stats.get('total_stocks', 0)}")
        print(f"   总市值: {market_summary.get('total_market_cap', 0)/1000000000000:.2f}万亿元")
        print(f"   上涨家数: {market_summary.get('up_count', 0)}")
        print(f"   下跌家数: {market_summary.get('down_count', 0)}")
    
    # 4. 多年财务分析
    print("\n4. 多年财务分析示例")
    stock_code = "600519"
    multi_year_data = fetcher.get_multi_year_financial_data(stock_code, years=3)
    for report_type, df in multi_year_data.items():
        if not df.empty:
            unique_years = df['报告年份'].nunique()
            print(f"   {report_type}: {unique_years} 年数据")
    
    # 5. 财务摘要分析
    print("\n5. 财务摘要分析示例")
    summary = fetcher.get_financial_summary(stock_code, years=3)
    if summary:
        trends = summary.get('financial_trends', {})
        print(f"   营收趋势: {trends.get('revenue_trend', '未知')}")
        print(f"   利润趋势: {trends.get('profit_trend', '未知')}")
        print(f"   负债水平: {trends.get('debt_level', '未知')}")
        
        risks = summary.get('risk_indicators', {})
        print(f"   整体风险: {risks.get('overall_risk', '未知')}")
    
    # 6. 综合报告生成
    print("\n6. 综合报告生成示例")
    comprehensive_report = fetcher.generate_comprehensive_report(stock_code, years=3)
    if comprehensive_report:
        print(f"   报告生成完成，包含以下数据:")
        print(f"   - 基本信息: {'√' if comprehensive_report.get('basic_info') is not None else '✗'}")
        print(f"   - 价格数据: {'√' if comprehensive_report.get('price_data') is not None else '✗'}")
        print(f"   - 财务报表: {len(comprehensive_report.get('financial_reports', {}))} 种")
        print(f"   - 财务指标: {'√' if comprehensive_report.get('financial_indicators') is not None else '✗'}")
        print(f"   - 财务比率: {'√' if comprehensive_report.get('calculated_ratios') else '✗'}")
        print(f"   - 同行业股票: {len(comprehensive_report.get('peers', []))} 只")


if __name__ == "__main__":
    print("请选择运行示例:")
    print("1. 基础使用示例")
    print("2. 增强版使用示例")
    print("3. 运行综合示例（推荐）")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        example_usage()
    elif choice == "2":
        example_enhanced_usage()
    elif choice == "3":
        # 运行综合示例
        try:
            from comprehensive_examples import main as run_comprehensive
            run_comprehensive()
        except ImportError:
            print("未找到综合示例文件，运行增强版示例")
            example_enhanced_usage()
    else:
        print("无效选择，运行基础示例")
        example_usage()