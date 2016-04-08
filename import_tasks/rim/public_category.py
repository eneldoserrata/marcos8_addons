

skub = open("product.txt", "r")


root = "U-PLT"
grade = []
serie_a = []
serie_b = []
rin = []


count = 0
for line in skub:
    gradel = line[6:7]
    serie_al = line[8:11]
    serie_bl = line[12:14]
    rinl = line[15:18]

    if not gradel in grade: grade.append(gradel)
    if not serie_al in serie_a: serie_a.append(serie_al)
    if not serie_bl in serie_b: serie_b.append(serie_bl)
    if not rinl in rin: rin.append(rinl)

import itertools
from pprint import pprint as pp

# g = sorted(grade)
# pp(g)
#
# sa = sorted(serie_a)
# pp(sa)
#
# sb = sorted(serie_b)
# pp(sb)
#
# r = sorted(rin)
# pp(r)


gsa = [sorted(grade), sorted(serie_a)]
gsal = list(itertools.product(*gsa))
pp(gsal)

gsab = [gsal, sorted(serie_b)]
gsabl = list(itertools.product(*gsab))
pp(gsabl)

gsabr = [gsabl, sorted(rin)]
gsabrl = list(itertools.product(*gsabr))
pp(gsabrl)

skub.close()
