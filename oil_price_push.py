import requests
import json
import os
from datetime import datetime

# -------------------------- 从环境变量读取配置 --------------------------
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")  # PushPlus令牌
TANSHU_API_KEY = os.getenv("TANSHU_API_KEY")  # 天极API秘钥
QY_WECHAT_WEBHOOK_KEY = os.getenv("QY")  # 企业微信Webhook Key（可选）
# ------------------------------------------------------------------------------

def calculate_change_percent(change, previous_price):
    """计算油价涨跌率"""
    try:
        if not change or change.strip() == "" or change == "0.00":
            return "暂无数据"
        if not previous_price or previous_price.strip() == "" or previous_price == "0.00":
            return "暂无数据"
        
        change_float = float(change)
        previous_float = float(previous_price)
        
        if previous_float == 0:
            return "暂无数据"
        
        percent = (change_float / previous_float) * 100
        return f"{percent:.2f}%"
    except (ValueError, TypeError):
        return "暂无数据"

def get_neimenggu_oil_price():
    """获取内蒙古油价数据，返回JSON、HTML、Markdown格式内容"""
    try:
        api_url = "https://apis.tianapi.com/oilprice/market"
        request_params = {
            "key": TANSHU_API_KEY,
            "prov": "内蒙古"
        }
        
        response = requests.get(
            url=api_url,
            params=request_params,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        api_result = response.json()

        if not isinstance(api_result, dict) or api_result.get("code") != 200:
            error_msg = f"油价接口返回失败：{api_result.get('msg', '未知错误')}" if api_result else "油价接口返回空"
            return {}, error_msg, "", "", "", False

        oil_raw_data = api_result.get("result", {})
        oil_json = {
            "province": oil_raw_data.get("prov", "内蒙古"),
            "last_change_date": "",
            "next_change_date": "暂无数据",
            "oil_detail": {
                "92号汽油": {
                    "current_price": oil_raw_data.get("p92", {}).get("price", "暂无数据"),
                    "last_price": oil_raw_data.get("p92", {}).get("previous_price", "暂无数据"),
                    "change": oil_raw_data.get("p92", {}).get("price_change", "暂无数据"),
                    "change_percent": ""
                },
                "95号汽油": {
                    "current_price": oil_raw_data.get("p95", {}).get("price", "暂无数据"),
                    "last_price": oil_raw_data.get("p95", {}).get("previous_price", "暂无数据"),
                    "change": oil_raw_data.get("p95", {}).get("price_change", "暂无数据"),
                    "change_percent": ""
                },
                "98号汽油": {
                    "current_price": oil_raw_data.get("p98", {}).get("price", "暂无数据"),
                    "last_price": oil_raw_data.get("p98", {}).get("previous_price", "暂无数据"),
                    "change": oil_raw_data.get("p98", {}).get("price_change", "暂无数据"),
                    "change_percent": ""
                }
            }
        }

        # 计算涨跌率并补充符号
        for oil_type in ["92号汽油", "95号汽油", "98号汽油"]:
            change = oil_json["oil_detail"][oil_type]["change"]
            last_price = oil_json["oil_detail"][oil_type]["last_price"]
            oil_json["oil_detail"][oil_type]["change_percent"] = calculate_change_percent(change, last_price)
            
            if change != "暂无数据" and change.strip() != "":
                try:
                    change_float = float(change)
                    if change_float > 0:
                        oil_json["oil_detail"][oil_type]["change"] = f"+{change}"
                except ValueError:
                    pass

        # 格式化日期
        raw_last_date = oil_raw_data.get("last_adjusted", "")
        if raw_last_date and len(raw_last_date) == 8 and raw_last_date.isdigit():
            oil_json["last_change_date"] = f"{raw_last_date[:4]}-{raw_last_date[4:6]}-{raw_last_date[6:8]}"
        raw_next_date = oil_raw_data.get("next_adjustment", "")
        if raw_next_date and len(raw_next_date) == 8 and raw_next_date.isdigit():
            oil_json["next_change_date"] = f"{raw_next_date[:4]}-{raw_next_date[4:6]}-{raw_next_date[6:8]}"

        # 生成HTML内容（PushPlus用）
        table_html = f"""
<h3>内蒙古油价更新信息</h3>
<p>最近调整日期：{oil_json['last_change_date'] or '暂无数据'}</p>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; text-align: center;">
  <tr style="background-color: #f0f0f0; font-weight: bold;">
    <<th>油价标号</</th>
    <<th>当前油价（元/升）</</th>
    <<th>上次油价（元/升）</</th>
    <<th>涨跌（元/升）</</th>
    <<th>涨跌率</</th>
  </tr>
  <tr>
    <td>92号汽油</td>
    <td>{oil_json['oil_detail']['92号汽油']['current_price']}</td>
    <td>{oil_json['oil_detail']['92号汽油']['last_price']}</td>
    <td>{
        f'<span style="color: green;">{oil_json["oil_detail"]["92号汽油"]["change"]}</span>' 
        if str(oil_json["oil_detail"]["92号汽油"]["change"]).startswith("-") 
        else f'<span style="color: red;">{oil_json["oil_detail"]["92号汽油"]["change"]}</span>' 
        if str(oil_json["oil_detail"]["92号汽油"]["change"]).startswith("+") 
        else oil_json["oil_detail"]["92号汽油"]["change"]
    }</td>
    <td>{oil_json['oil_detail']['92号汽油']['change_percent']}</td>
  </tr>
  <tr>
    <td>95号汽油</td>
    <td>{oil_json['oil_detail']['95号汽油']['current_price']}</td>
    <td>{oil_json['oil_detail']['95号汽油']['last_price']}</td>
    <td>{
        f'<span style="color: green;">{oil_json["oil_detail"]["95号汽油"]["change"]}</span>' 
        if str(oil_json["oil_detail"]["95号汽油"]["change"]).startswith("-") 
        else f'<span style="color: red;">{oil_json["oil_detail"]["95号汽油"]["change"]}</span>' 
        if str(oil_json["oil_detail"]["95号汽油"]["change"]).startswith("+") 
        else oil_json["oil_detail"]["95号汽油"]["change"]
    }</td>
    <td>{oil_json['oil_detail']['95号汽油']['change_percent']}</td>
  </tr>
  <tr>
    <td>98号汽油</td>
    <td>{oil_json['oil_detail']['98号汽油']['current_price']}</td>
    <td>{oil_json['oil_detail']['98号汽油']['last_price']}</td>
    <td>{
        f'<span style="color: green;">{oil_json["oil_detail"]["98号汽油"]["change"]}</span>' 
        if str(oil_json["oil_detail"]["98号汽油"]["change"]).startswith("-") 
        else f'<span style="color: red;">{oil_json["oil_detail"]["98号汽油"]["change"]}</span>' 
        if str(oil_json["oil_detail"]["98号汽油"]["change"]).startswith("+") 
        else oil_json["oil_detail"]["98号汽油"]["change"]
    }</td>
    <td>{oil_json['oil_detail']['98号汽油']['change_percent']}</td>
  </tr>
</table>
<p style="margin-top: 10px; font-weight: bold;">下一次油价调整时间：{oil_json['next_change_date']}</p>
"""
        
        # 生成企业微信Markdown内容（对照API示例添加<font>颜色标签）
        def format_change_color(change_val):
            """统一处理涨跌金额的颜色格式化（企业微信Markdown）"""
            change_str = str(change_val)
            if change_str.startswith("-"):
                return f'<font color="green">{change_str}</font>'  # 下跌-绿色
            elif change_str.startswith("+"):
                return f'<font color="red">{change_str}</font>'    # 上涨-红色
            else:
                return change_str  # 无涨跌-默认颜色

        markdown_content = f"""
### 内蒙古油价更新信息
> 最近调整日期：{oil_json['last_change_date'] or '暂无数据'}

| 油价标号 | 当前油价（元/升） | 上次油价（元/升） | 涨跌（元/升） | 涨跌率 |
| ---- | ---- | ---- | ---- | ---- |
| 92号汽油 | {oil_json['oil_detail']['92号汽油']['current_price']} | {oil_json['oil_detail']['92号汽油']['last_price']} | {format_change_color(oil_json['oil_detail']['92号汽油']['change'])} | {oil_json['oil_detail']['92号汽油']['change_percent']} |
| 95号汽油 | {oil_json['oil_detail']['95号汽油']['current_price']} | {oil_json['oil_detail']['95号汽油']['last_price']} | {format_change_color(oil_json['oil_detail']['95号汽油']['change'])} | {oil_json['oil_detail']['95号汽油']['change_percent']} |
| 98号汽油 | {oil_json['oil_detail']['98号汽油']['current_price']} | {oil_json['oil_detail']['98号汽油']['last_price']} | {format_change_color(oil_json['oil_detail']['98号汽油']['change'])} | {oil_json['oil_detail']['98号汽油']['change_percent']} |

**下一次油价调整时间：{oil_json['next_change_date']}**
"""

        return oil_json, table_html, markdown_content, oil_json["last_change_date"], oil_json["next_change_date"], True

    except Exception as e:
        error_info = f"获取油价失败：{str(e)}"
        print(error_info)
        return {}, error_info, "", "", "", False

def push_to_wechat_via_pushplus(title, content):
    """PushPlus微信推送"""
    if not PUSHPLUS_TOKEN:
        print("【错误】PushPlus Token为空（必填项）")
        return False
    if not content:
        print("【错误】推送内容Content为空（必填项）")
        return False

    try:
        push_json_params = {
            "token": PUSHPLUS_TOKEN,
            "title": title,
            "content": content,
            "template": "html",
            "channel": "wechat",
            "topic": 1
        }

        print("【调试】PushPlus推送JSON参数：")
        print(json.dumps(push_json_params, ensure_ascii=False, indent=2))

        push_url = "http://www.pushplus.plus/send"
        response = requests.post(
            url=push_url,
            data=json.dumps(push_json_params, ensure_ascii=False),
            headers={"Content-Type": "application/json"},
            timeout=15,
            verify=False
        )

        response.raise_for_status()
        push_result = response.json()

        if push_result.get("code") == 200:
            print(f"【成功】PushPlus推送完成，返回：{json.dumps(push_result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"【失败】PushPlus推送失败，返回：{json.dumps(push_result, ensure_ascii=False, indent=2)}")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"【错误】HTTP异常：{e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print(f"【错误】推送异常：{str(e)}")
        return False

def push_to_qy_wechat(title, markdown_content):
    """企业微信机器人推送（仅当配置了Key时执行）"""
    if not QY_WECHAT_WEBHOOK_KEY:
        print("【提示】未配置企业微信Webhook Key，跳过企业微信推送")
        return True  # 返回True避免主函数判断为失败
    if not markdown_content:
        print("【错误】企业微信推送内容为空（必填项）")
        return False

    qy_wechat_webhook_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={QY_WECHAT_WEBHOOK_KEY}"
    
    push_data = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"{title}\n{markdown_content}"
        }
    }

    try:
        print("【调试】企业微信推送参数：")
        print(json.dumps(push_data, ensure_ascii=False, indent=2))

        response = requests.post(
            url=qy_wechat_webhook_url,
            data=json.dumps(push_data, ensure_ascii=False),
            headers={"Content-Type": "application/json"},
            timeout=15,
            verify=False
        )

        response.raise_for_status()
        push_result = response.json()

        if push_result.get("errcode") == 0:
            print(f"【成功】企业微信推送完成，返回：{json.dumps(push_result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"【失败】企业微信推送失败，返回：{json.dumps(push_result, ensure_ascii=False, indent=2)}")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"【错误】企业微信推送HTTP异常：{e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print(f"【错误】企业微信推送异常：{str(e)}")
        return False

def main():
    """主函数"""
    os.environ["TZ"] = "Asia/Shanghai"
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"【运行】当前日期（中国时区）：{current_date}")

    # 获取油价数据
    oil_json, oil_html, oil_markdown, last_change_date, next_change_date, is_success = get_neimenggu_oil_price()
    if not is_success:
        print(f"【终止】{oil_html}")
        return

    print("【调试】油价JSON数据：")
    print(json.dumps(oil_json, ensure_ascii=False, indent=2))

    # 测试用强制推送（注释后启用正式逻辑）
    print("【测试】强制推送（GitHub Actions测试）...")
    # push_success_pushplus = push_to_wechat_via_pushplus(f"【内蒙古油价测试】{current_date}", oil_html)
    push_success_qywechat = push_to_qy_wechat(f"【内蒙古油价测试】{current_date}", oil_markdown)
    
    # 正式逻辑：仅调整日推送
    if current_date != last_change_date:
        print(f"【结束】今日({current_date})非调整日（最近调整日：{last_change_date}），无需推送")
        return
    
    print("【推送】今日为调整日，执行推送...")
    push_title = f"【内蒙古油价调整通知】{current_date}"
    
    # PushPlus推送（必填）
    push_success_pushplus = push_to_wechat_via_pushplus(push_title, oil_html)
    
    # 企业微信推送（可选：仅配置Key时执行）
    push_success_qywechat = push_to_qy_wechat(push_title, oil_markdown)
    
    print(f"【完成】PushPlus推送{'成功' if push_success_pushplus else '失败'}，企业微信推送{'成功' if push_success_qywechat else '失败'}")

if __name__ == "__main__":
    main()
