# 요청URL

# 박스오피스

* http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchWeeklyBoxOfficeList.json

# 요청변수(Request Parameter)

요청 변수	값	설명

key	문자열(필수)	발급받은키 값을 입력합니다.

targetDt	문자열(필수)	조회하고자 하는 날짜를 yyyymmdd 형식으로 입력합니다.

weekGb	문자열	주간/주말/주중을 선택 입력합니다. “0” : 주간 (월\~일), “1” : 주말 (금\~일) (default), “2” : 주중 (월\~목)

itemPerPage	문자열	결과 ROW 의 개수를 지정합니다.(default : “10”, 최대 : “10”)

multiMovieYn	문자열	다양성 영화/상업영화를 구분지어 조회할 수 있습니다. “Y” : 다양성 영화 “N” : 상업영화 (default : 전체)

repNationCd	문자열	한국/외국 영화별로 조회할 수 있습니다. “K: : 한국영화 “F” : 외국영화 (default : 전체)

wideAreaCd	문자열	상영지역별로 조회할 수 있으며, 지역코드는 공통코드 조회 서비스에서 “0105000000” 로서 조회된 지역코드입니다. (default : 전체)

# 출력결과(Response Element)

출력 결과	값	설명

boxofficeType	문자열	박스오피스 종류를 출력합니다.

showRange	문자열	대상 상영기간을 출력합니다.

yearWeekTime	문자열	조회일자에 해당하는 연도와 주차를 출력합니다.(YYYYIW)

rnum	문자열	순번을 출력합니다.

rank	문자열	해당일자의 박스오피스 순위를 출력합니다.

rankInten	문자열	전일대비 순위의 증감분을 출력합니다.

rankOldAndNew	문자열	랭킹에 신규진입여부를 출력합니다. “OLD” : 기존 , “NEW” : 신규

movieCd	문자열	영화의 대표코드를 출력합니다.

movieNm	문자열	영화명(국문)을 출력합니다.

openDt	문자열	영화의 개봉일을 출력합니다.

salesAmt	문자열	해당일의 매출액을 출력합니다.

salesShare	문자열	해당일자 상영작의 매출총액 대비 해당 영화의 매출비율을 출력합니다.

salesInten	문자열	전일 대비 매출액 증감분을 출력합니다.

salesChange	문자열	전일 대비 매출액 증감 비율을 출력합니다.

salesAcc	문자열	누적매출액을 출력합니다.

audiCnt	문자열	해당일의 관객수를 출력합니다.

audiInten	문자열	전일 대비 관객수 증감분을 출력합니다.

audiChange	문자열	전일 대비 관객수 증감 비율을 출력합니다.

audiAcc	문자열	누적관객수를 출력합니다.

scrnCnt	문자열	해당일자에 상영한 스크린수를 출력합니다.

showCnt	문자열	해당일자에 상영된 횟수를 출력합니다.에러메시지(에러코드별 조치방안 확인)



# 영화목록

* http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json

# 요청변수(Request Parameter)

요청 변수	값	설명

key	문자열(필수)	발급받은키 값을 입력합니다.

curPage	문자열	현재 페이지를 지정합니다.(default : “1”)

itemPerPage	문자열	결과 ROW 의 개수를 지정합니다.(default : “10”)

movieNm	문자열	영화명으로 조회합니다. (UTF-8 인코딩)

directorNm	문자열	감독명으로 조회합니다. (UTF-8 인코딩)

openStartDt	문자열	YYYY형식의 조회시작 개봉연도를 입력합니다.

openEndDt	문자열	YYYY형식의 조회종료 개봉연도를 입력합니다.

prdtStartYear	문자열	YYYY형식의 조회시작 제작연도를 입력합니다.

prdtEndYear	문자열	YYYY형식의 조회종료 제작연도를 입력합니다.

repNationCd	문자열	N개의 국적으로 조회할 수 있으며, 국적코드는 공통코드 조회 서비스에서 “2204” 로서 조회된 국적코드입니다. (default : 전체)

movieTypeCd	문자열	N개의 영화유형코드로 조회할 수 있으며, 영화유형코드는 공통코드 조회 서비스에서 “2201”로서 조회된 영화유형코드입니다.(default: 전체)

# 출력결과(Response Element)

출력 결과	값	설명

movieCd	문자열	영화코드를 출력합니다.

movieNm	문자열	영화명(국문)을 출력합니다.

movieNmEn	문자열	영화명(영문)을 출력합니다.

prdtYear	문자열	제작연도를 출력합니다.

openDt	문자열	개봉일을 출력합니다.

typeNm	문자열	영화유형을 출력합니다.

prdtStatNm	문자열	제작상태를 출력합니다.

nationAlt	문자열	제작국가(전체)를 출력합니다.

genreAlt	문자열	영화장르(전체)를 출력합니다.

repNationNm	문자열	대표 제작국가명을 출력합니다.

repGenreNm	문자열	대표 장르명을 출력합니다.

directors	문자열	영화감독을 나타냅니다.

peopleNm	문자열	영화감독명을 출력합니다.

companys	문자열	제작사를 나타냅니다.

companyCd	문자열	제작사 코드를 출력합니다.

companyNm	문자열	제작사명을 출력합니다.



# 영화 상세정보

* http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json

# 요청변수(Request Parameter)

요청 변수	값	설명

key	문자열(필수)	발급받은키 값을 입력합니다.

movieCd	문자열(필수)	영화코드를 지정합니다.

# 출력결과(Response Element)

출력 결과	값	설명

movieCd	문자열	영화코드를 출력합니다.

movieNm	문자열	영화명(국문)을 출력합니다.

movieNmEn	문자열	영화명(영문)을 출력합니다.

movieNmOg	문자열	영화명(원문)을 출력합니다.

prdtYear	문자열	제작연도를 출력합니다.

showTm	문자열	상영시간을 출력합니다.

openDt	문자열	개봉연도를 출력합니다.

prdtStatNm	문자열	제작상태명을 출력합니다.

typeNm	문자열	영화유형명을 출력합니다.

nations	문자열	제작국가를 나타냅니다.

nationNm	문자열	제작국가명을 출력합니다.

genreNm	문자열	장르명을 출력합니다.

directors	문자열	감독을 나타냅니다.

peopleNm	문자열	감독명을 출력합니다.

peopleNmEn	문자열	감독명(영문)을 출력합니다.

actors	문자열	배우를 나타냅니다.

peopleNm	문자열	배우명을 출력합니다.

peopleNmEn	문자열	배우명(영문)을 출력합니다.

cast	문자열	배역명을 출력합니다.

castEn	문자열	배역명(영문)을 출력합니다.

showTypes	문자열	상영형태 구분을 나타냅니다.

showTypeGroupNm	문자열	상영형태 구분을 출력합니다.

showTypeNm	문자열	상영형태명을 출력합니다.

audits	문자열	심의정보를 나타냅니다.

auditNo	문자열	심의번호를 출력합니다.

watchGradeNm	문자열	관람등급 명칭을 출력합니다.

companys	문자열	참여 영화사를 나타냅니다.

companyCd	문자열	참여 영화사 코드를 출력합니다.

companyNm	문자열	참여 영화사명을 출력합니다.

companyNmEn	문자열	참여 영화사명(영문)을 출력합니다.

companyPartNm	문자열	참여 영화사 분야명을 출력합니다.

staffs	문자열	스텝을 나타냅니다.

peopleNm	문자열	스텝명을 출력합니다.

peopleNmEn	문자열	스텝명(영문)을 출력합니다.

staffRoleNm	문자열	스텝역할명을 출력합니다.



