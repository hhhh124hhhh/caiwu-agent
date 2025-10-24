#!/usr/bin/env python3
"""
Orchestra日志分析工具
分析多智能体系统的执行日志，生成性能报告和错误分析
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import re


class LogAnalyzer:
    """日志分析器"""

    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.logs = []
        self.analysis_results = {}

    def load_logs(self) -> None:
        """加载日志文件"""
        if not self.log_file.exists():
            raise FileNotFoundError(f"日志文件不存在: {self.log_file}")

        print(f"加载日志文件: {self.log_file}")
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    log_entry = json.loads(line)
                    log_entry['line_number'] = line_num
                    self.logs.append(log_entry)
                except json.JSONDecodeError as e:
                    print(f"警告: 第{line_num}行JSON解析失败: {e}")

        print(f"成功加载 {len(self.logs)} 条日志记录")

    def analyze_session_overview(self) -> Dict[str, Any]:
        """分析会话概览"""
        if not self.logs:
            return {"error": "没有日志数据"}

        sessions = defaultdict(list)
        for log in self.logs:
            session_id = log.get("session_id", "unknown")
            sessions[session_id].append(log)

        overview = {
            "total_sessions": len(sessions),
            "total_log_entries": len(self.logs),
            "sessions": {}
        }

        for session_id, session_logs in sessions.items():
            if not session_logs:
                continue

            # 获取会话时间范围
            timestamps = [log.get("timestamp") for log in session_logs if log.get("timestamp")]
            if timestamps:
                start_time = min(timestamps)
                end_time = max(timestamps)
                duration = self._calculate_duration(start_time, end_time)
            else:
                start_time = end_time = duration = "unknown"

            # 统计智能体活动
            agent_counts = Counter(log.get("agent_name", "unknown") for log in session_logs)
            event_types = Counter(log.get("event_type", "unknown") for log in session_logs)
            status_counts = Counter(log.get("status", "unknown") for log in session_logs)

            # 错误统计
            errors = [log for log in session_logs if log.get("status") == "failed"]

            overview["sessions"][session_id] = {
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
                "log_count": len(session_logs),
                "agents": dict(agent_counts),
                "event_types": dict(event_types),
                "status_breakdown": dict(status_counts),
                "error_count": len(errors),
                "success_rate": (len(session_logs) - len(errors)) / len(session_logs) * 100
            }

        return overview

    def analyze_performance_metrics(self) -> Dict[str, Any]:
        """分析性能指标"""
        if not self.logs:
            return {"error": "没有日志数据"}

        # 提取有duration_ms的日志
        performance_logs = [log for log in self.logs if log.get("duration_ms")]

        if not performance_logs:
            return {"error": "没有性能数据"}

        # 按智能体分组
        agent_performance = defaultdict(list)
        for log in performance_logs:
            agent = log.get("agent_name", "unknown")
            agent_performance[agent].append(log)

        performance_analysis = {
            "total_performance_records": len(performance_logs),
            "agents": {},
            "overall_stats": self._calculate_performance_stats(performance_logs)
        }

        for agent, logs in agent_performance.items():
            performance_analysis["agents"][agent] = self._calculate_performance_stats(logs)

        return performance_analysis

    def analyze_tool_usage(self) -> Dict[str, Any]:
        """分析工具使用情况"""
        if not self.logs:
            return {"error": "没有日志数据"}

        tool_logs = [log for log in self.logs if log.get("event_type") == "tool_usage"]

        if not tool_logs:
            return {"error": "没有工具使用数据"}

        # 工具使用统计
        tool_counts = Counter()
        tool_errors = Counter()
        tool_performance = defaultdict(list)

        for log in tool_logs:
            tool_name = log.get("metadata", {}).get("tool_name", "unknown")
            tool_counts[tool_name] += 1

            if log.get("status") == "failed":
                tool_errors[tool_name] += 1

            if log.get("duration_ms"):
                tool_performance[tool_name].append(log["duration_ms"])

        tool_analysis = {
            "total_tool_calls": len(tool_logs),
            "unique_tools": len(tool_counts),
            "tool_usage": dict(tool_counts),
            "tool_errors": dict(tool_errors),
            "tool_performance": {}
        }

        # 计算工具性能统计
        for tool, durations in tool_performance.items():
            tool_analysis["tool_performance"][tool] = {
                "call_count": len(durations),
                "avg_duration_ms": sum(durations) / len(durations),
                "min_duration_ms": min(durations),
                "max_duration_ms": max(durations),
                "total_duration_ms": sum(durations)
            }

        return tool_analysis

    def analyze_errors(self) -> Dict[str, Any]:
        """分析错误情况"""
        if not self.logs:
            return {"error": "没有日志数据"}

        error_logs = [log for log in self.logs if log.get("status") == "failed"]

        if not error_logs:
            return {"message": "没有错误记录", "total_logs": len(self.logs)}

        # 按智能体分组错误
        agent_errors = defaultdict(list)
        for log in error_logs:
            agent = log.get("agent_name", "unknown")
            agent_errors[agent].append(log)

        error_types = Counter()
        error_analysis = {
            "total_errors": len(error_logs),
            "error_rate": len(error_logs) / len(self.logs) * 100,
            "agents": {},
            "error_types": {}
        }

        for agent, logs in agent_errors.items():
            agent_error_types = Counter()
            for log in logs:
                error_info = log.get("error_info", {})
                error_type = error_info.get("type", "Unknown")
                agent_error_types[error_type] += 1
                error_types[error_type] += 1

            error_analysis["agents"][agent] = {
                "error_count": len(logs),
                "error_types": dict(agent_error_types),
                "error_rate": len(logs) / len([l for l in self.logs if l.get("agent_name") == agent]) * 100
            }

        error_analysis["error_types"] = dict(error_types)

        return error_analysis

    def analyze_workflow_patterns(self) -> Dict[str, Any]:
        """分析工作流模式"""
        if not self.logs:
            return {"error": "没有日志数据"}

        # 按trace_id分组，分析执行流程
        trace_groups = defaultdict(list)
        for log in self.logs:
            trace_id = log.get("trace_id", "unknown")
            trace_groups[trace_id].append(log)

        # 分析执行顺序模式
        execution_patterns = []
        for trace_id, trace_logs in trace_groups.items():
            # 按时间戳排序
            trace_logs.sort(key=lambda x: x.get("timestamp", ""))

            # 提取执行序列
            sequence = []
            for log in trace_logs:
                event_type = log.get("event_type", "unknown")
                agent = log.get("agent_name", "unknown")
                status = log.get("status", "unknown")
                sequence.append(f"{agent}:{event_type}:{status}")

            execution_patterns.append(sequence)

        # 查找常见模式
        pattern_counts = Counter()
        for pattern in execution_patterns:
            pattern_key = " -> ".join(pattern[:5])  # 只取前5步
            pattern_counts[pattern_key] += 1

        workflow_analysis = {
            "total_traces": len(trace_groups),
            "unique_patterns": len(pattern_counts),
            "common_patterns": dict(pattern_counts.most_common(10)),
            "pattern_examples": {}
        }

        # 为常见模式提供示例
        for pattern, count in pattern_counts.most_common(3):
            # 找到第一个匹配的trace
            for i, exec_pattern in enumerate(execution_patterns):
                pattern_key = " -> ".join(exec_pattern[:5])
                if pattern_key == pattern:
                    workflow_analysis["pattern_examples"][pattern] = {
                        "trace_index": i,
                        "pattern": exec_pattern,
                        "occurrences": count
                    }
                    break

        return workflow_analysis

    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """计算时间间隔"""
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = end - start

            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except:
            return "unknown"

    def _calculate_performance_stats(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算性能统计"""
        durations = [log["duration_ms"] for log in logs if log.get("duration_ms")]

        if not durations:
            return {"error": "没有有效的性能数据"}

        return {
            "count": len(durations),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "median_duration_ms": sorted(durations)[len(durations) // 2],
            "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)],
            "total_duration_ms": sum(durations)
        }

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """生成完整分析报告"""
        print("开始生成分析报告...")

        # 执行各种分析
        overview = self.analyze_session_overview()
        performance = self.analyze_performance_metrics()
        tool_usage = self.analyze_tool_usage()
        errors = self.analyze_errors()
        workflow = self.analyze_workflow_patterns()

        # 构建报告
        report_lines = [
            "# Orchestra日志分析报告",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"分析文件: {self.log_file}",
            "=" * 80,
            "",
            "## 1. 会话概览",
            ""
        ]

        # 添加会话概览
        if "error" not in overview:
            report_lines.append(f"- 总会话数: {overview['total_sessions']}")
            report_lines.append(f"- 总日志条目: {overview['total_log_entries']}")
            report_lines.append("")
            report_lines.append("### 会话详情:")
            for session_id, session_info in overview["sessions"].items():
                report_lines.extend([
                    f"**会话 {session_id[:8]}**:",
                    f"- 时间范围: {session_info['start_time']} ~ {session_info['end_time']}",
                    f"- 持续时间: {session_info['duration']}",
                    f"- 日志数量: {session_info['log_count']}",
                    f"- 成功率: {session_info['success_rate']:.1f}%",
                    f"- 错误数量: {session_info['error_count']}",
                    ""
                ])
        else:
            report_lines.append(f"错误: {overview['error']}")
            report_lines.append("")

        # 添加性能分析
        report_lines.extend([
            "## 2. 性能分析",
            ""
        ])

        if "error" not in performance:
            overall_stats = performance["overall_stats"]
            report_lines.extend([
                f"- 总性能记录: {performance['total_performance_records']}",
                f"- 平均执行时间: {overall_stats['avg_duration_ms']:.1f}ms",
                f"- 最快执行时间: {overall_stats['min_duration_ms']}ms",
                f"- 最慢执行时间: {overall_stats['max_duration_ms']}ms",
                f"- 中位数执行时间: {overall_stats['median_duration_ms']}ms",
                f"- P95执行时间: {overall_stats['p95_duration_ms']}ms",
                ""
            ])

            report_lines.append("### 智能体性能:")
            for agent, stats in performance["agents"].items():
                report_lines.extend([
                    f"**{agent}**:",
                    f"- 调用次数: {stats['count']}",
                    f"- 平均时间: {stats['avg_duration_ms']:.1f}ms",
                    f"- 最快时间: {stats['min_duration_ms']}ms",
                    f"- 最慢时间: {stats['max_duration_ms']}ms",
                    ""
                ])
        else:
            report_lines.append(f"错误: {performance['error']}")
            report_lines.append("")

        # 添加工具使用分析
        report_lines.extend([
            "## 3. 工具使用分析",
            ""
        ])

        if "error" not in tool_usage:
            report_lines.extend([
                f"- 总工具调用: {tool_usage['total_tool_calls']}",
                f"- 使用的工具数: {tool_usage['unique_tools']}",
                ""
            ])

            report_lines.append("### 工具使用排行:")
            for tool, count in sorted(tool_usage["tool_usage"].items(), key=lambda x: x[1], reverse=True):
                error_count = tool_usage["tool_errors"].get(tool, 0)
                success_rate = ((count - error_count) / count * 100) if count > 0 else 0
                report_lines.append(f"- {tool}: {count}次调用 (成功率: {success_rate:.1f}%)")

            report_lines.append("")
            report_lines.append("### 工具性能:")
            for tool, perf in tool_usage["tool_performance"].items():
                report_lines.extend([
                    f"**{tool}**:",
                    f"- 调用次数: {perf['call_count']}",
                    f"- 平均耗时: {perf['avg_duration_ms']:.1f}ms",
                    f"- 总耗时: {perf['total_duration_ms']}ms",
                    ""
                ])
        else:
            report_lines.append(f"错误: {tool_usage['error']}")
            report_lines.append("")

        # 添加错误分析
        report_lines.extend([
            "## 4. 错误分析",
            ""
        ])

        if "message" not in errors:
            report_lines.extend([
                f"- 总错误数: {errors['total_errors']}",
                f"- 错误率: {errors['error_rate']:.2f}%",
                ""
            ])

            report_lines.append("### 按智能体分组的错误:")
            for agent, error_info in errors["agents"].items():
                report_lines.extend([
                    f"**{agent}**:",
                    f"- 错误数: {error_info['error_count']}",
                    f"- 错误率: {error_info['error_rate']:.2f}%",
                    f"- 错误类型: {', '.join(error_info['error_types'].keys())}",
                    ""
                ])

            report_lines.append("### 错误类型统计:")
            for error_type, count in errors["error_types"].items():
                report_lines.append(f"- {error_type}: {count}次")
        else:
            report_lines.append(errors["message"])

        report_lines.append("")

        # 添加工作流模式分析
        report_lines.extend([
            "## 5. 工作流模式分析",
            ""
        ])

        if "error" not in workflow:
            report_lines.extend([
                f"- 总执行轨迹: {workflow['total_traces']}",
                f"- 唯一模式数: {workflow['unique_patterns']}",
                ""
            ])

            report_lines.append("### 常见执行模式:")
            for i, (pattern, count) in enumerate(workflow["common_patterns"][:5], 1):
                report_lines.append(f"{i}. {pattern} (出现{count}次)")

            report_lines.append("")
            report_lines.append("### 模式示例:")
            for pattern, example in workflow["pattern_examples"].items():
                report_lines.extend([
                    f"**模式**: {pattern}",
                    f"**出现次数**: {example['occurrences']}",
                    f"**执行序列**: {' -> '.join(example['pattern'])}",
                    ""
                ])
        else:
            report_lines.append(f"错误: {workflow['error']}")

        # 添加建议
        report_lines.extend([
            "## 6. 改进建议",
            ""
        ])

        suggestions = self._generate_suggestions(overview, performance, tool_usage, errors, workflow)
        for suggestion in suggestions:
            report_lines.append(f"- {suggestion}")

        report_content = "\n".join(report_lines)

        # 保存到文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"报告已保存到: {output_file}")

        return report_content

    def _generate_suggestions(self, overview, performance, tool_usage, errors, workflow) -> List[str]:
        """生成改进建议"""
        suggestions = []

        # 性能建议
        if "error" not in performance:
            overall_stats = performance["overall_stats"]
            if overall_stats["avg_duration_ms"] > 5000:
                suggestions.append("平均执行时间较长，考虑优化任务并行度或缓存机制")
            if overall_stats["p95_duration_ms"] > 10000:
                suggestions.append("P95执行时间过长，检查是否存在性能瓶颈")

        # 错误建议
        if "message" not in errors:
            if errors["error_rate"] > 10:
                suggestions.append("错误率较高，建议增强错误处理和重试机制")
            if any("ConnectionError" in err for err in errors["error_types"]):
                suggestions.append("存在网络连接错误，建议添加网络重试和超时处理")
            if any("TimeoutError" in err for err in errors["error_types"]):
                suggestions.append("存在超时错误，建议增加任务超时时间或优化执行效率")

        # 工具使用建议
        if "error" not in tool_usage:
            low_usage_tools = [tool for tool, count in tool_usage["tool_usage"].items() if count < 3]
            if low_usage_tools:
                suggestions.append(f"工具 {', '.join(low_usage_tools)} 使用频率较低，检查是否需要优化工具调用策略")

        # 工作流建议
        if "error" not in workflow:
            if workflow["unique_patterns"] < workflow["total_traces"] * 0.5:
                suggestions.append("执行模式多样化，建议标准化工作流程")

        return suggestions


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Orchestra日志分析工具")
    parser.add_argument("--log-file", required=True, help="日志文件路径")
    parser.add_argument("--output", help="输出报告文件路径")
    parser.add_argument("--trace-id", help="分析特定的trace_id")
    parser.add_argument("--agent", help="分析特定的智能体")
    parser.add_argument("--quiet", action="store_true", help="静默模式，只输出到文件")

    args = parser.parse_args()

    try:
        # 创建分析器
        analyzer = LogAnalyzer(args.log_file)
        analyzer.load_logs()

        # 过滤日志（如果指定了过滤条件）
        if args.trace_id:
            analyzer.logs = [log for log in analyzer.logs if log.get("trace_id") == args.trace_id]
            if not analyzer.logs:
                print(f"未找到trace_id为 {args.trace_id} 的日志记录")
                return

        if args.agent:
            analyzer.logs = [log for log in analyzer.logs if log.get("agent_name") == args.agent]
            if not analyzer.logs:
                print(f"未找到智能体为 {args.agent} 的日志记录")
                return

        # 生成报告
        output_file = args.output or f"orchestra_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report = analyzer.generate_report(output_file)

        if not args.quiet:
            print("\n" + "="*80)
            print("分析完成！")
            print("="*80)
            print(f"日志文件: {args.log_file}")
            print(f"报告文件: {output_file}")
            print(f"日志记录数: {len(analyzer.logs)}")

    except Exception as e:
        print(f"分析失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()