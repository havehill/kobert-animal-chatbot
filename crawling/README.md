### 크롤링 코드 원출처
: https://github.com/catSirup/naver_kin_crawling

### 수정 사항 
0. **selenium 버전 업데이트로 인해 변경된 명령어 수정**
  - driver.find_elements_by_class_name => driver.find_elements(By.CLASS_NAME,)
2. **keyword 검색이 아닌 네이버 수의학 전문가 답변 크롤링**
  - crawling_expert_list : 수의학 전문가들 qna 사이트 url 크롤링
  - crawling_expert : expert_list로 얻은 url에 대해 모든 전문가들의 답변 페이지 url 크롤링
  - crawling_qna : crawling_expert 로 얻은 url에 대해 제목,본문,답변 크롤링
3. **빠르고 반복적인 크롤링으로 인해 생기는 Exception 처리**
  - find_element 문마다 try-except, WebDriverWait().until() 추가

### 크롤링 데이터 이상사항
0. 트래픽 때문에 제목이나 질문에 Exception 처리 + 중복 된 것이 많음  

위에 행은 제목, 질문 정상적으로 나왔는데 밑에 행은 제목이나 질문이 Exception 돼서 중복되어 저장된 경우가 많음.    

=> 답변은 이상하게 다 정상이라 답변 기준으로 중복 제거하면  될 거 같음

1.  제목은 정상인데 질문은 Exception 처리된 것은 작성자가 질문에다가 본문 내용 써놓고 본문은 비워놓은 경우일 수 있음


