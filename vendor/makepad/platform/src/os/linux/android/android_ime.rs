//! Android editor operations. The focused Rust widget is the canonical owner;
//! Java's Editable is an optimistic mirror, never an unversioned replacement.
#[derive(Clone, Debug, PartialEq)]
pub struct EditorState {
    pub text: String,
    pub selection: (usize, usize), // UTF-16 offsets, Android InputConnection units
    pub composition: Option<(usize, usize)>,
}
#[derive(Clone, Debug)]
pub struct Edit {
    pub kind: i32, pub text: String, pub start: i32, pub end: i32, pub cursor: i32,
}
impl EditorState {
    fn floor(text: &[u16], mut at: usize) -> usize {
        at=at.min(text.len());
        if at>0 && at<text.len() && (0xdc00..=0xdfff).contains(&text[at]) && (0xd800..=0xdbff).contains(&text[at-1]) {at-=1;}
        at
    }
    fn ceil(text:&[u16],at:usize)->usize {let at=at.min(text.len());let floor=Self::floor(text,at);if floor<at {(floor+2).min(text.len())}else{at}}
    fn clamp(text:&[u16],at:i32)->usize {Self::floor(text,if at<0 {text.len()}else{at as usize})}
    fn step(text:&[u16],mut at:usize,amount:i32)->usize {
        for _ in 0..amount.unsigned_abs().min(text.len() as u32) {if amount<0 {if at==0 {break;}at=Self::floor(text,at-1);}else{if at==text.len(){break;}at=Self::ceil(text,at+1);}}
        at
    }
    pub fn apply(&mut self,edit:&Edit)->bool {
        if !(1..=12).contains(&edit.kind)||edit.text.len()>4*1024*1024 {return false;}
        let mut text:Vec<u16>=self.text.encode_utf16().collect();
        let mut a=Self::floor(&text,self.selection.0);let mut b=Self::floor(&text,self.selection.1);
        if a>b {std::mem::swap(&mut a,&mut b);}
        let composition=self.composition.map(|(a,b)|(Self::floor(&text,a),Self::ceil(&text,b))).filter(|(a,b)|a<b);
        match edit.kind {
            1|2|8=> { // commit, compose, explicit replacement
                let (start,end)=if edit.kind==8 {
                    let a=Self::clamp(&text,edit.start);let b=Self::clamp(&text,edit.end);(a.min(b),a.max(b))
                }else{composition.unwrap_or((a,b))};
                let insert:Vec<u16>=edit.text.encode_utf16().collect();let length=insert.len();
                text.splice(start..end,insert);
                let cursor=if edit.cursor>0 {(start+length) as i64+edit.cursor as i64-1}else{start as i64+edit.cursor as i64};
                let cursor=Self::floor(&text,cursor.clamp(0,text.len() as i64) as usize);
                self.selection=(cursor,cursor);
                self.composition=if edit.kind==2&&length>0 {Some((start,start+length))}else{None};
            },
            3=>self.composition=None,
            4|5=> { // surrounding deletion preserves the selected range
                let (start,end)=if edit.kind==5 {(Self::step(&text,a,-edit.start.max(0)),Self::step(&text,b,edit.end.max(0)))}else{(Self::floor(&text,a.saturating_sub(edit.start.max(0) as usize)),Self::ceil(&text,b.saturating_add(edit.end.max(0) as usize)))};
                text.drain(b..end);text.drain(start..a);self.selection=(start,start+(b-a));self.composition=None;
            },
            6=> {
                let start=Self::clamp(&text,edit.start);let end=Self::clamp(&text,edit.end);self.selection=(start,end);
                if composition.is_some_and(|(a,b)|start.min(end)<a||start.max(end)>b) {self.composition=None;}
            },
            7=> {let a=Self::clamp(&text,edit.start);let b=Self::clamp(&text,edit.end);self.composition=if a==b {None}else{Some((a.min(b),a.max(b)))};},
            9=> {self.selection=(0,text.len());self.composition=None;},
            10=> {text.drain(a..b);self.selection=(a,a);self.composition=None;},
            11|12=> { // physical backspace/delete uses canonical selection
                let (start,end)=if a!=b {(a,b)}else if edit.kind==11 {(Self::step(&text,a,-1),a)}else{(b,Self::step(&text,b,1))};
                text.drain(start..end);self.selection=(start,start);self.composition=None;
            },
            _=>return false,
        }
        let Ok(value)=String::from_utf16(&text) else{return false;};self.text=value;true
    }
}
