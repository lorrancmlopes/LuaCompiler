# Status dos testes

![git status](http://3.129.230.99/svg/lorrancmlopes/logcomp/)

**EBNF:**
```
EXPRESSION = TERM, { ("+" | "-"), TERM } ;
TERM = FACTOR, { ("*" | "/"), FACTOR } ;
FACTOR = ("+" | "-") FACTOR | "(" EXPRESSION ")" | number ;

```

<p align="center">
  <img src="estadoAtual.png" width="350" title="Estado Atual">
</p>
