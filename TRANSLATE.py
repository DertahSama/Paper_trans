import os

def TRANSLATE():
    # ========打开文件=======
    with open('filepath.txt','r') as f:
        basedir=f.read()

    input_file_path = basedir+'/1-TYPESETED.tex'
    output_file_path = basedir+'/2-TRANSLATED.tex'

    with open(input_file_path, 'r',encoding='utf-8') as file_2:
        tex_2 = file_2.readlines()

    # ======加载翻译器=====
    import translate_func2 as tf

    # ======进行翻译=======
    tex_3 = tex_2.copy()
    tex_3 = tf.translate_abstract(tex_3)
    tex_3 = tf.translate_body(tex_3)
    # tex_3 = tf.translate_captions(tex_3)

    # ======保存=========
    with open(output_file_path, 'w',encoding='utf-8') as file_3:
        file_3.write(' '.join(tex_3))

    print(">> 已保存到："+output_file_path)

    os.remove('filepath.txt')
    os.remove('suffix.txt')

if __name__=="__main__":
    TRANSLATE()
