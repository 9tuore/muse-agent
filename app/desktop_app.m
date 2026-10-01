#import <Cocoa/Cocoa.h>
#import <ApplicationServices/ApplicationServices.h>
#import <UserNotifications/UserNotifications.h>
#import <CommonCrypto/CommonHMAC.h>
#import <Security/Security.h>
#import <math.h>
#import "muse_model_manager.h"

@interface GOSIMAppDelegate : NSObject <NSApplicationDelegate, NSWindowDelegate, UNUserNotificationCenterDelegate, NSTextFieldDelegate>
@property(nonatomic, strong) NSWindow *window;
@property(nonatomic, strong) NSWindow *technicalWindow;
@property(nonatomic, strong) NSWindow *activityWindow;
@property(nonatomic, strong) NSTextField *activityState;
@property(nonatomic, strong) NSTextView *activityEventsView;
@property(nonatomic, strong) NSButton *activityToggle;
@property(nonatomic, strong) NSButton *activityTextEdit;
@property(nonatomic, strong) NSButton *activityEdge;
@property(nonatomic, assign) BOOL activityEnabled;
@property(nonatomic, strong) NSMutableArray<NSString *> *activityLines;
@property(nonatomic, copy) NSString *pendingTextEditRequestID;
@property(nonatomic, copy) NSString *pendingBrowserRecipeRequestID;
@property(nonatomic, copy) NSString *pendingBrowserGoalText;
@property(nonatomic, strong) NSMutableDictionary<NSString *, NSArray<NSDictionary *> *> *browserObservedControls;
@property(nonatomic, strong) NSTextField *modelStatus;
@property(nonatomic, strong) NSTextField *routeStatus;
@property(nonatomic, strong) NSTextField *taskTitle;
@property(nonatomic, strong) NSTextField *taskState;
@property(nonatomic, strong) NSTextField *permissionStatus;
@property(nonatomic, strong) NSTextField *watchStatus;
@property(nonatomic, strong) NSTextField *workerStatus;
@property(nonatomic, strong) NSTextField *notificationStatus;
@property(nonatomic, strong) NSTextView *logView;
@property(nonatomic, strong) NSTextView *technicalPlanView;
@property(nonatomic, strong) NSTextView *messageView;
@property(nonatomic, strong) NSTextView *stepsView;
@property(nonatomic, strong) NSTextView *chatView;
@property(nonatomic, strong) NSView *welcomeView;
@property(nonatomic, strong) NSTextField *chatInput;
@property(nonatomic, strong) NSButton *chatSendButton;
@property(nonatomic, copy) NSString *pendingChatPreviewRequestID;
@property(nonatomic, copy) NSString *pendingChatPreviewText;
@property(nonatomic, strong) NSArray<NSString *> *pendingChatMemoryScopes;
@property(nonatomic, strong) NSTextField *memoryStatus;
@property(nonatomic, strong) NSPopUpButton *goalPicker;
@property(nonatomic, strong) NSPopUpButton *goalResourcePicker;
@property(nonatomic, strong) NSTextField *modelEndpointField;
@property(nonatomic, strong) NSTextField *modelEndpointWarning;
@property(nonatomic, strong) NSButton *modelSettingsSaveButton;
@property(nonatomic, strong) NSButton *goalApproveButton;
@property(nonatomic, strong) NSButton *goalRejectButton;
@property(nonatomic, strong) NSButton *goalPauseButton;
@property(nonatomic, strong) NSButton *goalResumeButton;
@property(nonatomic, strong) NSButton *goalCancelButton;
@property(nonatomic, strong) NSButton *goalReviseButton;
@property(nonatomic, strong) NSButton *goalRetryButton;
@property(nonatomic, strong) NSBox *officialPanel;
@property(nonatomic, strong) NSTextField *officialState;
@property(nonatomic, strong) NSTextView *officialPlanView;
@property(nonatomic, strong) NSButton *officialApproveButton;
@property(nonatomic, strong) NSButton *officialDenyButton;
@property(nonatomic, strong) NSTimer *officialPollTimer;
@property(nonatomic, strong) NSDictionary *officialPending;
@property(nonatomic, copy) NSString *officialWitnessSecret;
@property(nonatomic, assign) BOOL officialApprovalAvailable;
@property(nonatomic, assign) BOOL officialDecisionInFlight;
@property(nonatomic, strong) NSTextField *pathField;
@property(nonatomic, strong) NSPopUpButton *commandPopup;
@property(nonatomic, strong) NSButton *sendButton;
@property(nonatomic, strong) NSButton *highTierToggle;
@property(nonatomic, strong) NSButton *terminalButton;
@property(nonatomic, strong) NSButton *approveButton;
@property(nonatomic, strong) NSButton *rejectButton;
@property(nonatomic, strong) NSTask *worker;
@property(nonatomic, strong) NSTask *mailBridge;
@property(nonatomic, strong) NSButton *mailModuleButton;
@property(nonatomic, strong) NSBox *inspectorCard;
@property(nonatomic, strong) NSView *taskPane;
@property(nonatomic, strong) NSBox *skillPane;
@property(nonatomic, strong) NSSegmentedControl *inspectorTabs;
@property(nonatomic, strong) MuseModelManager *modelManager;
@property(nonatomic, strong) NSWindow *downloadWindow;
@property(nonatomic, strong) NSProgressIndicator *downloadProgress;
@property(nonatomic, strong) NSTextField *downloadStatus;
@property(nonatomic, copy) NSString *pendingSetupMode;
@property(nonatomic, strong) NSFileHandle *workerInput;
@property(nonatomic, assign) BOOL paused;
@property(nonatomic, assign) BOOL pending;
@property(nonatomic, assign) BOOL selfTest;
@property(nonatomic, copy) NSString *workspace;
@property(nonatomic, copy) NSString *lineBuffer;
@property(nonatomic, strong) NSTimer *mailRecoveryTimer;
@property(nonatomic, strong) NSWindow *mailContactsWindow;
@property(nonatomic, strong) NSScrollView *mailContactsScroll;
@property(nonatomic, strong) NSTextField *mailContactsStatus;
@property(nonatomic, strong) NSArray<NSDictionary *> *mailContacts;
@property(nonatomic, strong) NSDate *lastMailStartAttempt;
@property(nonatomic, strong) NSDate *lastMailRestartAttempt;
@property(nonatomic, assign) BOOL mailKeychainLookupInProgress;
@property(nonatomic, assign) BOOL mailAutoConnectAllowed;
@property(nonatomic, strong) NSTimer *modelHealthTimer;
@property(nonatomic, strong) NSDate *lastModelStartAttempt;
@property(nonatomic, strong) NSBox *mailPanel;
@property(nonatomic, strong) NSTextField *mailPrompt;
@property(nonatomic, strong) NSTextView *mailEditor;
@property(nonatomic, strong) NSButton *mailPrimaryButton;
@property(nonatomic, strong) NSButton *mailSecondaryButton;
@property(nonatomic, strong) NSButton *mailLaterButton;
@property(nonatomic, copy) NSString *activeMailCardID;
@property(nonatomic, copy) NSString *activeMailState;
@property(nonatomic, strong) NSMutableSet<NSString *> *notifiedMailCards;
@property(nonatomic, copy) NSString *activeGoalID;
@property(nonatomic, strong) NSNumber *activeGoalRevision;
@property(nonatomic, copy) NSString *activeGoalPlanDigest;
@property(nonatomic, strong) NSDictionary *modelSettings;
@property(nonatomic, strong) NSDictionary *pricingStatus;
@property(nonatomic, assign) BOOL reasoningDialogRequested;
@property(nonatomic, strong) NSDictionary *memorySettings;
@property(nonatomic, strong) NSArray<NSString *> *availableGoalResultScopes;
@property(nonatomic, copy) NSString *selectedGoalResultScope;
@property(nonatomic, strong) NSDictionary *proactivitySettings;
@property(nonatomic, strong) NSDictionary *briefSettings;
@property(nonatomic, strong) NSMutableSet<NSString *> *displayedBriefIDs;
@property(nonatomic, strong) NSArray<NSDictionary *> *memoryRecords;
@property(nonatomic, strong) NSArray<NSDictionary *> *watches;
@property(nonatomic, strong) NSArray<NSDictionary *> *plugins;
@property(nonatomic, assign) BOOL pluginDialogRequested;
@property(nonatomic, strong) NSPopUpButton *memoryRecordPicker;
@property(nonatomic, strong) NSTextView *memoryRecordEditor;
@property(nonatomic, strong) NSMutableDictionary<NSString *, NSDictionary *> *goalNotifyByID;
@property(nonatomic, strong) NSMutableDictionary<NSString *, NSString *> *goalArtifactsByID;
@property(nonatomic, strong) NSMutableDictionary<NSString *, NSString *> *goalDisplayStatusByID;
@property(nonatomic, strong) NSMutableDictionary<NSString *, NSDate *> *lastGoalNotificationAt;
@end

@implementation GOSIMAppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    self.paused = NO;
    self.mailAutoConnectAllowed = YES;
    self.pending = NO;
    self.selfTest = [[[NSProcessInfo processInfo] arguments] containsObject:@"--self-test"];
    self.lineBuffer = @"";
    self.notifiedMailCards = [NSMutableSet set];
    self.goalNotifyByID = [NSMutableDictionary dictionary];
    self.goalArtifactsByID = [NSMutableDictionary dictionary];
    self.goalDisplayStatusByID = [NSMutableDictionary dictionary];
    self.lastGoalNotificationAt = [NSMutableDictionary dictionary];
    self.displayedBriefIDs = [NSMutableSet set];
    self.activityLines = [NSMutableArray array];
    self.browserObservedControls = [NSMutableDictionary dictionary];
    [UNUserNotificationCenter currentNotificationCenter].delegate = self;
    NSString *home = NSHomeDirectory();
    self.workspace = [[[NSProcessInfo processInfo] environment] objectForKey:@"AGENT_WORKSPACE"];
    if (self.workspace.length == 0) {
        self.workspace = [home stringByAppendingPathComponent:@"Library/Application Support/GOSIM Local Agent/workspace"];
    }
    [[NSFileManager defaultManager] createDirectoryAtPath:self.workspace withIntermediateDirectories:YES attributes:nil error:nil];
    NSArray *shown = [NSArray arrayWithContentsOfFile:[self.workspace stringByAppendingPathComponent:@".muse_displayed_briefs.plist"]];
    if ([shown isKindOfClass:[NSArray class]]) for (id item in shown) {
        if ([item isKindOfClass:[NSString class]]) [self.displayedBriefIDs addObject:item];
    }
    self.modelManager = [[MuseModelManager alloc] initWithResources:[[NSBundle mainBundle] resourcePath]
                                                       support:[self.workspace stringByDeletingLastPathComponent]];
    [[UNUserNotificationCenter currentNotificationCenter] getNotificationSettingsWithCompletionHandler:^(UNNotificationSettings *settings) {
        NSString *status = settings.authorizationStatus == UNAuthorizationStatusAuthorized ? @"NOTIFICATIONS_READY" : @"NOTIFICATIONS_NEED_AUTH";
        [self recordNotificationStatus:status cardID:@"" detail:[NSString stringWithFormat:@"authorization=%ld alert=%ld", (long)settings.authorizationStatus, (long)settings.alertSetting]];
    }];
    [self buildMenu];
    [self buildWindow];
    [self startWorker];
    [self requestSystemStatus];
    [self sendEvent:@{@"type": @"model_settings_get"}];
    [self sendEvent:@{@"type": @"model_pricing_get"}];
    [self sendEvent:@{@"type": @"memory_settings_get"}];
    [self sendEvent:@{@"type": @"memory_scope_list"}];
    [self sendEvent:@{@"type": @"proactivity_settings_get"}];
    [self sendEvent:@{@"type": @"brief_settings_get"}];
    [self sendEvent:@{@"type": @"watch_folder_list"}];
    [self sendEvent:@{@"type": @"goal_list"}];
    self.mailRecoveryTimer = [NSTimer scheduledTimerWithTimeInterval:2.0 target:self selector:@selector(checkPendingMailCard:) userInfo:nil repeats:YES];
    [self checkPendingMailCard:nil];
    [self checkModelHealth];
    [self performSelector:@selector(startManagedModelIfConfigured) withObject:nil afterDelay:0.5];
    self.modelHealthTimer = [NSTimer scheduledTimerWithTimeInterval:30.0 target:self selector:@selector(checkModelHealth) userInfo:nil repeats:YES];
    [self performSelector:@selector(startRememberedMailBridge) withObject:nil afterDelay:1.5];
    if (!self.selfTest && ![[[[NSProcessInfo processInfo] environment] objectForKey:@"GOSIM_SKIP_ONBOARDING"] boolValue] &&
        ![[[[NSProcessInfo processInfo] environment] objectForKey:@"GOSIM_BACKGROUND_TEST"] boolValue]) {
        [self performSelector:@selector(showFirstRunIfNeeded) withObject:nil afterDelay:1.0];
    }
    [self appendLog:@"窗口已启动；文件和终端动作都会先进入待确认任务卡。"];
    [self appendLog:@"共享 Qwen 服务由用户管理；退出本应用不会终止它。"];
    NSString *cardFixture = [[[NSProcessInfo processInfo] environment] objectForKey:@"GOSIM_UI_TEST_CARD"];
    if ([cardFixture isEqualToString:@"error"]) {
        [self performSelector:@selector(showResult:) withObject:@{@"ok": @NO, @"error": @"fixture_error"} afterDelay:2.0];
    } else if ([cardFixture isEqualToString:@"long"]) {
        NSString *detail = @"这是用于检查狭窄窗口的长中文结果卡：资料来源变化需要逐条核对，模型整理的提纲和资料要点尚未完成事实核验。请打开产物查看来源清单、采集时间、引用编号与每项待你决定的内容；对于无法读取的来源，保持等待，不推测正文。";
        [self performSelector:@selector(showResult:) withObject:@{@"ok": @YES,
            @"result_card": @{@"title": @"长中文资料整理与来源核对", @"status": @"WAITING_USER",
                              @"summary": detail, @"next_step": detail, @"source": @"ui_fixture"}} afterDelay:2.0];
    }
    if (self.selfTest) {
        [self.window orderFrontRegardless];
        [self performSelector:@selector(runSelfTestInput) withObject:nil afterDelay:0.3];
    }
}

- (void)buildMenu {
    NSMenu *main = [[NSMenu alloc] initWithTitle:@"MainMenu"];
    NSMenuItem *agentItem = [[NSMenuItem alloc] initWithTitle:@"Agent" action:nil keyEquivalent:@""];
    NSMenu *agent = [[NSMenu alloc] initWithTitle:@"Agent"];
    [agent addItemWithTitle:@"暂停监听" action:@selector(togglePause:) keyEquivalent:@"p"];
    [agent addItemWithTitle:@"查看任务记录" action:@selector(showTasks:) keyEquivalent:@"t"];
    [agent addItemWithTitle:@"技术详情" action:@selector(showTechnicalDetails:) keyEquivalent:@"d"];
    [agent addItemWithTitle:@"模型与预算设置" action:@selector(showModelSettings:) keyEquivalent:@","];
    [agent addItemWithTitle:@"备用高阶模型" action:@selector(showBackupModelSettings:) keyEquivalent:@""];
    [agent addItemWithTitle:@"高阶密钥与价格" action:@selector(showHighProviderSecurity:) keyEquivalent:@""];
    [agent addItemWithTitle:@"模型推理强度" action:@selector(showReasoningSettings:) keyEquivalent:@""];
    [agent addItemWithTitle:@"记忆记录设置" action:@selector(showMemorySettings:) keyEquivalent:@""];
    [agent addItemWithTitle:@"管理本机记忆" action:@selector(requestMemoryList:) keyEquivalent:@""];
    [agent addItemWithTitle:@"主动通知设置" action:@selector(showProactivitySettings:) keyEquivalent:@""];
    [agent addItemWithTitle:@"每日简报设置" action:@selector(showBriefSettings:) keyEquivalent:@""];
    [agent addItemWithTitle:@"系统权限自检" action:@selector(showPermissionsGuide:) keyEquivalent:@""];
    [agent addItemWithTitle:@"选择监控文件夹" action:@selector(selectWatchedFolder:) keyEquivalent:@""];
    [agent addItemWithTitle:@"撤销监控文件夹" action:@selector(revokeWatchedFolder:) keyEquivalent:@""];
    [agent addItemWithTitle:@"TextEdit 合成文件配方" action:@selector(prepareTextEditRecipe:) keyEquivalent:@""];
    [agent addItemWithTitle:@"Edge 公开搜索目标" action:@selector(prepareBrowserRecipe:) keyEquivalent:@""];
    [agent addItemWithTitle:@"连接或断开 QQ 邮箱" action:@selector(showMailBridgeConnection:) keyEquivalent:@""];
    [agent addItemWithTitle:@"插件与权限" action:@selector(requestPluginSettings:) keyEquivalent:@""];
    [agent addItem:[NSMenuItem separatorItem]];
    [agent addItemWithTitle:@"停止本应用服务" action:@selector(stopOwnedWorkers:) keyEquivalent:@""];
    [agent addItemWithTitle:@"退出全部" action:@selector(quitAll:) keyEquivalent:@"q"];
    [agentItem setSubmenu:agent];
    [main addItem:agentItem];
    NSMenuItem *editItem = [[NSMenuItem alloc] initWithTitle:@"编辑" action:nil keyEquivalent:@""];
    NSMenu *edit = [[NSMenu alloc] initWithTitle:@"编辑"];
    [edit addItemWithTitle:@"撤销" action:@selector(undo:) keyEquivalent:@"z"];
    NSMenuItem *redo = [edit addItemWithTitle:@"重做" action:@selector(redo:) keyEquivalent:@"z"];
    redo.keyEquivalentModifierMask = NSEventModifierFlagCommand | NSEventModifierFlagShift;
    [edit addItem:[NSMenuItem separatorItem]];
    [edit addItemWithTitle:@"剪切" action:@selector(cut:) keyEquivalent:@"x"];
    [edit addItemWithTitle:@"复制" action:@selector(copy:) keyEquivalent:@"c"];
    [edit addItemWithTitle:@"粘贴" action:@selector(paste:) keyEquivalent:@"v"];
    [edit addItemWithTitle:@"全选" action:@selector(selectAll:) keyEquivalent:@"a"];
    [editItem setSubmenu:edit];
    [main addItem:editItem];
    NSMenuItem *helpItem = [[NSMenuItem alloc] initWithTitle:@"帮助" action:nil keyEquivalent:@""];
    NSMenu *help = [[NSMenu alloc] initWithTitle:@"帮助"];
    [help addItemWithTitle:@"关于" action:@selector(showAbout:) keyEquivalent:@""];
    [helpItem setSubmenu:help];
    [main addItem:helpItem];
    [NSApp setMainMenu:main];
}

- (NSTextField *)label:(NSString *)text frame:(NSRect)frame size:(CGFloat)size color:(NSColor *)color {
    NSTextField *label = [[NSTextField alloc] initWithFrame:frame];
    label.stringValue = text;
    label.bezeled = NO;
    label.drawsBackground = NO;
    label.editable = NO;
    label.selectable = NO;
    label.font = [NSFont systemFontOfSize:size weight:(size >= 16 ? NSFontWeightBold : NSFontWeightRegular)];
    label.textColor = color ?: [NSColor colorWithCalibratedWhite:0.10 alpha:1];
    return label;
}

- (NSBox *)card:(NSString *)title frame:(NSRect)frame parent:(NSView *)parent {
    NSBox *box = [[NSBox alloc] initWithFrame:frame];
    box.title = title;
    box.boxType = NSBoxCustom;
    box.borderType = NSBezelBorder;
    box.borderColor = [NSColor separatorColor];
    box.borderWidth = 0.5;
    box.cornerRadius = 12;
    box.fillColor = [NSColor controlBackgroundColor];
    box.contentViewMargins = NSMakeSize(12, 12);
    [parent addSubview:box];
    return box;
}

- (void)setInspectorText:(NSString *)text {
    NSMutableAttributedString *styled = [[NSMutableAttributedString alloc] initWithString:text ?: @""];
    NSRange entire = NSMakeRange(0, styled.length);
    NSMutableParagraphStyle *paragraph = [[NSMutableParagraphStyle alloc] init];
    paragraph.lineSpacing = 3;
    [styled addAttributes:@{NSFontAttributeName: [NSFont systemFontOfSize:13],
                            NSForegroundColorAttributeName: [NSColor labelColor],
                            NSParagraphStyleAttributeName: paragraph} range:entire];
    NSUInteger offset = 0;
    for (NSString *section in [styled.string componentsSeparatedByString:@"\n\n"]) {
        NSRange colon = [section rangeOfString:@"："];
        if (colon.location != NSNotFound && colon.location < 24) {
            [styled addAttributes:@{NSFontAttributeName: [NSFont systemFontOfSize:12 weight:NSFontWeightSemibold],
                                    NSForegroundColorAttributeName: [NSColor secondaryLabelColor]}
                            range:NSMakeRange(offset, colon.location + 1)];
        }
        offset += section.length + 2;
    }
    [self.stepsView.textStorage setAttributedString:styled];
}

- (void)buildWindow {
    NSRect frame = NSMakeRect(0, 0, 1280, 800);
    self.window = [[NSWindow alloc] initWithContentRect:frame styleMask:(NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable) backing:NSBackingStoreBuffered defer:NO];
    self.window.title = @"Muse · GOSIM";
    self.window.minSize = NSMakeSize(980, 640);
    self.window.delegate = self;
    NSString *testAppearance = [[[NSProcessInfo processInfo] environment] objectForKey:@"GOSIM_UI_TEST_APPEARANCE"];
    if ([testAppearance isEqualToString:@"dark"]) self.window.appearance = [NSAppearance appearanceNamed:NSAppearanceNameDarkAqua];
    if ([testAppearance isEqualToString:@"light"]) self.window.appearance = [NSAppearance appearanceNamed:NSAppearanceNameAqua];
    [self.window center];
    NSView *content = self.window.contentView;
    NSTextField *appTitle = [self label:@"Muse" frame:NSMakeRect(25, 738, 180, 36) size:26 color:[NSColor labelColor]];
    appTitle.autoresizingMask = NSViewMinYMargin;
    [content addSubview:appTitle];
    NSTextField *appSubtitle = [self label:@"本机优先 · 清楚授权 · 持续跟进" frame:NSMakeRect(225, 746, 360, 20) size:12 color:[NSColor secondaryLabelColor]];
    appSubtitle.autoresizingMask = NSViewMinYMargin;
    [content addSubview:appSubtitle];
    NSString *version = [[NSBundle mainBundle] objectForInfoDictionaryKey:@"CFBundleShortVersionString"] ?: @"?";
    NSTextField *versionLabel = [self label:[@"版本 " stringByAppendingString:version]
                                      frame:NSMakeRect(1130, 746, 125, 20) size:11 color:[NSColor secondaryLabelColor]];
    versionLabel.alignment = NSTextAlignmentRight;
    versionLabel.autoresizingMask = NSViewMinXMargin | NSViewMinYMargin;
    [content addSubview:versionLabel];

    NSBox *sidebar = [self card:@"" frame:NSMakeRect(16, 16, 190, 708) parent:content];
    sidebar.autoresizingMask = NSViewHeightSizable;
    NSView *side = sidebar.contentView;
    NSTextField *workspaceHeader = [self label:@"工作台" frame:NSMakeRect(14, 666, 160, 18) size:11 color:[NSColor secondaryLabelColor]];
    workspaceHeader.autoresizingMask = NSViewMinYMargin;
    [side addSubview:workspaceHeader];
    NSArray<NSString *> *navTitles = @[@"对话", @"长期目标", @"记忆", @"活动记录"];
    SEL navActions[] = {@selector(showConversation:), @selector(showGoals:), @selector(showMemories:), @selector(showActivity:)};
    for (NSUInteger i = 0; i < navTitles.count; i++) {
        NSButton *nav = [self button:navTitles[i] frame:NSMakeRect(12, 620 - 44 * i, 162, 34) action:navActions[i] parent:side];
        nav.alignment = NSTextAlignmentLeft;
        nav.bordered = NO;
        nav.font = [NSFont systemFontOfSize:14 weight:(i == 0 ? NSFontWeightSemibold : NSFontWeightRegular)];
        nav.contentTintColor = i == 0 ? [NSColor controlAccentColor] : [NSColor secondaryLabelColor];
        nav.autoresizingMask = NSViewMinYMargin;
    }
    NSTextField *extensionHeader = [self label:@"扩展" frame:NSMakeRect(14, 430, 160, 18) size:11 color:[NSColor secondaryLabelColor]];
    extensionHeader.autoresizingMask = NSViewMinYMargin;
    [side addSubview:extensionHeader];
    NSButton *skillsNavigation = [self button:@"查看技能位" frame:NSMakeRect(12, 386, 162, 34)
                                      action:@selector(showSkillSlots:) parent:side];
    skillsNavigation.alignment = NSTextAlignmentLeft;
    skillsNavigation.bordered = NO;
    skillsNavigation.autoresizingMask = NSViewMinYMargin;
    NSButton *pluginsNavigation = [self button:@"管理技能包" frame:NSMakeRect(12, 342, 162, 34)
                                       action:@selector(showCapabilities:) parent:side];
    pluginsNavigation.alignment = NSTextAlignmentLeft;
    pluginsNavigation.bordered = NO;
    pluginsNavigation.autoresizingMask = NSViewMinYMargin;
    NSButton *mailContactsNavigation = [self button:@"邮箱往来联系人" frame:NSMakeRect(12, 298, 162, 34)
                                          action:@selector(showMailContacts:) parent:side];
    mailContactsNavigation.alignment = NSTextAlignmentLeft;
    mailContactsNavigation.bordered = NO;
    mailContactsNavigation.autoresizingMask = NSViewMinYMargin;
    self.memoryStatus = [self label:@"记忆 · 正在读取" frame:NSMakeRect(14, 91, 162, 20) size:11 color:[NSColor secondaryLabelColor]];
    [side addSubview:self.memoryStatus];
    [self button:@"设置与首启" frame:NSMakeRect(12, 47, 162, 32) action:@selector(showSetup:) parent:side];
    [self button:@"暂停自动操作" frame:NSMakeRect(12, 9, 162, 32) action:@selector(togglePause:) parent:side];

    NSBox *conversation = [self card:@"对话" frame:NSMakeRect(222, 16, 714, 708) parent:content];
    conversation.autoresizingMask = NSViewWidthSizable | NSViewHeightSizable;
    NSView *middle = conversation.contentView;
    NSTextField *conversationTitle = [self label:@"今天想让 Muse 处理什么？" frame:NSMakeRect(16, 655, 650, 29) size:19 color:[NSColor labelColor]];
    conversationTitle.autoresizingMask = NSViewWidthSizable | NSViewMinYMargin;
    [middle addSubview:conversationTitle];
    NSTextField *intro = [self label:@"直接提问，或设为长期目标；执行前会先请你审阅计划。" frame:NSMakeRect(16, 631, 650, 20) size:12 color:[NSColor secondaryLabelColor]];
    intro.autoresizingMask = NSViewWidthSizable | NSViewMinYMargin;
    [middle addSubview:intro];
    NSScrollView *chatScroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(16, 130, 682, 483)];
    chatScroll.hasVerticalScroller = YES;
    chatScroll.autoresizingMask = NSViewWidthSizable | NSViewHeightSizable;
    chatScroll.drawsBackground = NO;
    self.chatView = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 682, 483)];
    self.chatView.editable = NO;
    self.chatView.verticallyResizable = YES;
    self.chatView.autoresizingMask = NSViewWidthSizable;
    self.chatView.textContainer.widthTracksTextView = YES;
    self.chatView.font = [NSFont systemFontOfSize:14];
    self.chatView.textContainerInset = NSMakeSize(12, 16);
    self.chatView.drawsBackground = NO;
    self.chatView.textColor = [NSColor labelColor];
    self.chatView.string = @"";
    self.chatView.accessibilityTitle = @"Muse 对话";
    chatScroll.documentView = self.chatView;
    [middle addSubview:chatScroll];
    self.welcomeView = [[NSView alloc] initWithFrame:NSMakeRect(36, 330, 642, 278)];
    self.welcomeView.autoresizingMask = NSViewWidthSizable | NSViewMinYMargin;
    [middle addSubview:self.welcomeView];
    NSTextField *welcomeEyebrow = [self label:@"开始使用" frame:NSMakeRect(0, 253, 610, 18) size:11 color:[NSColor controlAccentColor]];
    welcomeEyebrow.autoresizingMask = NSViewWidthSizable;
    [self.welcomeView addSubview:welcomeEyebrow];
    NSTextField *welcomeTitle = [self label:@"从一件具体的事开始" frame:NSMakeRect(0, 216, 610, 33) size:23 color:[NSColor labelColor]];
    welcomeTitle.autoresizingMask = NSViewWidthSizable;
    [self.welcomeView addSubview:welcomeTitle];
    NSTextField *welcomeDetail = [self label:@"先提问，或设一个需要持续跟进的目标。" frame:NSMakeRect(0, 184, 610, 25) size:13 color:[NSColor secondaryLabelColor]];
    welcomeDetail.autoresizingMask = NSViewWidthSizable;
    [self.welcomeView addSubview:welcomeDetail];
    NSArray<NSString *> *prompts = @[@"了解一项新变化  →", @"持续关注公开网页  →", @"整理选定文件夹  →"];
    for (NSUInteger i = 0; i < prompts.count; i++) {
        NSButton *prompt = [self button:prompts[i] frame:NSMakeRect(0, 131 - 44 * i, 610, 38)
                                 action:@selector(useWelcomePrompt:) parent:self.welcomeView];
        prompt.tag = (NSInteger)i;
        prompt.alignment = NSTextAlignmentLeft;
        prompt.font = [NSFont systemFontOfSize:13 weight:NSFontWeightMedium];
        prompt.autoresizingMask = NSViewWidthSizable;
    }
    NSTextField *welcomeNote = [self label:@"选中后还可以修改；批准计划前不会执行。" frame:NSMakeRect(0, 4, 610, 18) size:11 color:[NSColor tertiaryLabelColor]];
    welcomeNote.autoresizingMask = NSViewWidthSizable;
    [self.welcomeView addSubview:welcomeNote];
    self.goalResourcePicker = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(16, 101, 682, 26) pullsDown:NO];
    self.goalResourcePicker.autoresizingMask = NSViewWidthSizable;
    [self.goalResourcePicker addItemWithTitle:@"这次目标不附加监控目录"];
    self.goalResourcePicker.lastItem.representedObject = @"";
    [middle addSubview:self.goalResourcePicker];
    self.chatInput = [[NSTextField alloc] initWithFrame:NSMakeRect(16, 59, 682, 36)];
    self.chatInput.autoresizingMask = NSViewWidthSizable;
    self.chatInput.bezelStyle = NSTextFieldRoundedBezel;
    self.chatInput.font = [NSFont systemFontOfSize:14];
    self.chatInput.placeholderString = @"问一个问题，或描述想长期完成的事…";
    self.chatInput.accessibilityTitle = @"即时对话输入";
    [middle addSubview:self.chatInput];
    self.window.initialFirstResponder = self.chatInput;
    NSButton *chatSend = [self button:@"发送" frame:NSMakeRect(16, 16, 94, 34) action:@selector(sendChat:) parent:middle];
    chatSend.bezelColor = [NSColor controlAccentColor];
    self.chatSendButton = chatSend;
    self.window.defaultButtonCell = chatSend.cell;
    [self button:@"设为长期目标" frame:NSMakeRect(118, 16, 132, 34) action:@selector(proposeGoal:) parent:middle];
    [self button:@"Edge 搜索目标" frame:NSMakeRect(258, 16, 135, 34) action:@selector(prepareBrowserRecipe:) parent:middle];

    self.inspectorTabs = [[NSSegmentedControl alloc] initWithFrame:NSMakeRect(952, 690, 312, 34)];
    self.inspectorTabs.segmentCount = 2;
    [self.inspectorTabs setLabel:@"查看技能" forSegment:0];
    [self.inspectorTabs setLabel:@"结果卡" forSegment:1];
    self.inspectorTabs.selectedSegment = 0;
    self.inspectorTabs.target = self;
    self.inspectorTabs.action = @selector(switchInspectorTab:);
    self.inspectorTabs.autoresizingMask = NSViewMinXMargin | NSViewMinYMargin;
    [content addSubview:self.inspectorTabs];
    NSBox *inspector = [self card:@"" frame:NSMakeRect(952, 16, 312, 668) parent:content];
    self.inspectorCard = inspector;
    inspector.autoresizingMask = NSViewMinXMargin | NSViewHeightSizable;
    NSView *inspectorContent = inspector.contentView;
    NSView *right = [[NSView alloc] initWithFrame:inspectorContent.bounds];
    right.autoresizingMask = NSViewWidthSizable | NSViewHeightSizable;
    [inspectorContent addSubview:right];
    self.taskPane = right;
    self.taskTitle = [self label:@"还没有任务" frame:NSMakeRect(14, 608, 280, 47) size:16 color:[NSColor labelColor]];
    self.taskTitle.lineBreakMode = NSLineBreakByTruncatingTail;
    self.taskTitle.autoresizingMask = NSViewMinYMargin;
    [right addSubview:self.taskTitle];
    self.taskState = [self label:@"把需要持续关注的事设为目标" frame:NSMakeRect(14, 581, 280, 22) size:12 color:[NSColor secondaryLabelColor]];
    self.taskState.autoresizingMask = NSViewMinYMargin;
    [right addSubview:self.taskState];
    self.goalPicker = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(12, 540, 282, 28) pullsDown:NO];
    self.goalPicker.autoresizingMask = NSViewMinYMargin;
    [self.goalPicker addItemWithTitle:@"选择长期目标…"];
    self.goalPicker.target = self;
    self.goalPicker.action = @selector(goalSelected:);
    [right addSubview:self.goalPicker];
    NSScrollView *planScroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(14, 239, 280, 329)];
    planScroll.hasVerticalScroller = YES;
    planScroll.autoresizingMask = NSViewHeightSizable;
    planScroll.drawsBackground = YES;
    planScroll.backgroundColor = [NSColor textBackgroundColor];
    planScroll.wantsLayer = YES;
    planScroll.layer.cornerRadius = 10;
    self.stepsView = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 280, 329)];
    self.stepsView.editable = NO;
    self.stepsView.verticallyResizable = YES;
    self.stepsView.textContainer.widthTracksTextView = YES;
    self.stepsView.font = [NSFont systemFontOfSize:13];
    self.stepsView.textContainerInset = NSMakeSize(8, 10);
    self.stepsView.drawsBackground = NO;
    self.stepsView.textColor = [NSColor labelColor];
    self.stepsView.string = @"当前没有进行中的目标。\n\n想让 Muse 持续跟进一件事？\n在左侧输入目标，点“设为长期目标”。\n\n来源、步骤和权限会先列成草案；你批准后才开始执行。";
    self.stepsView.accessibilityTitle = @"当前任务卡";
    planScroll.documentView = self.stepsView;
    [right addSubview:planScroll];
    self.approveButton = [self button:@"确认执行" frame:NSMakeRect(14, 195, 130, 31) action:@selector(confirmTask:) parent:right];
    self.approveButton.tag = 1;
    self.approveButton.enabled = NO;
    self.approveButton.hidden = YES;
    self.rejectButton = [self button:@"拒绝" frame:NSMakeRect(152, 195, 130, 31) action:@selector(confirmTask:) parent:right];
    self.rejectButton.tag = 0;
    self.rejectButton.enabled = NO;
    self.rejectButton.hidden = YES;
    self.goalApproveButton = [self button:@"批准计划" frame:NSMakeRect(14, 195, 130, 31) action:@selector(approveGoal:) parent:right];
    self.goalApproveButton.bezelColor = [NSColor controlAccentColor];
    self.goalRejectButton = [self button:@"拒绝计划" frame:NSMakeRect(152, 195, 130, 31) action:@selector(rejectGoal:) parent:right];
    self.goalPauseButton = [self button:@"暂停目标" frame:NSMakeRect(14, 195, 130, 31) action:@selector(pauseGoal:) parent:right];
    self.goalResumeButton = [self button:@"继续目标" frame:NSMakeRect(14, 195, 130, 31) action:@selector(resumeGoal:) parent:right];
    self.goalCancelButton = [self button:@"取消目标" frame:NSMakeRect(152, 195, 130, 31) action:@selector(cancelGoal:) parent:right];
    self.goalReviseButton = [self button:@"修改目标" frame:NSMakeRect(14, 157, 130, 31) action:@selector(reviseGoal:) parent:right];
    self.goalRetryButton = [self button:@"安全重试" frame:NSMakeRect(152, 195, 130, 31) action:@selector(retryGoal:) parent:right];
    [self button:@"查看计划" frame:NSMakeRect(152, 157, 130, 31) action:@selector(showTechnicalDetails:) parent:right];
    [self button:@"打开工作区" frame:NSMakeRect(14, 119, 130, 31) action:@selector(openWorkspace:) parent:right];
    [self button:@"刷新目标" frame:NSMakeRect(152, 119, 130, 31) action:@selector(requestGoalList:) parent:right];
    [self updateGoalButtons:@""];

    self.modelStatus = [self label:@"模型检查中…" frame:NSMakeRect(16, 54, 135, 18) size:11 color:[NSColor secondaryLabelColor]];
    [right addSubview:self.modelStatus];
    self.routeStatus = [self label:@"路由读取中…" frame:NSMakeRect(155, 54, 135, 18) size:11 color:[NSColor secondaryLabelColor]];
    [right addSubview:self.routeStatus];
    self.workerStatus = [self label:@"服务连接中…" frame:NSMakeRect(16, 29, 135, 18) size:11 color:[NSColor secondaryLabelColor]];
    [right addSubview:self.workerStatus];
    self.watchStatus = [self label:@"监控：关闭" frame:NSMakeRect(155, 29, 135, 18) size:11 color:[NSColor secondaryLabelColor]];
    [right addSubview:self.watchStatus];
    self.permissionStatus = [self label:@"权限待检查" frame:NSMakeRect(16, 6, 135, 18) size:11 color:[NSColor secondaryLabelColor]];
    [right addSubview:self.permissionStatus];
    self.notificationStatus = [self label:@"通知待检查" frame:NSMakeRect(155, 6, 135, 18) size:11 color:[NSColor secondaryLabelColor]];
    [right addSubview:self.notificationStatus];

    // The mail card appears only for a real queued mail decision, never as a sample message.
    self.mailPanel = [self card:@"邮件 · 由你决定" frame:NSMakeRect(10, 276, 290, 236) parent:right];
    self.mailPrompt = [self label:@"" frame:NSMakeRect(10, 184, 266, 38) size:11 color:[NSColor labelColor]];
    self.mailPrompt.lineBreakMode = NSLineBreakByWordWrapping;
    [self.mailPanel.contentView addSubview:self.mailPrompt];
    self.mailEditor = [[NSTextView alloc] initWithFrame:NSMakeRect(10, 74, 266, 101)];
    self.mailEditor.font = [NSFont systemFontOfSize:12];
    self.mailEditor.accessibilityTitle = @"邮件回复草稿或我的决定";
    [self.mailPanel.contentView addSubview:self.mailEditor];
    self.mailPrimaryButton = [self button:@"让 Muse 起草" frame:NSMakeRect(10, 39, 266, 29) action:@selector(mailPrimaryAction:) parent:self.mailPanel.contentView];
    self.mailSecondaryButton = [self button:@"我来写" frame:NSMakeRect(10, 5, 127, 29) action:@selector(mailWriteAction:) parent:self.mailPanel.contentView];
    self.mailLaterButton = [self button:@"暂不回复" frame:NSMakeRect(149, 5, 127, 29) action:@selector(mailLaterAction:) parent:self.mailPanel.contentView];
    self.mailPanel.hidden = YES;

    self.officialPanel = [self card:@"官方单步确认" frame:NSMakeRect(6, 101, 280, 604) parent:right];
    self.officialPanel.autoresizingMask = NSViewHeightSizable;
    NSView *officialContent = self.officialPanel.contentView;
    NSTextField *officialTitle = [self label:@"请审阅这一项操作" frame:NSMakeRect(8, 552, 248, 27)
                                        size:16 color:[NSColor labelColor]];
    officialTitle.autoresizingMask = NSViewMinYMargin;
    [officialContent addSubview:officialTitle];
    self.officialState = [self label:@"等待读取官方请求…" frame:NSMakeRect(8, 525, 248, 22)
                                   size:12 color:[NSColor systemOrangeColor]];
    self.officialState.autoresizingMask = NSViewMinYMargin;
    [officialContent addSubview:self.officialState];
    NSScrollView *officialScroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(8, 95, 248, 421)];
    officialScroll.hasVerticalScroller = YES;
    officialScroll.autoresizingMask = NSViewHeightSizable;
    self.officialPlanView = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 248, 421)];
    self.officialPlanView.editable = NO;
    self.officialPlanView.verticallyResizable = YES;
    self.officialPlanView.textContainer.widthTracksTextView = YES;
    self.officialPlanView.font = [NSFont systemFontOfSize:12];
    self.officialPlanView.textContainerInset = NSMakeSize(8, 9);
    self.officialPlanView.accessibilityTitle = @"官方单步计划与授权范围";
    officialScroll.documentView = self.officialPlanView;
    [officialContent addSubview:officialScroll];
    self.officialApproveButton = [self button:@"确认执行" frame:NSMakeRect(8, 49, 116, 34)
                                         action:@selector(decideOfficialPending:) parent:officialContent];
    self.officialApproveButton.tag = 1;
    self.officialApproveButton.accessibilityTitle = @"确认官方单步执行";
    self.officialApproveButton.bezelColor = [NSColor controlAccentColor];
    self.officialDenyButton = [self button:@"拒绝" frame:NSMakeRect(140, 49, 116, 34)
                                      action:@selector(decideOfficialPending:) parent:officialContent];
    self.officialDenyButton.tag = 0;
    self.officialDenyButton.accessibilityTitle = @"拒绝官方单步执行";
    [officialContent addSubview:[self label:@"仅当前请求；到期自动失效" frame:NSMakeRect(8, 18, 248, 17)
                                    size:11 color:[NSColor secondaryLabelColor]]];
    self.officialPanel.hidden = YES;

    self.skillPane = [self card:@"" frame:inspectorContent.bounds parent:inspectorContent];
    self.skillPane.autoresizingMask = NSViewWidthSizable | NSViewHeightSizable;
    self.skillPane.contentViewMargins = NSMakeSize(0, 0);
    self.skillPane.borderWidth = 0;
    NSView *slots = self.skillPane.contentView;
    NSTextField *skillsTitle = [self label:@"内置技能" frame:NSMakeRect(16, 610, 260, 28) size:19 color:[NSColor labelColor]];
    skillsTitle.autoresizingMask = NSViewMinYMargin;
    [slots addSubview:skillsTitle];
    NSTextField *skillsHint = [self label:@"每项技能对应一个可调用的软件或能力。" frame:NSMakeRect(16, 583, 270, 36)
                                    size:11 color:[NSColor secondaryLabelColor]];
    skillsHint.autoresizingMask = NSViewMinYMargin;
    [slots addSubview:skillsHint];
    self.mailModuleButton = [self button:@"QQ 邮箱 · 未连接" frame:NSMakeRect(16, 517, 260, 43)
                                  action:@selector(showMailBridgeConnection:) parent:slots];
    NSButton *calendarSkill = [self button:@"日历 · 授权与自检" frame:NSMakeRect(16, 443, 260, 43)
                                     action:@selector(showCalendarModule:) parent:slots];
    NSButton *wechatSkill = [self button:@"微信 · 尚未接通" frame:NSMakeRect(16, 369, 260, 43)
                                   action:@selector(showUnavailableSkill:) parent:slots];
    NSButton *computerSkill = [self button:@"电脑能力 · 查看授权" frame:NSMakeRect(16, 295, 260, 43)
                                     action:@selector(showCapabilities:) parent:slots];
    NSButton *pluginSkill = [self button:@"技能包 · 管理插件" frame:NSMakeRect(16, 221, 260, 43)
                                   action:@selector(showCapabilities:) parent:slots];
    for (NSButton *skill in @[self.mailModuleButton, calendarSkill, wechatSkill, computerSkill, pluginSkill]) {
        skill.alignment = NSTextAlignmentLeft;
        skill.autoresizingMask = NSViewMinYMargin | NSViewWidthSizable;
    }
    [slots addSubview:[self label:@"技能包可由插件 SDK 扩展；启用前逐项授权。"
                            frame:NSMakeRect(16, 12, 260, 28) size:11 color:[NSColor secondaryLabelColor]]];
    [self showSkillSlots:nil];

    BOOL developerUI = [[[[NSProcessInfo processInfo] environment] objectForKey:@"GOSIM_DEV_UI"] boolValue];
    self.messageView = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 1, 1)];
    self.messageView.string = @"请把这条测试记录保存到本地";
    self.highTierToggle = [NSButton checkboxWithTitle:@"请求高阶摘要" target:nil action:nil];
    if (developerUI) {
        [self button:@"注入合成事件" frame:NSMakeRect(264, 16, 130, 34) action:@selector(showSyntheticInput:) parent:middle];
    }
    self.technicalWindow = [[NSWindow alloc] initWithContentRect:NSMakeRect(0, 0, 760, 730)
        styleMask:(NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable)
        backing:NSBackingStoreBuffered defer:NO];
    self.technicalWindow.title = @"Muse · 技术详情";
    self.technicalWindow.releasedWhenClosed = NO;
    self.technicalWindow.minSize = NSMakeSize(600, 600);
    [self.technicalWindow center];
    NSView *technicalContent = self.technicalWindow.contentView;
    NSBox *evidence = [self card:@"执行证据" frame:NSMakeRect(20, 220, 720, 240) parent:technicalContent];
    NSScrollView *logScroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(10, 10, 690, 200)];
    logScroll.hasVerticalScroller = YES;
    self.logView = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 690, 200)];
    self.logView.editable = NO;
    self.logView.verticallyResizable = YES;
    self.logView.textContainer.widthTracksTextView = YES;
    self.logView.font = [NSFont monospacedSystemFontOfSize:11 weight:NSFontWeightRegular];
    logScroll.documentView = self.logView;
    [evidence.contentView addSubview:logScroll];
    NSBox *terminal = [self card:@"受限终端" frame:NSMakeRect(20, 20, 720, 180) parent:technicalContent];
    self.commandPopup = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(12, 110, 82, 28) pullsDown:NO];
    [self.commandPopup addItemsWithTitles:@[@"mkdir", @"touch"]];
    [terminal.contentView addSubview:self.commandPopup];
    self.pathField = [[NSTextField alloc] initWithFrame:NSMakeRect(102, 110, 596, 28)];
    self.pathField.stringValue = @"test-folder";
    [terminal.contentView addSubview:self.pathField];
    self.terminalButton = [self button:@"提出请求" frame:NSMakeRect(12, 64, 686, 32) action:@selector(terminalRequest:) parent:terminal.contentView];
    [terminal.contentView addSubview:[self label:@"仅 mkdir / touch；固定工作区；shell=False；10 秒超时。" frame:NSMakeRect(12, 16, 686, 36) size:11 color:[NSColor colorWithCalibratedWhite:0.35 alpha:1]]];
    NSBox *planDetails = [self card:@"完整计划与授权范围" frame:NSMakeRect(20, 480, 720, 230) parent:technicalContent];
    NSScrollView *detailsScroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(10, 10, 690, 190)];
    detailsScroll.hasVerticalScroller = YES;
    self.technicalPlanView = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 690, 190)];
    self.technicalPlanView.editable = NO;
    self.technicalPlanView.verticallyResizable = YES;
    self.technicalPlanView.textContainer.widthTracksTextView = YES;
    self.technicalPlanView.font = [NSFont monospacedSystemFontOfSize:11 weight:NSFontWeightRegular];
    detailsScroll.documentView = self.technicalPlanView;
    [planDetails.contentView addSubview:detailsScroll];
    if (![[[[NSProcessInfo processInfo] environment] objectForKey:@"GOSIM_BACKGROUND_TEST"] boolValue]) {
        BOOL reduceMotion = [NSWorkspace sharedWorkspace].accessibilityDisplayShouldReduceMotion;
        if (!reduceMotion) self.window.alphaValue = 0.96;
        [self.window makeKeyAndOrderFront:nil];
        [NSApp activateIgnoringOtherApps:YES];
        if (!reduceMotion) {
            [NSAnimationContext runAnimationGroup:^(NSAnimationContext *context) {
                context.duration = 0.18;
                self.window.animator.alphaValue = 1.0;
            } completionHandler:nil];
        }
    }
}

- (NSButton *)button:(NSString *)title frame:(NSRect)frame action:(SEL)action parent:(NSView *)parent {
    NSButton *button = [NSButton buttonWithTitle:title target:self action:action];
    button.frame = frame;
    button.bezelStyle = NSBezelStyleRounded;
    button.accessibilityElement = YES;
    button.accessibilityRole = NSAccessibilityButtonRole;
    button.accessibilityTitle = title;
    [parent addSubview:button];
    return button;
}

- (void)startWorker {
    NSString *resource = [[NSBundle mainBundle] resourcePath];
    NSString *python = [resource stringByAppendingPathComponent:@"python/bin/python3"];
    if (![[NSFileManager defaultManager] isExecutableFileAtPath:python]) {
        self.workerStatus.stringValue = @"运行时缺失";
        self.workerStatus.textColor = [NSColor systemRedColor];
        [self appendLog:@"应用包缺少 Python 运行时；请重新安装完整安装包。"];
        return;
    }
    self.worker = [[NSTask alloc] init];
    self.worker.launchPath = python;
    self.worker.arguments = @[@"-B", [resource stringByAppendingPathComponent:@"desktop_worker.py"], self.workspace];
    NSMutableDictionary *env = [[[NSProcessInfo processInfo] environment] mutableCopy];
    env[@"PYTHONPATH"] = resource;
    env[@"PYTHONNOUSERSITE"] = @"1";
    env[@"PYTHONDONTWRITEBYTECODE"] = @"1";
    env[@"LOCAL_MODEL_URL"] = @"http://127.0.0.1:8080/v1/chat/completions";
    env[@"AGENT_WORKSPACE"] = self.workspace;
    self.officialWitnessSecret = [NSString stringWithFormat:@"%@%@", [[NSUUID UUID] UUIDString], [[NSUUID UUID] UUIDString]];
    env[@"MUSE_NATIVE_WITNESS_SECRET"] = self.officialWitnessSecret;
    self.worker.environment = env;
    NSPipe *input = [NSPipe pipe];
    NSPipe *output = [NSPipe pipe];
    self.worker.standardInput = input;
    self.worker.standardOutput = output;
    self.worker.standardError = [NSPipe pipe];
    self.workerInput = input.fileHandleForWriting;
    __weak typeof(self) weakSelf = self;
    output.fileHandleForReading.readabilityHandler = ^(NSFileHandle *handle) {
        NSData *data = [handle availableData];
        if (data.length == 0) return;
        NSString *chunk = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
        dispatch_async(dispatch_get_main_queue(), ^{ [weakSelf handleWorkerChunk:chunk]; });
    };
    @try {
        [self.worker launch];
        self.officialPollTimer = [NSTimer scheduledTimerWithTimeInterval:2.0 target:self
                                        selector:@selector(pollOfficialPending:) userInfo:nil repeats:YES];
        [self pollOfficialPending:nil];
    }
    @catch (NSException *exception) {
        [self appendLog:[NSString stringWithFormat:@"worker 启动失败：%@", exception.reason]];
        self.workerStatus.stringValue = @"worker 失败";
        self.workerStatus.textColor = [NSColor systemRedColor];
    }
}

- (void)handleWorkerChunk:(NSString *)chunk {
    self.lineBuffer = [self.lineBuffer stringByAppendingString:chunk ?: @""];
    NSArray<NSString *> *parts = [self.lineBuffer componentsSeparatedByString:@"\n"];
    self.lineBuffer = parts.lastObject ?: @"";
    for (NSUInteger i = 0; i + 1 < parts.count; i++) {
        NSString *line = parts[i];
        if (line.length == 0) continue;
        NSData *data = [line dataUsingEncoding:NSUTF8StringEncoding];
        NSDictionary *result = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
        if ([result isKindOfClass:[NSDictionary class]]) [self showResult:result];
    }
}

- (void)requestSystemStatus {
    [self sendEvent:@{@"type": @"system_status"}];
}

- (void)sendEvent:(NSDictionary *)event {
    NSString *eventType = event[@"type"];
    NSSet *allowedWhilePaused = [NSSet setWithArray:@[@"message_control", @"mail_choice", @"mail_guidance", @"mail_reply_content",
                                                     @"mail_contacts_list", @"mail_reply_start",
                                                     @"goal_control", @"goal_get", @"goal_list", @"goal_revise", @"model_settings_get",
                                                     @"model_settings_set", @"model_secret_set", @"model_pricing_set", @"model_pricing_get",
                                                     @"model_capabilities_get",
                                                     @"memory_settings_get", @"memory_settings_set",
                                                     @"memory_list", @"memory_pin", @"memory_correct", @"memory_delete", @"memory_scope_list",
                                                     @"proactivity_settings_get", @"proactivity_settings_set",
                                                     @"brief_settings_get", @"brief_settings_set", @"brief_ack",
                                                     @"memory_claim_list", @"memory_claim_get", @"memory_claim_revision",
                                                     @"memory_claim_correct", @"memory_claim_pin", @"memory_claim_delete",
                                                     @"activity_status", @"activity_set", @"activity_poll",
                                                     @"official_pending_list", @"official_native_decide",
                                                     @"watch_folder_set", @"watch_folder_list", @"watch_folder_revoke",
                                                     @"system_status", @"health"]];
    if (self.paused && ![allowedWhilePaused containsObject:eventType]) { [self appendLog:@"监听已暂停；没有新增任务。"] ; return; }
    NSData *data = [NSJSONSerialization dataWithJSONObject:event options:0 error:nil];
    if (!data) return;
    NSMutableData *line = [data mutableCopy];
    [line appendData:[@"\n" dataUsingEncoding:NSUTF8StringEncoding]];
    @try { [self.workerInput writeData:line]; }
    @catch (NSException *exception) { [self appendLog:@"worker 写入失败，任务未发送。"]; }
}

- (void)pollOfficialPending:(id)sender {
    if (self.worker.isRunning && !self.officialDecisionInFlight) {
        [self sendEvent:@{@"type": @"official_pending_list"}];
    }
}

- (NSDate *)officialExpiry:(NSDictionary *)pending {
    NSString *value = [pending[@"expires_at"] isKindOfClass:[NSString class]] ? pending[@"expires_at"] : nil;
    if (!value) return nil;
    NSISO8601DateFormatter *formatter = [[NSISO8601DateFormatter alloc] init];
    formatter.formatOptions = NSISO8601DateFormatWithInternetDateTime | NSISO8601DateFormatWithFractionalSeconds;
    NSDate *date = [formatter dateFromString:value];
    if (!date) {
        formatter.formatOptions = NSISO8601DateFormatWithInternetDateTime;
        date = [formatter dateFromString:value];
    }
    return date;
}

- (void)refreshOfficialCountdown {
    if (!self.officialPending) return;
    NSDate *expiry = [self officialExpiry:self.officialPending];
    NSInteger remaining = expiry ? (NSInteger)ceil([expiry timeIntervalSinceNow]) : 0;
    BOOL ready = self.officialApprovalAvailable && remaining > 0 && !self.officialDecisionInFlight;
    self.officialApproveButton.enabled = ready;
    self.officialDenyButton.enabled = ready;
    self.officialState.stringValue = !expiry ? @"到期时间无法核对 · 操作已禁用" :
        remaining <= 0 ? @"请求已到期 · 操作已禁用" :
        !self.officialApprovalAvailable ? @"本机确认不可用 · 仅可查看" :
        [NSString stringWithFormat:@"等待你的决定 · 还剩 %ld 秒", (long)remaining];
    self.officialState.textColor = ready ? [NSColor systemOrangeColor] : [NSColor systemRedColor];
}

- (void)showOfficialPendingList:(NSDictionary *)result {
    NSArray *items = [result[@"pending"] isKindOfClass:[NSArray class]] ? result[@"pending"] : @[];
    NSDictionary *pending = items.count > 0 && [items[0] isKindOfClass:[NSDictionary class]] ? items[0] : nil;
    if (!pending) {
        self.officialPending = nil;
        self.officialPanel.hidden = YES;
        return;
    }
    NSDictionary *plan = [pending[@"plan"] isKindOfClass:[NSDictionary class]] ? pending[@"plan"] : nil;
    NSString *digest = [pending[@"plan_digest"] isKindOfClass:[NSString class]] ? pending[@"plan_digest"] : nil;
    NSString *pendingID = [pending[@"pending_id"] isKindOfClass:[NSString class]] ? pending[@"pending_id"] : nil;
    NSNumber *revision = [pending[@"revision"] isKindOfClass:[NSNumber class]] ? pending[@"revision"] : nil;
    if (!plan || digest.length != 64 || pendingID.length == 0 || !revision ||
        ![pending[@"status"] isEqualToString:@"WAITING_HUMAN"]) {
        self.officialPending = nil;
        self.officialPanel.hidden = YES;
        [self appendLog:@"官方待确认记录不完整；未提供执行按钮。"];
        return;
    }
    BOOL changed = ![self.officialPending[@"pending_id"] isEqualToString:pendingID] ||
                   ![self.officialPending[@"plan_digest"] isEqualToString:digest] ||
                   ![self.officialPending[@"revision"] isEqual:revision];
    self.officialPending = pending;
    self.officialApprovalAvailable = [result[@"approval_available"] boolValue];
    if (changed) {
        NSArray *steps = [plan[@"steps"] isKindOfClass:[NSArray class]] ? plan[@"steps"] : @[];
        NSDictionary *step = nil;
        for (id item in steps) {
            if ([item isKindOfClass:[NSDictionary class]] && [item[@"id"] isEqual:pending[@"step_id"]]) {
                step = item;
                break;
            }
        }
        NSData *planData = [NSJSONSerialization dataWithJSONObject:plan options:NSJSONWritingPrettyPrinted | NSJSONWritingSortedKeys error:nil];
        NSString *planJSON = planData ? [[NSString alloc] initWithData:planData encoding:NSUTF8StringEncoding] : @"无法显示完整计划";
        NSString *objective = [plan[@"objective"] isKindOfClass:[NSString class]] ? plan[@"objective"] : @"未命名目标";
        NSString *capability = [step[@"capability"] isKindOfClass:[NSString class]] ? step[@"capability"] : @"步骤不匹配";
        NSString *session = [pending[@"official_session_id"] isKindOfClass:[NSString class]] ? pending[@"official_session_id"] : @"?";
        NSString *turn = [pending[@"official_turn_id"] isKindOfClass:[NSString class]] ? pending[@"official_turn_id"] : @"?";
        NSString *toolCall = [pending[@"official_tool_call_id"] isKindOfClass:[NSString class]] ? pending[@"official_tool_call_id"] : @"?";
        NSString *callNonce = [pending[@"official_call_nonce"] isKindOfClass:[NSString class]] ? pending[@"official_call_nonce"] : @"?";
        self.officialPlanView.string = [NSString stringWithFormat:
            @"目标：%@\n\n本次步骤：%@ · %@\n计划修订：%@\n计划摘要：%@\n\n官方会话：%@\n官方回合：%@\n工具调用：%@\n调用标识：%@\n请求 ID：%@\n到期：%@\n\n完整计划（Goal Store 回读）：\n%@",
            objective, pending[@"step_id"] ?: @"?", capability, revision, digest,
            session, turn, toolCall, callNonce, pendingID, pending[@"expires_at"] ?: @"?", planJSON];
        [self.officialPlanView scrollRangeToVisible:NSMakeRange(0, 0)];
    }
    self.officialPanel.hidden = NO;
    if (changed) [self showTaskPane:nil];
    [self refreshOfficialCountdown];
}

- (NSString *)officialMACForPending:(NSDictionary *)pending decision:(NSString *)decision nonce:(NSString *)nonce {
    NSData *key = [self.officialWitnessSecret dataUsingEncoding:NSUTF8StringEncoding];
    if (key.length < 64) return nil;
    for (NSString *name in @[@"pending_id", @"plan_digest", @"official_session_id",
                             @"official_turn_id", @"official_tool_call_id", @"official_call_nonce"]) {
        if (![pending[name] isKindOfClass:[NSString class]] || [pending[name] length] == 0) return nil;
    }
    if (![pending[@"revision"] isKindOfClass:[NSNumber class]]) return nil;
    NSArray<NSString *> *fields = @[pending[@"pending_id"], [pending[@"revision"] description],
        pending[@"plan_digest"], pending[@"official_session_id"], pending[@"official_turn_id"],
        pending[@"official_tool_call_id"], pending[@"official_call_nonce"], decision, nonce];
    NSMutableData *message = [NSMutableData data];
    for (NSString *field in fields) {
        if (![field isKindOfClass:[NSString class]] || field.length == 0) return nil;
        NSData *value = [field dataUsingEncoding:NSUTF8StringEncoding];
        if (message.length > 0) [message appendBytes:"|" length:1];
        NSString *length = [NSString stringWithFormat:@"%lu:", (unsigned long)value.length];
        [message appendData:[length dataUsingEncoding:NSASCIIStringEncoding]];
        [message appendData:value];
    }
    unsigned char digest[CC_SHA256_DIGEST_LENGTH];
    CCHmac(kCCHmacAlgSHA256, key.bytes, key.length, message.bytes, message.length, digest);
    NSMutableString *hex = [NSMutableString stringWithCapacity:CC_SHA256_DIGEST_LENGTH * 2];
    for (NSUInteger i = 0; i < CC_SHA256_DIGEST_LENGTH; i++) [hex appendFormat:@"%02x", digest[i]];
    return hex;
}

- (void)decideOfficialPending:(NSButton *)sender {
    NSDictionary *pending = self.officialPending;
    if (!pending || !self.officialApprovalAvailable || self.officialDecisionInFlight ||
        [[self officialExpiry:pending] timeIntervalSinceNow] <= 0) return;
    NSString *decision = sender.tag == 1 ? @"approve" : @"deny";
    NSString *nonce = [[[NSUUID UUID] UUIDString] lowercaseString];
    NSString *mac = [self officialMACForPending:pending decision:decision nonce:nonce];
    if (!mac) {
        self.officialState.stringValue = @"确认信息不完整 · 未发送";
        self.officialState.textColor = [NSColor systemRedColor];
        return;
    }
    self.officialDecisionInFlight = YES;
    self.officialApproveButton.enabled = NO;
    self.officialDenyButton.enabled = NO;
    self.officialState.stringValue = @"正在提交这一项决定…";
    [self sendEvent:@{@"type": @"official_native_decide", @"pending_id": pending[@"pending_id"],
                      @"decision": decision, @"reviewed_digest": pending[@"plan_digest"],
                      @"native_witness": @{@"nonce": nonce, @"decision": decision, @"mac": mac}}];
}

- (void)runSelfTestInput {
    NSString *text = @"请把这条测试记录保存到本地 [GOSIM_TEST:desktop-app:self-test]";
    [self appendLog:@"self-test：发送合成保存任务。"];
    [self sendEvent:@{@"type": @"user_input", @"text": text}];
}

- (void)showConversation:(id)sender {
    [self.window makeKeyAndOrderFront:nil];
    [self.window makeFirstResponder:self.chatInput];
}

- (void)useWelcomePrompt:(NSButton *)sender {
    NSArray<NSString *> *examples = @[@"帮我梳理 Python 3.13 的主要变化和来源。",
                                     @"持续关注一个公开网页，有重要变化时告诉我。",
                                     @"整理我选择的文件夹中新加入的资料，并列出来源。"];
    if (sender.tag < 0 || sender.tag >= (NSInteger)examples.count) return;
    self.chatInput.stringValue = examples[(NSUInteger)sender.tag];
    [self.window makeFirstResponder:self.chatInput];
}

- (void)showGoals:(id)sender {
    [self requestGoalList:nil];
    [self showTaskPane:nil];
    [self.window makeKeyAndOrderFront:nil];
    [self.window makeFirstResponder:self.goalPicker];
}

- (void)showMemories:(id)sender {
    [self sendEvent:@{@"type": @"memory_claim_list"}];
}

- (void)showActivity:(id)sender {
    if (!self.activityWindow) {
        self.activityWindow = [[NSWindow alloc] initWithContentRect:NSMakeRect(0, 0, 620, 440)
            styleMask:(NSWindowStyleMaskTitled | NSWindowStyleMaskClosable)
            backing:NSBackingStoreBuffered defer:NO];
        self.activityWindow.title = @"Muse · 活动";
        self.activityWindow.delegate = self;
        [self.activityWindow center];
        NSView *root = self.activityWindow.contentView;
        [root addSubview:[self label:@"活动观察" frame:NSMakeRect(22, 390, 200, 28) size:19 color:[NSColor labelColor]]];
        NSTextField *scope = [self label:@"仅记录你选择的应用成为前台的时间与应用名；默认关闭。不读取屏幕、剪贴板或通知。"
                                    frame:NSMakeRect(22, 354, 570, 32) size:12 color:[NSColor secondaryLabelColor]];
        scope.lineBreakMode = NSLineBreakByWordWrapping;
        [root addSubview:scope];
        self.activityTextEdit = [NSButton checkboxWithTitle:@"TextEdit" target:nil action:nil];
        self.activityTextEdit.frame = NSMakeRect(22, 316, 145, 25);
        [root addSubview:self.activityTextEdit];
        self.activityEdge = [NSButton checkboxWithTitle:@"Microsoft Edge" target:nil action:nil];
        self.activityEdge.frame = NSMakeRect(180, 316, 175, 25);
        [root addSubview:self.activityEdge];
        self.activityToggle = [self button:@"开启观察" frame:NSMakeRect(375, 310, 105, 31)
                                      action:@selector(toggleActivity:) parent:root];
        self.activityToggle.enabled = NO;
        [self button:@"刷新" frame:NSMakeRect(490, 310, 100, 31) action:@selector(refreshActivity:) parent:root];
        self.activityState = [self label:@"正在读取状态…" frame:NSMakeRect(22, 280, 568, 24)
                                      size:12 color:[NSColor secondaryLabelColor]];
        [root addSubview:self.activityState];
        NSScrollView *scroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(22, 22, 568, 250)];
        scroll.autoresizingMask = NSViewWidthSizable | NSViewHeightSizable;
        scroll.hasVerticalScroller = YES;
        self.activityEventsView = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 568, 250)];
        self.activityEventsView.editable = NO;
        self.activityEventsView.verticallyResizable = YES;
        self.activityEventsView.textContainer.widthTracksTextView = YES;
        self.activityEventsView.font = [NSFont systemFontOfSize:12];
        self.activityEventsView.string = @"开启后，这里会出现白名单应用的真实前台切换。";
        scroll.documentView = self.activityEventsView;
        [root addSubview:scroll];
    }
    [self.activityWindow makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];
    self.activityToggle.enabled = NO;
    [self sendEvent:@{@"type": @"activity_status"}];
}

- (void)toggleActivity:(id)sender {
    BOOL enable = !self.activityEnabled;
    NSMutableArray<NSString *> *bundles = [NSMutableArray array];
    if (enable && self.activityTextEdit.state == NSControlStateValueOn) [bundles addObject:@"com.apple.TextEdit"];
    if (enable && self.activityEdge.state == NSControlStateValueOn) [bundles addObject:@"com.microsoft.edgemac"];
    if (enable && bundles.count == 0) {
        self.activityState.stringValue = @"请先选择至少一个允许观察的应用。";
        return;
    }
    self.activityToggle.enabled = NO;
    [self sendEvent:@{@"type": @"activity_set", @"enabled": @(enable), @"bundle_ids": bundles}];
}

- (void)refreshActivity:(id)sender {
    [self sendEvent:@{@"type": @"activity_status"}];
    if (self.activityEnabled) [self sendEvent:@{@"type": @"activity_poll"}];
}

- (void)showCapabilities:(id)sender {
    [self requestPluginSettings:nil];
}

- (void)showSetup:(id)sender {
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"Muse 设置";
    alert.informativeText = @"管理首启模式、模型、预算和密钥。系统权限由你在 macOS 中决定；Muse 不会代点系统同意。";
    [alert addButtonWithTitle:@"首启与模型"];
    [alert addButtonWithTitle:@"模型与预算"];
    [alert addButtonWithTitle:@"高阶密钥与价格"];
    [alert addButtonWithTitle:@"系统权限"];
    [alert addButtonWithTitle:@"关闭"];
    NSModalResponse choice = [alert runModal];
    if (choice == NSAlertFirstButtonReturn) [self showFirstRun:nil];
    if (choice == NSAlertSecondButtonReturn) [self showModelSettings:nil];
    if (choice == NSAlertThirdButtonReturn) [self showHighProviderSecurity:nil];
    if (choice == NSAlertThirdButtonReturn + 1) [self showPermissionsGuide:nil];
}

- (void)showPermissionsGuide:(id)sender {
    BOOL accessibility = AXIsProcessTrusted();
    NSString *helper = [[[NSBundle mainBundle] resourcePath] stringByAppendingPathComponent:@"muse_ax_helper"];
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
        NSString *helperStatus = @"安装包缺失";
        if ([[NSFileManager defaultManager] isExecutableFileAtPath:helper]) {
            helperStatus = @"无法确认";
            NSTask *probe = [[NSTask alloc] init];
            probe.launchPath = helper;
            probe.arguments = @[@"status"];
            NSPipe *output = [NSPipe pipe];
            probe.standardOutput = output;
            probe.standardError = [NSFileHandle fileHandleWithNullDevice];
            @try {
                [probe launch];
                NSDate *deadline = [NSDate dateWithTimeIntervalSinceNow:2.0];
                while (probe.isRunning && [deadline timeIntervalSinceNow] > 0) [NSThread sleepForTimeInterval:0.05];
                if (probe.isRunning) [probe terminate];
                else {
                    NSData *data = [[output fileHandleForReading] readDataToEndOfFile];
                    NSDictionary *status = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
                    if ([status[@"status"] isEqualToString:@"TRUSTED"] && [status[@"trusted"] boolValue]) helperStatus = @"已允许";
                    if ([status[@"status"] isEqualToString:@"BLOCKED_PERMISSION"]) helperStatus = @"未开启或已撤销";
                }
            } @catch (NSException *exception) { helperStatus = @"无法确认"; }
        }
        NSString *resolvedHelperStatus = helperStatus;
        [[UNUserNotificationCenter currentNotificationCenter] getNotificationSettingsWithCompletionHandler:^(UNNotificationSettings *settings) {
            dispatch_async(dispatch_get_main_queue(), ^{
                NSString *notification = settings.authorizationStatus == UNAuthorizationStatusAuthorized ? @"已允许" :
                    settings.authorizationStatus == UNAuthorizationStatusDenied ? @"已拒绝" : @"未开启";
                NSAlert *alert = [[NSAlert alloc] init];
                alert.messageText = @"Muse 系统权限自检";
                alert.informativeText = [NSString stringWithFormat:
                    @"辅助功能（当前应用）：%@\n跨应用助手：%@\n通知：%@\n\n使用 TextEdit 等应用时，macOS 可能单独要求批准辅助功能和自动化。文件夹、邮箱和高阶模型都要在 Muse 内另行明确选择。拒绝或撤销权限后，相应操作会停在等待状态。",
                    accessibility ? @"已允许" : @"未开启或已撤销", resolvedHelperStatus, notification];
                [alert addButtonWithTitle:@"打开系统设置"];
                [alert addButtonWithTitle:@"稍后"];
                if ([alert runModal] == NSAlertFirstButtonReturn) {
                    NSURL *url = [NSURL fileURLWithPath:@"/System/Applications/System Settings.app"];
                    [[NSWorkspace sharedWorkspace] openURL:url];
                }
            });
        }];
    });
}

- (NSString *)setupPath { return [[self.workspace stringByDeletingLastPathComponent] stringByAppendingPathComponent:@"setup.json"]; }

- (NSString *)setupMode {
    NSData *data = [NSData dataWithContentsOfFile:[self setupPath]];
    NSDictionary *saved = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
    NSString *mode = [saved isKindOfClass:[NSDictionary class]] ? saved[@"mode"] : nil;
    return [mode isKindOfClass:[NSString class]] ? mode : nil;
}

- (void)saveSetupMode:(NSString *)mode {
    NSData *data = [NSJSONSerialization dataWithJSONObject:@{@"version": @1, @"mode": mode} options:0 error:nil];
    if (data) [data writeToFile:[self setupPath] atomically:YES];
}

- (void)showFirstRunIfNeeded {
    if ([self setupMode].length == 0) [self showFirstRun:nil];
}

- (void)showFirstRun:(id)sender {
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"选择 Muse 的模型方式";
    alert.informativeText = @"默认 Qwen3-0.6B 约 639 MB，从 Qwen 官方模型页下载到本机并核对 SHA-256；模型许可为 Apache-2.0。来源：https://huggingface.co/Qwen/Qwen3-0.6B-GGUF 。应用包已带本地运行时。也可复用 127.0.0.1:8080 上已有的服务，或只配置高阶模型。任何选择都不会替你开启付费调用。";
    [alert addButtonWithTitle:@"下载默认模型"];
    [alert addButtonWithTitle:@"使用已有本地服务"];
    [alert addButtonWithTitle:@"仅高阶模型"];
    [alert addButtonWithTitle:@"稍后设置"];
    NSModalResponse choice = [alert runModal];
    if (choice == NSAlertFirstButtonReturn) {
        [self showModelDownload];
    } else if (choice == NSAlertSecondButtonReturn) {
        [self saveSetupMode:@"local-external"];
        [self checkModelHealth];
        [self showModelSettings:nil];
    } else if (choice == NSAlertThirdButtonReturn) {
        [self saveSetupMode:@"high-only"];
        self.pendingSetupMode = @"high";
        [self sendEvent:@{@"type": @"model_settings_get"}];
        [self appendChatLine:@"Muse · 已选择仅高阶模式；请配置 Provider、价格和密钥后再启用远程调用。"];
    }
}

- (void)startManagedModelIfConfigured {
    if (![[self setupMode] isEqualToString:@"local-managed"]) return;
    if (self.lastModelStartAttempt && [[NSDate date] timeIntervalSinceDate:self.lastModelStartAttempt] < 30.0) return;
    self.lastModelStartAttempt = [NSDate date];
    self.modelStatus.stringValue = @"校验本地模型…";
    self.modelStatus.textColor = [NSColor secondaryLabelColor];
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
        NSString *message = nil;
        BOOL started = [self.modelManager startOwnedServer:&message];
        dispatch_async(dispatch_get_main_queue(), ^{
            [self appendLog:message ?: @"模型服务状态未知。"];
            if (!started) {
                self.modelStatus.stringValue = @"模型待处理";
                self.modelStatus.textColor = [NSColor systemOrangeColor];
            }
            [self performSelector:@selector(checkModelHealth) withObject:nil afterDelay:2.0];
        });
    });
}

- (void)showModelDownload {
    self.downloadWindow = [[NSWindow alloc] initWithContentRect:NSMakeRect(0, 0, 470, 205)
        styleMask:(NSWindowStyleMaskTitled | NSWindowStyleMaskClosable) backing:NSBackingStoreBuffered defer:NO];
    self.downloadWindow.title = @"安装默认本地模型";
    self.downloadWindow.releasedWhenClosed = NO;
    self.downloadWindow.delegate = self;
    [self.downloadWindow center];
    NSView *body = self.downloadWindow.contentView;
    [body addSubview:[self label:@"Qwen3-0.6B · Q8_0" frame:NSMakeRect(20, 157, 430, 24) size:17 color:[NSColor labelColor]]];
    self.downloadStatus = [self label:@"检查空间与已有文件…" frame:NSMakeRect(20, 127, 430, 20) size:12 color:[NSColor secondaryLabelColor]];
    [body addSubview:self.downloadStatus];
    self.downloadProgress = [[NSProgressIndicator alloc] initWithFrame:NSMakeRect(20, 97, 430, 18)];
    self.downloadProgress.indeterminate = YES;
    [self.downloadProgress startAnimation:nil];
    [body addSubview:self.downloadProgress];
    NSTextField *source = [self label:@"来源：Qwen 官方 GGUF · Apache-2.0" frame:NSMakeRect(20, 62, 430, 18)
                              size:11 color:[NSColor secondaryLabelColor]];
    source.toolTip = @"https://huggingface.co/Qwen/Qwen3-0.6B-GGUF";
    [body addSubview:source];
    [self button:@"暂停下载" frame:NSMakeRect(315, 15, 135, 31) action:@selector(cancelModelDownload:) parent:body];
    [self.downloadWindow makeKeyAndOrderFront:nil];
    __weak typeof(self) weakSelf = self;
    self.modelManager.progress = ^(int64_t received, int64_t expected) {
        if (!weakSelf.downloadWindow) return;
        if (expected > 0) {
            weakSelf.downloadProgress.indeterminate = NO;
            weakSelf.downloadProgress.doubleValue = 100.0 * (double)received / (double)expected;
            weakSelf.downloadStatus.stringValue = [NSString stringWithFormat:@"已下载 %.0f / %.0f MB · 完成后校验 SHA-256",
                (double)received / 1000000.0, (double)expected / 1000000.0];
        } else {
            weakSelf.downloadStatus.stringValue = [NSString stringWithFormat:@"已下载 %.0f MB · 总量约 639 MB",
                (double)received / 1000000.0];
        }
    };
    self.modelManager.completion = ^(BOOL installed, NSString *message) {
        [weakSelf.downloadWindow orderOut:nil];
        weakSelf.downloadWindow = nil;
        if (installed) {
            [weakSelf saveSetupMode:@"local-managed"];
            [weakSelf startManagedModelIfConfigured];
        }
        NSAlert *result = [[NSAlert alloc] init];
        result.messageText = installed ? @"本地模型已就绪" : @"模型尚未就绪";
        result.informativeText = message ?: @"请稍后重试。";
        [result addButtonWithTitle:installed ? @"知道了" : @"重试下载"];
        if (!installed) [result addButtonWithTitle:@"稍后"];
        if ([result runModal] == NSAlertFirstButtonReturn && !installed) {
            dispatch_async(dispatch_get_main_queue(), ^{ [weakSelf showModelDownload]; });
        }
    };
    [self.modelManager downloadDefault];
}

- (void)cancelModelDownload:(id)sender { [self.modelManager cancelDownload]; }

- (void)showSyntheticInput:(id)sender {
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"仅供开发测试 · 注入合成事件";
    alert.informativeText = @"此事件标记为 synthetic，不代表真实外部消息。";
    NSScrollView *scroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(0, 0, 440, 100)];
    scroll.hasVerticalScroller = YES;
    self.messageView.frame = NSMakeRect(0, 0, 440, 100);
    scroll.documentView = self.messageView;
    alert.accessoryView = scroll;
    [alert addButtonWithTitle:@"注入"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] == NSAlertFirstButtonReturn) [self sendMessage:nil];
}

- (void)sendMessage:(id)sender {
    NSString *text = [self.messageView.string stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if (text.length == 0) return;
    NSString *messageID = [[NSUUID UUID] UUIDString];
    [self appendLog:[NSString stringWithFormat:@"收到合成消息事件：%@", [text substringToIndex:MIN((NSUInteger)120, text.length)]]];
    [self sendEvent:@{@"type": @"message_event", @"source": @"synthetic", @"message_id": messageID, @"conversation_id": @"desktop-inbox", @"direction": @"incoming", @"text": text, @"request_high_tier": @((BOOL)(self.highTierToggle.state == NSControlStateValueOn))}];
}

- (void)sendChat:(id)sender {
    if (self.pendingChatPreviewRequestID.length > 0) return;
    NSString *text = [self.chatInput.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if (text.length == 0) return;
    NSMutableArray<NSString *> *scopes = [NSMutableArray array];
    if (self.selectedGoalResultScope.length > 0 &&
        [self.availableGoalResultScopes containsObject:self.selectedGoalResultScope]) {
        if ([self.availableGoalResultScopes containsObject:@"local"]) [scopes addObject:@"local"];
        [scopes addObject:self.selectedGoalResultScope];
    }
    self.pendingChatPreviewRequestID = [[NSUUID UUID] UUIDString];
    self.pendingChatPreviewText = text;
    self.pendingChatMemoryScopes = [scopes copy];
    self.chatInput.enabled = NO;
    self.chatSendButton.enabled = NO;
    [self sendEvent:@{@"type": @"chat_preview", @"request_id": self.pendingChatPreviewRequestID,
                      @"text": text, @"memory_scopes": self.pendingChatMemoryScopes}];
}

- (void)finishChatPreviewWithDigest:(NSString *)digest {
    NSString *message = self.pendingChatPreviewText;
    NSArray<NSString *> *scopes = self.pendingChatMemoryScopes ?: @[];
    self.pendingChatPreviewRequestID = nil;
    self.pendingChatPreviewText = nil;
    self.pendingChatMemoryScopes = nil;
    self.chatInput.enabled = YES;
    self.chatSendButton.enabled = YES;
    if (message.length == 0) return;
    self.chatInput.stringValue = @"";
    [self appendChatLine:[NSString stringWithFormat:@"你：%@", message]];
    NSMutableDictionary *event = [@{@"type": @"chat_message", @"text": message} mutableCopy];
    if (scopes.count > 0) event[@"memory_scopes"] = scopes;
    if (digest.length > 0) event[@"cloud_preview_sha256"] = digest;
    [self sendEvent:event];
    [self appendLog:digest.length > 0 ? @"即时对话：已按预览确认发送。" : @"即时对话：已发送给本地 Agent。"];
}

- (void)cancelChatPreview {
    self.pendingChatPreviewRequestID = nil;
    self.pendingChatPreviewText = nil;
    self.pendingChatMemoryScopes = nil;
    self.chatInput.enabled = YES;
    self.chatSendButton.enabled = YES;
}

- (void)proposeGoal:(id)sender {
    NSString *text = [self.chatInput.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if (text.length == 0) return;
    [self appendChatLine:[NSString stringWithFormat:@"你 · 长期目标：%@", text]];
    self.chatInput.stringValue = @"";
    NSMutableDictionary *event = [@{@"type": @"goal_propose", @"text": text,
                                    @"request_id": [[NSUUID UUID] UUIDString]} mutableCopy];
    NSString *selectedRef = self.goalResourcePicker.selectedItem.representedObject;
    if ([selectedRef isKindOfClass:[NSString class]] && selectedRef.length > 0) {
        event[@"context_refs"] = @[@{@"ref": selectedRef, @"purpose": @"用户选择监控文件夹"}];
    }
    [self sendEvent:event];
    [self appendLog:@"已请求 Muse 生成长期目标草稿；批准前不会执行。"];
}

- (void)prepareTextEditRecipe:(id)sender {
    if (self.pendingTextEditRequestID.length > 0) return;
    NSString *notes = [[self.workspace stringByStandardizingPath] stringByAppendingPathComponent:@"notes"];
    NSDictionary *notesAttributes = [[NSFileManager defaultManager] attributesOfItemAtPath:notes error:nil];
    if (![notesAttributes[NSFileType] isEqualToString:NSFileTypeDirectory]) {
        [self appendChatLine:@"Muse · 工作区中没有 notes 目录。请先准备已存在的 Muse-Test-*.txt 合成文件，并在 TextEdit 中打开它。"];
        return;
    }
    NSMutableArray<NSString *> *names = [NSMutableArray array];
    NSArray *entries = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:notes error:nil];
    for (NSString *entry in entries) {
        NSRange match = [entry rangeOfString:@"^Muse-Test-[A-Za-z0-9-]{1,40}\\.txt$"
                                         options:NSRegularExpressionSearch];
        if (match.location != 0 || match.length != entry.length) continue;
        NSDictionary *attributes = [[NSFileManager defaultManager]
            attributesOfItemAtPath:[notes stringByAppendingPathComponent:entry] error:nil];
        if ([attributes[NSFileType] isEqualToString:NSFileTypeRegular] &&
            [attributes[NSFileSize] unsignedLongLongValue] <= 8192) [names addObject:entry];
    }
    [names sortUsingSelector:@selector(compare:)];
    if (names.count == 0) {
        [self appendChatLine:@"Muse · notes 中没有可选的 Muse-Test-*.txt 合成文件（最多 8 KB）。请先创建并在 TextEdit 中打开。"];
        return;
    }
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"TextEdit 合成保存";
    alert.informativeText = @"选择已在 TextEdit 中打开的合成文件，输入想保存的完整新内容。Muse 会先观察并生成待批准计划；此时不会写入文件。";
    NSView *form = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 440, 172)];
    NSPopUpButton *picker = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(0, 140, 440, 28) pullsDown:NO];
    [picker addItemsWithTitles:names];
    picker.accessibilityTitle = @"现有合成文件";
    [form addSubview:picker];
    NSScrollView *scroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(0, 0, 440, 130)];
    scroll.hasVerticalScroller = YES;
    NSTextView *editor = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 440, 130)];
    editor.accessibilityTitle = @"TextEdit 合成文件新内容";
    scroll.documentView = editor;
    [form addSubview:scroll];
    alert.accessoryView = form;
    [alert addButtonWithTitle:@"生成待批准计划"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] != NSAlertFirstButtonReturn) return;
    NSString *name = picker.selectedItem.title;
    NSDictionary *attributes = [[NSFileManager defaultManager]
        attributesOfItemAtPath:[notes stringByAppendingPathComponent:name] error:nil];
    if (![attributes[NSFileType] isEqualToString:NSFileTypeRegular] ||
        [attributes[NSFileSize] unsignedLongLongValue] > 8192) {
        [self appendChatLine:@"Muse · 所选合成文件已经改变，请重新打开菜单核对。"];
        return;
    }
    NSString *content = editor.string ?: @"";
    NSUInteger bytes = [content lengthOfBytesUsingEncoding:NSUTF8StringEncoding];
    if (bytes == 0 || bytes > 8192) {
        [self appendChatLine:@"Muse · 新内容必须是 1 至 8192 字节的文本；请重新打开菜单输入。"];
        return;
    }
    self.pendingTextEditRequestID = [[NSUUID UUID] UUIDString];
    [self sendEvent:@{@"type": @"recipe_prepare", @"relative_path": [@"notes/" stringByAppendingString:name],
                      @"content": content, @"request_id": self.pendingTextEditRequestID}];
    [self appendChatLine:[NSString stringWithFormat:@"Muse · 正在核对 TextEdit 中的 %@，并观察保存配方；批准前不会执行。", name]];
}

- (void)prepareBrowserRecipe:(id)sender {
    if (self.paused || self.pendingBrowserRecipeRequestID.length > 0) return;
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"准备 Edge 公开搜索目标";
    alert.informativeText = @"输入公开搜索词。Muse 会在隔离 Edge 会话打开 Python.org 并观察搜索控件；此时不提交搜索。生成的长期目标仍需你审阅并批准。";
    NSView *form = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 440, 58)];
    NSTextField *query = [self settingsField:@"Python.org 搜索词" value:@"" x:0 y:4 width:440 parent:form];
    query.accessibilityTitle = @"Edge 公开搜索词";
    alert.accessoryView = form;
    [alert addButtonWithTitle:@"观察搜索控件"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] != NSAlertFirstButtonReturn) return;
    NSString *search = [query.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if (search.length < 2 || search.length > 160) {
        [self appendChatLine:@"Muse · 搜索词需要 2 至 160 个字符；请重新打开 Edge 搜索目标。"];
        return;
    }
    NSString *objective = [self.chatInput.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if (objective.length == 0) {
        objective = [NSString stringWithFormat:@"用 Edge 浏览器在 Python.org 搜索 %@，读取三篇公开资料并写中文提纲；根据浏览器实际点击读回的来源标注来源。", search];
    }
    self.pendingBrowserGoalText = objective;
    self.pendingBrowserRecipeRequestID = [[NSUUID UUID] UUIDString];
    [self sendEvent:@{@"type": @"browser_recipe_prepare", @"query": search,
                      @"request_id": self.pendingBrowserRecipeRequestID}];
    [self appendChatLine:[NSString stringWithFormat:@"Muse · 正在观察 Edge 上的 Python.org 搜索控件：%@。批准前不会搜索或写文件。", search]];
}

- (void)requestGoalList:(id)sender { [self sendEvent:@{@"type": @"goal_list"}]; }

- (void)goalSelected:(id)sender {
    NSString *goalID = self.goalPicker.selectedItem.representedObject;
    if ([goalID isKindOfClass:[NSString class]] && goalID.length > 0) {
        [self sendEvent:@{@"type": @"goal_get", @"goal_id": goalID}];
    }
}

- (void)decideGoal:(NSString *)decision {
    if (self.activeGoalID.length == 0 || !self.activeGoalRevision) return;
    NSMutableDictionary *event = [@{@"type": @"goal_decide", @"goal_id": self.activeGoalID,
                                    @"revision": self.activeGoalRevision, @"decision": decision} mutableCopy];
    if ([decision isEqualToString:@"approve"]) {
        if (self.activeGoalPlanDigest.length != 64) {
            [self appendChatLine:@"Muse · 当前计划缺少可核对摘要，未发送批准；请重新选择目标。"];
            return;
        }
        event[@"plan_digest"] = self.activeGoalPlanDigest;
    }
    [self sendEvent:event];
}

- (void)controlGoal:(NSString *)action {
    if (self.activeGoalID.length == 0) return;
    [self sendEvent:@{@"type": @"goal_control", @"goal_id": self.activeGoalID, @"action": action}];
}

- (void)approveGoal:(id)sender { [self decideGoal:@"approve"]; }
- (void)rejectGoal:(id)sender { [self decideGoal:@"reject"]; }
- (void)pauseGoal:(id)sender { [self controlGoal:@"pause"]; }
- (void)resumeGoal:(id)sender { [self controlGoal:@"resume"]; }
- (void)cancelGoal:(id)sender { [self controlGoal:@"cancel"]; }
- (void)retryGoal:(id)sender { [self controlGoal:@"retry"]; }

- (void)reviseGoal:(id)sender {
    if (self.activeGoalID.length == 0) return;
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"修改长期目标";
    alert.informativeText = @"写下修订要求。新版计划生成后仍需重新批准。";
    NSTextField *field = [[NSTextField alloc] initWithFrame:NSMakeRect(0, 0, 430, 28)];
    field.placeholderString = @"例如：把提纲改成三分钟演讲，并补充隐私说明";
    field.accessibilityTitle = @"目标修订要求";
    alert.accessoryView = field;
    [alert addButtonWithTitle:@"生成新版计划"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] != NSAlertFirstButtonReturn) return;
    NSString *text = [field.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if (text.length == 0) return;
    [self sendEvent:@{@"type": @"goal_revise", @"goal_id": self.activeGoalID, @"text": text}];
    [self appendLog:@"已请求生成新版只读计划；旧批准不能用于新修订。"];
}

- (void)updateGoalButtons:(NSString *)status {
    BOOL draft = [status isEqualToString:@"DRAFT"];
    BOOL active = [status isEqualToString:@"ACTIVE"];
    BOOL paused = [status isEqualToString:@"PAUSED"];
    self.goalApproveButton.enabled = draft;
    self.goalRejectButton.enabled = draft;
    self.goalPauseButton.enabled = active;
    self.goalResumeButton.enabled = paused;
    self.goalCancelButton.enabled = active || paused;
    self.goalReviseButton.enabled = draft || active || paused || [status isEqualToString:@"WAITING_USER"];
    self.goalRetryButton.enabled = [status isEqualToString:@"WAITING_USER"];
    self.goalApproveButton.hidden = !self.goalApproveButton.enabled;
    self.goalRejectButton.hidden = !self.goalRejectButton.enabled;
    self.goalPauseButton.hidden = !self.goalPauseButton.enabled;
    self.goalResumeButton.hidden = !self.goalResumeButton.enabled;
    self.goalCancelButton.hidden = !self.goalCancelButton.enabled;
    self.goalReviseButton.hidden = !self.goalReviseButton.enabled;
    self.goalRetryButton.hidden = !self.goalRetryButton.enabled;
}

- (void)showGoalResult:(NSDictionary *)result {
    NSDictionary *plan = result[@"plan"];
    if (![plan isKindOfClass:[NSDictionary class]]) return;
    self.activeGoalID = result[@"goal_id"];
    self.activeGoalRevision = result[@"revision"];
    self.activeGoalPlanDigest = [result[@"plan_digest"] isKindOfClass:[NSString class]] ? result[@"plan_digest"] : nil;
    NSDictionary *goalNotify = plan[@"notify"];
    if ([self.activeGoalID isKindOfClass:[NSString class]] && [goalNotify isKindOfClass:[NSDictionary class]]) {
        self.goalNotifyByID[self.activeGoalID] = goalNotify;
    }
    NSString *status = result[@"status"] ?: @"UNKNOWN";
    if ([status isEqualToString:@"DRAFT"] || [status isEqualToString:@"WAITING_USER"]) [self showTaskPane:nil];
    [self updateGoalButtons:status];
    NSString *title = [plan[@"title"] isKindOfClass:[NSString class]] ? plan[@"title"] : @"长期目标";
    NSString *nextDue = [result[@"next_due"] isKindOfClass:[NSString class]] ? result[@"next_due"] : @"待定";
    NSString *deadline = [plan[@"deadline"] isKindOfClass:[NSString class]] ? plan[@"deadline"] : @"无";
    NSString *approvalID = [result[@"approval_id"] isKindOfClass:[NSString class]] ? result[@"approval_id"] : @"尚未批准";
    NSMenuItem *selectedGoal = nil;
    for (NSMenuItem *item in self.goalPicker.itemArray) {
        if ([item.representedObject isEqual:self.activeGoalID]) { selectedGoal = item; break; }
    }
    if (!selectedGoal) {
        [self.goalPicker addItemWithTitle:title];
        selectedGoal = self.goalPicker.lastItem;
        selectedGoal.representedObject = self.activeGoalID;
    }
    selectedGoal.title = title;
    [self.goalPicker selectItem:selectedGoal];
    self.taskTitle.stringValue = title;
    NSNumber *runCount = [result[@"run_count"] isKindOfClass:[NSNumber class]] ? result[@"run_count"] : @0;
    NSString *plainStatus = [status isEqualToString:@"DRAFT"] ? @"等待批准" :
        [status isEqualToString:@"ACTIVE"] ? (runCount.integerValue > 0 ? @"已更新 · 持续关注中" : @"已批准 · 执行中") :
        [status isEqualToString:@"COMPLETED"] ? @"产物已生成并核对" :
        [status isEqualToString:@"PAUSED"] ? @"已暂停" :
        [status isEqualToString:@"WAITING_USER"] ? @"等待你的决定" : status;
    self.taskState.stringValue = [NSString stringWithFormat:@"%@ · 修订 %@", plainStatus, self.activeGoalRevision ?: @"?"];
    self.taskState.textColor = ([status isEqualToString:@"ACTIVE"] || [status isEqualToString:@"COMPLETED"]) ?
        [NSColor systemGreenColor] : [NSColor systemOrangeColor];
    NSMutableArray<NSString *> *lines = [NSMutableArray array];
    [lines addObject:[NSString stringWithFormat:@"目标：%@", plan[@"objective"] ?: @""]];
    [lines addObject:[NSString stringWithFormat:@"计划摘要 SHA-256：%@", self.activeGoalPlanDigest ?: @"缺失"]];
    [lines addObject:[NSString stringWithFormat:@"截止：%@ · 时区：%@", deadline, plan[@"timezone"] ?: @"未知"]];
    NSArray *triggers = plan[@"triggers"];
    if ([triggers isKindOfClass:[NSArray class]]) {
        for (NSDictionary *trigger in triggers) {
            if (![trigger isKindOfClass:[NSDictionary class]]) continue;
            [lines addObject:[NSString stringWithFormat:@"触发：%@ · %@", trigger[@"kind"] ?: @"?",
                              trigger[@"every_seconds"] ?: trigger[@"topic"] ?: @"?"]];
        }
    }
    NSArray *steps = plan[@"steps"];
    NSDictionary *textEditArgs = nil;
    NSDictionary *browserArgs = nil;
    NSMutableArray<NSString *> *webReadURLs = [NSMutableArray array];
    if ([steps isKindOfClass:[NSArray class]]) {
        NSUInteger index = 0;
        for (NSDictionary *step in steps) {
            if (![step isKindOfClass:[NSDictionary class]]) continue;
            [lines addObject:[NSString stringWithFormat:@"%lu. %@ · %@", (unsigned long)++index,
                              step[@"capability"] ?: @"?", step[@"id"] ?: @"?"]];
            if ([step[@"capability"] isEqualToString:@"web.read"] &&
                [step[@"args"] isKindOfClass:[NSDictionary class]]) {
                NSString *url = step[@"args"][@"url"];
                if ([url isKindOfClass:[NSString class]] && url.length > 0) {
                    [lines addObject:[NSString stringWithFormat:@"公开网页 URL：%@", url]];
                    if (![webReadURLs containsObject:url]) [webReadURLs addObject:url];
                }
            }
            if ([step[@"capability"] isEqualToString:@"app.recipe"] &&
                [step[@"args"] isKindOfClass:[NSDictionary class]]) textEditArgs = step[@"args"];
            if ([step[@"capability"] isEqualToString:@"browser.research"] &&
                [step[@"args"] isKindOfClass:[NSDictionary class]] &&
                [step[@"args"][@"recipe_digest"] isKindOfClass:[NSString class]]) browserArgs = step[@"args"];
        }
    }
    if (self.activeGoalPlanDigest.length != 64 && [status isEqualToString:@"DRAFT"]) {
        self.goalApproveButton.enabled = NO;
    }
    if (textEditArgs) {
        [lines addObject:[NSString stringWithFormat:@"TextEdit 文件：%@ · 窗口：%@",
                          textEditArgs[@"relative_path"] ?: @"?", textEditArgs[@"window_title"] ?: @"?"]];
        [lines addObject:[NSString stringWithFormat:@"批准后将写入的完整内容：\n%@", textEditArgs[@"content"] ?: @""]];
    }
    if (browserArgs) {
        NSString *recipeDigest = browserArgs[@"recipe_digest"];
        [lines addObject:[NSString stringWithFormat:@"Edge 搜索：%@ · %@ · 最多 %@ 页",
                          browserArgs[@"query"] ?: @"?", browserArgs[@"engine"] ?: @"?", browserArgs[@"max_pages"] ?: @"?"]];
        [lines addObject:[NSString stringWithFormat:@"应用：%@ · 窗口：%@",
                          browserArgs[@"target_bundle_id"] ?: @"?", browserArgs[@"window_title"] ?: @"?"]];
        [lines addObject:[NSString stringWithFormat:@"配方摘要 SHA-256：%@", recipeDigest ?: @"?"]];
        for (NSDictionary *control in self.browserObservedControls[recipeDigest] ?: @[]) {
            if (![control isKindOfClass:[NSDictionary class]]) continue;
            [lines addObject:[NSString stringWithFormat:@"已观察控件：%@ · %@ · %@",
                              control[@"role"] ?: @"?", control[@"name"] ?: @"?", control[@"action"] ?: @"?"]];
        }
    }
    NSDictionary *permissions = plan[@"permissions"];
    if ([permissions isKindOfClass:[NSDictionary class]]) {
        [lines addObject:[NSString stringWithFormat:@"能力范围：%@", [permissions[@"capabilities"] componentsJoinedByString:@", "] ?: @"无"]];
        if ([permissions[@"resource_refs"] isKindOfClass:[NSArray class]]) {
            [lines addObject:[NSString stringWithFormat:@"来源与应用范围：%@",
                              [permissions[@"resource_refs"] componentsJoinedByString:@", "]]];
        }
    }
    NSDictionary *budget = plan[@"budget"];
    if ([budget isKindOfClass:[NSDictionary class]]) {
        [lines addObject:[NSString stringWithFormat:@"预算：模型 %@ tokens · 搜索 %@ 次", budget[@"max_model_tokens"] ?: @"?", budget[@"max_searches"] ?: @"?"]];
    }
    if ([goalNotify isKindOfClass:[NSDictionary class]]) {
        [lines addObject:[NSString stringWithFormat:@"通知：完成%@ · 需决定%@ · 重要变化%@",
                          [goalNotify[@"on_complete"] boolValue] ? @"开启" : @"关闭",
                          [goalNotify[@"on_need_decision"] boolValue] ? @"开启" : @"关闭",
                          [goalNotify[@"on_major_update"] boolValue] ? @"开启" : @"关闭"]];
    }
    [lines addObject:[NSString stringWithFormat:@"批准引用：%@", approvalID]];
    self.technicalPlanView.string = [lines componentsJoinedByString:@"\n"];
    NSMutableArray<NSString *> *summary = [NSMutableArray arrayWithObject:[NSString stringWithFormat:@"目标：%@", plan[@"objective"] ?: @""]];
    if ([status isEqualToString:@"DRAFT"]) {
        [summary addObject:@"计划草稿，尚未批准；批准前不会执行或写入文件。"];
        [summary addObject:[NSString stringWithFormat:@"计划摘要：%@", self.activeGoalPlanDigest ?: @"缺失"]];
        for (NSString *url in webReadURLs) {
            [summary addObject:[NSString stringWithFormat:@"公开网页来源（完整 URL）：%@", url]];
        }
        NSMutableArray<NSString *> *actions = [NSMutableArray array];
        NSDictionary *actionNames = @{@"web.search": @"查找公开来源", @"web.read": @"读取公开网页",
                                      @"browser.research": @"使用 Edge 查找并读取已授权站点",
                                      @"app.recipe": @"在 TextEdit 保存已打开的合成文件并回读核对",
                                      @"model.compose": @"整理内容",
                                      @"workspace.write_artifact": @"保存并核对文件"};
        for (NSDictionary *step in steps) {
            if (![step isKindOfClass:[NSDictionary class]]) continue;
            [actions addObject:actionNames[step[@"capability"]] ?: @"执行计划步骤"];
        }
        if (actions.count > 0) [summary addObject:[NSString stringWithFormat:@"执行安排：%@", [actions componentsJoinedByString:@" → "]]];
        if (textEditArgs) {
            [summary addObject:[NSString stringWithFormat:@"TextEdit 范围：工作区 %@；窗口 %@。",
                                textEditArgs[@"relative_path"] ?: @"?", textEditArgs[@"window_title"] ?: @"?"]];
            [summary addObject:[NSString stringWithFormat:@"批准后将写入的完整内容：\n%@", textEditArgs[@"content"] ?: @""]];
        }
        if (browserArgs) {
            NSString *recipeDigest = browserArgs[@"recipe_digest"];
            [summary addObject:[NSString stringWithFormat:@"Edge 公开搜索：%@；站点 %@；窗口 %@；最多 %@ 页。",
                                browserArgs[@"query"] ?: @"?", browserArgs[@"engine"] ?: @"?",
                                browserArgs[@"window_title"] ?: @"?", browserArgs[@"max_pages"] ?: @"?"]];
            for (NSDictionary *control in self.browserObservedControls[recipeDigest] ?: @[]) {
                if (![control isKindOfClass:[NSDictionary class]]) continue;
                [summary addObject:[NSString stringWithFormat:@"已观察控件：%@ · %@ · %@",
                                    control[@"role"] ?: @"?", control[@"name"] ?: @"?", control[@"action"] ?: @"?"]];
            }
            [summary addObject:[NSString stringWithFormat:@"配方摘要：%@", recipeDigest ?: @"?"]];
        }
        for (NSDictionary *step in steps) {
            if (![step[@"capability"] isEqualToString:@"browser.research"]) continue;
            NSDictionary *args = [step[@"args"] isKindOfClass:[NSDictionary class]] ? step[@"args"] : @{};
            [summary addObject:[NSString stringWithFormat:@"浏览器范围：Edge · %@ · 最多 %@ 页。",
                                args[@"engine"] ?: @"已批准站点", args[@"max_pages"] ?: @"?"]];
        }
        if ([budget isKindOfClass:[NSDictionary class]]) {
            [summary addObject:[NSString stringWithFormat:@"上限：模型 %@ tokens，网页读取 %@ 次。",
                budget[@"max_model_tokens"] ?: @"?", budget[@"max_searches"] ?: @"?"]];
        }
        [summary addObject:@"完整计划和授权范围可在右上角“技术详情”查看。"];
    } else {
        if (runCount.integerValue > 0) [summary addObject:[NSString stringWithFormat:@"最新进度：第 %@ 次更新的产物已核对。", runCount]];
        if ([result[@"fact_verification"] isEqualToString:@"NOT_VERIFIED"]) {
            [summary addObject:@"模型整理的提纲和资料要点尚未完成事实核验；请查看产物中的来源清单。"];
        }
        NSString *artifact = self.goalArtifactsByID[self.activeGoalID];
        if (artifact.length > 0) [summary addObject:[NSString stringWithFormat:@"文件：%@", artifact]];
        if ([status isEqualToString:@"ACTIVE"]) {
            [summary addObject:textEditArgs ? @"下一步：在已批准的 TextEdit 文件中保存并回读核对。" :
                 @"下一步：继续关注已授权来源，有变化时更新同一目标。"];
        } else if ([status isEqualToString:@"COMPLETED"]) {
            [summary addObject:textEditArgs ? @"下一步：检查 TextEdit 文件和保存回读记录。" :
                 @"下一步：打开工作区查看产物，或继续提出新目标。"];
        } else if ([status isEqualToString:@"PAUSED"]) {
            [summary addObject:@"下一步：点击“继续”恢复监控。"];
        } else if ([status isEqualToString:@"WAITING_USER"]) {
            [summary addObject:@"下一步：查看结果卡，决定如何继续。"];
        }
    }
    [self setInspectorText:[summary componentsJoinedByString:@"\n\n"]];
    NSString *previousStatus = self.goalDisplayStatusByID[self.activeGoalID];
    if (![previousStatus isEqualToString:status]) {
        if ([status isEqualToString:@"DRAFT"]) {
            [self appendChatLine:[NSString stringWithFormat:@"Muse · %@ 的计划草稿已生成，请在右侧审阅后决定。", title]];
        } else if ([status isEqualToString:@"ACTIVE"] && runCount.integerValue == 0) {
            [self appendChatLine:[NSString stringWithFormat:@"Muse · %@ 已批准，正在等待执行。", title]];
        }
        self.goalDisplayStatusByID[self.activeGoalID] = status;
    }
    [self appendLog:[NSString stringWithFormat:@"目标状态：%@ · 修订 %@", status, self.activeGoalRevision ?: @"?"]];
}

- (NSTextField *)settingsField:(NSString *)title value:(NSString *)value x:(CGFloat)x y:(CGFloat)y width:(CGFloat)width parent:(NSView *)parent {
    [parent addSubview:[self label:title frame:NSMakeRect(x, y + 25, width, 20) size:11 color:[NSColor secondaryLabelColor]]];
    NSTextField *field = [[NSTextField alloc] initWithFrame:NSMakeRect(x, y, width, 24)];
    field.stringValue = value ?: @"";
    [parent addSubview:field];
    return field;
}

- (void)requestPluginSettings:(id)sender {
    self.pluginDialogRequested = YES;
    [self sendEvent:@{@"type": @"plugin_list"}];
}

- (void)showPluginSettings {
    NSDictionary *builtIn = nil;
    NSUInteger stagedCount = 0;
    for (NSDictionary *item in self.plugins) {
        if (![item isKindOfClass:[NSDictionary class]]) continue;
        if ([item[@"id"] isEqualToString:@"builtin.text_stats"]) builtIn = item;
        else stagedCount++;
    }
    if (!builtIn) { [self appendLog:@"插件目录未提供内置示例。"] ; return; }
    NSString *manifestPath = [[[NSBundle mainBundle] resourcePath] stringByAppendingPathComponent:@"muse_plugin_manifest.json"];
    NSData *data = [NSData dataWithContentsOfFile:manifestPath];
    NSDictionary *manifest = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
    if (![manifest isKindOfClass:[NSDictionary class]]) {
        [self appendLog:@"插件清单无法读取；保持禁用。"];
        return;
    }
    NSDictionary *permissions = builtIn[@"permissions"];
    NSString *status = builtIn[@"status"] ?: @"UNKNOWN";
    NSString *statusLabel = [status isEqualToString:@"ENABLED"] ? @"已启用" :
        [status isEqualToString:@"DISABLED"] ? @"未启用" : @"已阻止：清单无效";
    NSString *digest = [builtIn[@"digest"] isKindOfClass:[NSString class]] ? builtIn[@"digest"] : @"?";
    NSString *details = [NSString stringWithFormat:
        @"%@\n%@\n\n版本：%@\n状态：%@\n能力：%@\n文件权限：%@\n网络：%@ · 进程：%@ · 密钥：%@\n清单摘要：%@…\n%@",
        manifest[@"name"] ?: @"内置示例", manifest[@"description"] ?: @"",
        builtIn[@"version"] ?: @"?", statusLabel,
        [builtIn[@"capabilities"] componentsJoinedByString:@"、"] ?: @"无",
        [permissions[@"filesystem"] isEqualToString:@"none"] ? @"无" : permissions[@"filesystem"] ?: @"?",
        [permissions[@"network"] boolValue] ? @"允许" : @"无",
        [permissions[@"process"] boolValue] ? @"允许" : @"无",
        [permissions[@"secrets"] boolValue] ? @"允许" : @"无",
        [digest substringToIndex:MIN((NSUInteger)16, digest.length)],
        stagedCount ? [NSString stringWithFormat:@"另有 %lu 个待审查条目，仅暂存，不能运行。", (unsigned long)stagedCount] : @"未审查插件不能运行。"];
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"插件与权限";
    alert.informativeText = details;
    if ([status isEqualToString:@"DISABLED"]) {
        [alert addButtonWithTitle:@"启用并授权"];
        [alert addButtonWithTitle:@"关闭"];
        if ([alert runModal] == NSAlertFirstButtonReturn) {
            [self sendEvent:@{@"type": @"plugin_decide", @"plugin_id": @"builtin.text_stats",
                              @"decision": @"enable", @"approved": @YES}];
        }
    } else if ([status isEqualToString:@"ENABLED"]) {
        [alert addButtonWithTitle:@"运行合成示例"];
        [alert addButtonWithTitle:@"禁用"];
        [alert addButtonWithTitle:@"关闭"];
        NSModalResponse response = [alert runModal];
        if (response == NSAlertFirstButtonReturn) {
            [self sendEvent:@{@"type": @"plugin_run", @"plugin_id": @"builtin.text_stats",
                              @"input": @{@"text": @"你好\n世界"}}];
        } else if (response == NSAlertSecondButtonReturn) {
            [self sendEvent:@{@"type": @"plugin_decide", @"plugin_id": @"builtin.text_stats",
                              @"decision": @"disable"}];
        }
    } else {
        [alert addButtonWithTitle:@"关闭"];
        [alert runModal];
    }
}

- (void)updateModelEndpointValidation {
    if (!self.modelEndpointField) return;
    NSString *text = [self.modelEndpointField.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    NSString *path = [NSURLComponents componentsWithString:text].path;
    BOOL baseURL = [path isEqualToString:@"/v1"] || [path isEqualToString:@"/v1/"];
    self.modelSettingsSaveButton.enabled = !baseURL;
    self.modelEndpointWarning.stringValue = baseURL ?
        @"这里只是 API 基础地址；请补全请求路径" : @"高阶需正确路由、正数调用上限和已核价";
    self.modelEndpointWarning.textColor = baseURL ? [NSColor systemRedColor] : [NSColor secondaryLabelColor];
}

- (void)controlTextDidChange:(NSNotification *)notification {
    if (notification.object == self.modelEndpointField) [self updateModelEndpointValidation];
}

- (void)showModelSettings:(id)sender {
    if (![self.modelSettings isKindOfClass:[NSDictionary class]]) {
        [self sendEvent:@{@"type": @"model_settings_get"}];
        [self appendLog:@"模型设置正在载入，请稍后再打开。"];
        return;
    }
    NSDictionary *settings = self.modelSettings;
    NSDictionary *profiles = settings[@"profiles"];
    NSString *localID = settings[@"active_local"] ?: @"local-default";
    NSString *highID = settings[@"active_high"] ?: @"high-default";
    NSDictionary *local = profiles[localID] ?: @{};
    NSDictionary *high = profiles[highID] ?: @{};
    NSView *form = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 720, 510)];
    [form addSubview:[self label:@"路由模式" frame:NSMakeRect(12, 474, 100, 22) size:12 color:nil]];
    NSPopUpButton *mode = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(116, 470, 170, 28) pullsDown:NO];
    [mode addItemsWithTitles:@[@"纯本地", @"纯高阶", @"混合", @"自定义"]];
    NSArray *modeValues = @[@"local", @"high", @"mixed", @"custom"];
    NSUInteger currentMode = [modeValues indexOfObject:settings[@"mode"] ?: @"local"];
    [mode selectItemAtIndex:(currentMode == NSNotFound ? 0 : currentMode)];
    [form addSubview:mode];
    [form addSubview:[self label:@"每次超时（秒）" frame:NSMakeRect(470, 474, 150, 22) size:12 color:nil]];
    NSTextField *timeout = [[NSTextField alloc] initWithFrame:NSMakeRect(622, 470, 80, 24)];
    timeout.integerValue = [settings[@"timeout_seconds"] integerValue];
    [form addSubview:timeout];
    [form addSubview:[self label:@"本地槽 · 更改 ID 可另存配置" frame:NSMakeRect(12, 435, 330, 23) size:13 color:nil]];
    [form addSubview:[self label:@"高阶槽 · 更改 ID 可另存配置" frame:NSMakeRect(370, 435, 330, 23) size:13 color:nil]];
    NSTextField *localIDField = [self settingsField:@"配置 ID" value:localID x:12 y:395 width:326 parent:form];
    NSTextField *localEndpoint = [self settingsField:@"兼容端点 URL" value:local[@"endpoint"] x:12 y:340 width:326 parent:form];
    NSTextField *localModel = [self settingsField:@"模型名称" value:local[@"model"] x:12 y:285 width:326 parent:form];
    NSTextField *highIDField = [self settingsField:@"配置 ID" value:highID x:370 y:395 width:326 parent:form];
    [form addSubview:[self label:@"协议" frame:NSMakeRect(370, 365, 326, 20) size:11 color:[NSColor secondaryLabelColor]]];
    NSPopUpButton *highProtocol = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(370, 337, 326, 28) pullsDown:NO];
    NSArray *highProtocolValues = @[@"openai_compatible", @"anthropic_messages", @"openai_responses", @"deepseek_chat"];
    [highProtocol addItemsWithTitles:@[@"OpenAI compatible", @"Anthropic Messages",
                                        @"OpenAI Responses (GPT)", @"DeepSeek Chat"]];
    NSUInteger currentProtocol = [highProtocolValues indexOfObject:high[@"protocol"] ?: @"openai_compatible"];
    [highProtocol selectItemAtIndex:(currentProtocol == NSNotFound ? 0 : currentProtocol)];
    [form addSubview:highProtocol];
    NSTextField *highEndpoint = [self settingsField:@"完整请求 URL（例如 …/v1/chat/completions）" value:high[@"endpoint"] x:370 y:285 width:326 parent:form];
    NSTextField *highModel = [self settingsField:@"模型名称（填写精确 ID）" value:high[@"model"] x:370 y:230 width:326 parent:form];
    NSTextField *dailyTokens = [self settingsField:@"每日总 token 上限" value:[settings[@"daily_token_limit"] description] x:12 y:230 width:326 parent:form];
    NSTextField *goalTokens = [self settingsField:@"每个目标 token 上限" value:[settings[@"per_goal_token_limit"] description] x:12 y:175 width:326 parent:form];
    NSTextField *maxTokens = [self settingsField:@"单次输出 token 上限" value:[settings[@"max_tokens_per_call"] description] x:12 y:120 width:326 parent:form];
    NSTextField *remoteCalls = [self settingsField:@"每日高阶远程调用上限" value:[settings[@"daily_remote_call_limit"] description] x:370 y:175 width:326 parent:form];
    NSButton *keychain = [NSButton checkboxWithTitle:@"使用本项目 Keychain 密钥引用" target:nil action:nil];
    keychain.frame = NSMakeRect(370, 128, 326, 24);
    keychain.state = [high[@"keychain_service"] length] > 0 ? NSControlStateValueOn : NSControlStateValueOff;
    [form addSubview:keychain];
    NSButton *cloud = [NSButton checkboxWithTitle:@"允许向已配置高阶端点发送任务资料" target:nil action:nil];
    cloud.frame = NSMakeRect(12, 73, 340, 24);
    cloud.state = [settings[@"cloud_data_allowed"] boolValue] ? NSControlStateValueOn : NSControlStateValueOff;
    [form addSubview:cloud];
    self.modelEndpointWarning = [self label:@"高阶需正确路由、正数调用上限和已核价" frame:NSMakeRect(370, 73, 340, 24)
                                        size:11 color:[NSColor secondaryLabelColor]];
    [form addSubview:self.modelEndpointWarning];
    NSTextField *routes = [self settingsField:@"自定义路由：例如 chat=local,goal_plan=high" value:@"" x:12 y:18 width:684 parent:form];
    NSDictionary *purposeRoutes = settings[@"purpose_routes"];
    if ([purposeRoutes isKindOfClass:[NSDictionary class]]) {
        NSMutableArray *parts = [NSMutableArray array];
        for (NSString *purpose in [[purposeRoutes allKeys] sortedArrayUsingSelector:@selector(compare:)]) {
            [parts addObject:[NSString stringWithFormat:@"%@=%@", purpose, purposeRoutes[purpose]]];
        }
        routes.stringValue = [parts componentsJoinedByString:@","];
    }
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"Muse 模型与预算";
    NSString *modeHint = [settings[@"mode"] isEqualToString:@"local"] ? @"当前保存的是纯本地模式，聊天不会调用高阶模型。" : @"";
    NSString *limitHint = remoteCalls.integerValue == 0 ? @"当前保存的每日高阶调用上限为 0，远程请求会被阻止。" : @"";
    alert.informativeText = [NSString stringWithFormat:@"设置只影响模型路由，不改变文件、邮件或目标权限。%@%@密钥只从本项目 Keychain 条目读取。", modeHint, limitHint];
    alert.accessoryView = form;
    self.modelSettingsSaveButton = [alert addButtonWithTitle:@"保存"];
    [alert addButtonWithTitle:@"取消"];
    self.modelEndpointField = highEndpoint;
    highEndpoint.delegate = self;
    [self updateModelEndpointValidation];
    alert.window.initialFirstResponder = highModel;
    NSModalResponse response = [alert runModal];
    highEndpoint.delegate = nil;
    self.modelEndpointField = nil;
    self.modelEndpointWarning = nil;
    self.modelSettingsSaveButton = nil;
    if (response != NSAlertFirstButtonReturn) return;
    NSString *newLocalID = [localIDField.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    NSString *newHighID = [highIDField.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    NSMutableDictionary *newProfiles = [profiles mutableCopy];
    newProfiles[newLocalID] = @{@"protocol": @"openai_compatible", @"endpoint": localEndpoint.stringValue,
                             @"model": localModel.stringValue, @"keychain_service": @"", @"keychain_account": @""};
    NSString *service = keychain.state == NSControlStateValueOn ? [@"org.gosim.local-agent.model." stringByAppendingString:newHighID] : @"";
    newProfiles[newHighID] = @{@"protocol": highProtocolValues[highProtocol.indexOfSelectedItem],
                            @"endpoint": highEndpoint.stringValue, @"model": highModel.stringValue,
                            @"keychain_service": service, @"keychain_account": service.length > 0 ? newHighID : @""};
    NSMutableDictionary *newRoutes = [NSMutableDictionary dictionary];
    for (NSString *part in [routes.stringValue componentsSeparatedByString:@","]) {
        NSString *trimmed = [part stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if (trimmed.length == 0) continue;
        NSArray *pair = [trimmed componentsSeparatedByString:@"="];
        if (pair.count != 2) { [self appendLog:@"自定义路由格式错误，设置未保存。"]; return; }
        newRoutes[[pair[0] stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]]] =
            [pair[1] stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    }
    NSMutableDictionary *updated = [settings mutableCopy];
    updated[@"profiles"] = newProfiles;
    updated[@"active_local"] = newLocalID;
    updated[@"active_high"] = newHighID;
    if ([updated[@"backup_high"] isEqualToString:newHighID]) updated[@"backup_high"] = @"";
    NSMutableDictionary *selectedEfforts = [settings[@"selected_reasoning_effort"] isKindOfClass:[NSDictionary class]] ?
        [settings[@"selected_reasoning_effort"] mutableCopy] : [NSMutableDictionary dictionary];
    if (![localModel.stringValue isEqualToString:local[@"model"] ?: @""]) [selectedEfforts removeObjectForKey:newLocalID];
    if (![highModel.stringValue isEqualToString:high[@"model"] ?: @""] ||
        ![newProfiles[newHighID][@"protocol"] isEqualToString:high[@"protocol"] ?: @""]) {
        [selectedEfforts removeObjectForKey:newHighID];
    }
    updated[@"selected_reasoning_effort"] = selectedEfforts;
    updated[@"mode"] = modeValues[mode.indexOfSelectedItem];
    updated[@"purpose_routes"] = newRoutes;
    updated[@"cloud_data_allowed"] = @((BOOL)(cloud.state == NSControlStateValueOn));
    updated[@"daily_remote_call_limit"] = @(remoteCalls.integerValue);
    updated[@"daily_token_limit"] = @(dailyTokens.integerValue);
    updated[@"per_goal_token_limit"] = @(goalTokens.integerValue);
    updated[@"max_tokens_per_call"] = @(maxTokens.integerValue);
    updated[@"timeout_seconds"] = @(timeout.integerValue);
    [self sendEvent:@{@"type": @"model_settings_set", @"settings": updated}];
}

- (NSString *)modelOrigin:(NSString *)endpoint {
    NSURLComponents *parts = [NSURLComponents componentsWithString:endpoint ?: @""];
    NSString *scheme = parts.scheme.lowercaseString;
    NSString *host = parts.host.lowercaseString;
    if (!([scheme isEqualToString:@"http"] || [scheme isEqualToString:@"https"]) || host.length == 0) return nil;
    NSInteger port = parts.port ? parts.port.integerValue : ([scheme isEqualToString:@"https"] ? 443 : 80);
    return [NSString stringWithFormat:@"%@://%@:%ld", scheme, host, (long)port];
}

- (void)showBackupModelSettings:(id)sender {
    NSDictionary *settings = self.modelSettings;
    NSDictionary *profiles = [settings[@"profiles"] isKindOfClass:[NSDictionary class]] ? settings[@"profiles"] : nil;
    NSString *primaryID = [settings[@"active_high"] isKindOfClass:[NSString class]] ? settings[@"active_high"] : nil;
    NSDictionary *primary = [profiles[primaryID] isKindOfClass:[NSDictionary class]] ? profiles[primaryID] : nil;
    if (!primary) {
        [self sendEvent:@{@"type": @"model_settings_get"}];
        [self appendChatLine:@"Muse · 请先配置主用高阶模型。"];
        return;
    }
    NSString *primaryOrigin = [self modelOrigin:primary[@"endpoint"]];
    NSPopUpButton *picker = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(0, 0, 410, 28) pullsDown:NO];
    [picker addItemWithTitle:@"无备用模型"];
    picker.lastItem.representedObject = @"";
    for (NSString *profileID in [[profiles allKeys] sortedArrayUsingSelector:@selector(compare:)]) {
        if ([profileID isEqualToString:primaryID]) continue;
        NSDictionary *candidate = profiles[profileID];
        if (![candidate isKindOfClass:[NSDictionary class]]) continue;
        NSString *origin = [self modelOrigin:candidate[@"endpoint"]];
        if (!primaryOrigin || ![origin isEqualToString:primaryOrigin] ||
            ![candidate[@"protocol"] isEqualToString:primary[@"protocol"]]) continue;
        [picker addItemWithTitle:[NSString stringWithFormat:@"%@ · %@", profileID, candidate[@"model"] ?: @"模型待配置"]];
        picker.lastItem.representedObject = profileID;
    }
    NSString *saved = [settings[@"backup_high"] isKindOfClass:[NSString class]] ? settings[@"backup_high"] : @"";
    for (NSMenuItem *item in picker.itemArray) if ([item.representedObject isEqualToString:saved]) {
        [picker selectItem:item];
        break;
    }
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"备用高阶模型";
    alert.informativeText = [NSString stringWithFormat:
        @"主用：%@。只有同来源、同协议的备用配置才会在主用可用性故障时尝试接替一次；备用还需独立密钥、已确认价格和可用预算。不同来源的 Provider 需要你手动切换主用。",
        primaryID];
    alert.accessoryView = picker;
    [alert addButtonWithTitle:@"保存"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] != NSAlertFirstButtonReturn) return;
    NSMutableDictionary *updated = [settings mutableCopy];
    updated[@"backup_high"] = picker.selectedItem.representedObject ?: @"";
    [self sendEvent:@{@"type": @"model_settings_set", @"settings": updated}];
}

- (void)showReasoningSettings:(id)sender {
    NSString *profileID = [self.modelSettings[@"active_high"] isKindOfClass:[NSString class]] ? self.modelSettings[@"active_high"] : nil;
    if (profileID.length == 0) {
        [self sendEvent:@{@"type": @"model_settings_get"}];
        [self appendChatLine:@"Muse · 请先配置高阶模型，再选择其支持的推理强度。"];
        return;
    }
    self.reasoningDialogRequested = YES;
    [self sendEvent:@{@"type": @"model_capabilities_get", @"profile_id": profileID}];
}

- (void)showReasoningOptions:(NSDictionary *)capabilities {
    NSString *profileID = capabilities[@"profile_id"];
    NSArray *supported = [capabilities[@"reasoning_efforts"] isKindOfClass:[NSArray class]] ? capabilities[@"reasoning_efforts"] : @[];
    if (![profileID isKindOfClass:[NSString class]] || supported.count == 0) {
        NSAlert *unknown = [[NSAlert alloc] init];
        unknown.messageText = @"该模型未确认原生强度参数";
        unknown.informativeText = @"Muse 不会用提示词伪装推理强度。请检查模型名称与协议，或保留模型默认值。";
        [unknown addButtonWithTitle:@"知道了"];
        [unknown runModal];
        return;
    }
    NSPopUpButton *picker = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(0, 0, 390, 28) pullsDown:NO];
    [picker addItemWithTitle:@"模型默认值"];
    picker.lastItem.representedObject = @"";
    NSDictionary *effortLabels = @{@"minimal": @"极简", @"low": @"低", @"medium": @"中", @"high": @"高",
                                   @"xhigh": @"超高", @"max": @"最大", @"ultra": @"极致", @"none": @"关闭"};
    for (NSString *effort in supported) {
        if (![effort isKindOfClass:[NSString class]]) continue;
        NSString *label = effortLabels[effort] ?: effort;
        [picker addItemWithTitle:[NSString stringWithFormat:@"%@ (%@)", label, effort]];
        picker.lastItem.representedObject = effort;
    }
    NSString *current = self.modelSettings[@"selected_reasoning_effort"][profileID];
    for (NSMenuItem *item in picker.itemArray) if ([item.representedObject isEqualToString:current]) {
        [picker selectItem:item];
        break;
    }
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"模型推理强度";
    alert.informativeText = [NSString stringWithFormat:@"%@ · %@。仅显示此协议和模型已核对的原生取值；实际请求会按选择发送。",
                             capabilities[@"model"] ?: @"模型", capabilities[@"protocol"] ?: @"协议"];
    alert.accessoryView = picker;
    [alert addButtonWithTitle:@"保存"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] != NSAlertFirstButtonReturn) return;
    NSMutableDictionary *settings = [self.modelSettings mutableCopy];
    NSMutableDictionary *selected = [settings[@"selected_reasoning_effort"] isKindOfClass:[NSDictionary class]] ?
        [settings[@"selected_reasoning_effort"] mutableCopy] : [NSMutableDictionary dictionary];
    NSString *effort = picker.selectedItem.representedObject;
    if (effort.length > 0) selected[profileID] = effort;
    else [selected removeObjectForKey:profileID];
    settings[@"selected_reasoning_effort"] = selected;
    [self sendEvent:@{@"type": @"model_settings_set", @"settings": settings}];
}

- (void)showHighProviderSecurity:(id)sender {
    NSDictionary *settings = self.modelSettings;
    NSDictionary *profiles = [settings[@"profiles"] isKindOfClass:[NSDictionary class]] ? settings[@"profiles"] : nil;
    NSString *profileID = [settings[@"active_high"] isKindOfClass:[NSString class]] ? settings[@"active_high"] : nil;
    NSDictionary *profile = [profiles[profileID] isKindOfClass:[NSDictionary class]] ? profiles[profileID] : nil;
    NSString *endpoint = [profile[@"endpoint"] isKindOfClass:[NSString class]] ? profile[@"endpoint"] : nil;
    NSString *model = [profile[@"model"] isKindOfClass:[NSString class]] ? profile[@"model"] : nil;
    NSURLComponents *url = [NSURLComponents componentsWithString:endpoint ?: @""];
    if (profileID.length == 0 || model.length == 0 || url.scheme.length == 0 || url.host.length == 0) {
        [self sendEvent:@{@"type": @"model_settings_get"}];
        NSAlert *missing = [[NSAlert alloc] init];
        missing.messageText = @"先配置高阶模型";
        missing.informativeText = @"请先在“模型与预算设置”中填写高阶模型、协议与端点。纯本地使用无需密钥。";
        [missing addButtonWithTitle:@"知道了"];
        [missing runModal];
        return;
    }
    if ([url.path isEqualToString:@"/v1"] || [url.path isEqualToString:@"/v1/"]) {
        NSAlert *incomplete = [[NSAlert alloc] init];
        incomplete.messageText = @"先补全高阶请求 URL";
        incomplete.informativeText = @"当前是 API 基础地址；请在“模型与预算设置”中填写与你所选协议对应的完整请求路径，然后再配置密钥与价格。";
        [incomplete addButtonWithTitle:@"知道了"];
        [incomplete runModal];
        return;
    }
    url.scheme = url.scheme.lowercaseString;
    url.host = url.host.lowercaseString;
    url.port = url.port ?: ([url.scheme isEqualToString:@"https"] ? @443 : @80);
    url.path = @"";
    url.query = nil;
    url.fragment = nil;
    url.user = nil;
    url.password = nil;
    NSString *origin = url.string;
    NSDictionary *prices = [self.pricingStatus[@"prices"] isKindOfClass:[NSDictionary class]] ? self.pricingStatus[@"prices"] : @{};
    NSDictionary *saved = [prices[profileID] isKindOfClass:[NSDictionary class]] ? prices[profileID] : @{};
    NSView *form = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 500, 245)];
    [form addSubview:[self label:[NSString stringWithFormat:@"%@ · %@ · %@", profileID, model, origin]
                           frame:NSMakeRect(0, 215, 500, 22) size:12 color:[NSColor secondaryLabelColor]]];
    [form addSubview:[self label:@"API 密钥（留空则保持现有密钥）" frame:NSMakeRect(0, 187, 500, 19) size:11 color:nil]];
    NSSecureTextField *secret = [[NSSecureTextField alloc] initWithFrame:NSMakeRect(0, 159, 500, 27)];
    secret.placeholderString = @"只写入本机钥匙串，不进入记忆或日志";
    secret.accessibilityTitle = @"高阶 API 密钥";
    [form addSubview:secret];
    NSTextField *inputRate = [self settingsField:@"输入价 · 元 / 百万 token" value:saved[@"input_cny_per_million"]
                                              x:0 y:95 width:242 parent:form];
    NSTextField *outputRate = [self settingsField:@"输出价 · 元 / 百万 token" value:saved[@"output_cny_per_million"]
                                               x:258 y:95 width:242 parent:form];
    NSTextField *source = [self settingsField:@"价格来源与核对日期" value:saved[@"source"]
                                         x:0 y:40 width:500 parent:form];
    NSDictionary *budget = [self.pricingStatus[@"budget"] isKindOfClass:[NSDictionary class]] ? self.pricingStatus[@"budget"] : nil;
    NSString *budgetText = budget ? [NSString stringWithFormat:@"本轮上限 ¥%.2f · 余额 ¥%.2f · 未知价请求阻止",
                            [budget[@"limit_micros"] doubleValue] / 1000000.0,
                            [budget[@"remaining_micros"] doubleValue] / 1000000.0] :
                            @"预算读取中 · 未知价请求阻止";
    [form addSubview:[self label:budgetText frame:NSMakeRect(0, 7, 500, 21) size:11 color:[NSColor secondaryLabelColor]]];
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"高阶模型密钥与价格";
    alert.informativeText = @"密钥仅经应用私有管道送入本机钥匙串。价格由你核对后填写；未确认价格前远程调用保持阻止。";
    alert.accessoryView = form;
    [alert addButtonWithTitle:@"保存"];
    [alert addButtonWithTitle:@"取消"];
    alert.window.initialFirstResponder = secret;
    if ([alert runModal] != NSAlertFirstButtonReturn) { secret.stringValue = @""; return; }
    NSString *input = [inputRate.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    NSString *output = [outputRate.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    NSString *priceSource = [source.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    BOOL anyPrice = input.length > 0 || output.length > 0 || priceSource.length > 0;
    NSRegularExpression *decimal = [NSRegularExpression regularExpressionWithPattern:@"^[0-9]+(\\.[0-9]{1,6})?$" options:0 error:nil];
    if (anyPrice && (input.length == 0 || output.length == 0 || priceSource.length == 0 ||
                     [decimal numberOfMatchesInString:input options:0 range:NSMakeRange(0, input.length)] != 1 ||
                     [decimal numberOfMatchesInString:output options:0 range:NSMakeRange(0, output.length)] != 1)) {
        secret.stringValue = @"";
        NSAlert *invalid = [[NSAlert alloc] init];
        invalid.messageText = @"价格尚未保存";
        invalid.informativeText = @"请同时填写输入价、输出价和价格来源；价格使用非负十进制元/百万 token。密钥也未发送。";
        [invalid addButtonWithTitle:@"知道了"];
        [invalid runModal];
        return;
    }
    if (secret.stringValue.length > 0) {
        [self sendEvent:@{@"type": @"model_secret_set", @"profile_id": profileID, @"secret": secret.stringValue}];
    }
    secret.stringValue = @"";
    if (anyPrice) {
        [self sendEvent:@{@"type": @"model_pricing_set", @"profile_id": profileID, @"model": model,
                          @"origin": origin, @"input_cny_per_million": input,
                          @"output_cny_per_million": output, @"source": priceSource, @"confirmed": @YES}];
    }
    [self sendEvent:@{@"type": @"model_pricing_get"}];
}

- (void)showMemorySettings:(id)sender {
    if (![self.memorySettings isKindOfClass:[NSDictionary class]]) {
        [self sendEvent:@{@"type": @"memory_settings_get"}];
        [self appendLog:@"记忆设置正在载入，请稍后再打开。"];
        return;
    }
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"本机记忆记录";
    alert.informativeText = [NSString stringWithFormat:@"当前范围：%@ / %@。关闭记录不会删除已有记忆。聊天默认只引用本机记忆；其他账号的已核验目标结果由你单独选择。",
                             self.memorySettings[@"scope"] ?: @"personal", self.memorySettings[@"account_scope"] ?: @"local"];
    NSView *form = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 420, 105)];
    NSButton *recording = [NSButton checkboxWithTitle:@"在当前范围记录新记忆" target:nil action:nil];
    recording.frame = NSMakeRect(0, 72, 420, 28);
    recording.state = [self.memorySettings[@"recording"] boolValue] ? NSControlStateValueOn : NSControlStateValueOff;
    [form addSubview:recording];
    [form addSubview:[self label:@"聊天可引用的其他账号已核验目标结果" frame:NSMakeRect(0, 45, 420, 22) size:12 color:nil]];
    NSPopUpButton *otherScope = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(0, 10, 420, 28) pullsDown:NO];
    [otherScope addItemWithTitle:@"不纳入其他账号（默认）"];
    otherScope.lastItem.representedObject = @"";
    for (NSString *scope in self.availableGoalResultScopes) {
        if (![scope isKindOfClass:[NSString class]] || [scope isEqualToString:@"local"]) continue;
        [otherScope addItemWithTitle:scope];
        otherScope.lastItem.representedObject = scope;
        if ([scope isEqualToString:self.selectedGoalResultScope]) [otherScope selectItem:otherScope.lastItem];
    }
    [form addSubview:otherScope];
    alert.accessoryView = form;
    [alert addButtonWithTitle:@"保存"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] == NSAlertFirstButtonReturn) {
        NSString *selected = otherScope.selectedItem.representedObject;
        self.selectedGoalResultScope = [selected isKindOfClass:[NSString class]] ? selected : @"";
        [self sendEvent:@{@"type": @"memory_settings_set", @"scope": self.memorySettings[@"scope"] ?: @"personal",
                          @"account_scope": self.memorySettings[@"account_scope"] ?: @"local",
                          @"enabled": @((BOOL)(recording.state == NSControlStateValueOn))}];
    }
}

- (void)requestMemoryList:(id)sender { [self sendEvent:@{@"type": @"memory_list"}]; }

- (void)showClaimList:(NSArray *)claims {
    if (claims.count == 0) {
        NSAlert *empty = [[NSAlert alloc] init];
        empty.messageText = @"还没有带来源的记忆";
        empty.informativeText = @"已核验的目标结果会在这里形成事实、声称或推测。原有聊天记忆仍可单独管理。";
        [empty addButtonWithTitle:@"查看原有记忆"];
        [empty addButtonWithTitle:@"关闭"];
        if ([empty runModal] == NSAlertFirstButtonReturn) [self requestMemoryList:nil];
        return;
    }
    NSPopUpButton *picker = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(0, 0, 480, 28) pullsDown:NO];
    for (NSDictionary *document in claims) {
        NSDictionary *payload = [document[@"payload"] isKindOfClass:[NSDictionary class]] ? document[@"payload"] : @{};
        NSString *value = [payload[@"value"] isKindOfClass:[NSString class]] ? payload[@"value"] : @"";
        NSString *summary = [value substringToIndex:MIN((NSUInteger)65, value.length)];
        [picker addItemWithTitle:[NSString stringWithFormat:@"%@ · %@", payload[@"epistemic_type"] ?: @"记忆", summary]];
        picker.lastItem.representedObject = document[@"id"];
    }
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"带来源的记忆";
    alert.informativeText = @"请选择一条查看来源、时间和事实类型；可更正、固定或删除。";
    alert.accessoryView = picker;
    [alert addButtonWithTitle:@"查看"];
    [alert addButtonWithTitle:@"原有记忆"];
    [alert addButtonWithTitle:@"关闭"];
    NSModalResponse choice = [alert runModal];
    if (choice == NSAlertFirstButtonReturn && [picker.selectedItem.representedObject isKindOfClass:[NSString class]]) {
        [self sendEvent:@{@"type": @"memory_claim_get", @"claim_id": picker.selectedItem.representedObject}];
    } else if (choice == NSAlertSecondButtonReturn) {
        [self requestMemoryList:nil];
    }
}

- (void)showClaimDetails:(NSDictionary *)claim {
    NSDictionary *document = [claim[@"document"] isKindOfClass:[NSDictionary class]] ? claim[@"document"] : nil;
    NSDictionary *payload = [document[@"payload"] isKindOfClass:[NSDictionary class]] ? document[@"payload"] : nil;
    NSString *claimID = [document[@"id"] isKindOfClass:[NSString class]] ? document[@"id"] : nil;
    if (!payload || claimID.length == 0) return;
    NSDictionary *labels = @{@"fact": @"已核验事实", @"user_statement": @"用户说法",
                             @"external_claim": @"外部声称", @"inference": @"推测"};
    NSMutableArray<NSString *> *lines = [NSMutableArray arrayWithObjects:
        payload[@"value"] ?: @"", [NSString stringWithFormat:@"类型：%@ · 观察时间：%@",
                              labels[payload[@"epistemic_type"]] ?: @"未分类", payload[@"observed_at"] ?: @"未知"], nil];
    for (NSDictionary *source in claim[@"sources"]) {
        if (![source isKindOfClass:[NSDictionary class]]) continue;
        [lines addObject:[NSString stringWithFormat:@"来源：%@ · %@", source[@"locator"] ?: @"未知",
                          source[@"observed_at"] ?: @"时间未知"]];
    }
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = [claim[@"pinned"] boolValue] ? @"已固定的记忆" : @"记忆详情";
    alert.informativeText = [lines componentsJoinedByString:@"\n\n"];
    [alert addButtonWithTitle:@"更正"];
    [alert addButtonWithTitle:[claim[@"pinned"] boolValue] ? @"取消固定" : @"固定"];
    [alert addButtonWithTitle:@"删除"];
    [alert addButtonWithTitle:@"关闭"];
    NSModalResponse choice = [alert runModal];
    if (choice == NSAlertFirstButtonReturn) {
        NSAlert *edit = [[NSAlert alloc] init];
        edit.messageText = @"更正这条记忆";
        edit.informativeText = @"更正后保留来源与修订记录，并标记为你的说法。";
        NSTextField *content = [[NSTextField alloc] initWithFrame:NSMakeRect(0, 0, 480, 29)];
        content.stringValue = payload[@"value"] ?: @"";
        edit.accessoryView = content;
        [edit addButtonWithTitle:@"保存更正"];
        [edit addButtonWithTitle:@"取消"];
        if ([edit runModal] == NSAlertFirstButtonReturn && content.stringValue.length > 0) {
            [self sendEvent:@{@"type": @"memory_claim_correct", @"claim_id": claimID,
                              @"content": content.stringValue}];
        }
    } else if (choice == NSAlertSecondButtonReturn) {
        [self sendEvent:@{@"type": @"memory_claim_pin", @"claim_id": claimID,
                          @"pinned": @((BOOL)(![claim[@"pinned"] boolValue]))}];
    } else if (choice == NSAlertThirdButtonReturn) {
        NSAlert *confirm = [[NSAlert alloc] init];
        confirm.messageText = @"删除这条记忆？";
        confirm.informativeText = @"删除会阻止相同来源内容在重新索引时回流。";
        [confirm addButtonWithTitle:@"删除"];
        [confirm addButtonWithTitle:@"取消"];
        if ([confirm runModal] == NSAlertFirstButtonReturn) {
            [self sendEvent:@{@"type": @"memory_claim_delete", @"claim_id": claimID}];
        }
    }
}

- (void)memoryRecordSelected:(id)sender {
    NSNumber *recordID = self.memoryRecordPicker.selectedItem.representedObject;
    for (NSDictionary *record in self.memoryRecords) {
        if ([record[@"id"] isEqual:recordID]) {
            self.memoryRecordEditor.string = record[@"content"] ?: @"";
            return;
        }
    }
}

- (void)showMemoryRecords:(NSArray<NSDictionary *> *)records {
    self.memoryRecords = records;
    if (records.count == 0) {
        NSAlert *empty = [[NSAlert alloc] init];
        empty.messageText = @"当前范围暂无记忆";
        empty.informativeText = @"新的对话或由你选择的文件夹内容会出现在这里。";
        [empty runModal];
        return;
    }
    NSView *view = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 620, 250)];
    self.memoryRecordPicker = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(0, 217, 620, 28) pullsDown:NO];
    self.memoryRecordPicker.target = self;
    self.memoryRecordPicker.action = @selector(memoryRecordSelected:);
    for (NSDictionary *record in records) {
        NSString *content = [record[@"content"] isKindOfClass:[NSString class]] ? record[@"content"] : @"";
        NSString *summary = [content substringToIndex:MIN((NSUInteger)55, content.length)];
        NSString *label = [NSString stringWithFormat:@"#%@ %@ %@ · %@", record[@"id"] ?: @"?",
                           [record[@"pinned"] boolValue] ? @"📌" : @"", record[@"kind"] ?: @"记忆", summary];
        [self.memoryRecordPicker addItemWithTitle:label];
        self.memoryRecordPicker.lastItem.representedObject = record[@"id"];
    }
    [view addSubview:self.memoryRecordPicker];
    NSScrollView *scroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(0, 0, 620, 205)];
    scroll.hasVerticalScroller = YES;
    self.memoryRecordEditor = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 620, 205)];
    self.memoryRecordEditor.font = [NSFont systemFontOfSize:13];
    self.memoryRecordEditor.verticallyResizable = YES;
    self.memoryRecordEditor.textContainer.widthTracksTextView = YES;
    scroll.documentView = self.memoryRecordEditor;
    [view addSubview:scroll];
    [self memoryRecordSelected:nil];
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"管理本机记忆";
    alert.informativeText = @"可在下方修正内容、固定或遗忘。遗忘会从当前检索范围移除，并防止所选文件被自动重新索引。";
    alert.accessoryView = view;
    [alert addButtonWithTitle:@"保存更正"];
    [alert addButtonWithTitle:@"固定/取消固定"];
    [alert addButtonWithTitle:@"遗忘"];
    [alert addButtonWithTitle:@"关闭"];
    NSModalResponse choice = [alert runModal];
    NSNumber *recordID = self.memoryRecordPicker.selectedItem.representedObject;
    if (![recordID isKindOfClass:[NSNumber class]]) return;
    if (choice == NSAlertFirstButtonReturn) {
        NSString *corrected = [self.memoryRecordEditor.string stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if (corrected.length > 0) [self sendEvent:@{@"type": @"memory_correct", @"id": recordID, @"content": corrected}];
    } else if (choice == NSAlertSecondButtonReturn) {
        NSDictionary *selected = nil;
        for (NSDictionary *record in records) if ([record[@"id"] isEqual:recordID]) { selected = record; break; }
        [self sendEvent:@{@"type": @"memory_pin", @"id": recordID, @"pinned": @((BOOL)(![selected[@"pinned"] boolValue]))}];
    } else if (choice == NSAlertThirdButtonReturn) {
        NSAlert *confirm = [[NSAlert alloc] init];
        confirm.messageText = @"确认遗忘这条记忆？";
        confirm.informativeText = @"当前内容将从本机记忆检索中移除。";
        [confirm addButtonWithTitle:@"遗忘"];
        [confirm addButtonWithTitle:@"取消"];
        if ([confirm runModal] == NSAlertFirstButtonReturn) [self sendEvent:@{@"type": @"memory_delete", @"id": recordID}];
    }
}

- (void)showProactivitySettings:(id)sender {
    if (![self.proactivitySettings isKindOfClass:[NSDictionary class]]) {
        [self sendEvent:@{@"type": @"proactivity_settings_get"}];
        [self appendLog:@"主动通知设置正在载入，请稍后再打开。"];
        return;
    }
    NSView *form = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 450, 130)];
    NSButton *enabled = [NSButton checkboxWithTitle:@"允许长期目标主动通知" target:nil action:nil];
    enabled.frame = NSMakeRect(0, 100, 420, 24);
    enabled.state = [self.proactivitySettings[@"enabled"] boolValue] ? NSControlStateValueOn : NSControlStateValueOff;
    [form addSubview:enabled];
    NSButton *complete = [NSButton checkboxWithTitle:@"完成时通知" target:nil action:nil];
    complete.frame = NSMakeRect(0, 70, 200, 24);
    complete.state = [self.proactivitySettings[@"notify_on_completion"] boolValue] ? NSControlStateValueOn : NSControlStateValueOff;
    [form addSubview:complete];
    NSButton *decision = [NSButton checkboxWithTitle:@"需要决定时通知" target:nil action:nil];
    decision.frame = NSMakeRect(210, 70, 220, 24);
    decision.state = [self.proactivitySettings[@"notify_on_need_decision"] boolValue] ? NSControlStateValueOn : NSControlStateValueOff;
    [form addSubview:decision];
    NSTextField *interval = [self settingsField:@"同一目标通知最短间隔（秒）" value:[self.proactivitySettings[@"minimum_interval_seconds"] description]
                                                  x:0 y:10 width:220 parent:form];
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"Muse 主动通知";
    alert.informativeText = @"关闭通知不会停止已批准目标；目标状态仍在应用内更新。每个计划中的通知规则也会单独生效。";
    alert.accessoryView = form;
    [alert addButtonWithTitle:@"保存"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] == NSAlertFirstButtonReturn) {
        [self sendEvent:@{@"type": @"proactivity_settings_set", @"settings": @{
            @"enabled": @((BOOL)(enabled.state == NSControlStateValueOn)),
            @"notify_on_completion": @((BOOL)(complete.state == NSControlStateValueOn)),
            @"notify_on_need_decision": @((BOOL)(decision.state == NSControlStateValueOn)),
            @"minimum_interval_seconds": @(interval.integerValue),
        }}];
    }
}

- (void)showBriefSettings:(id)sender {
    if (![self.briefSettings isKindOfClass:[NSDictionary class]]) {
        [self sendEvent:@{@"type": @"brief_settings_get"}];
        [self appendChatLine:@"Muse · 简报设置正在读取，请稍后再打开。"];
        return;
    }
    NSView *form = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 440, 190)];
    [form addSubview:[self label:@"简报时间" frame:NSMakeRect(0, 160, 170, 20) size:12 color:nil]];
    NSPopUpButton *mode = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(175, 156, 250, 27) pullsDown:NO];
    [mode addItemsWithTitles:@[@"关闭", @"早上 08:00", @"晚上 20:00", @"自定时间"]];
    NSArray *values = @[@"off", @"morning", @"evening", @"custom"];
    NSUInteger selection = [values indexOfObject:self.briefSettings[@"brief_mode"] ?: @"off"];
    [mode selectItemAtIndex:(selection == NSNotFound ? 0 : selection)];
    [form addSubview:mode];
    NSTextField *clock = [self settingsField:@"自定时间（HH:MM）" value:self.briefSettings[@"brief_local_time"]
                                       x:0 y:95 width:210 parent:form];
    NSString *quietStart = [self.briefSettings[@"quiet_start"] isKindOfClass:[NSString class]] ? self.briefSettings[@"quiet_start"] : @"";
    NSString *quietEnd = [self.briefSettings[@"quiet_end"] isKindOfClass:[NSString class]] ? self.briefSettings[@"quiet_end"] : @"";
    NSTextField *start = [self settingsField:@"安静时段开始（可留空）" value:quietStart x:0 y:35 width:210 parent:form];
    NSTextField *end = [self settingsField:@"安静时段结束（可留空）" value:quietEnd x:230 y:35 width:210 parent:form];
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"每日简报";
    alert.informativeText = @"简报只汇总已核验的目标更新和待你决定的事项；无变化不会编造进度。首次开启不补发此前结果。";
    alert.accessoryView = form;
    [alert addButtonWithTitle:@"保存"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] != NSAlertFirstButtonReturn) return;
    NSString *custom = [clock.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    NSString *from = [start.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    NSString *until = [end.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    NSRegularExpression *time = [NSRegularExpression regularExpressionWithPattern:@"^([01][0-9]|2[0-3]):[0-5][0-9]$" options:0 error:nil];
    BOOL validCustom = [time numberOfMatchesInString:custom options:0 range:NSMakeRange(0, custom.length)] == 1;
    BOOL validQuiet = (from.length == 0 && until.length == 0) ||
        (from.length > 0 && until.length > 0 &&
         [time numberOfMatchesInString:from options:0 range:NSMakeRange(0, from.length)] == 1 &&
         [time numberOfMatchesInString:until options:0 range:NSMakeRange(0, until.length)] == 1);
    if (!validCustom || !validQuiet) {
        NSAlert *invalid = [[NSAlert alloc] init];
        invalid.messageText = @"简报时间未保存";
        invalid.informativeText = @"时间请用 HH:MM；安静时段需同时填写开始与结束，或同时留空。";
        [invalid addButtonWithTitle:@"知道了"];
        [invalid runModal];
        return;
    }
    [self sendEvent:@{@"type": @"brief_settings_set", @"settings": @{
        @"brief_mode": values[mode.indexOfSelectedItem], @"brief_local_time": custom,
        @"quiet_start": from.length > 0 ? from : [NSNull null],
        @"quiet_end": until.length > 0 ? until : [NSNull null]}}];
}

- (void)indexMemory:(id)sender {
    NSOpenPanel *panel = [NSOpenPanel openPanel];
    panel.canChooseFiles = NO;
    panel.canChooseDirectories = YES;
    panel.allowsMultipleSelection = NO;
    panel.prompt = @"加入记忆";
    [panel beginWithCompletionHandler:^(NSModalResponse response) {
        if (response != NSModalResponseOK || panel.URL.path.length == 0) return;
        dispatch_async(dispatch_get_main_queue(), ^{
            self.memoryStatus.stringValue = @"记忆：索引中…";
            [self sendEvent:@{@"type": @"memory_index_folder", @"path": panel.URL.path}];
        });
    }];
}

- (void)selectWatchedFolder:(id)sender {
    NSOpenPanel *panel = [NSOpenPanel openPanel];
    panel.canChooseFiles = NO;
    panel.canChooseDirectories = YES;
    panel.allowsMultipleSelection = NO;
    panel.prompt = @"授权监控此目录";
    [panel beginWithCompletionHandler:^(NSModalResponse response) {
        if (response != NSModalResponseOK || panel.URL.path.length == 0) return;
        dispatch_async(dispatch_get_main_queue(), ^{
            [self sendEvent:@{@"type": @"watch_folder_set", @"path": panel.URL.path, @"approved": @YES}];
        });
    }];
}

- (void)revokeWatchedFolder:(id)sender {
    if (self.watches.count == 0) {
        [self sendEvent:@{@"type": @"watch_folder_list"}];
        [self appendLog:@"当前没有已授权监控目录，或列表正在载入。"];
        return;
    }
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"撤销文件夹监控";
    alert.informativeText = @"撤销后停止从该目录产生新事件；已保存的目标计划不会因此获得其他目录权限。";
    NSPopUpButton *picker = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(0, 0, 500, 30) pullsDown:NO];
    for (NSDictionary *watch in self.watches) {
        NSString *label = [NSString stringWithFormat:@"%@ · %@", watch[@"resource_ref"] ?: @"?", watch[@"root"] ?: @"?"];
        [picker addItemWithTitle:label];
        picker.lastItem.representedObject = watch[@"resource_ref"];
    }
    alert.accessoryView = picker;
    [alert addButtonWithTitle:@"撤销监控"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] == NSAlertFirstButtonReturn) {
        NSString *ref = picker.selectedItem.representedObject;
        if ([ref isKindOfClass:[NSString class]]) [self sendEvent:@{@"type": @"watch_folder_revoke", @"resource_ref": ref}];
    }
}

- (void)terminalRequest:(id)sender {
    NSString *path = [self.pathField.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if (path.length == 0) return;
    NSString *command = self.commandPopup.selectedItem.title;
    [self appendLog:[NSString stringWithFormat:@"提出终端请求：%@ %@", command, path]];
    [self sendEvent:@{@"type": @"terminal_request", @"argv": @[command, path]}];
}

- (void)confirmTask:(NSButton *)sender {
    [self appendLog:(sender.tag == 1 ? @"用户确认执行" : @"用户拒绝执行")];
    [self sendEvent:@{@"type": @"confirm", @"approved": @(sender.tag == 1)}];
}

- (void)showMessageResult:(NSDictionary *)result {
    NSDictionary *analysis = result[@"analysis"];
    if (![analysis isKindOfClass:[NSDictionary class]]) return;
    NSString *source = result[@"source"] ?: @"unknown";
    NSString *status = result[@"status"] ?: @"unknown";
    self.taskTitle.stringValue = [NSString stringWithFormat:@"消息处理 · %@", source];
    self.taskState.stringValue = status;
    self.taskState.textColor = [status isEqualToString:@"PROCESSED"] ? [NSColor systemGreenColor] : [NSColor systemOrangeColor];
    NSMutableArray<NSString *> *lines = [NSMutableArray array];
    NSString *category = analysis[@"category"] ?: @"unknown";
    NSString *summary = analysis[@"summary"] ?: @"";
    NSString *provenance = analysis[@"provenance"] ?: @"unknown";
    [lines addObject:[NSString stringWithFormat:@"分类：%@", category]];
    [lines addObject:[NSString stringWithFormat:@"摘要：%@", summary]];
    [lines addObject:[NSString stringWithFormat:@"模型来源：%@", provenance]];
    NSArray *todos = analysis[@"todos"];
    if ([todos isKindOfClass:[NSArray class]] && todos.count > 0) {
        [lines addObject:[NSString stringWithFormat:@"待办：%@", [todos componentsJoinedByString:@"；"]]];
    }
    if (result[@"observation_kind"]) [lines addObject:[NSString stringWithFormat:@"观察：%@", result[@"observation_kind"]]];
    if (result[@"action_status"]) [lines addObject:[NSString stringWithFormat:@"动作：%@", result[@"action_status"]]];
    NSDictionary *access = result[@"access_profile"];
    if ([access isKindOfClass:[NSDictionary class]]) {
        [lines addObject:[NSString stringWithFormat:@"访问配置：%@ · 敏感动作%@确认", access[@"label"] ?: access[@"id"] ?: @"unknown", ([result[@"audit"][@"confirmation_required"] boolValue] ? @"需" : @"无需")]];
    }
    NSDictionary *highTier = result[@"high_tier"];
    if ([highTier isKindOfClass:[NSDictionary class]]) [lines addObject:[NSString stringWithFormat:@"高阶通道：%@", highTier[@"status"] ?: @"unknown"]];
    NSDictionary *card = result[@"result_card"];
    if ([card isKindOfClass:[NSDictionary class]]) {
        [lines addObject:[NSString stringWithFormat:@"结果卡：%@ · %@", card[@"status"] ?: @"unknown", card[@"verification"] ?: @"unknown"]];
        if (card[@"adapter_kind"]) [lines addObject:[NSString stringWithFormat:@"宿主适配：%@ · %@", card[@"adapter_kind"], card[@"live_status"] ?: @"unknown"]];
        if (card[@"next_step"]) [lines addObject:[NSString stringWithFormat:@"下一步：%@", card[@"next_step"]]];
    }
    self.stepsView.string = [lines componentsJoinedByString:@"\n"];
    NSDictionary *messageTask = result[@"task_card"];
    NSString *actionStatus = result[@"action_status"] ?: @"none";
    self.pending = [messageTask[@"requires_confirmation"] boolValue]
        && [actionStatus isEqualToString:@"REQUIRES_EXPLICIT_CONFIRMATION"];
    self.approveButton.enabled = self.pending;
    self.rejectButton.enabled = self.pending;
    self.approveButton.hidden = !self.pending;
    self.rejectButton.hidden = !self.pending;
    [self appendLog:[NSString stringWithFormat:@"消息已处理：%@ · 分类：%@ · 模型：%@", status, category, provenance]];
}

- (void)appendChatLine:(NSString *)line {
    if (!self.chatView) return;
    self.welcomeView.hidden = YES;
    NSString *current = self.chatView.string ?: @"";
    NSString *next = current.length > 0 ? [current stringByAppendingFormat:@"\n%@", line] : line;
    if (next.length > 5000) next = [next substringFromIndex:next.length - 5000];
    self.chatView.string = next;
    [self.chatView scrollRangeToVisible:NSMakeRange(self.chatView.string.length, 0)];
}

- (NSString *)adviceForModelError:(NSString *)error {
    NSDictionary<NSString *, NSString *> *advice = @{
        @"resident_model_not_configured": @"本机模型尚未就绪，请在“设置与首启”检查本机模型。",
        @"model_slot_not_configured": @"当前路由的模型或请求 URL 未配置完整，请检查“模型与预算设置”。",
        @"model_endpoint_incomplete": @"高阶模型需要填写完整请求 URL，不能只填到 /v1。请检查协议和模型 ID。",
        @"local_context_too_long": @"这条消息超出本地模型的上下文容量。请缩短消息后重试。",
        @"remote_call_budget_exhausted": @"每日高阶远程调用上限为 0 或已用完，请在“模型与预算设置”核对。",
        @"model_budget_exhausted": @"本次 token 预算不足，请检查模型与预算上限。",
        @"model_money_budget_exhausted": @"本轮费用预算不足，请核对已确认的价格与预算。",
        @"price_confirmation_required": @"高阶模型价格尚未核对确认，请在“高阶密钥与价格”中补全。",
        @"cost_unknown": @"高阶模型价格未知或与当前端点不匹配，请先核对价格。",
        @"keychain_secret_unavailable": @"当前高阶配置缺少可用密钥，请检查本机钥匙串配置。",
        @"keychain_origin_mismatch": @"密钥绑定的服务地址与当前请求地址不同，请核对端点。",
        @"cloud_data_not_allowed": @"尚未允许向高阶端点发送本次资料，请检查模型设置。",
        @"cloud_preview_required": @"远程请求需要先审阅发送内容，再决定是否继续。",
        @"provider_invalid_request": @"模型服务拒绝请求；请核对完整请求 URL、协议与精确模型 ID。",
        @"provider_auth_failed": @"模型服务拒绝身份验证；请核对本机钥匙串中的密钥及服务地址。",
        @"provider_balance_exhausted": @"模型服务端余额不足，请核对服务商账户状态。",
        @"provider_rate_limited": @"模型服务暂时限流，请稍后重试。",
        @"provider_temporarily_unavailable": @"模型服务暂时不可用，请稍后重试。",
        @"provider_overloaded": @"模型服务繁忙，请稍后重试。",
        @"provider_http_error": @"模型服务返回 HTTP 错误，请核对完整请求 URL 与模型 ID。",
        @"invalid_model_response": @"模型服务的响应格式不符合当前协议，请核对协议与请求 URL。",
        @"empty_model_response": @"模型服务返回空内容，请核对模型 ID 后重试。",
        @"URLError": @"无法连接模型服务，请核对完整请求 URL 与网络。",
        @"TimeoutError": @"模型服务响应超时，请稍后重试。",
    };
    return advice[error] ?: @"模型服务未能完成请求；请核对路由、完整请求 URL、精确模型 ID 与服务状态。";
}

- (void)showChatResult:(NSDictionary *)result {
    NSString *reply = result[@"chat_reply"];
    if ([reply isKindOfClass:[NSString class]]) {
        [self appendChatLine:[NSString stringWithFormat:@"Agent：%@", reply]];
        if ([result[@"status"] isEqualToString:@"MODEL_UNAVAILABLE"]) {
            NSDictionary *model = [result[@"model"] isKindOfClass:[NSDictionary class]] ? result[@"model"] : @{};
            NSString *error = [model[@"error"] isKindOfClass:[NSString class]] ? model[@"error"] : @"";
            [self appendChatLine:[NSString stringWithFormat:@"Muse · 无法回答的原因：%@", [self adviceForModelError:error]]];
        }
        self.memoryStatus.stringValue = [NSString stringWithFormat:@"记忆：%@ 条", result[@"memory_count"] ?: @"0"];
        [self appendLog:[NSString stringWithFormat:@"即时对话：%@", result[@"status"] ?: @"unknown"]];
    }
}

- (void)notifyResultCard:(NSDictionary *)card {
    NSString *cardID = card[@"id"];
    if ([cardID isKindOfClass:[NSString class]] && [self.notifiedMailCards containsObject:cardID]) return;
    if ([cardID isKindOfClass:[NSString class]]) [self.notifiedMailCards addObject:cardID];
    BOOL mail = [card[@"source"] isEqualToString:@"qqmail"];
    NSString *title = mail ? @"GOSIM 收到新邮件" : (card[@"title"] ?: @"GOSIM 结果卡");
    NSString *body = mail ? @"请打开应用查看结果卡，再决定是否回复。" : (card[@"next_step"] ?: @"请打开应用查看结果。");
    UNUserNotificationCenter *center = [UNUserNotificationCenter currentNotificationCenter];
    [center getNotificationSettingsWithCompletionHandler:^(UNNotificationSettings *settings) {
        [self recordNotificationStatus:@"SETTINGS_CHECKED" cardID:cardID detail:[NSString stringWithFormat:@"authorization=%ld alert=%ld", (long)settings.authorizationStatus, (long)settings.alertSetting]];
        void (^deliver)(void) = ^{
            UNMutableNotificationContent *content = [[UNMutableNotificationContent alloc] init];
            content.title = title;
            content.body = body;
            content.sound = [UNNotificationSound defaultSound];
            UNNotificationRequest *request = [UNNotificationRequest requestWithIdentifier:cardID ?: [[NSUUID UUID] UUIDString] content:content trigger:nil];
            [center addNotificationRequest:request withCompletionHandler:^(NSError *error) {
                [self recordNotificationStatus:(error ? @"SUBMISSION_FAILED" : @"SUBMITTED_TO_MACOS") cardID:cardID detail:(error ? error.localizedDescription : @"macOS 已接受通知请求，横幅显示仍由系统设置决定")];
            }];
        };
        if (settings.authorizationStatus == UNAuthorizationStatusAuthorized || settings.authorizationStatus == UNAuthorizationStatusProvisional) {
            deliver();
        } else if (settings.authorizationStatus == UNAuthorizationStatusNotDetermined) {
            [self recordNotificationStatus:@"NOTIFICATIONS_NEED_AUTH" cardID:cardID detail:@"可在设置中由用户开启通知；未自动请求系统授权"];
        } else {
            [self recordNotificationStatus:@"AUTHORIZATION_DISABLED" cardID:cardID detail:@"请在系统设置中允许 GOSIM Local Agent 通知"];
        }
    }];
}

- (void)maybeNotifyGoalRun:(NSDictionary *)result card:(NSDictionary *)card {
    if (result[@"notify"] && ![result[@"notify"] boolValue]) return;
    NSString *goalID = card[@"id"];
    NSString *runID = result[@"run_id"];
    if (![goalID isKindOfClass:[NSString class]] || ![goalID hasPrefix:@"goal:"] ||
        ![runID isKindOfClass:[NSString class]] || runID.length == 0) return;
    NSDictionary *global = self.proactivitySettings;
    NSDictionary *policy = self.goalNotifyByID[goalID];
    if (![global[@"enabled"] boolValue] || ![policy isKindOfClass:[NSDictionary class]]) return;
    NSString *runStatus = result[@"status"];
    NSString *reason = [result[@"notification_reason"] isKindOfClass:[NSString class]] ? result[@"notification_reason"] : nil;
    BOOL verifiedRun = [runStatus isEqualToString:@"COMPLETED"] &&
        [result[@"verification"] isEqualToString:@"CHECKS_PASSED"];
    BOOL needsDecision = (reason ? [reason isEqualToString:@"need_decision"] : [runStatus isEqualToString:@"WAITING_USER"]) &&
        [global[@"notify_on_need_decision"] boolValue] && [policy[@"on_need_decision"] boolValue];
    BOOL finished = verifiedRun && (reason ? [reason isEqualToString:@"complete"] : YES) &&
        [global[@"notify_on_completion"] boolValue] && [policy[@"on_complete"] boolValue];
    BOOL majorChange = verifiedRun &&
        (reason ? [reason isEqualToString:@"major_update"] : [result[@"event_id"] isKindOfClass:[NSString class]]) &&
        [policy[@"on_major_update"] boolValue];
    if (!needsDecision && !finished && !majorChange) return;
    NSDate *now = [NSDate date];
    NSDate *previous = self.lastGoalNotificationAt[goalID];
    NSInteger interval = [global[@"minimum_interval_seconds"] integerValue];
    if (previous && [now timeIntervalSinceDate:previous] < interval) return;
    self.lastGoalNotificationAt[goalID] = now;
    NSMutableDictionary *notificationCard = [card mutableCopy];
    notificationCard[@"id"] = [NSString stringWithFormat:@"%@:%@", goalID, runID];
    [self notifyResultCard:notificationCard];
}

- (void)recordNotificationStatus:(NSString *)status cardID:(NSString *)cardID detail:(NSString *)detail {
    dispatch_async(dispatch_get_main_queue(), ^{
        NSDictionary *record = @{@"status": status ?: @"UNKNOWN", @"card_id": cardID ?: @"", @"detail": detail ?: @"", @"time": [[NSDate date] description]};
        NSData *data = [NSJSONSerialization dataWithJSONObject:record options:0 error:nil];
        NSString *path = [self.workspace stringByAppendingPathComponent:@".agent_notification_status.json"];
        if (data) [data writeToFile:path atomically:YES];
        [self appendLog:[NSString stringWithFormat:@"系统通知：%@ · %@", status, detail]];
        if ([status isEqualToString:@"AUTHORIZATION_NOT_GRANTED"] || [status isEqualToString:@"AUTHORIZATION_DISABLED"] || [status isEqualToString:@"NOTIFICATIONS_NEED_AUTH"]) {
            self.notificationStatus.stringValue = @"系统通知未授权 · 请到系统设置开启";
            self.notificationStatus.textColor = [NSColor systemOrangeColor];
        } else if ([status isEqualToString:@"SUBMITTED_TO_MACOS"] || [status isEqualToString:@"NOTIFICATIONS_READY"] || [status isEqualToString:@"FOREGROUND_BANNER_REQUESTED"]) {
            self.notificationStatus.stringValue = @"系统通知已连接";
            self.notificationStatus.textColor = [NSColor systemGreenColor];
        }
    });
}

- (void)userNotificationCenter:(UNUserNotificationCenter *)center willPresentNotification:(UNNotification *)notification withCompletionHandler:(void (^)(UNNotificationPresentationOptions))completionHandler {
    [self recordNotificationStatus:@"FOREGROUND_BANNER_REQUESTED" cardID:notification.request.identifier detail:@"应用在前台，已请求 macOS 显示横幅"];
    completionHandler(UNNotificationPresentationOptionBanner | UNNotificationPresentationOptionSound);
}

- (void)userNotificationCenter:(UNUserNotificationCenter *)center didReceiveNotificationResponse:(UNNotificationResponse *)response withCompletionHandler:(void (^)(void))completionHandler {
    dispatch_async(dispatch_get_main_queue(), ^{ [self showTasks:nil]; });
    completionHandler();
}

- (void)checkPendingMailCard:(NSTimer *)timer {
    if (self.mailBridge.isRunning) {
        NSString *healthPath = [self.workspace stringByAppendingPathComponent:@".qqmail_bridge_health.json"];
        NSData *healthData = [NSData dataWithContentsOfFile:healthPath];
        NSDictionary *health = healthData ? [NSJSONSerialization JSONObjectWithData:healthData options:0 error:nil] : nil;
        NSString *status = [health isKindOfClass:NSDictionary.class] ? health[@"status"] : nil;
        NSDate *modified = [[[NSFileManager defaultManager] attributesOfItemAtPath:healthPath error:nil] fileModificationDate];
        BOOL stale = modified ? -[modified timeIntervalSinceNow] > 75 :
            (self.lastMailStartAttempt && -[self.lastMailStartAttempt timeIntervalSinceNow] > 75);
        self.mailModuleButton.title = stale ? @"QQ 邮箱 · 监听中断" :
                                      [status isEqualToString:@"CONNECTED"] ? @"QQ 邮箱 · 监听中" :
                                      [status isEqualToString:@"ERROR"] ? @"QQ 邮箱 · 连接异常" : @"QQ 邮箱 · 连接中";
        if (stale && (!self.lastMailRestartAttempt || -[self.lastMailRestartAttempt timeIntervalSinceNow] > 90)) {
            NSString *address = [[NSUserDefaults standardUserDefaults] stringForKey:@"QQMailAddress"];
            if (address.length && self.mailAutoConnectAllowed) {
                self.lastMailRestartAttempt = [NSDate date];
                [self appendLog:@"QQ 邮箱监听状态已过期，正在重启本应用的邮箱连接。"];
                [self.mailBridge terminate];
                self.mailBridge = nil;
                [self performSelector:@selector(startRememberedMailBridge) withObject:nil afterDelay:3.0];
            }
        }
    } else {
        self.mailModuleButton.title = self.mailKeychainLookupInProgress ? @"QQ 邮箱 · 恢复连接中" : @"QQ 邮箱 · 未连接";
    }
    self.mailModuleButton.accessibilityTitle = self.mailModuleButton.title;
    NSString *path = [self.workspace stringByAppendingPathComponent:@".agent_mail_reply_state.json"];
    NSData *data = [NSData dataWithContentsOfFile:path];
    id value = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
    NSDictionary *root = [value isKindOfClass:[NSDictionary class]] ? value : nil;
    NSDictionary *pending = [root[@"version"] isEqual:@2]
        ? ([root[@"active"] isKindOfClass:[NSDictionary class]] ? root[@"active"] : nil)
        : root;
    if (![pending isKindOfClass:[NSDictionary class]]) {
        self.mailPanel.hidden = YES;
        self.activeMailCardID = nil;
        self.activeMailState = nil;
        return;
    }
    NSString *state = pending[@"state"];
    NSString *cardID = pending[@"card_id"];
    if (![state isKindOfClass:[NSString class]] || ![cardID isKindOfClass:[NSString class]] || cardID.length == 0) return;
    BOOL sameState = [cardID isEqualToString:self.activeMailCardID] && [state isEqualToString:self.activeMailState];
    NSString *summary = [pending[@"summary"] isKindOfClass:[NSString class]] ? pending[@"summary"] : @"已收到一封邮件。";
    NSString *sender = [pending[@"sender"] isKindOfClass:[NSString class]] ? pending[@"sender"] : @"未知发件人";
    BOOL manualReply = [pending[@"origin"] isEqualToString:@"contact"];
    self.taskTitle.stringValue = manualReply ? @"给联系人回信" : @"QQ 邮箱结果卡";
    self.taskState.stringValue = state;
    self.stepsView.string = [NSString stringWithFormat:@"发件人：%@\n邮件摘要：%@", sender, summary];
    if (sameState) return;
    self.activeMailCardID = cardID;
    self.activeMailState = state;
    [self showTaskPane:nil];
    self.mailPanel.hidden = NO;
    self.mailEditor.hidden = YES;
    self.mailPrimaryButton.hidden = NO;
    self.mailPrimaryButton.enabled = YES;
    self.mailSecondaryButton.hidden = YES;
    self.mailLaterButton.hidden = NO;
    if ([state isEqualToString:@"CHOICE"]) {
        self.mailPrompt.stringValue = manualReply ? @"已选定收件人。请告诉 Agent 想表达什么，发送前仍由你确认。" :
            @"这封邮件需要你的决定。Agent 可以起草，但不会直接发送。";
        self.mailPrimaryButton.title = @"让 Agent 起草";
        self.mailSecondaryButton.hidden = NO;
        if (!manualReply) [self notifyResultCard:@{@"id": cardID, @"source": @"qqmail"}];
    } else if ([state isEqualToString:@"NEEDS_GUIDANCE"]) {
        self.mailPrompt.stringValue = [pending[@"question"] isKindOfClass:[NSString class]] ? pending[@"question"] : @"请告诉我你想表达什么。";
        self.mailEditor.string = @"";
        self.mailEditor.hidden = NO;
        self.mailPrimaryButton.title = @"生成草稿";
    } else if ([state isEqualToString:@"DRAFT_READY"]) {
        self.mailPrompt.stringValue = @"请审阅或修改下面的回复。只有你确认后才会发送。";
        self.mailEditor.string = [pending[@"draft"] isKindOfClass:[NSString class]] ? pending[@"draft"] : @"";
        self.mailEditor.hidden = NO;
        self.mailPrimaryButton.title = @"确认发送";
    } else {
        self.mailPrompt.stringValue = @"已请求发送，正在等待 QQ 邮箱回传结果。";
        self.mailPrimaryButton.hidden = YES;
        self.mailLaterButton.hidden = YES;
    }
}

- (void)mailPrimaryAction:(id)sender {
    if (self.activeMailCardID.length == 0) return;
    if ([self.activeMailState isEqualToString:@"CHOICE"]) {
        [self sendEvent:@{@"type": @"mail_choice", @"card_id": self.activeMailCardID, @"choice": @"reply_suggested"}];
    } else if ([self.activeMailState isEqualToString:@"NEEDS_GUIDANCE"]) {
        NSString *guidance = [self.mailEditor.string stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if (guidance.length == 0) { self.mailPrompt.stringValue = @"请先输入你希望表达的意思。"; return; }
        [self sendEvent:@{@"type": @"mail_guidance", @"card_id": self.activeMailCardID, @"text": guidance}];
    } else if ([self.activeMailState isEqualToString:@"DRAFT_READY"]) {
        NSString *body = [self.mailEditor.string stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if (body.length == 0) { self.mailPrompt.stringValue = @"回复不能为空；请先写好内容。"; return; }
        self.mailPrimaryButton.enabled = NO;
        [self sendEvent:@{@"type": @"mail_reply_content", @"card_id": self.activeMailCardID, @"body": body, @"confirmed": @YES}];
    }
}

- (void)mailWriteAction:(id)sender {
    if (self.activeMailCardID.length == 0 || ![self.activeMailState isEqualToString:@"CHOICE"]) return;
    [self sendEvent:@{@"type": @"mail_choice", @"card_id": self.activeMailCardID, @"choice": @"reply_custom"}];
}

- (void)mailLaterAction:(id)sender {
    if (self.activeMailCardID.length == 0) return;
    [self sendEvent:@{@"type": @"mail_choice", @"card_id": self.activeMailCardID, @"choice": @"skip"}];
}

- (void)showMailContacts:(id)sender {
    if (!self.mailContactsWindow) {
        self.mailContactsWindow = [[NSWindow alloc] initWithContentRect:NSMakeRect(0, 0, 560, 500)
            styleMask:NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable
            backing:NSBackingStoreBuffered defer:NO];
        self.mailContactsWindow.title = @"QQ 邮箱 · 最近来信联系人";
        self.mailContactsWindow.minSize = NSMakeSize(460, 360);
        [self.mailContactsWindow center];
        NSView *content = self.mailContactsWindow.contentView;
        [content addSubview:[self label:@"最近来信联系人" frame:NSMakeRect(18, 455, 390, 28)
                                size:19 color:[NSColor labelColor]]];
        self.mailContactsStatus = [self label:@"正在读取收件箱邮件头…" frame:NSMakeRect(18, 425, 500, 24)
                                        size:12 color:[NSColor secondaryLabelColor]];
        [content addSubview:self.mailContactsStatus];
        [self button:@"刷新" frame:NSMakeRect(460, 450, 80, 30)
              action:@selector(refreshMailContacts:) parent:content];
        self.mailContactsScroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(18, 20, 524, 395)];
        self.mailContactsScroll.hasVerticalScroller = YES;
        self.mailContactsScroll.autoresizingMask = NSViewWidthSizable | NSViewHeightSizable;
        self.mailContactsScroll.documentView = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 506, 395)];
        [content addSubview:self.mailContactsScroll];
    }
    [self.mailContactsWindow makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];
    [self refreshMailContacts:nil];
}

- (void)refreshMailContacts:(id)sender {
    self.mailContactsStatus.stringValue = @"正在读取收件箱邮件头…";
    [self sendEvent:@{@"type": @"mail_contacts_list"}];
}

- (void)renderMailContacts:(NSDictionary *)result {
    NSArray *contacts = [result[@"contacts"] isKindOfClass:NSArray.class] ? result[@"contacts"] : @[];
    self.mailContacts = contacts;
    NSString *status = [result[@"status"] isKindOfClass:NSString.class] ? result[@"status"] : @"REFRESHING";
    self.mailContactsStatus.stringValue = [status isEqualToString:@"READY"] ?
        (contacts.count ? [NSString stringWithFormat:@"最近收件箱有 %lu 位可回复联系人；点击一位开始起草。", (unsigned long)contacts.count] :
                          @"最近 60 封来信中没有可回复的联系人。") :
        @"联系人暂不可用；请确认 QQ 邮箱已连接后刷新。";
    CGFloat rowHeight = 58;
    CGFloat height = MAX(395, contacts.count * rowHeight + 12);
    NSView *rows = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 506, height)];
    for (NSUInteger index = 0; index < contacts.count; index++) {
        NSDictionary *contact = contacts[index];
        if (![contact isKindOfClass:NSDictionary.class]) continue;
        NSString *address = [contact[@"address"] isKindOfClass:NSString.class] ? contact[@"address"] : @"";
        NSString *name = [contact[@"name"] isKindOfClass:NSString.class] ? contact[@"name"] : @"";
        NSString *subject = [contact[@"subject"] isKindOfClass:NSString.class] ? contact[@"subject"] : @"";
        CGFloat y = height - (index + 1) * rowHeight;
        NSString *title = name.length ? [NSString stringWithFormat:@"%@  <%@>", name, address] : address;
        NSButton *row = [self button:title frame:NSMakeRect(8, y + 22, 490, 32)
                               action:@selector(beginReplyToContact:) parent:rows];
        row.tag = (NSInteger)index;
        row.alignment = NSTextAlignmentLeft;
        row.bordered = NO;
        row.accessibilityTitle = [NSString stringWithFormat:@"回复给 %@", address];
        [rows addSubview:[self label:[NSString stringWithFormat:@"最近主题：%@", subject.length ? subject : @"无主题"]
                                frame:NSMakeRect(20, y + 3, 476, 19) size:11 color:[NSColor secondaryLabelColor]]];
    }
    self.mailContactsScroll.documentView = rows;
}

- (void)beginReplyToContact:(NSButton *)sender {
    NSUInteger index = (NSUInteger)sender.tag;
    if (index >= self.mailContacts.count) return;
    NSDictionary *contact = self.mailContacts[index];
    NSString *contactID = contact[@"contact_id"];
    NSString *sourceID = contact[@"source_message_id"];
    if (![contactID isKindOfClass:NSString.class] || ![sourceID isKindOfClass:NSString.class]) return;
    [self.mailContactsWindow orderOut:nil];
    [self.window makeKeyAndOrderFront:nil];
    [self sendEvent:@{@"type": @"mail_reply_start", @"contact_id": contactID,
                      @"source_message_id": sourceID}];
}

- (void)displayActivityEvent:(NSDictionary *)event {
    if (![event[@"bundle_id"] isKindOfClass:[NSString class]] ||
        ![event[@"observed_at"] isKindOfClass:[NSString class]]) return;
    NSString *bundle = event[@"bundle_id"];
    NSString *appName = [bundle isEqualToString:@"com.apple.TextEdit"] ? @"TextEdit" :
        [bundle isEqualToString:@"com.microsoft.edgemac"] ? @"Microsoft Edge" : bundle;
    NSString *action = [event[@"type"] isEqualToString:@"frontmost_snapshot"] ? @"当前前台" : @"切换到前台";
    [self.activityLines addObject:[NSString stringWithFormat:@"%@ · %@ · %@ · NSWorkspace",
                                   event[@"observed_at"], appName, action]];
    while (self.activityLines.count > 100) [self.activityLines removeObjectAtIndex:0];
    self.activityEventsView.string = [self.activityLines componentsJoinedByString:@"\n"];
    [self.activityEventsView scrollRangeToVisible:NSMakeRange(self.activityEventsView.string.length, 0)];
}

- (void)showResult:(NSDictionary *)result {
    NSString *operation = result[@"operation"];
    if ([operation isEqualToString:@"mail_contacts_list"]) {
        [self renderMailContacts:result];
        return;
    }
    if ([operation isEqualToString:@"official_pending_list"]) {
        [self showOfficialPendingList:result];
        return;
    }
    if ([operation isEqualToString:@"official_native_decide"]) {
        [self showTaskPane:nil];
        self.officialDecisionInFlight = NO;
        self.officialPending = nil;
        self.officialPanel.hidden = YES;
        NSString *status = [result[@"status"] isKindOfClass:[NSString class]] ? result[@"status"] : @"BLOCKED";
        BOOL completed = [status isEqualToString:@"COMPLETED"] && [result[@"ok"] boolValue];
        self.taskTitle.stringValue = completed ? @"官方单步执行完成" :
            [status isEqualToString:@"DENIED"] ? @"已拒绝官方单步执行" : @"官方单步请求未完成";
        self.taskState.stringValue = completed ? @"已回读核对" : status;
        self.taskState.textColor = completed ? [NSColor systemGreenColor] :
            [status isEqualToString:@"DENIED"] ? [NSColor secondaryLabelColor] : [NSColor systemRedColor];
        NSDictionary *receipt = [result[@"receipt"] isKindOfClass:[NSDictionary class]] ? result[@"receipt"] : @{};
        self.stepsView.string = completed ? [NSString stringWithFormat:@"请求：%@\n文件：%@\n回读 SHA-256：%@",
            result[@"pending_id"] ?: @"?", receipt[@"relative_path"] ?: @"?",
            result[@"readback_sha256"] ?: @"?"] :
            [NSString stringWithFormat:@"请求：%@\n状态：%@\n原因：%@",
                result[@"pending_id"] ?: @"?", status, result[@"error"] ?: @"由你拒绝或请求已失效"];
        [self appendLog:[NSString stringWithFormat:@"官方单步决定：%@ · %@", status, result[@"pending_id"] ?: @"?"]];
        [self pollOfficialPending:nil];
        return;
    }
    NSString *workerState = result[@"status"];
    if ([workerState isEqualToString:@"WORKSPACE_IN_USE"] ||
        [workerState isEqualToString:@"WORKSPACE_LOCK_FAILED"]) {
        [self.officialPollTimer invalidate];
        self.officialPollTimer = nil;
        self.officialPanel.hidden = YES;
        BOOL inUse = [workerState isEqualToString:@"WORKSPACE_IN_USE"];
        self.workerStatus.stringValue = inUse ? @"工作区已被占用" : @"工作区锁定失败";
        self.workerStatus.textColor = [NSColor systemRedColor];
        self.taskTitle.stringValue = inUse ? @"另一份 Muse 正在运行" : @"工作区无法使用";
        self.taskState.stringValue = @"后台服务未连接";
        self.taskState.textColor = [NSColor systemRedColor];
        self.stepsView.string = inUse ? @"请退出另一份 Muse，然后重新打开此版本。工作区数据没有被本窗口修改。" :
            @"请检查工作区权限后重新打开 Muse。后台服务未连接，本窗口不会处理新任务。";
        [self appendLog:[@"后台服务未连接：" stringByAppendingString:workerState]];
        return;
    }
    if ([result[@"operation"] isEqualToString:@"chat_preview"] &&
        [result[@"request_id"] isEqualToString:self.pendingChatPreviewRequestID]) {
        NSString *status = [result[@"status"] isKindOfClass:[NSString class]] ? result[@"status"] : @"BLOCKED";
        if ([status isEqualToString:@"LOCAL"] && [result[@"ok"] boolValue]) {
            [self finishChatPreviewWithDigest:nil];
            return;
        }
        NSDictionary *destination = [result[@"destination"] isKindOfClass:[NSDictionary class]] ? result[@"destination"] : nil;
        NSDictionary *body = [result[@"request_body"] isKindOfClass:[NSDictionary class]] ? result[@"request_body"] : nil;
        NSDictionary *backupBody = [result[@"backup_request_body"] isKindOfClass:[NSDictionary class]] ? result[@"backup_request_body"] : nil;
        NSString *digest = [result[@"sha256"] isKindOfClass:[NSString class]] ? result[@"sha256"] : nil;
        if ([status isEqualToString:@"PREVIEW"] && [result[@"ok"] boolValue] &&
            destination && body && digest.length == 64) {
            NSData *destinationJSON = [NSJSONSerialization dataWithJSONObject:destination options:NSJSONWritingPrettyPrinted error:nil];
            NSData *bodyJSON = [NSJSONSerialization dataWithJSONObject:body options:NSJSONWritingPrettyPrinted error:nil];
            NSData *backupJSON = backupBody ? [NSJSONSerialization dataWithJSONObject:backupBody options:NSJSONWritingPrettyPrinted error:nil] : nil;
            if (destinationJSON && bodyJSON) {
                NSString *destinationText = [[NSString alloc] initWithData:destinationJSON encoding:NSUTF8StringEncoding];
                NSString *bodyText = [[NSString alloc] initWithData:bodyJSON encoding:NSUTF8StringEncoding];
                NSString *backupText = backupJSON ? [[NSString alloc] initWithData:backupJSON encoding:NSUTF8StringEncoding] : nil;
                NSAlert *alert = [[NSAlert alloc] init];
                alert.messageText = @"确认发送给高阶模型";
                alert.informativeText = [NSString stringWithFormat:@"目的地：%@\n模型：%@。请核对下方完整请求正文。当前仅包含本次输入，不会附带本机记忆；取消则不发送。",
                    destination[@"endpoint"] ?: @"未知", destination[@"model"] ?: @"未知"];
                NSScrollView *scroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(0, 0, 460, 270)];
                scroll.hasVerticalScroller = YES;
                NSTextView *preview = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 460, 270)];
                preview.editable = NO;
                preview.selectable = YES;
                preview.accessibilityTitle = @"完整云端请求预览";
                preview.string = [NSString stringWithFormat:@"目的地与备用配置：\n%@\n\n实际请求正文：\n%@%@",
                    destinationText, bodyText,
                    backupText ? [@"\n\n备用模型请求正文：\n" stringByAppendingString:backupText] : @""];
                scroll.documentView = preview;
                alert.accessoryView = scroll;
                [alert addButtonWithTitle:@"确认发送"];
                [alert addButtonWithTitle:@"取消"];
                if ([alert runModal] == NSAlertFirstButtonReturn) [self finishChatPreviewWithDigest:digest];
                else [self cancelChatPreview];
                return;
            }
        }
        [self cancelChatPreview];
        NSString *message = [result[@"error"] isEqualToString:@"cloud_sensitive_content"] ?
            @"这段输入可能包含敏感信息，云端请求已阻止。请修改输入后重试。" :
            @"请求预览未能完成，消息没有发送。请检查模型设置后重试。";
        [self appendChatLine:[@"Muse · " stringByAppendingString:message]];
        return;
    }
    if ([result[@"operation"] isEqualToString:@"recipe_prepare"] &&
        [result[@"request_id"] isEqualToString:self.pendingTextEditRequestID]) {
        self.pendingTextEditRequestID = nil;
        NSDictionary *recipe = [result[@"recipe"] isKindOfClass:[NSDictionary class]] ? result[@"recipe"] : nil;
        if (![result[@"ok"] boolValue] || ![result[@"status"] isEqualToString:@"PROPOSED"] || !recipe) {
            [self appendChatLine:[NSString stringWithFormat:@"Muse · TextEdit 配方未生成：%@。请确认合成文件已在 TextEdit 中打开且没有未保存修改。",
                                  result[@"error"] ?: @"当前文档无法核对"]];
            return;
        }
        NSMutableArray<NSString *> *observed = [NSMutableArray array];
        for (NSDictionary *step in result[@"observed_steps"]) {
            if (![step isKindOfClass:[NSDictionary class]]) continue;
            [observed addObject:[NSString stringWithFormat:@"%@ · %@", step[@"action"] ?: @"?", step[@"name"] ?: @"?"]];
        }
        [self appendChatLine:[NSString stringWithFormat:@"Muse · 已观察 %@ 的 TextEdit 配方：%@。已准备草稿；只有你批准目标后才会尝试保存。",
                              recipe[@"window_title"] ?: @"合成文件", [observed componentsJoinedByString:@" → "]]];
        NSString *objective = [NSString stringWithFormat:@"请在 TextEdit 中保存合成测试文件 %@，并核对保存后的内容。",
                               recipe[@"relative_path"] ?: @"notes/Muse-Test.txt"];
        [self sendEvent:@{@"type": @"goal_propose", @"request_id": [[NSUUID UUID] UUIDString],
                          @"text": objective, @"recipe": recipe}];
        return;
    }
    if ([result[@"operation"] isEqualToString:@"browser_recipe_prepare"] &&
        [result[@"request_id"] isEqualToString:self.pendingBrowserRecipeRequestID]) {
        self.pendingBrowserRecipeRequestID = nil;
        NSString *objective = self.pendingBrowserGoalText;
        self.pendingBrowserGoalText = nil;
        NSDictionary *recipe = [result[@"browser_recipe"] isKindOfClass:[NSDictionary class]] ? result[@"browser_recipe"] : nil;
        NSArray *controls = [result[@"observed_controls"] isKindOfClass:[NSArray class]] ? result[@"observed_controls"] : nil;
        NSString *digest = [recipe[@"recipe_digest"] isKindOfClass:[NSString class]] ? recipe[@"recipe_digest"] : nil;
        NSSet *keys = [NSSet setWithArray:@[@"query", @"engine", @"max_pages", @"recipe_id", @"recipe_revision",
                                            @"recipe_digest", @"target_bundle_id", @"window_title"]];
        if (![result[@"ok"] boolValue] || ![result[@"status"] isEqualToString:@"PROPOSED"] ||
            !recipe || ![[NSSet setWithArray:recipe.allKeys] isEqualToSet:keys] ||
            digest.length != 64 || !controls || [result[@"side_effects"] boolValue]) {
            [self appendChatLine:[NSString stringWithFormat:@"Muse · Edge 搜索配方未就绪：%@。请检查 Edge 与公开站点后重试。",
                                  result[@"error"] ?: @"观察结果不完整"]];
            return;
        }
        self.browserObservedControls[digest] = controls;
        NSMutableArray<NSString *> *observed = [NSMutableArray array];
        for (NSDictionary *control in controls) {
            if (![control isKindOfClass:[NSDictionary class]]) continue;
            [observed addObject:[NSString stringWithFormat:@"%@ · %@ · %@", control[@"role"] ?: @"?",
                                 control[@"name"] ?: @"?", control[@"action"] ?: @"?"]];
        }
        NSAlert *alert = [[NSAlert alloc] init];
        alert.messageText = @"审阅 Edge 搜索配方";
        alert.informativeText = @"这里只观察到公开搜索控件，尚未提交搜索或执行目标。生成草稿后仍需单独批准。";
        NSScrollView *scroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(0, 0, 470, 235)];
        scroll.hasVerticalScroller = YES;
        NSTextView *preview = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, 470, 235)];
        preview.editable = NO;
        preview.selectable = YES;
        preview.accessibilityTitle = @"Edge 搜索配方预览";
        preview.string = [NSString stringWithFormat:@"搜索词：%@\n站点：%@ · 最多 %@ 页\n应用：%@\n窗口：%@\n观察到的控件：\n%@\n\n配方摘要 SHA-256：%@\n\n目标：%@",
                          recipe[@"query"], recipe[@"engine"], recipe[@"max_pages"],
                          recipe[@"target_bundle_id"], recipe[@"window_title"],
                          [observed componentsJoinedByString:@"\n"], digest, objective ?: @""];
        scroll.documentView = preview;
        alert.accessoryView = scroll;
        [alert addButtonWithTitle:@"生成待批准计划"];
        [alert addButtonWithTitle:@"取消"];
        if ([alert runModal] == NSAlertFirstButtonReturn) {
            [self sendEvent:@{@"type": @"goal_propose", @"request_id": [[NSUUID UUID] UUIDString],
                              @"text": objective ?: @"", @"browser_recipe": recipe}];
            [self appendChatLine:@"Muse · Edge 搜索计划草稿正在生成；批准前不会运行搜索。"];
        } else {
            [self appendChatLine:@"Muse · 已取消生成 Edge 搜索目标；没有搜索或执行。"];
        }
        return;
    }
    NSString *activityStatus = [result[@"status"] isKindOfClass:[NSString class]] ? result[@"status"] : nil;
    if ([activityStatus isEqualToString:@"READY"] && [result[@"source"] isEqualToString:@"NSWorkspace"] &&
        [result[@"enabled"] isKindOfClass:[NSNumber class]]) {
        self.activityEnabled = [result[@"enabled"] boolValue];
        NSArray *bundles = [result[@"bundle_ids"] isKindOfClass:[NSArray class]] ? result[@"bundle_ids"] : @[];
        self.activityTextEdit.state = [bundles containsObject:@"com.apple.TextEdit"] ? NSControlStateValueOn : NSControlStateValueOff;
        self.activityEdge.state = [bundles containsObject:@"com.microsoft.edgemac"] ? NSControlStateValueOn : NSControlStateValueOff;
        self.activityToggle.title = self.activityEnabled ? @"停止观察" : @"开启观察";
        self.activityToggle.accessibilityTitle = self.activityToggle.title;
        self.activityToggle.enabled = YES;
        self.activityTextEdit.enabled = !self.activityEnabled;
        self.activityEdge.enabled = !self.activityEnabled;
        self.activityState.stringValue = self.activityEnabled ? @"正在观察所选应用的前台切换" : @"未开启";
        [self.activityLines removeAllObjects];
        if (self.activityEnabled) for (NSDictionary *event in result[@"recent"]) {
            if ([event isKindOfClass:[NSDictionary class]]) [self displayActivityEvent:event];
        }
        if (self.activityLines.count == 0) self.activityEventsView.string = self.activityEnabled ?
            @"正在等待所选应用的前台切换。" : @"开启后，这里会出现白名单应用的真实前台切换。";
        return;
    }
    if ([activityStatus isEqualToString:@"RUNNING"] && [result[@"source"] isEqualToString:@"NSWorkspace"] &&
        [result[@"bundle_ids"] isKindOfClass:[NSArray class]]) {
        self.activityEnabled = YES;
        self.activityToggle.title = @"停止观察";
        self.activityToggle.accessibilityTitle = self.activityToggle.title;
        self.activityToggle.enabled = YES;
        self.activityTextEdit.enabled = NO;
        self.activityEdge.enabled = NO;
        self.activityState.stringValue = @"正在观察所选应用的前台切换";
        [self sendEvent:@{@"type": @"activity_status"}];
        return;
    }
    if ([activityStatus isEqualToString:@"EVENT"] && [result[@"source"] isEqualToString:@"NSWorkspace"]) {
        if (self.activityEnabled) [self displayActivityEvent:result];
        return;
    }
    if ([activityStatus isEqualToString:@"NO_EVENT"]) return;
    if ([activityStatus isEqualToString:@"DISABLED"] && !result[@"plugin_id"] && self.activityWindow) {
        self.activityEnabled = NO;
        self.activityToggle.title = @"开启观察";
        self.activityToggle.accessibilityTitle = self.activityToggle.title;
        self.activityToggle.enabled = YES;
        self.activityTextEdit.enabled = YES;
        self.activityEdge.enabled = YES;
        self.activityState.stringValue = @"已关闭；本次活动列表已清空";
        [self.activityLines removeAllObjects];
        self.activityEventsView.string = @"开启后，这里会出现白名单应用的真实前台切换。";
        return;
    }
    if ([activityStatus isEqualToString:@"BLOCKED"] &&
        [result[@"error"] isKindOfClass:[NSString class]] && [result[@"error"] hasPrefix:@"activity_"]) {
        self.activityToggle.enabled = YES;
        self.activityState.stringValue = @"活动观察暂不可用；查看活动记录了解原因。";
        [self appendLog:[NSString stringWithFormat:@"活动观察：%@", result[@"error"]]];
        return;
    }
    if ([activityStatus isEqualToString:@"REJECTED"] &&
        [result[@"error"] isKindOfClass:[NSString class]] && [result[@"error"] hasPrefix:@"activity_"]) {
        self.activityToggle.enabled = YES;
        self.activityState.stringValue = @"请重新选择允许观察的应用。";
        [self appendLog:[NSString stringWithFormat:@"活动观察：%@", result[@"error"]]];
        return;
    }
    if ([result[@"claims"] isKindOfClass:[NSArray class]]) {
        [self showClaimList:result[@"claims"]];
        return;
    }
    if ([result[@"claim"] isKindOfClass:[NSDictionary class]]) {
        [self showClaimDetails:result[@"claim"]];
        return;
    }
    if ([result[@"claim_id"] isKindOfClass:[NSString class]] && [result[@"status"] isEqualToString:@"SAVED"]) {
        [self appendChatLine:@"Muse · 记忆变更已保存。"];
        [self sendEvent:@{@"type": @"memory_claim_list"}];
        return;
    }
    if ([result[@"capabilities"] isKindOfClass:[NSDictionary class]]) {
        if (self.reasoningDialogRequested) {
            self.reasoningDialogRequested = NO;
            [self showReasoningOptions:result[@"capabilities"]];
        }
        return;
    }
    if ([result[@"brief_settings"] isKindOfClass:[NSDictionary class]]) {
        self.briefSettings = result[@"brief_settings"];
        return;
    }
    if ([result[@"status"] isEqualToString:@"BRIEF_READY"] &&
        [result[@"brief"] isKindOfClass:[NSDictionary class]]) {
        NSDictionary *brief = result[@"brief"];
        NSString *briefID = [brief[@"brief_id"] isKindOfClass:[NSString class]] ? brief[@"brief_id"] : nil;
        if (briefID.length > 0 && ![self.displayedBriefIDs containsObject:briefID]) {
            [self.displayedBriefIDs addObject:briefID];
            [[[self.displayedBriefIDs allObjects] sortedArrayUsingSelector:@selector(compare:)]
                writeToFile:[self.workspace stringByAppendingPathComponent:@".muse_displayed_briefs.plist"] atomically:YES];
            NSString *summary = [brief[@"summary"] isKindOfClass:[NSString class]] ? brief[@"summary"] : @"已有新的目标产物。";
            NSArray *updates = [brief[@"verified_updates"] isKindOfClass:[NSArray class]] ? brief[@"verified_updates"] : @[];
            NSArray *decisions = [brief[@"needs_decision"] isKindOfClass:[NSArray class]] ? brief[@"needs_decision"] : @[];
            NSMutableArray *lines = [NSMutableArray arrayWithObject:summary];
            for (NSDictionary *item in updates) {
                if (![item isKindOfClass:[NSDictionary class]]) continue;
                [lines addObject:[NSString stringWithFormat:@"目标产物：%@", item[@"goal_id"] ?: @"未知"]];
                for (NSString *url in item[@"source_urls"]) {
                    if ([url isKindOfClass:[NSString class]]) [lines addObject:[NSString stringWithFormat:@"来源：%@", url]];
                }
            }
            if (decisions.count > 0) [lines addObject:[NSString stringWithFormat:@"待你决定：%lu 项", (unsigned long)decisions.count]];
            self.taskTitle.stringValue = @"每日简报";
            self.taskState.stringValue = @"基于已核对的目标产物";
            self.stepsView.string = [lines componentsJoinedByString:@"\n\n"];
            [self appendChatLine:[NSString stringWithFormat:@"Muse · 每日简报\n%@", [lines componentsJoinedByString:@"\n"]]];
        }
        if (briefID.length > 0) [self sendEvent:@{@"type": @"brief_ack", @"brief_id": briefID}];
        return;
    }
    if ([result[@"prices"] isKindOfClass:[NSDictionary class]] &&
        [result[@"budget"] isKindOfClass:[NSDictionary class]]) {
        self.pricingStatus = result;
        return;
    }
    if ([result[@"profile_id"] isKindOfClass:[NSString class]] && [result[@"has_secret"] boolValue]) {
        [self appendChatLine:@"Muse · 高阶密钥已保存到本机钥匙串。"];
        return;
    }
    if ([result[@"profile_id"] isKindOfClass:[NSString class]] &&
        [result[@"status"] isEqualToString:@"SAVED"] && result[@"origin"]) {
        [self appendChatLine:@"Muse · 高阶模型价格已保存；运行前仍会核对预算与授权范围。"];
        [self sendEvent:@{@"type": @"model_pricing_get"}];
        return;
    }
    NSArray *plugins = result[@"plugins"];
    if ([plugins isKindOfClass:[NSArray class]]) {
        self.plugins = plugins;
        if (self.pluginDialogRequested) {
            self.pluginDialogRequested = NO;
            [self showPluginSettings];
        }
        return;
    }
    if ([result[@"plugin_id"] isKindOfClass:[NSString class]]) {
        NSDictionary *output = result[@"output"];
        if ([output isKindOfClass:[NSDictionary class]]) {
            [self appendChatLine:[NSString stringWithFormat:@"Muse · 合成插件示例：%@ 个字符，%@ 行；未读取文件或网络。",
                                  output[@"characters"] ?: @"?", output[@"lines"] ?: @"?"]];
        } else {
            NSString *status = result[@"status"] ?: @"未知";
            [self appendChatLine:[NSString stringWithFormat:@"Muse · 文本统计插件：%@。", [status isEqualToString:@"ENABLED"] ? @"已启用" :
                                  [status isEqualToString:@"DISABLED"] ? @"已禁用" : status]];
            [self sendEvent:@{@"type": @"plugin_list"}];
        }
        return;
    }
    NSArray *goalScopes = result[@"goal_result_scopes"];
    if ([goalScopes isKindOfClass:[NSArray class]]) {
        NSMutableArray<NSString *> *valid = [NSMutableArray array];
        for (id scope in goalScopes) if ([scope isKindOfClass:[NSString class]]) [valid addObject:scope];
        self.availableGoalResultScopes = valid;
        if (self.selectedGoalResultScope.length > 0 && ![valid containsObject:self.selectedGoalResultScope]) {
            self.selectedGoalResultScope = @"";
        }
        return;
    }
    NSArray *watches = result[@"watches"];
    if ([watches isKindOfClass:[NSArray class]]) {
        self.watches = watches;
        self.watchStatus.stringValue = [NSString stringWithFormat:@"监控：%lu 个授权目录", (unsigned long)watches.count];
        NSString *selectedRef = self.goalResourcePicker.selectedItem.representedObject;
        if (self.goalResourcePicker) {
            [self.goalResourcePicker removeAllItems];
            [self.goalResourcePicker addItemWithTitle:@"本次目标：不附加监控目录"];
            self.goalResourcePicker.lastItem.representedObject = @"";
            for (NSDictionary *item in watches) {
                NSString *ref = item[@"resource_ref"];
                NSString *root = item[@"root"];
                if (![ref isKindOfClass:[NSString class]] || ![root isKindOfClass:[NSString class]]) continue;
                [self.goalResourcePicker addItemWithTitle:[NSString stringWithFormat:@"监控目录：%@", root.lastPathComponent]];
                self.goalResourcePicker.lastItem.representedObject = ref;
                self.goalResourcePicker.lastItem.toolTip = root;
                if ([ref isEqualToString:selectedRef]) [self.goalResourcePicker selectItem:self.goalResourcePicker.lastItem];
            }
        }
        return;
    }
    NSDictionary *watch = result[@"watch"];
    if ([watch isKindOfClass:[NSDictionary class]]) {
        NSString *root = [watch[@"root"] isKindOfClass:[NSString class]] ? watch[@"root"] : @"";
        [self appendChatLine:[NSString stringWithFormat:@"Muse · 已授权监控目录：%@。设立目标时可在输入框上方选择。",
                              root.lastPathComponent.length > 0 ? root.lastPathComponent : @"所选目录"]];
        [self sendEvent:@{@"type": @"watch_folder_list"}];
        return;
    }
    if ([result[@"status"] isEqualToString:@"REVOKED"]) {
        [self appendLog:@"文件夹监控已撤销。"];
        [self sendEvent:@{@"type": @"watch_folder_list"}];
        return;
    }
    NSDictionary *proactivity = result[@"proactivity_settings"];
    if ([proactivity isKindOfClass:[NSDictionary class]]) {
        self.proactivitySettings = proactivity;
        [self appendLog:[NSString stringWithFormat:@"主动通知：%@", [proactivity[@"enabled"] boolValue] ? @"开启" : @"关闭"]];
        return;
    }
    if ([result[@"recording"] isKindOfClass:[NSNumber class]] && result[@"scope"] && result[@"account_scope"]) {
        self.memorySettings = result;
        self.memoryStatus.stringValue = [NSString stringWithFormat:@"记忆：%@ · %@ 条",
                                          [result[@"recording"] boolValue] ? @"记录中" : @"已停记",
                                          result[@"memory_count"] ?: @"0"];
        return;
    }
    NSArray *records = result[@"records"];
    if ([records isKindOfClass:[NSArray class]]) {
        [self showMemoryRecords:records];
        return;
    }
    if ([result[@"id"] isKindOfClass:[NSNumber class]] && [result[@"status"] isEqualToString:@"SAVED"]) {
        [self appendLog:@"记忆变更已保存。"];
        [self sendEvent:@{@"type": @"memory_list"}];
        return;
    }
    NSDictionary *settings = result[@"model_settings"];
    if ([settings isKindOfClass:[NSDictionary class]]) {
        self.modelSettings = settings;
        if ([self.pendingSetupMode isEqualToString:@"high"]) {
            self.pendingSetupMode = nil;
            NSMutableDictionary *highOnly = [settings mutableCopy];
            highOnly[@"mode"] = @"high";
            self.modelSettings = highOnly;
            [self sendEvent:@{@"type": @"model_settings_set", @"settings": highOnly}];
            [self performSelector:@selector(showModelSettings:) withObject:nil afterDelay:0.2];
        }
        NSDictionary *modeLabels = @{@"local": @"纯本地", @"high": @"纯高阶", @"mixed": @"混合", @"custom": @"自定义"};
        NSString *mode = settings[@"mode"] ?: @"local";
        self.routeStatus.stringValue = [NSString stringWithFormat:@"模式：%@", modeLabels[mode] ?: mode];
        [self appendLog:[NSString stringWithFormat:@"模型设置：%@", result[@"status"] ?: @"READY"]];
        return;
    }
    NSArray *goals = result[@"goals"];
    if ([goals isKindOfClass:[NSArray class]]) {
        NSString *previousGoalID = self.activeGoalID;
        [self.goalPicker removeAllItems];
        [self.goalPicker addItemWithTitle:@"选择长期目标…"];
        for (NSDictionary *item in goals) {
            if (![item isKindOfClass:[NSDictionary class]]) continue;
            NSString *goalID = item[@"goal_id"];
            NSDictionary *plan = item[@"plan"];
            if (![goalID isKindOfClass:[NSString class]] || ![plan isKindOfClass:[NSDictionary class]]) continue;
            if ([plan[@"notify"] isKindOfClass:[NSDictionary class]]) self.goalNotifyByID[goalID] = plan[@"notify"];
            NSString *label = [NSString stringWithFormat:@"%@ · %@", plan[@"title"] ?: goalID, item[@"status"] ?: @"?"];
            [self.goalPicker addItemWithTitle:label];
            self.goalPicker.lastItem.representedObject = goalID;
        }
        NSMenuItem *selection = nil;
        for (NSMenuItem *item in self.goalPicker.itemArray) {
            if ([item.representedObject isEqual:previousGoalID]) { selection = item; break; }
        }
        if (!selection && self.goalPicker.numberOfItems > 1) selection = [self.goalPicker itemAtIndex:1];
        if (selection) {
            [self.goalPicker selectItem:selection];
            if (![selection.representedObject isEqual:previousGoalID]) {
                [self sendEvent:@{@"type": @"goal_get", @"goal_id": selection.representedObject}];
            }
        }
        [self appendLog:[NSString stringWithFormat:@"长期目标：%lu 个", (unsigned long)(self.goalPicker.numberOfItems - 1)]];
        return;
    }
    if ([result[@"plan"] isKindOfClass:[NSDictionary class]]) {
        [self showGoalResult:result];
        return;
    }
    NSDictionary *system = result[@"system"];
    if ([system isKindOfClass:[NSDictionary class]]) {
        NSString *platform = system[@"platform"] ?: @"unknown";
        NSString *machine = system[@"machine"] ?: @"unknown";
        self.permissionStatus.stringValue = @"权限：按需开启";
        self.permissionStatus.textColor = [NSColor secondaryLabelColor];
        self.workerStatus.stringValue = @"后台服务在线";
        self.workerStatus.textColor = [NSColor systemGreenColor];
        [self appendLog:[NSString stringWithFormat:@"设备状态：%@ %@ · 能力 %@", platform, machine, [system[@"capabilities"] componentsJoinedByString:@", "]]];
        return;
    }
    if ([result[@"chat_reply"] isKindOfClass:[NSString class]]) {
        [self showChatResult:result];
        return;
    }
    NSDictionary *memoryIndex = result[@"memory_index"];
    if ([memoryIndex isKindOfClass:[NSDictionary class]]) {
        self.memoryStatus.stringValue = [NSString stringWithFormat:@"记忆：%@ 个文件", memoryIndex[@"indexed"] ?: @"0"];
        [self appendLog:[NSString stringWithFormat:@"记忆索引：%@", memoryIndex[@"status"] ?: @"unknown"]];
        return;
    }
    NSDictionary *resultCard = result[@"result_card"];
    if ([resultCard isKindOfClass:[NSDictionary class]]) {
        [self showTaskPane:nil];
        self.taskTitle.stringValue = resultCard[@"title"] ?: @"结果卡";
        NSString *cardStatus = resultCard[@"status"] ?: @"unknown";
        NSDictionary *cardStatusLabels = @{@"WAITING_USER": @"等待你的决定", @"COMPLETED": @"已完成",
                                            @"NO_CHANGE": @"资料未变化", @"BLOCKED_PERMISSION": @"权限待开启",
                                            @"FAILED": @"失败"};
        self.taskState.stringValue = cardStatusLabels[cardStatus] ?: cardStatus;
        self.taskState.textColor = [resultCard[@"status"] isEqualToString:@"COMPLETED"] ? [NSColor systemGreenColor] : [NSColor systemOrangeColor];
        NSMutableArray *cardLines = [NSMutableArray array];
        if (resultCard[@"summary"]) [cardLines addObject:[NSString stringWithFormat:@"摘要：%@", resultCard[@"summary"]]];
        if (resultCard[@"next_step"]) [cardLines addObject:[NSString stringWithFormat:@"下一步：%@", resultCard[@"next_step"]]];
        if (resultCard[@"verification"]) [cardLines addObject:[NSString stringWithFormat:@"验证：%@", resultCard[@"verification"]]];
        if (resultCard[@"adapter_kind"]) [cardLines addObject:[NSString stringWithFormat:@"宿主适配：%@ · %@", resultCard[@"adapter_kind"], resultCard[@"live_status"] ?: @"unknown"]];
        NSArray *options = resultCard[@"options"];
        if ([options isKindOfClass:[NSArray class]] && options.count > 0) {
            NSMutableArray *labels = [NSMutableArray array];
            for (NSDictionary *option in options) {
                if ([option isKindOfClass:[NSDictionary class]] && option[@"label"]) [labels addObject:option[@"label"]];
            }
            if (labels.count > 0) [cardLines addObject:[NSString stringWithFormat:@"可选操作：%@", [labels componentsJoinedByString:@" / "]]];
        }
        [self setInspectorText:[cardLines componentsJoinedByString:@"\n\n"]];
        [self appendLog:[NSString stringWithFormat:@"结果卡：%@ · %@", resultCard[@"status"] ?: @"unknown", resultCard[@"source"] ?: @"unknown"]];
        NSString *goalCardID = resultCard[@"id"];
        if ([goalCardID isKindOfClass:[NSString class]] && [goalCardID hasPrefix:@"goal:"]) {
            NSString *runStatus = result[@"status"] ?: resultCard[@"status"] ?: @"未知";
            NSString *friendlyStatus = [runStatus isEqualToString:@"COMPLETED"] ? @"产物已生成并核对" :
                [runStatus isEqualToString:@"NO_CHANGE"] ? @"资料未变化" :
                [runStatus isEqualToString:@"WAITING_USER"] ? @"等待你的决定" : runStatus;
            NSMutableArray<NSString *> *update = [NSMutableArray arrayWithObjects:@"Muse · 目标更新",
                resultCard[@"title"] ?: @"长期目标", friendlyStatus, nil];
            if ([result[@"event_id"] isKindOfClass:[NSString class]] && [result[@"event_id"] hasPrefix:@"file:"]) {
                [update addObject:@"监控目录有变化"];
            }
            for (NSDictionary *receipt in result[@"receipts"]) {
                if (![receipt isKindOfClass:[NSDictionary class]] ||
                    ![receipt[@"capability"] isEqualToString:@"workspace.write_artifact"]) continue;
                NSString *path = receipt[@"output"][@"relative_path"];
                if ([path isKindOfClass:[NSString class]] && path.length > 0) {
                    [update addObject:[NSString stringWithFormat:@"已生成 %@", path]];
                    self.goalArtifactsByID[goalCardID] = path;
                }
            }
            BOOL changed = ![result[@"status"] isEqualToString:@"NO_CHANGE"];
            BOOL shouldNotify = result[@"notify"] ? [result[@"notify"] boolValue] : changed;
            if (changed && shouldNotify) {
                [self appendChatLine:[update componentsJoinedByString:@" · "]];
                [self maybeNotifyGoalRun:result card:resultCard];
            }
            [self sendEvent:@{@"type": @"goal_get", @"goal_id": goalCardID}];
            if ([result[@"status"] isEqualToString:@"COMPLETED"]) [self sendEvent:@{@"type": @"memory_scope_list"}];
        }
        if (([resultCard[@"source"] isEqualToString:@"qqmail"] &&
             ([resultCard[@"status"] isEqualToString:@"AWAITING_USER_CHOICE"] || [resultCard[@"status"] isEqualToString:@"QUEUED_FOR_USER"])) ||
            [resultCard[@"source"] isEqualToString:@"robrix2"] || [resultCard[@"source"] isEqualToString:@"wechat"]) {
            [self notifyResultCard:resultCard];
        }
        if ([resultCard[@"source"] isEqualToString:@"qqmail"]) [self checkPendingMailCard:nil];
    }
    if (![result[@"ok"] boolValue] && ![resultCard isKindOfClass:[NSDictionary class]]) {
        [self showTaskPane:nil];
        self.taskTitle.stringValue = @"请求未完成";
        self.taskState.stringValue = @"失败";
        self.taskState.textColor = [NSColor systemRedColor];
        self.stepsView.string = @"有一项请求未完成。可在“活动”查看原因，检查模型或后台服务后重试。";
        [self appendLog:[NSString stringWithFormat:@"请求未执行：%@ %@", result[@"error"] ?: @"", result[@"detail"] ?: @""]];
        return;
    }
    if ([result[@"analysis"] isKindOfClass:[NSDictionary class]]) {
        [self showMessageResult:result];
        return;
    }
    NSDictionary *card = result[@"task_card"];
    if ([card isKindOfClass:[NSDictionary class]]) {
        [self showTaskPane:nil];
        self.taskTitle.stringValue = card[@"title"] ?: @"任务";
        NSString *status = card[@"status"] ?: @"unknown";
        self.taskState.stringValue = status;
        self.taskState.textColor = [status isEqualToString:@"completed"] ? [NSColor systemGreenColor] : ([status isEqualToString:@"rejected"] ? [NSColor systemRedColor] : [NSColor systemOrangeColor]);
        NSTextView *steps = self.stepsView;
        NSArray *lines = card[@"steps"];
        steps.string = [lines componentsJoinedByString:@"\n• "];
        if (lines.count > 0) steps.string = [NSString stringWithFormat:@"• %@", steps.string];
        self.pending = [card[@"requires_confirmation"] boolValue] && [status isEqualToString:@"proposed"];
        if (self.selfTest && self.pending) {
            [self performSelector:@selector(runSelfTestConfirm) withObject:nil afterDelay:0.3];
        }
        if (self.selfTest && [status isEqualToString:@"completed"]) {
            [self performSelector:@selector(quitAll:) withObject:nil afterDelay:0.3];
        }
        self.approveButton.enabled = self.pending;
        self.rejectButton.enabled = self.pending;
        self.approveButton.hidden = !self.pending;
        self.rejectButton.hidden = !self.pending;
        [self appendLog:[NSString stringWithFormat:@"任务：%@ · 状态：%@", card[@"title"] ?: @"", status]];
    }
    if (result[@"created"]) [self appendLog:[NSString stringWithFormat:@"已创建并回读：%@", result[@"created"]]];
    NSDictionary *execution = result[@"execution"];
    if ([execution isKindOfClass:[NSDictionary class]]) [self appendLog:[NSString stringWithFormat:@"终端退出码：%@ · 命令：%@", execution[@"returncode"], [execution[@"argv"] componentsJoinedByString:@" "]]];
}

- (void)runSelfTestConfirm {
    [self appendLog:@"self-test：确认合成任务。"];
    [self sendEvent:@{@"type": @"confirm", @"approved": @YES}];
}

- (void)appendLog:(NSString *)text {
    if (!self.logView) return;
    NSString *stamp = [[NSDate date] descriptionWithLocale:[NSLocale currentLocale]];
    NSString *line = [NSString stringWithFormat:@"[%@] %@\n", [stamp substringToIndex:MIN((NSUInteger)19, stamp.length)], text];
    [[self.logView textStorage] appendAttributedString:[[NSAttributedString alloc] initWithString:line]];
    [self.logView scrollRangeToVisible:NSMakeRange(self.logView.string.length, 0)];
}

- (void)checkModelHealth {
    NSURL *url = [NSURL URLWithString:@"http://127.0.0.1:8080/health"];
    [[[NSURLSession sharedSession] dataTaskWithURL:url completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        BOOL ok = !error && [(NSHTTPURLResponse *)response statusCode] == 200;
        dispatch_async(dispatch_get_main_queue(), ^{
            self.modelStatus.stringValue = ok ? @"本机模型在线" : @"本机模型离线";
            self.modelStatus.textColor = ok ? [NSColor systemGreenColor] : [NSColor systemOrangeColor];
            [self appendLog:(ok ? @"Qwen3-0.6B 健康检查通过。" : @"Qwen 服务未连接，路由器使用规则回退。")];
            if (!ok && !self.modelManager.ownedServer.isRunning) [self startManagedModelIfConfigured];
        });
    }] resume];
}

- (void)togglePause:(id)sender {
    self.paused = !self.paused;
    NSMenuItem *item = [(NSMenuItem *)sender isKindOfClass:[NSMenuItem class]] ? (NSMenuItem *)sender : nil;
    item.title = self.paused ? @"恢复监听" : @"暂停监听";
    NSTextField *listen = [self.window.contentView viewWithTag:401];
    listen.stringValue = self.paused ? @"● 已暂停" : @"● 监听中";
    listen.textColor = self.paused ? [NSColor systemOrangeColor] : [NSColor systemGreenColor];
    [self sendEvent:@{@"type": @"message_control", @"action": (self.paused ? @"pause" : @"resume")}];
    [self appendLog:(self.paused ? @"监听已暂停；现有任务保留，新的输入不会路由。" : @"监听已恢复。")];
}

- (void)switchInspectorTab:(NSSegmentedControl *)sender {
    if (sender.selectedSegment == 0) [self showSkillSlots:nil];
    else [self showTaskPane:nil];
}
- (void)showSkillSlots:(id)sender {
    self.taskPane.hidden = YES;
    self.skillPane.hidden = NO;
    self.inspectorTabs.selectedSegment = 0;
}
- (void)showTaskPane:(id)sender {
    self.skillPane.hidden = YES;
    self.taskPane.hidden = NO;
    self.inspectorTabs.selectedSegment = 1;
}
- (void)showUnavailableSkill:(id)sender {
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"微信技能尚未接通";
    alert.informativeText = @"当前成品没有通过微信监听与动作回读的真实验收，因此不会启用此技能。";
    [alert addButtonWithTitle:@"知道了"];
    [alert runModal];
}
- (void)showTasks:(id)sender { [self showTaskPane:nil]; [self.window makeKeyAndOrderFront:nil]; [NSApp activateIgnoringOtherApps:YES]; [self appendLog:@"已定位到当前任务与结果卡。"]; }
- (void)showTechnicalDetails:(id)sender { [self.technicalWindow makeKeyAndOrderFront:nil]; [NSApp activateIgnoringOtherApps:YES]; }
- (NSDictionary *)runCalendarSelftest:(NSString *)mode {
    NSString *resources = [[NSBundle mainBundle] resourcePath];
    NSString *python = [resources stringByAppendingPathComponent:@"python/bin/python3"];
    NSString *script = [resources stringByAppendingPathComponent:@"calendar_selftest.py"];
    NSString *helper = [resources stringByAppendingPathComponent:@"muse_calendar_helper"];
    if (![[NSFileManager defaultManager] isExecutableFileAtPath:python] ||
        ![[NSFileManager defaultManager] isReadableFileAtPath:script]) {
        return @{@"ok": @NO, @"stage": @"runtime", @"error": @"calendar_selftest_runtime_missing"};
    }
    NSString *tz = [NSTimeZone localTimeZone].name ?: @"UTC";
    NSTask *task = [[NSTask alloc] init];
    task.launchPath = python;
    task.arguments = @[@"-B", script, mode, self.workspace, helper, tz];
    NSMutableDictionary *env = [[[NSProcessInfo processInfo] environment] mutableCopy];
    env[@"PYTHONDONTWRITEBYTECODE"] = @"1";
    task.environment = env;
    NSPipe *output = [NSPipe pipe];
    task.standardOutput = output;
    task.standardError = [NSFileHandle fileHandleWithNullDevice];
    @try {
        [task launch];
        NSDate *deadline = [NSDate dateWithTimeIntervalSinceNow:180];
        while (task.isRunning && [deadline timeIntervalSinceNow] > 0) [NSThread sleepForTimeInterval:0.1];
        if (task.isRunning) { [task terminate]; return @{@"ok": @NO, @"error": @"calendar_selftest_timeout"}; }
    } @catch (NSException *exception) {
        return @{@"ok": @NO, @"error": @"calendar_selftest_launch_failed"};
    }
    NSData *data = [[output fileHandleForReading] readDataToEndOfFile];
    NSDictionary *result = data.length ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
    return [result isKindOfClass:[NSDictionary class]] ? result : @{@"ok": @NO, @"error": @"calendar_selftest_no_output"};
}

- (void)showCalendarModule:(id)sender {
    NSAlert *intro = [[NSAlert alloc] init];
    intro.messageText = @"日历授权与自检";
    intro.informativeText = @"Muse 会先请求“完全访问日历”，然后在一个你有权访问的日历里创建唯一标记的测试事件"
                             "（[Muse Test] MUSE-CALENDAR-TEST-…），立即读回、修改、再读回；删除前会再次询问。"
                             "绝不会改动你已有的日程。";
    [intro addButtonWithTitle:@"开始"];
    [intro addButtonWithTitle:@"取消"];
    if ([intro runModal] != NSAlertFirstButtonReturn) return;
    [self appendChatLine:@"Muse · 日历自检：正在检查授权并请求完全访问；若出现系统弹窗请选择“允许完全访问”。"];
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        NSDictionary *created = [self runCalendarSelftest:@"create"];
        dispatch_async(dispatch_get_main_queue(), ^{ [self finishCalendarCreate:created]; });
    });
}

- (void)finishCalendarCreate:(NSDictionary *)result {
    if (![result[@"ok"] boolValue]) {
        if ([result[@"stage"] isEqualToString:@"permission"]) {
            NSDictionary *auth = [result[@"authorization"] isKindOfClass:[NSDictionary class]] ? result[@"authorization"] : @{};
            [self appendChatLine:[NSString stringWithFormat:
                @"Muse · 日历未获完全访问（当前：%@）。请在“系统设置 → 隐私与安全性 → 日历”里允许 Muse 后再试。",
                auth[@"status"] ?: @"UNKNOWN"]];
        } else {
            [self appendChatLine:[NSString stringWithFormat:@"Muse · 日历自检未完成：%@",
                result[@"error"] ?: result[@"stage"] ?: @"unknown"]];
        }
        return;
    }
    NSDictionary *steps = [result[@"steps"] isKindOfClass:[NSDictionary class]] ? result[@"steps"] : @{};
    NSDictionary *createStep = [steps[@"create"] isKindOfClass:[NSDictionary class]] ? steps[@"create"] : @{};
    NSDictionary *updateStep = [steps[@"update"] isKindOfClass:[NSDictionary class]] ? steps[@"update"] : @{};
    [self appendChatLine:[NSString stringWithFormat:@"Muse · 已创建并读回测试事件：%@（日历：%@）",
        result[@"title"] ?: @"", result[@"calendar_title"] ?: @""]];
    [self appendChatLine:[NSString stringWithFormat:@"Muse · 创建回读=%@，修改回读=%@",
        [createStep[@"readback_matches"] boolValue] ? @"通过" : @"未通过",
        [updateStep[@"readback_matches"] boolValue] ? @"通过" : @"未通过"]];
    NSAlert *confirm = [[NSAlert alloc] init];
    confirm.messageText = @"删除测试事件？";
    confirm.informativeText = [NSString stringWithFormat:@"将删除唯一标记的测试事件：\n%@\n\n不会影响其他日程。", result[@"title"] ?: @""];
    [confirm addButtonWithTitle:@"删除并读回"];
    [confirm addButtonWithTitle:@"暂时保留"];
    if ([confirm runModal] != NSAlertFirstButtonReturn) {
        [self appendChatLine:@"Muse · 已保留测试事件；它带有唯一标记，可在日历里手动删除。"];
        return;
    }
    [self appendChatLine:@"Muse · 正在删除测试事件并读回…"];
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        NSDictionary *deleted = [self runCalendarSelftest:@"delete"];
        dispatch_async(dispatch_get_main_queue(), ^{ [self finishCalendarDelete:deleted]; });
    });
}

- (void)finishCalendarDelete:(NSDictionary *)result {
    if ([result[@"ok"] boolValue] && [result[@"readback_absent"] boolValue]) {
        [self appendChatLine:@"Muse · 测试事件已删除，删除后读回确认不存在。"];
    } else {
        [self appendChatLine:[NSString stringWithFormat:@"Muse · 删除未确认：%@",
            result[@"delete_status"] ?: result[@"error"] ?: @"unknown"]];
    }
}
- (NSDictionary *)mailKeychainQuery:(NSString *)address {
    return @{(__bridge id)kSecClass: (__bridge id)kSecClassGenericPassword,
             (__bridge id)kSecAttrService: @"org.gosim.local-agent.qqmail",
             (__bridge id)kSecAttrAccount: address};
}
- (BOOL)rememberMailAuthCode:(NSString *)secret address:(NSString *)address {
    NSData *data = [secret dataUsingEncoding:NSUTF8StringEncoding];
    NSMutableDictionary *item = [[self mailKeychainQuery:address] mutableCopy];
    item[(__bridge id)kSecValueData] = data;
    OSStatus status = SecItemAdd((__bridge CFDictionaryRef)item, NULL);
    if (status == errSecDuplicateItem) {
        status = SecItemUpdate((__bridge CFDictionaryRef)[self mailKeychainQuery:address],
                               (__bridge CFDictionaryRef)@{(__bridge id)kSecValueData: data});
    }
    if (status != errSecSuccess) return NO;
    [[NSUserDefaults standardUserDefaults] setObject:address forKey:@"QQMailAddress"];
    return YES;
}
- (NSString *)rememberedMailAuthCode:(NSString *)address {
    NSMutableDictionary *query = [[self mailKeychainQuery:address] mutableCopy];
    query[(__bridge id)kSecReturnData] = @YES;
    query[(__bridge id)kSecMatchLimit] = (__bridge id)kSecMatchLimitOne;
    CFTypeRef result = NULL;
    OSStatus status = SecItemCopyMatching((__bridge CFDictionaryRef)query, &result);
    if (status != errSecSuccess || !result) return nil;
    NSString *secret = [[NSString alloc] initWithData:(__bridge NSData *)result encoding:NSUTF8StringEncoding];
    CFRelease(result);
    return secret;
}
- (void)forgetRememberedMailBridge {
    NSString *address = [[NSUserDefaults standardUserDefaults] stringForKey:@"QQMailAddress"];
    if (address.length) SecItemDelete((__bridge CFDictionaryRef)[self mailKeychainQuery:address]);
    [[NSUserDefaults standardUserDefaults] removeObjectForKey:@"QQMailAddress"];
}
- (void)startRememberedMailBridge {
    if (!self.mailAutoConnectAllowed || self.mailKeychainLookupInProgress ||
        self.mailBridge.isRunning || [self externalMailBridgeUsesWorkspace]) return;
    NSString *address = [[NSUserDefaults standardUserDefaults] stringForKey:@"QQMailAddress"];
    if (!address.length) return;
    self.mailKeychainLookupInProgress = YES;
    self.mailModuleButton.title = @"QQ 邮箱 · 恢复连接中";
    self.mailModuleButton.accessibilityTitle = self.mailModuleButton.title;
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        NSString *secret = [self rememberedMailAuthCode:address];
        dispatch_async(dispatch_get_main_queue(), ^{
            self.mailKeychainLookupInProgress = NO;
            if (!self.mailAutoConnectAllowed ||
                ![address isEqualToString:[[NSUserDefaults standardUserDefaults] stringForKey:@"QQMailAddress"]]) return;
            if (!secret.length) {
                [self appendLog:@"QQ 邮箱自动连接尚未就绪；请在左侧 QQ 邮箱模块重新连接。"];
                return;
            }
            [self startMailBridgeWithAddress:address authCode:secret];
        });
    });
}
- (BOOL)externalMailBridgeUsesWorkspace {
    NSTask *probe = [[NSTask alloc] init];
    probe.launchPath = @"/bin/ps";
    probe.arguments = @[@"-ww", @"-axo", @"command="];
    NSPipe *output = [NSPipe pipe];
    probe.standardOutput = output;
    probe.standardError = [NSFileHandle fileHandleWithNullDevice];
    @try { [probe launch]; }
    @catch (NSException *exception) { return YES; }
    NSData *data = [output.fileHandleForReading readDataToEndOfFile];
    [probe waitUntilExit];
    NSString *listing = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    if (probe.terminationStatus != 0 || !listing) return YES;
    for (NSString *line in [listing componentsSeparatedByString:@"\n"]) {
        if ([line containsString:@"qqmail_imap_bridge.py"] && [line containsString:self.workspace]) return YES;
    }
    return NO;
}
- (void)showMailBridgeConnection:(id)sender {
    if (self.mailBridge.isRunning) {
        NSAlert *running = [[NSAlert alloc] init];
        running.messageText = @"QQ 邮箱连接运行中";
        running.informativeText = @"仅管理这次由 Muse 启动的邮箱桥；旧终端连接不会受影响。";
        [running addButtonWithTitle:@"保持连接"];
        [running addButtonWithTitle:@"断开并忘记自动连接"];
        if ([running runModal] == NSAlertSecondButtonReturn) {
            [self.mailBridge terminate];
            self.mailBridge = nil;
            [self forgetRememberedMailBridge];
            self.mailModuleButton.title = @"QQ 邮箱 · 未连接";
            [self appendLog:@"已断开本应用启动的 QQ 邮箱桥。"];
        }
        return;
    }
    if ([self externalMailBridgeUsesWorkspace]) {
        NSAlert *existing = [[NSAlert alloc] init];
        existing.messageText = @"此工作区已有 QQ 邮箱连接";
        existing.informativeText = @"请先在原来的终端断开它，再由 Muse 连接。Muse 不会关闭或接管旧连接。";
        [existing addButtonWithTitle:@"知道了"];
        [existing runModal];
        return;
    }
    NSView *form = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 440, 145)];
    NSString *savedAddress = [[NSUserDefaults standardUserDefaults] stringForKey:@"QQMailAddress"] ?: @"";
    NSTextField *address = [self settingsField:@"QQ 邮箱地址" value:savedAddress x:0 y:94 width:440 parent:form];
    NSSecureTextField *auth = [[NSSecureTextField alloc] initWithFrame:NSMakeRect(0, 39, 440, 25)];
    auth.placeholderString = @"QQ 邮箱 IMAP/SMTP 授权码";
    auth.accessibilityTitle = @"QQ 邮箱授权码";
    [form addSubview:[self label:@"QQ 邮箱授权码" frame:NSMakeRect(0, 67, 440, 20) size:11 color:[NSColor secondaryLabelColor]]];
    [form addSubview:auth];
    NSButton *remember = [NSButton checkboxWithTitle:@"保存在此 Mac 的钥匙串中，下次启动自动监听" target:nil action:nil];
    remember.frame = NSMakeRect(0, 5, 440, 23);
    remember.state = NSControlStateValueOn;
    [form addSubview:remember];
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"连接 QQ 邮箱";
    alert.informativeText = @"授权码不会写入项目文件。勾选后仅保存在此 Mac 的钥匙串中，Muse 下次启动会自动恢复监听；也可取消勾选只连接本次。";
    alert.accessoryView = form;
    [alert addButtonWithTitle:@"连接"];
    [alert addButtonWithTitle:@"取消"];
    if ([alert runModal] != NSAlertFirstButtonReturn) { auth.stringValue = @""; return; }
    NSString *mailAddress = [address.stringValue stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    NSString *secret = auth.stringValue;
    auth.stringValue = @"";
    if (mailAddress.length == 0 || [mailAddress rangeOfCharacterFromSet:[NSCharacterSet newlineCharacterSet]].location != NSNotFound ||
        secret.length == 0 || secret.length > 256 || [secret rangeOfCharacterFromSet:[NSCharacterSet newlineCharacterSet]].location != NSNotFound) {
        [self appendLog:@"QQ 邮箱地址或授权码格式无效，连接未启动。"];
        return;
    }
    if ([self externalMailBridgeUsesWorkspace]) {
        [self appendLog:@"此工作区已有邮箱桥，连接未启动；授权码未保存。"];
        return;
    }
    if (remember.state != NSControlStateValueOn) [self forgetRememberedMailBridge];
    if (remember.state == NSControlStateValueOn && ![self rememberMailAuthCode:secret address:mailAddress]) {
        [self appendLog:@"钥匙串保存失败；这次仍尝试连接，下次启动需要重新输入授权码。"];
    }
    [self startMailBridgeWithAddress:mailAddress authCode:secret];
}
- (BOOL)startMailBridgeWithAddress:(NSString *)mailAddress authCode:(NSString *)secret {
    if (self.mailBridge.isRunning || [self externalMailBridgeUsesWorkspace]) return NO;
    NSData *credential = [[secret stringByAppendingString:@"\n"] dataUsingEncoding:NSUTF8StringEncoding];
    NSString *resource = [[NSBundle mainBundle] resourcePath];
    NSTask *bridge = [[NSTask alloc] init];
    bridge.launchPath = [[[NSBundle mainBundle] resourcePath] stringByAppendingPathComponent:@"python/bin/python3"];
    bridge.arguments = @[@"-B", [resource stringByAppendingPathComponent:@"qqmail_imap_bridge.py"],
                         @"--workspace", self.workspace, @"--address", mailAddress, @"--auth-code-stdin"];
    NSMutableDictionary *env = [[[NSProcessInfo processInfo] environment] mutableCopy];
    for (NSString *key in [env allKeys]) if ([key hasPrefix:@"QQMAIL_"]) [env removeObjectForKey:key];
    env[@"PYTHONPATH"] = resource;
    env[@"PYTHONNOUSERSITE"] = @"1";
    env[@"PYTHONDONTWRITEBYTECODE"] = @"1";
    bridge.environment = env;
    NSPipe *input = [NSPipe pipe];
    bridge.standardInput = input;
    bridge.standardOutput = [NSFileHandle fileHandleWithNullDevice];
    bridge.standardError = [NSFileHandle fileHandleWithNullDevice];
    __weak typeof(self) weakSelf = self;
    __weak NSTask *weakBridge = bridge;
    bridge.terminationHandler = ^(NSTask *task) {
        dispatch_async(dispatch_get_main_queue(), ^{
            if (weakSelf.mailBridge == weakBridge) {
                weakSelf.mailBridge = nil;
                weakSelf.mailModuleButton.title = @"QQ 邮箱 · 未连接";
                [weakSelf appendLog:@"本应用启动的 QQ 邮箱桥已停止。"];
            }
        });
    };
    @try {
        [[NSFileManager defaultManager] removeItemAtPath:[self.workspace stringByAppendingPathComponent:@".qqmail_bridge_health.json"] error:nil];
        [bridge launch];
        [input.fileHandleForWriting writeData:credential];
        [input.fileHandleForWriting closeFile];
        self.mailBridge = bridge;
        self.lastMailStartAttempt = [NSDate date];
        self.mailModuleButton.title = @"QQ 邮箱 · 连接中";
        [self appendLog:@"QQ 邮箱桥已启动，正在尝试连接；收到邮件后才会出现事件卡。"];
        return YES;
    } @catch (NSException *exception) {
        if (bridge.isRunning) [bridge terminate];
        [self appendLog:@"QQ 邮箱桥启动失败；请检查安装包和本机权限。"];
        return NO;
    }
}
- (void)stopOwnedWorkers:(id)sender {
    self.mailAutoConnectAllowed = NO;
    [self.officialPollTimer invalidate];
    [self.modelHealthTimer invalidate];
    self.modelHealthTimer = nil;
    self.officialPollTimer = nil;
    self.officialPanel.hidden = YES;
    if (self.worker.isRunning) [self.worker terminate];
    if (self.mailBridge.isRunning) [self.mailBridge terminate];
    [self.modelManager stopOwnedServer];
    self.workerStatus.stringValue = @"后台服务已停止";
    self.workerStatus.textColor = [NSColor systemOrangeColor];
    [self appendLog:@"本应用的后台服务已停止；重新打开 Muse 可恢复。共享 Qwen 和旧终端连接不受影响。"];
}
- (void)openWorkspace:(id)sender { [[NSWorkspace sharedWorkspace] openURL:[NSURL fileURLWithPath:self.workspace]]; [self appendLog:@"已请求 Finder 打开工作区。"]; }
- (void)showAbout:(id)sender { [NSApp orderFrontStandardAboutPanel:nil]; }
- (void)quitAll:(id)sender { [self appendLog:@"退出本应用；共享 Qwen 服务保持运行。"]; [NSApp terminate:nil]; }
- (BOOL)applicationShouldHandleReopen:(NSApplication *)sender hasVisibleWindows:(BOOL)visible {
    if (!visible) [self.window makeKeyAndOrderFront:nil];
    [sender activateIgnoringOtherApps:YES];
    return YES;
}
- (BOOL)windowShouldClose:(NSWindow *)sender {
    if (sender == self.downloadWindow) { [self cancelModelDownload:nil]; [sender orderOut:nil]; return NO; }
    [sender orderOut:nil];
    if (sender == self.window) [self appendLog:@"主窗口已关闭；可从 Dock 重新打开，worker 仍保持。"];
    return NO;
}
- (void)applicationWillTerminate:(NSNotification *)notification {
    [self.officialPollTimer invalidate];
    [self.mailRecoveryTimer invalidate];
    [self.modelHealthTimer invalidate];
    [self.modelManager cancelDownload];
    if (self.worker.isRunning) [self.worker terminate];
    if (self.mailBridge.isRunning) [self.mailBridge terminate];
    [self.modelManager stopOwnedServer];
}
@end

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        NSApplication *app = [NSApplication sharedApplication];
        GOSIMAppDelegate *delegate = [[GOSIMAppDelegate alloc] init];
        app.delegate = delegate;
        [app setActivationPolicy:NSApplicationActivationPolicyRegular];
        return NSApplicationMain(argc, argv);
    }
}
