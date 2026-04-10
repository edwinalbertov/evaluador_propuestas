import os
from pathlib import Path
from azure.ai.openai import AzureOpenAI

def analizar_carpeta(ruta_carpeta):
    """
    Lee el contenido de una carpeta, cuenta los archivos y muestra información sobre ellos.
    
    Args:
        ruta_carpeta (str): Ruta de la carpeta a analizar
    """
    try:
        carpeta = Path(ruta_carpeta)
        
        if not carpeta.exists():
            print(f"La carpeta '{ruta_carpeta}' no existe.")
            return
        
        if not carpeta.is_dir():
            print(f"'{ruta_carpeta}' no es una carpeta.")
            return
        
        archivos = list(carpeta.iterdir())
        archivos_solo = [f for f in archivos if f.is_file()]
        
        print(f"Total de archivos: {len(archivos_solo)}\n")
        print("Detalle de archivos:")
        print("-" * 60)
        
        for archivo in archivos_solo:
            tamaño = archivo.stat().st_size
            extension = archivo.suffix
            print(f"Nombre: {archivo.name}")
            print(f"  Tipo: {extension if extension else 'sin extensión'}")
            print(f"  Tamaño: {tamaño} bytes")
            print()
        
        # Analizar subcarpetas recursivamente
        print("\n" + "=" * 60)
        print("SUBCARPETAS:")
        print("=" * 60)
        
        subcarpetas = [f for f in archivos if f.is_dir()]
        for subcarpeta in subcarpetas:
            archivos_sub = list(subcarpeta.rglob('*'))
            archivos_sub_solo = [f for f in archivos_sub if f.is_file()]
            print(f"\n📁 {subcarpeta.name}: {len(archivos_sub_solo)} archivos")
            for archivo in archivos_sub_solo:
                print(f"   - {archivo.name} ({archivo.stat().st_size} bytes)")
        
        # Resumen ejecutivo
        print("\n" + "=" * 60)
        print("RESUMEN EJECUTIVO:")
        print("=" * 60)
        total_archivos = len(archivos_solo) + sum(len([f for f in s.rglob('*') if f.is_file()]) for s in subcarpetas)
        total_tamaño = sum(f.stat().st_size for f in carpeta.rglob('*') if f.is_file())
        print(f"Total de archivos: {total_archivos}")
        print(f"Total de tamaño: {total_tamaño / 1024:.2f} KB")
        print(f"Número de subcarpetas: {len(subcarpetas)}")
    
    except Exception as e:
        print(f"Error al procesar la carpeta: {e}")

# Uso
if __name__ == "__main__":
    ruta = os.getcwd()  # Usa el directorio actual
    analizar_carpeta(ruta)

    # Integración con Azure OpenAI para analizar documentos

    def analizar_documentos_con_llm(ruta_carpeta):
        """
        Lee documentos de una carpeta y usa Azure OpenAI para generar resúmenes.
        """
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        carpeta = Path(ruta_carpeta)
        documentos = [f for f in carpeta.rglob('*') if f.is_file() and f.suffix in ['.txt', '.pdf', '.docx']]
        
        for doc in documentos:
            try:
                contenido = doc.read_text(encoding='utf-8', errors='ignore')[:4000]
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un asistente que resume documentos."},
                        {"role": "user", "content": f"Resume este documento:\n\n{contenido}"}
                    ]
                )
                
                print(f"\n📄 {doc.name}")
                print(f"Resumen: {response.choices[0].message.content}\n")
            except Exception as e:
                print(f"Error procesando {doc.name}: {e}")

    # Llamar función
    analizar_documentos_con_llm(os.path.join(ruta, "ejemplos"))