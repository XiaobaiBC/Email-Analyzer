## Email Analyzer: 高效邮件分析助手

---

## **介绍**

Email Analyzer 是一款旨在帮助用户高效处理电子邮件的工具。通过整合 IMAP 邮件协议与大语言模型，该程序不仅能够自动化提取邮件的核心信息、评估其重要性、提供处理建议，还能对邮件内容进行多语言分析，特别支持巴西葡萄牙语。它特别适合那些每天需要处理大量邮件、难以快速判断优先级的用户，尤其在多语言邮件处理上表现出色。
![WeChat图片编辑_20250105203312](https://github.com/user-attachments/assets/6eeb4f77-bd11-46c1-800e-877ec60a3028)



---

## **程序背景**

在快节奏的工作环境中，电子邮件是主要的沟通工具，但大量的邮件常常让人不知从何开始。尤其是对于国际化团队，处理包含巴西葡萄牙语或其他语言的邮件更具挑战性。Email Analyzer 应运而生，旨在通过自动化技术和人工智能的结合，帮助用户轻松应对邮件处理挑战。特别地，我们的系统能够理解和处理巴西葡萄牙语邮件，提供高效的邮件分析与处理建议。

---

## **目标与目的**

Email Analyzer 的主要目标是：

1. **高效处理邮件**：自动从用户邮箱中提取邮件内容，按日期范围筛选（今天、本周、本月）。
2. **智能分析与多语言支持**：使用大语言模型分析邮件内容，确保巴西葡萄牙语邮件能够得到正确解析，并生成结构化的分析报告。
3. **提升工作效率**：减少用户手动阅读邮件的时间，快速掌握重要信息。
4. **提供结构化建议**：帮助用户从大量邮件中筛选出关键任务或重要事项，避免遗漏。

---

## **技术要求**

以下是运行 **Email Analyzer** 所需的技术条件：

### **运行环境**
- **操作系统**：Windows、macOS 或 Linux
- **Python 版本**：3.8 及以上

### **依赖库与安装**
- **IMAP 邮件库**：用于连接和获取邮件
  ```bash
  pip install imaplib
  ```
- **邮件解析与HTML处理**：`email`、`BeautifulSoup`、`html2text`
  ```bash
  pip install beautifulsoup4 html2text
  ```
- **正则表达式**：`re`（Python 内置库）
- **HTTP 请求**：用于调用大语言模型 API
  ```bash
  pip install requests
  ```
- **JSON 解析**：用于处理 API 返回的数据（Python 内置）

### **外部服务依赖**
- **IMAP 邮箱服务**：支持标准 IMAP 协议的邮箱（如：Gmail、Outlook、163 邮箱等）。
- **大语言模型 API 服务**：用于分析邮件内容，确保支持多语言处理，并正确理解巴西葡萄牙语内容，需配置 API 密钥。

---

## **功能描述**

### **1. 连接邮箱**
程序通过 IMAP 协议连接到指定邮箱，并支持筛选“今天”、“本周”或“本月”的邮件。用户可以指定日期范围，程序会从指定邮箱中自动提取符合日期范围的邮件，确保邮件能够实时获取并进行分析。

#### **连接代码**：
```python
# 使用SSL连接到IMAP服务器
mail = imaplib.IMAP4_SSL(imap_server, imap_port)
mail.login(email_address, email_password)  # 登录邮箱

# 选择收件箱
mail.select('INBOX')
```
上述代码通过IMAP协议连接到邮箱，登录并选择收件箱（INBOX）。

### **2. 提取邮件内容**
- 自动提取邮件的基本信息，如：主题、发件人、收件人、时间等。
- 支持 HTML 格式邮件的解析与转换，通过 `BeautifulSoup` 和 `html2text` 库提取清晰的文本内容。

#### **解析邮件内容代码**：
```python
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
```
这段代码遍历邮件的所有部分，如果邮件包含HTML内容，则提取并转换为纯文本。

### **3. 智能分析与多语言支持**
通过大语言模型，我们对邮件内容进行智能分析。特别注意，程序已适配巴西葡萄牙语，使得该语言的邮件内容能够被正确理解与分析。以下是处理邮件头部的代码示例：

#### **解码邮件头部**：
```python
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
```
`decode_str`函数用于解码邮件头部的编码字段（如发件人、主题等），确保巴西葡萄牙语邮件等非ASCII邮件能够被正确解析。

#### **使用大语言模型分析邮件**：
```python
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

```
该代码在收到邮件后，生成一个格式化的分析请求，确保巴西葡萄牙语等非中文内容被正确处理，并返回结构化报告。

### **4. 多轮交互**
支持逐封邮件分析，用户可以在分析一封邮件后选择是否继续处理下一封邮件。通过按回车键，用户可以轻松完成所有邮件的处理。

---

## **代码解析**

在此部分，我们将逐步解析程序中的核心函数，帮助用户理解代码实现。

### **`decode_str` 函数**
该函数用于解码邮件头部的字段，如发件人、主题等。解码后，能够处理包含非ASCII字符的邮件（如巴西葡萄牙语邮件），并确保其能够显示正确的文字。

#### **工作原理**：
- 使用 `decode_header` 解码邮件字段。
- 处理字节数据和字符集，确保正确解码。

### **`process_content` 函数**
该函数用于清理邮件正文内容，去除多余的空格和换行符，使邮件内容更加简洁和易于分析。

#### **工作原理**：
- 使用正则表达式清除多余的空白字符和换行符。

### **`analyze_email_with_llm` 函数**
该函数使用大语言模型分析邮件内容，并生成结构化的分析报告。它将邮件内容、发件人、主题等信息传递给模型，获取邮件的关键信息，并生成简明的报告。

#### **工作原理**：
- 通过 HTTP 请求与大语言模型 API 交互。
- 根据邮件内容生成分析报告，输出重要任务、截止日期等信息。

### **`get_emails` 函数**
该函数通过 IMAP 协议连接邮箱，获取并解析邮件内容。它支持按日期范围（如今天、本周、本月）筛选邮件，并提取邮件的文本内容。

#### **工作原理**：
- 使用 `imaplib` 连接到邮箱。
- 提取邮件的主题、发件人、收件人等信息，并解析邮件正文。

---

## 模型
模型使用自回归的Transformer架构，并结合了监督式微调（SFT）和强化学习（RLHF）。该模型特别设计用于多语言处理，在此处为针对葡萄牙语进行特调。
#### **训练数据与性能表现**
模型基于大规模的数据集进行训练，数据来源于多个公开的互联网资源。它在多个标准基准测试中表现出色，特别是在**MMLU（Massive Multitask Language Understanding）**、**推理能力**等任务上，展示了其强大的能力：
- **MMLU基准**：模型在MMLU基准上取得了83.6%的成绩，显著优于前代版本。
- **推理任务**：在“ARC-Challenge”等推理任务中，准确率为92.9%

## **结论**

**Email Analyzer** 是一个高效的邮件处理工具，适合需要快速处理大量邮件的用户，特别是在面对多语言邮件（如巴西葡萄牙语）时，能够提供额外的帮助。通过结合 IMAP 协议和大语言模型，该工具能够自动提取邮件中的关键信息、评估邮件的重要性，并给出处理建议，从而提高邮件处理效率。

1. **理解多语言邮件**：特别是巴西葡萄牙语，确保邮件内容得到正确处理。
2. **智能分析邮件**：根据邮件的内容和紧急性，自动评估优先级，并提供相应的处理建议。
3. **生成简明报告**：帮助用户快速掌握邮件的关键点，避免遗漏重要信息。

### **提升工作效率**

使用 **Email Analyzer**，用户能够节省大量的时间，快速识别出重要的邮件，避免浪费大量时间来理解各个邮件内容。未来，我们也会根据用户反馈，继续优化功能，增加更多实用的邮件处理工具。希望大家多多交流
