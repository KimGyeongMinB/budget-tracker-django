from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from budgets.models import (
    Budget,
    Category,
    ExpensePrediction,
    MLCategoryTrainingData,
    TransactionRecord,
    TransactionType,
)


class Command(BaseCommand):
    help = "테스트 데이터를 생성합니다."

    def handle(self, *args, **options):
        User = get_user_model()

        user, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@example.com"},
        )

        if created:
            user.set_password("demo1234")
            user.save()

        food, _ = Category.objects.get_or_create(
            user=None,
            name="식비",
            type=TransactionType.EXPENSE,
            defaults={"is_default": True},
        )

        transport, _ = Category.objects.get_or_create(
            user=None,
            name="교통",
            type=TransactionType.EXPENSE,
            defaults={"is_default": True},
        )

        shopping, _ = Category.objects.get_or_create(
            user=None,
            name="쇼핑",
            type=TransactionType.EXPENSE,
            defaults={"is_default": True},
        )

        salary, _ = Category.objects.get_or_create(
            user=None,
            name="월급",
            type=TransactionType.INCOME,
            defaults={"is_default": True},
        )

        fixed, _ = Category.objects.get_or_create(
            user=None,
            name="고정지출",
            type=TransactionType.EXPENSE,
            defaults={"is_default": True},
        )

        allowance, _ = Category.objects.get_or_create(
            user=None,
            name="용돈",
            type=TransactionType.INCOME,
            defaults={"is_default": True},
        )

        # ── 1월 ──
        TransactionRecord.objects.get_or_create(
            user=user, category=salary, type=TransactionType.INCOME,
            amount=Decimal("500000"), description="아르바이트 급여",
            transaction_date=date(2026, 1, 5),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=allowance, type=TransactionType.INCOME,
            amount=Decimal("100000"), description="용돈",
            transaction_date=date(2026, 1, 1),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=food, type=TransactionType.EXPENSE,
            amount=Decimal("45000"), description="편의점 식비",
            transaction_date=date(2026, 1, 10),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=food, type=TransactionType.EXPENSE,
            amount=Decimal("38000"), description="마트 장보기",
            transaction_date=date(2026, 1, 18),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=transport, type=TransactionType.EXPENSE,
            amount=Decimal("28000"), description="교통카드 충전",
            transaction_date=date(2026, 1, 7),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=shopping, type=TransactionType.EXPENSE,
            amount=Decimal("67000"), description="쿠팡 생필품",
            transaction_date=date(2026, 1, 20),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=fixed, type=TransactionType.EXPENSE,
            amount=Decimal("80000"), description="통신비",
            transaction_date=date(2026, 1, 25),
        )

        # ── 2월 ──
        TransactionRecord.objects.get_or_create(
            user=user, category=salary, type=TransactionType.INCOME,
            amount=Decimal("500000"), description="아르바이트 급여",
            transaction_date=date(2026, 2, 5),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=allowance, type=TransactionType.INCOME,
            amount=Decimal("100000"), description="용돈",
            transaction_date=date(2026, 2, 1),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=food, type=TransactionType.EXPENSE,
            amount=Decimal("52000"), description="카페 식비",
            transaction_date=date(2026, 2, 8),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=food, type=TransactionType.EXPENSE,
            amount=Decimal("31000"), description="마트 장보기",
            transaction_date=date(2026, 2, 15),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=transport, type=TransactionType.EXPENSE,
            amount=Decimal("22000"), description="버스 교통비",
            transaction_date=date(2026, 2, 10),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=shopping, type=TransactionType.EXPENSE,
            amount=Decimal("45000"), description="의류 구매",
            transaction_date=date(2026, 2, 14),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=fixed, type=TransactionType.EXPENSE,
            amount=Decimal("80000"), description="통신비",
            transaction_date=date(2026, 2, 25),
        )

        # ── 3월 ──
        TransactionRecord.objects.get_or_create(
            user=user, category=salary, type=TransactionType.INCOME,
            amount=Decimal("520000"), description="아르바이트 급여",
            transaction_date=date(2026, 3, 5),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=allowance, type=TransactionType.INCOME,
            amount=Decimal("100000"), description="용돈",
            transaction_date=date(2026, 3, 1),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=food, type=TransactionType.EXPENSE,
            amount=Decimal("61000"), description="외식비",
            transaction_date=date(2026, 3, 9),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=food, type=TransactionType.EXPENSE,
            amount=Decimal("29000"), description="편의점 식비",
            transaction_date=date(2026, 3, 20),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=transport, type=TransactionType.EXPENSE,
            amount=Decimal("35000"), description="교통카드 충전",
            transaction_date=date(2026, 3, 6),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=shopping, type=TransactionType.EXPENSE,
            amount=Decimal("92000"), description="쿠팡 주문",
            transaction_date=date(2026, 3, 17),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=fixed, type=TransactionType.EXPENSE,
            amount=Decimal("80000"), description="통신비",
            transaction_date=date(2026, 3, 25),
        )

        # ── 4월 ──
        TransactionRecord.objects.get_or_create(
            user=user, category=salary, type=TransactionType.INCOME,
            amount=Decimal("500000"), description="아르바이트 급여",
            transaction_date=date(2026, 4, 5),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=allowance, type=TransactionType.INCOME,
            amount=Decimal("100000"), description="용돈",
            transaction_date=date(2026, 4, 1),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=food, type=TransactionType.EXPENSE,
            amount=Decimal("48000"), description="마트 장보기",
            transaction_date=date(2026, 4, 11),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=food, type=TransactionType.EXPENSE,
            amount=Decimal("33000"), description="카페 식비",
            transaction_date=date(2026, 4, 19),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=transport, type=TransactionType.EXPENSE,
            amount=Decimal("27000"), description="지하철 교통비",
            transaction_date=date(2026, 4, 8),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=shopping, type=TransactionType.EXPENSE,
            amount=Decimal("55000"), description="생활용품 구매",
            transaction_date=date(2026, 4, 22),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=fixed, type=TransactionType.EXPENSE,
            amount=Decimal("80000"), description="통신비",
            transaction_date=date(2026, 4, 25),
        )

        # ── 5월 ──
        TransactionRecord.objects.get_or_create(
            user=user, category=salary, type=TransactionType.INCOME,
            amount=Decimal("520000"), description="아르바이트 급여",
            transaction_date=date(2026, 5, 5),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=allowance, type=TransactionType.INCOME,
            amount=Decimal("100000"), description="용돈",
            transaction_date=date(2026, 5, 1),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=food, type=TransactionType.EXPENSE,
            amount=Decimal("57000"), description="외식비",
            transaction_date=date(2026, 5, 10),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=food, type=TransactionType.EXPENSE,
            amount=Decimal("41000"), description="마트 장보기",
            transaction_date=date(2026, 5, 21),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=transport, type=TransactionType.EXPENSE,
            amount=Decimal("31000"), description="교통카드 충전",
            transaction_date=date(2026, 5, 7),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=shopping, type=TransactionType.EXPENSE,
            amount=Decimal("78000"), description="쿠팡 주문",
            transaction_date=date(2026, 5, 16),
        )
        TransactionRecord.objects.get_or_create(
            user=user, category=fixed, type=TransactionType.EXPENSE,
            amount=Decimal("80000"), description="통신비",
            transaction_date=date(2026, 5, 25),
        )

        # ── 6월 (기존) ──
        TransactionRecord.objects.get_or_create(
            user=user,
            category=food,
            type=TransactionType.EXPENSE,
            amount=Decimal("6500"),
            description="스타벅스 아메리카노",
            transaction_date=date(2026, 6, 8),
        )

        TransactionRecord.objects.get_or_create(
            user=user,
            category=transport,
            type=TransactionType.EXPENSE,
            amount=Decimal("1450"),
            description="지하철",
            transaction_date=date(2026, 6, 8),
        )

        TransactionRecord.objects.get_or_create(
            user=user,
            category=shopping,
            type=TransactionType.EXPENSE,
            amount=Decimal("32900"),
            description="쿠팡 생필품 주문",
            transaction_date=date(2026, 6, 7),
        )

        TransactionRecord.objects.get_or_create(
            user=user,
            category=salary,
            type=TransactionType.INCOME,
            amount=Decimal("500000"),
            description="아르바이트 급여",
            transaction_date=date(2026, 6, 5),
        )

        Budget.objects.get_or_create(
            user=user,
            year=2026,
            month=6,
            defaults={"amount": Decimal("700000")},
        )

        # 식비 학습 데이터 (125개)
        for desc in [
            # 카페/음료
            "스타벅스", "스타벅스 아메리카노", "스타벅스 라떼", "스타벅스 프라푸치노",
            "이디야", "이디야커피", "메가커피", "메가MGC", "투썸플레이스", "투썸",
            "할리스", "커피빈", "폴바셋", "블루보틀", "카페베네", "엔제리너스",
            "아메리카노", "카페라떼", "카푸치노", "아이스라떼", "콜드브루",
            "카페음료", "음료구매", "커피값", "카페값",
            # 패스트푸드
            "맥도날드", "맥도날드 햄버거", "버거킹", "버거킹 와퍼", "롯데리아", "KFC", "맘스터치",
            "서브웨이", "쉐이크쉑", "파이브가이즈", "노브랜드버거",
            # 배달
            "배민", "배달의민족", "쿠팡이츠", "요기요", "배달주문", "치킨배달", "피자배달",
            "배달비", "치킨주문", "피자주문", "족발배달", "보쌈배달", "중국집배달",
            # 한식
            "삼겹살", "삼겹살집", "고기집", "국밥", "순대국밥", "설렁탕", "갈비탕",
            "냉면", "물냉면", "비빔냉면", "김치찌개", "된장찌개", "부대찌개", "청국장",
            "곱창", "막창", "불고기", "갈비", "보쌈", "족발", "쌈밥",
            # 분식/간식
            "떡볶이", "순대", "튀김", "김밥", "김밥천국", "분식집", "라면", "우동",
            "편의점 도시락", "편의점 삼각김밥", "편의점 컵라면", "간식", "빵", "파리바게뜨", "뚜레쥬르",
            # 일식/중식/양식
            "초밥", "스시", "일식", "라멘", "돈카츠", "마라탕", "마라샹궈", "중식",
            "파스타", "피자", "스테이크", "양식", "이탈리안",
            # 식재료/장보기
            "식재료구매", "채소구입", "과일구입", "정육점", "수산물", "반찬가게",
            "재래시장", "전통시장", "시장반찬", "장보기음식",
            # 식사 일반
            "점심", "저녁", "아침", "점심식사", "저녁식사", "외식", "회식", "식비",
            "밥값", "식사비", "음식값", "먹거리", "저녁밥", "점심밥",
        ]:
            MLCategoryTrainingData.objects.get_or_create(user=user, category=food, description=desc)

        # 교통 학습 데이터 (125개)
        for desc in [
            # 지하철
            "지하철", "지하철요금", "지하철비", "지하철충전", "수도권전철", "전철",
            "지하철1호선", "지하철2호선", "지하철3호선", "지하철4호선", "지하철5호선",
            "지하철6호선", "지하철7호선", "지하철8호선", "지하철9호선",
            "신분당선", "분당선", "경의중앙선", "공항철도", "AREX", "도시철도",
            "지하철승차", "지하철하차", "환승", "지하철역",
            # 버스
            "버스", "버스요금", "버스비", "버스충전", "광역버스", "마을버스", "시내버스",
            "버스카드", "버스탑승", "고속버스", "시외버스", "직행버스", "간선버스", "지선버스",
            "공항버스", "리무진버스", "셔틀버스", "통학버스",
            # 교통카드
            "교통카드", "티머니", "캐시비", "레일플러스", "한페이", "교통카드충전",
            "티머니충전", "캐시비충전", "선불교통카드",
            # 택시
            "택시", "택시비", "카카오택시", "카카오T", "우버", "타다", "UT택시",
            "모범택시", "대형택시", "택시요금", "심야택시", "콜택시",
            # 기차/KTX
            "기차", "기차표", "기차요금", "KTX", "KTX예매", "KTX요금", "SRT", "SRT예매",
            "ITX", "무궁화호", "새마을호", "코레일", "레츠코레일",
            # 기타 교통
            "킥보드", "전동킥보드", "씽씽", "라임", "빔", "따릉이", "공공자전거",
            "자전거", "렌터카", "차량렌트", "주유", "주유비", "기름값", "휘발유",
            "경유", "LPG", "통행료", "하이패스", "주차비", "주차요금",
            "교통비", "이동비", "출퇴근비",
        ]:
            MLCategoryTrainingData.objects.get_or_create(user=user, category=transport, description=desc)

        # 쇼핑 학습 데이터 (125개)
        for desc in [
            # 온라인 쇼핑몰
            "쿠팡", "쿠팡로켓", "쿠팡로켓배송", "11번가", "G마켓", "옥션", "인터파크",
            "위메프", "티몬", "SSG", "SSG닷컴", "롯데ON", "롯데온", "현대H몰",
            "네이버쇼핑", "네이버스마트스토어", "카카오쇼핑", "온라인쇼핑", "인터넷쇼핑",
            # 패션
            "무신사", "무신사스토어", "지그재그", "에이블리", "브랜디", "하고",
            "유니클로", "자라", "ZARA", "H&M", "스파오", "탑텐", "8seconds",
            "아디다스", "나이키", "뉴발란스", "푸마", "리복", "컨버스", "반스",
            "옷", "의류", "의류구매", "옷구매", "패션", "티셔츠", "바지", "청바지",
            "코트", "자켓", "점퍼", "후드티", "맨투맨", "니트", "원피스", "치마",
            "신발", "운동화", "구두", "슬리퍼", "샌들", "신발구매",
            "가방", "백팩", "크로스백", "숄더백", "클러치", "가방구매",
            # 뷰티/화장품
            "올리브영", "올리브영구매", "화장품", "스킨케어", "메이크업", "향수",
            "샴푸", "린스", "바디워시", "로션", "선크림", "립스틱", "파운데이션",
            # 생활용품
            "다이소", "이케아", "생활용품", "생필품", "주방용품", "욕실용품",
            "청소용품", "세제", "휴지", "물티슈",
            # 전자기기
            "애플스토어", "삼성스토어", "전자제품", "핸드폰케이스", "이어폰", "충전기",
            "노트북", "태블릿", "스마트워치", "악세사리",
        ]:
            MLCategoryTrainingData.objects.get_or_create(user=user, category=shopping, description=desc)

        # 고정지출 학습 데이터 (125개)
        for desc in [
            # 통신
            "통신비", "핸드폰요금", "휴대폰요금", "통신요금", "데이터요금",
            "SKT", "KT", "LGU+", "알뜰폰", "선불폰", "로밍요금",
            "인터넷요금", "인터넷비", "유선인터넷", "와이파이",
            "KT인터넷", "SKB", "LG인터넷",
            # 주거
            "월세", "월세이체", "월세납부", "전세이자", "관리비", "아파트관리비",
            "전기요금", "전기세", "전기비", "한전", "수도요금", "수도세", "수도비",
            "가스요금", "가스비", "도시가스", "난방비", "공과금", "관리비납부",
            # 보험
            "보험", "보험료", "생명보험", "실손보험", "자동차보험", "화재보험",
            "암보험", "건강보험", "국민건강보험", "국민연금", "고용보험",
            # OTT/구독
            "넷플릭스", "유튜브프리미엄", "유튜브구독", "스포티파이", "애플뮤직",
            "애플TV+", "디즈니플러스", "디즈니+", "왓챠", "웨이브", "티빙", "쿠팡플레이",
            "시즌", "네이버플러스", "네이버구독", "카카오구독", "밀리의서재",
            "리디북스", "윌라", "클래스101", "인프런", "패스트캠퍼스",
            # 정기결제
            "구독", "정기구독", "월정액", "월납부", "자동이체", "정기결제",
            "월간이용료", "연간구독", "멤버십", "프리미엄멤버십",
            "아마존프라임", "애플원", "마이크로소프트365", "어도비",
            # 대출/적금
            "대출이자", "학자금대출", "신용대출", "적금", "청약", "펀드",
            "고정비", "월고정비", "매달납부",
        ]:
            MLCategoryTrainingData.objects.get_or_create(user=user, category=fixed, description=desc)

        ExpensePrediction.objects.get_or_create(
            user=user,
            target_year=2026,
            target_month=7,
            defaults={"predicted_amount": Decimal("620000")},
        )

        self.stdout.write(self.style.SUCCESS("테스트 데이터 생성이 완료되었습니다."))
