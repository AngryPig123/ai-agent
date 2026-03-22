# Tool Router / Registry 구현 순서와 다음 개발 플랜

이 문서는 현재 코드베이스를 기준으로, 다음 개발 단계를 실제로 구현하면서 익힐 수 있도록 작업 순서를 정리한 문서다.

## 먼저 무엇부터 구현해야 하나

결론부터 말하면 `tool registry`를 먼저 구현하는 편이 맞다.

이유는 단순하다.

- `tool router`는 "무엇을 선택할지" 판단해야 한다.
- 그런데 선택 대상인 tool 목록과 메타데이터가 먼저 정리되어 있지 않으면 router는 사실상 동작할 수 없다.
- 즉, registry가 tool 집합과 lookup 기준을 제공하고, router는 그 위에서 선택 정책만 담당하는 구조가 가장 자연스럽다.

권장 순서:

1. `BaseTool`에 공통 메타데이터를 추가한다.
2. `ToolRegistry`를 만든다.
3. 개별 tool이 자신의 입력 조건과 출력 결과를 선언하도록 바꾼다.
4. `ToolRouter`를 만든다.
5. `BlogAnswerService`를 하드코딩된 순서 실행에서 state 기반 실행으로 바꾼다.
6. 마지막에 테스트를 붙인다.

## 구현 작업 순서 리스트

아래 순서대로 직접 구현하면 흐름을 익히기 좋다.

### 1. `BaseTool` 확장

대상 파일:

- `app/application/tool/base_tool.py`

해야 할 일:

- `name`, `description` 외에 아래 속성을 추가한다.
- `requires`: 이 tool이 실행되기 위해 필요한 상태 키 목록
- `provides`: 이 tool이 실행 후 제공하는 상태 키 목록
- `is_terminal`: 이 tool 실행 후 흐름을 종료해도 되는지 여부

추가하면 좋은 메서드:

- `build_input(state) -> dict`
- `can_handle(state) -> bool`
- `update_state(state, result) -> dict`

이 단계의 목적:

- 각 tool이 "무엇을 필요로 하고 무엇을 만들어내는지" 자기 자신이 설명할 수 있게 만드는 것

### 2. `ToolRegistry` 구현

대상 파일:

- `app/application/tool/tool_registry.py`

최소 기능:

- tool 등록
- 이름으로 tool 조회
- 등록된 전체 tool 목록 조회

처음에는 이 정도면 충분하다.

- `register(tool)`
- `get(name)`
- `list_tools()`

이 단계의 목적:

- router가 참조할 수 있는 tool 저장소 만들기
- `main.py` 조립 코드를 단순하게 만들기

### 3. 기존 tool들에 메타데이터 붙이기

대상 파일:

- `app/application/tool/search_blog_tool.py`
- `app/application/tool/summarize_context_tool.py`
- `app/application/tool/answer_draft_tool.py`

예시 흐름:

- `search_blog`는 `question`이 있으면 실행 가능하고 `posts`를 제공한다.
- `summarize_context`는 `posts`가 있으면 실행 가능하고 `summary`를 제공한다.
- `answer_draft`는 `question`, `posts`, `summary`가 있으면 실행 가능하고 `answer`를 제공한다.

이 단계의 목적:

- router가 rule 기반으로 다음 tool을 선택할 수 있는 재료 만들기

### 4. `ToolRouter` 구현

대상 파일:

- `app/application/tool/tool_router.py`

처음에는 rule-based로 시작하는 게 맞다.

최소 판단 기준:

- 아직 실행하지 않은 tool일 것
- 현재 state가 해당 tool의 `requires`를 만족할 것
- 가능하다면 아직 없는 결과를 만들어내는 tool을 우선할 것
- 최종 답을 만드는 tool은 `is_terminal=True`로 구분할 것

처음 버전에서 추천하는 메서드:

- `next_tool(state, executed_tools) -> BaseTool | None`

이 단계의 목적:

- 고정된 절차 대신 상태 기반 선택으로 전환하기

### 5. `BlogAnswerService`를 오케스트레이터로 변경

대상 파일:

- `app/application/service/blog_answer_service.py`

현재 문제:

- tool 실행 순서가 서비스 안에 하드코딩되어 있다.
- 실패 처리가 약하다.
- `result.data`가 `None`이어도 바로 `.get()`을 호출하고 있다.

변경 방향:

- 초기 state를 `{"question": text}`로 시작한다.
- `while` 루프에서 router가 다음 tool을 고른다.
- tool 실행 결과를 state에 반영한다.
- terminal tool 실행 후 종료한다.
- 최종적으로 `answer`가 없으면 명시적으로 예외를 발생시킨다.

이 단계의 목적:

- service를 "직접 실행자"가 아니라 "흐름 관리자"로 바꾸기

### 6. `main.py` 조립 코드 변경

대상 파일:

- `app/main.py`

해야 할 일:

- tool 인스턴스를 만든다.
- registry에 등록한다.
- router를 생성한다.
- service에 registry/router를 주입한다.

이 단계의 목적:

- 런타임 조립 지점을 명확히 분리하기

### 7. 테스트 추가

추천 테스트 파일:

- `tests/test_tool_router.py`
- `tests/test_blog_answer_service.py`

처음에 꼭 넣을 테스트:

- question만 있을 때 `search_blog`가 선택되는지
- posts까지 있으면 `summarize_context`가 선택되는지
- summary까지 있으면 `answer_draft`가 선택되는지
- 실행 가능한 tool이 없으면 `None`을 반환하는지
- tool 실패 시 service가 명시적으로 실패하는지

이 단계의 목적:

- 구조가 커지기 전에 선택 로직을 고정하기

## 직접 구현하면서 익히기 좋은 추천 순서

가장 학습 효율이 좋은 실제 작업 순서는 아래다.

1. `BaseTool`에 `requires`, `provides`, `build_input`만 먼저 넣는다.
2. `SearchBlogTool` 하나만 새로운 방식으로 바꾼다.
3. `ToolRegistry`를 만든다.
4. `ToolRouter`를 아주 단순한 규칙으로 만든다.
5. `SummarizeContextTool`, `AnswerDraftTool`를 같은 방식으로 바꾼다.
6. `BlogAnswerService`를 루프로 바꾼다.
7. 마지막으로 테스트를 붙인다.

이 순서가 좋은 이유:

- 처음부터 전부 바꾸지 않고 한 tool씩 구조를 고정할 수 있다.
- registry와 router의 역할 차이를 구현 과정에서 바로 체감할 수 있다.
- 중간 단계마다 실행 확인이 가능하다.

## 그 다음에 어떤 기능을 추가하면 좋은가

지금 프로젝트를 AI multi-agent 방향으로 키우려면, 단순히 tool 수를 늘리는 것보다 "에이전트가 어떤 상태를 보고 어떤 역할을 맡는가"를 먼저 분리하는 게 좋다.

### 1. Planner Agent 추가

역할:

- 사용자 질문을 분석해서 어떤 tool 또는 어떤 worker agent가 필요한지 계획한다.

추가 포인트:

- `plan`
- `subtasks`
- `required_capabilities`

이걸 넣으면 지금의 단순 router에서 한 단계 올라간다.

### 2. Executor Agent 분리

역할:

- 실제 tool 실행 담당
- 검색, 요약, 초안 작성 같은 작업 수행

효과:

- planner와 executor 책임이 분리된다.

### 3. Shared Memory 추가

권장 형태:

- short-term memory: 현재 세션 state
- long-term memory: 이전 대화, 작업 결과, 자주 쓰는 문서 요약

지금은 `ToolContext`만 있고 memory 개념이 거의 없다.
multi-agent로 가려면 memory 없이는 금방 막힌다.

### 4. Agent Registry 추가

tool registry 다음 단계로 자연스럽다.

역할:

- 어떤 agent가 어떤 capability를 가지는지 등록
- router가 tool이 아니라 agent를 선택할 수 있게 확장

예시:

- `research_agent`
- `writer_agent`
- `critic_agent`
- `retrieval_agent`

### 5. Agent Router 추가

tool router의 상위 계층이다.

역할:

- 지금 상태에서 어떤 agent에게 일을 넘길지 결정

좋은 구조:

- `AgentRouter`
- `ToolRouter`

즉, agent가 먼저 선택되고 그 agent 내부에서 tool이 선택되는 2계층 구조가 좋다.

### 6. Critic / Reviewer 단계 추가

아주 중요하다.

지금 구조는 답변을 만들기만 하고 검증하지 않는다.

추가할 만한 단계:

- 사실성 검토
- 근거 누락 검토
- 답변 품질 평가
- 정책 위반 여부 평가

이 단계를 넣으면 single-agent toy 수준에서 조금 더 실전형 구조로 올라간다.

### 7. 관측성 추가

반드시 필요한 항목:

- 어떤 tool이 왜 선택되었는지
- 실행 시간
- 입력 크기와 출력 크기
- 실패한 이유
- 전체 trace_id 기준 실행 흐름

지금은 디버깅 정보가 거의 없다.
multi-agent에서는 이게 없으면 원인 분석이 매우 어렵다.

### 8. 비동기 / 병렬 실행

예시:

- 검색은 여러 source에서 병렬
- 요약도 chunk 단위 병렬
- critic과 answer refinement를 병렬 후보 생성으로 확장

이 단계는 router와 state 관리가 먼저 안정화된 뒤 가는 게 맞다.

## 추천 로드맵

무리하지 않고 키우려면 아래 순서가 좋다.

1. Tool metadata + registry + router
2. Service orchestration loop
3. Router 테스트와 실패 처리
4. Planner agent
5. Shared memory
6. Agent registry / agent router
7. Critic agent
8. Parallel execution
9. Trace / observability
10. Human-in-the-loop 승인 단계

## 지금 코드 수준 평가

현재 코드는 "작동하는 첫 번째 RAG 파이프라인" 수준이다.

좋은 점:

- 레이어 분리는 의식하고 있다.
- port / adapter 방향이 크게 틀리지는 않았다.
- tool 개념을 이미 도입해 둬서 다음 단계 확장이 가능하다.
- `BlogAnswerService`가 유스케이스 진입점 역할을 하고 있어서 구조를 키우기 좋다.

아쉬운 점:

- 실제 실행 흐름은 아직 tool 기반이 아니라 하드코딩된 절차형 서비스에 가깝다.
- tool 간 계약이 명시적이지 않다.
- 에러 처리가 약하다.
- 테스트가 거의 없다.
- 관측성, 로깅, tracing이 부족하다.
- 설정값이 코드에 하드코딩되어 있다.
- LLM 호출 실패, DB 실패, empty retrieval 같은 경계 케이스 처리가 부족하다.

즉, 아키텍처 이름은 꽤 좋아 보이지만 실제 구현 완성도는 아직 초반 단계다.

## 지금 가장 부족한 부분

### 1. 계약 명세 부족

tool이 무엇을 입력으로 받고 무엇을 출력하는지 타입 수준에서 약하다.

보완 방향:

- Pydantic 모델 또는 dataclass 기반 input/output 스키마 도입

### 2. 실패 처리 부족

현재 코드에서는 실패가 발생해도 어디서 어떻게 실패했는지 추적이 어렵다.

보완 방향:

- `ToolResult`를 더 엄격하게 설계
- `error_code`
- `retryable`
- `metadata`

### 3. 테스트 부족

현재 단계에서 가장 위험한 부분이다.

보완 방향:

- router 단위 테스트
- service orchestration 테스트
- fake llm / fake embed / fake repository 기반 통합 테스트

### 4. 설정 하드코딩

현재 `main.py`에 DB URL, 모델 이름이 박혀 있다.

보완 방향:

- `settings.py`로 이동
- 환경 변수로 주입

### 5. 추상화와 실제 책임의 불일치

tool이 있지만 service가 다 제어하고 있다.

보완 방향:

- service는 orchestration만 담당
- tool은 capability 단위 실행
- router는 선택만 담당

### 6. 멀티 에이전트로 가기 위한 기반 부족

아직은 multi-agent라기보다 "tool을 순차 호출하는 single-agent workflow"에 가깝다.

보완 방향:

- planner
- reviewer
- memory
- agent routing

## 지금 당장 보완하면 좋은 항목

우선순위 순서로 정리하면 아래가 좋다.

1. `ToolRegistry` 구현
2. `ToolRouter` 구현
3. `BlogAnswerService`를 state 기반 루프로 전환
4. `ToolResult`와 실패 처리 강화
5. 테스트 추가
6. 설정 외부화
7. 실행 trace / logging 추가
8. planner agent 도입

## 최종 판단

지금 코드는 방향은 괜찮지만 아직 "구조를 설명할 수 있는 수준"이지 "안정적으로 확장 가능한 수준"은 아니다.

좋게 말하면:

- 다음 단계로 넘어가기 좋은 초석은 있다.

냉정하게 말하면:

- router / registry / state orchestration / test가 들어가기 전까지는 multi-agent로 부르기 어렵다.

그래서 다음 개발 단계는 아주 명확하다.

- 먼저 `registry`
- 그 다음 `router`
- 그 다음 `service orchestration`
- 그리고 테스트


  이 대화에서 정리된 수정 방향은 꽤 명확해졌다. 각 tool 구현체는 지금 app/application/tool/summarize_context_tool.py, app/
  application/tool/search_blog_tool.py, app/application/tool/answer_draft_tool.py 에서처럼 build_input(state)로 공용 state에서
  필요한 값만 추출하고, run(input_data, context)는 state를 모르도록 유지하는 방향이 맞다. 즉, tool은 state 전체를 직접 수정하지
  않고, 실행 결과만 ToolResult로 내보내고, state 반영은 update_state()를 통해 일관되게 처리하는 게 맞다는 점이 정리됐다. 서비스
  는 그 결과를 받아 다음 tool에 넘길 state를 갱신하는 orchestrator 역할을 해야 한다는 것도 분명해졌다.

  개선된 점은 개념적 경계가 정리된 것이다. build_input()는 “state에서 필요한 입력만 꺼내는 역할”, run()은 “순수 실행 역할”,
  update_state()는 “결과를 공용 state에 반영하는 역할”로 이해가 맞춰졌다. 그리고 app/application/service/blog_answer_service.py
  의 서비스 코드도, 네가 마지막에 적은 형태처럼 각 tool의 execute() 결과를 순차적으로 받아 다음 state로 넘기는 패턴이 현재 설계
  와 일치한다는 점이 확인됐다. 다만 여기에는 반드시 result.success 검사와 실패 시 중단 로직이 들어가야 한다는 보완점도 같이 드
  러났다.

  현재 작성된 코드를 기준으로 보면 아직 남아 있는 문제도 있다. app/application/tool/base_tool.py 는 execute()가 튜플을 반환하는
  구조로 가고 있는데, 그렇다면 이 패턴을 전체 코드에서 일관되게 유지해야 한다. is_terminal 기본값이 True인 것도 현재 단계에서는
  부적절하고, can_handle()와 can_handler()가 중복되어 있는 점도 정리 대상이다. app/application/service/blog_answer_service.py
  는 지금 순차 전달 구조로 바뀌고 있지만, 아직은 tool 실패 처리, 빈 결과 처리, 최종 answer 보장 같은 방어 코드가 더 필요하다.
  app/main.py 도 지금은 상태를 직접 만들고 서비스에 넘기는 수준이지만, 이후 registry/router를 붙이려면 조립 코드가 조금 더 명시
  적으로 바뀌어야 한다.

  동적 tool 선택을 위해 다음 단계로 구현해야 할 부분은 네 가지다. 첫째, app/application/tool/base_tool.py 에서 name, requires,
  provides, is_terminal 같은 메타데이터를 안정적으로 정리해야 한다. 지금 일부 tool에는 들어가 있지만 전체적으로 계약을 더 분명
  히 해야 한다. 둘째, ToolRegistry를 추가해 등록된 tool 목록과 lookup을 관리해야 한다. 이게 먼저 있어야 router가 선택 대상을 알
  수 있다. 셋째, ToolRouter를 만들어 현재 state와 이미 실행한 tool 목록을 바탕으로 다음 tool을 고르는 규칙을 넣어야 한다. 처음
  에는 rule-based면 충분하다. 예를 들면 question만 있으면 search_blog, blog_posts가 있으면 summarize_context, summary까지 있으
  면 answer_draft를 고르는 방식이다. 넷째, app/application/service/blog_answer_service.py 를 고정 순서 실행자에서 “현재 state를
  보고 router가 선택한 tool을 실행하는 루프”로 바꿔야 한다.

  결국 이번 세션에서 정리된 개발 방향은 이렇다. 지금 프로젝트는 “tool을 순차 호출하는 구조”까지는 손이 닿았고, 그 과정에서
  state 전달 방식과 tool 책임 경계가 정리됐다. 다음 단계는 그 순차 호출을 하드코딩하지 않고, registry에 등록된 tool들을 router
  가 state 기반으로 선택하게 만드는 것이다. 순서로 적으면 BaseTool 계약 정리 -> 서비스 실패 처리 정리 -> ToolRegistry 구현 ->
  ToolRouter 구현 -> BlogAnswerService를 router 기반 루프로 전환 -> 테스트 추가가 가장 자연스럽다. 원하면 다음 턴에서 이 기준으
  로 현재 코드에 정확히 어떤 파일을 어떤 순서로 수정하면 되는지 실행 계획처럼 쪼개서 적어줄 수 있다.

