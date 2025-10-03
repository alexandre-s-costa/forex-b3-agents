import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Iniciando Forex Agents...")
    print("Acesse a interface em: http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    