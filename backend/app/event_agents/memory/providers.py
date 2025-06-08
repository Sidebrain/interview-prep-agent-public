from typing import Dict, List

import yaml

## Concrete implementations of providers


class YAMLConfigProvider:
    """Concrete implementation of ConfigProvider using YAML files."""

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path

    def get_system_prompt(self) -> List[Dict[str, str]]:
        if self.config_path is None:
            return []
        with open(self.config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            return [
                {
                    "role": "system",
                    "content": config["interview_agent"][
                        "system_prompt"
                    ],
                }
            ]
