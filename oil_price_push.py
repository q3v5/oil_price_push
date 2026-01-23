import requests
import json
import os
from datetime import datetime

# -------------------------- 从环境变量读取配置（关键适配GitHub Actions） --------------------------
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")  # 从GitHub Secrets读取
TANSHU_API_KEY = os.getenv("TANSHU_API_KEY")  # 保留原变量名，实际配置天极API秘钥
# 企业微信webhook地址
QY_WECHAT_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=750d5858-0553-4ac5-8a4c-522103205c0b"
# ------------------------------------------------------------------------------

def calculate_change_percent(change, previous_price):
    """
    计算油价涨跌率（新API无该字段，需自行计算）
    :param change: 涨跌金额（字符串/数字）
    :param previous_price: 上次油价（字符串/数字）
    :return: 涨跌率（保留两位小数）或"暂无数据"
    """
    try:
        # 空值/非数字/0值处理
        if not change or change.strip() == "" or change == "0.00":
            return "暂无数据"
        if not previous_price or previous_price.strip() == "" or previous_price == "0.00":
            return "暂无数据"
        
        # 类型转换
        change_float = float(change)
        previous_float = float(previous_price)
        
        # 避免除零错误
        if previous_float == 0:
            return "暂无数据"
        
        # 计算涨跌率（保留两位小数，带百分号）
        percent = (change_float / previous_float) * 100
        return f"{percent:.2f}%"
    except (ValueError, TypeError):
        return "暂无数据"

def get_neimenggu_oil_price():
    """获取油价数据（适配新的天极API，保留原变量名）"""
    try:
        # 新API地址和参数（保留原TANSHU_API_KEY变量名）
        api_url = "https://apis.tianapi.com/oilprice/market"
        request_params = {
            "key": TANSHU_API_KEY,  # 仍用原变量名，配置新秘钥
            "prov": "内蒙古"        # 新API参数名改为prov
        }
        
        response = requests.get(
            url=api_url,
            params=request_params,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        api_result = response.json()

        # 新API返回码判断（200为成功，替换原code=1）
        if not isinstance(api_result, dict) or api_result.get("code") != 200:
            error_msg = f"油价接口返回失败：{api_result.get('msg', '未知错误')}" if api_result else "油价接口返回空"
            return {}, error_msg, "", "", False

        # 新API数据主体从result获取（替换原data）
        oil_raw_data = api_result.get("result", {})
        oil_json = {
            "province": oil_raw_data.get("prov", "内蒙古"),
            "last_change_date": "",
            "next_change_date": "暂无数据",
            "oil_detail": {
                "92号汽油": {
                    "current_price": oil_raw_data.get("p92", {}).get("price", "暂无数据"),  # 新字段p92
                    "last_price": oil_raw_data.get("p92", {}).get("previous_price", "暂无数据"),  # 新字段previous_price
                    "change": oil_raw_data.get("p92", {}).get("price_change", "暂无数据"),  # 新字段price_change
                    "change_percent": ""  # 新API无该字段，后续计算
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

        # 计算各标号油价涨跌率
        for oil_type in ["92号汽油", "95号汽油", "98号汽油"]:
            change = oil_json["oil_detail"][oil_type]["change"]
            last_price = oil_json["oil_detail"][oil_type]["last_price"]
            oil_json["oil_detail"][oil_type]["change_percent"] = calculate_change_percent(change, last_price)
            
            # 为涨跌金额补充符号（正数加+，负数保留-，空值不变）
            if change != "暂无数据" and change.strip() != "":
                try:
                    change_float = float(change)
                    if change_float > 0:
                        oil_json["oil_detail"][oil_type]["change"] = f"+{change}"
                except ValueError:
                    pass  # 非数字则保持原样

        # 日期格式化（新字段last_adjusted/next_adjustment替换原字段）
        raw_last_date = oil_raw_data.get("last_adjusted", "")
        if raw_last_date and len(raw_last_date) == 8 and raw_last_date.isdigit():
            oil_json["last_change_date"] = f"{raw_last_date[:4]}-{raw_last_date[4:6]}-{raw_last_date[6:8]}"
        raw_next_date = oil_raw_data.get("next_adjustment", "")
        if raw_next_date and len(raw_next_date) == 8 and raw_next_date.isdigit():
            oil_json["next_change_date"] = f"{raw_next_date[:4]}-{raw_next_date[4:6]}-{raw_next_date[6:8]}"

        # 生成HTML表格（格式不变，仅适配新数据）
        table_html = f"""
<h3>内蒙古油价更新信息</h3>
<p>最近调整日期：{oil_json['last_change_date'] or '暂无数据'}</p>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; text-align: center;">
  <tr style="background-color: #f0f0f0; font-weight: bold;">
    <th>油价标号</th>
    <th>当前油价（元/升）</th>
    <th>上次油价（元/升）</th>
    <th>涨跌（元/升）</th>
    <th>涨跌率</th>
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
        # 生成企业微信markdown_v2格式内容
        markdown_content = f"""# 内蒙古油价更新信息
## 最近调整日期：{oil_json['last_change_date'] or '暂无数据'}

| 油价标号 | 当前油价（元/升） | 上次油价（元/升） | 涨跌（元/升） | 涨跌率 |
| :------- | :--------------: | :--------------: | :-----------: | :----: |
| 92号汽油 | {oil_json['oil_detail']['92号汽油']['current_price']} | {oil_json['oil_detail']['92号汽油']['last_price']} | {oil_json['oil_detail']['92号汽油']['change']} | {oil_json['oil_detail']['92号汽油']['change_percent']} |
| 95号汽油 | {oil_json['oil_detail']['95号汽油']['current_price']} | {oil_json['oil_detail']['95号汽油']['last_price']} | {oil_json['oil_detail']['95号汽油']['change']} | {oil_json['oil_detail']['95号汽油']['change_percent']} |
| 98号汽油 | {oil_json['oil_detail']['98号汽油']['current_price']} | {oil_json['oil_detail']['98号汽油']['last_price']} | {oil_json['oil_detail']['98号汽油']['change']} | {oil_json['oil_detail']['98号汽油']['change_percent']} |

**下一次油价调整时间：{oil_json['next_change_date']}**
"""
        return oil_json, table_html, oil_json["last_change_date"], oil_json["next_change_date"], True, markdown_content

    except Exception as e:
        error_info = f"获取油价失败：{str(e)}"
        print(error_info)
        return {}, error_info, "", "", False, ""

def push_to_wechat_via_pushplus(title, content):
    """推送函数（逻辑完全不变）"""
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
        print(f"【错误】PushPlus HTTP异常：{e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print(f"【错误】PushPlus推送异常：{str(e)}")
        return False

def push_to_qy_wechat(title, markdown_content):
    """企业微信推送函数（markdown_v2格式）"""
    if not QY_WECHAT_WEBHOOK:
        print("【错误】企业微信Webhook地址为空")
        return False
    if not markdown_content:
        print("【错误】企业微信推送内容为空")
        return False

    try:
        # 企业微信markdown_v2消息体
        push_data = {
            "msgtype": "markdown_v2",
            "markdown_v2": {
                "content": markdown_content
            }
        }

        print("【调试】企业微信推送参数：")
        print(json.dumps(push_data, ensure_ascii=False, indent=2))

        response = requests.post(
            url=QY_WECHAT_WEBHOOK,
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
        print(f"【错误】企业微信HTTP异常：{e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print(f"【错误】企业微信推送异常：{str(e)}")
        return False

def main():
    """主逻辑（新增企业微信推送）"""
    # 设置时区为中国上海（解决GitHub Actions默认UTC时区导致的日期错误）
    os.environ["TZ"] = "Asia/Shanghai"
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"【运行】当前日期（中国时区）：{current_date}")

    # 获取油价数据（新增markdown_content返回值）
    oil_json, oil_html, last_change_date, next_change_date, is_success, markdown_content = get_neimenggu_oil_price()
    if not is_success:
        print(f"【终止】{oil_html}")
        return

    print("【调试】油价JSON数据：")
    print(json.dumps(oil_json, ensure_ascii=False, indent=2))

    # 强制推送（测试用）| 正式环境注释以下行，启用日期判断
    print("【测试】强制推送（GitHub Actions测试）...")
    #push_plus_success = push_to_wechat_via_pushplus(f"【内蒙古油价测试】{current_date}", oil_html)
    qy_wechat_success = push_to_qy_wechat(f"【内蒙古油价测试】{current_date}", markdown_content)
    
    # 正式环境：按日期判断推送（注释测试代码后启用）
    if current_date != last_change_date:
        print(f"【结束】今日({current_date})非调整日（最近调整日：{last_change_date}），无需推送")
        return
    
    print("【推送】今日为调整日，执行推送...")
    # PushPlus推送
    push_plus_title = f"【内蒙古油价调整通知】{current_date}"
    push_plus_success = push_to_wechat_via_pushplus(push_plus_title, oil_html)
    
    # 企业微信推送
    qy_wechat_title = f"【内蒙古油价调整通知】{current_date}"
    qy_wechat_success = push_to_qy_wechat(qy_wechat_title, markdown_content)
    
    print(f"【完成】PushPlus推送{'成功' if push_plus_success else '失败'}，企业微信推送{'成功' if qy_wechat_success else '失败'}")

if __name__ == "__main__":
    main()
