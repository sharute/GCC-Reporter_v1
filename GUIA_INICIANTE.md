# 🎯 GUIA PASSO A PASSO - INICIANTE

## 📱 Sistema de Comunicados - Tutorial Simples

---

## PARTE 1: PREPARAR O SISTEMA

### Passo 1: Abrir o Terminal
- Pressione `Ctrl + Alt + T`
- Uma janela preta vai abrir

### Passo 2: Instalar Python (se necessário)
Digite esses comandos, um por vez:

```bash
sudo apt-get update
```
*Pressione Enter e digite sua senha se pedir*

```bash
sudo apt-get install python3 python3-pip
```
*Pressione Enter e depois digite `s` ou `y` se perguntar*

```bash
sudo apt-get install fonts-dejavu-core
```
*Pressione Enter*

### Passo 3: Ir para a pasta do projeto
```bash
cd /home/gccreporter
```

### Passo 4: Instalar as dependências
```bash
pip3 install --user -r requirements.txt
```
*Espere alguns segundos enquanto instala*

---

## PARTE 2: INICIAR O SISTEMA

### Passo 5: Rodar o script de inicialização
```bash
./iniciar.sh
```

**Você verá algo assim:**
```
🚀 Sistema de Comunicados - Globo Tecnologia
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Python: Python 3.x.x

📦 Instalando dependências...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🌐 Acesse: http://localhost:5000

  👤 Admin:    admin / admin123
  👤 Analista: analista / analista123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

✅ **O sistema está rodando!**

---

## PARTE 3: ACESSAR NO NAVEGADOR

### Passo 6: Abrir o navegador
- Abra Chrome, Firefox ou qualquer navegador
- Digite na barra de endereço:
```
http://localhost:5000
```
- Pressione Enter

### Passo 7: Fazer Login
Você verá uma tela de login. Use:

**Para testar como ANALISTA:**
- Usuário: `analista`
- Senha: `analista123`

**Para testar como ADMIN:**
- Usuário: `admin`
- Senha: `admin123`

---

## PARTE 4: CRIAR SEU PRIMEIRO COMUNICADO

### Passo 8: Clicar em "Criar Comunicado"
- Você verá uma tela dividida em duas partes
- **Esquerda**: Formulário para preencher
- **Direita**: Prévia do comunicado

### Passo 9: Preencher os campos

1. **Template**: Escolha "Template Padrão Globo"

2. **Título**: Digite
   ```
   AMBIENTE NORMALIZADO
   ```

3. **Subtítulo**: Digite
   ```
   Telefonia fixa - São Paulo
   ```

4. **Corpo** (clique na área de texto e digite):
   ```
   Informamos que recebimentos de ligações externas no sites JRM e BERRINI 
   através dos prefixos padrões 5509-XXXX / 5112-XXXX, estão normalizados.
   ```

5. **Rodapé**: Digite
   ```
   Em caso de dúvidas consulte o Service Desk no telefone 3003-7000
   ```

6. **Público Alvo**: Digite
   ```
   São Paulo
   ```

### Passo 10: Ver a Prévia
- Enquanto você digita, o lado direito mostra como ficará a imagem
- **É em tempo real!** Mágico, né? ✨

### Passo 11: Formatar o Texto (opcional)
- Selecione um texto
- Clique em **B** para negrito
- Clique em **I** para itálico
- Clique em **U** para sublinhado
- Clique em **• Lista** para criar lista

### Passo 12: Salvar e Baixar
- Clique no botão **"💾 Salvar e Gerar Imagem"**
- O download começa automaticamente!
- A imagem PNG será salva no seu computador

---

## PARTE 5: VER HISTÓRICO

### Passo 13: Acessar o Histórico
- Clique em **"📋 Histórico"** no menu superior
- Veja TODOS os comunicados já criados
- Clique em **"⬇️ Baixar"** para baixar novamente

---

## PARTE 6: PERSONALIZAR (APENAS ADMIN)

### Passo 14: Fazer Login como Admin
- Saia (botão "Sair")
- Entre novamente com:
  - Usuário: `admin`
  - Senha: `admin123`

### Passo 15: Abrir Painel Admin
- Clique em **"⚙️ Admin"** no menu superior

### Passo 16: Mudar Cores e Fontes
1. Aba **"🎨 Configurações"**
2. Você verá 4 seções:
   - 📝 Título
   - 📝 Subtítulo
   - 📄 Corpo
   - 🔻 Rodapé

3. Para cada seção você pode mudar:
   - **Fonte**: Nome da fonte
   - **Tamanho**: Número em pixels
   - **Cor**: Clique na caixinha colorida para escolher

4. Clique em **"💾 Salvar Configurações"**

### Passo 17: Adicionar Novos Templates
1. Aba **"🖼️ Templates"**
2. Digite um nome: `Meu Template Especial`
3. Clique em **"Escolher arquivo"**
4. Selecione uma imagem do seu computador
   - **Dica**: Use imagens de 1200x630 pixels
5. Clique em **"➕ Adicionar Template"**
6. Pronto! O template está disponível!

---

## DICAS E TRUQUES

### 💡 Atalhos do Teclado
- `Ctrl + B` = Negrito
- `Ctrl + I` = Itálico
- `Ctrl + U` = Sublinhado

### 💡 Prévia Automática
- A prévia atualiza sozinha enquanto você digita
- Não precisa clicar em nada!

### 💡 Templates
- Crie templates diferentes para:
  - Incidentes
  - Manutenções programadas
  - Avisos gerais
  - Comunicados urgentes

### 💡 Reaproveitando Comunicados
- Use o Histórico para ver comunicados antigos
- Copie e cole o texto para criar similares
- Baixe novamente se precisar

---

## PROBLEMAS COMUNS E SOLUÇÕES

### ❌ "python3: command not found"
**Solução:**
```bash
sudo apt-get install python3 python3-pip
```

### ❌ "Permission denied" ao executar iniciar.sh
**Solução:**
```bash
chmod +x iniciar.sh
```

### ❌ Erro ao gerar imagem
**Solução:**
```bash
sudo apt-get install fonts-dejavu-core
```

### ❌ Porta 5000 ocupada
**Solução:**
- Edite o arquivo `app.py`
- Na última linha, troque `5000` por `5001`
- Acesse `http://localhost:5001`

### ❌ Não consigo fazer login
**Solução:**
- Verifique se está digitando corretamente:
  - Usuário: `admin` (tudo minúsculo)
  - Senha: `admin123` (tudo minúsculo)

---

## PARA PARAR O SISTEMA

### Como parar:
1. Vá no Terminal onde está rodando
2. Pressione `Ctrl + C`
3. O sistema para

### Como iniciar novamente:
```bash
cd /home/gccreporter
./iniciar.sh
```

---

## PRECISA DE AJUDA?

### Verificar logs:
- O Terminal mostra todos os eventos
- Se der erro, copie a mensagem de erro

### Reiniciar do zero:
```bash
rm comunicados.db
python3 app.py
```
*Isso recria o banco de dados*

---

## RESUMO RÁPIDO

```
1. Instalar Python
2. cd /home/gccreporter
3. pip3 install --user -r requirements.txt
4. ./iniciar.sh
5. Abrir http://localhost:5000
6. Login: analista / analista123
7. Criar comunicado
8. Baixar PNG!
```

---

## ✅ CHECKLIST DE PRIMEIRO USO

- [ ] Python instalado
- [ ] Dependências instaladas
- [ ] Sistema iniciado
- [ ] Login funcionando
- [ ] Comunicado criado
- [ ] PNG baixado
- [ ] Histórico visualizado
- [ ] (Admin) Configurações alteradas
- [ ] (Admin) Template adicionado

---

**Pronto! Agora você é expert em criar comunicados! 🎉**

**Qualquer dúvida, consulte o README.md completo**
