# Waagenspiel – Mathenacht 2025, Aufgabe 1.6

## Problemstellung

Gegeben sind vier positive ganze Zahlen $a, b, c, d \geq 1$.
Ein **Relationssystem** ist eine Menge von Aussagen der Form

$$L \;\mathbin{<}\; R, \quad L \;=\; R, \quad L \;>\; R,$$

wobei $L$ und $R$ jeweils Summen (ohne Koeffizienten) über $\{a, b, c, d\}$ sind,
z. B. $a + b < c + d$ oder $a = b + c + d$.

**Frage:** Für welche Relationssysteme lässt sich aus den gegebenen Relationen
zwingend schließen, dass **genau eine** der vier Variablen das Maximum ist –
unabhängig von den konkreten Zahlenwerten, solange alle Relationen erfüllt sind?

---

## Theorie

### 1. Modellierung als Lineares Programm (LP)

Weil alle Relationen *linear* in $a, b, c, d$ sind und die Variablen reelle
Zahlen $\geq 1$ sein dürfen (der diskrete Fall ≥ 1 ist eine Teilmenge davon),
lässt sich jede Frage der Art

> „Kann es vorkommen, dass $y \geq x$?"

als **LP-Machbarkeitsproblem** formulieren:

$$
\text{Gibt es } a,b,c,d \geq 1 \text{ mit} \begin{cases}
\text{alle Systemrelationen,} \\
y - x \geq 0 \;?
\end{cases}
$$

Wenn dieses LP **unerfüllbar** (infeasible) ist, gilt $x > y$ in jedem zulässigen
Punkt – also auch für alle ganzzahligen Lösungen.

> **Korrektheit:** Ist das LP über den Reellen unerfüllbar, so erst recht über
> den ganzen Zahlen ≥ 1. Die LP-Relaxierung liefert also keine falsch-positiven
> Urteile.

### 2. Eindeutiges Maximum

Eine Variable $x$ ist **eindeutiges Maximum** des Systems, wenn für jeden
Konkurrenten $y \neq x$ das LP

$$
\text{Minimiere } x - y \quad \text{u.d.N. Systemrelationen, } a,b,c,d \geq 1
$$

**unerfüllbar** ist (d. h. $y \geq x$ ist unmöglich).

Ein System hat ein eindeutiges Maximum, wenn **genau eine** Variable alle ihre
Konkurrenten schlägt.

### 3. Kanonische Form & Symmetriereduktion

Da die Namen der Variablen willkürlich sind, werden alle Systeme in eine
**kanonische Form** gebracht: Die lexikographisch kleinste Umbenennung
$\{a,b,c,d\} \to \{a,b,c,d\}$, die das System invariant lässt. Dadurch wird
jedes strukturell gleiche System nur einmal gezählt.

### 4. Einfluss der Schranke $\geq 1$ vs. $\geq 0$

Der Wechsel von $a,b,c,d \geq 0$ zu $\geq 1$ verkleinert den Lösungsraum und
kann neue eindeutige Maxima erzeugen. Ein Beispiel:

**System:** $a < a+b,\quad a = b+c+d$

- **$\geq 1$:** Da $c,d \geq 1$, folgt $a = b+c+d > b$, $> c$, $> d$.
  Also ist $a$ eindeutiges Maximum. ✓
- **$\geq 0$:** Mit $c=d=0$, $a=b=1$ sind alle Relationen erfüllt,
  aber $a = b$ – kein eindeutiges Maximum. ✗

---

## Ergebnisse

| Datei | Inhalt |
|---|---|
| `relation_systems.json` | Alle 140 589 kanonisch verschiedenen Relationssysteme (mit ≤ 3 Relationen) |
| `unique_systems.json` | Die 11 988 Systeme davon, die ein eindeutiges Maximum besitzen |

Anteil mit eindeutigem Maximum: **≈ 8,5 %**.

---

## Skripte

### `validate_systems.py`

Prüft für ein gegebenes Relationssystem (oder alle Systeme aus der JSON-Datei),
ob ein eindeutiges Maximum existiert.

**Verwendung:**
```bash
python validate_systems.py                    # validiert alle Systeme
python validate_systems.py meine_systeme.json # eigene Datei
```

**Algorithmus (LP-basiert, `scipy.optimize.linprog`):**

Für jede Kandidatenvariable $x$ und jeden Gegner $y$:
1. Baue das LP aus den Systemrelationen auf.
2. Füge die Bedingung $y \geq x$ hinzu.
3. Falls das LP unerfüllbar → $x > y$ ist gesichert.
4. Falls $x$ alle Gegner schlägt → $x$ ist eindeutiges Maximum.

### `analyze_systems.py`

Filtert aus `relation_systems.json` alle Systeme mit eindeutigem Maximum,
speichert sie in `unique_systems.json` und gibt ausführliche Statistiken aus
(Systemgröße, Operatoren, Relationsformen, Häufigkeit des Maximums, …).

```bash
python analyze_systems.py
```

### `primes.py` / `1_9.py` / `1_5_2.py` / `2_10.py`

Hilfsskripte für weitere Aufgaben der Mathenacht 2025.

---

## Aufgabenlösungen

Die Markdown-Dateien `1_1.md` … `1_10.md` enthalten die Lösungswege zu den
Aufgaben der **1. Runde**, die Datei `2_10.py` eine Lösung aus Runde 2.

Die Aufgabenblätter liegen als PDFs bei:
- `__(11)1213-1-1.pdf` – Runde 1
- `Aufgaben 123 Runde 2.pdf` – Runden 1–3

---

## Abhängigkeiten

```bash
pip install numpy scipy
```
