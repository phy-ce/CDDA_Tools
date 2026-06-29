# Cataclysm: Bright Nights — 전투 알고리즘 / 수식 정리

이 문서는 **게임 C++ 소스에서 직접 추출**한 전투 계산식을 정리한 것입니다.
설명을 위해 식을 단순화하지 않았으며, 각 항목에 원본 `파일:줄` 참조를 답니다.

- **대상 포크:** Cataclysm: Bright Nights (`cataclysmbn/Cataclysm-BN`)
- **고정 커밋:** `426991f91134255148f61a2e64d9a88af660b74d` (설치 빌드 `2026-06-27-0308` 의 `VERSION.txt` commit sha)
- 줄 번호는 이 커밋 기준입니다. CDDA(메인)와는 일부 식이 다릅니다.

> ⚠️ **표기 규칙**
> - `skill_X` = 해당 스킬 레벨, `dex/per/str` = 능력치(`get_dex()` 등).
> - 곱은 `·`, 정수 절단은 `⌊⌋` 로 표기. C++ `int` 대입은 0 방향 절단.
> - 길이/무게는 내부 단위(volume: mL, weight: g, 각도: arcmin=MoA).

---

## 0. 공용 난수 함수 (`src/rng.cpp`)

| 함수 | 정의 |
|---|---|
| `dice(n, sides)` | `Σ_{i=1..n} rng(1, sides)` — 각 항은 1..sides 균등 정수 (rng.cpp:85) |
| `rng_float(lo, hi)` | 구간 `[lo,hi)` 균등 실수 |
| `normal_roll(mean, stddev)` | 정규분포 `N(mean, stddev)` — **둘째 인자는 표준편차** (rng.cpp:42) |
| `rng_normal(lo, hi)` | `clamp( normal_roll((lo+hi)/2, (hi−lo)/4), lo, hi )` (rng.cpp:122) |
| `rng_normal(hi)` | `rng_normal(0, hi)` |
| `roll_remainder(x)` | 확률적 반올림: 소수부 확률로 올림 (예: 1.3 → 70%로 1, 30%로 2) |
| `one_in(n)` | `1/n` 확률로 참 |

기하 보조 (`src/line.cpp:21`):

```
iso_tangent(distance, θ) = √( 2·distance² · (1 − cos θ) ) = 2·distance·sin(θ/2)
```

상수 (`src/game_constants.h`, `src/melee.h`):

```
MAX_SKILL          = 10
BIO_CQB_LEVEL      = 5        // CQB 바이오닉이 강제하는 최소 무기 스킬
accuracy_roll_stddev = 5.0
MAX_RECOIL         = 3000     // MoA, "스냅/허리쏘기" 수준의 정확도
accuracy_headshot  = 0.1
accuracy_critical  = 0.2
accuracy_goodhit   = 0.5
accuracy_standard  = 0.8
accuracy_grazing   = 1.0
```

---

## 1. 근접 전투 (Melee)

전체 흐름(`Character::melee_attack`, melee.cpp:1477):
1. 명중 굴림 `hit_roll` 을 만들고, 대상의 `deal_melee_attack` 으로 **명중 여부(`hit_spread`)** 판정.
2. 빗나가면 휘청임(stumble)만 적용. 명중하면 치명타 판정 → 피해 굴림 → 방어구 경감 → 실제 피해.

### 1.1 명중 굴림 (to-hit)

**기본치** (character.cpp:6643, 6637):

```
Character.get_hit_base()   = dex / 4
Character.get_dodge_base() = dex / 4 + skill_dodge
```

**무기 보정** `get_hit_weapon` (melee.cpp:1342):

```
skill_w = skill(무기의 melee_skill)         // CQB 활성 시 max(skill_w, 5)
get_hit_weapon = skill_w/3 + skill_melee/2 + weapon.to_hit + weapon.melee_hit_bonus
```

**종합 명중치** `get_melee_hit` (melee.cpp:1360):

```
hit = get_hit_base + get_hit_weapon + mabuff_tohit_bonus
원시(遠視, HYPEROPIC) & 미교정:        hit −= 2
불안정 지형(bouldering):              hit ×= 0.75
hit ×= max( 0.25 , 1 − torso_encumbrance / 100 )
```

**명중 굴림** (melee.cpp:1381, 3759):

```
hit_roll = melee_hit_range(hit) = normal_roll( hit · 5 , 25 )
```

> ⚠️ **코드 내 불일치 주의.** 실제 굴림 `melee_hit_range` 는
> `normal_roll(accuracy·5, accuracy_roll_stddev²)` 즉 **표준편차 25** 를 사용한다
> (melee.cpp:3761). 반면 NPC AI/표시용 추정 함수 `melee::hit_chance`(melee.cpp:3764)는
> 표준편차 5 를 가정한다: `0.5·(1 + erf(−accuracy/√2))`. 두 값은 일치하지 않으며,
> **실제 전투 판정에 쓰이는 것은 표준편차 25 쪽**이다.

### 1.2 명중 여부 / 회피 (`Creature::deal_melee_attack`, creature.cpp:684)

```
hit_spread = hit_roll − dodge_roll − size_melee_penalty
대상이 IMMOBILE(고정 포탑 등):  hit_spread += 40
명중 성공  ⇔  hit_spread ≥ 0
```

**회피 굴림** (melee.cpp:2011 / monster.cpp:2838):

```
dodge_roll = get_dodge() · 5
```

**크기 페널티** `size_melee_penalty` (creature.cpp:663) — 작을수록 맞히기 어려움:

| 크기 | tiny | small | medium | large | huge |
|---|---|---|---|---|---|
| 페널티 | +30 | +15 | 0 | −10 | −20 |

**플레이어 회피** `Character::get_dodge` (melee.cpp:1963) — `Creature::get_dodge()`(=base+bonus)에 상황 보정:

```
수면/마취/스태미나 0           → 0
스태미나 < 50%                 → ×(stamina/stamina_max · 2)
곰덫·올무                      → /2
붙잡힘(grabbed)               → ×(1 − 0.25 · 붙잡은 좀비 수)
인라인/롤러스케이트            → /5  (PROF_SKATER면 /2)
bouldering                    → /4
이번 턴 추가 회피(dodges_left≤0) → += dodges_left·2 − 2
결과는 max(0, ret)
```

### 1.3 치명타 (Critical hit)

판정 (melee.cpp:1877):

```
scored_crit = ( rng_float(0,1) < crit_chance(hit_roll, target_dodge, weapon) )
```

`crit_chance` (melee.cpp:1891) — 세 독립 확률을 합성:

```
# 무기 확률
weapon_cc = 0.5
  무기가 비무장(unarmed)일 때:  weapon_cc = 0.5 + 0.05 · skill_unarmed
  ath = weapon.to_hit + weapon.melee_hit_bonus
  ath > 0:  weapon_cc = max(weapon_cc, 0.5 + 0.1·ath)
  ath < 0:  weapon_cc += 0.1·ath
  weapon_cc = clamp(weapon_cc, 0, 1)

# 능력치 확률
stat_cc  = clamp( 0.25 + 0.01·dex + 0.02·per , 0, 1 )

# 스킬 확률
sk = skill(무기 melee_skill)            # CQB 시 max(sk,5)
sk += skill_melee / 2.5
skill_cc = clamp( 0.25 + 0.025·sk , 0, 1 )

triple = weapon_cc · stat_cc · skill_cc          # 무조건 치명타
if hit_roll > target_dodge · 3/2:
    double = 0.5 · ( weapon_cc·stat_cc + stat_cc·skill_cc + weapon_cc·skill_cc − 3·triple )
    crit_chance = triple + double
else:
    crit_chance = triple
```

### 1.4 피해 굴림

세 물리 피해(타격/절단/관통)를 각각 굴려 `damage_instance` 에 누적한다.
각 단위는 `(amount, res_pen=방어관통, res_mult=방어배수, damage_multiplier)` 4값.

**힘 보너스** (melee.cpp:2021):

```
bonus_damage(random=true)  = rng_float( str/2 , str )
bonus_damage(random=false) = str · 0.75      // 평균 경로
```

#### 타격 (Bash) — `roll_bash_damage` (melee.cpp:2031)

```
skill = skill_bashing (비무장이면 skill_unarmed)   # CQB 시 5
stat  = str
stat_bonus = bonus_damage(random) + mabuff_damage_bonus(BASH)

weap_dam = weapon.damage_melee(BASH) + stat_bonus
           (비무장이면 + skill)

bash_cap = 2·stat + 2·skill
# 스킬별 배수: 80,88,96,104,112,116,120,124,128,132 %
bash_mul = (skill < 5) ? 0.8 + 0.08·skill : 0.96 + 0.04·skill

# 능력/스킬이 낮아 cap을 넘기면 배수를 cap과 절반 지점으로 축소
if bash_cap < weap_dam and 무기 != null:
    bash_mul ·= (1 + bash_cap/weap_dam) / 2

low_cap  = min(1, stat/20)
bash_min = low_cap · weap_dam
weap_dam = rng_float(bash_min, weap_dam)      # 평균: (bash_min+weap_dam)/2

bash_dam += weap_dam
bash_mul ·= mabuff_damage_mult(BASH)

armor_mult = attack 자체 res_mult(BASH);  arpen = attack res_pen(BASH) (+ mabuff)
치명타면:  bash_mul ·= 1.5 ,  armor_mult ·= 0.5   # 방어 50% 관통

add_damage(BASH, amount=bash_dam, res_pen=arpen, res_mult=armor_mult, damage_multiplier=bash_mul)
```

#### 절단 (Cut) — `roll_cut_damage` (melee.cpp:2143)

```
cut_dam = mabuff_damage_bonus(CUT) + weapon.damage_melee(CUT)   (+ 비무장 변이/생체칼날 보너스)
if cut_dam ≤ 0: 절단 없음

# 80,88,96,104,112,116,120,124,128,132 %
cut_mul = (skill_cutting < 5) ? 0.8 + 0.08·skill_cutting : 0.96 + 0.04·skill_cutting
cut_mul ·= mabuff_damage_mult(CUT)

arpen = attack res_pen(CUT) (+ mabuff)
DIAMOND 플래그:  arpen += cut_dam·0.35 + 10
치명타면:  cut_mul ·= 1.25 ,  arpen += 5 ,  armor_mult = 0.75   # 25% 관통

add_damage(CUT, cut_dam, arpen, armor_mult, cut_mul)
```

#### 관통 (Stab) — `roll_stab_damage` (melee.cpp:2222)

```
stab_dam = mabuff_damage_bonus(STAB) + weapon.damage_melee(STAB)   (+ 비무장 변이/생체칼날)
if stab_dam ≤ 0: 관통 없음

# 66,76,86,96,106,116,122,128,134,140 %
stab_mul = (skill_stabbing ≤ 5) ? 0.66 + 0.1·skill_stabbing : 0.86 + 0.06·skill_stabbing
stab_mul ·= mabuff_damage_mult(STAB)

arpen = attack res_pen(STAB) (+ mabuff)
DIAMOND 플래그:  arpen += stab_dam·0.35 + 10
치명타면:  stab_mul ·= 1 + skill_stabbing/10 ,  armor_mult ·= 0.66

add_damage(STAB, stab_dam, arpen, armor_mult, stab_mul)
```

#### 전체 피해 인스턴스 보정 (melee.cpp:1618~)

세 피해를 굴린 뒤 공격 직전에 추가 곱이 적용된다(각 단위의 `damage_multiplier` 에 곱):

```
양팔 모두 부러짐(working_arm < 1):                d ·= 0.1
폴암으로 인접칸 공격(POLEARM, 사거리>1, 비도달타): d ·= 0.7
스태미나 < 25%:  d ·= 0.5 + (stamina / stamina_max · 2)
```

### 1.5 피해 적용 & 방어구 경감

적용 순서 (`Creature::deal_damage`, creature.cpp:1246 → `absorb_hit` → `deal_damage_handle_type`):

1. `absorb_hit` 이 **방어구로 `amount` 를 깎음**(아래).
2. 단위별 실제 피해 = `⌊ amount · damage_multiplier ⌋` (creature.cpp:1293). 즉 **치명타·스킬 배수는 방어 적용 후 곱해진다.**

**유효 저항** (damage.cpp:317):

```
effective_resist(du) = max( type_resist(du.type) − du.res_pen , 0 ) · du.res_mult
```

**한 방어구의 경감** `item::mitigate_damage` (item.cpp:7369):

```
mitigation   = effective_resist(du)
du.res_pen   = max(0, du.res_pen − type_resist)     # 다음 레이어용으로 관통 소모
du.amount    = max(0, du.amount − mitigation)
```

플레이어는 겉옷→속옷 순으로 각 레이어가 차례로 `mitigate_damage` 를 적용하며,
레이어 적중은 `rng(1,100) > coverage` 면 건너뜀(armor_absorb, character.cpp:9238).
타격 피해엔 LIGHT_BONES ×1.4 / HOLLOW_BONES ×1.8 가 추가로 곱해진다(character.cpp:9218).

**몬스터 방어** `monster::resists` (monster.cpp:2167): 타입별 `armor_*` + 착용 + 보너스 합을
저항으로 두고 `amount −= min(effective_resist, amount)` (monster.cpp:2146).

### 1.6 공격 소요 무브 (Attack moves)

아이템 기본 공격비용 `item::attack_cost` (item.cpp:5865):

```
base = 65 + ( volume/62.5mL + weight/60g ) / count   (+ 인챈트)
```

플레이어 1회 공격 무브 `Character::attack_cost` (melee.cpp:3504):

```
b        = weapon.attack_cost() / 2
skill_cost = b · (15 − skill_melee) / 15            # CQB면 skill_melee=5
enc      = torso_enc + (hand_l_enc + hand_r_enc)/2
stamina_ratio   = stamina / stamina_max
stamina_penalty = 1 + max( (0.25 − stamina_ratio)·4 , 0 )   # 25%→0%에서 1.0→2.0

move  = b
move += enc
move ·= stamina_penalty
move += skill_cost
move −= dex
# 한 손으로 들 수 있는데 두 손으로 드는 무거운(>100) 무기: 지수 보정
if weapon.attack_cost() > 100 and 한손가능 and 양팔 and !RESTRICT_HANDS:
    move = move^0.975
move += 인챈트(ATTACK_COST)
move ·= 무술 공격비용 배수 ; move += 무술 공격비용 가산
move ·= mutation "attackcost_modifier"
return max(25, move)        # 하한 25 무브
```

> 참고: 속도(speed) 100에서 100무브 = 1초. 즉 1회 공격 시간(초) ≈ move / speed.

**휘청임(빗나감 페널티)** `stumble` (melee.cpp:1861):

```
stumble = volume/125mL + weight/(str·10g + 13g)      # DEFT 특성이면 0
빗나가면:  move_cost += min(60, stumble)              # 미스 회복술이 있으면 추가로 /2
```

**근접 스태미나 소모** `get_melee_stamina_cost` (melee.cpp:1458):

```
weight_cost = weight / 16g
enc_cost    = roll_remainder( (arm_l_enc + arm_r_enc) · 2 )
deft_bonus  = DEFT ? 50 : 0
strbonus    = 1 / (2 + str·0.25)
skill_cost  = max( 0.667 , (30 − skill_melee)/30 )
cost = (weight_cost + enc_cost − deft_bonus + 50) · skill_cost · (0.75 + strbonus)
```

---

## 2. 원거리 전투 (Ranged)

흐름: **분산(dispersion) 합성 → 굴림 → 빗나간 거리(missed_by) → 회피 합성(goodhit) →
명중 등급별 피해배수(severity) → 부위 판정 → 방어 적용.**

### 2.1 분산 (Dispersion, 단위 MoA)

`dispersion_sources` 는 세 종류의 원천을 모은다 (dispersion.h):
- **linear**: `rng_float(0, source)` 로 굴림
- **normal**: `rng_normal(source)` 로 굴림
- **multiplier**: 합에 곱함

굴림/통계 (dispersion.cpp):

```
roll() = ( Σ rng_float(0, linear_i) + Σ rng_normal(normal_i) ) · Π multiplier_k
max()  = ( Σ linear_i + Σ normal_i ) · Π multiplier_k
avg()  = max() / 2
```

무기 분산 합성 `ranged::get_weapon_dispersion` (ranged.cpp:2650):

```
normal 원천:  weapon_dispersion = gun_dispersion()
+linear: ranged_dex_mod = max( (20 − dex)·0.5 , 0 )          (character.cpp:4991)
+linear: (arm_l_enc + arm_r_enc) / 5
운전 중:  +linear: max( vol/250mL − skill_driving , 1 ) · 20
+linear: dispersion_from_skill(avgSkill, weapon_dispersion)
         avgSkill = min(10, (skill_gun + skill_무기) / 2)
×0.75  bio_targeting
×0.75  웅크림(crouch)
×0.25  LASER_GUIDED
×(1 / str_draw_dispersion_modifier)   # 활 당김 힘 부족 시 ≥1
물/수중 불일치:  +linear 150 , ×4
거치총 미지지 페널티(상황별 +500/+1000)
+linear: 인챈트(RANGED_DISPERSION)
```

스킬에 의한 분산 `dispersion_from_skill(skill, wd)` (ranged.cpp:2627):

```
skill ≥ 10:                         0
공통:  penalty = 3·(10 − skill)
skill ≥ 5:   penalty + ( wd·(10 − skill)·1.25 ) / (10 − 5)
skill < 5:   penalty + wd·( 1.25 + (5 − skill)·3.75/5 )
```

### 2.2 반동 / 조준 (Recoil & Aim, 단위 MoA)

```
recoil_vehicle = (차량 탑승 시) |velocity|·3/100                  (ranged.cpp:2822)
recoil_total   = max( 0 , recoil + recoil_vehicle + 인챈트 )      (ranged.cpp:2835)
```

조준 1무브당 반동 감소 `ranged::aim_per_move` (ranged.cpp:4718):

```
aim_speed = 10
          + aim_speed_skill_modifier        (0–10)
          + aim_speed_dex_modifier          (0–12)
          + sight_speed_modifier            (0–10)
          − aim_speed_encumbrance_modifier  (손 거추장 5당 −1)
aim_speed ·= aim_multiplier_from_volume(gun)
aim_speed ·= 6.5
aim_speed ·= 1 − logarithmic_range(0, MAX_RECOIL, recoil)
aim_speed  = max(5, aim_speed + 인챈트)
return min( aim_speed , recoil − limit )     # 현재 조준기가 허용하는 최소치까지만
```

### 2.3 발사체 명중 (`projectile_attack_roll`, ballistics.cpp:280)

```
d            = dispersion.roll()                          # MoA
missed_by_tiles = iso_tangent( range , from_arcmin(d) )   # = 2·range·sin(d/2)
target_size  > 0:  missed_by = min( 1 , missed_by_tiles / target_size )
target_size == 0:  missed_by = 1
```

### 2.4 회피 합성 & 명중 등급 (`Creature::deal_projectile_attack`, creature.cpp:839)

```
avoid_roll     = dodge_roll()
diff_roll      = dice(10, proj.speed)        # 총알 speed≈1000, 화살≈100, 투척≈20
dodge_adj      = avoid_roll / diff_roll       # 0.01 미만은 0 으로 처리
goodhit        = missed_by + clamp(dodge_adj, 0, 1)
goodhit ≥ 1.0  ⇒  완전 회피(피해 없음)
```

`goodhit` 이 낮을수록 좋은 명중:
`헤드샷 < 0.1`, `치명 < 0.2`, `우수 < 0.5`, `보통 < 0.8`, `0.8 ≤ 스침(graze)`.

### 2.5 피해 배수 (Severity) (creature.cpp:930)

```
일반 탄(비마법):
  goodhit > 0.8 :  severity = max( 0.01 , 4·(1 − goodhit) )      # 스침: 1~80%
  goodhit > 0.5 :  severity = 1.6 − goodhit                      # 80~110%
  goodhit > 0.2 :  severity = 1.766 − (goodhit·4/3)              # 110~150%
  그 외          :  severity = 1.5                                # 정확도 기여분 상한
마법:  severity = rng_float(0.9, 1.1)

goodhit ≤ 0.2 이고 발사자가 캐릭터/NPC면(스킬 조준 치명타 보너스):
  severity += (wep_skill_adjust + stat_adjust) · ( (0.2 − goodhit)·5 )
```

부위 판정용 `hit_value = | goodhit + rng_float(−var, var) |`,
`var`(hit_location_variance)는 기본 0.9 에서 `(0.05·(dex+per−16) + 무기스킬·0.15)·스태미나비율`
만큼 감소(최소 0.05). 명중 부위는 `hit_value` 와 `accuracy_*` 밴드로 결정(머리/몸통/팔다리).

**부위별 severity 상한** (creature.cpp:1047):
머리 ≤ 2.0 (캐릭터/일부 몬스터는 1.5), 몸통 ≤ 1.5, 팔다리 ≤ 1.25
(+ 탄약 `aimedcritmaxbonus`, PROJECTILE_RESISTANT_* 몬스터는 더 낮게 캡).

**적용** (creature.cpp:1095):

```
impact = proj.impact
impact.mult_damage( severity , pre_armor = (goodhit > 0.8) )
```

즉 **스침(>0.8)은 방어 적용 전에** 배수가 곱해지고(=방어가 더 크게 작용),
그 외에는 방어 적용 후 곱해진다. 이후 §1.5 의 방어구 경감을 동일하게 거친다.

---

## 3. 몬스터 전투

명중/회피 기본치 (monster.cpp):

```
get_hit_base()   = type.melee_skill   (· pet_training^training_level)   (2750)
get_dodge_base() = type.sk_dodge      (· pet_training^training_level)   (2759)
hit_roll()       = melee_hit_range( get_hit() )   # bouldering이면 /4    (2768)
dodge_roll()     = get_dodge() · 5                                       (2838)
get_hit()/get_dodge() = base + bonus
```

근접 공격 `monster::melee_attack` (monster.cpp:2175, 2180):

```
melee_attack(target)          ≡ melee_attack(target, get_hit())
무브 소모:  −type.attack_cost
hitspread = target.deal_melee_attack( this , melee_hit_range(accuracy) )   # ≥0 이면 명중

피해 = type.melee_damage(고정 damage_instance)
     + DT_BASH:  dice( type.melee_dice , type.melee_sides )   # 무장해제 시 sides/2
     + DT_BASH:  bash_bonus
     + DT_CUT :  cut_bonus
명중 시 target.deal_melee_hit(...) → §1.5 방어/피해 적용
```

안정성(넘어짐 저항) `monster::stability_roll` (monster.cpp:2783):

```
stability = dice(melee_sides, melee_dice) + size_bonus
size_bonus: tiny −7, small −3, medium 0, large +5, huge +10
기절(stunned)이면 −rng(1,5)
```

발사체 피격은 §2.4~2.5 의 `Creature::deal_projectile_attack` 경로를 캐릭터와 공유한다
(몬스터 방어는 §1.5 의 `monster::resists`).

---

## 3.5 방어구 아이템 보호치 (재질 기반, `item.cpp`)

장비 아이템의 방어치는 JSON에 직접 저장되지 않고 **재질(material)의 저항값 ×
두께(`material_thickness`)** 로 산출된다. 손상 0·의류 보정(`clothing_mod`) 0 인
새 아이템 기준:

```text
phys_resist (item.cpp:7034, 물리계 공통 템플릿):
    resist = Σ_재질 mat.<X>_resist / 재질수            # 재질 단순 평균
    값      = round( resist · thickness )              # thickness = get_thickness()

bash    (item.cpp:7081) = round( avg(bash_resist)   · thickness )
cut     (item.cpp:7086) = round( avg(cut_resist)    · thickness )
stab    (item.cpp:7095) = int( 0.8 · cut )           # cut(정수)에 0.8, 버림
bullet  (item.cpp:7101) = round( avg(bullet_resist) · thickness )

acid    (item.cpp:7107) = round( avg(acid_resist) · env_scale )
fire    (item.cpp:7147) = round( avg(fire_resist) · env_scale )
    env      = get_env_resist()      = environmental_protection (item.cpp:6670)
    env_scale = (env ≥ 10) ? 1 : env/10              # 환경보호 낮으면 침투
```

`thickness` = `get_thickness()` (item.cpp:6895) = 방어구 슬롯의 `material_thickness`.
재질 저항값은 `data/json/materials.json` 의 `*_resist` 필드. 검증: `boots_steel`
(steel+leather, thickness 3, env 3) → bash `round((6+2)/2·3)=12`, bullet
`round((5+2)/2·3)=10`, acid `round((7+4)/2·0.3)=2` — 게임 내 표기와 일치.

이 식은 `dataindex.DataIndex.armor_protection()` 에 구현되어 아이템 페이지의 방어
박스와 아이템 표의 🛡 열을 채운다.

## 4. 요약 치트시트

| 항목 | 핵심 식 |
|---|---|
| 근접 명중 굴림 | `normal_roll(5·hit, 25)`, `hit_spread = 굴림 − dodge·5 − 크기` |
| 근접 명중치 | `dex/4 + skill_w/3 + skill_melee/2 + 무기to_hit + (보정)` |
| 타격 배수 | 스킬<5 `0.8+0.08·s`, 아니면 `0.96+0.04·s`; 치명 ×1.5 |
| 절단 배수 | 스킬<5 `0.8+0.08·s`, 아니면 `0.96+0.04·s`; 치명 ×1.25 |
| 관통 배수 | 스킬≤5 `0.66+0.1·s`, 아니면 `0.86+0.06·s`; 치명 ×(1+s/10) |
| 실제 피해 | `⌊ (amount − 유효저항) · damage_multiplier ⌋` |
| 유효 저항 | `max(저항 − 관통, 0) · 방어배수` |
| 공격 무브 | `≈ base/2·(1 + (15−melee)/15) + enc − dex`, 하한 25 |
| 분산 굴림 | `(Σ rng_float(0,L) + Σ rng_normal(N)) · Π mult` (MoA) |
| 빗나간 거리 | `2·range·sin(dispersion/2) / target_size` |
| 발사 명중도 | `goodhit = missed_by + dodge_roll/dice(10,speed)` |
| 발사 피해배수 | goodhit 0.2/0.5/0.8 경계로 1.5 / (1.766−4g/3) / (1.6−g) / 4(1−g) |
| 방어구 물리저항 | `round( avg(재질 *_resist) · 두께 )`, stab=`int(0.8·cut)` |
| 방어구 환경저항 | `round( avg(재질 acid/fire_resist) · (env≥10?1:env/10) )` |

---

### 출처 파일 (모두 위 고정 커밋 기준)

`src/melee.cpp`, `src/melee.h`, `src/ranged.cpp`, `src/ballistics.cpp`,
`src/dispersion.cpp`, `src/dispersion.h`, `src/creature.cpp`, `src/character.cpp`,
`src/monster.cpp`, `src/damage.cpp`, `src/damage.h`, `src/item.cpp`,
`src/rng.cpp`, `src/line.cpp`, `src/game_constants.h`.
