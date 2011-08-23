Slug: coffeescript 
Category: 개발 
Title: 커피스크립트
Date: 2011-08-23
Status: draft

[더글러스 크록포드](http://javascript.crockford.com/popular.html) 아저씨가 [어떤 글](http://javascript.crockford.com/popular.html)에서 말했듯이, 자바스크립트는 지금 가장 중요한 언어 중의 하나가 되었다. [크롬 OS](http://en.wikipedia.org/wiki/Google_Chrome_OS)는 자바스크립트로 작성된 웹 앱들로 운영체제의 네이티브 앱을 대체하려고 들고, 그것도 모자라 [node.js](http://nodejs.org/)는 서버도 자바스크립트로 작성하려고 한다. 지난 2년 사이에 꽤나 유명해진 문서 기반 데이터베이스인 [MongoDB](http://www.mongodb.org/)는 아예 쉘에서 자바스크립트를 지원한다.

이렇게 자바스크립트의 사용이 점점 늘어가지만 자바스크립트에는 여러 고질적인 문제들이 있다. 자바스크립트의 대표적인 옹호자 중 하나인 더글러스 옹께서도 위에서 언급한 글에서 "JavaScript is an astonishing language, in the very worst sense. (자바스크립트는 정말 끝내주는 언어다. 안 좋은 의미로.)" 라고 할 정도니 말 다 했다. DOM에의 의존성 등의 거창한 이유를 언급하지 않아도 자바스크립트에는 너무 많은 함정이 널려 있다. 

얼마 전에 자바스크립트의 함정들에 대해 다루는 [좋은 글](http://blog.cheol.net/post/9208860498)을 보았다. 사실 이런 글들은 엄청 많은데 [여기](http://www.fitzblog.com/bid/2127/Nine-Javascript-Gotchas)나 [여기](http://stackoverflow.com/questions/2749952/what-are-the-top-javascript-pitfalls)도 한번씩 보도록 하자. 

이런 점들을 잘 알고 피해가는 것도 중요하지만, 더 좋은 방법은 [성공의 함정에 빠지도록](http://www.codinghorror.com/blog/2007/08/falling-into-the-pit-of-success.html) 도와 주는 언어를 사용하는 것이라고 생각한다.

그런 목적으로 등장한 언어가 있으니 바로 [커피스크립트](http://jashkenas.github.com/coffee-script/)다. 커피스크립트는 **자바스크립트로 컴파일되는** 스크립트 언어로써, 단순히 [syntactic sugar](http://en.wikipedia.org/wiki/Syntactic_sugar)라고 생각할 수도 있지만 다른 언어에 익숙한 개발자가 제정신을 유지하고 자바스크립트를 작성할 수 있도록 많은 기능들을 지원한다. [커피스크립트 홈페이지](http://jashkenas.github.com/coffee-script/)에 잘 설명되어 있지만, 우선 개인적으로 느끼기에 큰 장점들만 다뤄 보겠다.

### == 와 ===

위 글에서도 언급했다시피 자바스크립트의 `==` 는 [Transitive Relation](http://en.wikipedia.org/wiki/Transitive_relation)이 아니다. `a == b`이고 `b == c`이더라도 `a == c`이지 않을 수 있다는 말이다. 제 정신을 가진 사람이라면 이런 연산자를 사용하고 싶지 않을 것이다..

커피스크립트에서는 `==` 연산과 `!=` 연산을 자동으로 `===`와 `!==`로 컴파일한다. 만악의 근원인 자바스크립트의 `==` 연산자는 아예 지원하지 않는다.

### 루프 안에서 클로저 만들기

자바스크립트에서 루프 안에서 변화하는 변수의 값에 의존하는 클로저를 만들기 위해서는 아래와 같은 코드를 써야 한다.

	#!javascript
	function f() {
		for (var i = 0; i < 3; i++) {
			setTimeout((function (i) {
				return function () {
					console.log(i);
				};
			})(i), 50);
		}
	}

울고 싶다.

다행히 커피스크립트에서는 이와 같은 일을 쉽게 해 주는 이디엄을 지원한다. `do(i)`는 `i`의 값을 새 익명함수 내부로 옮겨 준다.

	#!coffeescript
	f = ->
		for i in [0..2]
			do (i) ->
				alrt = -> alert(i)
				setTimeout(alrt, 50)

### 전역 네임스페이스 보존

커피스크립트는 컴파일할 때 모든 코드를 익명 함수 내부에 넣어 준다. 따라서 다른 스크립트 간에 변수명이나 함수명이 충돌할 여지가 없다. 전역 변수를 사용할 경우 `window.xxx` 같이 명시적으로 `window` 객체에 추가할 것을 권하고 있다(이건 정말 좋은 선택인지 잘 모르겠다. -\_-;).

### 인간적인 for 문

자바스크립트에서 모든 객체는 사실 [연관 배열](http://en.wikipedia.org/wiki/Associative_array)이다. 다시 말해 자바스크립트는 객체와 연관 배열을 구분하지 않는다.... 이것만으론 별 문제가 아닌 듯 싶지만

	#!javascript
	Object.prototype.help = function() { console.log("me"); };
	var sqr = {1: 2, 2: 4, 3: 9};
	for(var i in sqr) console.log(i, sqr[i]);

해보면 1, 2, 3과 함께 help가 나오는 것을 볼 수 있다..... 어? 이 문제를 방지하기 위해서는 `for`문 안에서 `hasOwnProperty`를 이용해 해당 키가 프로토타입의 키인지 일일이 확인해 줄 필요가 있다..

다행히 커피스크립트에서는 `for own`이라는 문법을 통해 이것을 간단하게 해 준다.

### 일반적인 클래스 선언 문법

자바스크립트는 [프로토타입 기반 타입시스템](http://en.wikipedia.org/wiki/Prototype-based_programming)을 지원하는데, 이건 아주 강력하지만 상속 기반 OOP에 찌든 나의 오염된 마음에는

	#!javascript
	PlayingField.prototype.getCardDirection = function(player) { .. }
	PlayingField.prototype.getCardPosition = function(player, cards, index) { .. }
	PlayingField.prototype.clear = function() { .. }

이렇게 객체를 만드는 것은 맘에 들지 않았다. 메소드 선언이 여기저기 흩어져 있는 것도 맘에 들지 않았고. 커피스크립트는 좀더 일반적인 클래스 형태로 메소드들을 선언할 수 있게 해준다. 물론 기존 클래스의 프로토타입을 변경하는 문법도 별개로 지원한다.

### this 유지

자바스크립트에서는 this 변수를 지원하는데, 마지막으로 핸들러가 호출된 DOM 객체를 가리킨다. 따라서 다른 DOM 객체에 핸들러를 지정하면서 현재 this 를 쓰고 싶으면 클로저 내의 다른 변수에 저장해 두던가 `apply`를 써서 직접 덮어씌워 줘야 한다.

커피스크립트에서는 함수를 선언할 때 쓰는 `->` 대신 `=>` 를 씀으로써 이것을 자동화할 수 있게 해 준다.

### 각종 편리한 신택틱 슈거

한번 중독되면 벗어날 수 없는 array comprehension이나 assignment destructuring 등을 지원한다. 파이썬에서 지원하는 chained comparison도 종종 유용하다.

### 스코프 관리

그렇다고 커피스크립트에도 주의할 점이 없는 것은 아니다. 자바스크립트와 다른 변수 스코프 규칙은 주의해야 한다.

커피스크립트에서는 사용자가 `var` 키워드를 써서 변수의 스코프를 정의할 수 없으며, 모든 변수는 해당 변수가 사용된 가장 상위 위치에 선언된다. 따라서 해당하는 이름을 갖는 전역변수가 있을 경우 지역변수가 선언되는 것이 아니라 전역변수를 덮어씌우게 된다. 

아 졸려서 이쯤 써야겠다.. 어쨌건 커피스크립트를 도전해 볼 마음이 든 사람들이 많이 생기길 바란다. >.<
