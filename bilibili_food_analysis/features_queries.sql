-- 1. 播放量的最小值、最大值、平均值是多少？
SELECT max(播放) as 播放最大值, MIN(`播放`) as 播放最小值, round(AVG(播放),0) as 播放平均值
from video_features;

-- 2. 播放量的中位数是多少？
WITH t AS (
SELECT 播放, 
ROW_NUMBER() over(
ORDER BY `播放` 
)as pm ,
count(*) over() as cnt
FROM video_features
)
SELECT avg(播放) as 播放中位数 FROM t 
where pm in (FLOOR((cnt+1)/2),CEIL((cnt+1)/2));

-- 3. 播放量的90、75、25、10分位是多少？
WITH t AS (
SELECT 播放, 
ROW_NUMBER() over(
ORDER BY `播放` 
)as pm ,
count(*) over() as cnt
FROM video_features
)
SELECT 
sum(CASE when pm = CEIL(cnt*0.9) then 播放 else 0 end) as `播放90分位数`,
sum(CASE when pm = CEIL(cnt*0.75) then 播放 else 0 end) as `播放75分位数`,
sum(CASE when pm = CEIL(cnt*0.25) then 播放 else 0 end) as `播放25分位数`,
sum(CASE when pm = CEIL(cnt*0.1) then 播放 else 0 end) as `播放10分位数`
FROM t;

-- 4. 播放量>=1000的视频有多少行？占总样本的百分之多少？
with t as (
SELECT 播放 ,count(*) over() as cnt FROM video_features
)
SELECT count(播放) as `播放>=1000视频数` , round(count(播放)/max(cnt),3)*100 as `播放>=1000视频占比 %`
from t where 播放 >=1000; 

-- 5. 播放量>=10000的视频有多少行？占总样本的百分之多少？
with t as (
SELECT 播放 ,count(*) over() as cnt FROM video_features
)
SELECT count(播放) as `播放>=10000视频数` , round(count(播放)/max(cnt),3)*100 as `播放>=10000视频占比 %`
from t where 播放 >=10000; 

-- 6. 按时段分组，每个时段的平均互动率和样本数分别是多少？互动率最高的时段和最低的时段差多少倍？
with t as (
SELECT 时段, round(avg(`互动率`),3) as `平均互动率` ,count(*) as 视频数量
from video_features GROUP BY `时段` ORDER BY 平均互动率 desc
)
SELECT round(max(平均互动率) / (SELECT 平均互动率 FROM t where 时段 = '凌晨'),2) AS `最高/最低` FROM t;


-- 7. 按“是/否是工作日？”分组，平均互动率差多少？
SELECT 是否工作日 ,round(avg(`互动率`),3) as `平均互动率`, count(*) as 视频数量
FROM video_features GROUP BY `是否工作日`;

-- 8. 按标签数量分组，每组的平均互动率是多少？
SELECT max(`标签数量`) as 标签数量最大值, MIN(`标签数量`) as 标签数量最小值, round(AVG(标签数量),2) as 标签数量平均值 from video_features;

WITH t AS (
SELECT 标签数量, 
ROW_NUMBER() over(
ORDER BY `标签数量` 
)as pm ,
count(*) over() as cnt
FROM video_features
)
SELECT avg(`标签数量`) as 标签数量中位数 FROM t 
where pm in (FLOOR((cnt+1)/2),CEIL((cnt+1)/2));

with t as (
SELECT CASE 
	WHEN 标签数量 >=0 and 标签数量 <=3 THEN
		'0-3:标签较少'
  WHEN 标签数量 >=4 and 标签数量 <=7 THEN
		'4-7:标签适量'
	ELSE
    '8+：标签较多'
END as 标签数量等级,
互动率,标签数量 from video_features
)
SELECT 标签数量等级 ,round(avg(`互动率`),3) as `平均互动率`, count(*) as 视频数量
from t GROUP BY 标签数量等级;

-- 9. 按发布者聚合，统计每个UP主的投稿数和总播放量，按投稿数降序看前10名是谁、各投了多少稿？
SELECT 发布者, count(*) as 投稿数 , sum(播放) as 总播放量, round(avg(播放),1) AS 平均播放量,round(avg(`互动率`),3) AS 平均互动率
FROM video_features where 发布者 is NOT NULL AND 发布者 <> '#NAME?' 
GROUP BY 发布者 ORDER BY 投稿数 desc LIMIT 10;

-- 10. 把up主按投稿数分层，每一层的单条平均播放和单条平均互动率分别是多少？ 
WITH t1 as (
SELECT 发布者, count(*) as 投稿数 , sum(播放) as 总播放量, 
round(avg(播放),1) AS 平均播放量, round(avg(`互动率`),3) AS 平均互动率
FROM video_features WHERE 发布者 is NOT NULL AND 发布者 <> '#NAME?' 
GROUP BY 发布者 ORDER BY 投稿数 DESC
),
t2 as (
SELECT 发布者, 投稿数, 平均播放量, 平均互动率,
CASE 
	WHEN 投稿数 =1 THEN
		'1:投稿数唯一'
  WHEN 投稿数 >=2 and  投稿数 <=5 THEN
		'2-5:投稿数很少'
  WHEN 投稿数 >=6 and  投稿数 <=20 THEN
		'6-20:投稿数适量'
	ELSE
		'20+:投稿数较多'
END AS 投稿数等级 FROM t1
)
SELECT 投稿数等级 ,round(avg(平均播放量),1) AS 平均播放量, round(avg(平均互动率),3) AS 平均互动率
from t2 group by 投稿数等级;


-- 实际发现小播放量的视频的互动率虚高 -------
-- 查询互动率相关数值 ----
WITH t AS (
SELECT `互动率`, 
ROW_NUMBER() over(
ORDER BY `互动率`  DESC
)as pm ,
count(*) over() as cnt
FROM video_features where `互动率` is NOT NULL
)
SELECT
    (SELECT COUNT(*) FROM video_features WHERE 互动率 > 1) as `互动率>1的视频数`,
    (SELECT MAX(`互动率`)  FROM video_features) as 互动率最大值,
    (SELECT round(AVG(`互动率`),3) FROM video_features) AS 互动率均值,
    (SELECT round(AVG(`互动率`),3) FROM t WHERE pm IN (FLOOR((cnt+1)/2), CEIL((cnt+1)/2))) AS 互动率中位数;
-- 对播放量进行分组查询 ----
WITH t AS (
SELECT  `播放`, `互动率`,
    CASE
        WHEN 播放 < 100 THEN '<100'
        WHEN 播放 < 1000 AND 播放 >=100 THEN '100-1k'
        WHEN 播放 < 10000 AND 播放 >=1000 THEN '1k-1w'
        WHEN 播放 < 100000 AND 播放 >=10000 THEN '1w-10w'
        ELSE '>10w'
    END AS 播放量等级
FROM video_features where  `互动率` is not null
),
t_rank AS (
SELECT 播放量等级, `互动率`,
    ROW_NUMBER() OVER(PARTITION BY 播放量等级 ORDER BY `互动率` ) AS rn,
    COUNT(*) OVER(PARTITION BY 播放量等级) AS grp_cnt
FROM t
)
SELECT 
    播放量等级,
    MAX(grp_cnt) AS 视频数量,
    ROUND(AVG(`互动率`),3) AS 互动率均值,
    ROUND(AVG(CASE WHEN rn IN (FLOOR((grp_cnt+1)/2), CEIL((grp_cnt+1)/2)) THEN `互动率` END),3) AS 互动率中位数
FROM t_rank
GROUP BY 播放量等级
ORDER BY FIELD(播放量等级, '<100','100-1k','1k-1w','1w-10w','>10w');

-- 在过滤较低样本之后（播放>=1000）重新查询一些问题 ---
-- 8(改进版)按标签数量分组，每组的平均互动率、互动率中位数是多少？
with t as (
SELECT CASE 
	WHEN 标签数量 >=0 and 标签数量 <=3 THEN
		'0-3:标签较少'
  WHEN 标签数量 >=4 and 标签数量 <=7 THEN
		'4-7:标签适量'
	ELSE
    '8+：标签较多'
END as 标签数量等级,
互动率,标签数量,`播放` from video_features WHERE 播放 >=1000
),
t_rank AS (
SELECT 标签数量等级, 互动率, 
ROW_NUMBER() over(PARTITION by 标签数量等级 ORDER BY `互动率`) as rn,
count(*) over(PARTITION by 标签数量等级) as grp_cnt 
from t 
)
SELECT 标签数量等级,
    MAX(grp_cnt) AS 视频数量,
    ROUND(AVG(`互动率`),3) AS 互动率均值,
    ROUND(AVG(CASE WHEN rn IN (FLOOR((grp_cnt+1)/2), CEIL((grp_cnt+1)/2)) THEN `互动率` END),3) AS 互动率中位数
FROM t_rank 
GROUP BY 标签数量等级;

-- 6(改进版)按时段分组，每个时段的平均互动率、互动率中位数和样本数分别是多少？互动率最高的时段和最低的时段差多少倍？
with t as (
SELECT 时段, 互动率,
ROW_NUMBER() over(PARTITION by 时段 ORDER BY 互动率) as rn,
count(*) over (PARTITION by 时段) as grp_cnt 
FROM video_features where 播放 >= 1000
)
SELECT 时段,
    MAX(grp_cnt) AS 视频数量,
    ROUND(AVG(`互动率`),3) AS 互动率均值,
    ROUND(AVG(CASE WHEN rn IN (FLOOR((grp_cnt+1)/2), CEIL((grp_cnt+1)/2)) THEN `互动率` END),3) AS 互动率中位数
FROM t
GROUP BY 时段
ORDER BY FIELD('上午','下午','晚上','凌晨','未知');

-- 10(改进版)把up主按投稿数分层，每一层的单条平均播放和单条平均互动率、互动率中位数分别是多少？
WITH t1 as (
SELECT 发布者, count(*) as 投稿数 , sum(播放) as 总播放量, 
round(avg(播放),1) AS 平均播放量, round(avg(`互动率`),3) AS 平均互动率
FROM video_features WHERE 发布者 is NOT NULL AND 发布者 <> '#NAME?'  and 播放 >=1000
GROUP BY 发布者 ORDER BY 投稿数 DESC
),
t2 as (
SELECT 发布者, 投稿数, 平均播放量, 平均互动率,
CASE 
	WHEN 投稿数 =1 THEN
		'1:投稿数唯一'
  WHEN 投稿数 >=2 and  投稿数 <=5 THEN
		'2-5:投稿数很少'
  WHEN 投稿数 >=6 and  投稿数 <=20 THEN
		'6-20:投稿数适量'
	ELSE
		'20+:投稿数较多'
END AS 投稿数等级 FROM t1
),
t_rank as (
SELECT 投稿数等级, 平均播放量, 平均互动率, 
ROW_NUMBER() over(PARTITION by 投稿数等级 ORDER BY 平均互动率) as rn,
count(*) over (PARTITION by 投稿数等级) as grp_cnt 
FROM t2
)
SELECT 投稿数等级,
    ROUND(AVG(平均播放量),0) as 平均播放量,
    ROUND(AVG(平均互动率),4) AS 互动率均值,
    ROUND(AVG(CASE WHEN rn IN (FLOOR((grp_cnt+1)/2), CEIL((grp_cnt+1)/2)) THEN 平均互动率 END),4) AS 互动率中位数
FROM t_rank
GROUP BY 投稿数等级
ORDER BY FIELD(投稿数等级, '1:投稿数唯一','2-5:投稿数很少','6-20:投稿数适量','20+:投稿数较多');


-- 进一步分析播放区间与标签数量交叉之后的平均互动率是多少？ --
WITH t AS (
SELECT
  CASE
      WHEN 播放 < 10000 AND 播放 >=1000 THEN '1k-1w'
      WHEN 播放 < 100000 AND 播放 >=10000 THEN '1w-10w'
      ELSE '>10w'
  END AS 播放量等级,
  CASE  
    WHEN 标签数量 >=0 and 标签数量 <=3 THEN '0-3:标签较少'
    WHEN 标签数量 >=4 and 标签数量 <=7 THEN '4-7:标签适量'
    ELSE
    '8+：标签较多'
  END as 标签数量等级,
  `互动率`
FROM video_features WHERE 播放 >=1000 and `互动率`is NOT NULL
)
SELECT 播放量等级,
round(avg(case when 标签数量等级 = '0-3:标签较少' then `互动率` end),3) as '0-3:标签较少',
round(avg(case when 标签数量等级 = '4-7:标签适量' then `互动率` end),3) as '4-7:标签适量',
round(avg(case when 标签数量等级 = '8+：标签较多' then `互动率` end),3) as '8+：标签较多'
from t
GROUP BY 播放量等级
ORDER BY FIELD(播放量等级, '1k-1w','1w-10w','>10w');

-- 进一步分析播放区间与标签数量交叉之后的互动率中位数是多少？ --
WITH t1 AS (
SELECT
  CASE
      WHEN 播放 < 10000 AND 播放 >=1000 THEN '1k-1w'
      WHEN 播放 < 100000 AND 播放 >=10000 THEN '1w-10w'
      ELSE '>10w'
  END AS 播放量等级,
  CASE  
    WHEN 标签数量 >=0 and 标签数量 <=3 THEN '0-3:标签较少'
    WHEN 标签数量 >=4 and 标签数量 <=7 THEN '4-7:标签适量'
    ELSE
    '8+：标签较多'
  END as 标签数量等级,
  `互动率`
FROM video_features WHERE 播放 >=1000 and `互动率`is NOT NULL
),
t2 AS (
SELECT  播放量等级, 标签数量等级, 互动率,
ROW_NUMBER() over(PARTITION BY 播放量等级, 标签数量等级 ORDER BY `互动率`) as rn,
COUNT(*) over(PARTITION BY 播放量等级, 标签数量等级) as grp_cnt
from t1  
),
t3 as (
SELECT 播放量等级, 标签数量等级,
avg(互动率) as 互动率中位数, max(grp_cnt) as 样本数
from t2 where rn IN (FLOOR((grp_cnt+1)/2), CEIL((grp_cnt+1)/2))
GROUP BY 播放量等级, 标签数量等级
)
SELECT 播放量等级,
round(max(case when 标签数量等级 = '0-3:标签较少' then `互动率中位数` end),3) as '0-3:标签较少',
round(max(case when 标签数量等级 = '4-7:标签适量' then `互动率中位数` end),3) as '4-7:标签适量',
round(max(case when 标签数量等级 = '8+：标签较多' then `互动率中位数` end),3) as '8+：标签较多'
from t3 
GROUP BY 播放量等级
ORDER BY FIELD(播放量等级, '1k-1w','1w-10w','>10w');


