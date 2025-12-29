"""
Módulo para gerar imagens PNG/JPG a partir dos comunicados
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import re
import random
import logging
from html import unescape

# Configurar logging
logger = logging.getLogger(__name__)

# Constantes de configuração
DIMENSOES_PADRAO = (1200, 630)
MARGEM_X_PADRAO = 60
CORPO_WIDTH = 880
CORPO_PADDING = 20
CORPO_ALTURA_MINIMA = 200
CORPO_OVERLAY_ALPHA = 230
LINE_HEIGHT_RATIO = 1.6
ESPACAMENTO_TITULO = 10
ESPACAMENTO_SUBTITULO = 8
ESPACAMENTO_RODAPE = 5
ESPACAMENTO_PUBLICO_ALVO = 5
MARGEM_RODAPE = 30
MARGEM_IMAGEM = 50
QUALIDADE_IMAGEM = 95

# Cores padrão
COR_PRETO = '#000000'
COR_BRANCO = '#FFFFFF'

# Caminhos das fontes
FONTE_GLOBO_REGULAR = 'static/fonts/GlobotipoCorporativa-Regular.ttf'
FONTE_GLOBO_BOLD = 'static/fonts/GlobotipoCorporativa-Bold.ttf'

# Títulos especiais que devem ser quebrados em duas linhas
TITULOS_ESPECIAIS = {
    'INDISPONIBILIDADE': ['INDISPONIBILIDADE', 'DETECTADA'],
    'INSTABILIDADE': ['INSTABILIDADE', 'DETECTADA'],
    'DEGRADAÇÃO': ['DEGRADAÇÃO', 'DETECTADA'],
    'NORMALIZAÇÃO': ['AMBIENTE', 'NORMALIZADO']
}

def _detectar_formato_texto(parte):
    """
    Detecta o formato de uma parte de texto (negrito, itálico ou normal).
    
    Returns:
        tuple: (texto_limpo, marcador, tipo) onde tipo é 'bold', 'italic' ou 'normal'
    """
    if parte.startswith('**') and parte.endswith('**'):
        return parte[2:-2], '**', 'bold'
    elif parte.startswith('_') and parte.endswith('_'):
        return parte[1:-1], '_', 'italic'
    else:
        return parte, None, 'normal'


def _obter_fonte_formatada(fonte_corpo, fonte_corpo_bold, fonte_corpo_italic, tipo):
    """Retorna a fonte apropriada baseada no tipo de formatação."""
    if tipo == 'bold':
        return fonte_corpo_bold
    elif tipo == 'italic':
        return fonte_corpo_italic
    else:
        return fonte_corpo


def _calcular_largura_texto(partes, fonte_corpo, fonte_corpo_bold, fonte_corpo_italic):
    """Calcula a largura total de uma lista de partes formatadas."""
    largura_total = 0
    for parte in partes:
        if not parte:
            continue
        texto, _, tipo = _detectar_formato_texto(parte)
        if texto.strip():
            fonte = _obter_fonte_formatada(fonte_corpo, fonte_corpo_bold, fonte_corpo_italic, tipo)
            bbox = fonte.getbbox(texto)
            largura_total += bbox[2] - bbox[0]
            if parte != partes[-1]:
                largura_total += 2  # Espaçamento entre partes
    return largura_total


def _calcular_posicao_x_alinhada(texto_pos_x, corpo_width, largura_total, alinhamento):
    """Calcula a posição X baseada no alinhamento."""
    if alinhamento == 'center':
        return texto_pos_x + ((corpo_width - (CORPO_PADDING * 2)) - largura_total) // 2
    elif alinhamento == 'right':
        return texto_pos_x + corpo_width - (CORPO_PADDING * 2) - largura_total
    else:
        return texto_pos_x


def quebrar_linha_auto(partes_linha, largura_max, fonte_corpo, fonte_corpo_bold, fonte_corpo_italic):
    """
    Quebra uma linha automaticamente se exceder largura máxima.
    
    Args:
        partes_linha: Lista de partes da linha (com formatação)
        largura_max: Largura máxima permitida
        fonte_corpo: Fonte normal
        fonte_corpo_bold: Fonte negrito
        fonte_corpo_italic: Fonte itálico
    
    Returns:
        Lista de linhas, onde cada linha é uma lista de partes
    """
    linhas_result = []
    linha_atual = []
    
    for parte in partes_linha:
        if not parte:
            continue
        
        texto, marcador, tipo = _detectar_formato_texto(parte)
        fonte = _obter_fonte_formatada(fonte_corpo, fonte_corpo_bold, fonte_corpo_italic, tipo)
        
        if not texto.strip():
            if marcador:
                linha_atual.append(parte)
            continue
        
        # Quebrar por palavras
        palavras = texto.split(' ')
        for i, palavra in enumerate(palavras):
            if not palavra:  # Espaço vazio (espaço múltiplo)
                if linha_atual:
                    ultima_parte = linha_atual[-1]
                    if marcador and ultima_parte.startswith(marcador) and ultima_parte.endswith(marcador):
                        texto_ultima = ultima_parte[len(marcador):-len(marcador)]
                        linha_atual[-1] = marcador + texto_ultima + ' ' + marcador
                    elif not marcador:
                        if ultima_parte.startswith('**') and ultima_parte.endswith('**'):
                            texto_ultima = ultima_parte[2:-2]
                            linha_atual[-1] = '**' + texto_ultima + ' ' + '**'
                        elif ultima_parte.startswith('_') and ultima_parte.endswith('_'):
                            texto_ultima = ultima_parte[1:-1]
                            linha_atual[-1] = '_' + texto_ultima + ' ' + '_'
                        else:
                            linha_atual[-1] = ultima_parte + ' '
                continue
            
            # Construir texto da linha atual para medir
            texto_linha = ''
            for p in linha_atual:
                texto_p, _, _ = _detectar_formato_texto(p)
                texto_linha += texto_p
            if linha_atual:
                texto_linha += ' '
            texto_linha += palavra
            
            # Medir largura
            bbox = fonte.getbbox(texto_linha)
            largura_teste = bbox[2] - bbox[0]
            
            if largura_teste <= largura_max:
                # Cabe na linha atual
                if linha_atual:
                    linha_atual.append(' ')
                if marcador:
                    linha_atual.append(marcador + palavra + marcador)
                else:
                    linha_atual.append(palavra)
            else:
                # Não cabe, quebrar linha
                if linha_atual:
                    linhas_result.append(linha_atual)
                linha_atual = []
                if marcador:
                    linha_atual.append(marcador + palavra + marcador)
                else:
                    linha_atual.append(palavra)
                if i < len(palavras) - 1:
                    if marcador:
                        linha_atual.append(marcador + ' ' + marcador)
                    else:
                        linha_atual.append(' ')
    
    # Adicionar última linha
    if linha_atual:
        linhas_result.append(linha_atual)
    
    return linhas_result if linhas_result else [partes_linha]


def _carregar_fontes(tamanhos):
    """
    Carrega todas as fontes necessárias.
    
    Args:
        tamanhos: Dicionário com tamanhos {'titulo', 'subtitulo', 'corpo', 'rodape', 'publico_alvo'}
    
    Returns:
        Dicionário com todas as fontes carregadas
    """
    fontes = {}
    try:
        fontes['titulo'] = ImageFont.truetype(FONTE_GLOBO_BOLD, tamanhos['titulo'])
        fontes['subtitulo'] = ImageFont.truetype(FONTE_GLOBO_BOLD, tamanhos['subtitulo'])
        fontes['corpo'] = ImageFont.truetype(FONTE_GLOBO_REGULAR, tamanhos['corpo'])
        fontes['corpo_bold'] = ImageFont.truetype(FONTE_GLOBO_BOLD, tamanhos['corpo'])
        fontes['corpo_italic'] = ImageFont.truetype(FONTE_GLOBO_REGULAR, tamanhos['corpo'])
        fontes['rodape'] = ImageFont.truetype(FONTE_GLOBO_REGULAR, tamanhos['rodape'])
        fontes['publico_alvo'] = ImageFont.truetype(FONTE_GLOBO_REGULAR, tamanhos['publico_alvo'])
    except Exception as e:
        logger.warning(f'Erro ao carregar fonte Globo Corporativa, usando fontes padrão: {e}')
        # Fallback para fontes padrão
        for key in fontes.keys():
            fontes[key] = ImageFont.load_default()
        # Garantir que todas as fontes estejam definidas
        fontes.setdefault('titulo', ImageFont.load_default())
        fontes.setdefault('subtitulo', ImageFont.load_default())
        fontes.setdefault('corpo', ImageFont.load_default())
        fontes.setdefault('corpo_bold', ImageFont.load_default())
        fontes.setdefault('corpo_italic', ImageFont.load_default())
        fontes.setdefault('rodape', ImageFont.load_default())
        fontes.setdefault('publico_alvo', ImageFont.load_default())
    
    return fontes


def _criar_imagem_base(comunicado):
    """
    Cria a imagem base (template ou gradiente padrão).
    
    Returns:
        tuple: (Image, width, height)
    """
    if comunicado.template and comunicado.template.imagem_fundo:
        try:
            img_path = os.path.join('static', comunicado.template.imagem_fundo)
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            width, height = img.size
            return img, width, height
        except Exception as e:
            logger.error(f'Erro ao carregar template de fundo: {e}', exc_info=True)
    
    # Usar dimensões padrão e criar gradiente
    width, height = DIMENSOES_PADRAO
    img = criar_gradiente_padrao(width, height)
    return img, width, height


def gerar_png(comunicado, configs, formato='PNG'):
    """
    Gera uma imagem PNG do comunicado
    
    Args:
        comunicado: Objeto Comunicado do banco de dados
        configs: Dicionário com configurações de estilo
        formato: 'PNG' ou 'JPEG'
    
    Returns:
        bytes: Imagem em formato de bytes
    """
    # Criar imagem base
    img, width, height = _criar_imagem_base(comunicado)
    draw = ImageDraw.Draw(img)
    
    # Tamanhos das fontes
    tamanhos = {
        'titulo': getattr(comunicado, 'tipo_tamanho', 42),
        'subtitulo': getattr(comunicado, 'subtitulo_tamanho', 32),
        'corpo': getattr(comunicado, 'corpo_tamanho', 24),
        'rodape': getattr(comunicado, 'rodape_tamanho', 24),
        'publico_alvo': getattr(comunicado, 'publico_alvo_tamanho', 16)
    }
    
    # Carregar fontes
    fontes = _carregar_fontes(tamanhos)
    fonte_titulo = fontes['titulo']
    fonte_subtitulo = fontes['subtitulo']
    fonte_corpo = fontes['corpo']
    fonte_corpo_bold = fontes['corpo_bold']
    fonte_corpo_italic = fontes['corpo_italic']
    fonte_rodape = fontes['rodape']
    fonte_publico_alvo = fontes['publico_alvo']
    
    # Cores
    cor_titulo = configs.get('cor_titulo', COR_BRANCO)
    cor_subtitulo = COR_PRETO
    cor_corpo = COR_PRETO
    cor_rodape = COR_PRETO
    
    # Posições personalizadas
    tipo_pos_x = getattr(comunicado, 'tipo_pos_x', MARGEM_X_PADRAO)
    tipo_pos_y = getattr(comunicado, 'tipo_pos_y', 80)
    subtitulo_pos_x = getattr(comunicado, 'subtitulo_pos_x', 0)
    subtitulo_pos_y = getattr(comunicado, 'subtitulo_pos_y', 430)
    corpo_pos_x = getattr(comunicado, 'corpo_pos_x', MARGEM_X_PADRAO)
    corpo_pos_y = getattr(comunicado, 'corpo_pos_y', 510)
    corpo_alinhamento = getattr(comunicado, 'corpo_alinhamento', 'justify')
    rodape_pos_x = getattr(comunicado, 'rodape_pos_x', MARGEM_X_PADRAO)
    rodape_pos_y = getattr(comunicado, 'rodape_pos_y', 1000)
    publico_alvo_pos_x = getattr(comunicado, 'publico_alvo_pos_x', MARGEM_X_PADRAO)
    publico_alvo_pos_y = getattr(comunicado, 'publico_alvo_pos_y', 1120)
    
    # Largura máxima para textos
    max_width = width - (MARGEM_X_PADRAO * 2)
    
    # Desenhar título (tipo) em NEGRITO E MAIÚSCULAS
    if comunicado.titulo:
        titulo_upper = comunicado.titulo.upper()
        
        # Verificar se é um título especial que deve ser quebrado em duas linhas
        titulo_linhas = TITULOS_ESPECIAIS.get(titulo_upper, None)
        if titulo_linhas is None:
            titulo_linhas = quebrar_texto(titulo_upper, fonte_titulo, max_width)
        
        y_position = tipo_pos_y
        for linha in titulo_linhas:
            draw.text((tipo_pos_x, y_position), linha, font=fonte_titulo, fill=cor_titulo)
            y_position += tamanhos['titulo'] + ESPACAMENTO_TITULO
    
    # Desenhar subtítulo (centralizado e negrito se pos_x = 0, senão alinhado à esquerda)
    if comunicado.subtitulo:
        # Usar subtítulo como está (sem conversão automática para maiúsculas)
        subtitulo_linhas = quebrar_texto(comunicado.subtitulo, fonte_subtitulo, max_width)
        y_position = subtitulo_pos_y
        for linha in subtitulo_linhas:
            if subtitulo_pos_x == 0:
                # Calcular posição centralizada
                bbox = fonte_subtitulo.getbbox(linha)
                text_width = bbox[2] - bbox[0]
                x_centered = (width - text_width) // 2
                draw.text((x_centered, y_position), linha, font=fonte_subtitulo, fill=cor_subtitulo)
            else:
                # Usar posição X especificada
                draw.text((subtitulo_pos_x, y_position), linha, font=fonte_subtitulo, fill=cor_subtitulo)
            y_position += tamanhos['subtitulo'] + ESPACAMENTO_SUBTITULO
    
    # Desenhar corpo (área central branca)
    if comunicado.corpo:
        # Desenhar texto do corpo com formatação PRIMEIRO para calcular altura necessária
        corpo_limpo = limpar_html(comunicado.corpo)
        
        # Calcular espaçamento entre linhas baseado no line-height
        espacamento_linha = int(round(tamanhos['corpo'] * LINE_HEIGHT_RATIO))
        
        # Calcular altura dinâmica do container baseado no conteúdo
        linhas_temp = corpo_limpo.split('\n')
        num_linhas_estimado = len([l for l in linhas_temp if l.strip()])
        
        # Calcular altura necessária: padding superior + padding inferior + linhas * espaçamento
        corpo_height = (CORPO_PADDING * 2) + (num_linhas_estimado * espacamento_linha) + CORPO_PADDING
        corpo_height = max(CORPO_ALTURA_MINIMA, corpo_height)
        
        # Criar retângulo branco semi-transparente para o corpo
        corpo_y_start = corpo_pos_y - CORPO_PADDING
        
        # Criar camada semi-transparente
        overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            [corpo_pos_x - CORPO_PADDING, corpo_y_start, 
             corpo_pos_x + CORPO_WIDTH, corpo_y_start + corpo_height],
            fill=(255, 255, 255, CORPO_OVERLAY_ALPHA)
        )
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Posição inicial do texto
        y_position = corpo_pos_y + CORPO_PADDING
        texto_pos_x = corpo_pos_x + CORPO_PADDING
        largura_maxima = CORPO_WIDTH - (CORPO_PADDING * 2)
        
        # Calcular limite do rodapé uma única vez
        limite_rodape = rodape_pos_y - MARGEM_RODAPE
        
        # Processar cada linha do texto (respeitando quebras de linha manuais)
        linhas_originais = corpo_limpo.split('\n')
        
        for linha_manual in linhas_originais:
            # Verificar se ultrapassou o limite da imagem ou se está muito próximo do rodapé
            if y_position > limite_rodape or y_position > height - MARGEM_IMAGEM:
                break
            
            # Remover espaços em branco no final da linha (mas preservar linha vazia)
            linha_manual = linha_manual.rstrip(' \t\r')
                
            # Linha vazia = quebra de linha manual
            if not linha_manual.strip():
                y_position += espacamento_linha
                continue
            
            # Processar formatação de negrito e itálico nesta linha manual
            partes_formatadas = re.split(r'(\*\*.*?\*\*|_.*?_)', linha_manual)
            partes_formatadas = [p for p in partes_formatadas if p]
            
            # Construir texto completo removendo marcadores de formatação para medir
            texto_linha_completa = ''
            for parte in partes_formatadas:
                texto, _, _ = _detectar_formato_texto(parte)
                texto_linha_completa += texto
            
            # Verificar se a linha cabe inteira ou precisa ser quebrada
            bbox_teste = fonte_corpo.getbbox(texto_linha_completa)
            largura_linha_completa = bbox_teste[2] - bbox_teste[0]
            
            if largura_linha_completa <= largura_maxima:
                # Linha cabe inteira - renderizar diretamente
                linhas_finais = [partes_formatadas]
            else:
                # Linha não cabe - quebrar automaticamente
                linhas_finais = quebrar_linha_auto(
                    partes_formatadas, largura_maxima, 
                    fonte_corpo, fonte_corpo_bold, fonte_corpo_italic
                )
            
            # Renderizar cada linha resultante
            for linha_parts in linhas_finais:
                # Verificar se ultrapassou o limite antes do rodapé
                if y_position > limite_rodape or y_position > height - MARGEM_IMAGEM:
                    break
                
                # Calcular largura total para alinhamento
                if corpo_alinhamento in ['center', 'right']:
                    largura_total = _calcular_largura_texto(
                        linha_parts, fonte_corpo, fonte_corpo_bold, fonte_corpo_italic
                    )
                else:
                    largura_total = 0
                
                # Calcular posição X baseada no alinhamento
                x_position = _calcular_posicao_x_alinhada(
                    texto_pos_x, CORPO_WIDTH, largura_total, corpo_alinhamento
                )
                
                # Desenhar cada parte da linha
                for i, parte in enumerate(linha_parts):
                    if not parte:
                        continue
                    
                    texto_parte, marcador, tipo = _detectar_formato_texto(parte)
                    fonte_atual = _obter_fonte_formatada(fonte_corpo, fonte_corpo_bold, fonte_corpo_italic, tipo)
                    
                    # Verificar se precisa adicionar espaço antes desta parte
                    if i > 0 and texto_parte and texto_parte.strip():
                        parte_anterior = linha_parts[i-1]
                        if parte_anterior:
                            texto_anterior, _, _ = _detectar_formato_texto(parte_anterior)
                            # Se ambas têm conteúdo, verificar se há espaço entre elas
                            if texto_anterior and texto_anterior.strip():
                                # Verificar se há espaço no final da parte anterior ou início da atual
                                anterior_termina_espaco = texto_anterior.endswith(' ')
                                atual_comeca_espaco = texto_parte.startswith(' ')
                                
                                # Se não há espaço em nenhuma das bordas, adicionar um espaço
                                if not anterior_termina_espaco and not atual_comeca_espaco:
                                    bbox_espaco = fonte_atual.getbbox(' ')
                                    x_position += bbox_espaco[2] - bbox_espaco[0]
                    
                    # Desenhar o texto da parte
                    if texto_parte == ' ':
                        bbox_espaco = fonte_atual.getbbox(' ')
                        x_position += bbox_espaco[2] - bbox_espaco[0]
                    elif texto_parte.strip():
                        # Determinar se devemos preservar o espaço no final
                        # Preservar se a próxima parte não começar com espaço
                        preservar_espaco_final = False
                        if i < len(linha_parts) - 1:
                            proxima_parte = linha_parts[i + 1]
                            if proxima_parte:
                                texto_proximo, _, _ = _detectar_formato_texto(proxima_parte)
                                if texto_proximo and texto_proximo.strip() and not texto_proximo.startswith(' '):
                                    # Próxima parte tem conteúdo e não começa com espaço
                                    # Preservar espaço no final desta parte se houver
                                    preservar_espaco_final = texto_parte.endswith(' ')
                        
                        # Renderizar o texto
                        if preservar_espaco_final:
                            # Preservar espaço no final
                            texto_para_renderizar = texto_parte
                        else:
                            # Remover espaços no final
                            texto_para_renderizar = texto_parte.rstrip(' \t\r')
                        
                        if texto_para_renderizar:
                            draw.text((x_position, y_position), texto_para_renderizar, 
                                     font=fonte_atual, fill=cor_corpo)
                            bbox = fonte_atual.getbbox(texto_para_renderizar)
                            x_position += bbox[2] - bbox[0]
                
                # Próxima linha
                y_position += espacamento_linha
    
    # Desenhar rodapé (centralizado, preto)
    if comunicado.rodape:
        rodape_limpo = limpar_html(comunicado.rodape)
        # Usar largura maior para o rodapé para garantir que caiba em uma linha
        max_width_rodape = width - int(MARGEM_X_PADRAO * 0.8)  # Apenas 48px de margem total
        rodape_linhas = quebrar_texto(rodape_limpo, fonte_rodape, max_width_rodape)
        y_position = rodape_pos_y
        
        for linha in rodape_linhas:
            # Centralizar o rodapé
            bbox = fonte_rodape.getbbox(linha)
            text_width = bbox[2] - bbox[0]
            x_centered = (width - text_width) // 2
            draw.text((x_centered, y_position), linha, font=fonte_rodape, fill=cor_rodape)
            y_position += tamanhos['rodape'] + ESPACAMENTO_RODAPE
    
    # Desenhar público alvo
    if comunicado.publico_alvo:
        max_width_publico_alvo = width - (publico_alvo_pos_x * 2)
        publico_alvo_linhas = quebrar_texto(comunicado.publico_alvo, fonte_publico_alvo, max_width_publico_alvo)
        
        y_position = publico_alvo_pos_y
        for linha in publico_alvo_linhas:
            draw.text((publico_alvo_pos_x, y_position), linha, font=fonte_publico_alvo, fill=cor_corpo)
            y_position += tamanhos['publico_alvo'] + ESPACAMENTO_PUBLICO_ALVO
    
    # Converter para bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format=formato, quality=QUALIDADE_IMAGEM)
    img_bytes.seek(0)
    
    return img_bytes.getvalue()


def criar_gradiente_padrao(width, height):
    """
    Cria um fundo azul com textura similar à imagem fornecida.
    
    Otimizado para melhor performance usando operações em lote quando possível.
    """
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # Gradiente horizontal de azul claro para roxo
    for x in range(width):
        ratio = x / width
        
        # Gradiente: azul claro (#00bfff) -> azul (#1e90ff) -> roxo (#6a5acd) -> roxo claro (#8b5cf6)
        if ratio < 0.25:
            # Primeiro quartil: azul claro para azul
            local_ratio = ratio / 0.25
            r = int(0 + (30 * local_ratio))
            g = int(191 - (47 * local_ratio))
            b = 255
        elif ratio < 0.75:
            # Segundo e terceiro quartis: azul para roxo
            local_ratio = (ratio - 0.25) / 0.5
            r = int(30 + (76 * local_ratio))
            g = int(144 - (54 * local_ratio))
            b = int(255 - (50 * local_ratio))
        else:
            # Último quartil: roxo para roxo claro
            local_ratio = (ratio - 0.75) / 0.25
            r = int(106 + (33 * local_ratio))
            g = int(90 + (2 * local_ratio))
            b = int(205 + (41 * local_ratio))
        
        # Preencher coluna inteira de uma vez (mais eficiente que linha por linha)
        cor = (r, g, b)
        for y in range(height):
            pixels[x, y] = cor
    
    # Adicionar textura de pontos para simular o efeito da imagem
    random.seed(42)  # Para consistência
    num_pontos = width * height // 50  # Densidade de pontos
    draw = ImageDraw.Draw(img)
    
    for _ in range(num_pontos):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        # Pontos mais escuros para textura
        brightness = random.randint(-15, 5)
        pixel = pixels[x, y]
        new_pixel = tuple(max(0, min(255, c + brightness)) for c in pixel)
        draw.point((x, y), fill=new_pixel)
    
    return img


def quebrar_texto(texto, fonte, max_width):
    """Quebra o texto em linhas que cabem na largura máxima"""
    linhas = []
    palavras = texto.split()
    
    linha_atual = []
    for palavra in palavras:
        teste_linha = ' '.join(linha_atual + [palavra])
        
        # Verificar largura (usando aproximação)
        try:
            bbox = fonte.getbbox(teste_linha)
            largura = bbox[2] - bbox[0]
        except Exception:
            largura = len(teste_linha) * 10  # Fallback
        
        if largura <= max_width:
            linha_atual.append(palavra)
        else:
            if linha_atual:
                linhas.append(' '.join(linha_atual))
            linha_atual = [palavra]
    
    if linha_atual:
        linhas.append(' '.join(linha_atual))
    
    return linhas


def limpar_html(texto):
    """Processa tags HTML e converte para texto formatado"""
    if not texto:
        return ''
    
    # IMPORTANTE: Ordem das operações é crucial!
    # Primeiro, converter quebras de linha HTML para \n ANTES de remover outras tags
    
    # Converter diferentes tipos de quebras de linha HTML para \n
    # Tratar blocos (div, p) que criam quebras de linha
    texto = re.sub(r'</div>', '\n', texto, flags=re.IGNORECASE)
    texto = re.sub(r'</p>', '\n', texto, flags=re.IGNORECASE)
    texto = re.sub(r'<div[^>]*>', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'<p[^>]*>', '', texto, flags=re.IGNORECASE)
    
    # Converter quebras de linha explícitas (<br>, <br/>, <br />)
    texto = re.sub(r'<br\s*/?>', '\n', texto, flags=re.IGNORECASE)
    
    # Processar listas (também criam quebras)
    texto = re.sub(r'<li[^>]*>', '• ', texto, flags=re.IGNORECASE)
    texto = re.sub(r'</li>', '\n', texto, flags=re.IGNORECASE)
    texto = re.sub(r'<ul[^>]*>', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'</ul>', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'<ol[^>]*>', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'</ol>', '', texto, flags=re.IGNORECASE)
    
    # Manter marcadores de formatação temporariamente (ANTES de remover outras tags)
    texto = re.sub(r'<b[^>]*>', '**', texto, flags=re.IGNORECASE)
    texto = re.sub(r'</b>', '**', texto, flags=re.IGNORECASE)
    texto = re.sub(r'<strong[^>]*>', '**', texto, flags=re.IGNORECASE)
    texto = re.sub(r'</strong>', '**', texto, flags=re.IGNORECASE)
    
    texto = re.sub(r'<i[^>]*>', '_', texto, flags=re.IGNORECASE)
    texto = re.sub(r'</i>', '_', texto, flags=re.IGNORECASE)
    texto = re.sub(r'<em[^>]*>', '_', texto, flags=re.IGNORECASE)
    texto = re.sub(r'</em>', '_', texto, flags=re.IGNORECASE)
    
    texto = re.sub(r'<u[^>]*>', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'</u>', '', texto, flags=re.IGNORECASE)
    
    # AGORA remover outras tags HTML (mas preservar os \n que já foram inseridos)
    texto = re.sub(r'<[^>]+>', '', texto)
    
    # Decodificar entidades HTML
    texto = unescape(texto)
    texto = texto.replace('&nbsp;', ' ')
    
    # IMPORTANTE: NÃO limpar quebras de linha consecutivas
    # Cada <br> deve gerar uma quebra de linha, mesmo que sejam consecutivas
    # Isso garante que quebras manuais sejam sempre respeitadas
    
    # Remover apenas espaços em branco nas extremidades, mas PRESERVAR quebras de linha
    # strip() remove \n também, então precisamos fazer manualmente
    texto = texto.lstrip(' \t\r')  # Remove espaços/tabs no início, mas preserva \n
    texto = texto.rstrip(' \t\r')  # Remove espaços/tabs no final, mas preserva \n
    
    return texto
