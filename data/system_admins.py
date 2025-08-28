"""
한화생명 시스템 담당자 데이터베이스
실제 운영 환경에서는 데이터베이스나 API에서 가져올 데이터
"""

SYSTEM_ADMINS = [
    {
        'id': 'admin_001',
        'name': '김철수',
        'department': 'IT운영팀',
        'position': '차장',
        'phone': '02-1234-5678',
        'email': 'kim.cs@hanwha.com',
        'responsibilities': ['인사시스템', 'HR시스템', '급여시스템', '출입통제시스템'],
        'specialties': ['Oracle DB', 'Java 개발', '시스템 통합'],
        'keywords': ['인사', 'hr', '급여', '월급', '출입', '카드', '사원', '직원', '근태', '휴가']
    },
    {
        'id': 'admin_002',
        'name': '이영희',
        'department': 'IT운영팀',
        'position': '과장',
        'phone': '02-1234-5679',
        'email': 'lee.yh@hanwha.com',
        'responsibilities': ['보험가입시스템', '계약관리시스템', '고객관리시스템'],
        'specialties': ['SQL Server', '.NET 개발', '웹 애플리케이션'],
        'keywords': ['보험', '가입', '계약', '고객', '상품', '설계', '언더라이팅', '심사', '보험료']
    },
    {
        'id': 'admin_003',
        'name': '박민수',
        'department': 'IT보안팀',
        'position': '팀장',
        'phone': '02-1234-5680',
        'email': 'park.ms@hanwha.com',
        'responsibilities': ['보안시스템', '방화벽관리', '접근제어시스템', '백신관리'],
        'specialties': ['네트워크 보안', '침입탐지', '보안 컨설팅'],
        'keywords': ['보안', '방화벽', '접근', '권한', '백신', '해킹', '침입', 'vpn', '인증서', '암호화']
    },
    {
        'id': 'admin_004',
        'name': '최정민',
        'department': 'IT인프라팀',
        'position': '대리',
        'phone': '02-1234-5681',
        'email': 'choi.jm@hanwha.com',
        'responsibilities': ['서버관리', '네트워크관리', '스토리지관리', '백업시스템'],
        'specialties': ['Linux/Unix', 'VMware', '클라우드 인프라'],
        'keywords': ['서버', '네트워크', '인터넷', '연결', '백업', '복구', '장애', '점검', '스토리지', '디스크']
    },
    {
        'id': 'admin_005',
        'name': '정수연',
        'department': 'IT개발팀',
        'position': '차장',
        'phone': '02-1234-5682',
        'email': 'jung.sy@hanwha.com',
        'responsibilities': ['회계시스템', '재무시스템', '예산관리시스템', 'ERP시스템'],
        'specialties': ['SAP', 'ABAP 개발', '회계 프로세스'],
        'keywords': ['회계', '재무', '예산', 'erp', 'sap', '전표', '결산', '자산', '비용', '매출']
    },
    {
        'id': 'admin_006',
        'name': '한동욱',
        'department': 'IT지원팀',
        'position': '사원',
        'phone': '02-1234-5683',
        'email': 'han.dw@hanwha.com',
        'responsibilities': ['PC지원', '프린터관리', 'Office365', '화상회의시스템'],
        'specialties': ['Windows 지원', 'Office 제품군', '하드웨어 트러블슈팅'],
        'keywords': ['pc', '컴퓨터', '프린터', '오피스', '워드', '엑셀', '파워포인트', '화상회의', '팀즈', 'teams']
    },
    {
        'id': 'admin_007',
        'name': '송미경',
        'department': 'IT운영팀',
        'position': '과장',
        'phone': '02-1234-5684',
        'email': 'song.mk@hanwha.com',
        'responsibilities': ['영업지원시스템', '채널관리시스템', '대리점시스템', '모바일앱'],
        'specialties': ['모바일 개발', 'React Native', 'API 개발'],
        'keywords': ['영업', '채널', '대리점', '설계사', '모바일', '앱', 'fc', 'ga', '판매', '실적']
    },
    {
        'id': 'admin_008',
        'name': '임진호',
        'department': 'IT기획팀',
        'position': '부장',
        'phone': '02-1234-5685',
        'email': 'lim.jh@hanwha.com',
        'responsibilities': ['데이터웨어하우스', 'BI시스템', '통계분석시스템', '리포팅시스템'],
        'specialties': ['데이터 분석', 'Python', 'R', '머신러닝'],
        'keywords': ['데이터', '분석', '통계', '리포트', '대시보드', 'bi', '웨어하우스', '빅데이터', '예측']
    }
]
