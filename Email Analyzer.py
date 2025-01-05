import imaplib
import email
from email.header import decode_header
import datetime
from bs4 import BeautifulSoup
import html2text
import os
import re
import requests
import json

邮箱 =  
密码 =  
IMAP服务器地址 =  
IMAP服务器端口 =  
API_KEY= 

def decode_str(s):
    try:
        decoded_list = decode_header(s)
        result = ""
        for decoded_str, charset in decoded_list:
            if isinstance(decoded_str, bytes):
                if charset:
                    result += decoded_str.decode(charset)
                else:
                    result += decoded_str.decode('utf-8', errors='ignore')
            else:
                result += str(decoded_str)
        return result
    except Exception as e:
        return str(s)

def process_content(content):
    # 移除多余的空白字符和换行
    content = re.sub(r'\s+', ' ', content.strip())
    return content

def analyze_email_with_llm(email_data):
    """使用大模型分析邮件内容"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
    }

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

    json_data = {
        'model': 'meta-llama/Meta-Llama-3.1-70B-Instruct',
        'messages': [
            {
                'role': 'user',
                'content': prompt,
            },
        ],
    }

    try:
        response = requests.post(
            'https://api.deepinfra.com/v1/openai/chat/completions', 
            headers=headers, 
            json=json_data
        )
        response_json = response.json()
        
        # 打印分析结果
        print("\n📧 邮件分析报告")
        print("="*50)
        print(response_json['choices'][0]['message']['content'])
        print("="*50)
        
        # 打印使用统计
        usage = response_json['usage']
        cost_usd = usage['estimated_cost']
        print(f"\n📊 API使用情况")
        print(f"总Token数: {usage['total_tokens']} (输入: {usage['prompt_tokens']}, 输出: {usage['completion_tokens']})")
        print(f"成本: ${cost_usd:.6f} USD")
        
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")

def get_emails(date_range='today'):
    # 邮箱配置
    email_address = 邮箱
    email_password = 密码
    imap_server = IMAP服务器地址
    imap_port = IMAP服务器端口

    try:
        print("\n🔄 正在连接邮箱服务器...")
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_address, email_password)
        
        # 选择收件箱
        mail.select('INBOX')
        
        # 获取日期范围
        today = datetime.date.today()
        if date_range == 'today':
            search_criteria = f'(ON {today.strftime("%d-%b-%Y")})'
            range_desc = "今天"
        elif date_range == 'week':
            monday = today - datetime.timedelta(days=today.weekday())
            search_criteria = f'(SINCE {monday.strftime("%d-%b-%Y")})'
            range_desc = "本周"
        elif date_range == 'month':
            first_day = today.replace(day=1)
            search_criteria = f'(SINCE {first_day.strftime("%d-%b-%Y")})'
            range_desc = "本月"
        
        # 搜索邮件
        _, messages = mail.search(None, search_criteria)
        
        if not messages[0]:
            print(f"📭 {range_desc}没有邮件")
            return
        
        # 遍历所有邮件
        email_ids = messages[0].split()
        total_emails = len(email_ids)
        print(f"\n📬 {range_desc}共有 {total_emails} 封邮件")
        
        for index, num in enumerate(email_ids, 1):
            _, msg_data = mail.fetch(num, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # 获取基本信息
            email_data = {
                'subject': decode_str(email_message["subject"]),
                'from': decode_str(email_message["from"]),
                'to': decode_str(email_message["to"]),
                'date': decode_str(email_message["date"]),
                'content': ''
            }
            
            print(f"\n📨 正在处理第 {index}/{total_emails} 封邮件")
            print("="*50)
            print(f"📌 主题: {email_data['subject']}")
            print(f"👤 发件人: {email_data['from']}")
            print(f"📧 收件人: {email_data['to']}")
            print(f"🕒 日期: {email_data['date']}")
            
            # 获取邮件内容
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/html":
                        html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        h = html2text.HTML2Text()
                        h.ignore_links = True
                        h.ignore_images = True
                        h.body_width = 0
                        email_data['content'] = process_content(h.handle(str(soup)))
                        break
            else:
                content = email_message.get_payload(decode=True).decode(email_message.get_content_charset() or 'utf-8', errors='ignore')
                if email_message.get_content_type() == "text/html":
                    h = html2text.HTML2Text()
                    h.ignore_links = True
                    h.ignore_images = True
                    h.body_width = 0
                    email_data['content'] = process_content(h.handle(content))
                else:
                    email_data['content'] = process_content(content)
            
            print(f"\n📄 邮件原文:")
            print("-"*50)
            print(email_data['content'])
            print("-"*50)
            
            # 使用大模型分析邮件
            analyze_email_with_llm(email_data)
            
            # 如果还有下一封邮件，等待用户确认继续
            if index < total_emails:
                input("\n⏩ 按回车键继续分析下一封邮件...")
            
        mail.close()
        mail.logout()
        print("\n✅ 所有邮件处理完成！")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")

def main():
    print("📮 邮件分析助手")
    print("\n请选择要查看的邮件时间范围：")
    print("1. 📅 今天的邮件")
    print("2. 📅 本周的邮件")
    print("3. 📅 本月的邮件")
    
    while True:
        choice = input("\n请输入选项（1-3）: ")
        if choice == '1':
            get_emails('today')
            break
        elif choice == '2':
            get_emails('week')
            break
        elif choice == '3':
            get_emails('month')
            break
        else:
            print("❌ 无效的选项，请重新输入。")

if __name__ == "__main__":
    main() 
