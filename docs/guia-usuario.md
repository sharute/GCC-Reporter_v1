# 🎯 Guia do Usuário - Sistema de Comunicados

## Início Rápido

### 1. Iniciar o Sistema
```bash
cd /home/gccreporter
./iniciar.sh
```

### 2. Acessar
```
http://localhost:5000
```

---

## Criar um Comunicado

1. Clique em **"📢 Criar Comunicado"**
2. Selecione um **template**
3. Preencha os campos:
   - **Título**: Ex: "AMBIENTE NORMALIZADO" (obrigatório)
   - **Subtítulo**: Ex: "Telefonia fixa - São Paulo"
   - **Corpo**: Texto principal (obrigatório)
   - **Rodapé**: Ex: "Service Desk: 3003-7000"
   - **Público Alvo**: Ex: "São Paulo"

4. Use a barra de formatação:
   - **B**: Negrito | **I**: Itálico | **U**: Sublinhado

5. Veja a **prévia em tempo real** no painel direito
6. Clique em **"💾 Salvar e Gerar Imagem"**
7. Download automático do PNG!

---

## Ver Histórico

- Clique em **"📋 Histórico"** no menu
- Veja todos os comunicados criados
- Baixe novamente qualquer comunicado

---

## Painel Admin

### Configurar Estilos
1. Clique em **"⚙️ Admin"**
2. Aba **"🎨 Configurações"**
3. Ajuste fonte, tamanho e cor de cada elemento
4. Clique em **"💾 Salvar"**

### Gerenciar Templates
1. Aba **"🖼️ Templates"**
2. Digite o nome do template
3. Upload da imagem de fundo (1200x630px recomendado)
4. Clique em **"➕ Adicionar"**

---

## Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl + B` | Negrito |
| `Ctrl + I` | Itálico |
| `Ctrl + U` | Sublinhado |

---

## Solução de Problemas

### Python não encontrado
```bash
sudo apt-get install python3 python3-pip
```

### Erro ao gerar imagem
```bash
sudo apt-get install fonts-dejavu-core
```

### Porta 5000 ocupada
Edite `app.py`, altere a porta na última linha para `5001`

### Permissão negada no iniciar.sh
```bash
chmod +x iniciar.sh
```

---

## Parar e Reiniciar

**Parar**: Pressione `Ctrl + C` no terminal

**Reiniciar**:
```bash
./iniciar.sh
```
