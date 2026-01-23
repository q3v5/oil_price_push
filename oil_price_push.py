import requests
import json

def send_oil_price_msg(webhook_url):
    # 消息头指定JSON格式
    headers = {'Content-Type': 'application/json'}
    # 构造Markdown格式的油价消息
    markdown_content = """
# 内蒙古油价更新信息
**最近调整日期**：2026-01-21

| 油价标号 | 当前油价（元/升） | 上次油价（元/升） | 涨跌（元/升） | 涨跌率 |
|----------|------------------|------------------|--------------|--------|
| 92号汽油 | 6.77             | 6.71             | +0.06        | 0.89%  |
| 95号汽油 | 7.19             | 7.12             | +0.07        | 0.98%  |
| 98号汽油 | 7.86             | 7.78             | +0.08        | 1.03%  |

**下一次油价调整时间**：2026-01-30
    """
    # 企业微信机器人消息体（指定msgtype为markdown）
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": markdown_content.strip()
        }
    }
    # 发送请求
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
    return response.json()

# 替换为你的企业微信机器人webhook地址（在机器人设置中复制）
webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的机器人key"
# 执行推送
result = send_oil_price_msg(webhook)
print("推送结果：", result)
