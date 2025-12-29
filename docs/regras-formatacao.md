# 📋 Regras de Formatação dos Campos - Sistema de Comunicados

> **Documentação Oficial** - Última atualização: 28 de novembro de 2025

---

## 🎯 Visão Geral

Este documento define as regras de formatação aplicadas a cada campo do comunicado, tanto na **prévia em tempo real** quanto na **imagem PNG exportada**.

---

## 📝 Campos e Suas Formatações

### 1️⃣ **TIPO / TÍTULO** (campo `titulo`)

| Propriedade | Valor |
|------------|-------|
| **Fonte** | GlobotipoCorporativa-Bold.ttf |
| **Peso** | Bold (Negrito) |
| **Transformação** | MAIÚSCULAS (UPPERCASE) |
| **Cor** | #FFFFFF (Branco) |
| **Tamanho Padrão** | 42px (personalizável) |
| **Posição X Padrão** | 60px |
| **Posição Y Padrão** | 80px |
| **Alinhamento** | Esquerda |

**Exemplo:**
- Entrada: `Indisponibilidade`
- Saída na imagem: `INDISPONIBILIDADE` (branco, negrito)

---

### 2️⃣ **SUBTÍTULO** (campo `subtitulo`)

| Propriedade | Valor |
|------------|-------|
| **Fonte** | GlobotipoCorporativa-Bold.ttf |
| **Peso** | Bold (Negrito) |
| **Transformação** | MAIÚSCULAS (UPPERCASE) |
| **Cor** | #000000 (Preto) |
| **Tamanho Padrão** | 32px (personalizável) |
| **Posição X Padrão** | 0 (centralizado) |
| **Posição Y Padrão** | 430px |
| **Alinhamento** | Centro (se pos_x = 0) ou Esquerda (se pos_x > 0) |

**Exemplo:**
- Entrada: `Telefonia fixa - São Paulo`
- Saída na imagem: `TELEFONIA FIXA - SÃO PAULO` (preto, negrito, centralizado)

---

### 3️⃣ **CORPO / DESCRIÇÃO** (campo `corpo`)

| Propriedade | Valor |
|------------|-------|
| **Fonte Base** | GlobotipoCorporativa-Regular.ttf |
| **Peso** | Regular (permite **negrito** e _itálico_ via marcações) |
| **Transformação** | Nenhuma (mantém original) |
| **Cor** | #000000 (Preto) |
| **Tamanho Padrão** | 24px (personalizável) |
| **Posição X Padrão** | 60px |
| **Posição Y Padrão** | 500px |
| **Alinhamento Padrão** | Justificado (personalizável: left, center, right, justify) |
| **Fundo** | Caixa branca semi-transparente (255, 255, 255, 230) |
| **Largura da Caixa** | 880px |

**Formatações Especiais:**
- `**texto**` → **Negrito** (GlobotipoCorporativa-Bold.ttf)
- `_texto_` → _Itálico_ (GlobotipoCorporativa-Regular.ttf simulado)
- Suporta quebra de linha automática
- Limite de 8 linhas

**Exemplo:**
- Entrada: `Informamos que **recebimentos de ligações** externas estão _normalizados_.`
- Saída: Texto com "recebimentos de ligações" em negrito e "normalizados" em itálico

---

### 4️⃣ **RODAPÉ** (campo `rodape`)

| Propriedade | Valor |
|------------|-------|
| **Fonte** | GlobotipoCorporativa-Regular.ttf |
| **Peso** | Regular |
| **Transformação** | Nenhuma (mantém original) |
| **Cor** | #000000 (Preto) |
| **Tamanho Padrão** | 24px (personalizável) |
| **Posição X Padrão** | Centralizado |
| **Posição Y Padrão** | 1000px |
| **Alinhamento** | Centro (sempre) |
| **Largura Máxima** | 880px |

**Exemplo:**
- Entrada: `Em caso de dúvidas consulte o Service Desk no telefone 3003-7000`
- Saída: Texto centralizado, preto, fonte regular

---

### 5️⃣ **PÚBLICO ALVO** (campo `publico_alvo`)

| Propriedade | Valor |
|------------|-------|
| **Fonte** | GlobotipoCorporativa-Regular.ttf |
| **Peso** | Regular |
| **Estilo** | Itálico (italic) |
| **Transformação** | Nenhuma (mantém original) |
| **Cor** | #000000 (Preto) |
| **Tamanho Padrão** | 16px (personalizável) |
| **Posição X Padrão** | 60px |
| **Posição Y Padrão** | 1120px |
| **Alinhamento** | Esquerda |
| **Largura Máxima** | 880px |

**Exemplo:**
- Entrada: `São Paulo`
- Saída: _São Paulo_ (preto, itálico, pequeno)

---

## 🎨 Resumo Visual das Cores

```
┌─────────────────────────────────────────────┐
│  TIPO/TÍTULO: #FFFFFF (Branco)              │ ← Negrito + Maiúsculas
├─────────────────────────────────────────────┤
│  SUBTÍTULO: #000000 (Preto)                 │ ← Negrito + Maiúsculas + Centro
├─────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐   │
│  │ CORPO: #000000 (Preto)               │   │ ← Regular + Caixa Branca
│  │ Com suporte a **negrito** e _itálico_│   │
│  └──────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│  RODAPÉ: #000000 (Preto) - Centralizado    │ ← Regular
├─────────────────────────────────────────────┤
│  Público: #000000 (Preto) - Itálico        │ ← Itálico + Pequeno
└─────────────────────────────────────────────┘
```

---

## ⚙️ Personalizações Permitidas

Cada campo permite ajuste de:

1. **Posição X** (horizontal, em pixels)
2. **Posição Y** (vertical, em pixels)
3. **Tamanho da Fonte** (de 12px a 100px)

**Exceções:**
- **Rodapé**: Sempre centralizado horizontalmente (ignora pos_x)
- **Subtítulo**: Centralizado se pos_x = 0, caso contrário usa pos_x especificado
- **Corpo**: Alinhamento controlado por campo separado `corpo_alinhamento`

---

## 📐 Dimensões da Imagem

- **Largura**: 1000px (preview) / 1200px (exportação)
- **Altura**: 1300px
- **Margem Lateral**: 60px
- **Largura Útil**: 880px

---

## 🔧 Implementação Técnica

### Fontes Utilizadas
```python
fonte_titulo = ImageFont.truetype('static/fonts/GlobotipoCorporativa-Bold.ttf', tamanho_titulo)
fonte_subtitulo = ImageFont.truetype('static/fonts/GlobotipoCorporativa-Bold.ttf', tamanho_subtitulo)
fonte_corpo = ImageFont.truetype('static/fonts/GlobotipoCorporativa-Regular.ttf', tamanho_corpo)
fonte_corpo_bold = ImageFont.truetype('static/fonts/GlobotipoCorporativa-Bold.ttf', tamanho_corpo)
fonte_rodape = ImageFont.truetype('static/fonts/GlobotipoCorporativa-Regular.ttf', tamanho_rodape)
fonte_publico_alvo = ImageFont.truetype('static/fonts/GlobotipoCorporativa-Regular.ttf', tamanho_publico_alvo)
```

### Transformações de Texto
```python
# Título: sempre maiúsculas
titulo_upper = comunicado.titulo.upper()

# Subtítulo: sempre maiúsculas
subtitulo_upper = comunicado.subtitulo.upper()

# Corpo: mantém original + formatação markdown-like
# **texto** → negrito
# _texto_ → itálico

# Rodapé: mantém original
# Público Alvo: mantém original
```

---

## 📱 Compatibilidade

Estas regras são aplicadas em:

✅ **Preview em Tempo Real** (HTML/CSS no navegador)  
✅ **Imagem PNG Exportada** (Pillow/PIL em Python)  
✅ **Texto de Acessibilidade** (#ParaTodosVerem)

---

## 🚨 Importante

- **Nunca** alterar estas regras sem atualizar tanto `gerar_imagem.py` quanto `preview_comunicado.html`
- Sempre testar preview E exportação após qualquer mudança
- Manter consistência entre ambiente de desenvolvimento e produção

---

## 📞 Contato

Em caso de dúvidas sobre as regras de formatação, consulte o desenvolvedor responsável ou abra uma issue no repositório.

---

**Última revisão:** 28/11/2025  
**Versão do Sistema:** 2.0  
**Status:** ✅ Documentação Oficial
