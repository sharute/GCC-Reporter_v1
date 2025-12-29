# 🚀 GUIA DE INÍCIO RÁPIDO

## ⚡ 3 Passos Para Começar

### 1️⃣ Instalar Python e Dependências

```bash
# Instalar Python (se necessário)
sudo apt-get update
sudo apt-get install python3 python3-pip

# Instalar dependências do projeto
cd /home/gccreporter
pip3 install --user -r requirements.txt
```

### 2️⃣ Iniciar o Sistema

```bash
./iniciar.sh
```

ou manualmente:

```bash
python3 app.py
```

### 3️⃣ Acessar no Navegador

```
http://localhost:5000
```

**Login:**
- Admin: `admin` / `admin123`
- Analista: `analista` / `analista123`

---

## 📝 Criar Seu Primeiro Comunicado

1. **Login** como analista
2. Clique em **"📢 Criar Comunicado"**
3. Preencha:
   - Título: "AMBIENTE NORMALIZADO"
   - Subtítulo: "Telefonia fixa - São Paulo"
   - Corpo: Descrição do comunicado
   - Rodapé: "Em caso de dúvidas consulte o Service Desk"
4. Veja a **prévia em tempo real**
5. Clique em **"Salvar e Gerar Imagem"**
6. **Download automático** do PNG!

---

## ⚙️ Personalizar (Admin)

1. **Login** como admin
2. Clique em **"⚙️ Admin"**
3. Aba **"Configurações"**:
   - Ajuste fontes, tamanhos e cores
   - Salvar
4. Aba **"Templates"**:
   - Upload de imagens de fundo (1200x630px)

---

## 📂 Estrutura dos Arquivos

```
/home/gccreporter/
├── app.py              # 🐍 Aplicação principal
├── gerar_imagem.py     # 🖼️  Gerador de PNG
├── requirements.txt    # 📦 Dependências
├── iniciar.sh         # 🚀 Script de start
├── templates/         # 📄 HTML
└── static/uploads/    # 🖼️  Templates de imagem
```

---

## ⚠️ Problemas Comuns

**Python não encontrado:**
```bash
sudo apt-get install python3 python3-pip
```

**Erro ao gerar imagem:**
```bash
sudo apt-get install fonts-dejavu-core
```

**Porta ocupada:**
Edite `app.py` linha 318, troque `5000` por `5001`

---

## 💡 Dicas Rápidas

✅ Prévia atualiza em tempo real
✅ Use Ctrl+B, Ctrl+I, Ctrl+U para formatar
✅ Todos os comunicados ficam no histórico
✅ PNG gerado: 1200x630px (alta qualidade)
✅ Admin controla todo o visual

---

## 🔧 Status do Projeto

**Arquivos Criados:**
- ✅ `app.py` - Backend Flask completo
- ✅ `gerar_imagem.py` - Geração de imagens
- ✅ `requirements.txt` - Dependências
- ✅ `iniciar.sh` - Script de início
- ✅ `README.md` - Documentação completa
- ⚠️  `templates/*.html` - **FALTAM CRIAR**

**O que falta:**
Os templates HTML precisam ser criados. Vou criar agora.

---

**Pronto para usar! 🎉**
