from pydantic import BaseModel
from typing import Dict, TypedDict, TypeAlias, NotRequired


class Value(TypedDict):
    value: str
    # rFonts が複数存在する可能性があるため list にする
    font: NotRequired[list[str]]


TagInfo: TypeAlias = Dict[str, Value]


class DictTest(BaseModel):
    tags: TagInfo

    def get_tag_info(self) -> TagInfo:
        return self.tags


if __name__ == "__main__":
    data: TagInfo = {"tag1": {"font": "Arial", "value": "Value1"}}

    dict_test_instance = DictTest(tags=data)
    tag_info_result = dict_test_instance.get_tag_info()
    print(tag_info_result)

    tag_info_result["tag2"] = {"value": "Value2"}
    print(tag_info_result)
