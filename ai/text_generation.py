import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 设置环境变量
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_XET_CACHE"] = "https://hf-mirror.com/xet"
os.environ["http_proxy"] = ""  # 清除代理变量
os.environ["https_proxy"] = ""
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"  # 禁用符号链接警告

# 延迟导入以避免启动时出错
def continue_text(prompt, max_length=100):
    """
    使用DeepSeek模型进行文本续写
    
    Args:
        prompt: 输入的文本提示
        max_length: 生成文本的最大长度
    
    Returns:
        续写后的文本
    """
    # 验证输入
    if not prompt or not isinstance(prompt, str) or len(prompt.strip()) == 0:
        logging.warning("输入文本为空或无效")
        return "[警告] 输入文本为空或无效"
    
    try:
        logging.info(f"开始文本续写，输入长度: {len(prompt)}")
        
        # 导入transformers库
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        # 使用正确的DeepSeek模型名称
        # 选择一个体积较小的、常用的DeepSeek模型
        model_name = "deepseek-ai/deepseek-coder-1.3b-base"  # 这个模型较小，更容易下载
        logging.info(f"正在加载模型: {model_name}")
        
        # 加载tokenizer，使用local_files_only=False允许从远程下载
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            local_files_only=False,
            trust_remote_code=True,  # DeepSeek模型可能需要这个选项
            cache_dir="./cache"  # 指定缓存目录
        )
        logging.info("Tokenizer加载成功")
        
        # 加载模型，设置低内存模式
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            local_files_only=False,
            trust_remote_code=True,
            cache_dir="./cache",
            low_cpu_mem_usage=True,  # 低内存模式
            torch_dtype="auto"  # 自动选择合适的数据类型
        )
        logging.info("模型加载成功")
        
        # 将模型移至CPU
        model = model.to("cpu")
        
        # 将输入文本编码为token
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # 生成续写文本
        logging.info("开始生成文本...")
        # 生成续写文本，优化参数减少重复
        outputs = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,  # 添加attention_mask解决警告
            max_length=min(max_length, 200),  # 限制最大长度
            num_return_sequences=1,
            do_sample=True,
            temperature=0.6,  # 降低temperature减少随机性
            top_p=0.9,  # 控制采样分布
            repetition_penalty=1.5,  # 添加重复惩罚
            no_repeat_ngram_size=3,  # 避免3-gram重复
            num_beams=4,  # 使用beam search
            early_stopping=True,  # 提前停止
            pad_token_id=tokenizer.eos_token_id
        )
        
        # 解码生成的文本
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logging.info(f"文本生成完成，输出长度: {len(generated_text)}")
        
        return generated_text
        
    except Exception as e:
        error_message = str(e)
        logging.error(f"生成文本时出错: {error_message}")
        # 提供具体的错误信息和建议
        return f"AI生成过程中发生错误: {error_message}\n建议: 请检查网络连接、模型名称是否正确，或尝试使用较小的模型。"

if __name__ == "__main__":
    print("=== 开始文本续写测试 ===")
    input_text = "自盘古开天劈地以来，"
    print(f"输入文本: {input_text}")
    print("\n续写结果:")
    result = continue_text(input_text)
    print(result)
    print("\n=== 测试完成 ===")