/**
 * GCC Repórter - Criar Comunicado
 * JavaScript para a página de criação/edição de comunicados
 */

// ========== AUTO-SAVE FUNCTIONALITY ==========
let autoSaveTimeout;
let lastSavedData = '';
const AUTO_SAVE_DELAY = 10000;

function showSavingIndicator(message, type = 'saving') {
    const indicator = document.getElementById('savingIndicator');
    const text = document.getElementById('savingText');
    const spinner = indicator.querySelector('.spinner');

    indicator.className = 'saving-indicator show';
    text.textContent = message;

    if (type === 'success') {
        indicator.classList.add('success');
        spinner.style.display = 'none';
    } else if (type === 'error') {
        indicator.classList.add('error');
        spinner.style.display = 'none';
    } else {
        spinner.style.display = 'block';
    }

    if (type !== 'saving') {
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 3000);
    }
}

function startAutoSave() {
    clearTimeout(autoSaveTimeout);
    autoSaveTimeout = setTimeout(async () => {
        const currentData = JSON.stringify(coletarDadosFormulario());

        // Só salva se houver mudanças e se há um ID de comunicado (modo edição ou após primeiro save)
        if (currentData !== lastSavedData && document.getElementById('comunicado_id').value) {
            try {
                showSavingIndicator('Salvando automaticamente...', 'saving');
                await salvarRascunhoSilencioso();
                lastSavedData = currentData;
                showSavingIndicator('✓ Salvo', 'success');
            } catch (error) {
                showSavingIndicator('✗ Erro ao salvar', 'error');
            }
        }
    }, AUTO_SAVE_DELAY);
}

async function salvarRascunhoSilencioso() {
    const dados = coletarDadosFormulario();
    dados.status = 'rascunho';

    const comunicadoId = document.getElementById('comunicado_id').value;
    if (comunicadoId) {
        const response = await fetch(`/comunicado/${comunicadoId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });

        if (!response.ok) throw new Error('Erro ao salvar');
        return await response.json();
    }
}

// ========== TIPO PERSONALIZADO ==========
function toggleTipoCustom() {
    const checkbox = document.getElementById('tipoPersonalizado');
    const customGroup = document.getElementById('tipoCustomGroup');
    const posicionamentoCard = document.getElementById('posicionamentoTituloPersonalizadoCard');
    const tipoSelect = document.getElementById('tipo');
    const tipoCustom = document.getElementById('tipoCustom');
    const templateInput = document.getElementById('template');

    if (checkbox.checked) {
        customGroup.style.display = 'block';
        posicionamentoCard.style.display = 'block';
        tipoSelect.required = false;
        tipoSelect.disabled = true;
        tipoSelect.style.opacity = '0.5';
        tipoSelect.style.cursor = 'not-allowed';
        tipoCustom.required = true;
        tipoSelect.value = '';
        // Selecionar template Personalizado (ID 5)
        templateInput.value = '5';
        // Inicializar contador
        atualizarCharCounter('tipoCustom', 'tipoCustomCounter', 20);
        // Focar no campo personalizado
        setTimeout(() => tipoCustom.focus(), 100);
    } else {
        customGroup.style.display = 'none';
        posicionamentoCard.style.display = 'none';
        tipoSelect.required = true;
        tipoSelect.disabled = false;
        tipoSelect.style.opacity = '1';
        tipoSelect.style.cursor = 'pointer';
        tipoCustom.required = false;
        tipoCustom.value = '';
        atualizarCharCounter('tipoCustom', 'tipoCustomCounter', 20);
        // Atualizar estilo do select quando tipo personalizado é desmarcado
        atualizarEstiloTipoSelect();
        // Restaurar seleção de template baseado no tipo selecionado
        selecionarTemplatePorTipo();
    }
    atualizarPreview();
    atualizarInfoFormulario();
    startAutoSave();
}

// Função para resetar valores do título personalizado
function resetTituloPersonalizado(event) {
    // Prevenir propagação e submit do formulário
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    document.getElementById('tipoCustom_pos_x').value = '30';
    document.getElementById('tipoCustom_pos_y').value = '150';
    document.getElementById('tipoCustom_tamanho').value = '56';
    atualizarPreview();
    startAutoSave();
    return false;
}

// ========== CONTADORES E ESTATÍSTICAS ==========
function atualizarCharCounter(inputId, counterId, maxLength) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);
    if (input && counter) {
        const length = input.value.length;
        counter.textContent = `${length}/${maxLength}`;
        if (length >= maxLength) {
            counter.style.color = '#ef4444';
            counter.style.fontWeight = '600';
        } else if (length >= maxLength * 0.8) {
            counter.style.color = '#f59e0b';
            counter.style.fontWeight = '600';
        } else {
            counter.style.color = '#64748b';
            counter.style.fontWeight = '500';
        }
    }
}

function atualizarEstatisticasCorpo() {
    const corpoEl = document.getElementById('corpo');
    if (!corpoEl) return;

    // Obter texto sem HTML
    const texto = corpoEl.innerText || corpoEl.textContent || '';
    const textoLimpo = texto.trim();

    // Contar caracteres (sem espaços)
    const caracteres = textoLimpo.replace(/\s/g, '').length;
    const caracteresComEspacos = textoLimpo.length;

    // Contar palavras
    const palavras = textoLimpo ? textoLimpo.split(/\s+/).filter(p => p.length > 0).length : 0;

    // Calcular tempo de leitura (média de 200 palavras por minuto)
    const tempoLeitura = palavras > 0 ? Math.ceil(palavras / 200) : 0;

    // Atualizar contadores
    const charCounter = document.getElementById('corpoCharCounter');
    const wordCounter = document.getElementById('corpoWordCounter');
    const readTime = document.getElementById('corpoReadTime');

    if (charCounter) {
        charCounter.textContent = `${caracteresComEspacos.toLocaleString('pt-BR')} caracteres`;
    }
    if (wordCounter) {
        wordCounter.textContent = `${palavras.toLocaleString('pt-BR')} palavras`;
    }
    if (readTime) {
        if (tempoLeitura > 0) {
            readTime.textContent = `~${tempoLeitura} min leitura`;
            readTime.style.display = 'inline';
        } else {
            readTime.style.display = 'none';
        }
    }
}

// ========== PREVIEW ==========
function getTituloValue() {
    const checkbox = document.getElementById('tipoPersonalizado');
    if (checkbox.checked) {
        return document.getElementById('tipoCustom').value;
    } else {
        return document.getElementById('tipo').value;
    }
}

let previewTimeout;
function atualizarPreview() {
    clearTimeout(previewTimeout);
    previewTimeout = setTimeout(async () => {
        const tipoPersonalizadoCheckbox = document.getElementById('tipoPersonalizado');
        const usarTituloPersonalizado = tipoPersonalizadoCheckbox && tipoPersonalizadoCheckbox.checked;

        const dados = {
            template_id: document.getElementById('template').value,
            titulo: getTituloValue(),
            subtitulo: document.getElementById('subtitulo').value,
            corpo: document.getElementById('corpo').innerHTML,
            rodape: document.getElementById('rodape').value,
            publico_alvo: document.getElementById('publico_alvo').value,
            tipo_pos_x: usarTituloPersonalizado ? document.getElementById('tipoCustom_pos_x').value : document.getElementById('tipo_pos_x').value,
            tipo_pos_y: usarTituloPersonalizado ? document.getElementById('tipoCustom_pos_y').value : document.getElementById('tipo_pos_y').value,
            tipo_tamanho: usarTituloPersonalizado ? document.getElementById('tipoCustom_tamanho').value : document.getElementById('tipo_tamanho').value,
            subtitulo_pos_x: document.getElementById('subtitulo_pos_x').value,
            subtitulo_pos_y: document.getElementById('subtitulo_pos_y').value,
            subtitulo_tamanho: document.getElementById('subtitulo_tamanho').value,
            corpo_pos_x: document.getElementById('corpo_pos_x').value,
            corpo_pos_y: document.getElementById('corpo_pos_y').value,
            corpo_tamanho: document.getElementById('corpo_tamanho').value,
            corpo_alinhamento: document.getElementById('corpo_alinhamento').value,
            rodape_pos_x: document.getElementById('rodape_pos_x').value,
            rodape_pos_y: document.getElementById('rodape_pos_y').value,
            rodape_tamanho: document.getElementById('rodape_tamanho').value,
            publico_alvo_pos_x: document.getElementById('publico_alvo_pos_x').value,
            publico_alvo_pos_y: document.getElementById('publico_alvo_pos_y').value,
            publico_alvo_tamanho: document.getElementById('publico_alvo_tamanho').value
        };
        try {
            const response = await fetch('/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
            const data = await response.json();
            document.getElementById('previewContent').innerHTML = data.html;
            document.getElementById('previewError').style.display = 'none';

            // Ajustar quebra de linha do rodapé e subtítulo na prévia
            ajustarRodapePreview();
            ajustarSubtituloPreview();

            // Atualizar informações dos headers
            atualizarInfoPreview();
            atualizarInfoFormulario();

            // Aplicar zoom atual e centralizar após atualizar preview
            setTimeout(() => {
                document.getElementById('previewWrapper').style.transform = `scale(${currentZoom})`;
                centralizarPreview();
            }, 100);
        } catch (error) {
            console.error('Erro ao atualizar prévia:', error);
            document.getElementById('previewError').textContent = 'Erro ao gerar prévia. Tente novamente.';
            document.getElementById('previewError').style.display = 'block';

            // Atualizar status para erro
            const statusStat = document.getElementById('previewStatusStat');
            if (statusStat) {
                statusStat.innerHTML = '<span class="preview-stat-icon">⚠</span><span>Erro</span>';
                statusStat.style.color = '#ef4444';
            }
        }
    }, 800);
    startAutoSave();
}

// ========== EVENT LISTENERS ==========
function addInputListener(id) {
    const el = document.getElementById(id);
    el.addEventListener('input', () => {
        atualizarPreview();
        atualizarInfoFormulario();
        startAutoSave();
    });
    el.addEventListener('blur', () => {
        atualizarPreview();
        atualizarInfoFormulario();
        startAutoSave();
    });
}

function addChangeListener(id) {
    document.getElementById(id).addEventListener('change', () => {
        atualizarPreview();
        startAutoSave();
    });
}

// ========== FORMATAÇÃO DE TEXTO ==========
function formatText(command) {
    document.execCommand(command, false, null);
    document.getElementById('corpo').focus();
    atualizarPreview();
    startAutoSave();
}

function toggleSubtituloCase() {
    const subtituloInput = document.getElementById('subtitulo');
    const caseBtn = document.getElementById('subtituloCaseBtn');
    if (!subtituloInput || !caseBtn) return;

    const textoAtual = subtituloInput.value;
    if (!textoAtual.trim()) return;

    const estadoAtual = caseBtn.getAttribute('data-state') || 'normal';
    let novoEstado;
    let novoTexto;

    // Ciclar entre os três estados: uppercase -> lowercase -> capitalize -> uppercase...
    if (estadoAtual === 'normal') {
        novoEstado = 'uppercase';
        novoTexto = textoAtual.toUpperCase();
    } else if (estadoAtual === 'uppercase') {
        novoEstado = 'lowercase';
        novoTexto = textoAtual.toLowerCase();
    } else if (estadoAtual === 'lowercase') {
        novoEstado = 'capitalize';
        novoTexto = textoAtual.toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
    } else if (estadoAtual === 'capitalize') {
        novoEstado = 'uppercase';
        novoTexto = textoAtual.toUpperCase();
    }

    subtituloInput.value = novoTexto;
    caseBtn.setAttribute('data-state', novoEstado);
    atualizarPreview();
    startAutoSave();
}

function setAlign(align) {
    const corpo = document.getElementById('corpo');
    corpo.style.textAlign = align;
    document.getElementById('corpo_alinhamento').value = align;

    // Atualizar botões ativos
    document.querySelectorAll('.align-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`.align-btn[data-align="${align}"]`).classList.add('active');

    atualizarPreview();
    atualizarInfoFormulario();
    startAutoSave();
}

function limparFormulario() {
    document.getElementById('comunicadoForm').reset();
    document.getElementById('corpo').innerHTML = '';
    document.getElementById('rodape').value = 'Em caso de dúvidas consulte o Service Desk no telefone 3003-7000.';
    document.getElementById('modo_edicao').value = 'false';
    document.getElementById('comunicado_id').value = '';
    document.getElementById('pageTitle').textContent = 'Dados do Comunicado';
    document.getElementById('formPanelSubtitle').textContent = 'Preencha os campos abaixo';
    atualizarPreview();
    atualizarInfoFormulario();
}

// ========== AJUSTES DE PREVIEW ==========
function ajustarRodapePreview() {
    const rodapeEl = document.querySelector('#rodape-preview');
    if (!rodapeEl) return;

    rodapeEl.style.width = '980px';
    rodapeEl.style.maxWidth = '980px';
    rodapeEl.style.boxSizing = 'border-box';
    rodapeEl.style.wordWrap = 'break-word';
    rodapeEl.style.wordBreak = 'break-word';
    rodapeEl.style.overflowWrap = 'break-word';

    const texto = rodapeEl.textContent || rodapeEl.innerText;
    if (!texto.trim()) return;

    const temp = document.createElement('span');
    temp.style.position = 'absolute';
    temp.style.visibility = 'hidden';
    temp.style.whiteSpace = 'nowrap';
    temp.style.fontSize = rodapeEl.style.fontSize || '24px';
    temp.style.fontFamily = "'Globo Corporativa', 'GlobotipoCorporativa-Regular', sans-serif";
    temp.style.fontWeight = 'normal';
    temp.textContent = texto;
    document.body.appendChild(temp);

    const larguraTexto = temp.offsetWidth;
    const larguraDisponivel = 980;

    document.body.removeChild(temp);

    if (larguraTexto <= larguraDisponivel) {
        rodapeEl.style.whiteSpace = 'nowrap';
    } else {
        rodapeEl.style.whiteSpace = 'normal';
        rodapeEl.style.width = '980px';
    }
}

function ajustarSubtituloPreview() {
    const subtituloEl = document.querySelector('#subtitulo-preview');
    if (!subtituloEl) return;

    subtituloEl.style.width = '880px';
    subtituloEl.style.maxWidth = '880px';
    subtituloEl.style.boxSizing = 'border-box';
    subtituloEl.style.wordWrap = 'break-word';
    subtituloEl.style.wordBreak = 'break-word';
    subtituloEl.style.overflowWrap = 'break-word';

    const texto = subtituloEl.textContent || subtituloEl.innerText;
    if (!texto.trim()) return;

    const temp = document.createElement('span');
    temp.style.position = 'absolute';
    temp.style.visibility = 'hidden';
    temp.style.whiteSpace = 'nowrap';
    temp.style.fontSize = subtituloEl.style.fontSize || '32px';
    temp.style.fontFamily = "'Globo Corporativa', 'GlobotipoCorporativa-Bold', sans-serif";
    temp.style.fontWeight = '700';
    temp.style.textTransform = 'uppercase';
    temp.textContent = texto;
    document.body.appendChild(temp);

    const larguraTexto = temp.offsetWidth;
    const larguraDisponivel = 880;

    document.body.removeChild(temp);

    if (larguraTexto <= larguraDisponivel) {
        subtituloEl.style.whiteSpace = 'nowrap';
    } else {
        subtituloEl.style.whiteSpace = 'normal';
        subtituloEl.style.width = '880px';
    }
}

// ========== ZOOM ==========
let currentZoom = 0.58;

function ajustarZoom(delta) {
    currentZoom = Math.max(0.4, Math.min(1, currentZoom + delta));
    const wrapper = document.getElementById('previewWrapper');

    if (currentZoom >= 1) {
        wrapper.style.transformOrigin = 'top left';
    } else {
        wrapper.style.transformOrigin = 'center center';
    }

    wrapper.style.transform = `scale(${currentZoom})`;
    const zoomPercent = Math.round(currentZoom * 100);
    document.getElementById('zoomLevel').textContent = zoomPercent + '%';

    centralizarPreview();
}

function ajustarZoomParaCaber() {
    const container = document.querySelector('.preview-container');
    const wrapper = document.getElementById('previewWrapper');

    if (!container || !wrapper) return;

    const arteWidth = 1000;
    const arteHeight = 1300;

    const containerWidth = container.clientWidth - 56;
    const containerHeight = container.clientHeight - 56;

    const zoomX = containerWidth / arteWidth;
    const zoomY = containerHeight / arteHeight;

    const zoomIdeal = Math.min(zoomX, zoomY, 1);

    currentZoom = Math.max(0.4, Math.min(1, zoomIdeal));

    if (currentZoom >= 1) {
        wrapper.style.transformOrigin = 'top left';
    } else {
        wrapper.style.transformOrigin = 'center center';
    }

    wrapper.style.transform = `scale(${currentZoom})`;

    const zoomPercent = Math.round(currentZoom * 100);
    document.getElementById('zoomLevel').textContent = zoomPercent + '%';

    centralizarPreview();
}

// ========== INFORMAÇÕES DOS HEADERS ==========
function atualizarInfoFormulario() {
    const modoEdicao = document.getElementById('modo_edicao').value === 'true';
    const comunicadoId = document.getElementById('comunicado_id').value;

    const statusStat = document.getElementById('formStatusStat');
    const statusText = document.getElementById('formStatusText');
    if (statusStat && statusText) {
        if (modoEdicao && comunicadoId) {
            statusText.textContent = 'Editando';
            statusStat.style.color = '#6366f1';
        } else if (comunicadoId) {
            statusText.textContent = 'Salvo';
            statusStat.style.color = '#10b981';
        } else {
            statusText.textContent = 'Novo';
            statusStat.style.color = '#64748b';
        }
    }

    // Calcular progresso
    const campos = {
        tipo: getTituloValue(),
        subtitulo: document.getElementById('subtitulo').value,
        corpo: document.getElementById('corpo').innerText || document.getElementById('corpo').textContent || '',
        rodape: document.getElementById('rodape').value,
        publico_alvo: document.getElementById('publico_alvo').value
    };

    const camposPreenchidos = Object.values(campos).filter(v => v && v.trim().length > 0).length;
    const totalCampos = Object.keys(campos).length;
    const progresso = Math.round((camposPreenchidos / totalCampos) * 100);

    const progressStat = document.getElementById('formProgressStat');
    const progressText = document.getElementById('formProgressText');
    if (progressStat && progressText) {
        progressText.textContent = `${progresso}%`;
        if (progresso === 100) {
            progressStat.style.color = '#10b981';
        } else if (progresso >= 50) {
            progressStat.style.color = '#f59e0b';
        } else {
            progressStat.style.color = '#64748b';
        }
    }
}

function atualizarInfoPreview() {
    const titulo = getTituloValue();
    const subtitulo = document.getElementById('subtitulo').value;
    const corpoEl = document.getElementById('corpo');
    const corpoTexto = corpoEl ? (corpoEl.innerText || corpoEl.textContent || '').trim() : '';
    const rodape = document.getElementById('rodape').value;
    const publicoAlvo = document.getElementById('publico_alvo').value;

    const temConteudo = titulo || subtitulo || corpoTexto || rodape || publicoAlvo;

    const statusStat = document.getElementById('previewStatusStat');
    if (statusStat) {
        if (temConteudo) {
            statusStat.innerHTML = '<span class="preview-stat-icon">✓</span><span>Atualizado</span>';
            statusStat.style.color = '#10b981';
        } else {
            statusStat.innerHTML = '<span class="preview-stat-icon">○</span><span>Vazio</span>';
            statusStat.style.color = '#94a3b8';
        }
    }

    const contentStat = document.getElementById('previewContentStat');
    const contentInfo = document.getElementById('previewContentInfo');
    if (contentStat && contentInfo) {
        if (corpoTexto) {
            const palavras = corpoTexto.split(/\s+/).filter(p => p.length > 0).length;
            contentInfo.textContent = `${palavras} palavra${palavras !== 1 ? 's' : ''}`;
        } else if (titulo && subtitulo) {
            contentInfo.textContent = 'Completo';
        } else if (titulo || subtitulo) {
            contentInfo.textContent = 'Parcial';
        } else {
            contentInfo.textContent = 'Vazio';
        }
    }
}

function centralizarPreview() {
    const container = document.querySelector('.preview-container');
    const wrapper = document.getElementById('previewWrapper');

    if (!container || !wrapper) return;

    setTimeout(() => {
        const arteWidth = 1000 * currentZoom;
        const arteHeight = 1300 * currentZoom;

        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;

        if (arteWidth < containerWidth && arteHeight < containerHeight) {
            const scrollLeft = (arteWidth - containerWidth) / 2;
            const scrollTop = (arteHeight - containerHeight) / 2;

            container.scrollTo({
                left: Math.max(0, scrollLeft),
                top: Math.max(0, scrollTop),
                behavior: 'smooth'
            });
        } else {
            container.scrollTo({
                left: 0,
                top: 0,
                behavior: 'smooth'
            });
        }
    }, 100);
}

// ========== ACCORDION ==========
function toggleAccordion(element) {
    const content = element.nextElementSibling;
    const icon = element.querySelector('.accordion-icon');

    if (content.classList.contains('open')) {
        content.classList.remove('open');
        icon.classList.remove('open');
        element.setAttribute('aria-expanded', 'false');
    } else {
        content.classList.add('open');
        icon.classList.add('open');
        element.setAttribute('aria-expanded', 'true');
    }
}

// ========== CONTROLES DE POSIÇÃO ==========
function adjustValue(event, inputId, delta) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const input = document.getElementById(inputId);
    if (!input) return false;

    const currentValue = parseInt(input.value) || 0;
    const min = parseInt(input.min) || 0;
    const max = parseInt(input.max) || 1000;
    const step = parseInt(input.step) || 1;

    let newValue = currentValue + (delta * step);
    newValue = Math.max(min, Math.min(max, newValue));

    input.value = newValue;
    atualizarPreview();
    startAutoSave();
    return false;
}

function resetElement(event, elementType, posX, posY, tamanho) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    if (elementType === 'tipo') {
        const tipoSelect = document.getElementById('tipo');
        const tipoPersonalizadoCheckbox = document.getElementById('tipoPersonalizado');

        if (tipoSelect && !tipoPersonalizadoCheckbox.checked &&
            (tipoSelect.value === 'Indisponibilidade' || tipoSelect.value === 'Instabilidade' || tipoSelect.value === 'Degradação' || tipoSelect.value === 'Normalização')) {
            posX = 60;
            posY = 120;
            tamanho = 60;
        }
    }

    document.getElementById(`${elementType}_pos_x`).value = posX;
    document.getElementById(`${elementType}_pos_y`).value = posY;
    document.getElementById(`${elementType}_tamanho`).value = tamanho;
    atualizarPreview();
    startAutoSave();
    return false;
}

function aplicarPreset(event, presetType) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    switch (presetType) {
        case 'centralizar':
            document.getElementById('tipo_pos_x').value = 60;
            document.getElementById('subtitulo_pos_x').value = 0;
            document.getElementById('corpo_pos_x').value = 60;
            document.getElementById('rodape_pos_x').value = 0;
            document.getElementById('publico_alvo_pos_x').value = 60;
            break;

        case 'resetar':
            resetElement(null, 'tipo', 60, 80, 42);
            resetElement(null, 'subtitulo', 0, 430, 32);
            resetElement(null, 'corpo', 60, 510, 24);
            resetElement(null, 'rodape', 60, 1000, 24);
            resetElement(null, 'publico_alvo', 60, 1120, 16);
            break;

        case 'compacto':
            document.getElementById('corpo_pos_y').value = 550;
            document.getElementById('rodape_pos_y').value = 900;
            document.getElementById('publico_alvo_pos_y').value = 1120;
            break;

        case 'espacado':
            document.getElementById('corpo_pos_y').value = 480;
            document.getElementById('rodape_pos_y').value = 1000;
            document.getElementById('publico_alvo_pos_y').value = 1170;
            break;
    }
    atualizarPreview();
    startAutoSave();
    return false;
}

// ========== DADOS DE TESTE ==========
function preencherDadosTeste(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const tipoPersonalizadoCheckbox = document.getElementById('tipoPersonalizado');
    if (tipoPersonalizadoCheckbox && tipoPersonalizadoCheckbox.checked) {
        tipoPersonalizadoCheckbox.checked = false;
        toggleTipoCustom();
    }

    const tipoSelect = document.getElementById('tipo');
    if (tipoSelect) {
        tipoSelect.value = 'Indisponibilidade';
        tipoSelect.disabled = false;
    }

    const subtituloInput = document.getElementById('subtitulo');
    if (subtituloInput) {
        subtituloInput.value = 'INDISPONIBILIDADE DO SCOUT';
    }

    const corpoDiv = document.getElementById('corpo');
    if (corpoDiv) {
        corpoDiv.innerHTML = 'Informamos que estamos com um impacto global na AWS, impactando os serviços do Scout.<br><br>Os times estão acompanhando, e assim que normalizar informaremos.';
    }

    const publicoAlvoSelect = document.getElementById('publico_alvo');
    if (publicoAlvoSelect) {
        publicoAlvoSelect.value = 'Enviado para um público específico.';
    }

    atualizarPreview();
    startAutoSave();

    const buttons = document.querySelectorAll('.preset-btn');
    buttons.forEach(btn => {
        if (btn.textContent.includes('Dados de Teste')) {
            const originalBg = btn.style.background || '#fef3c7';
            const originalColor = btn.style.color || '#92400e';
            btn.style.background = '#10b981';
            btn.style.color = '#fff';
            setTimeout(() => {
                btn.style.background = originalBg;
                btn.style.color = originalColor;
            }, 1000);
        }
    });
    return false;
}

// ========== ESTILO DO SELECT DE TIPO ==========
function atualizarEstiloTipoSelect() {
    const tipoSelect = document.getElementById('tipo');
    const tipoIcon = document.getElementById('tipoIcon');

    if (!tipoSelect || !tipoIcon) return;

    tipoSelect.classList.remove('alert-indisponibilidade', 'alert-instabilidade', 'alert-degradacao', 'success-normalizacao');
    tipoIcon.textContent = '';

    const tipoSelecionado = tipoSelect.value;

    if (tipoSelecionado === 'Indisponibilidade') {
        tipoSelect.classList.add('alert-indisponibilidade');
        tipoIcon.textContent = '🚨';
    } else if (tipoSelecionado === 'Instabilidade') {
        tipoSelect.classList.add('alert-instabilidade');
        tipoIcon.textContent = '⚠️';
    } else if (tipoSelecionado === 'Degradação') {
        tipoSelect.classList.add('alert-degradacao');
        tipoIcon.textContent = '⚡';
    } else if (tipoSelecionado === 'Normalização') {
        tipoSelect.classList.add('success-normalizacao');
        tipoIcon.textContent = '✅';
    }
}

// ========== SELEÇÃO DE TEMPLATE ==========
function selecionarTemplatePorTipo() {
    const tipoSelect = document.getElementById('tipo');
    const templateInput = document.getElementById('template');
    const tipoPersonalizadoCheckbox = document.getElementById('tipoPersonalizado');

    if (!tipoSelect || !templateInput) return;

    if (tipoPersonalizadoCheckbox && tipoPersonalizadoCheckbox.checked) {
        atualizarEstiloTipoSelect();
        return;
    }

    const tipoSelecionado = tipoSelect.value;

    atualizarEstiloTipoSelect();

    if (tipoSelecionado === 'Instabilidade') {
        templateInput.value = '2';
        document.getElementById('tipo_pos_x').value = '60';
        document.getElementById('tipo_pos_y').value = '120';
        document.getElementById('tipo_tamanho').value = '60';
    } else if (tipoSelecionado === 'Degradação') {
        templateInput.value = '3';
        document.getElementById('tipo_pos_x').value = '60';
        document.getElementById('tipo_pos_y').value = '120';
        document.getElementById('tipo_tamanho').value = '60';
    } else if (tipoSelecionado === 'Normalização') {
        templateInput.value = '4';
        document.getElementById('tipo_pos_x').value = '60';
        document.getElementById('tipo_pos_y').value = '120';
        document.getElementById('tipo_tamanho').value = '60';
    } else if (tipoSelecionado === 'Indisponibilidade' || tipoSelecionado === '') {
        templateInput.value = '1';
        document.getElementById('tipo_pos_x').value = '60';
        document.getElementById('tipo_pos_y').value = '120';
        document.getElementById('tipo_tamanho').value = '60';
    }

    atualizarPreview();
}

// ========== INICIALIZAÇÃO ==========
window.addEventListener('DOMContentLoaded', () => {
    atualizarPreview();
    atualizarInfoPreview();
    atualizarInfoFormulario();

    const tipoCustomEl = document.getElementById('tipoCustom');
    if (tipoCustomEl && tipoCustomEl.value) {
        atualizarCharCounter('tipoCustom', 'tipoCustomCounter', 20);
    }

    atualizarEstatisticasCorpo();

    const subtituloInput = document.getElementById('subtitulo');
    if (subtituloInput) {
        subtituloInput.addEventListener('input', () => {
            const caseBtn = document.getElementById('subtituloCaseBtn');
            if (caseBtn) {
                caseBtn.setAttribute('data-state', 'normal');
            }
        });
    }

    const tipoSelect = document.getElementById('tipo');
    if (tipoSelect) {
        tipoSelect.addEventListener('change', selecionarTemplatePorTipo);
        atualizarEstiloTipoSelect();
    }

    // Verificar se há ID na URL para modo de edição
    const urlParams = new URLSearchParams(window.location.search);
    const comunicadoId = urlParams.get('editar');
    if (comunicadoId) {
        carregarComunicado(comunicadoId);
    }

    // Adicionar evento para limpar formatação ao colar
    const corpoElement = document.getElementById('corpo');
    corpoElement.addEventListener('paste', function (e) {
        e.preventDefault();
        const text = (e.originalEvent || e).clipboardData.getData('text/plain');
        document.execCommand('insertText', false, text);
        setTimeout(() => atualizarEstatisticasCorpo(), 10);
        atualizarPreview();
    });

    // Configurar event listeners
    addChangeListener('template');
    addChangeListener('tipo');

    if (tipoCustomEl) {
        tipoCustomEl.addEventListener('input', () => {
            atualizarCharCounter('tipoCustom', 'tipoCustomCounter', 20);
            atualizarPreview();
            startAutoSave();
        });
        tipoCustomEl.addEventListener('blur', () => {
            atualizarPreview();
            startAutoSave();
        });
    }

    addInputListener('subtitulo');

    const corpoEl = document.getElementById('corpo');
    if (corpoEl) {
        corpoEl.addEventListener('input', () => {
            atualizarEstatisticasCorpo();
            atualizarPreview();
            atualizarInfoFormulario();
            startAutoSave();
        });
        corpoEl.addEventListener('blur', () => {
            atualizarPreview();
            atualizarInfoFormulario();
            startAutoSave();
        });
    }

    addInputListener('rodape');
    addInputListener('publico_alvo');

    // Event listeners para controles de posição
    addInputListener('tipo_pos_x');
    addInputListener('tipo_pos_y');
    addInputListener('tipo_tamanho');
    addInputListener('tipoCustom_pos_x');
    addInputListener('tipoCustom_pos_y');
    addInputListener('tipoCustom_tamanho');
    addInputListener('subtitulo_pos_x');
    addInputListener('subtitulo_pos_y');
    addInputListener('subtitulo_tamanho');
    addInputListener('corpo_pos_x');
    addInputListener('corpo_pos_y');
    addInputListener('corpo_tamanho');
    addInputListener('rodape_pos_x');
    addInputListener('rodape_pos_y');
    addInputListener('rodape_tamanho');
    addInputListener('publico_alvo_pos_x');
    addInputListener('publico_alvo_pos_y');
    addInputListener('publico_alvo_tamanho');
});

// ========== CARREGAR COMUNICADO ==========
async function carregarComunicado(id) {
    try {
        const response = await fetch(`/comunicado/${id}`);
        const com = await response.json();

        document.getElementById('comunicado_id').value = com.id;
        document.getElementById('modo_edicao').value = 'true';
        document.getElementById('pageTitle').textContent = `Editando ${com.codigo_unico}`;
        document.getElementById('formPanelSubtitle').textContent = `Comunicado ${com.codigo_unico}`;
        atualizarInfoFormulario();

        if (com.template_id) {
            document.getElementById('template').value = com.template_id;
        }

        if (com.titulo.includes('Indisponibilidade') || com.titulo.includes('Instabilidade') || com.titulo.includes('Degradação') || com.titulo.includes('Normalização')) {
            document.getElementById('tipo').value = com.titulo;
            atualizarEstiloTipoSelect();
            if (!com.template_id) {
                selecionarTemplatePorTipo();
            }
        } else {
            document.getElementById('tipoPersonalizado').checked = true;
            toggleTipoCustom();
            document.getElementById('tipoCustom').value = com.titulo;
            atualizarCharCounter('tipoCustom', 'tipoCustomCounter', 20);
        }

        document.getElementById('subtitulo').value = com.subtitulo || '';
        document.getElementById('corpo').innerHTML = com.corpo || '';
        document.getElementById('rodape').value = com.rodape || 'Em caso de dúvidas consulte o Service Desk no telefone 3003-7000.';
        document.getElementById('publico_alvo').value = com.publico_alvo || '';

        setTimeout(() => atualizarEstatisticasCorpo(), 100);

        const tipoPersonalizadoCheckbox = document.getElementById('tipoPersonalizado');
        if (tipoPersonalizadoCheckbox && tipoPersonalizadoCheckbox.checked) {
            document.getElementById('tipoCustom_pos_x').value = com.tipo_pos_x;
            document.getElementById('tipoCustom_pos_y').value = com.tipo_pos_y;
            document.getElementById('tipoCustom_tamanho').value = com.tipo_tamanho;
        } else {
            document.getElementById('tipo_pos_x').value = com.tipo_pos_x;
            document.getElementById('tipo_pos_y').value = com.tipo_pos_y;
            document.getElementById('tipo_tamanho').value = com.tipo_tamanho;
        }
        document.getElementById('subtitulo_pos_x').value = com.subtitulo_pos_x;
        document.getElementById('subtitulo_pos_y').value = com.subtitulo_pos_y;
        document.getElementById('corpo_pos_x').value = com.corpo_pos_x;
        document.getElementById('corpo_pos_y').value = com.corpo_pos_y;
        const alinhamento = com.corpo_alinhamento || 'justify';
        document.getElementById('corpo_alinhamento').value = alinhamento;
        document.getElementById('corpo').style.textAlign = alinhamento;
        document.querySelectorAll('.align-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const btnAtivo = document.querySelector(`.align-btn[data-align="${alinhamento}"]`);
        if (btnAtivo) btnAtivo.classList.add('active');
        document.getElementById('rodape_pos_x').value = com.rodape_pos_x;
        document.getElementById('rodape_pos_y').value = com.rodape_pos_y;
        document.getElementById('publico_alvo_pos_x').value = com.publico_alvo_pos_x || 60;
        document.getElementById('publico_alvo_pos_y').value = com.publico_alvo_pos_y || 1120;

        atualizarPreview();
        lastSavedData = JSON.stringify(coletarDadosFormulario());
    } catch (error) {
        alert('Erro ao carregar comunicado: ' + error);
    }
}

// ========== SALVAR RASCUNHO ==========
async function salvarRascunho() {
    showSavingIndicator('Salvando rascunho...', 'saving');
    const dados = coletarDadosFormulario();
    dados.status = 'rascunho';

    try {
        const comunicadoId = document.getElementById('comunicado_id').value;
        let response;

        if (comunicadoId) {
            response = await fetch(`/comunicado/${comunicadoId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
        } else {
            response = await fetch('/criar-comunicado', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
        }

        const data = await response.json();
        if (data.success) {
            lastSavedData = JSON.stringify(dados);
            showSavingIndicator(`✓ Rascunho ${data.codigo} salvo!`, 'success');
            const successMsg = document.getElementById('successMessage');
            successMsg.textContent = `✅ Rascunho ${data.codigo} salvo com sucesso!`;
            successMsg.style.display = 'block';

            document.getElementById('comunicado_id').value = data.id;
            document.getElementById('modo_edicao').value = 'true';

            setTimeout(() => {
                successMsg.style.display = 'none';
                window.location.href = '/historico';
            }, 2000);
        }
    } catch (error) {
        showSavingIndicator('✗ Erro ao salvar rascunho', 'error');
        console.error('Erro ao salvar rascunho:', error);
    }
}

// ========== COLETAR DADOS ==========
function coletarDadosFormulario() {
    const tipoPersonalizadoCheckbox = document.getElementById('tipoPersonalizado');
    const usarTituloPersonalizado = tipoPersonalizadoCheckbox && tipoPersonalizadoCheckbox.checked;

    return {
        template_id: document.getElementById('template').value,
        titulo: getTituloValue(),
        subtitulo: document.getElementById('subtitulo').value,
        corpo: document.getElementById('corpo').innerHTML,
        rodape: document.getElementById('rodape').value,
        publico_alvo: document.getElementById('publico_alvo').value,
        tipo_pos_x: usarTituloPersonalizado ? document.getElementById('tipoCustom_pos_x').value : document.getElementById('tipo_pos_x').value,
        tipo_pos_y: usarTituloPersonalizado ? document.getElementById('tipoCustom_pos_y').value : document.getElementById('tipo_pos_y').value,
        tipo_tamanho: usarTituloPersonalizado ? document.getElementById('tipoCustom_tamanho').value : document.getElementById('tipo_tamanho').value,
        subtitulo_pos_x: document.getElementById('subtitulo_pos_x').value,
        subtitulo_pos_y: document.getElementById('subtitulo_pos_y').value,
        subtitulo_tamanho: document.getElementById('subtitulo_tamanho').value,
        corpo_pos_x: document.getElementById('corpo_pos_x').value,
        corpo_pos_y: document.getElementById('corpo_pos_y').value,
        corpo_tamanho: document.getElementById('corpo_tamanho').value,
        corpo_alinhamento: document.getElementById('corpo_alinhamento').value,
        rodape_pos_x: document.getElementById('rodape_pos_x').value,
        rodape_pos_y: document.getElementById('rodape_pos_y').value,
        rodape_tamanho: document.getElementById('rodape_tamanho').value,
        publico_alvo_pos_x: document.getElementById('publico_alvo_pos_x').value,
        publico_alvo_pos_y: document.getElementById('publico_alvo_pos_y').value,
        publico_alvo_tamanho: document.getElementById('publico_alvo_tamanho').value
    };
}

// ========== SUBMIT DO FORMULÁRIO ==========
document.getElementById('comunicadoForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const dados = coletarDadosFormulario();
    dados.status = 'enviado';

    try {
        const comunicadoId = document.getElementById('comunicado_id').value;
        let response;

        if (comunicadoId) {
            response = await fetch(`/comunicado/${comunicadoId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
            const data = await response.json();
            if (data.success) {
                window.location.href = '/gerar-imagem/' + data.id;
            }
        } else {
            response = await fetch('/criar-comunicado', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });
            const data = await response.json();
            if (data.success) {
                window.location.href = '/gerar-imagem/' + data.id;
            }
        }
    } catch (error) {
        alert('Erro ao salvar comunicado. Tente novamente.');
        console.error('Erro:', error);
    }
});

// ========== MODAL ACESSIBILIDADE ==========
function abrirModalAcessibilidade() {
    const subtituloEl = document.getElementById('subtitulo');
    const corpoEl = document.getElementById('corpo');
    const rodapeEl = document.getElementById('rodape');
    const publicoAlvoEl = document.getElementById('publico_alvo');

    const subtitulo = (subtituloEl && subtituloEl.value) ? subtituloEl.value.trim() : '';
    const corpo = (corpoEl && corpoEl.innerText) ? corpoEl.innerText.trim() : '';
    const rodape = (rodapeEl && rodapeEl.value) ? rodapeEl.value.trim() : '';
    const publico_alvo = (publicoAlvoEl && publicoAlvoEl.value) ? publicoAlvoEl.value.trim() : '';

    if (!subtitulo && !corpo && !rodape && !publico_alvo) {
        alert('Preencha pelo menos um campo antes de gerar o texto de acessibilidade.');
        return;
    }

    let textoHTML = '<div style="font-family: Verdana, sans-serif; font-size: 8pt; text-align: center; line-height: 1.6;">';
    textoHTML += '<p><strong>#ParaTodosVerem</strong></p>';

    if (subtitulo) textoHTML += `<p>${limparHTML(subtitulo)}</p>`;
    if (corpo) textoHTML += `<p>${limparHTML(corpo)}</p>`;
    if (rodape) textoHTML += `<p>${limparHTML(rodape)}</p>`;
    if (publico_alvo) textoHTML += `<p>${limparHTML(publico_alvo)}</p>`;

    textoHTML += '</div>';

    let textoPuro = '#ParaTodosVerem\n';
    if (subtitulo) textoPuro += limparHTML(subtitulo) + '\n';
    if (corpo) textoPuro += limparHTML(corpo) + '\n';
    if (rodape) textoPuro += limparHTML(rodape) + '\n';
    if (publico_alvo) textoPuro += limparHTML(publico_alvo);

    const previewElement = document.getElementById('acessibilidadePreview');
    const modalElement = document.getElementById('modalAcessibilidade');

    if (previewElement && modalElement) {
        previewElement.innerHTML = textoHTML;
        window.acessibilidadeHTMLCache = textoPuro;
        modalElement.classList.add('show');
    } else {
        console.error('Elementos do modal não encontrados!', {
            preview: !!previewElement,
            modal: !!modalElement
        });
    }
}

function fecharModalAcessibilidade() {
    document.getElementById('modalAcessibilidade').classList.remove('show');
}

function copiarTextoAcessibilidade(event) {
    const textoPuro = window.acessibilidadeHTMLCache;

    if (!textoPuro) {
        alert('Nenhum texto para copiar. Tente gerar novamente.');
        return;
    }

    const btn = event ? event.target : document.querySelector('button[onclick*="copiarTextoAcessibilidade"]');

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textoPuro).then(() => {
            atualizarBotaoCopiado(btn);
        }).catch(err => {
            console.error('Erro ao copiar:', err);
            fallbackCopyText(textoPuro, btn);
        });
    } else {
        fallbackCopyText(textoPuro, btn);
    }
}

function atualizarBotaoCopiado(btn) {
    if (!btn) return;
    const originalText = btn.textContent;
    btn.textContent = '✓ Copiado!';
    btn.style.background = '#10b981';

    setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
    }, 2000);
}

function fallbackCopyText(text, btn) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();

    try {
        document.execCommand('copy');
        atualizarBotaoCopiado(btn);
    } catch (err) {
        alert('Erro ao copiar. Selecione o texto manualmente:\n\n' + text);
    } finally {
        document.body.removeChild(textarea);
    }
}

function limparHTML(texto) {
    const div = document.createElement('div');
    div.innerHTML = texto;
    return div.textContent || div.innerText || '';
}
