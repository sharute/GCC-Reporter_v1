"""
Módulo para gerar imagens PNG/JPG a partir do HTML da prévia
Usa html2image para renderizar o HTML diretamente, garantindo 100% de fidelidade com a prévia
"""
from html2image import Html2Image
from io import BytesIO
import os
from flask import render_template

def gerar_png_html(comunicado, configs, formato='PNG'):
    """
    Gera uma imagem PNG do comunicado renderizando o HTML da prévia diretamente
    Isso garante que a imagem seja IDÊNTICA à prévia HTML
    
    Args:
        comunicado: Objeto Comunicado do banco de dados
        configs: Dicionário com configurações de estilo
        formato: 'PNG' ou 'JPEG'
    
    Returns:
        bytes: Imagem em formato de bytes
    """
    from app import app
    
    # Renderizar o HTML da prévia
    template = comunicado.template if comunicado.template else None
    
    with app.app_context():
        html_content = render_template('preview_comunicado.html',
            titulo=comunicado.titulo,
            subtitulo=comunicado.subtitulo,
            corpo=comunicado.corpo,
            rodape=comunicado.rodape,
            publico_alvo=comunicado.publico_alvo,
            template=template,
            configs=configs,
            tipo_pos_x=getattr(comunicado, 'tipo_pos_x', 60),
            tipo_pos_y=getattr(comunicado, 'tipo_pos_y', 80),
            tipo_tamanho=getattr(comunicado, 'tipo_tamanho', 42),
            subtitulo_pos_x=getattr(comunicado, 'subtitulo_pos_x', 0),
            subtitulo_pos_y=getattr(comunicado, 'subtitulo_pos_y', 430),
            subtitulo_tamanho=getattr(comunicado, 'subtitulo_tamanho', 32),
            corpo_pos_x=getattr(comunicado, 'corpo_pos_x', 60),
            corpo_pos_y=getattr(comunicado, 'corpo_pos_y', 510),
            corpo_tamanho=getattr(comunicado, 'corpo_tamanho', 24),
            corpo_alinhamento=getattr(comunicado, 'corpo_alinhamento', 'justify'),
            rodape_pos_x=getattr(comunicado, 'rodape_pos_x', 60),
            rodape_pos_y=getattr(comunicado, 'rodape_pos_y', 1000),
            rodape_tamanho=getattr(comunicado, 'rodape_tamanho', 24),
            publico_alvo_pos_x=getattr(comunicado, 'publico_alvo_pos_x', 60),
            publico_alvo_pos_y=getattr(comunicado, 'publico_alvo_pos_y', 1120),
            publico_alvo_tamanho=getattr(comunicado, 'publico_alvo_tamanho', 16)
        )
    
    # Criar instância do Html2Image
    hti = Html2Image()
    
    # Configurar tamanho da imagem (1000x1300 como na prévia)
    width = 1000
    height = 1300
    
    # Criar arquivo temporário único
    import tempfile
    import uuid
    temp_file = os.path.join(tempfile.gettempdir(), f'comunicado_{uuid.uuid4().hex}.png')
    
    try:
        # Renderizar HTML para imagem
        # Usar tamanho customizado e qualidade alta
        hti.screenshot(
            html_str=html_content,
            save_as=temp_file,
            size=(width, height)
        )
        
        # Ler a imagem gerada
        with open(temp_file, 'rb') as f:
            img_bytes = f.read()
        
        return img_bytes
    finally:
        # Remover arquivo temporário
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass

