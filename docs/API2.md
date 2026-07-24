# 요청URL

# 영화인 목록

* http://www.kobis.or.kr/kobisopenapi/webservice/rest/people/searchPeopleList.json

# 요청변수(Request Parameter)

요청 변수	값	설명

key	문자열(필수)	발급받은키 값을 입력합니다.

curPage	문자열	현재 페이지를 지정합니다.(default : “1”)

itemPerPage	문자열	결과 ROW 의 개수를 지정합니다.(default : “10”)

peopleNm	문자열	영화인명으로 조회합니다.

filmoNames	문자열	필모리스트로 조회합니다.

# 출력결과(Response Element)

출력 결과	값	설명

peopleCd	문자열	영화인 코드를 출력합니다.

peopleNm	문자열	영화인명을 출력합니다.

peopleNmEn	문자열	영화인명(영문)을 출력합니다.

repRoleNm	문자열	분야를 출력합니다.

filmoNames	문자열	필모리스트를 출력합니다.



# 영화인 상세정보

* http://www.kobis.or.kr/kobisopenapi/webservice/rest/people/searchPeopleInfo.json

# 요청변수(Request Parameter)

요청 변수	값	설명

key	문자열(필수)	발급받은키 값을 입력합니다.

peopleCd	문자열	영화인코드를 지정합니다.

# 출력결과(Response Element)

출력 결과	값	설명

peopleCd	문자열	영화인 코드를 출력합니다.

peopleNm	문자열	영화인명을 출력합니다.

peopleNmEn	문자열	영화인명(영문)을 출력합니다.

sex	문자열	성별을 출력합니다.

repRoleNm	문자열	영화인 분류명을 출력합니다.

filmos	문자열	영화인 필모를 나타냅니다.

movieCd	문자열	참여 영화코드를 출력합니다.

movieNm	문자열	참여 영화명을 출력합니다.

moviePartNm	문자열	참여분야를 나타냅니다.

homepages	문자열	관련 URL을 출력합니다.

