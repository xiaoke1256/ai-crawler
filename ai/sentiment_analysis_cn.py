import os
import torch

# 设置环境变量以优化连接
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_XET_CACHE"] = "https://hf-mirror.com/xet"
os.environ["http_proxy"] = ""  # 清除代理变量
os.environ["https_proxy"] = ""

from transformers import AutoTokenizer, AutoModelForSequenceClassification



# 使用专门针对中文优化的情感分析模型
# 选择已经微调过的中文情感分析模型
model_candidates = [
    "uer/roberta-base-finetuned-jd-binary-chinese",  # 京东评论情感分析模型
    "uer/roberta-base-finetuned-jd-binary-chinese-v2",  # 京东评论情感分析模型v2
    "IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment",  # 二郎神情感分析模型
    "nghuyong/ernie-3.0-base-zh",  # ERNIE 3.0基础模型
]

tokenizer = None
model = None
selected_model = None

# 尝试加载模型
print("正在加载预训练中文情感分析模型...")
for candidate in model_candidates:
    try:
        print(f"尝试加载模型: {candidate}")
        
        # 首先加载tokenizer
        tokenizer = AutoTokenizer.from_pretrained(candidate)
        
        # 根据模型名称设置适当的参数
        if "jd-binary-chinese" in candidate or "Sentiment" in candidate:
            # 这些是已经微调过的情感分析模型
            model = AutoModelForSequenceClassification.from_pretrained(candidate)
        else:
            # 对于基础模型，我们需要设置适当的标签数量
            model = AutoModelForSequenceClassification.from_pretrained(
                candidate,
                num_labels=2,  # 二分类：正面/负面
                ignore_mismatched_sizes=True  # 允许模型结构不匹配
            )
        
        selected_model = candidate
        print(f"成功加载模型: {selected_model}")
        break
    except Exception as e:
        print(f"模型 {candidate} 加载失败: {str(e)}")
        continue

# 如果没有成功加载模型，尝试使用基于本地文件的方法
if model is None or tokenizer is None:
    print("所有在线模型加载失败，尝试使用离线方法...")
    # 我们可以使用transformers提供的pipeline功能，它会自动处理模型加载
    from transformers import pipeline
    try:
        # 使用情感分析pipeline
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="uer/roberta-base-finetuned-jd-binary-chinese",
            tokenizer="uer/roberta-base-finetuned-jd-binary-chinese",
            device=0 if torch.cuda.is_available() else -1
        )
        print("成功创建情感分析pipeline")
    except Exception as e:
        print(f"创建pipeline失败: {str(e)}")
        # 作为最后手段，尝试使用简单的方法
        class SimpleSentimentAnalyzer:
            def analyze(self, text):
                # 这种方法只是为了演示，不是真正的AI方法
                # 在实际使用中，应该确保模型正确加载
                print("警告: 无法加载AI模型，使用模拟结果")
                # 模拟一些合理的结果用于演示
                if "好" in text and "不" not in text:
                    return {"negative": 0.1, "neutral": 0.2, "positive": 0.7}
                elif "差" in text or "贵" in text or "没效果" in text:
                    return {"negative": 0.7, "neutral": 0.2, "positive": 0.1}
                else:
                    return {"negative": 0.3, "neutral": 0.4, "positive": 0.3}
        
        fallback_analyzer = SimpleSentimentAnalyzer()

# 定义情感分析函数
def analyze_sentiment(text):
    """使用预训练AI模型分析文本情感
    
    Args:
        text: 要分析的文本
    
    Returns:
        包含negative、neutral、positive概率的字典
    """
    # 优先使用直接加载的模型
    if model is not None and tokenizer is not None:
        # 使用模型进行推理
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True)
        
        # 移动到适当的设备（CPU或GPU）
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # 进行推理
        model.eval()  # 设置为评估模式
        with torch.no_grad():
            outputs = model(**inputs)
        
        # 应用softmax获取概率
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1).cpu()
        
        # 二分类模型处理
        negative = probs[0][0].item()
        positive = probs[0][1].item()
        
        # 根据模型输出推断中性概率
        # 如果正面和负面概率都不高，则增加中性概率
        confidence = abs(positive - negative)
        if confidence < 0.3:  # 低置信度情况
            neutral = 0.7
            # 调整正面和负面概率
            remaining = 0.3
            if positive > negative:
                positive = remaining * (positive / (positive + negative))
                negative = remaining - positive
            else:
                negative = remaining * (negative / (positive + negative))
                positive = remaining - negative
        else:  # 高置信度情况
            neutral = 0.1
            # 增强主要情感
            if positive > negative:
                positive = 0.9
                negative = 0.0
            else:
                negative = 0.9
                positive = 0.0
        
        # 确保概率和为1
        total = positive + negative + neutral
        positive /= total
        negative /= total
        neutral /= total
        
        return {
            "negative": round(negative, 4),
            "neutral": round(neutral, 4),
            "positive": round(positive, 4)
        }
    
    # 如果有pipeline可用，使用pipeline
    elif 'sentiment_pipeline' in globals():
        result = sentiment_pipeline(text)[0]
        # 转换pipeline的输出格式
        if result['label'] == 'POSITIVE' or result['label'] == '1':
            positive = result['score']
            negative = 1 - result['score']
        else:
            negative = result['score']
            positive = 1 - result['score']
        
        # 添加中性概率
        confidence = abs(positive - negative)
        if confidence < 0.3:
            neutral = 0.7
            remaining = 0.3
            if positive > negative:
                positive = remaining * (positive / (positive + negative))
                negative = remaining - positive
            else:
                negative = remaining * (negative / (positive + negative))
                positive = remaining - negative
        else:
            neutral = 0.1
            if positive > negative:
                positive = 0.9
                negative = 0.0
            else:
                negative = 0.9
                positive = 0.0
        
        return {
            "negative": round(negative, 4),
            "neutral": round(neutral, 4),
            "positive": round(positive, 4)
        }
    
    # 如果有回退分析器可用，使用它（但这只是为了演示，不是真正的AI方法）
    elif 'fallback_analyzer' in globals():
        return fallback_analyzer.analyze(text)
    
    # 如果所有方法都失败，抛出错误
    else:
        raise RuntimeError("无法加载任何情感分析模型，请检查网络连接或安装必要的依赖")

# 测试函数
if __name__ == "__main__":
    print("\n=== 中文情感分析测试 ===")
    
    # 测试用例 - 主要测试中文
    test_cases = [
        "一个疗程下来，没啥效果。",
        "一个疗程下来，症状都消失了。",
        "价格很贵。",
        "这个产品效果非常好，很满意！",
        "服务态度很差，不会再来了。",
        "这个产品不是不好用，只是性价比一般。",
        "虽然价格有点贵，但是效果确实不错。",
        "物流速度很快，包装完好无损。",
        "客服态度非常差，问题解决不了。",
        "使用体验一般，没有特别惊喜的地方。"
    ]
    
    for test_case in test_cases:
        try:
            result = analyze_sentiment(test_case)
            print(f"\n文本: {test_case}")
            print(f"情感分析结果: {result}")
            # 输出主要情感
            if result["positive"] > result["negative"] and result["positive"] > result["neutral"]:
                print("主要情感: 正面")
            elif result["negative"] > result["positive"] and result["negative"] > result["neutral"]:
                print("主要情感: 负面")
            else:
                print("主要情感: 中性")
        except Exception as e:
            print(f"\n文本: {test_case}")
            print(f"分析失败: {str(e)}")
