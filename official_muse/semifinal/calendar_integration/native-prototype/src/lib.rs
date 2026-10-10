//! Read-only hosted prototype. The Shell supplies the service and owns the runtime.
pub use makepad_widgets;
mod history;
use makepad_app_module::{
    makepad_ai_services::wire::{ServiceCall, ServiceManifest, ToolResult},
    AppModule, ExecOutcome, InstanceHandles, InstanceParts, OpenSchema, ServiceExecutor,
    ValidatedOpen,
};
use makepad_widgets::*;
use octosense_app_peers::{
    injection, ContextEvent, ContextOp, ContextSpec, EventSink, OctosAppService, OctosContext,
    TurnTrigger,
};
use std::sync::{mpsc, Arc};

pub const APP_ID: &str = "muse-native-prototype";
// ADR 0004 §11: Shell peer_link::DEVICE for apps with storage.accounts=false.
const DEVICE_ACCOUNT: &str = "device";
const READ_REQUEST: &str = "Use calendar.events with limit=10 to read the builtin Calendar. Report the actual tool result or error. Do not create, update, remove or notify. Do not claim exact absence from a truncated list.";

script_mod! {
    use mod.prelude.widgets.*
    mod.widgets.MuseNativePrototypeView = set_type_default() do #(MuseNativePrototypeView::register_widget(vm)) {
        ..mod.widgets.ScrollYView
        width: Fill height: Fill
        flow: Down padding: 24 spacing: 16
        title := Label { text: "Muse 原生只读原型" draw_text.text_style.font_size: 24 }
        description := Label {
            width: Fill draw_text.wrap: Words
            text: "独立原生身份 · 内置 Calendar 只读联调。首次授权后重新打开此模块。"
        }
        read := Button { text: "请求 Agent 读取日历" }
        stop := Button { text: "停止" }
        history := Button { text: "查看读取证据" }
        status := Label { width: Fill draw_text.wrap: Words text: "尚未请求；未验证 Relay。" }
        evidence := Label { width: Fill draw_text.wrap: Words text: "尚无本回合工具证据。" }
    }
}

#[derive(Script, ScriptHook, Widget)]
pub struct MuseNativePrototypeView {
    #[deref]
    view: View,
    #[rust]
    service: Option<Arc<dyn OctosAppService>>,
    #[rust]
    context: Option<Arc<dyn OctosContext>>,
    #[rust]
    events: Option<mpsc::Receiver<ContextEvent>>,
    #[rust]
    instance: String,
    #[rust]
    running: bool,
    #[rust]
    last_turn: Option<String>,
    #[rust]
    history_events: Option<mpsc::Receiver<String>>,
}

impl MuseNativePrototypeView {
    fn status(&self, cx: &mut Cx, text: &str) {
        self.view.label(cx, ids!(status)).set_text(cx, text);
    }

    fn request_read(&mut self, cx: &mut Cx) {
        if self.running || self.history_events.is_some() {
            return;
        }
        self.last_turn = None;
        self.view.label(cx, ids!(evidence)).set_text(cx, "尚无本回合工具证据。");
        let Some(service) = self.service.as_ref() else {
            self.status(cx, "Shell 未提供 assistant；请检查首次 consent、构建和 Host 状态，再重新打开模块。");
            return;
        };
        if self.context.as_ref().is_none_or(|context| !context.is_open()) {
            // This module has no login/accounts. Bind only the standard device key.
            service.set_account(Some(DEVICE_ACCOUNT));
            match service.open_conversation(ContextSpec {
                account: DEVICE_ACCOUNT.into(),
                instance: self.instance.clone(),
                services: service.services(),
            }) {
                Ok(context) => self.context = Some(context),
                Err(error) => {
                    self.status(cx, &format!("Host 拒绝打开：{error}"));
                    return;
                }
            }
        }
        let (sender, receiver) = mpsc::channel();
        let sink: EventSink = Arc::new(move |event| {
            // Progress does not prove a tool ran; retain only the final Host response.
            if matches!(event, ContextEvent::Complete(_)) && sender.send(event).is_ok() {
                SignalToUI::set_ui_signal();
            }
        });
        let context = self.context.as_ref().expect("opened above");
        // App provenance is intentional. This prototype never claims a trusted Person.
        match context.call(
            ContextOp::TurnFrom { text: READ_REQUEST.into(), trigger: TurnTrigger::App },
            sink,
        ) {
            Ok(()) => {
                self.events = Some(receiver);
                self.running = true;
                self.status(cx, "请求已受理；须以真实 Relay/工具结果核实读取。此状态不代表日历读取成功。");
            }
            Err(error) => self.status(cx, &format!("Host 拒绝请求：{error}")),
        }
    }

    fn request_history(&mut self, cx: &mut Cx) {
        if self.running || self.history_events.is_some() {
            return;
        }
        let (Some(context), Some(turn)) = (self.context.as_ref(), self.last_turn.clone()) else {
            self.status(cx, "没有可关联的已完成回合；请先发起只读请求。");
            return;
        };
        let (sender, receiver) = mpsc::sync_channel(1);
        let sink: EventSink = Arc::new(move |event| {
            let ContextEvent::Complete(result) = event else { return };
            let text = match result {
                Ok(value) => history::calendar_evidence(&value, &turn),
                Err(_) => "读取证据不足：Host 无法提供本 App 历史。".into(),
            };
            if sender.send(text).is_ok() {
                SignalToUI::set_ui_signal();
            }
        });
        // One explicit read, no model turn, grant, polling, file or other runtime.
        match context.call(ContextOp::History, sink) {
            Ok(()) => {
                self.history_events = Some(receiver);
                self.status(cx, "正在读取本回合历史；停止可取消。");
            }
            Err(_) => self.status(cx, "Host 拒绝读取历史；未取得工具证据。"),
        }
    }

    fn shutdown(&mut self) {
        if let Some(context) = self.context.take() {
            context.close();
        }
        self.events = None;
        self.history_events = None;
        self.last_turn = None;
        self.running = false;
        // Release this instance's leases; never shutdown the shared runtime.
        if let Some(service) = self.service.take() {
            service.release();
        }
    }
}

impl Widget for MuseNativePrototypeView {
    fn draw_walk(&mut self, cx: &mut Cx2d, scope: &mut Scope, walk: Walk) -> DrawStep {
        self.view.draw_walk(cx, scope, walk)
    }

    fn handle_event(&mut self, cx: &mut Cx, event: &Event, scope: &mut Scope) {
        self.view.handle_event(cx, event, scope);
        if let Some(ContextEvent::Complete(result)) = self.events.as_ref().and_then(|rx| rx.try_recv().ok()) {
            self.events = None;
            self.running = false;
            match result {
                Ok(value) => {
                    self.last_turn = value.get("turn_id").and_then(|v| v.as_str())
                        .filter(|id| !id.is_empty() && id.len() <= 256).map(str::to_owned);
                    self.status(cx, "Host 回合结束；可查看读取证据，尚未认定 Relay 通过。");
                }
                Err(error) => self.status(cx, &format!("Host 回合失败：{error}")),
            }
        }
        if self.history_events.is_some() && self.context.as_ref().is_none_or(|context| !context.is_open()) {
            self.history_events = None;
            self.last_turn = None;
            self.view.label(cx, ids!(evidence)).set_text(cx, "读取证据不足：请求 context 已关闭。");
            self.status(cx, "历史等待已清除；请求 context 已关闭。");
        }
        if let Some(result) = self.history_events.as_ref().map(|rx| rx.try_recv()) {
            match result {
                Ok(text) => {
                    self.history_events = None;
                    self.view.label(cx, ids!(evidence)).set_text(cx, &text);
                    self.status(cx, "历史读取结束；工具正文仍须与独立审计核对。");
                }
                Err(mpsc::TryRecvError::Disconnected) => {
                    self.history_events = None;
                    self.view.label(cx, ids!(evidence)).set_text(cx, "读取证据不足：Host 未交付历史结果。");
                    self.status(cx, "历史通道已关闭，等待已清除。");
                }
                Err(mpsc::TryRecvError::Empty) => {}
            }
        }
        if let Event::Actions(actions) = event {
            if self.view.button(cx, ids!(read)).clicked(actions) {
                self.request_read(cx);
            }
            if self.view.button(cx, ids!(history)).clicked(actions) {
                self.request_history(cx);
            }
            if self.view.button(cx, ids!(stop)).clicked(actions) {
                // Closing the scoped context interrupts it and drops late replies.
                if let Some(context) = self.context.take() {
                    context.close();
                }
                self.events = None;
                self.history_events = None;
                self.last_turn = None;
                self.running = false;
                self.view.label(cx, ids!(evidence)).set_text(cx, "已关闭 context；读取证据已清除。");
                self.status(cx, "已关闭请求 context；后续结果丢弃。未更改 Calendar。");
            }
        }
    }
}

pub struct MuseNativePrototypeModule;
pub static MUSE_NATIVE_PROTOTYPE_MODULE: MuseNativePrototypeModule = MuseNativePrototypeModule;

impl AppModule for MuseNativePrototypeModule {
    fn id(&self) -> &'static str { APP_ID }
    fn label(&self) -> &'static str { "Muse 原生只读原型" }
    fn register(&self, vm: &mut ScriptVm) { script_mod(vm); }
    fn open_schema(&self) -> OpenSchema { OpenSchema::new(1) }
    fn capabilities(&self) -> &'static [&'static str] {
        &["octos.session.open", "octos.session.history", "octos.turn.start", "octos.turn.interrupt"]
    }
    fn create(&self, vm: &mut ScriptVm, _open: ValidatedOpen, handles: InstanceHandles) -> InstanceParts {
        let instance = handles.scope.to_string();
        let service = injection::claim(APP_ID, &instance);
        let value = script_eval!(vm, { use mod.widgets.* MuseNativePrototypeView {} });
        let root = WidgetRef::script_from_value(vm, value);
        if let Some(mut view) = root.borrow_mut::<MuseNativePrototypeView>() {
            view.service = service;
            view.instance = instance;
        }
        let shutdown_root = root.clone();
        InstanceParts {
            root,
            executor: Box::new(NoOwnTools),
            shutdown: Box::new(move |_vm| {
                if let Some(mut view) = shutdown_root.borrow_mut::<MuseNativePrototypeView>() {
                    view.shutdown();
                }
            }),
        }
    }
}

struct NoOwnTools;
impl ServiceExecutor for NoOwnTools {
    fn manifest(&self) -> ServiceManifest {
        // The service-bus slug has a separate [a-z0-9_]{1,24} grammar.
        ServiceManifest::new("muse_native_prototype", "Muse 原生只读原型", "Read-only Calendar integration probe; no own tools.")
    }
    fn execute(&mut self, _cx: &mut Cx, call: &ServiceCall) -> ExecOutcome {
        ExecOutcome::Done(ToolResult::unavailable(&call.call_id, "This prototype declares no own tools"))
    }
}
