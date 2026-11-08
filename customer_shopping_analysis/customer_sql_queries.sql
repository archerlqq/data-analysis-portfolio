-- 数据总览
-- 营收（SUM）
SELECT category AS dim, SUM(purchase_amount) AS revenue FROM customer GROUP BY category;
SELECT age_group AS dim, SUM(purchase_amount) AS revenue FROM customer GROUP BY age_group;

-- 销量（COUNT）
SELECT category AS dim, COUNT(*) AS sales FROM customer GROUP BY category;
SELECT age_group AS dim, COUNT(*) AS sales FROM customer GROUP BY age_group;

-- 订阅占比（COUNT）
SELECT subscription_status AS dim, COUNT(*) AS cnt FROM customer GROUP BY subscription_status;


-- Q1. male vs females 各自总营收、客单价对比
SELECT gender, sum(purchase_amount) as sum_amount,
round(avg(purchase_amount),2) as  avg_amount
from customer
GROUP BY gender;

-- Q2. 折扣对于高消费客户的影响，使用了折扣但是消费仍然高于均值的客户
SELECT customer_id, purchase_amount
from customer
where discount_applied = 'yes'
and purchase_amount >= (SELECT avg(purchase_amount) FROM customer);

-- Q3. 哪些商品口碑最好？平均评分最高的五个商品
SELECT item_purchased, round(avg(review_rating),2) as avg_review
from customer
GROUP BY item_purchased
ORDER BY avg_review DESC
limit 5;

-- Q4. 配送方式与消费的关系，standard vs express 
SELECT shipping_type, round(avg(purchase_amount),2) AS avg_amount
from customer
group by shipping_type
ORDER BY avg_amount;

-- Q5. 订阅客户是否消费的更多，订阅客户的人数、平均消费、总消费
SELECT subscription_status, 
count(customer_id) as total_customers, 
round(avg(purchase_amount),2) as avg_amount,
sum(purchase_amount) as total_amount
from customer
GROUP BY subscription_status;

-- Q6. 商品的售卖与折购关系，折扣使用率最高的5个商品
WITH t1 as (
SELECT item_purchased ,count(item_purchased) as count_t1 from customer GROUP BY item_purchased ),
t2 as (
SELECT item_purchased,count(item_purchased) as count_t2 
FROM customer where discount_applied = 'yes' GROUP BY item_purchased)
SELECT t1.item_purchased,round(t2.count_t2 / t1.count_t1,4) as discount_rate
from t1 join t2 on t1.item_purchased = t2.item_purchased
ORDER BY discount_rate DESC
limit 5;

-- Q7. 对客户进行分层，按照历史购买次数分“新客(1)、回头客(2-10)、忠诚客”
with t as (
SELECT customer_id,
CASE 
	WHEN previous_purchases <= 1 THEN
		'新客'
  when previous_purchases >=2 and previous_purchases <= 10 THEN
    '回头客'
	ELSE
		'忠诚客'
END as  customer_segment
FROM customer)
SELECT customer_segment,
count(*)
from t GROUP BY customer_segment;

-- Q8. 每个品类内购买次数前三的商品
with t1 as (
SELECT category, item_purchased ,count(*) as total_orders 
from customer GROUP BY category,item_purchased
),
t2 as (
SELECT 
ROW_NUMBER() over (
partition by category
ORDER BY total_orders DESC
) as item_rank,
category,item_purchased,total_orders
FROM t1
)
SELECT t2.*
from t2 where item_rank <= 3;

-- Q9. 历史购买次数>10次的客户是否更可能订阅，比较在历史购买次数>10次的客户的订阅与非订阅情况
SELECT subscription_status, COUNT(*) as repeat_buyers
from customer where previous_purchases > 10
GROUP BY subscription_status;

-- Q10. 不同年龄阶段对于总销售额的影响
SELECT age_group, sum(purchase_amount) as total_amount
from customer GROUP BY age_group ORDER BY total_amount DESC;

-- Q11. 不同品类中使用折扣的订单占比多少
SELECT Category ,
round(sum(case when discount_applied = 'yes' then 1 ELSE 0 END) / COUNT(*),4) as rate_discount
from customer GROUP BY category order by rate_discount DESC;

-- Q12. 订阅与非订阅用户的历史购买次数>10的占比比较
SELECT subscription_status ,
round(sum(case when previous_purchases > 10 then 1 else 0 end) / COUNT(*),4) as rate
from customer GROUP BY subscription_status; 