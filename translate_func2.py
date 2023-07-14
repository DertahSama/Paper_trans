"""
翻译器在translators文件夹中，通过修改下面import哪个文件来决定用那个翻译库。
这些翻译库都需要自备api。
支持的服务商：
openai（chatGPT3.5），deepl，baidu，tencent
"""

translatorsdict={"1":"baidu","2":"tencent","3":"openai","4":"deepl"}
s=input("<< 选择翻译器"+str(translatorsdict)+"：")

# tt=__import__(translatorsdict[s]+"_translator")
exec("import translators."+translatorsdict[s]+"_translator as tt ") # 感觉不太优雅，但是就这样吧！
# from baidu_translator import * 

from time import sleep
import re,sys

def ProgressBar(now,alls):
    progress=int(now/alls*50)
    print("\r进度: %d/%d: "%(now,alls), "▋"*progress + "-"*(50-progress), end="")
    if now==alls:
        print("done！")   #100%了换个行
    sys.stdout.flush()
    sleep(0.01)

def translate_text(client,text):
    
    inline_eqn_results = re.findall(r'\$.*?\$',text) # 预处理行内公式
    
    for i in range(len(inline_eqn_results)):
        inline_eqn=inline_eqn_results[i]
        marker='XX'+'%03d'%i  # 把行内公式替换成标记，防止翻译时丢符号
        text = text.replace(inline_eqn,marker)
    
    text = re.sub(r'(Secs?\.|Eqn?s?\.|Refs?\.) (\(?\d+\)?)',r'\1\2',text)  # 把诸如「Sec. 3」变成「Sec.3」，防止这个点被认成句号导致错误断句。

    text_zh=tt.translator(client,text)
    sleep(0.2) # 每秒最多请求5次，可以删掉这行来搞快点

    for i in range(len(inline_eqn_results)):
        inline_eqn=inline_eqn_results[i]
        marker='XX'+'%03d'%i
        text_zh = text_zh.replace(marker,inline_eqn) # 替换回来

    return text_zh


def translate_abstract(tex_file):
    st = r'\begin{abstract}'
    st1 = r'\\title\{(.*?)\}'
    print('Translating abstract')

    client=tt.create_client()

    for line_idx, line in enumerate(tex_file):
        if re.search(st1,line):
            title_en=re.search(st1,line).group(1)
            title_zh=translate_text(client,title_en)
            tex_file[line_idx]=r'\title{'+title_zh+r'\\ \Large{'+title_en+'}}'
        if st in line:
            abstract_idx = line_idx+1
            abstract_en = tex_file[abstract_idx]
            abstract_ch = translate_text(client,abstract_en)+'\n'
            tex_file[abstract_idx] = r'\uline{'+abstract_en+r'}\\ \indent '+abstract_ch
            break
        
    

    return tex_file

def translate_body(tex_file):
    sub_environ=r'\\(begin|end)\{.*\}'
    sub_title=r'\\(chapter|section|subsection)\{(.*?)\}'

    st0 = r'\maketitle'
    # st1 = r'\section'
    st2 = r'{References}'
    # sx1 = r'{figure}'
    # sx2 = r'{equation}'
    # sx3 = r'{table}'
    
    print('Translating main body')

    client=tt.create_client()

    for line_idx, line in enumerate(tex_file):
        if st0 in line:
            start_idx = line_idx+1
        if st2 in line:
            end_idx = line_idx-1
            break
    
    flag = True
    L = end_idx-start_idx+1
    for line_idx in range(start_idx,end_idx):
        line = tex_file[line_idx]
        ProgressBar(line_idx-start_idx+1,L-1)
        # print(line_idx-start_idx+1,'/',L)

        # if sx1 in line or sx2 in line or sx3 in line:
        if re.findall(sub_environ,line):     # 寻找子环境
            flag = not flag
            continue

        if flag and len(line)>2: # 非子环境内
            searchobj=re.search(sub_title,line) # 搜寻章节标题
            if searchobj:
                name=searchobj.group(2)
                name_ch=translate_text(client, name)
                line_ch=line.replace(name,name_ch)
                tex_file[line_idx] = line_ch
            else:
                line_ch = translate_text(client, line)+'\n'
                tex_file[line_idx] = r"\begin{leftbar} \small "+line+r"\end{leftbar}"+line_ch # 翻译后，在前面放上原文

        if not flag: # 子环境内
            def doit(mo):
                text_en=mo.group(1)
                text_ch=translate_text(client,text_en)
                text_ch="\\caption{\\uline{"+text_en+ "}\\\\" + text_ch + "}"
                return text_ch
            tex_file[line_idx]=re.sub(r'\\caption{(.*)}',doit,line) # 翻译图注

    with open('suffix.txt','r') as f:
        tex_file[end_idx+1]=f.read()
    
    return tex_file

def translate_captions(tex_file):
    print('Translating captions')
    client=tt.create_client()
    def doit(mo):
        text_en=mo.group(1)
        text_ch=translate_text(client,text_en)
        text_ch="\\caption{"+text_en+ "\\\\" + text_ch + "}"
        return text_ch
    
    L=len(tex_file)
    for line_idx, line in enumerate(tex_file):
        ProgressBar(line_idx+1,L)
        tex_file[line_idx]=re.sub(r'\\caption{(.*)}',doit,line)

    return tex_file