"""
키워드 매칭 유틸리티
사용자 입력과 시스템 담당자의 키워드를 매칭하여 관련 담당자를 찾는 기능
"""

import re
from typing import List, Dict, Any

class KeywordMatcher:
    def __init__(self, admins_data: List[Dict[str, Any]]):
        """
        키워드 매처 초기화
        
        Args:
            admins_data: 시스템 담당자 데이터 리스트
        """
        self.admins_data = admins_data
        self.stopwords = {'은', '는', '이', '가', '을', '를', '에', '에서', '으로', '로', '와', '과', '의', 
                         '도', '만', '까지', '부터', '에게', '한테', '께', '에서부터', '문제', '오류', 
                         '에러', '시스템', '관련', '담당자', '찾아', '도와', '해결', '문의', '질문'}
    
    def clean_text(self, text: str) -> str:
        """
        텍스트 정규화 및 정제
        
        Args:
            text: 정제할 텍스트
            
        Returns:
            정제된 텍스트
        """
        # 소문자 변환
        text = text.lower()
        
        # 특수문자 제거 (한글, 영문, 숫자만 유지)
        text = re.sub(r'[^가-힣a-z0-9\s]', ' ', text)
        
        # 여러 공백을 하나로 변환
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        텍스트에서 의미있는 키워드 추출
        
        Args:
            text: 키워드를 추출할 텍스트
            
        Returns:
            추출된 키워드 리스트
        """
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        
        # 불용어 제거 및 의미있는 키워드만 추출
        keywords = []
        for word in words:
            if len(word) >= 2 and word not in self.stopwords:
                keywords.append(word)
        
        return keywords
    
    def calculate_match_score(self, user_keywords: List[str], admin: Dict[str, Any]) -> float:
        """
        사용자 키워드와 담당자 정보의 매칭 점수 계산
        
        Args:
            user_keywords: 사용자 입력에서 추출한 키워드
            admin: 담당자 정보
            
        Returns:
            매칭 점수 (0.0 ~ 1.0)
        """
        if not user_keywords:
            return 0.0
        
        # 담당자의 모든 키워드 수집
        admin_keywords = []
        
        # 담당자의 키워드 필드에서 키워드 추가
        if 'keywords' in admin:
            admin_keywords.extend(admin['keywords'])
        
        # 업무 범위에서 키워드 추출
        for responsibility in admin.get('responsibilities', []):
            admin_keywords.extend(self.extract_keywords(responsibility))
        
        # 전문 분야에서 키워드 추출
        for specialty in admin.get('specialties', []):
            admin_keywords.extend(self.extract_keywords(specialty))
        
        # 부서명에서 키워드 추출
        admin_keywords.extend(self.extract_keywords(admin.get('department', '')))
        
        # 중복 제거 및 소문자 변환
        admin_keywords = list(set([kw.lower() for kw in admin_keywords if kw]))
        
        # 매칭 점수 계산
        matches = 0
        total_keywords = len(user_keywords)
        
        for user_kw in user_keywords:
            # 정확한 매칭
            if user_kw in admin_keywords:
                matches += 1
            else:
                # 부분 매칭 (포함 관계)
                for admin_kw in admin_keywords:
                    if user_kw in admin_kw or admin_kw in user_kw:
                        matches += 0.5
                        break
        
        return matches / total_keywords if total_keywords > 0 else 0.0
    
    def find_matching_admins(self, user_input: str, threshold: float = 0.1, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        사용자 입력에 매칭되는 담당자 찾기
        
        Args:
            user_input: 사용자 입력 텍스트
            threshold: 최소 매칭 점수 임계값
            max_results: 최대 결과 개수
            
        Returns:
            매칭된 담당자 리스트 (점수순 정렬)
        """
        user_keywords = self.extract_keywords(user_input)
        
        if not user_keywords:
            return []
        
        # 각 담당자의 매칭 점수 계산
        scored_admins = []
        for admin in self.admins_data:
            score = self.calculate_match_score(user_keywords, admin)
            if score >= threshold:
                scored_admins.append((admin, score))
        
        # 점수순으로 정렬 (내림차순)
        scored_admins.sort(key=lambda x: x[1], reverse=True)
        
        # 최대 결과 개수만큼 반환
        return [admin for admin, score in scored_admins[:max_results]]
    
    def get_suggestions(self, partial_input: str) -> List[str]:
        """
        부분 입력에 대한 검색 제안어 생성
        
        Args:
            partial_input: 부분 입력 텍스트
            
        Returns:
            제안어 리스트
        """
        suggestions = set()
        cleaned_input = self.clean_text(partial_input)
        
        # 모든 담당자의 키워드에서 제안어 찾기
        for admin in self.admins_data:
            # 업무 범위에서 제안어 추출
            for responsibility in admin.get('responsibilities', []):
                if cleaned_input in responsibility.lower():
                    suggestions.add(responsibility)
            
            # 키워드에서 제안어 추출
            if 'keywords' in admin:
                for keyword in admin['keywords']:
                    if cleaned_input in keyword.lower():
                        suggestions.add(keyword)
        
        return sorted(list(suggestions))[:10]  # 최대 10개 제안어
