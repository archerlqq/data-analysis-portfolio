-- 1. 重复检查，检查一个视频是否出现多次
SELECT `标题`, `总播放数`, `总弹幕数`, `发布时间`, `发布者`,`点赞数`,`金币数`,
`收藏量`,`分享数`,`视频介绍`,`标签`,`评论数`,
 count(*) as cnt  from  video_raw 
GROUP BY `标题`,`总播放数`, `总弹幕数`, `发布时间`, `发布者`,`点赞数`,`金币数`,
`收藏量`,`分享数`,`视频介绍`,`标签`,`评论数` HAVING cnt <> 1 ORDER BY cnt DESC;

-- 2. 缺失检查，检查哪些列存在null，有多少行是空的？
SELECT 
SUM(`标题` IS NULL) AS `标题缺失`,
SUM(`总播放数` IS NULL) AS `总播放数缺失`,
SUM(`总弹幕数` IS NULL) AS `总弹幕数缺失`,
SUM(`发布时间` IS NULL) AS `发布时间缺失`,
SUM(`发布者` IS NULL) AS `发布者缺失`,
SUM(`点赞数` IS NULL) AS `点赞数缺失`,
SUM(`金币数` IS NULL) AS `金币数缺失`,
SUM(`收藏量` IS NULL) AS `收藏量缺失`,
SUM(`分享数` IS NULL) AS `分享数缺失`,
SUM(`视频介绍` IS NULL) AS `视频介绍缺失`,
SUM(`标签` IS NULL) AS `标签缺失`,
SUM(`评论数` IS NULL) AS `评论数缺失`
FROM video_raw;

-- 3. 总播放量的数值形态检查，有多少行包含“万”字？有多少行是纯数字？
SELECT count(`总播放数`) as `播放数有“万”字` from video_raw where `总播放数` REGEXP '万';

-- 4. 点赞数、金币数、收藏量、分享数里有多少行不是数字，而是“点赞”、“投币”这类文字？
SELECT
SUM(CASE WHEN `点赞数` NOT REGEXP '^[0-9]+$' THEN 1 ELSE 0 END) AS `点赞数中纯文字`,
SUM(CASE WHEN `金币数` NOT REGEXP '^[0-9]+$' THEN 1 ELSE 0 END) AS `金币数中纯文字`,
SUM(CASE WHEN `收藏量` NOT REGEXP '^[0-9]+$' THEN 1 ELSE 0 END) AS `收藏量中纯文字`,
SUM(CASE WHEN `分享数` NOT REGEXP '^[0-9]+$' THEN 1 ELSE 0 END) AS `分享数中纯文字`
FROM video_raw;

-- 5. 播放数为0的视频有多少？
SELECT count(`总播放数`) as `播放数为0` from video_raw where `总播放数` REGEXP '(0播放)';

-- 6. 发布时间格式检查
SELECT count(*) as `时间格式异常` FROM video_raw 
where STR_TO_DATE(`发布时间`,'%Y/%m/%d %H:%i') is NULL;

SELECT count(*) as `时间格式异常` FROM video_features 
where STR_TO_DATE(`发布时间`,'%Y/%m/%d %H:%i') is NULL;
SELECT SUM(`发布时间` IS NULL) AS `发布时间缺失` FROM video_features;
