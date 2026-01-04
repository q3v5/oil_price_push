import requests
import json
import os
from datetime import datetime

# -------------------------- 从环境变量读取配置（关键适配GitHub Actions） --------------------------
PUSHPLUS_TOKEN = os.getenv("PUSHPLUS_TOKEN")  # 从GitHub Secrets读取
TANSHU_API_KEY = os.getenv("TANSHU_API_KEY")  # 从GitHub Secrets读取
# ------------------------------------------------------------------------------

def get_neimenggu_oil_price():
    """获取油价数据（逻辑不变，仅配置项来源修改）"""
    try:
        api_url = "https://api.tanshuapi.com/api/youjia/v1/trend"
        request_params = {
            "key": TANSHU_API_KEY,
            "province": "内蒙古"
        }
        response = requests.get(
            url=api_url,
            params=request_params,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        api_result = response.json()

        if not isinstance(api_result, dict) or api_result.get("code") != 1:
            error_msg = f"油价接口返回失败：{api_result.get('msg', '未知错误')}" if api_result else "油价接口返回空"
            return {}, error_msg, "", "", False

        oil_raw_data = api_result.get("data", {})
        oil_json = {
            "province": oil_raw_data.get("province", "内蒙古"),
            "last_change_date": "",
            "next_change_date": "暂无数据",
            "oil_detail": {
                "92号汽油": {
                    "current_price": oil_raw_data.get("92h", {}).get("price", "暂无数据"),
                    "last_price": oil_raw_data.get("92h", {}).get("change_before_price", "暂无数据"),
                    "change": oil_raw_data.get("92h", {}).get("change", "暂无数据"),
                    "change_percent": oil_raw_data.get("92h", {}).get("change_percent", "暂无数据")
                },
                "95号汽油": {
                    "current_price": oil_raw_data.get("95h", {}).get("price", "暂无数据"),
                    "last_price": oil_raw_data.get("95h", {}).get("change_before_price", "暂无数据"),
                    "change": oil_raw_data.get("95h", {}).get("change", "暂无数据"),
                    "change_percent": oil_raw_data.get("95h", {}).get("change_percent", "暂无数据")
                },
                "98号汽油": {
                    "current_price": oil_raw_data.get("98h", {}).get("price", "暂无数据"),
                    "last_price": oil_raw_data.get("98h", {}).get("change_before_price", "暂无数据"),
                    "change": oil_raw_data.get("98h", {}).get("change", "暂无数据"),
                    "change_percent": oil_raw_data.get("98h", {}).get("change_percent", "暂无数据")
                }
            }
        }

        # 日期格式化
        raw_last_date = oil_raw_data.get("before_change_time", "")
        if raw_last_date and len(raw_last_date) == 8 and raw_last_date.isdigit():
            oil_json["last_change_date"] = f"{raw_last_date[:4]}-{raw_last_date[4:6]}-{raw_last_date[6:8]}"
        raw_next_date = oil_raw_data.get("next_change_time", "")
        if raw_next_date and len(raw_next_date) == 8 and raw_next_date.isdigit():
            oil_json["next_change_date"] = f"{raw_next_date[:4]}-{raw_next_date[4:6]}-{raw_next_date[6:8]}"

        # 生成HTML表格
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
        if oil_json["oil_detail"]["92号汽油"]["change"].startswith("-") 
        else f'<span style="color: red;">{oil_json["oil_detail"]["92号汽油"]["change"]}</span>' 
        if oil_json["oil_detail"]["92号汽油"]["change"].startswith("+") 
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
        if oil_json["oil_detail"]["95号汽油"]["change"].startswith("-") 
        else f'<span style="color: red;">{oil_json["oil_detail"]["95号汽油"]["change"]}</span>' 
        if oil_json["oil_detail"]["95号汽油"]["change"].startswith("+") 
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
        if oil_json["oil_detail"]["98号汽油"]["change"].startswith("-") 
        else f'<span style="color: red;">{oil_json["oil_detail"]["98号汽油"]["change"]}</span>' 
        if oil_json["oil_detail"]["98号汽油"]["change"].startswith("+") 
        else oil_json["oil_detail"]["98号汽油"]["change"]
    }</td>
    <td>{oil_json['oil_detail']['98号汽油']['change_percent']}</td>
  </tr>
</table>
<p style="margin-top: 10px; font-weight: bold;">下一次油价调整时间：{oil_json['next_change_date']}</p>
"""
        return oil_json, table_html, oil_json["last_change_date"], oil_json["next_change_date"], True

    except Exception as e:
        error_info = f"获取油价失败：{str(e)}"
        print(error_info)
        return {}, error_info, "", "", False

def push_to_wechat_via_pushplus(title, content):
    """推送函数（逻辑不变，配置项从环境变量读取）"""
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
            "channel": "wechat"
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
            print(f"【成功】推送完成，返回：{json.dumps(push_result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"【失败】推送失败，返回：{json.dumps(push_result, ensure_ascii=False, indent=2)}")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"【错误】HTTP异常：{e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print(f"【错误】推送异常：{str(e)}")
        return False

def main():
    """主逻辑（适配GitHub Actions时区）"""
    # 设置时区为中国上海（解决GitHub Actions默认UTC时区导致的日期错误）
    os.environ["TZ"] = "Asia/Shanghai"
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"【运行】当前日期（中国时区）：{current_date}")

    # 获取油价数据
    oil_json, oil_html, last_change_date, next_change_date, is_success = get_neimenggu_oil_price()
    if not is_success:
        print(f"【终止】{oil_html}")
        return

    print("【调试】油价JSON数据：")
    print(json.dumps(oil_json, ensure_ascii=False, indent=2))

    # 强制推送（测试用）| 正式环境注释以下2行，启用日期判断
    #print("【测试】强制推送（GitHub Actions测试）...")
    #push_success = push_to_wechat_via_pushplus(f"【内蒙古油价测试】{current_date}", oil_html)
    
    # 正式环境：按日期判断推送（注释测试代码后启用）
     if current_date != last_change_date:
         print(f"【结束】今日({current_date})非调整日（最近调整日：{last_change_date}），无需推送")
         return
     print("【推送】今日为调整日，执行推送...")
     push_title = f"【内蒙古油价调整通知】{current_date}"
     push_success = push_to_wechat_via_pushplus(push_title, oil_html)
    
    print(f"【完成】推送{'成功' if push_success else '失败'}")

if __name__ == "__main__":
    main()
