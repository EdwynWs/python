from flask import Flask, request, jsonify, render_template
import win32com.client
import pythoncom
import os
from pathlib import Path

app = Flask(__name__)

CATEGORIAS = {
    "Coletor de Esterco": Path(r"\\SERVIDOR\Projetos Oficial\Projetos - J. Cortiça\10 - Edwyn\Coletor de Esterco"),
    "Coletor de Ovos": Path(r"\\SERVIDOR\Projetos Oficial\Projetos - J. Cortiça\10 - Edwyn\Coletor de Ovo"),
    "Controle de Abastecimento": Path(r"\\SERVIDOR\Projetos Oficial\Projetos - J. Cortiça\10 - Edwyn\Controle e Abastecimento"),
    "Painel de Chave Geral": Path(r"\\SERVIDOR\Projetos Oficial\Projetos - J. Cortiça\10 - Edwyn\Painel de Chave Geral"),
    "Retenção (Egg Saver)": Path(r"\\SERVIDOR\Projetos Oficial\Projetos - J. Cortiça\10 - Edwyn\Retenção (Egg Saver)"),
    "Roscas Transportadoras": Path(r"\\SERVIDOR\Projetos Oficial\Projetos - J. Cortiça\10 - Edwyn\Roscas Transportadoras"),
    "Transpoprtadora Ovos": Path(r"\\SERVIDOR\Projetos Oficial\Projetos - J. Cortiça\10 - Edwyn\Transportadora de Ovos"),
    "Transportadora de Esterco": Path(r"\\SERVIDOR\Projetos Oficial\Projetos - J. Cortiça\10 - Edwyn\Transpoprtadora de Esterco"),
    "Especial": Path(r"\\SERVIDOR\Projetos Oficial\Projetos - J. Cortiça\10 - Edwyn\Especial"),
}

etiquetas = {}


def carregar_arquivos():
    global etiquetas
    etiquetas = {}

 
    for categoria, pasta in CATEGORIAS.items():
        arquivos_categoria = {}
        
        for arquivo in pasta.glob("*.cdr"):  
            nome_base = arquivo.stem.lower()  
            arquivos_categoria[nome_base] = str(arquivo)  
        for arquivo in pasta.glob("*.pdf"):
            nome_base = arquivo.stem.lower()
            arquivos_categoria[nome_base] = str(arquivo)
        
        if arquivos_categoria:
            etiquetas[categoria] = arquivos_categoria

    print("Arquivos carregados por categoria:")
    for categoria, arquivos in etiquetas.items():
        print(f"{categoria}: {list(arquivos.keys())}")


carregar_arquivos()

def open_coreldraw_file(file_path):
    pythoncom.CoInitialize()
    corel = win32com.client.Dispatch("CorelDRAW.Application")
    corel.Visible = True  

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.cdr' or file_extension == '.pdf':
        doc = corel.OpenDocument(file_path)
    else:
        raise ValueError(f"Formato de arquivo não suportado: {file_extension}")

    return corel, doc

def search_and_customize_label(doc, search_term):
    if hasattr(doc, 'Shapes'):
        for shape in doc.Shapes:
            if shape.Type == 4:  
                if search_term.lower() in shape.Text.GetText().lower():
                    shape.Text.SetText(f"Etiqueta Encontrada: {search_term}")
                    break

@app.route('/')
def index():
    return render_template('index.html', categorias=CATEGORIAS.keys())

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    search_term = data.get("search_term", "").strip().lower()  
    categoria_selecionada = data.get("etiqueta", "").strip()

    if categoria_selecionada not in etiquetas:
        return jsonify({"error": "Etiqueta não encontrada!"}), 400

    file_path = etiquetas[categoria_selecionada].get(search_term, None)  

    print(f"Buscando por: '{search_term}' na categoria '{categoria_selecionada}'")

    if not file_path:
        return jsonify({"error": "Arquivo correspondente não encontrado!"}), 400

    try:
        corel, doc = open_coreldraw_file(file_path)
        search_and_customize_label(doc, search_term)
        return jsonify({"message": f"Etiqueta '{search_term}' processada com sucesso!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pg2')
def pg2():
    return render_template('pg2.html')

if __name__ == "__main__":
    app.run(debug=True)
