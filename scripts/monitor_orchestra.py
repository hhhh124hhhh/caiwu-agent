#!/usr/bin/env python3
"""
Orchestra实时监控工具
实时监控多智能体系统的执行状态
"""

import json
import time
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading
from collections import defaultdict, deque
import signal
import os


class OrchestraMonitor:
    """Orchestra监控器"""

    def __init__(self, log_dir: str, refresh_interval: float = 1.0):
        self.log_dir = Path(log_dir)
        self.refresh_interval = refresh_interval
        self.running = False
        self.latest_logs = deque(maxlen=1000)
        self.session_stats = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.last_file_size = {}
        self.current_trace_id = None
        self.monitoring_start_time = datetime.now()

        # ANSI颜色代码
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'reset': '\033[0m',
            'bold': '\033[1m'
        }

    def start_monitoring(self, trace_id: Optional[str] = None) -> None:
        """开始监控"""
        self.running = True
        self.current_trace_id = trace_id

        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print(f"开始监控Orchestra日志...")
        print(f"日志目录: {self.log_dir}")
        print(f"刷新间隔: {self.refresh_interval}秒")
        if trace_id:
            print(f"监控特定trace_id: {trace_id}")
        print("按 Ctrl+C 停止监控\n")

        try:
            self._monitor_loop()
        except KeyboardInterrupt:
            self._stop_monitoring()

    def _monitor_loop(self) -> None:
        """监控主循环"""
        while self.running:
            try:
                self._check_log_files()
                self._display_status()
                time.sleep(self.refresh_interval)
            except Exception as e:
                print(f"{self.colors['red']}监控错误: {e}{self.colors['reset']}")
                time.sleep(self.refresh_interval)

    def _check_log_files(self) -> None:
        """检查日志文件变化"""
        if not self.log_dir.exists():
            return

        # 查找最新的日志文件
        log_files = list(self.log_dir.glob("orchestra_*.json"))
        if not log_files:
            return

        latest_file = max(log_files, key=lambda f: f.stat().st_mtime)
        current_size = latest_file.stat().st_mtime

        # 检查文件是否有更新
        if latest_file not in self.last_file_size or self.last_file_size[latest_file] != current_size:
            self._read_new_logs(latest_file)
            self.last_file_size[latest_file] = current_size

    def _read_new_logs(self, log_file: Path) -> None:
        """读取新的日志条目"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 跟踪已读取的行数
            if not hasattr(self, '_lines_read'):
                self._lines_read = 0

            new_lines = lines[self._lines_read:]
            self._lines_read = len(lines)

            for line in new_lines:
                line = line.strip()
                if not line:
                    continue

                try:
                    log_entry = json.loads(line)

                    # 过滤trace_id（如果指定）
                    if self.current_trace_id and log_entry.get("trace_id") != self.current_trace_id:
                        continue

                    # 添加到最新日志队列
                    self.latest_logs.append(log_entry)

                    # 更新统计
                    self._update_stats(log_entry)

                    # 实时显示重要事件
                    self._display_log_entry(log_entry)

                except json.JSONDecodeError:
                    continue

        except Exception as e:
            print(f"{self.colors['red']}读取日志文件错误: {e}{self.colors['reset']}")

    def _update_stats(self, log_entry: Dict[str, Any]) -> None:
        """更新统计信息"""
        session_id = log_entry.get("session_id", "unknown")
        agent_name = log_entry.get("agent_name", "unknown")
        event_type = log_entry.get("event_type", "unknown")
        status = log_entry.get("status", "unknown")

        key = f"{session_id}:{agent_name}:{event_type}"
        self.session_stats[key] += 1

        if status == "failed":
            error_key = f"{session_id}:{agent_name}"
            self.error_counts[error_key] += 1

    def _display_log_entry(self, log_entry: Dict[str, Any]) -> None:
        """实时显示日志条目"""
        timestamp = log_entry.get("timestamp", "")
        agent_name = log_entry.get("agent_name", "unknown")
        event_type = log_entry.get("event_type", "unknown")
        status = log_entry.get("status", "unknown")
        duration = log_entry.get("duration_ms")

        # 选择颜色
        if status == "completed":
            color = self.colors['green']
        elif status == "failed":
            color = self.colors['red']
        elif status == "started":
            color = self.colors['blue']
        else:
            color = self.colors['white']

        # 格式化时间
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = timestamp[:8] if timestamp else "unknown"

        # 构建显示内容
        display_parts = [
            f"{self.colors['cyan']}{time_str}{self.colors['reset']}",
            f"{self.colors['bold']}{agent_name}{self.colors['reset']}",
            f"{event_type}",
            f"{color}{status}{self.colors['reset']}"
        ]

        if duration:
            display_parts.append(f"{duration}ms")

        # 添加额外信息
        if event_type == "task_execution" and log_entry.get("input_data"):
            task = log_entry["input_data"].get("task", "")[:50]
            if task:
                display_parts.append(f'"{task}..."')

        if event_type == "tool_usage" and log_entry.get("metadata"):
            tool_name = log_entry["metadata"].get("tool_name", "")
            if tool_name:
                display_parts.append(f"Tool: {tool_name}")

        # 显示
        print(" | ".join(display_parts))

    def _display_status(self) -> None:
        """显示状态概览"""
        # 清屏（每10次刷新一次）
        if not hasattr(self, '_refresh_count'):
            self._refresh_count = 0

        self._refresh_count += 1
        if self._refresh_count % 10 != 0:
            return

        # 构建状态信息
        uptime = datetime.now() - self.monitoring_start_time
        total_logs = len(self.latest_logs)
        total_errors = sum(self.error_counts.values())

        status_lines = [
            f"\n{self.colors['bold']}{'='*80}{self.colors['reset']}",
            f"{self.colors['bold']}Orchestra监控状态{self.colors['reset']}",
            f"{'='*80}",
            f"运行时间: {uptime}",
            f"日志条目: {total_logs}",
            f"错误数量: {total_errors}",
            f"监控开始: {self.monitoring_start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"{'='*80}",
        ]

        # 添加活跃智能体统计
        if self.session_stats:
            status_lines.append(f"\n{self.colors['bold']}活跃智能体:{self.colors['reset']}")
            agent_counts = defaultdict(int)
            for key, count in self.session_stats.items():
                parts = key.split(":")
                if len(parts) >= 2:
                    agent = parts[1]
                    agent_counts[agent] += count

            for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
                status_lines.append(f"  {agent}: {count} 次事件")

        # 添加错误统计
        if self.error_counts:
            status_lines.append(f"\n{self.colors['red']}错误统计:{self.colors['reset']}")
            for error_key, count in sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                parts = error_key.split(":")
                if len(parts) >= 2:
                    session_id, agent = parts[0], parts[1]
                    status_lines.append(f"  {agent}: {count} 次错误")

        # 打印状态
        print("\033[H\033[J", end="")  # 清屏并移动光标到顶部
        for line in status_lines:
            print(line)

    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n{self.colors['yellow']}收到停止信号，正在清理...{self.colors['reset']}")
        self._stop_monitoring()

    def _stop_monitoring(self):
        """停止监控"""
        self.running = False

        # 显示最终统计
        self._display_final_stats()

    def _display_final_stats(self):
        """显示最终统计"""
        print(f"\n{self.colors['bold']}{'='*80}{self.colors['reset']}")
        print(f"{self.colors['bold']}监控结束统计{self.colors['reset']}")
        print(f"{'='*80}")

        uptime = datetime.now() - self.monitoring_start_time
        total_logs = len(self.latest_logs)
        total_errors = sum(self.error_counts.values())

        print(f"监控时长: {uptime}")
        print(f"处理日志: {total_logs} 条")
        print(f"检测错误: {total_errors} 个")

        if total_errors > 0:
            print(f"\n{self.colors['red']}错误详情:{self.colors['reset']}")
            for error_key, count in sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True):
                parts = error_key.split(":")
                if len(parts) >= 2:
                    session_id, agent = parts[0], parts[1]
                    print(f"  {agent}: {count} 次")

        print(f"{self.colors['green']}监控已停止{self.colors['reset']}")
        print(f"{'='*80}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Orchestra实时监控工具")
    parser.add_argument("--log-dir", default="./logs", help="日志目录路径")
    parser.add_argument("--refresh", type=float, default=1.0, help="刷新间隔（秒）")
    parser.add_argument("--trace-id", help="监控特定的trace_id")
    parser.add_argument("--quiet", action="store_true", help="静默模式，不显示实时输出")

    args = parser.parse_args()

    # 检查日志目录
    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        print(f"错误: 日志目录不存在: {log_dir}")
        sys.exit(1)

    # 创建监控器
    monitor = OrchestraMonitor(str(log_dir), args.refresh)

    # 开始监控
    try:
        monitor.start_monitoring(args.trace_id)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()