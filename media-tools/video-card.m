#import <AppKit/AppKit.h>
#import <ImageIO/ImageIO.h>
static NSColor *rgb(int r,int g,int b){return [NSColor colorWithSRGBRed:r/255.0 green:g/255.0 blue:b/255.0 alpha:1];}
static void text(NSString *s,NSRect rect,CGFloat size,NSColor *color,BOOL bold){
 NSMutableParagraphStyle *p=[NSMutableParagraphStyle new];p.lineSpacing=12;
 [s drawInRect:rect withAttributes:@{NSFontAttributeName:[NSFont systemFontOfSize:size weight:bold?NSFontWeightSemibold:NSFontWeightRegular],NSForegroundColorAttributeName:color,NSParagraphStyleAttributeName:p}];
}
static void box(NSRect rect,NSColor *fill,NSColor *stroke){
 NSBezierPath *p=[NSBezierPath bezierPathWithRoundedRect:rect xRadius:24 yRadius:24];[fill setFill];[p fill];[stroke setStroke];p.lineWidth=1.5;[p stroke];
}
int main(int argc,const char **argv){@autoreleasepool{
 if(argc!=3)return 2;[NSApplication sharedApplication];
 NSBitmapImageRep *rep=[[NSBitmapImageRep alloc]initWithBitmapDataPlanes:NULL pixelsWide:1920 pixelsHigh:1080 bitsPerSample:8 samplesPerPixel:4 hasAlpha:YES isPlanar:NO colorSpaceName:NSCalibratedRGBColorSpace bytesPerRow:0 bitsPerPixel:0];
 [NSGraphicsContext saveGraphicsState];[NSGraphicsContext setCurrentContext:[NSGraphicsContext graphicsContextWithBitmapImageRep:rep]];
 NSGradient *g=[[NSGradient alloc]initWithStartingColor:rgb(8,14,27) endingColor:rgb(26,39,65)];[g drawInRect:NSMakeRect(0,0,1920,1080) angle:20];
 NSColor *white=rgb(238,245,252),*muted=rgb(145,164,190),*cyan=rgb(104,222,211),*blue=rgb(124,163,255);
 [cyan setFill];NSRectFill(NSMakeRect(100,954,64,4));
 text(@"Muse｜让记忆推动行动",NSMakeRect(100,850,1600,92),62,white,YES);
 text(@"持续行动记忆  /  可见行动链",NSMakeRect(102,801,900,44),26,muted,NO);
 BOOL end=[@(argv[1]) isEqualToString:@"outro"];
 if(end){
  text(@"不止完成任务，\n更会把事情继续办下去。",NSMakeRect(100,400,1730,288),90,white,YES);
  text(@"理解  →  行动  →  变化  →  继续",NSMakeRect(106,300,1500,70),36,cyan,NO);
 }else{
  text(@"计划变了，\n事情继续。",NSMakeRect(100,350,1120,344),112,white,YES);
  text(@"AI 还记得自己之前做过什么吗？",NSMakeRect(106,270,1110,68),34,muted,NO);
  [rgb(58,79,110) setStroke];NSBezierPath *line=[NSBezierPath bezierPath];[line moveToPoint:NSMakePoint(1270,294)];[line lineToPoint:NSMakePoint(1270,714)];line.lineWidth=3;[line stroke];
  NSArray *titles=@[@"记住上下文",@"调整原计划",@"接着办下去"];
  NSArray *details=@[@"偏好与事情的来处",@"15:00  →  16:00",@"同一事务，保留进展"];
  for(int i=0;i<3;i++){CGFloat y=635-i*180;box(NSMakeRect(1310,y,500,140),rgb(29,43,67),rgb(55,76,105));[(i==1?cyan:blue) setFill];[[NSBezierPath bezierPathWithOvalInRect:NSMakeRect(1258,y+58,24,24)]fill];text(titles[i],NSMakeRect(1346,y+61,430,54),34,white,YES);text(details[i],NSMakeRect(1346,y+16,430,40),25,muted,NO);}
 }
 text(@"110 秒 · 真实工作台演示",NSMakeRect(105,106,1100,50),24,muted,NO);
 [NSGraphicsContext restoreGraphicsState];
 NSData *png=[rep representationUsingType:NSBitmapImageFileTypePNG properties:@{}];return [png writeToFile:@(argv[2]) atomically:YES]?0:1;
}}
