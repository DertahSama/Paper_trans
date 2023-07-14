import latex_func as lf
from tkinter import filedialog
import os

def TYPESET():
    
    # ========打开文件=========
    print("<< 请打开从Mathpix导出的tex文档...")
    f_path = filedialog.askopenfilename(initialdir='./',filetypes=(('tex files','*.tex'),))
    if not f_path:
        exit()
    (basedir,filename)=os.path.split(f_path)
    
    with open('filepath.txt', 'w') as f:
        f.write(basedir)

    input_file_path = f_path
    template_file_path = 'template.tex'
    typeset_file_path = basedir+'/1-TYPESETED.tex'

    # =======处理文件===========
    print(">> 开始排版预处理...")
    with open(input_file_path, 'r') as file_0:
        tex_0 = file_0.readlines()
    with open(template_file_path, 'r',encoding='utf-8') as file_1:
        tex_1 = file_1.readlines()

    format_figure = lf.get_format_figure(tex_1)
    format_equation = lf.get_format_equation(tex_1)
    format_table = lf.get_format_table(tex_1)

    tex_2 = lf.create_new_tex(tex_1)
    tex_2 = lf.modify_title(tex_0,tex_2)
    tex_2 = lf.modify_author(tex_0,tex_2)
    tex_2 = lf.modify_abstract(tex_0,tex_2)
    tex_2 = lf.modify_body(tex_0,tex_2)
    # tex_2 = lf.modify_references(tex_0,tex_2)

    tex_2 = lf.modify_equation(tex_2,format_equation)
    tex_2 = lf.modify_figure(tex_2,format_figure)
    tex_2 = lf.modify_table(tex_2,format_table)
    tex_2 = lf.modify_stitch(tex_2)

    with open(typeset_file_path, 'w',encoding='utf-8') as file_2:
        file_2.write(' '.join(tex_2))

    print('>> 已保存到：'+typeset_file_path)
    path1=typeset_file_path.replace('/','\\')
    os.system(f"C:\Windows\explorer.exe /select, {path1}")

if __name__=="__main__":
    TYPESET()
