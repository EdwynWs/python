from flask import Flask, request, jsonify, render_template
import win32com.client
import pythoncom
import os

app = Flask(__name__)

def open_coreldraw_file(file_path):
    pythoncom.CoInitialize()
    corel = win32com.client.Dispatch("CorelDRAW.Application")
    corel.Visible = True  

   
    file_extension = os.path.splitext(file_path)[1].lower()

  
    if file_extension == '.cdr':
        doc = corel.OpenDocument(file_path)
    elif file_extension == '.pdf':
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
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    search_term = data.get("text")
    
    file_path = r"C:\Users\Pichau\OneDrive\Área de Trabalho\tudo\EtiquetaCEV-06-04.pdf" 
    file_path = r"C:\Users\Pichau\OneDrive\Área de Trabalho\tudo\Coletor de Esterco\220V\B1 - P34 - VRC- CEV22T-03-04.5-0-S\Etiqueta CEV-01-02 380V.cdr"  # exemplo de CDcR

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
