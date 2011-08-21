Slug: spell-correct
Category: 알고리즘
Title: 번역: 맞춤법 검사기 작성하기
Date: 2011-08-20
Status: draft

블로그 개장 기념으로 역시 내가 좋아하는 또다른 에세이 중 하나인 [Peter Norvig](http://norvig.com/)의 [How to Write a Spelling Corrector](http://norvig.com/spell-correct.html)를 번역해 보았다. 영문을 대상으로 한 맞춤법 검사기라서 국문에 그대로 적용할 수는 없지만, 맞춤법 검사기에 필요한 이론을 잘 설명하고 있고 코드가 간결하므로 꽤나 흥미롭게 읽을 수 있다.

번역상의 오탈자는 [번역자](mailto:theyearlyprophet@gmail.com) 에게 신고 바란다.

---

지난 주에 나는 구글이 검색어의 맞춤법을 그렇게 빠르고 정확하게 교정하는 것이 놀랍다는 말을 두 명의 친구들(딘과 빌)로부터 각각 들었다. 실제로 구글에 [마춤법](http://www.google.com/search?sourceid=chrome&ie=UTF-8&q=%EB%A7%88%EC%B6%A4%EB%B2%95)이라고 검색해 보면 대략 0.1초 안에 *이것을 찾으셨나요? [맞춤법](http://www.google.co.kr/#hl=ko&newwindow=1&sa=X&ei=qD5QTrCSDunk0QG5rPCCBw&ved=0CCoQBSgA&q=%EB%A7%9E%EC%B6%A4%EB%B2%95&spell=1&bav=on.2,or.r_gc.r_pw.&fp=c16bbd82e235a9c3&biw=837&bih=1080)* 같은 결과를 받게 된다. (야후나 마이크로소프트의 검색 결과도 다르지 않다.) 사실 나는 그런 말을 들어서 놀랐다. 굉장히 유능한 엔지니어이자 수학자인 딘과 빌 같은 사람들은 맞춤법 교정과 같은 통계적 언어 처리에 대해서는 충분히 잘 알 것이라고 생각했기 때문이다. 하지만 그들이 이런 주제에 대해 딱히 알아야 할 이유는 없다: 그들의 지식이 문제가 아니라 내 생각이 문제인 셈이다.

두 친구들 외에도 많은 사람들에게 도움이 되기를 바라며 맞춤법 검사기의 동작 과정에 대해 설명해 보겠다. 물론 실제 서비스에 사용되는 철자법 검사기의 내부는 여기에서 전부 다루기에는 너무 복잡하다([여기](http://static.googleusercontent.com/external_content/untrusted_dlcp/research.google.com/en/us/pubs/archive/36180.pdf)와 [여기](http://citeseerx.ist.psu.edu/viewdoc/download;jsessionid=52A3B869596656C9DA285DCE83A0339F?doi=10.1.1.146.4390&rep=rep1&type=pdf)에 관련된 자료가 좀 있다). 그러니 이 글에서는 그 원리를 이해하는 데 도움이 될 만한 간단하고 짧은 철자법 검사기의 동작 원리를 우선 설명해 보겠다. 이 철자법 검사기는 코드가 한 페이지도 안 될 정도로 아주 짧고, 80퍼센트에서 90퍼센트의 정확률을 보이며 초당 최소 10단어 정도는 처리할 수 있다.

다음 21줄의 [파이썬](http://python.org/) 2.5 코드로 완전한 맞춤법 검사기를 구현할 수 있다.

	#!python
	import re, collections

	def words(text): return re.findall('[a-z]+', text.lower()) 

	def train(features):
		model = collections.defaultdict(lambda: 1)
		for f in features:
			model[f] += 1
		return model

	NWORDS = train(words(file('big.txt').read()))

	alphabet = 'abcdefghijklmnopqrstuvwxyz'

	def edits1(word):
	   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
	   deletes    = [a + b[1:] for a, b in splits if b]
	   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
	   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
	   inserts    = [a + c + b     for a, b in splits for c in alphabet]
	   return set(deletes + transposes + replaces + inserts)

	def known_edits2(word):
		return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

	def known(words): return set(w for w in words if w in NWORDS)

	def correct(word):
		candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
		return max(candidates, key=NWORDS.get)

위 코드에 정의된 `correct` 함수는 단어를 입력받아 가장 그럴듯한 정정 결과를 반환한다. 예를 들면 다음과 같다.

	#!python
	>>> correct('speling')
	'spelling'
	>>> correct('korrecter')
	'corrector'

위 코드에 보인 `edits1` 함수는 처음에 내가 작성한 것이 아니라 다리우스 베이컨이 제시한 방법의 변형이다. 이 방법이 내가 원래 작성했던 방법보다 더 명료한 것 같아 이와 같이 바꿨다. 다리우스는 함수에 있던 버그도 잡아 주었다.

## 동작 원리: 확률 이론

이 코드의 동작 원리를 설명하기 위해서는 이론 얘기를 조금 해야 한다. 우리가 하려는 일은 단어가 주어졌을 때 가장 가능성이 높은 교정 결과를 찾아내는 것이다(물론 이 교정 결과는 원래 단어일 수도 있다). 물론 모든 경우에 항상 옳은 결과를 찾아낼 수 있는 방법은 없다(예를 들어 `lates`가 검색어로 주어졌다면, `late`로 교정해야 할 지, `latest`로 교정해야 할 지 알 수 없기 때문이다). 따라서 원래 단어 w가 주어졌을 때 각 교정 결과 후보 c에 조건부 확률 값을 배정하고 그 중 확률을 최대화하는 후보를 선택하는 것으로 하자. 이런 c를 다음과 같이 쓸 수 있다.

> argmax<sub>c</sub> P(c|w)

[베이즈 정리](http://ko.wikipedia.org/wiki/%EB%B2%A0%EC%9D%B4%EC%A6%88_%EC%A0%95%EB%A6%AC)에 의하면 이것을 다음과 같이 고쳐 쓸 수도 있다.

> argmax<sub>c</sub> P(w|c) P(c) / P(w)

이 식에서 P(w)는 모든 후보 c에 대해 같은 값이므로 생략하도록 하자. 그러면 다음 식을 얻을 수 있다.

> argmax<sub>c</sub> P(w|c) P(c)

이 식을 세 부분으로 나눌 수 있다. 오른쪽에서부터 설명해 보자.

1. P(c)는 w와 상관 없는 결과 후보 c 자체의 출현 확률을 나타낸다. 이것은 우리가 다루는 언어에 따라 달라지므로, 이것을 언어 모델(language model)이라고 부른다. 예를 들어 "영어 문장에서 c가 출현할 확률은 얼마나 되는가?" 라는 질문에 답하는 과정이 언어 모델인 셈이다. 잘 작성된 언어 모델에서 the가 출현할 확률 P("the")는 상대적으로 꽤 출현 확률이 높겠지만, P("zxzxzxzyyy")의 출현 확률은 거의 없을 것이다.
2. P(w|c)는 검색어를 입력한 사람이 c를 치려다가 w를 입력할 확률을 나타낸다. 이것을 오류 모델(error model)이라고 부른다. 
3. argmax<sub>c</sub>는 가능한 모든 c에 대해 두 확률의 곱을 계산해 보고, 곱을 최대화하는 결과를 반환하라는 것을 의미한다.

이쯤 되어서 왜 P(c|w)같은 간단한 식을 그냥 두지 않고 아래 있는 더 복잡한 수식으로 바꾸나? 하는 의문이 들 법도 하다. 왜냐면 P(c|w)를 계산하기 위해서는 두 개의 요소를 고려해야 하는데, 이들을 따로 나눠 이름을 붙이면 더 다루기 수월해지기 때문이다. 예를 들어 w="thew"가 입력되었다고 하자. 그럼 두 개의 후보 c="the"와 c="thaw" 중 더 확률 P(c|w)가 높은 것은 어느 쪽일까? 흠, a를 e로 바꾸기만 하면 되니 "thaw"가 그럴듯해 보인다. 하지만 "the"도 그럴듯해 보이는 것이, the는 영어에서 굉장히 흔하게 등장하는 단어인데다 e를 치면서 실수로 옆에 있는 w를 치는 일도 충분히 가능하기 때문이다. 이렇듯 P(c|w)를 직접 계산하려고 해도 위에서 언급한 두 개의 요소를 모두 고려해야 하므로, 차라리 명시적으로 이들을 분리하고 이름 붙이는 것이 낫다. 

자, 이제 프로그램의 동작 원리에 대해 설명해 보자. 먼저 P(c)를 계산하는 부분에 대해 이야기해 보겠다. 이 코드는 대략 백만 개의 단어를 포함하는 커다란 텍스트 파일 [big.txt](http://norvig.com/big.txt)를 읽어들인다. 이 파일은 [구텐베르크 프로젝트](http://www.gutenberg.org/wiki/Main_Page)에 공개된 책 몇 권, [Wiktionary](http://en.wiktionary.org/wiki/Wiktionary:Frequency_lists), 그리고 [British National Corpus](http://www.kilgarriff.co.uk/bnc-readme.html)에서 얻은 가장 흔한 영단어 목록을 합친 것이다. (이 코드를 처음 작성할 때 나는 귀국 비행기 안에 있었는데, 그 때 내 랩탑에는 셜록 홈즈 전권밖에 없었다. 나중에 문서를 추가하는 것이 정확도에 도움이 되지 않을 때까지 다른 여러 문서를 추가했다. 자세한 것은 평가 섹션을 참조하라.)

`big.txt`를 읽어들인 후에는 텍스트에 개별 단어들을 `words` 함수를 써서 추출한다. 이 함수는 각 연속된 알파벳 문자열들을 단어로 분리하며, 모든 알파벳을 소문자로 변환한다. 따라서 "The"가 "the"로 변환되고, "don't" 는 "don"과 "t" 두 개의 단어가 된다. 파일을 읽어들인 뒤에는 `train` 함수에서 확률 모델을 훈련하는데, 말은 거창하지만 사실 각 단어가 몇 번이나 등장하는지 세어보는 것이다. 다음 코드를 참조하자.

	#!python
	def words(text): return re.findall('[a-z]+', text.lower()) 

	def train(features):
		model = collections.defaultdict(lambda: 1)
		for f in features:
			model[f] += 1
		return model

	NWORDS = train(words(file('big.txt').read()))

이 시점에서 `NWORD[w]`는 파일 안에서 단어 `w`가 몇 번이나 출현했는지를 나타낸다. 이 때 따로 신경써야 할 점이 하나 있는데, 바로 새로운 단어들이다. 우리가 수집한 자료에 등장하지 않는 단어가 정답인 경우엔 어떻게 해야 할까? 우리가 본 적이 없다고 해서 반드시 틀린 단어라고 가정할 수는 없다. 이럴 때 쓸 수 있는 일반적인 접근 방법이 몇 가지 있는데, 여기서는 가장 쉬운 것을 택하자. 바로 새로운 단어들은 모두 한 번 봤다고 가정하는 것이다. 이와 같은 기법은 단어들의 확률 분포에서 0이어야 할 부분들을 최소값인 1로 늘림으로써 분포를 평평하게 하는 효과가 있어서, 일반적으로 **평활법(smoothing)**이라고 부른다. 이것은 파이썬의 일반 `dict` 구조체 (다른 언어에서는 해시 테이블이라고 흔히 부르는) 대신 `collections.defaultdict`를 사용하는 방법으로 쉽게 구현할 수 있다. 이 클래스는 `dict`와 똑같이 작동하지만 처음 보는 키의 기본 키를 우리가 지정할 수 있다는 차이점이 있다. 여기서는 1을 사용한다.

이제 단어 w가 주어졌을 때 가능한 교정 결과 후보들을 세어보는 과정을 다뤄 보자. 일반적으로 두 단어가 얼마나 비슷한가를 나타내는 기준으로 **편집 거리(edit distance)**라는 것이 있다. 이것은 한 단어를 다른 단어로 바꾸기 위해 필요한 연산의 최소 수를 의미한다. 한 연산은 한 글자를 지우거나(삭제), 인접한 두 글자를 바꾸거나(뒤집기), 한 글자를 다른 글자로 바꾸거나(변경), 새 글자를 추가할 수(삽입) 있다. 어떤 단어 w가 주어질 때 w에서 편집 거리가 1인 단어들을 모두 생성하는 함수를 아래와 같이 구현할 수 있다.

	#!python
	def edits1(word):
	   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
	   deletes    = [a + b[1:] for a, b in splits if b]
	   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
	   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
	   inserts    = [a + c + b     for a, b in splits for c in alphabet]
	   return set(deletes + transposes + replaces + inserts)

이 함수의 결과 집합은 꽤나 클 수 있다. 단어의 길이가 n이라고 하면, n개의 삭제, n-1개의 뒤집기, 26n개의 변경, 26(n+1)개의 삽입 연산이 가능하므로 전부 하면 54n+25개의 후보가 있을 수 있다 (대개 이 중 몇 개는 중복되겠지만). 예를 들어, `len(edits1('something'))` 으로 `edits1('something')`의 원소의 수를 세어 보면 494를 얻을 수 있다.

철자법 교정에 관한 논문들에서는 80% 에서 95% 의 철자법 오타 결과는 원문과 편집 거리가 1밖에 되지 않는다고 흔히 말한다. 나는 개발을 위해 270개의 오타 모음을 간단히 만들어서 확인해 보았는데, 이 중 원문과의 편집 거리가 1인 오타는 76%밖에 되지 않았다. 내가 수집한 오타들이 일반적인 오타들보다 어려울 가능성도 있지만, 이것으로는 영 만족스럽지 않아서 편집 거리 2인 단어들도 검사하기로 결정했다. `edits1`의 결과 단어들에 `edits1`을 한번씩 다시 적용하면 이것을 쉽게 할 수 있다.

	#!python
	def edits2(word):
		return set(e2 for e1 in edits1(word) for e2 in edits1(e1))

이걸 작성하는 것은 간단하지만, 이제는 계산량이 꽤나 많아지게 된다. `len(edits2('something'))`는 무려 114,324가 된다. 그렇지만 이 경우 대부분의 오타를 감안할 수 있게 된다. 270개의 예제에서 원문과의 편집 거리가 2 이상인 예제는 고작 3개밖에 없었다. 예제의 98.9%는 `edits2`로 커버할 수 있다는 말이므로, 나에겐 이것으로 충분하다. 편집 거리 3 이상인 단어들을 만들 필요는 없으므로 간단한 최적화를 하도록 하자. 모든 후보를 생성하는 대신, 실제로 우리가 알고 있는 단어들만을 반환하는 것이다. `known_edits2` 함수가 이와 같은 작업을 한다:

	#!python
	def known_edits2(word):
		return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

이렇게 코드를 바꾸면 `known_edits2('something')`은 `edits2`의 11만개 대신 이제 고작 smoothing, seething, something, soothing 의 4개 단어만을 반환한다. 이 최적화로 수행 시간의 10% 정도를 절약할 수 있었다.

이제 남은 문제는 오류 모델 P(w|c)를 만드는 부분이다. 내겐 이 부분이 특히 까다로웠는데, 비행기 안에서 인터넷도 쓸 수 없이 앉아 있으니 모델을 생성할 훈련용 데이터를 구할 수도 없는 노릇이었다. 물론 주먹구구로 모델을 만들 수는 있다. 두 개의 자음을 서로 헷갈리는 것보다 모음 두 개를 헷갈릴 가능성이 더 크고, 첫 글자는 다른 글자들보다 틀릴 가능성이 적다거나 하는 식으로. 하지만 이 주장을 뒷받침할 자료는 없었고, 때문에 간단한 지름길을 택하기로 했다: 입력 단어에서 편집 거리가 1인 모든 단어는 편집 거리가 2인 단어보다 무한히 더 가능성이 높고, 편집 거리가 0이고 우리가 알고 있는 단어마다 무한히 가능성이 낮다고 주장하는 것이다. 여기서 우리가 알고 있는 단어란 언어 모델, 즉 훈련용 데이터에 포함된 단어를 나타낸다. 이 전략을 다음과 같이 구현해 볼 수 있다.

	#!python
	def known(words): return set(w for w in words if w in NWORDS)

	def correct(word):
		candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
		return max(candidates, key=lambda w: NWORDS[w])

`correct` 함수는 주어진 입력 `word`에서 편집 거리가 가장 가까운 알려진 단어들의 목록을 `candidates`에 저장한다. 그 후에는 `NWORDS` 모델에 의해 알려진 대로 P(c)가 가장 큰 단어를 반환한다.

## 평가

이제 프로그램이 얼마나 정확하게 동작하는지 확인해 볼 차례다. 나는 비행기 안에서 몇 개의 예제를 테스트해 보았는데, 그럴 듯 했다. 비행기가 내린 후에 나는 로저 미튼의 [버크벡 철자법 오류 코퍼스](http://ota.ahds.ac.uk/texts/0643.html)를 옥스퍼드 문헌 목록에서 다운받았다. 이 코퍼스에서 두 개의 테스트 셋을 뽑아냈는데, 첫 번째는 개발하는 데 사용했다. 다시 말해 내가 프로그램을 짜는 중에 이 셋을 볼 수 있다는 것이다. 두 번째는 최종 테스트 셋으로, 내가 볼 수도 없고 프로그램이 틀렸을 경우에도 확인할 수 없다는 것이다. 이렇게 두 개의 테스트 셋을 준비하는 것은 좋은 습관이다. 이와 같은 습관이 없이 모든 테스트 셋을 보면서 프로그램을 개발하면, 이 테스트 셋에만 적합하도록 프로그램을 튜닝한 뒤 프로그램의 성능이 실제보다 우수하다고 착각하기 십상이다. 아래는 이 두 종류의 테스트의 일부와 이들을 수행하는 함수의 구현을 보여준다. 코드의 나머지와 전체 테스트를 보고 싶으면 [spell.py](http://norvig.com/spell.py)를 참조하라.

	#!python
	tests1 = { 'access': 'acess', 'accessing': 'accesing', 'accommodation':
		'accomodation acommodation acomodation', 'account': 'acount', ...}

	tests2 = {'forbidden': 'forbiden', 'decisions': 'deciscions descisions',
		'supposedly': 'supposidly', 'embellishing': 'embelishing', ...}

	def spelltest(tests, bias=None, verbose=False):
		import time
		n, bad, unknown, start = 0, 0, 0, time.clock()
		if bias:
			for target in tests: NWORDS[target] += bias
		for target,wrongs in tests.items():
			for wrong in wrongs.split():
				n += 1
				w = correct(wrong)
				if w!=target:
					bad += 1
					unknown += (target not in NWORDS)
					if verbose:
						print '%r => %r (%d); expected %r (%d)' % (
							wrong, w, NWORDS[w], target, NWORDS[target])
		return dict(bad=bad, n=n, bias=bias, pct=int(100. - 100.*bad/n), 
					unknown=unknown, secs=int(time.clock()-start) )

	print spelltest(tests1)
	print spelltest(tests2) ## only do this after everything is debugged

This gives the following output:

{'bad': 68, 'bias': None, 'unknown': 15, 'secs': 16, 'pct': 74, 'n': 270}
{'bad': 130, 'bias': None, 'unknown': 43, 'secs': 26, 'pct': 67, 'n': 400}

So on the development set of 270 cases, we get 74% correct in 13 seconds (a rate of 17 Hz), and on the final test set we get 67% correct (at 15 Hz).

Update: In the original version of this essay I incorrectly reported a higher score on both test sets, due to a bug. The bug was subtle, but I should have caught it, and I apologize for misleading those who read the earlier version. In the original version of spelltest, I left out the if bias: in the fourth line of the function (and the default value was bias=0, not bias=None). I figured that when bias = 0, the statement NWORDS[target] += bias would have no effect. In fact it does not change the value of NWORDS[target], but it does have an effect: it makes (target in NWORDS) true. So in effect the spelltest routine was cheating by making all the unknown words known. This was a humbling error, and I have to admit that much as I like defaultdict for the brevity it adds to programs, I think I would not have had this bug if I had used regular dicts.
Update 2: defaultdict strikes again. Darius Bacon pointed out that in the function correct, I had accessed NWORDS[w]. This has the unfortunate side-effect of adding w to the defaultdict, if w was not already there (i.e., if it was an unknown word). Then the next time, it would be present, and we would get the wrong answer. Darius correctly suggested changing to NWORDS.get. (This works because max(None, i) is i for any integer i.)

In conclusion, I met my goals for brevity, development time, and runtime speed, but not for accuracy.

Future Work

Let's think about how we could do better. (I've done some more in a separate chapter for a book.) We'll again look at all three factors of the probability model: (1) P(c); (2) P(w|c); and (3) argmaxc. We'll look at examples of what we got wrong. Then we'll look at some factors beyond the three...
P(c), the language model. We can distinguish two sources of error in the language model. The more serious is unknown words. In the development set, there are 15 unknown words, or 5%, and in the final test set, 43 unknown words or 11%. Here are some examples of the output of spelltest with verbose=True:
correct('economtric') => 'economic' (121); expected 'econometric' (1)
correct('embaras') => 'embargo' (8); expected 'embarrass' (1)
correct('colate') => 'coat' (173); expected 'collate' (1)
correct('orentated') => 'orentated' (1); expected 'orientated' (1)
correct('unequivocaly') => 'unequivocal' (2); expected 'unequivocally' (1)
correct('generataed') => 'generate' (2); expected 'generated' (1)
correct('guidlines') => 'guideline' (2); expected 'guidelines' (1)
In this output we show the call to correct and the result (with the NWORDS count for the result in parentheses), and then the word expected by the test set (again with the count in parentheses). What this shows is that if you don't know that 'econometric' is a word, you're not going to be able to correct 'economtric'. We could mitigate by adding more text to the training corpus, but then we also add words that might turn out to be the wrong answer. Note the last four lines above are inflections of words that do appear in the dictionary in other forms. So we might want a model that says it is okay to add '-ed' to a verb or '-s' to a noun.

The second potential source of error in the language model is bad probabilities: two words appear in the dictionary, but the wrong one appears more frequently. I must say that I couldn't find cases where this is the only fault; other problems seem much more serious.

We can simulate how much better we might do with a better language model by cheating on the tests: pretending that we have seen the correctly spelled word 1, 10, or more times. This simulates having more text (and just the right text) in the language model. The function spelltest has a parameter, bias, that does this. Here's what happens on the development and final test sets when we add more bias to the correctly-spelled words:

Bias	Dev.	Test
0	74%	67%
1	74%	70%
10	76%	73%
100	82%	77%
1000	89%	80%
On both test sets we get significant gains, approaching 80-90%. This suggests that it is possible that if we had a good enough language model we might get to our accuracy goal. On the other hand, this is probably optimistic, because as we build a bigger language model we would also introduce words that are the wrong answer, which this method does not do.

Another way to deal with unknown words is to allow the result of correct to be a word we have not seen. For example, if the input is "electroencephalographicallz", a good correction would be to change the final "z" to an "y", even though "electroencephalographically" is not in our dictionary. We could achieve this with a language model based on components of words: perhaps on syllables or suffixes (such as "-ally"), but it is far easier to base it on sequences of characters: 2-, 3- and 4-letter sequences.

P(w|c), the error model. So far, the error model has been trivial: the smaller the edit distance, the smaller the error. This causes some problems, as the examples below show. First, some cases where correct returns a word at edit distance 1 when it should return one at edit distance 2:
correct('reciet') => 'recite' (5); expected 'receipt' (14)
correct('adres') => 'acres' (37); expected 'address' (77)
correct('rember') => 'member' (51); expected 'remember' (162)
correct('juse') => 'just' (768); expected 'juice' (6)
correct('accesing') => 'acceding' (2); expected 'assessing' (1)
Here, for example, the alteration of 'd' to 'c' to get from 'adres' to 'acres' should count more than the sum of the two changes 'd' to 'dd' and 's' to 'ss'.

Also, some cases where we choose the wrong word at the same edit distance:

correct('thay') => 'that' (12513); expected 'they' (4939)
correct('cleark') => 'clear' (234); expected 'clerk' (26)
correct('wer') => 'her' (5285); expected 'were' (4290)
correct('bonas') => 'bones' (263); expected 'bonus' (3)
correct('plesent') => 'present' (330); expected 'pleasant' (97)
The same type of lesson holds: In 'thay', changing an 'a' to an 'e' should count as a smaller change than changing a 'y' to a 't'. How much smaller? It must be a least a factor of 2.5 to overcome the prior probability advantage of 'that' over 'they'.

Clearly we could use a better model of the cost of edits. We could use our intuition to assign lower costs for doubling letters and changing a vowel to another vowel (as compared to an arbitrary letter change), but it seems better to gather data: to get a corpus of spelling errors, and count how likely it is to make each insertion, deletion, or alteration, given the surrounding characters. We need a lot of data to do this well. If we want to look at the change of one character for another, given a window of two characters on each side, that's 266, which is over 300 million characters. You'd want several examples of each, on average, so we need at least a billion characters of correction data; probably safer with at least 10 billion.

Note there is a connection between the language model and the error model. The current program has such a simple error model (all edit distance 1 words before any edit distance 2 words) that it handicaps the language model: we are afraid to add obscure words to the model, because if one of those obscure words happens to be edit distance 1 from an input word, then it will be chosen, even if there is a very common word at edit distance 2. With a better error model we can be more aggressive about adding obscure words to the dictionary. Here are some examples where the presence of obscure words in the dictionary hurts us:

correct('wonted') => 'wonted' (2); expected 'wanted' (214)
correct('planed') => 'planed' (2); expected 'planned' (16)
correct('forth') => 'forth' (83); expected 'fourth' (79)
correct('et') => 'et' (20); expected 'set' (325)
The enumeration of possible corrections, argmaxc. Our program enumerates all corrections within edit distance 2. In the development set, only 3 words out of 270 are beyond edit distance 2, but in the final test set, there were 23 out of 400. Here they are:
purple perpul
curtains courtens
minutes muinets

successful sucssuful
hierarchy heiarky
profession preffeson
weighted wagted
inefficient ineffiect
availability avaiblity
thermawear thermawhere
nature natior
dissension desention
unnecessarily unessasarily
disappointing dissapoiting
acquaintances aquantences
thoughts thorts
criticism citisum
immediately imidatly
necessary necasery
necessary nessasary
necessary nessisary
unnecessary unessessay
night nite
minutes muiuets
assessing accesing
necessitates nessisitates
We could consider extending the model by allowing a limited set of edits at edit distance 3. For example, allowing only the insertion of a vowel next to another vowel, or the replacement of a vowel for another vowel, or replacing close consonants like "c" to "s" would handle almost all these cases.

There's actually a fourth (and best) way to improve: change the interface to correct to look at more context. So far, correct only looks at one word at a time. It turns out that in many cases it is difficult to make a decision based only on a single word. This is most obvious when there is a word that appears in the dictionary, but the test set says it should be corrected to another word anyway:
correct('where') => 'where' (123); expected 'were' (452)
correct('latter') => 'latter' (11); expected 'later' (116)
correct('advice') => 'advice' (64); expected 'advise' (20)
We can't possibly know that correct('where') should be 'were' in at least one case, but should remain 'where' in other cases. But if the query had been correct('They where going') then it seems likely that "where" should be corrected to "were".

The context of the surrounding words can help when there are obvious errors, but two or more good candidate corrections. Consider:

correct('hown') => 'how' (1316); expected 'shown' (114)
correct('ther') => 'the' (81031); expected 'their' (3956)
correct('quies') => 'quiet' (119); expected 'queries' (1)
correct('natior') => 'nation' (170); expected 'nature' (171)
correct('thear') => 'their' (3956); expected 'there' (4973)
correct('carrers') => 'carriers' (7); expected 'careers' (2)
Why should 'thear' be corrected as 'there' rather than 'their'? It is difficult to tell by the single word alone, but if the query were correct('There's no there thear') it would be clear.

To build a model that looks at multiple words at a time, we will need a lot of data. Fortunately, Google has released a database of word counts for all sequences up to five words long, gathered from a corpus of a trillion words.

I believe that a spelling corrector that scores 90% accuracy will need to use the context of the surrounding words to make a choice. But we'll leave that for another day...

We could improve our accuracy scores by improving the training data and the test data. We grabbed a million words of text and assumed they were all spelled correctly; but it is very likely that the training data contains several errors. We could try to identify and fix those. Less daunting a task is to fix the test sets. I noticed at least three cases where the test set says our program got the wrong answer, but I believe the program's answer is better than the expected answer:
correct('aranging') => 'arranging' (20); expected 'arrangeing' (1)
correct('sumarys') => 'summary' (17); expected 'summarys' (1)
correct('aurgument') => 'argument' (33); expected 'auguments' (1)
We could also decide what dialect we are trying to train for. The following three errors are due to confusion about American versus British spelling (our training data contains both):

correct('humor') => 'humor' (17); expected 'humour' (5)
correct('oranisation') => 'organisation' (8); expected 'organization' (43)
correct('oranised') => 'organised' (11); expected 'organized' (70)
Finally, we could improve the implementation by making it much faster, without changing the results. We could re-implement in a compiled language rather than an interpreted one. We could have a lookup table that is specialized to strings rather than Python's general-purpose dict. We could cache the results of computations so that we don't have to repeat them multiple times. One word of advice: before attempting any speed optimizations, profile carefully to see where the time is actually going.
Further Reading

Roger Mitton has a survey article on spell checking.
Jurafsky and Martin cover spelling correction well in their text Speech and Language Processing.
Manning and Schutze cover statistical language models very well in their text Foundations of Statistical Natural Language Processing, but they don't seem to cover spelling (at least it is not in the index).
The aspell project has a lot of interesting material, including some test data that seems better than what I used.
The LingPipe project has a spelling tutorial.
Errata

Originally my program was 20 lines, but Ivan Peev pointed out that I had used string.lowercase, which in some locales in some versions of Python, has more characters than just the a-z I intended. So I added the variable alphabet to make sure. I could have used string.ascii_lowercase.
Thanks to Jay Liang for pointing out there are only 54n+25 distance 1 edits, not 55n+25 as I originally wrote.

Thanks to Dmitriy Ryaboy for pointing out there was a problem with unknown words; this allowed me to find the NWORDS[target] += bias bug.

Other Computer Languages

After I posted this article, various people wrote versions in different programming languages. While the purpose of this article was to show the algorithms, not to highlight Python, the other examples may be interesting for those who like comparing languages, or for those who want to borrow an implementation in their desired language:
Language	Lines
Code	Author
(and link to implementation)
Awk	15	Tiago "PacMan" Peczenyj
Awk	28	Gregory Grefenstette
C	184	Marcelo Toledo
C++	98	Felipe Farinon
C#	43	Lorenzo Stoakes
C#	69	Frederic Torres
Clojure	18	Rich Hickey
D	23	Leonardo M
Erlang	87	Federico Feroldi
F#	16	Dejan Jelovic
F#	34	Sebastian G
Groovy	22	Rael Cunha
Haskell	24	Grzegorz
Java	35	Rael Cunha
Java	372	Dominik Schulz
Javascript	53	Panagiotis Astithas
Lisp	26	Mikael Jansson
Perl	63	riffraff
PHP	68	Felipe Ribeiro
PHP	103	Joe Sanders
Python	21	Peter Norvig
Rebol	133	Cyphre
Ruby	34	Brian Adkins
Scala	23	Thomas Jung
Scheme	45	Shiro
Scheme	89	Jens Axel
Other Natural Languages

This essay has been translated into:
Simplified Chinese by Eric You XU
Japanese by Yasushi Aoki
Russian by Petrov Alexander
40 languages by Google Translate:

	Gadgets powered by Google
Thanks to all the authors for creating these implementations and translations.

Peter Norvig
