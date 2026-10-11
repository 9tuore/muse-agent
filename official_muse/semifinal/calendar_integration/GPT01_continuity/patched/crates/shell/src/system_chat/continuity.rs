//! Native controls for the kernel's existing recurring loop. No timer,
//! provider selection, token, automatic enable, or turn interruption here.

use serde_json::Value;
use super::session::{SYSTEM_PROFILE, SYSTEM_SESSION};

pub const INTERVAL_SECONDS: u64 = 900;
// Exact prompt identifies this control's loop when a create reply was lost.
pub const PROMPT: &str = "OctoSense 持续模式 v1：检查已有授权目标的状态；没有可推进工作就结束本回合。有变化时报告。不要自动发送、发布、付款或修改外部数据；这些动作必须等待本人的单独批准。不要创建更多循环，不要改变模型或费用策略。";
pub const POLICY_MISSING: &str = "尚未配置并核实持续模式的模型与费用上限，暂不可启用。";

/// Native Host integration input, never supplied by an app or a loop result.
/// The Host must verify the actual profile AND enforced spending policy before
/// returning this. Labels describe those checks; labels do not enforce them.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Policy {
    pub profile_id: String,
    pub model_label: String,
    pub cost_limit_label: String,
}

impl Policy {
    pub fn valid(&self) -> bool {
        self.profile_id == SYSTEM_PROFILE
            && !self.model_label.trim().is_empty()
            && !self.cost_limit_label.trim().is_empty()
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Action { Refresh, Enable, Pause, Resume, Delete }

impl Action {
    pub fn method(self) -> &'static str {
        match self {
            Self::Refresh => "loop/list",
            Self::Enable => "loop/create",
            Self::Pause => "loop/pause",
            Self::Resume => "loop/resume",
            Self::Delete => "loop/delete",
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Record {
    pub loop_id: String,
    pub status: String,
    pub next_run_at_ms: Option<i64>,
    pub last_run_at_ms: Option<i64>,
    pub expires_at_ms: i64,
}

impl Record {
    pub fn parse(v: &Value) -> Result<Self, String> {
        if v["session_id"].as_str() != Some(SYSTEM_SESSION)
            || v["profile_id"].as_str() != Some(SYSTEM_PROFILE)
            || v["prompt"].as_str() != Some(PROMPT)
            || v["mode"].as_str() != Some("fixed_interval")
            || v["interval_seconds"].as_u64() != Some(INTERVAL_SECONDS)
        { return Err("循环的会话、profile 或规格不匹配。".into()); }
        let id = v["loop_id"].as_str().filter(|s| !s.is_empty()).ok_or("循环缺少真实 ID。")?;
        let status = v["status"].as_str().filter(|s| matches!(*s, "active" | "paused" | "expired" | "deleted")).ok_or("循环状态无法识别。")?;
        let time = |key: &str| -> Result<Option<i64>, String> {
            if v[key].is_null() { Ok(None) } else { v[key].as_i64().map(Some).ok_or_else(|| format!("循环的 {key} 无效。")) }
        };
        Ok(Self {
            loop_id: id.into(), status: status.into(),
            next_run_at_ms: time("next_run_at_ms")?, last_run_at_ms: time("last_run_at_ms")?,
            expires_at_ms: v["expires_at_ms"].as_i64().ok_or("循环缺少有效期。")?,
        })
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct State {
    pub record: Option<Record>,
    /// Retained across reconnect, including when list cannot find it.
    pub loop_id: Option<String>,
    pub checked: bool,
    pub busy: bool,
    /// A mutation sent without a trustworthy terminal response. Never retry
    /// create automatically; list must resolve it first.
    pub uncertain: bool,
    pub error: Option<String>,
    pub model_label: Option<String>,
    pub policy: Result<Policy, String>,
}

impl Default for State {
    fn default() -> Self {
        Self { record: None, loop_id: None, checked: false, busy: false, uncertain: false, error: None, model_label: None, policy: Err(POLICY_MISSING.into()) }
    }
}

impl State {
    pub fn keep_connection(&self) -> bool {
        self.uncertain || self.record.as_ref().is_some_and(|r| r.status == "active")
    }

    fn expired(&self) -> bool {
        let now = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_millis() as i64;
        self.record.as_ref().is_some_and(|r| r.expires_at_ms <= now)
    }

    pub fn label(&self) -> String {
        let state = if self.busy { "正在核对" }
            else if !self.checked || self.uncertain { "状态未确认" }
            else if self.expired() { "已过期" }
            else { match self.record.as_ref().map(|r| r.status.as_str()) {
                Some("active") => "已启用，按周期检查", Some("paused") => "已暂停，当前回合不受影响",
                Some("expired") => "已过期", _ => "未启用",
            }};
        format!("持续 AI：{state}")
    }

    pub fn controls(&self) -> Vec<(&'static str, Action, bool)> {
        let ready = !self.busy;
        let policy = self.policy.as_ref().is_ok_and(Policy::valid);
        let mut out = vec![("刷新", Action::Refresh, ready)];
        match self.record.as_ref().map(|r| r.status.as_str()) {
            Some("active") => out.push(("暂停", Action::Pause, ready)),
            Some("paused") => out.push(("恢复", Action::Resume, ready && self.checked && policy && !self.uncertain && !self.expired())),
            None if self.loop_id.is_none() => out.push(("启用", Action::Enable, ready && self.checked && policy && !self.uncertain && !self.expired())),
            _ => {}
        }
        if self.loop_id.is_some() { out.push(("移除", Action::Delete, ready)); }
        out
    }
}
