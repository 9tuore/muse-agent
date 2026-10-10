//! Host-owned ceiling only. Manifest admission, consent and relay grants
//! remain authoritative. No script API or environment switch enables this.
use std::sync::atomic::{AtomicBool, Ordering};

pub struct StoreAgentOffer(AtomicBool);

impl StoreAgentOffer {
    pub const fn new() -> Self { Self(AtomicBool::new(false)) }
    pub fn enable_calendar(&self, enabled: bool) { self.0.store(enabled, Ordering::SeqCst); }
    pub fn extend(&self, offered: &mut Vec<String>) {
        if self.0.load(Ordering::SeqCst) {
            for tool in ["calendar.events", "calendar.add_event", "calendar.notify"] {
                if !offered.iter().any(|name| name == tool) { offered.push(tool.into()); }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn disabled_by_default() {
        let offer = StoreAgentOffer::new();
        let mut tools = vec!["ask_user_question".into()];
        offer.extend(&mut tools);
        assert_eq!(tools, ["ask_user_question"]);
    }
    #[test]
    fn enables_only_original_shareable_tools_and_preserves_existing() {
        let offer = StoreAgentOffer::new();
        offer.enable_calendar(true);
        let mut tools = vec!["ask_user_question".into(), "calendar.events".into()];
        offer.extend(&mut tools); offer.extend(&mut tools);
        assert_eq!(tools, ["ask_user_question", "calendar.events", "calendar.add_event", "calendar.notify"]);
        for forbidden in ["calendar.update_event", "calendar.remove_event", "calendar.get_event", "shell", "dev.run"] {
            assert!(!tools.iter().any(|tool| tool == forbidden));
        }
    }
    #[test]
    fn revoked_offer_does_not_extend_new_admission() {
        let offer = StoreAgentOffer::new();
        offer.enable_calendar(true); offer.enable_calendar(false);
        let mut tools = Vec::new(); offer.extend(&mut tools);
        assert!(tools.is_empty());
    }
}
