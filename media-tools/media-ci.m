#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <AppKit/AppKit.h>
#import <QuartzCore/QuartzCore.h>
#import <ImageIO/ImageIO.h>
#import <CoreImage/CoreImage.h>
#import <CoreText/CoreText.h>
static CMTime tm(double n){ return CMTimeMakeWithSeconds(n,600); }
static void die(NSString *s){ fprintf(stderr,"%s\n",s.UTF8String);exit(1); }
static CIImage *textImage(NSString *text,CGFloat width,CGFloat height,CGFloat size){
 CGColorSpaceRef cs=CGColorSpaceCreateDeviceRGB();CGContextRef ctx=CGBitmapContextCreate(NULL,width,height,8,0,cs,kCGImageAlphaPremultipliedLast);CGColorSpaceRelease(cs);
 CTFontRef font=CTFontCreateWithName(CFSTR("PingFangSC-Semibold"),size,NULL);CGColorRef white=CGColorCreateGenericRGB(1,1,1,1);
 NSAttributedString *s=[[NSAttributedString alloc]initWithString:text attributes:@{(__bridge id)kCTFontAttributeName:(__bridge id)font,(__bridge id)kCTForegroundColorAttributeName:(__bridge id)white}];CTFramesetterRef fs=CTFramesetterCreateWithAttributedString((__bridge CFAttributedStringRef)s);CGPathRef path=CGPathCreateWithRect(CGRectMake(0,0,width,height),NULL);CTFrameRef frame=CTFramesetterCreateFrame(fs,CFRangeMake(0,0),path,NULL);CTFrameDraw(frame,ctx);CGImageRef cg=CGBitmapContextCreateImage(ctx);CIImage *result=[CIImage imageWithCGImage:cg];CGImageRelease(cg);CFRelease(frame);CFRelease(path);CFRelease(fs);CFRelease(font);CGColorRelease(white);CGContextRelease(ctx);return result;
}
int main(int argc,const char **argv){@autoreleasepool{
 [NSApplication sharedApplication];
 if(argc<3)die(@"media probe|frame|render path ...");
 NSString *mode=@(argv[1]);AVURLAsset *asset=[AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:@(argv[2])] options:nil];
 AVAssetTrack *source=[[asset tracksWithMediaType:AVMediaTypeVideo] firstObject];
 if([mode isEqualToString:@"probe"]){NSDictionary *d=@{@"duration":@(CMTimeGetSeconds(asset.duration)),@"width":@(source.naturalSize.width),@"height":@(source.naturalSize.height),@"audio_tracks":@([[asset tracksWithMediaType:AVMediaTypeAudio]count])};puts([[NSString alloc]initWithData:[NSJSONSerialization dataWithJSONObject:d options:0 error:nil] encoding:NSUTF8StringEncoding].UTF8String);return 0;}
 if([mode isEqualToString:@"frame"]){AVAssetImageGenerator *g=[[AVAssetImageGenerator alloc]initWithAsset:asset];g.appliesPreferredTrackTransform=YES;g.requestedTimeToleranceBefore=kCMTimeZero;g.requestedTimeToleranceAfter=kCMTimeZero;NSError *e=nil;CGImageRef im=[g copyCGImageAtTime:tm(atof(argv[3])) actualTime:nil error:&e];if(!im)die(e.description);CGImageDestinationRef dest=CGImageDestinationCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:@(argv[4])],CFSTR("public.png"),1,NULL);CGImageDestinationAddImage(dest,im,NULL);BOOL ok=CGImageDestinationFinalize(dest);CFRelease(dest);CGImageRelease(im);return ok?0:1;}
 if(![mode isEqualToString:@"render"]||argc!=5)die(@"media render raw.mov timeline.json output.mp4");
 NSError *err=nil;NSDictionary *config=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@(argv[3])] options:0 error:&err];if(!config)die(err.description);
 double duration=[config[@"duration"] doubleValue];AVMutableComposition *comp=[AVMutableComposition composition];AVMutableCompositionTrack *track=[comp addMutableTrackWithMediaType:AVMediaTypeVideo preferredTrackID:kCMPersistentTrackID_Invalid];
 for(NSDictionary *slice in config[@"slices"]){ fprintf(stderr,"slice %s at %.2f source %.2f duration %.2f\n",[slice[@"path"]UTF8String],[slice[@"at"]doubleValue],[slice[@"source"]doubleValue],[slice[@"duration"]doubleValue]); AVAssetTrack *sliceSource=source; if(slice[@"path"]){ AVURLAsset *sa=[AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:slice[@"path"]]options:nil];sliceSource=[[sa tracksWithMediaType:AVMediaTypeVideo]firstObject]; } CMTimeRange range=CMTimeRangeMake(tm([slice[@"source"]doubleValue]),tm([slice[@"duration"]doubleValue]));CMTime at=tm([slice[@"at"]doubleValue]);if(![track insertTimeRange:range ofTrack:sliceSource atTime:at error:&err])die(err.description);if(slice[@"output_duration"])[track scaleTimeRange:CMTimeRangeMake(at,range.duration) toDuration:tm([slice[@"output_duration"]doubleValue])];}
 AVMutableCompositionTrack *at=[comp addMutableTrackWithMediaType:AVMediaTypeAudio preferredTrackID:kCMPersistentTrackID_Invalid];
 for(NSDictionary *audio in config[@"audio"]){fprintf(stderr,"audio %s at %.2f\n",[audio[@"path"]UTF8String],[audio[@"at"]doubleValue]);AVURLAsset *a=[AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:audio[@"path"]]options:nil];if(![at insertTimeRange:CMTimeRangeMake(kCMTimeZero,a.duration) ofTrack:[[a tracksWithMediaType:AVMediaTypeAudio]firstObject] atTime:tm([audio[@"at"]doubleValue]) error:&err])die(err.description);}
 fprintf(stderr,"composition ready %.2f seconds\n",CMTimeGetSeconds(comp.duration));CGFloat w=1920,h=1080;NSArray *c=config[@"crop"];CGFloat cx=[c[0]doubleValue],cy=[c[1]doubleValue],cw=[c[2]doubleValue],ch=[c[3]doubleValue];CGFloat scale=MIN(1800/cw,820/ch);CGFloat dx=(w-cw*scale)/2,dy=156;
 CIImage *canvas=[[CIImage imageWithColor:[CIColor colorWithRed:.031 green:.055 blue:.106]]imageByCroppingToRect:CGRectMake(0,0,w,h)];
 CIImage *brand=[textImage(@"MUSE",350,60,36) imageByApplyingTransform:CGAffineTransformMakeTranslation(60,985)];
 CIImage *tagline=[textImage(@"持续行动记忆",360,45,24) imageByApplyingTransform:CGAffineTransformMakeTranslation(1570,998)];
 NSMutableArray *sectionImages=[NSMutableArray new];for(NSDictionary *section in config[@"sections"]){[sectionImages addObject:[textImage(section[@"title"],1050,50,27)imageByApplyingTransform:CGAffineTransformMakeTranslation(350,996)]];}
 NSMutableArray *cards=[NSMutableArray new];for(NSDictionary *card in config[@"cards"]){CIImage *cardImage=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:card[@"path"]]];if(!cardImage)die(@"Missing title card");[cards addObject:cardImage];}
 NSMutableArray *captionImages=[NSMutableArray new];for(NSDictionary *caption in config[@"captions"]){[captionImages addObject:[textImage(caption[@"text"],1760,72,32)imageByApplyingTransform:CGAffineTransformMakeTranslation(80,20)]];}
 NSMutableArray *stillImages=[NSMutableArray new];for(NSDictionary *v in config[@"stills"]){CIImage *im=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:v[@"path"]]];if(!im)die(@"Missing recorded freeze frame");[stillImages addObject:im];}
 NSMutableArray *noteImages=[NSMutableArray new];for(NSDictionary *n in config[@"notes"]){[noteImages addObject:[textImage(n[@"text"],900,400,[n[@"size"]doubleValue])imageByApplyingTransform:CGAffineTransformMakeTranslation([n[@"x"]doubleValue],[n[@"y"]doubleValue])]];}
 CGFloat sourceHeight=source.naturalSize.height;CGRect sourceCrop=CGRectMake(cx,sourceHeight-cy-ch,cw,ch);
 AVMutableVideoComposition *video=[AVMutableVideoComposition videoCompositionWithAsset:comp applyingCIFiltersWithHandler:^(AVAsynchronousCIImageFilteringRequest *request){
 double sec=CMTimeGetSeconds(request.compositionTime);CGRect crop=sourceCrop;CGFloat z=scale,x=dx,y=dy;
 for(NSDictionary *v in config[@"viewports"]){if(sec>=[v[@"start"]doubleValue]&&sec<[v[@"end"]doubleValue]){NSArray *r=v[@"crop"];CGFloat vw=[r[2]doubleValue],vh=[r[3]doubleValue];crop=CGRectMake([r[0]doubleValue],sourceHeight-[r[1]doubleValue]-vh,vw,vh);z=MIN(1800/vw,820/vh);x=v[@"x"]?[v[@"x"]doubleValue]:(w-vw*z)/2;y=dy+(820-vh*z)/2;}}
 CIImage *frameSource=request.sourceImage;for(NSUInteger i=0;i<stillImages.count;i++){NSDictionary *v=config[@"stills"][i];if(sec>=[v[@"start"]doubleValue]&&sec<[v[@"end"]doubleValue])frameSource=stillImages[i];}
 CIImage *im=[frameSource imageByCroppingToRect:crop];CGAffineTransform t=CGAffineTransformMakeTranslation(-crop.origin.x,-crop.origin.y);t=CGAffineTransformConcat(t,CGAffineTransformMakeScale(z,z));t=CGAffineTransformConcat(t,CGAffineTransformMakeTranslation(x,y));im=[[im imageByApplyingTransform:t]imageByCompositingOverImage:canvas];im=[brand imageByCompositingOverImage:im];im=[tagline imageByCompositingOverImage:im];
 for(NSUInteger i=0;i<sectionImages.count;i++){NSDictionary *s=config[@"sections"][i];if(sec>=[s[@"start"]doubleValue]&&sec<[s[@"end"]doubleValue])im=[sectionImages[i]imageByCompositingOverImage:im];}
 CIImage *progress=[[CIImage imageWithColor:[CIColor colorWithRed:.408 green:.871 blue:.827]]imageByCroppingToRect:CGRectMake(60,130,1800*MIN(1,sec/duration),3)];im=[progress imageByCompositingOverImage:im];
 for(NSUInteger i=0;i<cards.count;i++){NSDictionary *card=config[@"cards"][i];if(sec>=[card[@"start"]doubleValue]&&sec<[card[@"end"]doubleValue])im=[cards[i]imageByCompositingOverImage:im];}
 for(NSUInteger i=0;i<noteImages.count;i++){NSDictionary *n=config[@"notes"][i];if(sec>=[n[@"start"]doubleValue]&&sec<[n[@"end"]doubleValue])im=[noteImages[i]imageByCompositingOverImage:im];}
 for(NSUInteger i=0;i<captionImages.count;i++){NSDictionary *cap=config[@"captions"][i];if(sec>=[cap[@"start"]doubleValue]&&sec<[cap[@"end"]doubleValue])im=[captionImages[i]imageByCompositingOverImage:im];}[request finishWithImage:[im imageByCroppingToRect:CGRectMake(0,0,w,h)] context:nil];
 }];video.renderSize=CGSizeMake(w,h);video.frameDuration=CMTimeMake(1,30);
 NSString *output=@(argv[4]);if([[NSFileManager defaultManager]fileExistsAtPath:output])die(@"Output exists");
 AVAssetExportSession *exporter=[[AVAssetExportSession alloc]initWithAsset:comp presetName:AVAssetExportPreset1920x1080];exporter.outputURL=[NSURL fileURLWithPath:output];exporter.outputFileType=AVFileTypeMPEG4;exporter.videoComposition=video;exporter.shouldOptimizeForNetworkUse=YES;exporter.timeRange=CMTimeRangeMake(kCMTimeZero,tm(duration));
 fprintf(stderr,"starting export\n");__block BOOL done=NO;[exporter exportAsynchronouslyWithCompletionHandler:^{done=YES;}];while(!done){[[NSRunLoop currentRunLoop]runUntilDate:[NSDate dateWithTimeIntervalSinceNow:.1]];}
 if(exporter.status!=AVAssetExportSessionStatusCompleted)die(exporter.error.description);puts(output.UTF8String);return 0;
}}
