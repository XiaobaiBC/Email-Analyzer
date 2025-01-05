# 导入必要的库
import imaplib  # 用于连接IMAP邮件服务器并进行操作
import email  # 处理邮件内容的模块
from email.header import decode_header  # 解码邮件头
import datetime  # 处理日期和时间
from bs4 import BeautifulSoup  # 用于解析HTML内容
import html2text  # 将HTML内容转换为纯文本
import os  # 处理操作系统相关功能
import re  # 正则表达式，用于处理和清理文本
import requests  # 发送HTTP请求，调用API
import json  # 处理JSON数据

# 配置邮箱相关信息
邮箱 =   # 邮箱地址
密码 =   # 邮箱密码
IMAP服务器地址 =    # IMAP服务器地址
IMAP服务器端口 =    # IMAP服务器端口（SSL加密）
API_KEY =   # 用于调用分析API的API密钥

# 解码邮件头信息（如发件人、主题等）
def decode_str(s):
    try:
        # decode_header解析邮件头
        decoded_list = decode_header(s)
        result = ""
        # 遍历解码结果
        for decoded_str, charset in decoded_list:
            if isinstance(decoded_str, bytes):
                # 如果是字节类型，使用指定的字符集解码
                if charset:
                    result += decoded_str.decode(charset)
                else:
                    # 如果没有指定字符集，使用utf-8解码并忽略错误
                    result += decoded_str.decode('utf-8', errors='ignore')
            else:
                result += str(decoded_str)  # 如果是字符串类型，直接加到结果中
        return result
    except Exception as e:
        # 捕获异常并返回原始字符串
        return str(s)

# 处理邮件内容，移除多余的空白字符和换行
def process_content(content):
    # 使用正则表达式将多余的空白字符和换行替换为一个空格
    content = re.sub(r'\s+', ' ', content.strip())
    return content

# 使用大模型分析邮件内容
def analyze_email_with_llm(email_data):
    """使用大模型分析邮件内容"""
    headers = {
        'Content-Type': 'application/json',  # 设置内容类型为JSON
        'Authorization': f'Bearer {API_KEY}',  # 设置授权信息，使用Bearer Token
    }

    # 构建提示语，要求模型分析邮件内容
    prompt = f"""
    你是一位巴西专业的“邮件分析助手”，擅长提取邮件中的关键信息并生成高效、简明的分析报告,来帮助用户进行快速掌握每个邮件。请根据以下要求分析邮件内容并提供结构化输出：

    ---

    ### 分析目标
    1. 提取邮件的核心内容和重要信息。
    2. 评估邮件的重要性，并根据内容提供处理建议。
    3. 如果邮件包含非中文内容，请翻译核心信息为中文。

    ---

    ### 分析报告格式
    1. **邮件概要**
       - 主要内容：[总结邮件的核心内容，非中文内容需翻译]
       - 重要细节：[标注金额、截止日期、会议时间等关键信息]

    2. **重要程度**
       - 优先级：[高/中/低]
       - 理由：[简述优先级的原因，例如任务紧急性或关键性]

    3. 处理建议
       - 是否需要立即处理：[是/否]
       - 建议完成时间：[具体建议时间]
       - 建议步骤：[清晰列出处理的具体步骤]

    4. 注意事项
       - [列出需要特别注意的地方，如截止日期、金额、参与人员等]

    ---

    邮件详情
    - 发件人: {email_data['from']}
    - 收件人: {email_data['to']}
    - 主题: {email_data['subject']}
    - 时间: {email_data['date']}

    邮件正文:
    {email_data['content']}
    """

    # 将构造的JSON数据发送给API
    json_data = {
        'model': 'meta-llama/Meta-Llama-3.1-70B-Instruct',  # 使用的模型
        'messages': [
            {
                'role': 'user',  # 设置请求角色为用户
                'content': prompt,  # 请求内容为上面构造的提示语
            },
        ],
    }

    try:
        # 向API发送POST请求
        response = requests.post(
            'https://api.deepinfra.com/v1/openai/chat/completions',  # API的URL
            headers=headers,  # 请求头
            json=json_data  # 请求数据
        )
        response_json = response.json()  # 解析JSON响应

        # 打印分析结果
        print("\n📧 邮件分析报告")
        print("="*50)
        print(response_json['choices'][0]['message']['content'])  # 显示邮件分析内容
        print("="*50)

        # 打印API使用统计
        usage = response_json['usage']
        cost_usd = usage['estimated_cost']
        print(f"\n📊 API使用情况")
        print(f"总Token数: {usage['total_tokens']} (输入: {usage['prompt_tokens']}, 输出: {usage['completion_tokens']})")
        print(f"成本: ${cost_usd:.6f} USD")

    except Exception as e:
        # 如果API请求发生异常，打印错误信息
        print(f"分析过程中发生错误: {str(e)}")

# 获取指定日期范围内的邮件
def get_emails(date_range='today'):
    # 邮箱配置
    email_address = 邮箱
    email_password = 密码
    imap_server = IMAP服务器地址
    imap_port = IMAP服务器端口

    try:
        print("\n🔄 正在连接邮箱服务器...")
        # 使用SSL连接到IMAP服务器
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, email_password)  # 登录邮箱

        # 选择收件箱
        mail.select('INBOX')

        # 获取日期范围
        today = datetime.date.today()  # 获取今天的日期
        if date_range == 'today':
            # 获取今天的邮件
            search_criteria = f'(ON {today.strftime("%d-%b-%Y")})'
            range_desc = "今天"
        elif date_range == 'week':
            # 获取本周的邮件
            monday = today - datetime.timedelta(days=today.weekday())  # 本周一的日期
            search_criteria = f'(SINCE {monday.strftime("%d-%b-%Y")})'
            range_desc = "本周"
        elif date_range == 'month':
            # 获取本月的邮件
            first_day = today.replace(day=1)  # 本月的第一天
            search_criteria = f'(SINCE {first_day.strftime("%d-%b-%Y")})'
            range_desc = "本月"

        # 搜索符合条件的邮件
        _, messages = mail.search(None, search_criteria)

        if not messages[0]:
            print(f"📭 {range_desc}没有邮件")
            return

        # 获取所有邮件ID
        email_ids = messages[0].split()
        total_emails = len(email_ids)
        print(f"\n📬 {range_desc}共有 {total_emails} 封邮件")

        # 遍历所有邮件
        for index, num in enumerate(email_ids, 1):
            _, msg_data = mail.fetch(num, '(RFC822)')  # 获取邮件数据
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)  # 将邮件内容解析为邮件对象

            # 获取邮件的基本信息
            email_data = {
                'subject': decode_str(email_message["subject"]),  # 解码邮件主题
                'from': decode_str(email_message["from"]),  # 解码发件人
                'to': decode_str(email_message["to"]),  # 解码收件人
                'date': decode_str(email_message["date"]),  # 解码邮件日期
                'content': ''  # 初始化邮件内容为空
            }

            print(f"\n📨 正在处理第 {index}/{total_emails} 封邮件")
            print("="*50)
            print(f"📌 主题: {email_data['subject']}")
            print(f"👤 发件人: {email_data['from']}")
            print(f"📧 收件人: {email_data['to']}")
            print(f"🕒 日期: {email_data['date']}")

            # 获取邮件内容
            if email_message.is_multipart():
                # 如果邮件是多部分的，遍历每个部分
                for part in email_message.walk():
                    if part.get_content_type() == "text/html":  # 只处理HTML类型的部分
                        # 解码HTML内容
                        html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                        # 使用BeautifulSoup解析HTML
                        soup = BeautifulSoup(html_content, 'html.parser')
                        h = html2text.HTML2Text()
                        h.ignore_links = True  # 忽略链接
                        h.ignore_images = True  # 忽略图片
                        h.body_width = 0  # 不进行换行
                        email_data['content'] = process_content(h.handle(str(soup)))  # 转换并清理HTML内容
                        break
            else:
                # 如果邮件是纯文本的，直接处理
                content = email_message.get_payload(decode=True).decode(email_message.get_content_charset() or 'utf-8', errors='ignore')
                if email_message.get_content_type() == "text/html":
                    h = html2text.HTML2Text()
                    h.ignore_links = True
                    h.ignore_images = True
                    h.body_width = 0
                    email_data['content'] = process_content(h.handle(content))  # 转换并清理HTML内容
                else:
                    email_data['content'] = process_content(content)  # 处理纯文本邮件内容

            print(f"\n📄 邮件原文:")
            print("-"*50)
            print(email_data['content'])
            print("-"*50)

            # 使用大模型分析邮件内容
            analyze_email_with_llm(email_data)

            # 如果还有下一封邮件，等待用户确认继续
            if index < total_emails:
                input("\n⏩ 按回车键继续分析下一封邮件...")

        mail.close()  # 关闭连接
        mail.logout()  # 登出邮箱
        print("\n✅ 所有邮件处理完成！")

    except Exception as e:
        # 如果发生错误，打印错误信息
        print(f"\n❌ 发生错误: {str(e)}")

# 主函数，提供用户交互界面选择日期范围
def main():
    print("📮 邮件分析助手")
    print("\n请选择要查看的邮件时间范围：")
    print("1. 📅 今天的邮件")
    print("2. 📅 本周的邮件")
    print("3. 📅 本月的邮件")

    while True:
        # 提示用户选择操作
        choice = input("\n请输入选项（1-3）: ")
        if choice == '1':
            # 获取今天的邮件
            get_emails('today')
            break
        elif choice == '2':
            # 获取本周的邮件
            get_emails('week')
            break
        elif choice == '3':
            # 获取本月的邮件
            get_emails('month')
            break
        else:
            # 如果用户输入无效选项，提示重新输入
            print("❌ 无效的选项，请重新输入。")

# 程序入口
if __name__ == "__main__":
    main()
