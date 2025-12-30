#!/bin/bash

# 实验参数配置
product=8           # 目标产品索引（1-based）
run=3                 # 实验运行编号
catalog="coffee_machines"  # 产品目录
model_id="meta.llama3-70b-instruct-v1:0"  # Bedrock模型ID
region="us-east-1"      # AWS区域
user_msg_type="default"  # 用户消息类型
num_sts_chars=30        # STS字符长度
top_k=20                # 每次优化的候选数量

# 创建结果保存目录
results_dir="results2/${catalog}/${model_id}/${user_msg_type}/product${product}/run${run}"
mkdir -p ${results_dir}

# 定义日志文件路径（放在结果目录下，方便关联实验结果）
log_file="${results_dir}/experiment.log"

# 运行Bedrock版本优化脚本
python rank_opt_api.py \
    --results_dir ${results_dir} \
    --catalog ${catalog} \
    --user_msg_type ${user_msg_type} \
    --target_product_idx ${product} \
    --num_iter 50 \
    --test_iter 1 \
    --model_id ${model_id} \
    --region ${region} \
    --num_sts_chars ${num_sts_chars} \
    --top_k ${top_k} \
    --random_order \
    --save_state > ${log_file} 2>&1

# 输出节点信息（同样写入日志，若在集群环境运行）
echo "运行节点: $SLURM_NODELIST" >> ${log_file} 2>&1

# 可选：脚本结束后提示日志位置，方便查看
echo "实验已完成！日志文件保存至: ${log_file}"