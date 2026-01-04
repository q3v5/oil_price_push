# ⛽️ 内蒙古油价查询与推送工具

一个用于获取内蒙古最新油价信息，并通过PushPlus推送至微信的Python脚本，支持GitHub Actions自动运行，让你随时掌握油价动态！


## ✨ 功能说明

该工具主要实现以下功能：
- 📊 调用坦数数据API获取内蒙古地区92号、95号、98号汽油的最新价格
- 📈 解析油价数据，包括当前价格、上次价格、涨跌幅度及调整日期
- 📋 生成格式化的HTML表格展示油价信息，直观清晰
- 📱 通过PushPlus服务将油价信息推送至微信（支持调整日自动推送或测试强制推送）


## 🛠️ 依赖环境

- Python 3.6+
- 依赖库：`requests`（用于网络请求）


## 📦 安装步骤

1. 克隆或下载本项目代码到本地
2. 安装依赖库（一行命令搞定）：
```bash
pip install requests
```


## ⚙️ 环境变量配置

脚本需要以下环境变量支持，可通过系统环境变量设置或在GitHub Secrets中配置（用于GitHub Actions）：

| 环境变量名        | 说明                                  | 获取方式                                  |
|-------------------|---------------------------------------|-------------------------------------------|
| `PUSHPLUS_TOKEN`  | PushPlus推送服务的Token（必填）       | 注册并登录 [PushPlus官网](https://www.pushplus.plus/) 获取 |
| `TANSHU_API_KEY`  | 油价API的密钥（必填）             | 注册并登录 [API官网](https://www.tanshuapi.com/)，申请"油价查询"API获取 |


## 🚀 使用方法

### 💻 本地运行

1. 配置环境变量：
   ```bash
   # Linux/Mac
   export PUSHPLUS_TOKEN="你的PushPlus Token"
   export TANSHU_API_KEY="你的坦数API密钥"
   
   # Windows (PowerShell)
   $env:PUSHPLUS_TOKEN="你的PushPlus Token"
   $env:TANSHU_API_KEY="你的坦数API密钥"
   ```

2. 运行脚本（即刻获取油价）：
   ```bash
   python main.py
   ```


### 🔄 GitHub Actions 自动运行

1. Fork本项目到你的GitHub仓库
2. 在仓库设置中添加Secrets（就像藏起你的钥匙🔑）：
   - 进入仓库 → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`
   - 分别添加 `PUSHPLUS_TOKEN` 和 `TANSHU_API_KEY` 及其对应值

3. 创建工作流配置文件（如 `.github/workflows/oil-price.yml`）：
```yaml
name: 内蒙古油价推送

on:
  schedule:
    - cron: '0 8 * * *'  # 每天北京时间16:00运行（GitHub Actions默认UTC时区，需+8小时）
  workflow_dispatch:  # 支持手动触发（随时想查就查！）

jobs:
  send_oil_price:
    runs-on: ubuntu-latest
    steps:
      - name: 拉取代码
        uses: actions/checkout@v4
      
      - name: 设置Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: 安装依赖
        run: pip install requests
      
      - name: 运行脚本
        env:
          PUSHPLUS_TOKEN: ${{ secrets.PUSHPLUS_TOKEN }}
          TANSHU_API_KEY: ${{ secrets.TANSHU_API_KEY }}
        run: python main.py
```


## 🔍 脚本逻辑说明

1. **油价获取**：`get_neimenggu_oil_price()` 函数调用坦数数据API，解析返回的油价信息，生成结构化数据和美观的HTML表格。
2. **微信推送**：`push_to_wechat_via_pushplus()` 函数通过PushPlus API将HTML内容推送到你的微信，随时随地查看。
3. **主逻辑**：`main()` 函数处理时区设置（默认中国上海时区，避免时差问题），判断是否为油价调整日（正式环境），并智能执行推送操作。


## 🔄 模式切换

- **测试模式**（默认启用）：强制推送当前油价信息，方便调试：
  ```python
  print("【测试】强制推送（GitHub Actions测试）...")
  push_success = push_to_wechat_via_pushplus(f"【内蒙古油价测试】{current_date}", oil_html)
  ```

- **正式模式**：仅在油价调整日推送通知（更省推送次数），需注释测试代码并启用日期判断：
  ```python
  # 注释测试代码，启用以下逻辑
  if current_date != last_change_date:
      print(f"【结束】今日({current_date})非调整日（最近调整日：{last_change_date}），无需推送")
      return
  print("【推送】今日为调整日，执行推送...")
  push_title = f"【内蒙古油价调整通知】{current_date}"
  push_success = push_to_wechat_via_pushplus(push_title, oil_html)
  ```


## ⚠️ 注意事项

- 脚本中API请求默认关闭SSL验证（`verify=False`），如需启用，可移除该参数（需确保环境信任相关证书）。
- 坦数数据API可能有调用次数限制，具体请参考其平台说明（别太频繁哦~）。
- PushPlus免费版有推送频率限制，如需高频使用可考虑升级付费版。

---

💡 有了这个工具，再也不用担心错过油价调整啦！🚗💨
