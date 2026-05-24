# ⚠️ 警告：请勿在此文件中硬编码API密钥！
# 请使用环境变量或config.json文件来配置API密钥。
# 优先级：环境变量 > config.json > 抛出错误。
#
# 设置方法：
# 1. 环境变量：export OPENAI_API_KEY="sk-..."
# 2. 配置文件：在项目根目录创建config.json，内容如：{"OPENAI_API_KEY": "sk-..."}
# 3. .env文件：在项目根目录创建.env文件，内容如：OPENAI_API_KEY=sk-...

OPENAI_API_KEY_FALLBACK: str = ""  # 已移除硬编码密钥，请使用环境变量或配置文件


