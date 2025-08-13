from fastapi import FastAPI, HTTPException
import time
import random

app = FastAPI()

# 1. MCP服务描述接口（告诉大模型如何调用）
@app.get("/mcp/describe")
def describe():
    return {
        "name": "PoetryQuery",
        "description": "查询中国古诗词，支持按关键词或朝代筛选",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "查询关键词（如“月”“思乡”，为空则随机返回）"
                },
                "dynasty": {
                    "type": "string",
                    "enum": ["唐", "宋", "元", "明", "清"],
                    "description": "朝代筛选（可选，如“唐”“宋”）"
                }
            }
        }
    }

# 2. 本地模拟古诗词数据（避免依赖外部接口，确保稳定性）
mock_poetry = {
    "唐": [
        {
            "title": "静夜思",
            "author": "李白",
            "content": "床前明月光，疑是地上霜。举头望明月，低头思故乡。",
            "keywords": ["月", "思乡"]
        },
        {
            "title": "望庐山瀑布",
            "author": "李白",
            "content": "日照香炉生紫烟，遥看瀑布挂前川。飞流直下三千尺，疑是银河落九天。",
            "keywords": ["自然", "瀑布"]
        }
    ],
    "宋": [
        {
            "title": "水调歌头·明月几时有",
            "author": "苏轼",
            "content": "明月几时有？把酒问青天。不知天上宫阙，今夕是何年……但愿人长久，千里共婵娟。",
            "keywords": ["月", "思念"]
        },
        {
            "title": "如梦令·昨夜雨疏风骤",
            "author": "李清照",
            "content": "昨夜雨疏风骤，浓睡不消残酒。试问卷帘人，却道海棠依旧。知否，知否？应是绿肥红瘦。",
            "keywords": ["花", "春雨"]
        }
    ],
    "元": [
        {
            "title": "天净沙·秋思",
            "author": "马致远",
            "content": "枯藤老树昏鸦，小桥流水人家，古道西风瘦马。夕阳西下，断肠人在天涯。",
            "keywords": ["秋", "思乡"]
        }
    ]
}

# 3. MCP服务调用接口（核心逻辑）
@app.post("/mcp/call")
def call(data: dict):
    keyword = data.get("keyword", "").strip()
    dynasty = data.get("dynasty")

    # 校验朝代参数
    if dynasty and dynasty not in mock_poetry:
        raise HTTPException(status_code=400, detail="不支持的朝代，请从['唐', '宋', '元', '明', '清']中选择")

    # 筛选诗词（先按朝代，再按关键词）
    candidates = []
    # 1. 筛选朝代
    if dynasty:
        candidates = mock_poetry[dynasty]
    else:
        # 不指定朝代则合并所有数据
        for poems in mock_poetry.values():
            candidates.extend(poems)

    # 2. 筛选关键词
    if keyword:
        keyword_matched = []
        for poem in candidates:
            # 检查标题、内容、关键词是否包含查询词
            if (keyword in poem["title"] or
                keyword in poem["content"] or
                keyword in poem["keywords"]):
                keyword_matched.append(poem)
        candidates = keyword_matched

    # 3. 处理无结果的情况
    if not candidates:
        return {"error": "未找到匹配的古诗词，请尝试其他关键词或朝代"}

    # 4. 随机返回一首
    result = random.choice(candidates)

    return {
        "title": result["title"],
        "author": result["author"],
        "dynasty": dynasty if dynasty else "不限",
        "content": result["content"],
        "query_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # 端口8002，避免冲突
