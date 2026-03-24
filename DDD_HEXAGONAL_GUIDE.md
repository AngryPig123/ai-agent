# AI Agent 프로젝트에서 헥사고날 아키텍처와 DDD 정리

## 목적

이 문서는 `AI Agent + Hexagonal Architecture + DDD`를 같이 적용할 때,

- 헥사고날 아키텍처가 무엇을 지키려는 사상인지
- 각 영역에 무엇을 넣어야 하는지
- 무엇을 넣으면 경계가 무너지는지
- 특히 Agent 프로젝트에서 무엇을 조심해야 하는지

를 빠르게 판단할 수 있도록 정리한 문서다.

---

## 1. 헥사고날 아키텍처의 핵심 사상

헥사고날 아키텍처의 핵심은 "외부 기술이 내부 핵심을 흔들지 못하게 한다"는 것이다.

중요한 기준은 폴더 이름이 아니라 의존 방향이다.

- 안쪽은 바깥을 몰라야 한다
- 바깥은 안쪽을 알아도 된다
- 비즈니스 정책은 안쪽에 있어야 한다
- 프레임워크, DB, HTTP, LLM SDK 같은 것은 바깥에 있어야 한다

즉, 진짜 핵심은 다음이다.

- `domain`은 가장 안쪽
- `application`은 유스케이스와 흐름 조정
- `adapter / infrastructure`는 외부 세계와의 연결

헥사고날은 "계층을 예쁘게 나누는 기술"이 아니라 "핵심 정책을 외부 기술로부터 분리하는 설계 원칙"이다.

---

## 2. DDD와 헥사고날의 관계

둘은 경쟁 관계가 아니라 보완 관계다.

- DDD는 "무엇을 모델링할 것인가"에 가깝다
- 헥사고날은 "그 모델을 어떤 경계 안에 둘 것인가"에 가깝다

즉,

- DDD는 개념을 만든다
- 헥사고날은 그 개념이 외부 기술에 오염되지 않게 지킨다

예를 들어 AI Agent 프로젝트라면,

- DDD 관점에서는 `Question`, `AnsweringSession`, `ReferenceSet`, `ToolSelectionPolicy` 같은 개념이 중요할 수 있다
- 헥사고날 관점에서는 그런 개념이 `requests`, `sqlalchemy`, `ollama`, `fastapi`를 직접 몰라야 한다

---

## 3. 영역별 책임

### 3.1 Domain

가장 안쪽의 핵심 모델과 규칙이 들어간다.

들어가야 하는 것:

- Entity
- Value Object
- Domain Service
- Domain Rule
- Aggregate
- 도메인 개념 간의 불변 조건

들어가면 안 되는 것:

- SQLAlchemy 모델
- ORM 타입
- HTTP 요청/응답 객체
- `requests`, `fastapi`, `sqlalchemy`, `pydantic_settings`
- 프롬프트 전송 코드
- DB 세션
- 인프라 설정값 읽기

조심할 점:

- domain은 "데이터 통"이 아니라 의미를 가진 모델이어야 한다
- domain 모델이 프레임워크 타입에 의존하면 바로 경계가 무너진다
- domain에서 외부 API 응답 형식을 그대로 들고 있으면 안 된다

예시:

- `BlogPost`, `BlogPostChunk`
- 필요하다면 `AnsweringSession`, `Question`, `ReferenceSet`

주의:

- 단순 dataclass만 있다고 DDD가 되는 것은 아니다
- 도메인 규칙이 하나도 없으면 domain이 빈 껍데기가 되기 쉽다

### 3.2 Application

유스케이스를 실행하고 흐름을 조정하는 계층이다.

들어가야 하는 것:

- UseCase
- Application Service
- Inbound Port
- Outbound Port
- 유스케이스 요청/응답 모델
- 트랜잭션 경계의 논리적 조정
- 여러 도메인 객체와 외부 포트를 묶는 흐름

AI Agent 프로젝트에서 추가로 들어갈 수 있는 것:

- Agent Orchestrator
- Tool Router
- Tool Registry
- Tool 실행 정책
- Agent State

단, 이것들은 "application의 정책 객체"여야 한다.

들어가면 안 되는 것:

- 실제 HTTP 호출 구현
- DB 쿼리 구현
- ORM entity
- 외부 SDK 세부 코드
- 설정 파일 읽기

조심할 점:

- application이 너무 빈약하면 실제 정책이 adapter나 tool 구현으로 흩어진다
- 반대로 application이 외부 기술 코드를 직접 품기 시작하면 헥사고날이 무너진다
- `dict[str, Any]` 같은 범용 구조가 코어 모델 자리를 대신하기 시작하면 타입 경계가 약해진다

좋은 방향:

- `answer(command) -> result`
- `run(agent_state) -> agent_state`
- `select_next_tool(state) -> tool_name`

나쁜 방향:

- `execute(state: dict[str, Any])`
- 문자열 키로 상태를 계속 누적하는 방식
- application 내부에서 ORM 엔티티를 직접 다루는 방식

### 3.3 Adapter

application port를 실제 외부 세계와 연결하는 번역기다.

들어가야 하는 것:

- Inbound Adapter
- Outbound Adapter
- HTTP controller
- CLI entry adapter
- LLM adapter
- Embed adapter
- 메시지 큐 consumer/producer

역할:

- 외부 입력을 유스케이스 입력으로 번역
- 유스케이스 결과를 외부 응답 형식으로 번역
- outbound port를 실제 기술로 구현

들어가면 안 되는 것:

- 핵심 비즈니스 규칙
- 유스케이스 전체 흐름 결정
- 도메인 모델 대신 외부 DTO를 핵심 모델로 쓰는 것

조심할 점:

- adapter는 똑똑해지면 안 된다
- adapter가 정책을 가지기 시작하면 application이 비기 시작한다
- "LLM prompt를 어떻게 전송하는가"는 adapter에 가까울 수 있지만, "어떤 정보를 어떤 목적에 맞게 조합할 것인가"는 application 정책일 가능성이 높다

### 3.4 Infrastructure

기술 세부 구현을 담는 곳이다.

들어가야 하는 것:

- DB engine
- session factory
- ORM entity
- repository 구현
- config loader
- 외부 라이브러리 설정

들어가면 안 되는 것:

- 유스케이스 정책
- 도메인 규칙
- 에이전트의 의사결정 로직

조심할 점:

- infrastructure는 "중요하지 않다"는 뜻이 아니라 "핵심 정책의 바깥"이라는 뜻이다
- repository 구현은 infrastructure에 두되, interface는 application 쪽 port에 둔다

---

## 4. Port는 무엇인가

Port는 바깥과 연결되는 경계의 계약이다.

### Inbound Port

시스템이 외부로부터 어떤 요청을 받을 수 있는지를 정의한다.

예:

- `AnswerQuestionUseCase.answer(command) -> result`

좋은 특징:

- 유스케이스 언어가 드러난다
- 입력과 출력이 명확하다

나쁜 특징:

- `execute(state)`
- `handle(data: dict)`

이런 형태는 내부 표현을 바깥으로 새게 만들기 쉽다.

### Outbound Port

유스케이스가 외부 능력을 빌릴 때 사용하는 계약이다.

예:

- `BlogPostQueryPort`
- `BlogPostChunkQueryPort`
- `LLMPort`
- `EmbedPort`

좋은 특징:

- application은 "무엇이 필요하다"만 말한다
- 구현은 adapter/infrastructure가 맡는다

주의:

- port가 너무 저수준이면 application이 기술 세부사항을 너무 많이 알게 된다
- port가 너무 범용이면 모델링이 흐려진다

예:

- `generate(prompt: str)`는 단순하지만 저수준일 수 있다
- 어떤 프로젝트에서는 `summarize_references(...)`, `draft_answer(...)` 같은 더 의도 중심 포트가 맞을 수도 있다

---

## 5. AI Agent 프로젝트에서 특히 조심할 점

AI Agent 프로젝트는 헥사고날이 특히 무너지기 쉬운 분야다.

이유:

- 상태가 계속 바뀐다
- tool이 많다
- 라우팅 규칙이 있다
- 외부 LLM, embedding, vector search를 계속 호출한다
- 실험 코드가 코어로 들어오기 쉽다

그래서 아래 문제들이 자주 생긴다.

### 5.1 Tool 체인이 유스케이스를 잡아먹는 문제

증상:

- 서비스는 비어 있고
- 실제 정책은 tool들에 흩어지고
- orchestrator가 사실상 시스템 중심이 된다

이 경우 구조는 "Agent runtime 중심"이지 "UseCase 중심"이 아니다.

정리 기준:

- 유스케이스는 여전히 진입점이어야 한다
- tool, router, orchestrator는 application 내부의 협력 객체여야 한다
- "에이전트가 왜 이 tool을 선택하는가"는 application 정책으로 보여야 한다

### 5.2 State bucket 문제

증상:

- `dict[str, Any]`
- 문자열 키 누적
- 어디서 어떤 값이 채워지는지 추적이 어려움

문제:

- 타입 경계가 약해진다
- 리팩터링이 어려워진다
- 암묵적 결합이 생긴다

개선 방향:

- `AgentState`
- `ToolExecutionResult`
- `QuestionContext`
- `AnswerQuestionCommand`
- `AnswerQuestionResult`

처럼 명시적 모델을 둔다.

### 5.3 Tool을 generic utility로 보는 문제

증상:

- tool이 그냥 함수 묶음처럼 보인다
- 의미보다 순서만 남는다

개선 방향:

- tool은 capability 또는 action으로 본다
- 이름도 의미 중심으로 짓는다

예:

- `SearchRelevantPostsTool`
- `SummarizeReferencesTool`
- `DraftAnswerTool`

더 나아가면,

- `ToolSelectionPolicy`
- `AnsweringSession`
- `ReferencePreparationStep`

처럼 정책과 단계를 명시적으로 모델링할 수 있다.

### 5.4 Prompt와 정책이 섞이는 문제

AI 프로젝트에서는 prompt가 자주 정책을 먹어버린다.

구분 기준:

- 어떤 정보를 어떤 목적에 맞게 조합할지 결정하는 것: application 정책
- 실제로 모델 호출 payload를 만드는 것: adapter 또는 application의 명시적 translator

조심할 점:

- "프롬프트 문자열이 길다"는 이유로 무조건 adapter로 보내면 안 된다
- prompt 안에 핵심 업무 규칙이 들어 있으면 사실상 정책 코드다

---

## 6. 권장 의존 방향

권장 흐름:

- `domain <- application <- adapter/infrastructure`

좀 더 구체적으로:

- `domain`은 아무도 몰라도 스스로 서야 한다
- `application`은 `domain`과 `port`를 안다
- `adapter`는 `application port`를 구현한다
- `infrastructure`는 기술 세부 구현을 제공한다
- `main`은 조립만 한다

조심할 점:

- `domain -> sqlalchemy`
- `domain -> requests`
- `application -> orm entity`
- `application -> engine/session`
- `adapter -> usecase policy를 덮어쓰기`

이런 방향은 피해야 한다.

---

## 7. 프로젝트 구조 예시

이 프로젝트 성격이라면 아래 같은 구성이 이해하기 쉽다.

```text
app/
  domain/
    model/
    service/

  application/
    usecase/
    port/
      inbound/
      outbound/
    agent/
      agent_orchestrator.py
      tool_router.py
      tool_registry.py
      agent_state.py
      tools/

  adapter/
    inbound/
    outbound/

  infrastructure/
    config/
    db.py
    persistence/
      entity/
      repository/
```

핵심은 폴더가 아니라 책임이다.

- `application/agent`는 에이전트 정책
- `adapter/outbound/llm`은 실제 LLM 호출
- `infrastructure/persistence/repository`는 DB 구현

---

## 8. 각 영역에 넣어야 할 것 / 넣지 말아야 할 것

### Domain 체크리스트

넣어야 할 것:

- 도메인 개념
- 불변 조건
- 의미 있는 상태 전이

넣지 말아야 할 것:

- ORM 타입
- HTTP 타입
- SDK 응답 타입

### Application 체크리스트

넣어야 할 것:

- 유스케이스
- 흐름 조정
- 포트
- 에이전트 선택 정책

넣지 말아야 할 것:

- SQL 쿼리
- HTTP 호출 구현
- DB 세션 생성

### Adapter 체크리스트

넣어야 할 것:

- 포트 구현
- 외부 프로토콜 번역

넣지 말아야 할 것:

- 비즈니스 정책
- 핵심 상태 전이 규칙

### Infrastructure 체크리스트

넣어야 할 것:

- DB, 설정, ORM, 세션

넣지 말아야 할 것:

- 유스케이스 의사결정
- 도메인 규칙

---

## 9. 자주 하는 오해

### 오해 1. 폴더를 나누면 헥사고날이다

아니다. 의존 방향이 핵심이다.

### 오해 2. port interface만 있으면 충분하다

아니다. 유스케이스와 도메인 모델이 비어 있으면 껍데기만 남는다.

### 오해 3. AI Agent는 원래 동적이니 구조화하기 어렵다

어렵지만 구조화 불가능한 것은 아니다.

중요한 것은:

- 선택 정책을 명시적으로 드러내고
- 상태를 타입으로 모델링하고
- 외부 호출을 포트 뒤로 숨기는 것

### 오해 4. prompt는 전부 adapter 책임이다

아니다. prompt 안에 업무 규칙이 들어가면 이미 application 정책의 일부다.

---

## 10. 이 프로젝트에서 현실적인 목표

이 프로젝트 같은 AI Agent 시스템에서 처음부터 완벽한 DDD를 기대하기는 어렵다.

대신 다음 순서로 성숙도를 올리는 것이 현실적이다.

1. domain에서 외부 기술 의존 제거
2. inbound/outbound port 명확화
3. usecase request/response 명시화
4. agent state를 typed model로 전환
5. router/orchestrator/tool을 application 정책 객체로 재배치
6. 필요하면 그 다음에 aggregate, policy, session 모델로 더 끌어올리기

즉, 처음 목표는 "완벽한 DDD"가 아니라 아래에 가깝다.

- 핵심 정책이 바깥으로 새지 않게 만들기
- agent 흐름을 추론 가능한 구조로 만들기
- 기술 교체가 쉬운 경계를 확보하기

---

## 11. 최종 판단 기준

이 질문으로 스스로 체크하면 된다.

- domain이 프레임워크를 모르나?
- usecase가 실제 흐름의 중심인가?
- agent orchestration이 application 정책으로 보이나?
- tool 선택 규칙이 명시적으로 드러나나?
- adapter는 번역만 하고 있나?
- infrastructure가 코어 규칙을 몰라도 되나?
- 외부 기술을 바꿔도 application과 domain이 크게 안 흔들리나?

이 질문에 대부분 "예"라고 답할 수 있으면 헥사고날스럽다.

대부분 "아니오"라면 폴더만 헥사고날일 가능성이 높다.
