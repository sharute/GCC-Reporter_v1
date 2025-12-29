#!/usr/bin/env python3
"""
Script para corrigir os horários dos comunicados existentes
Converte de UTC para horário de Brasília (UTC-3)
"""
import sys
sys.path.insert(0, '/home/gccreporter')

from app import app, db, Comunicado
from datetime import datetime, timezone, timedelta

TZ_BRASIL = timezone(timedelta(hours=-3))

def corrigir_horarios():
    """Corrige os horários dos comunicados existentes"""
    with app.app_context():
        comunicados = Comunicado.query.all()
        if not comunicados:
            print("ℹ️ Nenhum comunicado encontrado")
            return
        
        print(f"🔄 Corrigindo horários de {len(comunicados)} comunicado(s)...")
        corrigidos = 0
        
        for comunicado in comunicados:
            atualizado = False
            
            # Corrigir criado_em apenas se o horário for suspeito (00:00-03:59)
            if comunicado.criado_em:
                dt_original = comunicado.criado_em
                hora = dt_original.hour
                
                # Apenas corrigir se o horário está entre 00:00 e 03:59 (suspeito de estar em UTC)
                if dt_original.tzinfo is None and (hora >= 0 and hora < 4):
                    print(f"  Comunicado ID {comunicado.id}:")
                    print(f"    Antes: {dt_original.strftime('%d/%m/%Y às %H:%M:%S')}")
                    
                    # Assumir UTC e converter para UTC-3
                    dt_utc = dt_original.replace(tzinfo=timezone.utc)
                    dt_brasil = dt_utc.astimezone(TZ_BRASIL)
                    comunicado.criado_em = dt_brasil.replace(tzinfo=None)
                    print(f"    Depois: {comunicado.criado_em.strftime('%d/%m/%Y às %H:%M:%S')}")
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
                print()
        
        if corrigidos > 0:
            db.session.commit()
            print(f"✅ {corrigidos} comunicado(s) corrigido(s) com sucesso!")
        else:
            print("ℹ️ Nenhum comunicado precisou de correção")

if __name__ == '__main__':
    try:
        corrigir_horarios()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

