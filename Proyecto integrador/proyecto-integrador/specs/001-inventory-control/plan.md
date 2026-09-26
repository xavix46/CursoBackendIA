# Implementation Plan: Sistema de Control de Inventario Simple

**Branch**: `001-inventory-control` | **Date**: 2026-09-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-inventory-control/spec.md`

## Summary

Implementar un sistema de backend para control de inventario seguro y multi-usuario, exponiendo tanto una API REST (FastAPI) como un servidor MCP. El sistema asegura contraseñas hasheadas, garantiza el aislamiento de productos por usuario (retornando `403 Forbidden` ante accesos cruzados), restringe nombres duplicados por usuario, y hace cumplir que el stock de cualquier creación o ajuste nunca quede por debajo de la `cantidad_minima`. Incluye una suite completa de pruebas automatizadas con `pytest` para los 5 casos de error críticos definidos.

## Technical Context

**Language/Version**: Python >= 3.12 
**Primary Dependencies**: FastAPI, Uvicorn, SQLAlchemy 2.0, PyJWT, passlib[bcrypt]/bcrypt, pydantic-settings, email-validator, mcp[cli]<2
**Storage**: SQLite por defecto, configurable a PostgreSQL mediante SQLAlchemy ORM
**Testing**: pytest, pytest-cov, httpx
**Target Platform**: Servidor backend multiplataforma

## Constitution Check

- **Gate 1 - Aislamiento Multi-usuario**: **PASS** (Filtro estricto por `usuario_id`, rechazo con `403`).
- **Gate 2 - Paridad Funcional REST y MCP**: **PASS** (Ambos consumen `services/`).
- **Gate 3 - Cobertura de Casos Críticos de Error**: **PASS** (Tests explícitos para los 5 casos de error).
- **Gate 4 - Arquitectura y DIP**: **PASS** (Capa `repositories/` explícita, inyectada en `services/`).

## Project Structure

### Source Code (repository root)

```text
.
├── app/
│   ├── __init__.py
│   ├── main.py              
│   ├── config.py            
│   ├── database.py          
│   ├── auth.py              
│   ├── models/
│   │   ├── __init__.py
│   │   ├── usuario.py       
│   │   └── producto.py      
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── usuario.py       
│   │   └── producto.py      
│   ├── repositories/        
│   │   ├── __init__.py
│   │   ├── usuario_repo.py  # Operaciones DB aislando lógica SQL
│   │   └── producto_repo.py # Operaciones DB aislando lógica SQL
│   ├── services/
│   │   ├── __init__.py
│   │   ├── usuario_service.py   
│   │   └── producto_service.py  # Reglas de negocio; inyecta repos (DIP) y levanta excepciones de dominio
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          
│   │   └── productos.py     # Captura excepciones de dominio -> códigos HTTP
│   └── mcp/
│       ├── __init__.py
│       ├── server.py        
│       └── tools.py         # Captura excepciones de dominio -> retorna {"error": "..."}
├── tests/
│   ├── __init__.py
│   ├── conftest.py          
│   ├── test_auth.py         
│   ├── test_productos.py    # Usa repositorios falsos para aislar pruebas unitarias
│   └── test_mcp.py          
├── pyproject.toml           
├── .env.example             
└── README.md