# Super Forge Edits

```python
r"^((?P<bronze>Bronze) Geno Core: (?P<bronzecore>.*))$|^((?P<silver>Silver) Geno Core: (?P<silvercore>.*))$|((?P<gold>Gold) Geno Core: (?P<goldcore>.*))$|^((?P<gemstone>Gemstone) Geno Core: (?P<gemstonecore>.*))$|^((?P<super>Super) Geno Core: (?P<supercore>.*))$""
```

> Finds all matches for geno cores in named capture groups

### Generic Geno Core Regex

```python
r"^((?P<class>\w+) Geno Core: (?P<core>.*))$\n"
```

#### Global pattern flags

- g modifier: **g**lobal. All matches (don't return after first match)

- m modifier: **m**ulti line. Causes `^` and `$` to match the begin/end of each line (not only begin/end of string)

- i modifier: **i**nsensitive. Case insensitive match `(ignores case of [a-zA-Z])`



#### Explination

> `^` asserts position at start of a line
>
> ##### 1st Capturing Group 
>
> ```python
> r"((?P<class>\w+) Geno Core: (?P<core>.\*))
> ```
>
> ###### Named Capture Group `class` (?P<class>\w+)
>
> - `\w` matches any word character (equivalent to [a-zA-Z0-9_])
>
> - `\+` matches the previous token between one and unlimited times, as many times as possible, giving back as needed (greedy)

---



#### Ungrouped Match

> - `Geno Core:  `matches the characters  `Geno Core: ` literally (case insensitive)

---



####  Named Capture Group `core` (?P<core>.\*)

> - `.` matches any character (except for line terminators)
>
> - `\*` matches the previous token between zero and unlimited times, as many times as possible, giving back as needed (greedy)
>
> - `$` asserts position at the end of a line- \n matches a line-feed (newline) character (ASCII 10)
>
> - `\n` matches a line-feed (newline) character (ASCII 10)

---



### Replacement

```python
<div class="tables">
	<table class="center70">
		<tr>
			<th>\g<class> Geno Core</th>
    </tr><tr>
			<td>\g</td>
		</tr>
	</table>
	<!--\g-->
</div>
```

