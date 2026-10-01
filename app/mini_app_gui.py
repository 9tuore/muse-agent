#!/usr/bin/env python3
"""Small native macOS window for the local agent.

The window is standard-library only so it can ship in a small .app bundle on
this Intel Mac. It talks to the same LocalAgent as the JSONL and browser
adapters; it does not own or stop the shared Qwen server. The menu is the
lifecycle surface: pause/resume intake, show tasks, stop app-owned workers, or
quit this app.
"""

from __future__ import annotations

import os
import subprocess
import threading
import tkinter as tk
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Optional

from agent_app import LocalAgent, LocalModelRouter


DEFAULT_WORKSPACE = Path.home() / "Library" / "Application Support" / "GOSIM Local Agent" / "workspace"
WORKSPACE = Path(os.environ.get("AGENT_WORKSPACE", DEFAULT_WORKSPACE)).expanduser().resolve()
MODEL_URL = os.environ.get("LOCAL_MODEL_URL", "http://127.0.0.1:8080/v1/chat/completions")
MODEL_HEALTH_URL = os.environ.get("LOCAL_MODEL_HEALTH_URL", "http://127.0.0.1:8080/health")


class MiniApp:
    def __init__(self, window: tk.Tk) -> None:
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        self.agent = LocalAgent(WORKSPACE, LocalModelRouter(MODEL_URL, timeout=10))
        self.window = window
        self.paused = False
        self.busy = False
        self.last_result: Optional[dict[str, Any]] = None
        self.window.title("GOSIM 本地 Agent")
        self.window.geometry("1280x800")
        self.window.minsize(960, 620)
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)
        self._build_menu()
        self._build_layout()
        self._append("窗口已启动；文件和终端动作都会先进入待确认任务卡。")
        self._append("共享 Qwen 服务由用户管理；退出本应用不会终止它。")
        self._check_model()

    def _build_menu(self) -> None:
        menu = tk.Menu(self.window)
        agent_menu = tk.Menu(menu, tearoff=False)
        self.pause_menu_label = tk.StringVar(value="暂停监听")
        agent_menu.add_command(labelvariable=self.pause_menu_label, command=self.toggle_pause)
        agent_menu.add_command(label="查看任务记录", command=self.show_tasks)
        agent_menu.add_separator()
        agent_menu.add_command(label="停止本应用服务", command=self.stop_owned_workers)
        agent_menu.add_command(label="退出全部", command=self.quit_all)
        menu.add_cascade(label="Agent", menu=agent_menu)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="关于", command=self.show_about)
        menu.add_cascade(label="帮助", menu=help_menu)
        self.window.configure(menu=menu)

    def _build_layout(self) -> None:
        style = ttk.Style(self.window)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Helvetica", 22, "bold"), foreground="#14213d")
        style.configure("Sub.TLabel", font=("Helvetica", 11), foreground="#5b6475")
        style.configure("Card.TLabelframe", padding=12)
        style.configure("Card.TLabelframe.Label", font=("Helvetica", 12, "bold"), foreground="#14213d")
        style.configure("Status.TLabel", font=("Helvetica", 11, "bold"))
        style.configure("Primary.TButton", padding=(14, 8))

        outer = ttk.Frame(self.window, padding=24)
        outer.pack(fill="both", expand=True)
        header = ttk.Frame(outer)
        header.pack(fill="x")
        ttk.Label(header, text="GOSIM 本地 Agent", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="本机 Qwen 路由 · 任务卡 · 显式确认 · 工作区能力", style="Sub.TLabel").pack(anchor="w", pady=(4, 14))
        self.pause_status = ttk.Label(header, text="监听中", style="Status.TLabel", foreground="#13795b")
        self.pause_status.pack(anchor="e")

        status_row = ttk.Frame(outer)
        status_row.pack(fill="x", pady=(0, 16))
        self.qwen_status = self._status_card(status_row, "模型", "检查中…")
        self.route_status = self._status_card(status_row, "路由器", "本地 Qwen + 规则回退")
        self.permission_status = self._status_card(status_row, "权限", "工作区 / 需确认")
        self.worker_status = self._status_card(status_row, "服务", "本应用未启动额外 worker")

        columns = ttk.PanedWindow(outer, orient="horizontal")
        columns.pack(fill="both", expand=True)
        left = ttk.Frame(columns, padding=(0, 0, 12, 0))
        center = ttk.Frame(columns, padding=(12, 0, 12, 0))
        right = ttk.Frame(columns, padding=(12, 0, 0, 0))
        columns.add(left, weight=1)
        columns.add(center, weight=2)
        columns.add(right, weight=1)

        inbox = ttk.LabelFrame(left, text="收件箱", style="Card.TLabelframe")
        inbox.pack(fill="both", expand=True)
        ttk.Label(inbox, text="给常驻 Agent 发消息", style="Sub.TLabel").pack(anchor="w")
        self.message = tk.Text(inbox, height=5, wrap="word", padx=8, pady=8)
        self.message.pack(fill="x", pady=(8, 10))
        self.message.insert("1.0", "请把这条测试记录保存到本地")
        self.send_button = ttk.Button(inbox, text="发送到任务队列", style="Primary.TButton", command=self.send_message)
        self.send_button.pack(fill="x")
        ttk.Label(inbox, text="消息只送入本地路由；写文件或终端动作必须再次确认。", style="Sub.TLabel", wraplength=290).pack(anchor="w", pady=(12, 0))

        task_box = ttk.LabelFrame(center, text="任务与摘要", style="Card.TLabelframe")
        task_box.pack(fill="both", expand=True)
        self.task_title = ttk.Label(task_box, text="等待新事件", font=("Helvetica", 15, "bold"))
        self.task_title.pack(anchor="w")
        self.task_state = ttk.Label(task_box, text="空闲", style="Status.TLabel", foreground="#5b6475")
        self.task_state.pack(anchor="w", pady=(3, 8))
        self.task_steps = tk.Text(task_box, height=9, wrap="word", state="disabled", padx=8, pady=8)
        self.task_steps.pack(fill="x")
        approval = ttk.Frame(task_box)
        approval.pack(fill="x", pady=(12, 8))
        self.approve_button = ttk.Button(approval, text="确认执行", command=lambda: self.confirm(True), state="disabled")
        self.approve_button.pack(side="left")
        self.reject_button = ttk.Button(approval, text="拒绝", command=lambda: self.confirm(False), state="disabled")
        self.reject_button.pack(side="left", padx=(8, 0))
        ttk.Button(approval, text="打开工作区", command=self.open_workspace).pack(side="right")
        ttk.Label(task_box, text=f"工作区：{WORKSPACE}", style="Sub.TLabel", wraplength=610).pack(anchor="w", pady=(4, 0))

        evidence = ttk.LabelFrame(right, text="执行证据", style="Card.TLabelframe")
        evidence.pack(fill="both", expand=True)
        self.log = tk.Text(evidence, height=20, wrap="word", state="disabled", padx=8, pady=8)
        self.log.pack(fill="both", expand=True)
        terminal = ttk.LabelFrame(right, text="受限终端", style="Card.TLabelframe")
        terminal.pack(fill="x", pady=(12, 0))
        row = ttk.Frame(terminal)
        row.pack(fill="x")
        self.command = tk.StringVar(value="mkdir")
        ttk.Combobox(row, textvariable=self.command, values=("mkdir", "touch"), state="readonly", width=8).pack(side="left")
        self.path = ttk.Entry(row)
        self.path.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.path.insert(0, "test-folder")
        self.terminal_button = ttk.Button(terminal, text="提出请求", command=self.terminal_request)
        self.terminal_button.pack(fill="x", pady=(8, 0))
        ttk.Label(terminal, text="仅 mkdir / touch；固定工作区；shell=False；10 秒超时。", style="Sub.TLabel", wraplength=310).pack(anchor="w", pady=(8, 0))

    def _status_card(self, parent: ttk.Frame, title: str, value: str) -> ttk.Frame:
        card = ttk.LabelFrame(parent, text=title, style="Card.TLabelframe")
        card.pack(side="left", fill="x", expand=True, padx=(0, 10))
        label = ttk.Label(card, text=value, style="Status.TLabel", foreground="#5b6475")
        label.pack(anchor="w")
        card.value_label = label  # type: ignore[attr-defined]
        return card

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).astimezone().strftime("%H:%M:%S")

    def _append(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", f"[{self._now()}] {message}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _show_steps(self, lines: list[str]) -> None:
        self.task_steps.configure(state="normal")
        self.task_steps.delete("1.0", "end")
        self.task_steps.insert("end", "\n".join(f"• {line}" for line in lines))
        self.task_steps.configure(state="disabled")

    def _check_model(self) -> None:
        def probe() -> None:
            try:
                with urllib.request.urlopen(MODEL_HEALTH_URL, timeout=2) as response:
                    healthy = response.status == 200
            except OSError:
                healthy = False
            self.window.after(0, lambda: self._set_model_status(healthy))

        threading.Thread(target=probe, daemon=True).start()

    def _set_model_status(self, healthy: bool) -> None:
        text = "在线 · 127.0.0.1:8080" if healthy else "离线 · 规则回退"
        color = "#13795b" if healthy else "#a15c00"
        self.qwen_status.value_label.configure(text=text, foreground=color)  # type: ignore[attr-defined]
        self._append("Qwen3-0.6B 健康检查通过。" if healthy else "Qwen 服务未连接，路由器将标记并使用规则回退。")

    def _busy(self, busy: bool) -> None:
        self.busy = busy
        state = "disabled" if busy or self.paused else "normal"
        self.send_button.configure(state=state)
        self.terminal_button.configure(state=state)
        pending = self.agent.pending is not None
        self.approve_button.configure(state="normal" if pending and not busy else "disabled")
        self.reject_button.configure(state="normal" if pending and not busy else "disabled")

    def _dispatch(self, event: dict[str, Any]) -> None:
        if self.paused:
            self._append("监听已暂停；没有新增任务。")
            return
        self._busy(True)

        def work() -> None:
            result = self.agent.handle(event)
            self.window.after(0, lambda: self._show_result(result))

        threading.Thread(target=work, daemon=True).start()

    def _show_result(self, result: dict[str, Any]) -> None:
        self.last_result = result
        self._busy(False)
        if not result.get("ok"):
            self.task_state.configure(text="失败", foreground="#b42318")
            self._append(f"请求未执行：{result.get('error')} {result.get('detail', '')}")
            return
        card = result.get("task_card") or {}
        if card:
            self.task_title.configure(text=card.get("title", "任务"))
            status = card.get("status", "unknown")
            colors = {"completed": "#13795b", "proposed": "#a15c00", "rejected": "#b42318", "failed": "#b42318"}
            self.task_state.configure(text=status, foreground=colors.get(status, "#5b6475"))
            self._show_steps(card.get("steps", []))
            self._append(f"任务：{card.get('title')} · 状态：{status}")
        if result.get("created"):
            self._append(f"已创建并回读：{result['created']}")
        if result.get("execution"):
            execution = result["execution"]
            self._append(f"终端退出码：{execution['returncode']} · 命令：{' '.join(execution['argv'])}")
            if execution.get("stderr"):
                self._append(execution["stderr"])
        if self.agent.pending is not None:
            self._append("待确认：请检查任务卡后选择确认或拒绝。")

    def send_message(self) -> None:
        text = self.message.get("1.0", "end").strip()
        if text:
            self._append(f"收到本地事件：{text[:120]}")
            self._dispatch({"type": "user_input", "text": text})

    def terminal_request(self) -> None:
        relative_path = self.path.get().strip()
        if relative_path:
            self._append(f"提出终端请求：{self.command.get()} {relative_path}")
            self._dispatch({"type": "terminal_request", "argv": [self.command.get(), relative_path]})

    def confirm(self, approved: bool) -> None:
        self._append("用户确认执行" if approved else "用户拒绝执行")
        self._dispatch({"type": "confirm", "approved": approved})

    def toggle_pause(self) -> None:
        self.paused = not self.paused
        if self.paused:
            self.pause_menu_label.set("恢复监听")
            self.pause_status.configure(text="已暂停", foreground="#a15c00")
            self._append("监听已暂停；现有任务仍保留，新的输入不会路由。")
        else:
            self.pause_menu_label.set("暂停监听")
            self.pause_status.configure(text="监听中", foreground="#13795b")
            self._append("监听已恢复。")
        self._busy(self.busy)

    def show_tasks(self) -> None:
        self.window.deiconify()
        self.window.lift()
        self._append("已定位到当前任务与执行证据。")

    def stop_owned_workers(self) -> None:
        self._append("本应用没有启动额外 worker；共享 Qwen 由用户管理，未被停止。")
        self.worker_status.value_label.configure(text="无自有 worker", foreground="#5b6475")  # type: ignore[attr-defined]

    def quit_all(self) -> None:
        self._append("退出本应用；共享 Qwen 服务保持运行。")
        self.window.destroy()

    def _close_window(self) -> None:
        self.window.withdraw()

    def open_workspace(self) -> None:
        subprocess.Popen(["/usr/bin/open", str(WORKSPACE)])
        self._append("已请求 Finder 打开工作区。")

    def show_about(self) -> None:
        messagebox.showinfo("关于 GOSIM 本地 Agent", "标准库 Tk 桌面适配器\n本地 Qwen 路由与显式确认边界")


def main() -> None:
    window = tk.Tk()
    MiniApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
