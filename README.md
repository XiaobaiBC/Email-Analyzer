# Email Analyzer - README

## **主题**

Email Analyzer: 高效邮件分析助手

---

## **介绍**

Email Analyzer 是一款旨在帮助用户高效处理电子邮件的工具。通过整合 IMAP 邮件协议与大语言模型，该程序不仅能够自动化提取邮件的核心信息、评估其重要性、提供处理建议，还能对邮件内容进行多语言分析，特别支持巴西葡萄牙语。它特别适合那些每天需要处理大量邮件、难以快速判断优先级的用户，尤其在多语言邮件处理上表现出色。

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
通过 IMAP 协议连接到邮箱，并支持筛选“今天”、“本周”或“本月”的邮件。程序会从指定邮箱中自动提取符合日期范围的邮件，确保邮件能够实时获取并进行分析。

### **2. 提取邮件内容**
- 自动提取邮件的基本信息，如：主题、发件人、收件人、时间等。
- 支持 HTML 格式邮件的解析与转换，通过 `BeautifulSoup` 和 `html2text` 库提取清晰的文本内容。

### **3. 智能分析与多语言支持**
通过大语言模型，我们对邮件内容进行智能分析。特别注意，程序已适配巴西葡萄牙语，使得该语言的邮件内容能够被正确理解与分析。

#### **示例代码**：
```python
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
```
该代码块用于解码邮件的主题、发件人等字段，确保即使是巴西葡萄牙语邮件也能够被正确解析。

#### **巴西葡萄牙语邮件的特别支持**：
在分析邮件时，我们会将非中文邮件（如巴西葡萄牙语邮件）翻译为中文，并按照需求生成结构化的分析报告。以下是分析请求的代码示例：

```python
def analyze_email_with_llm(email_data):
    """使用大模型分析邮件内容"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY',
    }

    prompt = f"""
    你是一位专业的“邮件分析助手”，擅长提取邮件中的关键信息并生成高效、简明的分析报告。请根据以下要求分析邮件内容并提供结构化输出：

    ---

    ### **分析报告格式**
    1. **邮件概要**
       - 主要内容：[总结邮件的核心内容，非中文内容需翻译]
       - 重要细节：[标注金额、截止日期、会议时间等关键信息]
    ...
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
        print(response_json['choices'][0]['message']['content'])
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")
```
该代码在收到邮件后，生成一个格式化的分析请求，确保巴西葡萄牙语等非中文内容被正确处理，并返回结构化报告。

### **4. 多轮交互**
支持逐封邮件分析，用户可以在分析一封邮件后选择是否继续处理下一封邮件。通过按回车键，用户可以轻松完成所有邮件的处理。

---

## **结论**

Email Analyzer 是一款高效的邮件处理工具，特别适合那些需要处理大量邮件并且面临多语言邮件（如巴西葡萄牙语）挑战的用户。通过结合 IMAP 协议、自然语言处理和大语言模型，Email Analyzer 不仅大大提高了邮件处理效率，还通过智能分析帮助用户快速识别邮件中的关键信息。未来，随着技术不断进步，我们还将继续拓展更多的功能，如情感分析、自动回复模板等，进一步提升用户体验。

通过运行 **Email Analyzer**，用户能够高效地处理邮件，避免遗漏重要信息，从而提升工作效率。
