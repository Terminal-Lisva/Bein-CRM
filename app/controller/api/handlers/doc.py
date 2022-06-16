from pydantic import BaseModel, validator, ValidationError
from datetime import date





class ModelFieldMeta(BaseModel):
    href: str
    type: str

class ModelField(BaseModel):
    meta: ModelFieldMeta

class ModelDoc(BaseModel):
    code_doc: ModelField
    name: str
    date_start: date
    date_finish: date
    responsible: ModelField

    @validator('code_doc')
    def check_type_meta_code_doc(cls, code_doc):
        if code_doc.meta.type != "document management system":
            raise ValueError()
        return code_doc

    @validator('responsible')
    def check_type_meta_responsible(cls, responsible):
        if responsible.meta.type != "app users":
            raise ValueError()
        return responsible
