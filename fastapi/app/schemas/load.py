from pydantic import BaseModel, Field
from typing import Optional

class LoadModelRequest(BaseModel):
    model_name: str = Field(..., example="meu_modelo")
    alias: Optional[str] = Field(None, example="champion")
    version: Optional[str] = Field(None, example="3")

    def validate_choice(self):
        if not self.alias and not self.version:
            raise ValueError("Informe ao menos 'stage' ou 'version'.")
