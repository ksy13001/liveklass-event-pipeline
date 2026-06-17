# liveklass-event-pipeline

웹 서비스에서 발생하는 유저 행동 이벤트를 생성·저장·분석하는 소규모 데이터 파이프라인입니다.

---

## 1. 실행 방법

**필요한 도구**

- [Git](https://git-scm.com)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

**설치 및 실행**

```bash
git clone https://github.com/ksy13001/liveklass-event-pipeline.git

cd liveklass-event-pipeline

docker compose up --build
```

실행이 완료되면 `charts/` 폴더가 생성되고 결과를 확인할 수 있습니다.

| 파일                                 | 분석 항목                         |
| ------------------------------------ | --------------------------------- |
| `charts/event_type_count.png`        | 이벤트 타입별 발생 횟수 및 비율   |
| `charts/hourly_trend.png`            | 시간대별 이벤트 타입 추이         |
| `charts/daily_trend.png`             | 일별 이벤트 타입 추이             |
| `charts/error_code_distribution.png` | 에러 코드별 발생 비율             |
| `charts/daily_revenue.png`           | 일별 결제금액 / 취소금액 / 실매출 |

---
<br>

## 2. 스키마 설명

```sql
CREATE TABLE IF NOT EXISTS events (
    id             BIGINT       AUTO_INCREMENT PRIMARY KEY,
    event_id       VARCHAR(36)  NOT NULL UNIQUE,
    event_type     VARCHAR(50)  NOT NULL,
    user_id        BIGINT       NOT NULL,
    order_id       INT,
    lecture_id     INT,
    amount         INT,
    payment_method VARCHAR(50),
    error_code     VARCHAR(50),
    error_page     VARCHAR(100),
    timestamp      DATETIME     NOT NULL
);
```

4가지 이벤트 타입을 단일 테이블로 관리하며, 이벤트 타입에 따라 사용하지 않는 컬럼은 NULL을 허용합니다. `id`(BIGINT)는 내부 PK, `event_id`(UUID)는 이벤트 고유 식별자로 역할을 분리했으며, `timestamp`에 이벤트 발생 시각을 기록합니다.

---
<br>

## 3. 구현하면서 고민한 점

### 이벤트 테이블 설계

이벤트 타입 간 공통 필드(`event_id`, `user_id`, `timestamp` 등)는 별도 컬럼으로 저장하고, 이벤트 타입별로 다른 필드(`amount`, `payment_method`, `error_code` 등)는 nullable 컬럼으로 설계했습니다.
    
처음에는 이벤트 타입별 가변 필드를 JSON 컬럼 하나에 저장하는 방식도 고려했습니다. 하지만 JSON 방식은 집계 시 JSON 함수를 사용해야 해서 쿼리가 복잡해지고, 과제 요구사항에서도 이벤트 필드를 구분해 저장하는 것을 요구하고 있었습니다. 현재 이벤트 타입과 가변 필드 수가 많지 않기 때문에, 명시적인 컬럼과 NULL 허용 방식이 더 단순하고 분석하기 쉽다고 판단했습니다.

다만 이벤트 타입이 계속 늘어나고 타입별 속성이 많아진다면, 공통 필드는 컬럼으로 유지하고 타입별 가변 필드는 JSON 컬럼으로 관리하는 방식도 고려할 것 같습니다. 이 경우 스키마 변경 없이 새 이벤트 속성을 추가할 수 있어 확장성 측면에서 유리할 것 같습니다.


### MySQL 선택 이유

이벤트 타입별 건수, 시간대별 추이, 매출 합계 등 집계 쿼리를 통한 시각화가 필요했기 때문에 `GROUP BY`, `CASE WHEN`, `SUM` 같은 SQL을 그대로 쓸 수 있는 관계형 DB를 선택했습니다.

관계형 DB 중에서는 MySQL과 PostgreSQL을 후보로 고민했습니다. PostgreSQL은 대용량 INSERT 성능과 JSONB 지원 면에서 유리할 수 있지만, 이번 과제는 제한된 시간 안에 이벤트 생성·저장·분석·시각화까지 완성하는 것이 중요했습니다. 따라서 제가 더 익숙하게 다룰 수 있는 MySQL을 선택하는 편이 안정적이라고 판단했습니다.

또한 현재 규모에서는 두 DB 간 성능 차이가 실질적으로 크지 않을 것이라고 생각했고, JSON 컬럼도 도입하지 않아 PostgreSQL의 JSONB 장점도 크기 필요하지 않았습니다. 향후 데이터 규모가 커지거나 이벤트 타입별 속성이 다양해져 JSON 저장이 필요해진다면 PostgreSQL 전환을 고려할 것입니다.

### 이벤트 타입 설계

이벤트 타입은 단순 조회 행동(`page_view`), 매출과 관련된 행동(`purchase_complete`, `purchase_cancel`), 서비스 품질 분석에 필요한 실패 상황(`error`)으로 나누었습니다. 이를 통해 기본 트래픽, 매출 흐름, 에러 비율을 모두 집계할 수 있도록 설계했습니다.

### 이벤트 생성 방식 

실제 서비스 로그처럼 무한 생성하는 방식과, 이벤트 수를 정해두고 한 번에 생성하는 일괄 생성 방식 중 어떤 것을 선택할지 고민했습니다. 무한 생성 방식은 실제 환경에 가깝지만 과제처럼 짧게 실행하고 결과를 확인하는 환경에서는 시간 분포 분석이 제한적인 문제가 있었습니다.

그래서 이번 과제에서는 총 이벤트 수와 1주일치 타임스탬프 범위를 지정하고, 시간대별 가중치를 적용해 이벤트를 일괄적으로 생성했습니다. 이 방식은 시간대별 이벤트 추이가 더 자연스럽고, `docker compose up --build` 한 번으로 생성·적재·분석까지 완료되어 실행 편의성도 높아졌습니다.


### DB 적재 방식

이벤트를 단건으로 생성하던 방식에서 일괄 생성 방식으로 전환하면서, DB 적재도 단건 `INSERT` 대신 `executemany()`로 한 번에 처리하도록 변경했습니다. 현재 이벤트 수(10만 건)는 메모리에 올려두고 한 번에 적재하는 방식으로 충분하지만, 이벤트 수가 수백만~수천만 건 이상 늘어난다면 일정 단위로 나누어 생성하고 적재하는 방식으로 전환할 예정입니다.


### 결제 취소의 인과관계 보장

이벤트 생성 시 모든 필드를 랜덤값으로 채우면 결제 완료 없이 결제 취소가 발생하는 등 데이터 정합성이 깨지는 문제가 있었습니다. 단순 시뮬레이션 데이터라도 설득력 있는 집계 결과를 위해 결제 취소 이벤트는 결제 완료가 선행된 주문에 대해서만 발생하도록 설계했습니다.