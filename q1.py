from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Optional, Literal


class ToolCallSchema(BaseModel):
    action: Literal["search", "answer"]
    q: Optional[str] = Field(default=None)
    k: int = Field(default=3, ge=1, le=5)

    @model_validator(mode="after")
    def validate_q(self):
        if self.action == "search":
            if self.q is None or (isinstance(self.q, str) and not self.q.strip()):
                raise ValueError("q: String should have at least 1 character")

        return self


def validate_tool_call(payload):
    try:
        validated = ToolCallSchema.model_validate(payload)
        return validated.model_dump(), []
    except ValidationError as e:
        return {}, format_errors(e)


def format_errors(e: ValidationError) -> list[str]:
    messages: list[str] = []
    for err in e.errors():
        loc = ".".join(str(part) for part in err.get("loc", ()))
        msg = err.get("msg", "Invalid value")
        if loc:
            messages.append(f"{loc}: {msg}")
        else:
            messages.append(msg)
            
    return messages


if __name__ == "__main__":
    example_payloads = [
        {"action": "search", "q": "hello", "k": 3},
        {"action": "answer", "k": 10},
        {"action": "search", "q": "hello", "k": "3"}, 
        {"action": "search", "q": "", "k": "6"},
        {"action": "search"},
        {"action": "", "q": "", "k": "6"},
        {"action": "search", "q": "egg", "k": "6"},
        {"action": "search", "q": "egg", "k": "abc"},
        {"action": "search", "q": "egg", "k": ""},
    ]

    for i, payload in enumerate(example_payloads, start=1):
        clean, errors = validate_tool_call(payload)
        print(f"Example {i}:")
        print("  input :", payload)
        print("  clean :", clean)
        print("  errors:", errors)
        print()
