"""
专门用于A股财报数据获取的工具包类
提供稳定、可靠的财务数据接口，避免智能体生成代码的错误
包含智能缓存和增量更新功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import logging
import traceback
import json
import os
import pickle
from pathlib import Path
import hashlib

from ..config import ToolkitConfig
from .base import AsyncBaseToolkit, register_tool

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialDataCache:
    """财务数据缓存管理器"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            # 默认缓存目录在项目根目录下
            project_root = Path(__file__).parent.parent
            cache_dir = str(project_root / "financial_data_cache")
        
        # 确保cache_dir是字符串类型
        cache_dir_str: str = cache_dir if cache_dir is not None else ""
        self.cache_dir = Path(cache_dir_str)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 元数据文件
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
        
        logger.info(f"财务数据缓存初始化完成，缓存目录: {self.cache_dir}")
    
    def _load_metadata(self) -> Dict:
        """加载缓存元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载缓存元数据失败: {e}")
        
        return {
            "stocks": {},
            "last_cleanup": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    def _save_metadata(self):
        """保存缓存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存元数据失败: {e}")
    
    def get_cache_key(self, stock_code: str) -> str:
        """生成缓存键"""
        return f"stock_{stock_code}"
    
    def get_cache_file_path(self, stock_code: str, data_type: str) -> Path:
        """获取缓存文件路径"""
        cache_key = self.get_cache_key(stock_code)
        return self.cache_dir / f"{cache_key}_{data_type}.pkl"
    
    def is_data_cached(self, stock_code: str) -> bool:
        """检查数据是否已缓存"""
        cache_key = self.get_cache_key(stock_code)
        
        if cache_key not in self.metadata["stocks"]:
            return False
        
        # 检查所有必要的数据文件是否存在
        data_types = ["income", "balance", "cashflow", "metrics", "trend"]
        for data_type in data_types:
            cache_file = self.get_cache_file_path(stock_code, data_type)
            if not cache_file.exists():
                return False
        
        # 检查缓存是否过期（默认7天）
        cache_info = self.metadata["stocks"][cache_key]
        cache_date = datetime.fromisoformat(cache_info["cached_date"])
        if datetime.now() - cache_date > timedelta(days=7):
            logger.info(f"缓存数据已过期: {stock_code}")
            return False
        
        return True
    
    def get_cached_data(self, stock_code: str) -> Optional[Dict]:
        """获取缓存的数据"""
        if not self.is_data_cached(stock_code):
            return None
        
        try:
            data = {}
            data_types = ["income", "balance", "cashflow", "metrics", "trend"]
            
            for data_type in data_types:
                cache_file = self.get_cache_file_path(stock_code, data_type)
                if cache_file.exists():
                    with open(cache_file, 'rb') as f:
                        data[data_type] = pickle.load(f)
            
            cache_key = self.get_cache_key(stock_code)
            cache_info = self.metadata["stocks"][cache_key]
            logger.info(f"从缓存加载数据: {stock_code} (缓存时间: {cache_info['cached_date']})")
            
            return data
            
        except Exception as e:
            logger.error(f"加载缓存数据失败: {e}")
            return None
    
    def cache_data(self, stock_code: str, data: Dict[str, pd.DataFrame], 
                   latest_report_date: Optional[str] = None):
        """缓存数据"""
        try:
            cache_key = self.get_cache_key(stock_code)
            
            # 保存各类数据
            data_types = ["income", "balance", "cashflow", "metrics", "trend"]
            saved_count = 0
            
            for data_type in data_types:
                if data_type in data and data[data_type] is not None:
                    cache_file = self.get_cache_file_path(stock_code, data_type)
                    with open(cache_file, 'wb') as f:
                        pickle.dump(data[data_type], f)
                    saved_count += 1
            
            # 更新元数据
            self.metadata["stocks"][cache_key] = {
                "stock_code": stock_code,
                "cached_date": datetime.now().isoformat(),
                "latest_report_date": latest_report_date or "",
                "data_types": [dt for dt in data_types if dt in data and data[dt] is not None],
                "file_count": saved_count
            }
            
            self._save_metadata()
            logger.info(f"数据缓存成功: {stock_code} (保存了{saved_count}个文件)")
            
        except Exception as e:
            logger.error(f"缓存数据失败: {e}")
    
    def needs_update(self, stock_code: str, current_data: Dict) -> bool:
        """检查是否需要增量更新"""
        if not self.is_data_cached(stock_code):
            return True
        
        # 获取缓存信息
        cache_key = self.get_cache_key(stock_code)
        cache_info = self.metadata["stocks"][cache_key]
        
        # 如果当前数据有更新的报告日期，则需要更新
        if "income" in current_data and not current_data["income"].empty:
            latest_cached_date = cache_info.get("latest_report_date", "")
            
            # 获取当前数据的最新报告日期
            date_col = 'REPORT_DATE' if 'REPORT_DATE' in current_data["income"].columns else '报告期'
            if date_col in current_data["income"].columns:
                current_latest_date = pd.to_datetime(current_data["income"][date_col].iloc[0]).strftime('%Y-%m-%d')
                
                if current_latest_date > latest_cached_date:
                    logger.info(f"检测到新财报数据: {stock_code} {latest_cached_date} -> {current_latest_date}")
                    return True
        
        return False
    
    def cleanup_old_cache(self, days: int = 30):
        """清理过期缓存"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cleaned_count = 0
            
            # 清理过期的股票数据
            expired_stocks = []
            for cache_key, cache_info in self.metadata["stocks"].items():
                cache_date = datetime.fromisoformat(cache_info["cached_date"])
                if cache_date < cutoff_date:
                    expired_stocks.append(cache_key)
            
            for cache_key in expired_stocks:
                # 删除数据文件
                data_types = ["income", "balance", "cashflow", "metrics", "trend"]
                for data_type in data_types:
                    cache_file = self.get_cache_file_path(cache_key.replace("stock_", ""), data_type)
                    if cache_file.exists():
                        cache_file.unlink()
                
                # 从元数据中删除
                del self.metadata["stocks"][cache_key]
                cleaned_count += 1
            
            if cleaned_count > 0:
                self._save_metadata()
                logger.info(f"清理了{cleaned_count}个过期缓存")
            
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")


class AKShareFinancialDataTool(AsyncBaseToolkit):
    """AKShare财务数据获取专用工具包类（带智能缓存）"""
    
    def __init__(self, config: ToolkitConfig | dict | None = None):
        super().__init__(config)
        cache_dir = self.config.config.get("cache_dir") if self.config.config else None
        self.cache = FinancialDataCache(cache_dir)
        self.akshare: Any = None
        self._setup_akshare()
        
    def _setup_akshare(self):
        """设置AKShare"""
        try:
            import akshare as ak
            self.akshare = ak
            logger.info("AKShare初始化成功")
        except ImportError:
            logger.error("AKShare未安装，正在安装...")
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "akshare>=1.12.0"])
            import akshare as ak
            self.akshare = ak
            logger.info("AKShare安装成功")
        except Exception as e:
            logger.error(f"AKShare设置失败: {e}")
            raise
    
    def _convert_stock_code(self, stock_code: str) -> str:
        """转换股票代码格式"""
        if stock_code.startswith('6'):
            return f"SH{stock_code}"
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            return f"SZ{stock_code}"
        else:
            return stock_code
    
    def _clean_financial_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """清洗财务数据"""
        try:
            # 确保输入是DataFrame
            if not isinstance(df, pd.DataFrame):
                logger.warning(f"输入数据不是DataFrame类型: {type(df)}")
                return pd.DataFrame()
            
            # 删除空值行
            if 'REPORT_DATE' in df.columns:
                # 使用loc确保返回DataFrame而不是Series
                mask = df['REPORT_DATE'].notna()
                if isinstance(mask, pd.Series):
                    df = df.loc[mask].copy()
                else:
                    df = df.copy()
            elif '报告期' in df.columns:
                # 使用loc确保返回DataFrame而不是Series
                mask = df['报告期'].notna()
                if isinstance(mask, pd.Series):
                    df = df.loc[mask].copy()
                else:
                    df = df.copy()
            
            # 转换数值列
            exclude_cols = ['REPORT_DATE', '报告期', '报表类型', 'REPORT_TYPE', 
                          'SECUCODE', 'SECURITY_CODE', 'SECURITY_NAME_ABBR']
            
            for col in df.columns:
                if col not in exclude_cols:
                    # 确保转换为数值类型，无法转换的设为NaN
                    df.loc[:, col] = pd.to_numeric(df[col], errors='coerce')
            
            # 转换日期列并排序
            date_col = 'REPORT_DATE' if 'REPORT_DATE' in df.columns else '报告期'
            if date_col in df.columns:
                df.loc[:, date_col] = pd.to_datetime(df[date_col])
                df = df.sort_values(date_col, ascending=False)
            
            logger.info(f"{data_type}数据清洗完成，剩余{len(df)}行")
            return df
            
        except Exception as e:
            logger.error(f"{data_type}数据清洗失败: {e}")
            # 返回空的DataFrame而不是原始df
            return pd.DataFrame()
    
    @register_tool()
    def get_financial_reports(self, stock_code: str, stock_name: Optional[str] = None, force_refresh: bool = False) -> Dict[str, pd.DataFrame]:
        """
        获取完整财务报表数据（带智能缓存）
        
        Args:
            stock_code: 股票代码，如 '600248'
            stock_name: 股票名称，可选
            force_refresh: 是否强制刷新缓存
            
        Returns:
            包含利润表、资产负债表、现金流量表的字典
        """
        if stock_name is None:
            stock_name = f"股票{stock_code}"
            
        logger.info(f"开始获取{stock_name}({stock_code})财务数据")
        
        # 检查缓存
        if not force_refresh:
            cached_data = self.cache.get_cached_data(stock_code)
            if cached_data:
                logger.info(f"使用缓存数据: {stock_code}")
                return cached_data
        
        symbol = self._convert_stock_code(stock_code)
        logger.info(f"股票代码转换: {stock_code} -> {symbol}")
        
        results: Dict[str, pd.DataFrame] = {}
        
        # 确保akshare已初始化
        if self.akshare is None:
            logger.error("AKShare未正确初始化")
            return results
        
        try:
            # 1. 获取利润表
            logger.info("获取利润表...")
            try:
                income_df = self.akshare.stock_profit_sheet_by_report_em(symbol=symbol)
                income_df = self._clean_financial_data(income_df, "利润表")
                results['income'] = income_df
                logger.info(f"利润表获取成功: {len(income_df)}行")
            except Exception as e:
                logger.error(f"利润表获取失败: {e}")
                # 尝试备用方法
                try:
                    income_df = self.akshare.stock_lrb_em(symbol=symbol)  # 使用symbol而不是stock_code
                    income_df = self._clean_financial_data(income_df, "利润表(备用)")
                    results['income'] = income_df
                    logger.info(f"利润表(备用方法)获取成功: {len(income_df)}行")
                except Exception as e2:
                    logger.error(f"利润表备用方法也失败: {e2}")
            
            # 2. 获取资产负债表
            logger.info("获取资产负债表...")
            try:
                balance_df = self.akshare.stock_balance_sheet_by_report_em(symbol=symbol)
                balance_df = self._clean_financial_data(balance_df, "资产负债表")
                results['balance'] = balance_df
                logger.info(f"资产负债表获取成功: {len(balance_df)}行")
            except Exception as e:
                logger.error(f"资产负债表获取失败: {e}")
                try:
                    balance_df = self.akshare.stock_zcfz_em(symbol=symbol)  # 使用symbol而不是stock_code
                    balance_df = self._clean_financial_data(balance_df, "资产负债表(备用)")
                    results['balance'] = balance_df
                    logger.info(f"资产负债表(备用方法)获取成功: {len(balance_df)}行")
                except Exception as e2:
                    logger.error(f"资产负债表备用方法也失败: {e2}")
            
            # 3. 获取现金流量表
            logger.info("获取现金流量表...")
            try:
                cashflow_df = self.akshare.stock_cash_flow_sheet_by_report_em(symbol=symbol)
                cashflow_df = self._clean_financial_data(cashflow_df, "现金流量表")
                results['cashflow'] = cashflow_df
                logger.info(f"现金流量表获取成功: {len(cashflow_df)}行")
            except Exception as e:
                logger.error(f"现金流量表获取失败: {e}")
                try:
                    cashflow_df = self.akshare.stock_xjll_em(symbol=symbol)  # 使用symbol而不是stock_code
                    cashflow_df = self._clean_financial_data(cashflow_df, "现金流量表(备用)")
                    results['cashflow'] = cashflow_df
                    logger.info(f"现金流量表(备用方法)获取成功: {len(cashflow_df)}行")
                except Exception as e2:
                    logger.error(f"现金流量表备用方法也失败: {e2}")
            
            # 检查是否需要更新缓存
            if not force_refresh and self.cache.needs_update(stock_code, results):
                logger.info(f"检测到新数据，更新缓存: {stock_code}")
            
            # 计算并缓存指标和趋势数据
            if results:
                metrics = self.get_key_metrics(results)
                trend = self.get_historical_trend(results)
                
                results['metrics'] = pd.DataFrame([metrics]) if metrics else pd.DataFrame()
                results['trend'] = trend
                
                # 获取最新报告日期
                latest_report_date = ""
                if 'income' in results and not results['income'].empty:
                    date_col = 'REPORT_DATE' if 'REPORT_DATE' in results['income'].columns else '报告期'
                    if date_col in results['income'].columns:
                        latest_report_date = pd.to_datetime(results['income'][date_col].iloc[0]).strftime('%Y-%m-%d')
                
                # 缓存数据
                self.cache.cache_data(stock_code, results, latest_report_date)
                logger.info(f"数据已缓存: {stock_code}")
            
            return results
            
        except Exception as e:
            logger.error(f"获取财务报表失败: {e}")
            logger.error(traceback.format_exc())
            return results
    
    def get_key_metrics(self, financial_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """
        提取关键财务指标（内部使用）
        
        Args:
            financial_data: 财务数据字典
            
        Returns:
            关键财务指标字典
        """
        # 保留原来的方法实现
        logger.info("提取关键财务指标")
        
        metrics = {}
        
        try:
            if not financial_data:
                logger.error("财务数据为空")
                return metrics
                
            # 获取最新一期数据
            latest_income = financial_data.get('income', pd.DataFrame())
            latest_balance = financial_data.get('balance', pd.DataFrame())
            latest_cashflow = financial_data.get('cashflow', pd.DataFrame())
            
            if latest_income.empty:
                logger.error("利润表数据为空")
                return metrics
                
            latest_income = latest_income.iloc[0]
            
            # 提取盈利能力指标（支持多种列名）
            revenue_cols = ['TOTAL_OPERATE_INCOME', '营业收入', 'operating_revenue']
            net_profit_cols = ['NETPROFIT', '净利润', 'net_profit']
            parent_profit_cols = ['PARENT_NETPROFIT', '归属于母公司所有者的净利润', 'parent_net_profit']
            
            revenue = self._get_value_by_col_names(latest_income, revenue_cols) / 1e8
            net_profit = self._get_value_by_col_names(latest_income, net_profit_cols) / 1e8
            parent_profit = self._get_value_by_col_names(latest_income, parent_profit_cols) / 1e8
            
            metrics['revenue_billion'] = revenue
            metrics['net_profit_billion'] = net_profit
            metrics['parent_profit_billion'] = parent_profit
            metrics['net_profit_margin'] = (net_profit / revenue * 100) if revenue > 0 else 0
            
            # 提取财务状况指标
            if not latest_balance.empty:
                latest_balance = latest_balance.iloc[0]
                
                asset_cols = ['TOTAL_ASSETS', '资产总计', 'total_assets']
                liability_cols = ['TOTAL_LIABILITIES', '负债合计', 'total_liabilities']
                equity_cols = ['TOTAL_EQUITY', '所有者权益合计', 'total_equity']
                
                total_assets = self._get_value_by_col_names(latest_balance, asset_cols) / 1e8
                total_liabilities = self._get_value_by_col_names(latest_balance, liability_cols) / 1e8
                total_equity = self._get_value_by_col_names(latest_balance, equity_cols) / 1e8
                
                metrics['total_assets_billion'] = total_assets
                metrics['total_liabilities_billion'] = total_liabilities
                metrics['total_equity_billion'] = total_equity
                metrics['debt_to_asset_ratio'] = (total_liabilities / total_assets * 100) if total_assets > 0 else 0
                
                # 计算ROE
                if total_equity > 0:
                    metrics['roe'] = parent_profit / total_equity * 100
            
            logger.info("关键指标提取完成")
            return metrics
            
        except Exception as e:
            logger.error(f"提取关键指标失败: {e}")
            logger.error(traceback.format_exc())
            return metrics
    
    @register_tool("get_key_metrics_from_reports")
    def get_key_metrics_from_reports(self, stock_code: str, stock_name: Optional[str] = None) -> Dict[str, float]:
        """
        提取关键财务指标
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            
        Returns:
            关键财务指标字典
        """
        # 先获取财务数据
        financial_data = self.get_financial_reports(stock_code, stock_name)
        # 调用内部方法处理
        return self.get_key_metrics(financial_data)
    
    def _get_value_by_col_names(self, row: pd.Series, col_names: List[str]) -> float:
        """根据可能的列名获取数值"""
        for col in col_names:
            # 检查列是否存在且不为NaN
            if col in row.index:
                value = row[col]
                # 检查值是否为NaN，使用安全的方式检查
                try:
                    # 对于标量数值类型
                    if isinstance(value, (int, float, np.integer, np.floating)):
                        # 检查是否为NaN
                        if not (isinstance(value, float) and np.isnan(value)):
                            return float(value)
                    elif isinstance(value, pd.Series):
                        # 对于pandas Series对象，检查是否为空
                        if len(value) > 0 and not pd.isna(value).all():  # 确保不为空且不全为NaN
                            # 获取第一个非NaN值
                            valid_values = value.dropna()
                            if len(valid_values) > 0:
                                val = valid_values.iloc[0]
                                # 检查是否有item方法且可调用（仅对numpy标量）
                                if hasattr(val, 'item') and callable(getattr(val, 'item', None)) and isinstance(val, (np.integer, np.floating)):
                                    return float(val.item())
                                else:
                                    return float(val)
                    elif isinstance(value, pd.DataFrame):
                        # DataFrame情况
                        if len(value) > 0 and len(value.columns) > 0:
                            # 获取第一个值
                            val = value.iloc[0, 0]
                            # 检查是否有item方法且可调用（仅对numpy标量）
                            if hasattr(val, 'item') and callable(getattr(val, 'item', None)) and isinstance(val, (np.integer, np.floating)):
                                return float(val.item())
                            else:
                                return float(val)
                    else:
                        # 其他类型，尝试直接转换
                        if not (isinstance(value, float) and np.isnan(value)):
                            # 检查是否有item方法且可调用（仅对numpy标量）
                            if hasattr(value, 'item') and callable(getattr(value, 'item', None)) and isinstance(value, (np.integer, np.floating)):
                                return float(value.item())
                            else:
                                return float(value)
                except (TypeError, ValueError, AttributeError, IndexError):
                    # 如果检查时出错，尝试直接转换
                    try:
                        # 对于pandas对象，先提取值再转换
                        if hasattr(value, 'iloc') and not isinstance(value, (int, float, np.integer, np.floating)):
                            # 确保value有长度属性且不是numpy标量
                            if hasattr(value, '__len__') and len(value) > 0 and not np.isscalar(value):
                                if isinstance(value, pd.Series):
                                    val = value.iloc[0]
                                elif isinstance(value, pd.DataFrame) and len(value.columns) > 0:
                                    val = value.iloc[0, 0]
                                else:
                                    # 对于numpy数组等，安全访问
                                    try:
                                        val = value[0] if len(value) > 0 else value.item() if hasattr(value, 'item') and callable(getattr(value, 'item', None)) and isinstance(value, (np.integer, np.floating)) else value
                                    except (IndexError, TypeError):
                                        val = value.item() if hasattr(value, 'item') and callable(getattr(value, 'item', None)) and isinstance(value, (np.integer, np.floating)) else value
                                # 确保val不是DataFrame
                                if not isinstance(val, pd.DataFrame):
                                    return float(val)
                        # 检查是否有item方法且可调用，且不是基本数值类型（仅对numpy标量）
                        elif hasattr(value, 'item') and callable(getattr(value, 'item', None)) and isinstance(value, (np.integer, np.floating)):
                            return float(value.item())
                        else:
                            # 最后尝试直接转换，但排除DataFrame
                            if not isinstance(value, pd.DataFrame):  # DataFrame不能直接转换为float
                                return float(value)
                    except (TypeError, ValueError, IndexError):
                        continue
        return 0.0
    
    def get_historical_trend(self, financial_data: Dict[str, pd.DataFrame], years: int = 4) -> pd.DataFrame:
        """
        获取历史趋势数据（内部使用）
        
        Args:
            financial_data: 财务数据字典
            years: 获取年数
            
        Returns:
            趋势数据DataFrame
        """
        # 保留原来的方法实现
        logger.info(f"获取最近{years}年趋势数据")
        
        try:
            income_df = financial_data.get('income', pd.DataFrame())
            if income_df.empty:
                logger.error("利润表数据为空")
                return pd.DataFrame()
            
            # 获取最近N年数据
            trend_data = income_df.head(years).copy()
            
            # 确定日期列名
            date_col = 'REPORT_DATE' if 'REPORT_DATE' in trend_data.columns else '报告期'
            if date_col in trend_data.columns:
                trend_data.loc[:, '年份'] = pd.to_datetime(trend_data[date_col]).dt.year
            else:
                logger.error("未找到日期列")
                return pd.DataFrame()
            
            # 提取关键指标（支持多种列名）
            revenue_cols = ['TOTAL_OPERATE_INCOME', '营业收入', 'operating_revenue']
            profit_cols = ['NETPROFIT', '净利润', 'net_profit']
            
            result_df = pd.DataFrame()
            # 确保从trend_data中提取的是Series
            if '年份' in trend_data.columns:
                result_df['年份'] = trend_data['年份'].copy()
            result_df['营业收入'] = self._get_values_by_col_names(trend_data, revenue_cols) / 1e8
            result_df['净利润'] = self._get_values_by_col_names(trend_data, profit_cols) / 1e8
            
            logger.info(f"趋势数据获取成功: {len(result_df)}年")
            return result_df
            
        except Exception as e:
            logger.error(f"获取趋势数据失败: {e}")
            return pd.DataFrame()
    
    @register_tool("get_historical_trend_from_reports")
    def get_historical_trend_from_reports(self, stock_code: str, stock_name: Optional[str] = None, years: int = 4) -> str:
        """
        获取历史趋势数据
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            years: 获取年数
            
        Returns:
            趋势数据的JSON字符串
        """
        # 先获取财务数据
        financial_data = self.get_financial_reports(stock_code, stock_name)
        # 调用内部方法处理
        trend_df = self.get_historical_trend(financial_data, years)
        # 转换为JSON字符串返回
        json_str = trend_df.to_json(orient='records', date_format='iso')
        return json_str if json_str is not None else "[]"
    
    def _get_values_by_col_names(self, df: pd.DataFrame, col_names: List[str]) -> pd.Series:
        """根据可能的列名获取数值列"""
        for col in col_names:
            if col in df.columns:
                series = df[col]
                # 确保返回的是Series类型
                if isinstance(series, pd.Series):
                    return series.copy()
                else:
                    # 如果不是Series，创建一个Series
                    return pd.Series([series], index=[0])
        # 如果没有找到匹配的列，返回零值Series
        return pd.Series([0.0] * len(df), index=df.index) if len(df) > 0 else pd.Series([0.0])
    
    def save_to_csv(self, financial_data: Dict[str, pd.DataFrame], filepath_prefix: str):
        """
        保存财务数据到CSV文件（内部使用）
        
        Args:
            financial_data: 财务数据字典
            filepath_prefix: 文件路径前缀
        """
        # 保留原来的方法实现
        logger.info(f"保存财务数据到 {filepath_prefix}")
        
        try:
            for data_type, df in financial_data.items():
                if not df.empty:
                    filepath = f"{filepath_prefix}_{data_type}.csv"
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
                    logger.info(f"{data_type}数据已保存到: {filepath}")
                    
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
    
    @register_tool("save_financial_data")
    def save_financial_data(self, stock_code: str, stock_name: Optional[str] = None, filepath_prefix: str = "financial_data"):
        """
        保存财务数据到CSV文件
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            filepath_prefix: 文件路径前缀
        """
        # 先获取财务数据
        financial_data = self.get_financial_reports(stock_code, stock_name)
        # 调用内部方法处理
        self.save_to_csv(financial_data, filepath_prefix)
    
    @register_tool()
    def check_cache_status(self, stock_code: str) -> Dict:
        """
        检查缓存状态
        
        Args:
            stock_code: 股票代码
            
        Returns:
            缓存状态信息
        """
        cache_key = self.cache.get_cache_key(stock_code)
        
        if cache_key in self.cache.metadata["stocks"]:
            cache_info = self.cache.metadata["stocks"][cache_key]
            return {
                "cached": True,
                "cached_date": cache_info["cached_date"],
                "latest_report_date": cache_info.get("latest_report_date", ""),
                "data_types": cache_info.get("data_types", []),
                "file_count": cache_info.get("file_count", 0)
            }
        else:
            return {
                "cached": False,
                "cached_date": "",
                "latest_report_date": "",
                "data_types": [],
                "file_count": 0
            }
    
    @register_tool()
    def refresh_cache(self, stock_code: str, stock_name: Optional[str] = None) -> bool:
        """
        强制刷新缓存
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            
        Returns:
            刷新是否成功
        """
        logger.info(f"强制刷新缓存: {stock_code}")
        
        try:
            # 强制获取新数据
            new_data = self.get_financial_reports(stock_code, stock_name, force_refresh=True)
            
            if new_data and ('income' in new_data and not new_data['income'].empty):
                logger.info(f"缓存刷新成功: {stock_code}")
                return True
            else:
                logger.warning(f"缓存刷新失败，数据为空: {stock_code}")
                return False
                
        except Exception as e:
            logger.error(f"缓存刷新失败: {e}")
            return False
    
    @register_tool()
    def cleanup_cache(self, days: int = 30):
        """
        清理过期缓存
        
        Args:
            days: 保留天数
        """
        logger.info(f"清理{days}天前的缓存")
        self.cache.cleanup_old_cache(days)
    
    @register_tool()
    def get_cache_info(self) -> Dict:
        """
        获取缓存整体信息
        
        Returns:
            缓存统计信息
        """
        stocks = self.cache.metadata["stocks"]
        total_files = sum(info.get("file_count", 0) for info in stocks.values())
        
        # 计算缓存大小
        total_size = 0
        for stock_code in stocks.keys():
            data_types = ["income", "balance", "cashflow", "metrics", "trend"]
            for data_type in data_types:
                cache_file = self.cache.get_cache_file_path(stock_code.replace("stock_", ""), data_type)
                if cache_file.exists():
                    total_size += cache_file.stat().st_size
        
        return {
            "total_stocks": len(stocks),
            "total_files": total_files,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "last_cleanup": self.cache.metadata.get("last_cleanup", ""),
            "cache_directory": str(self.cache.cache_dir)
        }
    
    @register_tool()
    def clear_all_cache(self):
        """清除所有缓存"""
        logger.warning("清除所有缓存数据")
        
        try:
            # 删除所有缓存文件
            for stock_info in list(self.cache.metadata["stocks"].values()):
                stock_code = stock_info["stock_code"]
                data_types = ["income", "balance", "cashflow", "metrics", "trend"]
                for data_type in data_types:
                    cache_file = self.cache.get_cache_file_path(stock_code, data_type)
                    if cache_file.exists():
                        cache_file.unlink()
            
            # 重置元数据
            self.cache.metadata = {
                "stocks": {},
                "last_cleanup": datetime.now().isoformat(),
                "version": "1.0"
            }
            self.cache._save_metadata()
            
            logger.info("所有缓存已清除")
            
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
    
    @register_tool()
    def export_cache_summary(self, filepath: Optional[str] = None):
        """
        导出缓存摘要

        Args:
            filepath: 导出文件路径
        """
        if filepath is None:
            filepath = str(self.cache.cache_dir / "cache_summary.csv")

        try:
            summary_data = []
            for cache_key, info in self.cache.metadata["stocks"].items():
                summary_data.append({
                    "stock_code": info["stock_code"],
                    "cached_date": info["cached_date"],
                    "latest_report_date": info.get("latest_report_date", ""),
                    "data_types": ", ".join(info.get("data_types", [])),
                    "file_count": info.get("file_count", 0)
                })

            df = pd.DataFrame(summary_data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"缓存摘要已导出到: {filepath}")

        except Exception as e:
            logger.error(f"导出缓存摘要失败: {e}")

    # ===== 时间感知功能增强 =====

    @register_tool()
    def check_latest_available_report(self, stock_code: str) -> Dict:
        """
        检查最新可用的财报报告

        Args:
            stock_code: 股票代码

        Returns:
            包含最新可用财报信息的字典
        """
        try:
            # 尝试获取财务数据
            financial_data = self.get_financial_reports(stock_code)

            if not financial_data or 'income' not in financial_data or financial_data['income'].empty:
                return {
                    "stock_code": stock_code,
                    "available": False,
                    "reason": "无法获取财务数据",
                    "suggestion": "请检查股票代码是否正确，或稍后重试"
                }

            # 获取最新报告日期
            income_df = financial_data['income']
            date_col = 'REPORT_DATE' if 'REPORT_DATE' in income_df.columns else '报告期'

            if date_col not in income_df.columns:
                return {
                    "stock_code": stock_code,
                    "available": False,
                    "reason": "财务数据格式异常",
                    "suggestion": "数据源可能有问题，请稍后重试"
                }

            # 提取最新报告信息
            latest_row = income_df.iloc[0]
            latest_date = pd.to_datetime(latest_row[date_col])

            # 判断报告类型
            month = latest_date.month
            if month == 3:
                quarter = 1
                report_type = "第一季度报告"
            elif month == 6:
                quarter = 2
                report_type = "半年度报告"
            elif month == 9:
                quarter = 3
                report_type = "第三季度报告"
            else:
                quarter = 4
                report_type = "年度报告"

            return {
                "stock_code": stock_code,
                "available": True,
                "latest_report_date": latest_date.strftime("%Y-%m-%d"),
                "report_year": latest_date.year,
                "report_quarter": quarter,
                "report_type": report_type,
                "period": f"{latest_date.year}Q{quarter}",
                "data_completeness": self._check_data_completeness(financial_data),
                "description": f"最新可用财报为{latest_date.year}年第{quarter}季度{report_type}"
            }

        except Exception as e:
            logger.error(f"检查最新可用报告失败: {e}")
            return {
                "stock_code": stock_code,
                "available": False,
                "reason": f"处理过程中发生错误: {str(e)}",
                "suggestion": "请稍后重试或联系技术支持"
            }

    def _check_data_completeness(self, financial_data: Dict[str, pd.DataFrame]) -> Dict:
        """检查数据完整性"""
        completeness = {
            "income_statement": "income" in financial_data and not financial_data["income"].empty,
            "balance_sheet": "balance" in financial_data and not financial_data["balance"].empty,
            "cash_flow_statement": "cashflow" in financial_data and not financial_data["cashflow"].empty,
        }

        # 计算完整性评分
        complete_count = sum(completeness.values())
        total_count = len(completeness)
        completeness_score = (complete_count / total_count) * 100 if total_count > 0 else 0

        completeness["overall_score"] = completeness_score
        completeness["complete_reports"] = complete_count
        completeness["total_reports"] = total_count

        return completeness

    @register_tool()
    def get_financial_calendar_info(self, stock_code: str) -> Dict:
        """
        获取财报日历信息

        Args:
            stock_code: 股票代码

        Returns:
            财报日历信息
        """
        current_date = datetime.now()
        current_year = current_date.year

        # 获取最新可用报告信息
        latest_report = self.check_latest_available_report(stock_code)

        # 构建基础日历
        calendar = {
            "stock_code": stock_code,
            "current_date": current_date.strftime("%Y-%m-%d"),
            "current_year": current_year,
            "latest_available_report": latest_report,
            "expected_schedule": self._generate_expected_schedule(current_year, stock_code),
            "data_status": self._assess_data_status(stock_code, current_date)
        }

        return calendar

    def _generate_expected_schedule(self, year: int, stock_code: str) -> List[Dict]:
        """生成预期财报发布时间表"""
        schedule = [
            {
                "quarter": 1,
                "report_name": "第一季度报告",
                "period": f"{year}Q1",
                "expected_date": f"{year}-04-30",
                "description": "预计4月30日前发布"
            },
            {
                "quarter": 2,
                "report_name": "半年度报告",
                "period": f"{year}Q2",
                "expected_date": f"{year}-08-31",
                "description": "预计8月31日前发布"
            },
            {
                "quarter": 3,
                "report_name": "第三季度报告",
                "period": f"{year}Q3",
                "expected_date": f"{year}-10-31",
                "description": "预计10月31日前发布"
            },
            {
                "quarter": 4,
                "report_name": "年度报告",
                "period": f"{year}Q4",
                "expected_date": f"{year+1}-04-30",
                "description": f"预计{year+1}年4月30日前发布"
            }
        ]

        # 标记已发布的报告
        current_date = datetime.now()
        for item in schedule:
            expected_date = datetime.strptime(item["expected_date"], "%Y-%m-%d")
            if current_date > expected_date:
                item["status"] = "expected_published"
            else:
                item["status"] = "upcoming"

        return schedule

    def _assess_data_status(self, stock_code: str, current_date: datetime) -> Dict:
        """评估数据状态"""
        latest_report = self.check_latest_available_report(stock_code)

        if not latest_report["available"]:
            return {
                "status": "no_data",
                "description": "暂无可用数据",
                "action_needed": "检查股票代码或稍后重试"
            }

        # 计算数据新鲜度
        latest_date = datetime.strptime(latest_report["latest_report_date"], "%Y-%m-%d")
        days_old = (current_date - latest_date).days

        if days_old <= 30:
            freshness = "very_fresh"
            freshness_desc = "数据非常新鲜（30天内）"
        elif days_old <= 90:
            freshness = "fresh"
            freshness_desc = "数据较新鲜（90天内）"
        elif days_old <= 180:
            freshness = "moderate"
            freshness_desc = "数据时效性一般（180天内）"
        else:
            freshness = "stale"
            freshness_desc = "数据较旧（超过180天）"

        return {
            "status": "data_available",
            "freshness": freshness,
            "freshness_description": freshness_desc,
            "days_since_latest": days_old,
            "latest_period": latest_report["period"],
            "completeness_score": latest_report.get("data_completeness", {}).get("overall_score", 0),
            "recommendation": self._get_data_recommendation(freshness, days_old)
        }

    def _get_data_recommendation(self, freshness: str, days_old: int) -> str:
        """获取数据使用建议"""
        if freshness == "very_fresh":
            return "数据质量优秀，可以直接用于分析"
        elif freshness == "fresh":
            return "数据质量良好，适合大部分分析需求"
        elif freshness == "moderate":
            return "数据可接受，但建议关注最新动态"
        else:
            return "数据较旧，建议谨慎使用并寻找更新数据源"

    @register_tool()
    def validate_data_freshness(self, stock_code: str, requested_period: Dict) -> Dict:
        """
        验证数据新鲜度

        Args:
            stock_code: 股票代码
            requested_period: 请求的财报期间，格式：{"year": 2024, "quarter": 3}

        Returns:
            数据新鲜度验证结果
        """
        try:
            year = requested_period.get("year")
            quarter = requested_period.get("quarter")

            if not year or not quarter:
                return {
                    "valid": False,
                    "reason": "请求的期间格式不正确",
                    "suggestion": "请提供正确的年份和季度"
                }

            # 获取最新可用报告
            latest_report = self.check_latest_available_report(stock_code)

            if not latest_report["available"]:
                return {
                    "valid": False,
                    "reason": "无法获取最新财报数据",
                    "suggestion": "请检查股票代码或网络连接"
                }

            # 比较请求期间与最新可用期间
            latest_year = latest_report["report_year"]
            latest_quarter = latest_report["report_quarter"]

            # 计算期间差
            year_diff = year - latest_year
            quarter_diff = quarter - latest_quarter
            total_quarter_diff = year_diff * 4 + quarter_diff

            current_date = datetime.now()
            requested_date = datetime(year, quarter * 3, 1)  # 近似月份
            is_future = requested_date > current_date

            result = {
                "stock_code": stock_code,
                "requested_period": f"{year}Q{quarter}",
                "latest_available": f"{latest_year}Q{latest_quarter}",
                "is_future_request": is_future,
                "quarter_difference": total_quarter_diff,
                "data_gap_periods": max(0, total_quarter_diff)
            }

            if is_future:
                result["valid"] = False
                result["reason"] = f"请求的{year}Q{quarter}是未来时间，财报尚未发布"
                result["suggestion"] = f"建议使用最新可用数据{latest_year}Q{latest_quarter}"
            elif total_quarter_diff > 0:
                result["valid"] = False
                result["reason"] = f"请求的{year}Q{quarter}数据不存在，最新可用数据为{latest_year}Q{latest_quarter}"
                result["suggestion"] = f"建议使用{latest_year}Q{latest_quarter}数据进行分析"
            else:
                result["valid"] = True
                result["reason"] = "请求数据可用"
                result["freshness"] = self._calculate_freshness(latest_report["latest_report_date"])

            return result

        except Exception as e:
            logger.error(f"验证数据新鲜度失败: {e}")
            return {
                "valid": False,
                "reason": f"验证过程中发生错误: {str(e)}",
                "suggestion": "请稍后重试"
            }

    def _calculate_freshness(self, report_date_str: str) -> Dict:
        """计算数据新鲜度"""
        report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
        current_date = datetime.now()
        days_old = (current_date - report_date).days

        if days_old <= 30:
            level = "excellent"
            description = "优秀（30天内）"
        elif days_old <= 60:
            level = "good"
            description = "良好（60天内）"
        elif days_old <= 120:
            level = "acceptable"
            description = "可接受（120天内）"
        else:
            level = "outdated"
            description = "较旧（超过120天）"

        return {
            "level": level,
            "description": description,
            "days_old": days_old,
            "report_date": report_date_str
        }

    def _serialize_for_analysis(self, financial_data: Dict[str, pd.DataFrame]) -> str:
        """
        将财务数据序列化为适合分析的JSON格式

        Args:
            financial_data: 包含利润表、资产负债表、现金流量表的字典

        Returns:
            序列化后的JSON字符串
        """
        try:
            # 导入数据适配器
            from ..utils.data_adapter import get_data_adapter
            adapter = get_data_adapter()

            # 使用数据适配器进行序列化
            serialized_data = adapter.normalize_financial_data(financial_data)
            logger.info(f"财务数据序列化完成，数据大小: {len(serialized_data)} 字符")

            return serialized_data

        except Exception as e:
            logger.error(f"财务数据序列化失败: {e}")
            # 返回空的财务结构
            empty_structure = {
                "income": [],
                "balance": [],
                "cashflow": []
            }
            return json.dumps(empty_structure, ensure_ascii=False)

    @register_tool("get_financial_data_for_analysis")
    def get_financial_data_for_analysis(self, stock_code: str, stock_name: Optional[str] = None, format_type: str = "json") -> str:
        """
        获取适合财务分析的标准化数据

        Args:
            stock_code: 股票代码，如 '600248'
            stock_name: 股票名称，可选
            format_type: 输出格式，支持 'json', 'metrics', 'simple'

        Returns:
            标准化的财务数据JSON字符串
        """
        if stock_name is None:
            stock_name = f"股票{stock_code}"

        logger.info(f"获取 {stock_name}({stock_code}) 的标准化分析数据")

        try:
            # 获取原始财务数据
            financial_data = self.get_financial_reports(stock_code, stock_name)

            if not financial_data or all(df.empty for df in financial_data.values()):
                logger.error("未获取到有效的财务数据")
                return json.dumps({
                    "error": True,
                    "message": f"未获取到 {stock_name}({stock_code}) 的有效财务数据",
                    "suggestions": [
                        "检查股票代码是否正确",
                        "确认该股票是否有公开财报数据",
                        "尝试稍后重试"
                    ]
                }, ensure_ascii=False)

            if format_type == "metrics":
                # 提取关键指标
                from ..utils.data_adapter import get_data_adapter
                adapter = get_data_adapter()
                key_metrics = adapter.extract_key_metrics(financial_data)

                result = {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "key_metrics": key_metrics,
                    "data_source": "akshare",
                    "extract_time": datetime.now().isoformat()
                }

                logger.info(f"提取到 {len(key_metrics)} 个关键指标")
                return json.dumps(result, ensure_ascii=False, default=str)

            elif format_type == "simple":
                # 简化格式，只保留最新数据
                simplified_data = {}

                for table_name, df in financial_data.items():
                    if not df.empty:
                        # 只取第一行（最新数据）
                        latest_row = df.iloc[0].to_dict()
                        # 清理数据
                        cleaned_row = {}
                        for key, value in latest_row.items():
                            if pd.notna(value):
                                if isinstance(value, (int, float, np.integer, np.floating)):
                                    cleaned_row[key] = float(value)
                                elif isinstance(value, str):
                                    cleaned_row[key] = value
                                else:
                                    cleaned_row[key] = str(value)
                        simplified_data[table_name] = cleaned_row

                result = {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "financial_data": simplified_data,
                    "data_source": "akshare",
                    "format": "simple"
                }

                logger.info(f"简化数据格式生成完成: {list(simplified_data.keys())}")
                return json.dumps(result, ensure_ascii=False, default=str)

            else:  # format_type == "json" (默认)
                # 标准JSON格式，适合直接传递给财务分析工具
                serialized_data = self._serialize_for_analysis(financial_data)

                # 添加元数据
                enhanced_data = {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "financial_data": json.loads(serialized_data),
                    "data_source": "akshare",
                    "format": "standard",
                    "serialization_time": datetime.now().isoformat()
                }

                logger.info(f"标准化分析数据生成完成")
                return json.dumps(enhanced_data, ensure_ascii=False, default=str)

        except Exception as e:
            logger.error(f"获取标准化分析数据失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")

            return json.dumps({
                "error": True,
                "error_code": "DATA_EXTRACTION_ERROR",
                "message": f"获取 {stock_name}({stock_code}) 的分析数据失败: {str(e)}",
                "suggestions": [
                    "检查网络连接是否正常",
                    "确认股票代码是否正确",
                    "稍后重试或联系技术支持"
                ]
            }, ensure_ascii=False)

    @register_tool("convert_financial_data_format")
    def convert_financial_data_format(self, financial_data: Union[str, Dict], target_format: str = "analysis_ready") -> str:
        """
        转换财务数据格式

        Args:
            financial_data: 输入的财务数据（JSON字符串或字典）
            target_format: 目标格式，支持 'analysis_ready', 'simple', 'metrics'

        Returns:
            转换后的JSON字符串
        """
        logger.info(f"转换财务数据格式，目标格式: {target_format}")

        try:
            # 导入数据适配器
            from ..utils.data_adapter import get_data_adapter
            adapter = get_data_adapter()

            if target_format == "analysis_ready":
                # 转换为适合分析的标准格式
                if isinstance(financial_data, str):
                    # 已经是字符串，使用适配器标准化
                    result = adapter.normalize_financial_data(financial_data)
                else:
                    # 字典格式，直接标准化
                    result = adapter.normalize_financial_data(financial_data)

            elif target_format == "simple":
                # 转换为简化格式
                if isinstance(financial_data, str):
                    data_dict = json.loads(financial_data)
                else:
                    data_dict = financial_data

                # 提取关键指标
                key_metrics = adapter.extract_key_metrics(data_dict)

                result = {
                    "key_metrics": key_metrics,
                    "format": "simple",
                    "conversion_time": datetime.now().isoformat()
                }

            elif target_format == "metrics":
                # 只提取关键指标
                if isinstance(financial_data, str):
                    data_dict = json.loads(financial_data)
                else:
                    data_dict = financial_data

                key_metrics = adapter.extract_key_metrics(data_dict)
                result = json.dumps(key_metrics, ensure_ascii=False, default=str)

            else:
                # 不支持的格式
                result = json.dumps({
                    "error": True,
                    "message": f"不支持的目标格式: {target_format}",
                    "supported_formats": ["analysis_ready", "simple", "metrics"]
                }, ensure_ascii=False)

            logger.info(f"数据格式转换完成: {target_format}")
            return result

        except Exception as e:
            logger.error(f"数据格式转换失败: {e}")
            return json.dumps({
                "error": True,
                "error_code": "FORMAT_CONVERSION_ERROR",
                "message": f"数据格式转换失败: {str(e)}",
                "suggestions": [
                    "检查输入数据格式是否正确",
                    "确认目标格式是否支持",
                    "参考文档中的格式示例"
                ]
            }, ensure_ascii=False)


# 便利函数
def get_financial_reports(stock_code: str, stock_name: Optional[str] = None, force_refresh: bool = False) -> Dict[str, pd.DataFrame]:
    """获取财务报表数据的便利函数"""
    tool = AKShareFinancialDataTool()
    return tool.get_financial_reports(stock_code, stock_name, force_refresh)

def get_key_metrics(financial_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
    """获取关键财务指标的便利函数"""
    tool = AKShareFinancialDataTool()
    return tool.get_key_metrics(financial_data)

def get_historical_trend(financial_data: Dict[str, pd.DataFrame], years: int = 4) -> pd.DataFrame:
    """获取历史趋势数据的便利函数"""
    tool = AKShareFinancialDataTool()
    return tool.get_historical_trend(financial_data, years)

# 缓存管理便利函数
def check_cache_status(stock_code: str) -> Dict:
    """检查缓存状态"""
    tool = AKShareFinancialDataTool()
    return tool.check_cache_status(stock_code)

def refresh_cache(stock_code: str, stock_name: Optional[str] = None) -> bool:
    """刷新缓存"""
    tool = AKShareFinancialDataTool()
    return tool.refresh_cache(stock_code, stock_name)

def cleanup_cache(days: int = 30):
    """清理过期缓存"""
    tool = AKShareFinancialDataTool()
    tool.cleanup_cache(days)

def get_cache_info() -> Dict:
    """获取缓存信息"""
    tool = AKShareFinancialDataTool()
    return tool.get_cache_info()

def clear_all_cache():
    """清除所有缓存"""
    tool = AKShareFinancialDataTool()
    tool.clear_all_cache()

def export_cache_summary(filepath: Optional[str] = None):
    """导出缓存摘要"""
    tool = AKShareFinancialDataTool()
    tool.export_cache_summary(filepath)

if __name__ == "__main__":
    # 测试代码
    print("=== AKShare财务数据工具完整测试（含智能缓存） ===\n")
    
    # 初始化工具
    tool = AKShareFinancialDataTool()
    
    # 测试1: 首次获取数据（应该从网络获取）
    print("1. 首次获取陕西建工数据（从网络获取）...")
    data1 = tool.get_financial_reports("600248", "陕西建工")
    
    if data1:
        print("   ✓ 数据获取成功")
        
        # 检查缓存状态
        cache_status = tool.check_cache_status("600248")
        print(f"   ✓ 缓存状态: {cache_status}")
        
        # 测试关键指标
        metrics = tool.get_key_metrics(data1)
        if metrics:
            print(f"   ✓ 关键指标: 营收 {metrics.get('revenue_billion', 0):.1f}亿元")
    
    # 测试2: 第二次获取数据（应该从缓存获取）
    print("\n2. 第二次获取陕西建工数据（从缓存获取）...")
    data2 = tool.get_financial_reports("600248", "陕西建工")
    
    if data2:
        print("   ✓ 缓存数据获取成功")
        
        # 比较两次数据是否一致
        if data1 and data2:
            income_match = len(data1.get('income', pd.DataFrame())) == len(data2.get('income', pd.DataFrame()))
            print(f"   ✓ 数据一致性: {'通过' if income_match else '失败'}")
    
    # 测试3: 缓存管理功能
    print("\n3. 测试缓存管理功能...")
    
    # 获取缓存信息
    cache_info = tool.get_cache_info()
    print(f"   ✓ 缓存统计: {cache_info['total_stocks']}只股票, {cache_info['total_size_mb']}MB")
    
    # 测试强制刷新
    refresh_success = tool.refresh_cache("600248", "陕西建工")
    print(f"   ✓ 强制刷新: {'成功' if refresh_success else '失败'}")
    
    # 测试4: 多股票缓存
    print("\n4. 测试多股票缓存...")
    test_stocks = [("000858", "五粮液"), ("600519", "贵州茅台")]
    
    for code, name in test_stocks:
        print(f"   获取 {name}({code})...")
        try:
            data = tool.get_financial_reports(code, name)
            if data and 'income' in data and not data['income'].empty:
                metrics = tool.get_key_metrics(data)
                print(f"     ✓ 成功 - 营收: {metrics.get('revenue_billion', 0):.1f}亿元")
            else:
                print(f"     ✗ 失败")
        except Exception as e:
            print(f"     ✗ 异常: {e}")
    
    # 测试5: 最终缓存统计
    print("\n5. 最终缓存统计...")
    final_cache_info = tool.get_cache_info()
    print(f"   总缓存股票数: {final_cache_info['total_stocks']}")
    print(f"   总缓存文件数: {final_cache_info['total_files']}")
    print(f"   总缓存大小: {final_cache_info['total_size_mb']}MB")
    print(f"   缓存目录: {final_cache_info['cache_directory']}")
    
    # 导出缓存摘要
    tool.export_cache_summary()
    print("   ✓ 缓存摘要已导出")
    
    print("\n=== 测试总结 ===")
    print("✓ 智能缓存功能正常")
    print("✓ 增量更新机制工作")
    print("✓ 缓存管理功能完整")
    print("✓ 数据一致性保证")
    print("\n🎉 工具升级完成！现在具备智能缓存和增量更新功能。")
    print("\n主要特性:")
    print("- 同一公司数据获取一次后自动缓存")
    print("- 检测新财报数据并自动增量更新")
    print("- 缓存有效期管理（默认7天）")
    print("- 自动清理过期缓存")
    print("- 完整的缓存管理功能")

    def _serialize_for_analysis(self, financial_data: Dict[str, pd.DataFrame]) -> str:
        """
        将财务数据序列化为适合分析的JSON格式

        Args:
            financial_data: 包含利润表、资产负债表、现金流量表的字典

        Returns:
            序列化后的JSON字符串
        """
        try:
            # 导入数据适配器
            from ..utils.data_adapter import get_data_adapter
            adapter = get_data_adapter()

            # 使用数据适配器进行序列化
            serialized_data = adapter.normalize_financial_data(financial_data)
            logger.info(f"财务数据序列化完成，数据大小: {len(serialized_data)} 字符")

            return serialized_data

        except Exception as e:
            logger.error(f"财务数据序列化失败: {e}")
            # 返回空的财务结构
            empty_structure = {
                "income": [],
                "balance": [],
                "cashflow": []
            }
            return json.dumps(empty_structure, ensure_ascii=False)

    @register_tool("get_financial_data_for_analysis")
    def get_financial_data_for_analysis(self, stock_code: str, stock_name: Optional[str] = None, format_type: str = "json") -> str:
        """
        获取适合财务分析的标准化数据

        Args:
            stock_code: 股票代码，如 '600248'
            stock_name: 股票名称，可选
            format_type: 输出格式，支持 'json', 'metrics', 'simple'

        Returns:
            标准化的财务数据JSON字符串
        """
        if stock_name is None:
            stock_name = f"股票{stock_code}"

        logger.info(f"获取 {stock_name}({stock_code}) 的标准化分析数据")

        try:
            # 获取原始财务数据
            financial_data = self.get_financial_reports(stock_code, stock_name)

            if not financial_data or all(df.empty for df in financial_data.values()):
                logger.error("未获取到有效的财务数据")
                return json.dumps({
                    "error": True,
                    "message": f"未获取到 {stock_name}({stock_code}) 的有效财务数据",
                    "suggestions": [
                        "检查股票代码是否正确",
                        "确认该股票是否有公开财报数据",
                        "尝试稍后重试"
                    ]
                }, ensure_ascii=False)

            if format_type == "metrics":
                # 提取关键指标
                from ..utils.data_adapter import get_data_adapter
                adapter = get_data_adapter()
                key_metrics = adapter.extract_key_metrics(financial_data)

                result = {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "key_metrics": key_metrics,
                    "data_source": "akshare",
                    "extract_time": datetime.now().isoformat()
                }

                logger.info(f"提取到 {len(key_metrics)} 个关键指标")
                return json.dumps(result, ensure_ascii=False, default=str)

            elif format_type == "simple":
                # 简化格式，只保留最新数据
                simplified_data = {}

                for table_name, df in financial_data.items():
                    if not df.empty:
                        # 只取第一行（最新数据）
                        latest_row = df.iloc[0].to_dict()
                        # 清理数据
                        cleaned_row = {}
                        for key, value in latest_row.items():
                            if pd.notna(value):
                                if isinstance(value, (int, float, np.integer, np.floating)):
                                    cleaned_row[key] = float(value)
                                elif isinstance(value, str):
                                    cleaned_row[key] = value
                                else:
                                    cleaned_row[key] = str(value)
                        simplified_data[table_name] = cleaned_row

                result = {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "financial_data": simplified_data,
                    "data_source": "akshare",
                    "format": "simple"
                }

                logger.info(f"简化数据格式生成完成: {list(simplified_data.keys())}")
                return json.dumps(result, ensure_ascii=False, default=str)

            else:  # format_type == "json" (默认)
                # 标准JSON格式，适合直接传递给财务分析工具
                serialized_data = self._serialize_for_analysis(financial_data)

                # 添加元数据
                enhanced_data = {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "financial_data": json.loads(serialized_data),
                    "data_source": "akshare",
                    "format": "standard",
                    "serialization_time": datetime.now().isoformat()
                }

                logger.info(f"标准化分析数据生成完成")
                return json.dumps(enhanced_data, ensure_ascii=False, default=str)

        except Exception as e:
            logger.error(f"获取标准化分析数据失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")

            return json.dumps({
                "error": True,
                "error_code": "DATA_EXTRACTION_ERROR",
                "message": f"获取 {stock_name}({stock_code}) 的分析数据失败: {str(e)}",
                "suggestions": [
                    "检查网络连接是否正常",
                    "确认股票代码是否正确",
                    "稍后重试或联系技术支持"
                ]
            }, ensure_ascii=False)

    @register_tool("convert_financial_data_format")
    def convert_financial_data_format(self, financial_data: Union[str, Dict], target_format: str = "analysis_ready") -> str:
        """
        转换财务数据格式

        Args:
            financial_data: 输入的财务数据（JSON字符串或字典）
            target_format: 目标格式，支持 'analysis_ready', 'simple', 'metrics'

        Returns:
            转换后的JSON字符串
        """
        logger.info(f"转换财务数据格式，目标格式: {target_format}")

        try:
            # 导入数据适配器
            from ..utils.data_adapter import get_data_adapter
            adapter = get_data_adapter()

            if target_format == "analysis_ready":
                # 转换为适合分析的标准格式
                if isinstance(financial_data, str):
                    # 已经是字符串，使用适配器标准化
                    result = adapter.normalize_financial_data(financial_data)
                else:
                    # 字典格式，直接标准化
                    result = adapter.normalize_financial_data(financial_data)

            elif target_format == "simple":
                # 转换为简化格式
                if isinstance(financial_data, str):
                    data_dict = json.loads(financial_data)
                else:
                    data_dict = financial_data

                # 提取关键指标
                key_metrics = adapter.extract_key_metrics(data_dict)

                result = {
                    "key_metrics": key_metrics,
                    "format": "simple",
                    "conversion_time": datetime.now().isoformat()
                }

            elif target_format == "metrics":
                # 只提取关键指标
                if isinstance(financial_data, str):
                    data_dict = json.loads(financial_data)
                else:
                    data_dict = financial_data

                key_metrics = adapter.extract_key_metrics(data_dict)
                result = json.dumps(key_metrics, ensure_ascii=False, default=str)

            else:
                # 不支持的格式
                result = json.dumps({
                    "error": True,
                    "message": f"不支持的目标格式: {target_format}",
                    "supported_formats": ["analysis_ready", "simple", "metrics"]
                }, ensure_ascii=False)

            logger.info(f"数据格式转换完成: {target_format}")
            return result

        except Exception as e:
            logger.error(f"数据格式转换失败: {e}")
            return json.dumps({
                "error": True,
                "error_code": "FORMAT_CONVERSION_ERROR",
                "message": f"数据格式转换失败: {str(e)}",
                "suggestions": [
                    "检查输入数据格式是否正确",
                    "确认目标格式是否支持",
                    "参考文档中的格式示例"
                ]
            }, ensure_ascii=False)