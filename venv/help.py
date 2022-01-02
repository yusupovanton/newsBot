# str = 'гендиректор уаза адиль ширинов заявил о неизбежном закрытии завода'
# str2 = "завод"
# if str2 in str:
#     print('yes')
import difflib
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

str = '<a class="mg-card__link" data-log-id="u-1637600928000-449cec-425" href="https://yandex.ru/news/story/Kompaniya_Ferrari_predstavila_superkar_Ferrari_Daytona_SP3_serii_Icona--d482fc8d9344ee4c5bda928d332b132e?lang=ru&amp;rubric=auto&amp;fan=1&amp;stid=ji-6uw-Tgch1ytyHeg3r&amp;t=1637600555&amp;persistent_id=169689320" rel="noopener" target="_self"><h2 class="mg-card__title">Компания Ferrari представила суперкар Ferrari Daytona SP3 серии Icona</h2></a>'
word = 'украина'

def similarity(s1, s2):
  normalized1 = s1.lower()
  normalized2 = s2.lower()
  matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
  return matcher.ratio()

print(similarity(str, word))

print(process.extract(word, str, limit=3))


