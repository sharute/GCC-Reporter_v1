from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_, text
from datetime import datetime, timezone, timedelta
import os
from io import BytesIO
import re
from functools import wraps
from time import time
import logging
import secrets

# Carregar variáveis de ambiente (opcional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv não instalado, usar apenas variáveis de ambiente do sistema
    pass

app = Flask(__name__)

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurações via variáveis de ambiente (com valores padrão seguros)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
# Para SQLite, usar caminho absoluto para evitar problemas com diretório de trabalho
default_db_path = os.path.join(BASE_DIR, 'database', 'comunicados.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', f'sqlite:///{default_db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
app.config['HOST'] = os.getenv('FLASK_HOST', '0.0.0.0')
app.config['PORT'] = int(os.getenv('FLASK_PORT', '5000'))

db = SQLAlchemy(app)

# Configurar fuso horário (Brasil/São Paulo - UTC-3)
TZ_BRASIL = timezone(timedelta(hours=-3))

def agora_brasil():
    """Retorna o datetime atual no fuso horário de Brasília (UTC-3) como datetime naive"""
    # Obter UTC atual
    utc_now = datetime.now(timezone.utc)
    # Converter para horário de Brasília (UTC-3)
    dt_brasil = utc_now.astimezone(TZ_BRASIL)
    # Retornar como datetime naive (sem timezone) para compatibilidade com SQLite
    return dt_brasil.replace(tzinfo=None)

# Configurar logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/audit.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Rate limiting
request_history = {}
RATE_LIMIT = 30  # requests per minute
RATE_WINDOW = 60  # seconds

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time()
        
        # Clean old entries
        if client_ip in request_history:
            request_history[client_ip] = [t for t in request_history[client_ip] if current_time - t < RATE_WINDOW]
        else:
            request_history[client_ip] = []
        
        # Check rate limit
        if len(request_history[client_ip]) >= RATE_LIMIT:
            return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
        
        request_history[client_ip].append(current_time)
        return f(*args, **kwargs)
    return decorated_function

def sanitize_html(text):
    """Remove scripts and dangerous HTML, keep only safe formatting"""
    if not text:
        return text
    
    # Remove script tags and their content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove dangerous attributes
    text = re.sub(r'\s(on\w+)=["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s(javascript:)[^"\'\s>]*', '', text, flags=re.IGNORECASE)
    
    # Remove style attributes (keep only CSS in head)
    text = re.sub(r'\sstyle=["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
    
    # Keep only safe tags
    allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'br', 'p', 'ul', 'ol', 'li', 'span', 'div']
    pattern = r'<(?!/?' + '|/?'.join(allowed_tags) + r'\b)[^>]+>'
    text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text

def processar_tags(tags_input):
    """
    Processa e normaliza tags: remove espaços, duplicatas, e caracteres inválidos.
    Retorna string com tags separadas por vírgula.
    """
    if not tags_input:
        return ''
    
    # Se for string, dividir por vírgula
    if isinstance(tags_input, str):
        tags_list = [tag.strip() for tag in tags_input.split(',')]
    elif isinstance(tags_input, list):
        tags_list = [str(tag).strip() for tag in tags_input]
    else:
        return ''
    
    # Remover tags vazias e normalizar (primeira letra maiúscula, resto minúscula)
    tags_limpas = []
    for tag in tags_list:
        tag = tag.strip()
        if tag:
            # Remover caracteres especiais perigosos, manter apenas letras, números, espaços e hífens
            tag = re.sub(r'[^a-zA-Z0-9\s\-_]', '', tag)
            tag = tag.strip()
            if tag:
                # Capitalizar primeira letra de cada palavra
                tag = ' '.join(word.capitalize() for word in tag.split())
                tags_limpas.append(tag)
    
    # Remover duplicatas mantendo ordem
    tags_unicas = []
    for tag in tags_limpas:
        if tag not in tags_unicas:
            tags_unicas.append(tag)
    
    return ', '.join(tags_unicas)

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    imagem_fundo = db.Column(db.String(200))
    criado_em = db.Column(db.DateTime, default=agora_brasil)
    ativo = db.Column(db.Boolean, default=True)
    
class Configuracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), default='texto')  # texto, cor, numero
    descricao = db.Column(db.String(200))

class Comunicado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_unico = db.Column(db.String(20), unique=True, nullable=False)  # Ex: COM-2511281 (COM-YYMMDDN)
    titulo = db.Column(db.String(200), nullable=False)
    subtitulo = db.Column(db.String(300))
    corpo = db.Column(db.Text, nullable=False)
    rodape = db.Column(db.Text)
    publico_alvo = db.Column(db.String(100))
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'))
    status = db.Column(db.String(20), default='rascunho')  # rascunho, enviado
    tags = db.Column(db.Text, default='')  # Tags separadas por vírgula (ex: "SAP,Oracle,MySQL")
    criado_em = db.Column(db.DateTime, default=agora_brasil)
    atualizado_em = db.Column(db.DateTime, default=agora_brasil, onupdate=agora_brasil)
    criado_por = db.Column(db.String(100))
    atualizado_por = db.Column(db.String(100))
    # Posições personalizadas
    tipo_pos_x = db.Column(db.Integer, default=60)
    tipo_pos_y = db.Column(db.Integer, default=80)
    tipo_tamanho = db.Column(db.Integer, default=42)
    subtitulo_pos_x = db.Column(db.Integer, default=0)
    subtitulo_pos_y = db.Column(db.Integer, default=430)
    subtitulo_tamanho = db.Column(db.Integer, default=32)
    corpo_pos_x = db.Column(db.Integer, default=60)
    corpo_pos_y = db.Column(db.Integer, default=510)
    corpo_tamanho = db.Column(db.Integer, default=24)
    corpo_alinhamento = db.Column(db.String(20), default='justify')
    rodape_pos_x = db.Column(db.Integer, default=60)
    rodape_pos_y = db.Column(db.Integer, default=1000)
    rodape_tamanho = db.Column(db.Integer, default=24)
    publico_alvo_pos_x = db.Column(db.Integer, default=60)
    publico_alvo_pos_y = db.Column(db.Integer, default=1120)
    publico_alvo_tamanho = db.Column(db.Integer, default=16)
    
    template = db.relationship('Template', backref='comunicados')

# Rotas principais
@app.route('/')
def index():
    return redirect(url_for('criar_comunicado'))

@app.route('/criar-comunicado', methods=['GET', 'POST'])
def criar_comunicado():
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Sanitize HTML content
        corpo_sanitized = sanitize_html(data.get('corpo', ''))
        rodape_sanitized = sanitize_html(data.get('rodape', ''))
        
        # Log audit trail
        logger.info(f"[CRIAR] IP: {request.remote_addr} | Tipo: {data.get('titulo')} | Status: {data.get('status', 'enviado')}")
        
        # Gerar código único no formato COM-YYMMDDN
        # Exemplo: COM-2511281 (COM-25/11/28 - 1º comunicado do dia)
        data_atual = agora_brasil()
        ano = str(data_atual.year)[-2:]  # Últimos 2 dígitos do ano
        mes = f"{data_atual.month:02d}"  # Mês com 2 dígitos
        dia = f"{data_atual.day:02d}"    # Dia com 2 dígitos
        
        # Buscar último comunicado do mesmo dia
        prefixo_dia = f'COM-{ano}{mes}{dia}'
        ultimo_com = Comunicado.query.filter(
            Comunicado.codigo_unico.like(f'{prefixo_dia}%')
        ).order_by(Comunicado.id.desc()).first()
        
        if ultimo_com:
            # Extrair o número sequencial do último código
            ultimo_codigo = ultimo_com.codigo_unico
            # O formato é COM-YYMMDDN, então removemos o prefixo e pegamos o número
            try:
                # Remove o prefixo "COM-YYMMDD" e pega o restante como número
                sufixo = ultimo_codigo.replace(prefixo_dia, '')
                ultimo_num = int(sufixo) if sufixo else 0
                novo_num = ultimo_num + 1
            except ValueError:
                novo_num = 1
        else:
            novo_num = 1
        
        codigo_unico = f'{prefixo_dia}{novo_num}'
        
        # Determinar status
        status = data.get('status', 'enviado')  # 'rascunho' ou 'enviado'
        
        # Valores padrão específicos para Indisponibilidade, Instabilidade, Degradação e Normalização
        titulo = data['titulo']
        if titulo and (titulo.upper() == 'INDISPONIBILIDADE' or titulo.upper() == 'INSTABILIDADE' or titulo.upper() == 'DEGRADAÇÃO' or titulo.upper() == 'NORMALIZAÇÃO'):
            tipo_pos_x_default = 60
            tipo_pos_y_default = 120
            tipo_tamanho_default = 60
        else:
            tipo_pos_x_default = 60
            tipo_pos_y_default = 80
            tipo_tamanho_default = 42
        
        comunicado = Comunicado(
            codigo_unico=codigo_unico,
            titulo=titulo,
            subtitulo=data.get('subtitulo'),
            corpo=corpo_sanitized,
            rodape=rodape_sanitized,
            publico_alvo=data.get('publico_alvo'),
            template_id=data['template_id'],
            status=status,
            tags='',  # Tags serão gerenciadas apenas na página de histórico
            criado_por=data.get('criado_por', 'Sistema'),
            atualizado_por=data.get('criado_por', 'Sistema'),
            tipo_pos_x=int(data.get('tipo_pos_x', tipo_pos_x_default)),
            tipo_pos_y=int(data.get('tipo_pos_y', tipo_pos_y_default)),
            tipo_tamanho=int(data.get('tipo_tamanho', tipo_tamanho_default)),
            subtitulo_pos_x=int(data.get('subtitulo_pos_x', 0)),
            subtitulo_pos_y=int(data.get('subtitulo_pos_y', 430)),
            subtitulo_tamanho=int(data.get('subtitulo_tamanho', 32)),
            corpo_pos_x=int(data.get('corpo_pos_x', 60)),
            corpo_pos_y=int(data.get('corpo_pos_y', 510)),
            corpo_tamanho=int(data.get('corpo_tamanho', 24)),
            corpo_alinhamento=data.get('corpo_alinhamento', 'justify'),
            rodape_pos_x=int(data.get('rodape_pos_x', 60)),
            rodape_pos_y=int(data.get('rodape_pos_y', 1200)),
            rodape_tamanho=int(data.get('rodape_tamanho', 24)),
            publico_alvo_pos_x=int(data.get('publico_alvo_pos_x', 60)),
            publico_alvo_pos_y=int(data.get('publico_alvo_pos_y', 1120)),
            publico_alvo_tamanho=int(data.get('publico_alvo_tamanho', 16))
        )
        
        db.session.add(comunicado)
        db.session.commit()
        
        return jsonify({'success': True, 'id': comunicado.id, 'codigo': codigo_unico})
    
    templates = Template.query.filter_by(ativo=True).all()
    configs = {c.chave: c.valor for c in Configuracao.query.all()}
    
    return render_template('criar_comunicado.html', templates=templates, configs=configs)

@app.route('/gerar-imagem/<int:comunicado_id>')
def gerar_imagem(comunicado_id):
    # Usar renderização HTML para garantir 100% de fidelidade com a prévia
    try:
        from scripts.gerar_imagem_html import gerar_png_html
        comunicado = Comunicado.query.get_or_404(comunicado_id)
        configs = {c.chave: c.valor for c in Configuracao.query.all()}
        # Gerar imagem a partir do HTML (método novo - 100% fiel à prévia)
        img_bytes = gerar_png_html(comunicado, configs)
    except Exception as e:
        # Fallback para método antigo se houver erro
        print(f"Erro ao usar renderização HTML, usando método PIL: {e}")
        from scripts.gerar_imagem import gerar_png
        comunicado = Comunicado.query.get_or_404(comunicado_id)
        configs = {c.chave: c.valor for c in Configuracao.query.all()}
        # Gerar imagem
        img_bytes = gerar_png(comunicado, configs)
    
    # Gerar nome do arquivo: tipo_dia_mes_ano.png
    # Sanitizar o título removendo caracteres inválidos para nomes de arquivo
    tipo = re.sub(r'[<>:"/\\|?*]', '', comunicado.titulo).strip()
    tipo = re.sub(r'\s+', '_', tipo)  # Substituir espaços por underscore
    
    # Formatar data: dia_mes_ano
    data = comunicado.criado_em if comunicado.criado_em else agora_brasil()
    dia = f"{data.day:02d}"
    mes = f"{data.month:02d}"
    ano = f"{data.year}"
    
    nome_arquivo = f"{tipo}_{dia}_{mes}_{ano}.png"
    
    return send_file(
        BytesIO(img_bytes),
        mimetype='image/png',
        as_attachment=True,
        download_name=nome_arquivo
    )

@app.route('/preview', methods=['POST'])
@rate_limit
def preview():
    """Retorna prévia em HTML do comunicado"""
    data = request.get_json()
    configs = {c.chave: c.valor for c in Configuracao.query.all()}
    
    # Sanitize HTML content
    corpo_sanitized = sanitize_html(data.get('corpo', ''))
    rodape_sanitized = sanitize_html(data.get('rodape', ''))
    
    template_id = data.get('template_id')
    try:
        template_id = int(template_id) if template_id else None
    except (ValueError, TypeError):
        template_id = None
    template = db.session.get(Template, template_id) if template_id else None
    
    html = render_template('preview_comunicado.html', 
                          titulo=data.get('titulo', ''),
                          subtitulo=data.get('subtitulo', ''),
                          corpo=corpo_sanitized,
                          rodape=rodape_sanitized,
                          publico_alvo=data.get('publico_alvo', ''),
                          tipo_pos_x=data.get('tipo_pos_x', '60'),
                          tipo_pos_y=data.get('tipo_pos_y', '80'),
                          tipo_tamanho=data.get('tipo_tamanho', '42'),
                          subtitulo_pos_x=data.get('subtitulo_pos_x', '0'),
                          subtitulo_pos_y=data.get('subtitulo_pos_y', '430'),
                          subtitulo_tamanho=data.get('subtitulo_tamanho', '32'),
                          corpo_pos_x=data.get('corpo_pos_x', '60'),
                          corpo_pos_y=data.get('corpo_pos_y', '510'),
                          corpo_tamanho=data.get('corpo_tamanho', '24'),
                          corpo_alinhamento=data.get('corpo_alinhamento', 'justify'),
                          rodape_pos_x=data.get('rodape_pos_x', '60'),
                          rodape_pos_y=data.get('rodape_pos_y', '1000'),
                          rodape_tamanho=data.get('rodape_tamanho', '24'),
                          publico_alvo_pos_x=data.get('publico_alvo_pos_x', '60'),
                          publico_alvo_pos_y=data.get('publico_alvo_pos_y', '1120'),
                          publico_alvo_tamanho=data.get('publico_alvo_tamanho', '16'),
                          template=template,
                          configs=configs)
    
    return jsonify({'html': html})

@app.route('/historico')
def historico():
    # Obter parâmetros de busca e filtro
    tag_filtro = request.args.get('tag', '').strip()
    busca_texto = request.args.get('busca', '').strip()
    tipo_filtro = request.args.get('tipo', '').strip()
    data_inicio = request.args.get('data_inicio', '').strip()
    data_fim = request.args.get('data_fim', '').strip()
    
    # Obter parâmetro de página (padrão: 1)
    try:
        pagina_atual = int(request.args.get('page', 1))
        if pagina_atual < 1:
            pagina_atual = 1
    except (ValueError, TypeError):
        pagina_atual = 1
    
    # Limite de registros por página
    registros_por_pagina = 20
    
    # Iniciar query base
    query = Comunicado.query
    
    # Aplicar filtros
    filtros_aplicados = []
    
    # Filtro por tag
    if tag_filtro:
        query = query.filter(
            or_(
                Comunicado.tags.like(f'{tag_filtro},%'),
                Comunicado.tags.like(f'%, {tag_filtro},%'),
                Comunicado.tags.like(f'%, {tag_filtro}'),
                Comunicado.tags == tag_filtro
            )
        )
        filtros_aplicados.append(f'tag={tag_filtro}')
    
    # Filtro por tipo de comunicado (título)
    if tipo_filtro:
        query = query.filter(Comunicado.titulo == tipo_filtro)
        filtros_aplicados.append(f'tipo={tipo_filtro}')
    
    # Busca por texto (título, subtítulo, corpo) - case insensitive e suporta múltiplas palavras
    if busca_texto:
        # Dividir em palavras e buscar cada uma
        palavras = busca_texto.split()
        condicoes_busca = []
        
        for palavra in palavras:
            if palavra.strip():
                busca_pattern = f'%{palavra.strip()}%'
                condicoes_busca.append(
                    or_(
                        Comunicado.titulo.ilike(busca_pattern),
                        Comunicado.subtitulo.ilike(busca_pattern),
                        Comunicado.corpo.ilike(busca_pattern)
                    )
                )
        
        if condicoes_busca:
            # Todas as palavras devem estar presentes (AND)
            query = query.filter(and_(*condicoes_busca))
            filtros_aplicados.append(f'busca={busca_texto}')
    
    # Filtro por período de data de criação
    if data_inicio or data_fim:
        try:
            if data_inicio:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
                # Início do dia
                data_inicio_completa = datetime.combine(data_inicio_obj.date(), datetime.min.time())
                query = query.filter(Comunicado.criado_em >= data_inicio_completa)
                filtros_aplicados.append(f'data_inicio={data_inicio}')
            
            if data_fim:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
                # Fim do dia (23:59:59)
                data_fim_completa = datetime.combine(data_fim_obj.date(), datetime.max.time())
                query = query.filter(Comunicado.criado_em <= data_fim_completa)
                filtros_aplicados.append(f'data_fim={data_fim}')
        except ValueError:
            pass  # Ignorar data inválida
    
    # Contar total de registros (antes da paginação)
    total_registros = query.count()
    
    # Calcular total de páginas
    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina if total_registros > 0 else 1
    
    # Ajustar página atual se necessário
    if pagina_atual > total_paginas and total_paginas > 0:
        pagina_atual = total_paginas
    
    # Calcular offset
    offset = (pagina_atual - 1) * registros_por_pagina
    
    # Executar query com paginação
    comunicados = query.order_by(Comunicado.criado_em.desc()).offset(offset).limit(registros_por_pagina).all()
    
    # Coletar todas as tags únicas para o filtro
    todas_tags = set()
    for com in Comunicado.query.all():
        if com.tags:
            tags_list = [tag.strip() for tag in com.tags.split(',')]
            todas_tags.update(tags_list)
    
    # Coletar todos os tipos únicos de comunicado
    todos_tipos = set()
    for com in Comunicado.query.all():
        if com.titulo:
            todos_tipos.add(com.titulo)
    
    return render_template('historico.html', 
                         comunicados=comunicados, 
                         todas_tags=sorted(todas_tags),
                         todos_tipos=sorted(todos_tipos),
                         tag_filtro=tag_filtro,
                         busca_texto=busca_texto,
                         tipo_filtro=tipo_filtro,
                         data_inicio=data_inicio,
                         data_fim=data_fim,
                         pagina_atual=pagina_atual,
                         total_paginas=total_paginas,
                         total_registros=total_registros,
                         registros_por_pagina=registros_por_pagina)

@app.route('/comunicado/<int:comunicado_id>')
def obter_comunicado(comunicado_id):
    """Retorna dados de um comunicado para edição"""
    comunicado = Comunicado.query.get_or_404(comunicado_id)
    return jsonify({
        'id': comunicado.id,
        'codigo_unico': comunicado.codigo_unico,
        'titulo': comunicado.titulo,
        'subtitulo': comunicado.subtitulo,
        'corpo': comunicado.corpo,
        'rodape': comunicado.rodape,
        'publico_alvo': comunicado.publico_alvo,
        'template_id': comunicado.template_id,
        'status': comunicado.status,
        'tipo_pos_x': comunicado.tipo_pos_x,
        'tipo_pos_y': comunicado.tipo_pos_y,
        'subtitulo_pos_x': comunicado.subtitulo_pos_x,
        'subtitulo_pos_y': comunicado.subtitulo_pos_y,
        'corpo_pos_x': comunicado.corpo_pos_x,
        'corpo_pos_y': comunicado.corpo_pos_y,
        'corpo_alinhamento': comunicado.corpo_alinhamento,
        'rodape_pos_x': comunicado.rodape_pos_x,
        'rodape_pos_y': comunicado.rodape_pos_y,
        'publico_alvo_pos_x': comunicado.publico_alvo_pos_x,
        'publico_alvo_pos_y': comunicado.publico_alvo_pos_y,
        'criado_por': comunicado.criado_por,
        'criado_em': comunicado.criado_em.isoformat(),
        'tags': comunicado.tags or ''
    })

@app.route('/comunicado/<int:comunicado_id>', methods=['PUT'])
@rate_limit
def atualizar_comunicado(comunicado_id):
    """Atualiza um comunicado existente"""
    comunicado = Comunicado.query.get_or_404(comunicado_id)
    data = request.get_json()
    
    # Log audit trail
    logger.info(f"[ATUALIZAR] ID: {comunicado_id} | IP: {request.remote_addr} | Codigo: {comunicado.codigo_unico}")
    
    # Sanitize HTML content
    corpo_sanitized = sanitize_html(data.get('corpo', comunicado.corpo))
    rodape_sanitized = sanitize_html(data.get('rodape', comunicado.rodape))
    
    comunicado.titulo = data.get('titulo', comunicado.titulo)
    comunicado.subtitulo = data.get('subtitulo', comunicado.subtitulo)
    comunicado.corpo = corpo_sanitized
    comunicado.rodape = rodape_sanitized
    comunicado.publico_alvo = data.get('publico_alvo', comunicado.publico_alvo)
    comunicado.status = data.get('status', comunicado.status)
    # Tags não são atualizadas aqui - são gerenciadas apenas na página de histórico
    comunicado.atualizado_por = data.get('atualizado_por', 'Sistema')
    
    # Função auxiliar para converter valores numéricos de forma segura
    def safe_int(value, default):
        if value is None or value == '':
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    comunicado.tipo_pos_x = safe_int(data.get('tipo_pos_x'), comunicado.tipo_pos_x or 60)
    comunicado.tipo_pos_y = safe_int(data.get('tipo_pos_y'), comunicado.tipo_pos_y or 80)
    comunicado.tipo_tamanho = safe_int(data.get('tipo_tamanho'), comunicado.tipo_tamanho or 42)
    comunicado.subtitulo_pos_x = safe_int(data.get('subtitulo_pos_x'), comunicado.subtitulo_pos_x or 0)
    comunicado.subtitulo_pos_y = safe_int(data.get('subtitulo_pos_y'), comunicado.subtitulo_pos_y or 430)
    comunicado.subtitulo_tamanho = safe_int(data.get('subtitulo_tamanho'), comunicado.subtitulo_tamanho or 32)
    comunicado.corpo_pos_x = safe_int(data.get('corpo_pos_x'), comunicado.corpo_pos_x or 60)
    comunicado.corpo_pos_y = safe_int(data.get('corpo_pos_y'), comunicado.corpo_pos_y or 500)
    comunicado.corpo_tamanho = safe_int(data.get('corpo_tamanho'), comunicado.corpo_tamanho or 24)
    comunicado.corpo_alinhamento = data.get('corpo_alinhamento', comunicado.corpo_alinhamento or 'justify')
    comunicado.rodape_pos_x = safe_int(data.get('rodape_pos_x'), comunicado.rodape_pos_x or 60)
    comunicado.rodape_pos_y = safe_int(data.get('rodape_pos_y'), comunicado.rodape_pos_y or 1000)
    comunicado.rodape_tamanho = safe_int(data.get('rodape_tamanho'), comunicado.rodape_tamanho or 24)
    comunicado.publico_alvo_pos_x = safe_int(data.get('publico_alvo_pos_x'), comunicado.publico_alvo_pos_x or 60)
    comunicado.publico_alvo_pos_y = safe_int(data.get('publico_alvo_pos_y'), comunicado.publico_alvo_pos_y or 1120)
    comunicado.publico_alvo_tamanho = safe_int(data.get('publico_alvo_tamanho'), comunicado.publico_alvo_tamanho or 16)
    
    db.session.commit()
    
    return jsonify({'success': True, 'id': comunicado.id, 'codigo': comunicado.codigo_unico})

@app.route('/comunicado/<int:comunicado_id>/status', methods=['PUT'])
def atualizar_status(comunicado_id):
    """Atualiza apenas o status de um comunicado"""
    comunicado = Comunicado.query.get_or_404(comunicado_id)
    data = request.get_json()
    
    old_status = comunicado.status
    new_status = data.get('status', comunicado.status)
    
    logger.info(f"[STATUS] ID: {comunicado_id} | IP: {request.remote_addr} | {old_status} → {new_status}")
    
    comunicado.status = new_status
    comunicado.atualizado_por = data.get('atualizado_por', 'Sistema')
    
    db.session.commit()
    
    return jsonify({'success': True, 'status': comunicado.status})

@app.route('/comunicado/<int:comunicado_id>/tags', methods=['PUT'])
@rate_limit
def atualizar_tags(comunicado_id):
    """Atualiza apenas as tags de um comunicado"""
    comunicado = Comunicado.query.get_or_404(comunicado_id)
    data = request.get_json()
    
    tags_input = data.get('tags', '')
    tags_processed = processar_tags(tags_input)
    
    logger.info(f"[TAGS] ID: {comunicado_id} | IP: {request.remote_addr} | Tags: {tags_processed}")
    
    comunicado.tags = tags_processed
    comunicado.atualizado_por = data.get('atualizado_por', 'Sistema')
    
    db.session.commit()
    
    return jsonify({'success': True, 'tags': comunicado.tags})

@app.route('/comunicado/<int:comunicado_id>', methods=['DELETE'])
def deletar_comunicado(comunicado_id):
    """Deleta um comunicado"""
    comunicado = Comunicado.query.get_or_404(comunicado_id)
    codigo = comunicado.codigo_unico
    
    logger.warning(f"[DELETAR] ID: {comunicado_id} | IP: {request.remote_addr} | Codigo: {codigo}")
    
    db.session.delete(comunicado)
    db.session.commit()
    
    return jsonify({'success': True})


def migrar_banco_dados():
    """Adiciona colunas novas ao banco de dados existente"""
    with app.app_context():
        try:
            # Verificar se a coluna tags existe consultando o schema do SQLite
            result = db.session.execute(text("PRAGMA table_info(comunicado)"))
            columns = [row[1] for row in result]  # row[1] é o nome da coluna
            
            if 'tags' not in columns:
                logger.info("🔄 Adicionando coluna 'tags' à tabela 'comunicado'...")
                db.session.execute(text("ALTER TABLE comunicado ADD COLUMN tags TEXT DEFAULT ''"))
                db.session.commit()
                logger.info("✅ Coluna 'tags' adicionada com sucesso!")
            else:
                logger.info("✅ Coluna 'tags' já existe no banco de dados")
        except Exception as e:
            logger.error(f"❌ Erro ao migrar banco de dados: {e}")
            # Se der erro, tenta criar tudo do zero
            try:
                db.create_all()
            except Exception as ex:
                logger.error(f"❌ Erro ao criar tabelas: {ex}")

def corrigir_horarios_comunicados():
    """Corrige os horários dos comunicados existentes de UTC para horário de Brasília (UTC-3)
    Apenas corrige comunicados com horário suspeito (00:00-03:59), que provavelmente estão em UTC
    """
    try:
        with app.app_context():
            comunicados = Comunicado.query.all()
            if not comunicados:
                logger.info("ℹ️ Nenhum comunicado encontrado para corrigir")
                return
            
            logger.info(f"🔄 Verificando horários de {len(comunicados)} comunicado(s)...")
            corrigidos = 0
            
            for comunicado in comunicados:
                atualizado = False
                
                # Corrigir criado_em apenas se o horário for suspeito (00:00-03:59)
                # Isso indica que provavelmente está em UTC
                if comunicado.criado_em:
                    dt_original = comunicado.criado_em
                    hora = dt_original.hour
                    
                    # Se o horário está entre 00:00 e 03:59, provavelmente está em UTC
                    # e precisa ser convertido para UTC-3 (subtrair 3 horas)
                    if dt_original.tzinfo is None and (hora >= 0 and hora < 4):
                        # Adicionar timezone UTC
                        dt_utc = dt_original.replace(tzinfo=timezone.utc)
                        # Converter para horário de Brasília (UTC-3)
                        dt_brasil = dt_utc.astimezone(TZ_BRASIL)
                        # Remover timezone para salvar como naive
                        comunicado.criado_em = dt_brasil.replace(tzinfo=None)
                        logger.info(f"  Corrigido ID {comunicado.id}: {dt_original.strftime('%d/%m/%Y %H:%M')} → {comunicado.criado_em.strftime('%d/%m/%Y %H:%M')}")
                        atualizado = True
                
                # Corrigir atualizado_em apenas se o horário for suspeito
                if comunicado.atualizado_em:
                    dt_original = comunicado.atualizado_em
                    hora = dt_original.hour
                    if dt_original.tzinfo is None and (hora >= 0 and hora < 4):
                        dt_utc = dt_original.replace(tzinfo=timezone.utc)
                        dt_brasil = dt_utc.astimezone(TZ_BRASIL)
                        comunicado.atualizado_em = dt_brasil.replace(tzinfo=None)
                        atualizado = True
                
                if atualizado:
                    corrigidos += 1
            
            if corrigidos > 0:
                db.session.commit()
                logger.info(f"✅ {corrigidos} comunicado(s) corrigido(s) com sucesso!")
            else:
                logger.info("ℹ️ Nenhum comunicado precisou de correção (todos já estão no horário correto)")
                
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir horários: {e}")
        db.session.rollback()

def inicializar_dados():
    """Cria dados iniciais se não existirem"""
    with app.app_context():
        # Primeiro, fazer migração se necessário
        migrar_banco_dados()
        
        db.create_all()
        
        # Corrigir horários dos comunicados existentes
        corrigir_horarios_comunicados()
        
        # Configurações padrão
        configs_padrao = [
            ('fonte_titulo', 'Globo Corporativa', 'texto', 'Fonte do título'),
            ('tamanho_titulo', '42', 'numero', 'Tamanho da fonte do título (px)'),
            ('cor_titulo', '#FFFFFF', 'cor', 'Cor do título'),
            ('fonte_subtitulo', 'Globo Corporativa', 'texto', 'Fonte do subtítulo'),
            ('tamanho_subtitulo', '32', 'numero', 'Tamanho da fonte do subtítulo (px)'),
            ('cor_subtitulo', '#FFFFFF', 'cor', 'Cor do subtítulo'),
            ('fonte_corpo', 'Globo Corporativa', 'texto', 'Fonte do corpo'),
            ('tamanho_corpo', '18', 'numero', 'Tamanho da fonte do corpo (px)'),
            ('cor_corpo', '#333333', 'cor', 'Cor do corpo'),
            ('fonte_rodape', 'Globo Corporativa', 'texto', 'Fonte do rodapé'),
            ('tamanho_rodape', '12', 'numero', 'Tamanho da fonte do rodapé (px)'),
            ('cor_rodape', '#666666', 'cor', 'Cor do rodapé'),
        ]
        
        for chave, valor, tipo, descricao in configs_padrao:
            if not Configuracao.query.filter_by(chave=chave).first():
                config = Configuracao(chave=chave, valor=valor, tipo=tipo, descricao=descricao)
                db.session.add(config)
        
        # Criar template padrão
        if not Template.query.first():
            template_padrao = Template(nome='Template Padrão Globo', ativo=True)
            db.session.add(template_padrao)
        
        db.session.commit()
        logger.info("✅ Banco de dados inicializado")

if __name__ == '__main__':
    inicializar_dados()
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )
