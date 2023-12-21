import os
import json

from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from  langchain.output_parsers import PydanticOutputParser
from typing import List, Dict


load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


MODEL = "gpt-3.5-turbo-0613"


prompt = PromptTemplate.from_template(
    """
    너는 매우 경험이 많고 유능한 주문봇이야
    가게에서 판매하는 상품 정보를 바탕으로 고객 문의에 적절히 답변해주면 돼.
    
    가게에서 판매하는 상품 목록.
    1. 상품: 떡케익5호
    기본 판매 단위: 1개
    기본 판매 단위의 가격: 54,000원
    2. 상품: 무지개 백설기 케익
    기본 판매 단위: 1개
    기본 판매 단위의 가격: 51,500원
    3. 상품: 미니 백설기
    기본 판매 단위: 1세트(35개)
    기본 판매 단위의 가격: 31,500원
    4. 상품: 개별 모듬팩
    기본 판매 단위: 1개
    기본 판매 단위의 가격: 13,500원

    고객 문의는 크게 두 유형으로 구분돼.
    - 단순 문의:단순 문의란 주문 요청, 주문내역 조회 요청, 주문취소 요청 등 어떤 작업을 요청하지 않는 메시지를 의미해. 
    - 요청 문의: 주문 요청, 주문내역 조회 요청, 주문취소 요청 등 어떤 작업을 요청하는 메시지를 의미해.

    ##주의할 점##
    - 특정 표현이 포함돼 있는지만을 따져서 단순 문의와 요청 문의를 분류하면 실수할 수 있음. 예를 들어 다음과 같은 상황이 존재할 수 있어. 고객 메시지에 '주문'이란 단어가 포함돼 있어도 주문을 직접 요청하는 게 아니라 주문에 관한 일반적인 질문이나 이야기하는 상황.

    고객 문의를 꼼꼼하게 살펴보고 아래 정보들을 추출하여 json 형태로 추출 결과를 반환해줘. 
    json의 key와 value에 대한 설명:
    user (str): 고객의 사용자 이름
    response_type(str): [general], [response_to_request] 중 하나로 분류. 단순 문의에 대한 응답이라면  [general], 요청 문의에 대한 응답이라면 [response_to_request]
    response(str): 고객 문의에 대한 모델의 답변
    request_type (str): [order], [order_inquiry], [order_change], [order_cancel] 중 하나로 분류
    products (List[Dict]): 주문된 상품들의 목록, 각 상품은 다음 정보를 포함해야 함:
    - name (str): 상품명
    - price (int): 상품 가격
    - quantity (int): 주문 수량
    order_date (str): 문의 요청 날짜와 시간, '2023. 12. 15. 오후 5:54:51'와 같은 형식의 문자열

    출력 결과 예시
    ##단순 문의에 대한 답변 예시##
    {{
    "user": "사용자이름",
    "response_type": "general",
    "response": "사용자 문의에 대한 모델의 답변",
    "request_type": "general_inquiry",
    "products": [],
    "order_date": "2023. 12. 24. 오후 7:52:11"
    }}

    ##요청 문의에 대한 답변 예시##
    {{
    "user": "사용자이름",
    "response_type": "response_to_request",
    "response": "사용자 문의에 대한 모델의 답변",
    "request_type": "order",
    "products": [
        {{
        "name": "상품명1",
        "price": 22000,
        "quantity": 2
        }},
        {{
        "name": "상품명2",
        "price": 30000,
        "quantity": 2
        }}
    ],
    "order_date": "2023. 12. 15. 오후 5:54:51"
    }}
    
    <고객이 현재 입력한 메시지>
    {customer_message}
    <문의 요청 시간>
    {date}
    """
    )


# class JsonParser(BaseModel):
#     response: str = Field(
#         description="""
#         문의에 대한 답변 결과
#         {
#             "user": "사용자이름",
#             "response_type": "response_to_request"
#             "response": "사용자 문의에 대한 모델의 답변"
#             "request_type": "order",
#             "products": [
#                 {
#                 "name": "상품명1",
#                 "price": 22000,
#                 "quantity": 2
#                 },
#                 {
#                 "name": "상품명2",
#                 "price": 30000,
#                 "quantity": 2
#                 }
#                 ],
#             "order_date": "2023. 12. 15. 오후 5:54:51",
#             }
#             """
#     )
class JsonParser(BaseModel):
    user: str = Field(description="고객의 사용자 이름")
    response_type: str = Field(description="[general], [response_to_request] 중 하나로 분류. 단순 문의에 대한 응답이라면  [general], 요청 문의에 대한 응답이라면 [response_to_request]")
    response : str = Field(description="고객 문의에 대한 모델의 답변")
    request_type: str = Field(description="[order], [order_inquiry], [order_change], [order_cancel] 중 하나로 분류")
    products: List[Dict] = Field(description="주문된 상품들의 목록, 각 상품은 다음 정보를 포함해야 함: name (str): 상품명, price (int): 상품 가격, quantity (int): 주문 수량")
    order_date: str = Field(description="문의 요청 날짜와 시간, '2023. 12. 15. 오후 5:54:51'와 같은 형식의 문자열")

parser = PydanticOutputParser(pydantic_object=JsonParser)
    
message = "떡케익 5호 2개, 미니 백설기 1개로 주문 좀 변경할게요."
date = "2023. 12. 18. 오후 8:03:18"
chain = prompt | ChatOpenAI(model=MODEL)
# chain = prompt | ChatOpenAI(model=MODEL) | parser
response = chain.invoke({"customer_message": message,
                         "date": date})
print(type(response.content))
print(response)
# parsed_response = json.loads(response)
# print(parsed_response)

# output = chain.invoke({"customer_message": message,
#                        "date": date})
# print(parser.parse(output))

