#!/usr/bin/env python3
"""
Script de migração para adicionar coluna tags ao banco de dados
"""
import sqlite3
import os

db_path = 'database/comunicados.db'

if not os.path.exists(db_path):
    print(f"❌ Banco de dados {db_path} não encontrado!")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se a coluna existe
    cursor.execute("PRAGMA table_info(comunicado)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'tags' not in columns:
        print("🔄 Adicionando coluna 'tags'...")
        cursor.execute("ALTER TABLE comunicado ADD COLUMN tags TEXT DEFAULT ''")
        conn.commit()
        print("✅ Coluna 'tags' adicionada com sucesso!")
    else:
        print("✅ Coluna 'tags' já existe")
    
    # Verificar novamente
    cursor.execute("PRAGMA table_info(comunicado)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"📋 Colunas na tabela comunicado: {', '.join(columns)}")
    
    conn.close()
    print("✅ Migração concluída!")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("✅ Coluna 'tags' já existe (erro esperado)")
    else:
        print(f"❌ Erro: {e}")
        exit(1)
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    exit(1)

